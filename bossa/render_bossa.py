"""Plays and mixes the bossa nova sketches with ../render_samples.py (sfizz,
each part's tone and level, the room, loudness), from the libraries
../fetch_samples.py and fetch_bossa.py put in one folder:

    python bossa/render_bossa.py out/bossa --sfizz path/to/sfizz_render --libs libs
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
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
