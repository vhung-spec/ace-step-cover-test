"""Plays and mixes the bossa nova sketches with ../render_samples.py (sfizz,
each part's tone and level, the room, loudness), from the libraries
../fetch_samples.py and fetch_bossa.py put in one folder:

    python bossa/render_bossa.py out/bossa --sfizz path/to/sfizz_render --libs libs
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import mido
import numpy as np
import soundfile as sf
from scipy.ndimage import maximum_filter1d, uniform_filter1d

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import render_samples  # noqa: E402

_sfz_copy = render_samples.sfz_copy


def sfz_copy(sfz: Path, part: str, db: float, tone: dict) -> Path:
    """render_samples.sfz_copy, the part's level set in every <global> of
    the file, not only its first: Virtuosity Drums opens one a microphone,
    and each <global> starts afresh (the level set in the first would move
    the kick's microphone alone)."""
    copy = _sfz_copy(sfz, part, db, tone)
    text = copy.read_text()
    line = f"global_volume={db:g}"
    first = text.find("<global>") + len("<global>")
    copy.write_text(text[:first] + text[first:].replace("<global>", f"<global>\n{line}"))
    return copy


render_samples.sfz_copy = sfz_copy  # render_part looks it up by name

_apply_tone = render_samples.apply_tone


def compress(audio: np.ndarray, ratio: float = 3.0, attack: float = 0.005, release: float = 0.12,
             above_db: float = 3.0) -> np.ndarray:
    """A part's compressor, vectorized as render_samples.limit is: its level
    (the louder channel, averaged over the attack) over a threshold set from
    the part's own playing level (the upper quartile of its level, plus
    above_db), cut by the ratio, the cut reached over the attack and let go
    at 10 dB per `release` seconds. No make-up: the mix sets each part's
    level after it. Real instruments' attacks (a finger-plucked bass, a nylon
    string plucked hard, a cajón) left the rumba mixes 16 dB of peak over
    their loudness (the references 11): 3 to 5 dB less a part with it."""
    rate = render_samples.RATE
    level = np.abs(audio).max(axis=0)
    size = max(1, int(attack * rate))
    env_db = 20 * np.log10(uniform_filter1d(level, size=size) + 1e-9)
    sounding = env_db > env_db.max() - 50
    if not sounding.any():
        return audio
    threshold = np.percentile(env_db[sounding], 75) + above_db
    cut = np.maximum(0.0, env_db - threshold) * (1 - 1 / ratio)
    cut = uniform_filter1d(maximum_filter1d(cut, size=2 * size + 1), size=2 * size + 1)
    n = np.arange(len(cut))
    step = 10.0 / (release * rate)  # dB a sample
    held = np.maximum.accumulate(cut + n * step) - n * step
    print(f"    compressed: at most {held.max():.1f} dB, {100 * np.mean(held > 1):.0f} % of the time over 1 dB",
          flush=True)
    return audio * 10 ** (-held / 20)


def apply_tone(audio: np.ndarray, tone: dict) -> np.ndarray:
    """render_samples.apply_tone, then the tone's compressor if it names one
    ("compress": compress()'s settings)."""
    audio = _apply_tone(audio, tone)
    return compress(audio, **tone["compress"]) if tone.get("compress") else audio


render_samples.apply_tone = apply_tone  # mix_folder looks it up by name

_render_part = render_samples.render_part


def render_sf2(sf2: Path, part: str, midi: Path, wav: Path, tone: dict) -> np.ndarray:
    """A part played on a SoundFont by FluidSynth, its own reverb and chorus
    off (the mix has its room): the part's MIDI on channel 1 with the tone's
    General MIDI program, or on channel 10 (the drum kits) with its keys
    moved as the tone's remap says ({"88": 37}: a cross-stick to GM's)."""
    channel = 9 if tone.get("drums") else 0
    remap = {int(k): int(v) for k, v in tone.get("remap", {}).items()}
    source = mido.MidiFile(midi)
    copy = mido.MidiFile(ticks_per_beat=source.ticks_per_beat)
    for track in source.tracks:
        out = mido.MidiTrack()
        out.append(mido.Message("program_change", program=int(tone.get("program", 0)), channel=channel, time=0))
        for msg in track:
            if msg.type in ("note_on", "note_off"):
                msg = msg.copy(channel=channel, note=remap.get(msg.note, msg.note))
            elif msg.type == "pitchwheel":
                msg = msg.copy(channel=channel)
            out.append(msg)
        copy.tracks.append(out)
    gm_midi = wav.with_suffix(".gm.mid")
    copy.save(gm_midi)
    rate = render_samples.RATE
    subprocess.run(["fluidsynth", "-ni", "-R", "0", "-C", "0", "-g", "0.6", "-r", str(rate), "-O", "float",
                    "-T", "wav", "-F", str(wav), str(sf2), str(gm_midi)], check=True, capture_output=True, timeout=900)
    audio, got = sf.read(wav, always_2d=True, dtype="float32")
    if got != rate:
        raise ValueError(f"{wav}: {got} Hz")
    print(f"    {part} on {sf2.name}, program {tone.get('program', 0)}{' (drums)' if channel == 9 else ''}: "
          f"peak {20 * np.log10(np.abs(audio).max() + 1e-12):.1f} dBFS", flush=True)
    return audio.T if audio.shape[1] == 2 else np.repeat(audio.T, 2, axis=0)


def render_part(sfizz: str, sfz: Path, part: str, midi: Path, wav: Path, tone: dict) -> np.ndarray:
    """render_samples.render_part, or FluidSynth for a SoundFont (.sf2)."""
    if Path(sfz).suffix.lower() == ".sf2":
        return render_sf2(Path(sfz), part, midi, wav, tone)
    return _render_part(sfizz, sfz, part, midi, wav, tone)


render_samples.render_part = render_part  # mix_folder looks it up by name


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--sfizz", default="sfizz_render")
    parser.add_argument("--libs", type=Path, required=True)
    parser.add_argument("--keep-parts", action="store_true", help="keep each part's WAV (to check a part alone)")
    args = parser.parse_args()
    libraries = {name: args.libs / name for name in ("vcsl", "vsco", "jrhodes", "freepats", "smolken", "swirly",
                                                      "meatbass", "rusty", "iowa", "emily", "fashionbass",
                                                      "virtuosity", "shiny")}
    libraries["local"] = Path(__file__).resolve().parent.parent / "instruments"  # our own (the synth pad)
    libraries["gm"] = Path("/usr/share/sounds/sf2")  # FluidR3_GM.sf2 (MIT), from Ubuntu's fluid-soundfont-gm
    for folder in sorted(p for p in args.out.iterdir() if (p / "mix.json").is_file()):
        print(f"== {folder.name}", flush=True)
        sheet = json.loads((folder / "mix.json").read_text())
        for entry in sheet["parts"]:  # an instrument that could not be fetched: its stand-in
            if not (libraries[entry["library"]] / entry["sfz"]).is_file() and "fallback" in entry:
                print(f"  {entry['part']}: {entry['library']} is missing, played on {entry['fallback']['library']}",
                      flush=True)
                entry.update({k: entry["fallback"][k] for k in ("library", "sfz", "tone")})
        (folder / "mix.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False))
        # a style's own loudness (the beats aim at their references' -15 LUFS, not the engine's -16), the
        # engine's limiter allowed that much more: its settings for this piece only
        engine = (render_samples.TARGET_LUFS, render_samples.MOST_LIMITING_DB, render_samples.QUIETEST_LUFS)
        loud = sheet.get("loudness")
        if loud:
            render_samples.TARGET_LUFS = loud["target"]
            render_samples.MOST_LIMITING_DB = loud.get("most_limiting_db", engine[1])
            render_samples.QUIETEST_LUFS = loud.get("quietest", engine[2])
        try:
            render_samples.mix_folder(folder, args.sfizz, libraries, keep_parts=args.keep_parts)
        finally:
            render_samples.TARGET_LUFS, render_samples.MOST_LIMITING_DB, render_samples.QUIETEST_LUFS = engine


if __name__ == "__main__":
    main()
