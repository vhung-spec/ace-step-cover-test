"""Renders the parts written by arrange.py with real instrument samples and
mixes them into one piece per folder:

    python render_samples.py out/sampled --sfizz path/to/sfizz_render --vsco <VSCO-2-CE> --vcsl <VCSL>
        [--salamander <SalamanderGrandPiano>]

- each part is played by sfizz_render from its SFZ instrument (mix.json),
  then played again louder or quieter until its peaks sit between -20 and
  -1 dBFS: sfizz writes 16-bit WAV, which clips above full scale and turns
  grainy when a quiet part is turned up afterwards;
- each part's loudness while it plays is set against the melody's by its
  role (arrange.ROLES), so libraries recorded at different levels still sit
  right, then it is placed in the stereo field;
- a hall reverb: a synthetic impulse response (decaying noise, the highs
  dying faster), so no recording of a real hall and no licence is needed;
- the piece is brought to -16 LUFS (YouTube plays music at about -14), a
  look-ahead limiter keeping peaks below -1 dBFS, and its last notes fade
  out over the reverb's tail; it is saved as <folder>.wav and <folder>.mp3.
"""

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
import pyloudnorm
import soundfile as sf
from scipy.ndimage import maximum_filter1d
from scipy.signal import butter, fftconvolve, lfilter, sosfilt

RATE = 48000
TARGET_LUFS = -16.0


def at_volume(sfz: Path, db: float) -> Path:
    """A copy of an SFZ file, next to it (its sample paths are relative), with
    every region turned up or down by db (sfizz's global_volume opcode)."""
    text = sfz.read_text(errors="replace")
    line = f"global_volume={db:g}"
    if "<global>" in text:
        text = text.replace("<global>", f"<global>\n{line}", 1)
    else:
        text = f"<global>\n{line}\n{text}"
    copy = sfz.with_name(f".{sfz.stem}.{db:+g}dB.sfz")
    copy.write_text(text)
    return copy


def render_part(sfizz: str, sfz: Path, midi: Path, wav: Path) -> np.ndarray:
    db = 0.0
    for attempt in range(5):
        subprocess.run([sfizz, "--sfz", str(at_volume(sfz, db)), "--midi", str(midi), "--wav", str(wav),
                        "--samplerate", str(RATE), "--polyphony", "256", "--quality", "3"],
                       check=True, capture_output=True)
        audio, rate = sf.read(wav, always_2d=True, dtype="float32")
        if rate != RATE:
            raise ValueError(f"{wav}: {rate} Hz")
        peak = 20 * np.log10(np.abs(audio).max() + 1e-12)
        if peak > -0.1:  # clipped
            db -= 12
        elif peak < -20 and attempt < 4:
            db += round(-8 - peak)
        else:
            break
    else:
        raise RuntimeError(f"{midi.stem}: no level without clipping")
    return audio.T if audio.shape[1] == 2 else np.repeat(audio.T, 2, axis=0)


def playing_db(audio: np.ndarray) -> float:
    """Loudness (RMS, dB) over the 50 ms frames where the part plays, i.e.
    within 40 dB of its loudest frame."""
    mono = audio.mean(axis=0)
    frame = RATE // 20
    n = len(mono) // frame
    if n == 0:
        return -120.0
    rms = np.sqrt(np.mean(mono[: n * frame].reshape(n, frame) ** 2, axis=1)) + 1e-12
    db = 20 * np.log10(rms)
    return float(10 * np.log10(np.mean(10 ** (db[db > db.max() - 40] / 10))))


def pan(audio: np.ndarray, position: float) -> np.ndarray:
    """Constant-power balance, -1 left to 1 right; 0 leaves the part as recorded."""
    angle = (position + 1) * np.pi / 4
    return audio * (np.array([[np.cos(angle)], [np.sin(angle)]]) * np.sqrt(2))


def hall_ir(rt60: float = 2.2, seconds: float = 3.0, predelay: float = 0.022, seed: int = 1) -> np.ndarray:
    """Stereo impulse response of a warm hall: a few early reflections, then
    decaying noise whose highs fade faster than its lows (as in air)."""
    rng = np.random.default_rng(seed)
    n = int(seconds * RATE)
    t = np.arange(n) / RATE
    noise = rng.standard_normal((2, n))
    low = sosfilt(butter(2, 2500, "low", fs=RATE, output="sos"), noise) * np.exp(-6.91 * t / rt60)
    high = sosfilt(butter(2, 2500, "high", fs=RATE, output="sos"), noise) * np.exp(-6.91 * t / (rt60 * 0.45))
    ir = low + 0.5 * high
    ir[:, : int(0.008 * RATE)] *= np.linspace(0, 1, int(0.008 * RATE))  # no click at the start
    for delay, gain, side in ((0.011, 0.5, 0), (0.017, 0.45, 1), (0.029, 0.35, 0), (0.037, 0.3, 1)):
        ir[side, int(delay * RATE)] += gain * np.abs(ir).max()
    ir = np.concatenate([np.zeros((2, int(predelay * RATE))), ir], axis=1)
    return ir / np.sqrt(np.sum(ir ** 2) / 2)


def limit(audio: np.ndarray, ceiling_db: float = -1.0, lookahead: float = 0.005,
          release: float = 0.12) -> np.ndarray:
    """Turns peaks down to the ceiling a few ms before they come and lets the
    gain recover smoothly, so no sample goes over and nothing distorts."""
    ceiling = 10 ** (ceiling_db / 20)
    level = np.abs(audio).max(axis=0)
    needed = 1 - np.minimum(1, ceiling / np.maximum(level, 1e-12))  # gain reduction per sample
    window = int(lookahead * RATE) * 2 + 1
    needed = maximum_filter1d(needed, size=window)  # start before the peak
    a = np.exp(-1 / (release * RATE))
    smooth = lfilter([1 - a], [1, -a], needed)  # recover slowly...
    reduction = np.maximum(needed, smooth)  # ...but never less than needed
    return audio * (1 - reduction)


def fade_tail(audio: np.ndarray, seconds: float = 3.0) -> np.ndarray:
    """Ends the piece when it has faded 60 dB below its peak, the last seconds
    faded out, rather than on a long, barely audible tail."""
    level = np.abs(audio).max(axis=0)
    loud = np.nonzero(level > level.max() * 10 ** (-60 / 20))[0]
    audio = audio[:, : loud[-1] + 1] if len(loud) else audio
    n = min(int(seconds * RATE), audio.shape[1])
    audio[:, -n:] *= np.linspace(1, 0, n) ** 2
    return audio


def mix_folder(folder: Path, sfizz: str, libraries: dict, ir: np.ndarray, keep_parts: bool) -> Path:
    sheet = json.loads((folder / "mix.json").read_text())
    parts = {}
    for entry in sheet:
        sfz = libraries[entry["library"]] / entry["sfz"]
        audio = render_part(sfizz, sfz, folder / f"{entry['part']}.mid", folder / f"{entry['part']}.wav")
        parts[entry["part"]] = (entry, audio)
        peak = 20 * np.log10(np.abs(audio).max() + 1e-12)
        print(f"  {entry['part']}: {audio.shape[1] / RATE:.1f} s, peak {peak:.1f} dBFS")
    melody = [playing_db(a) for e, a in parts.values() if e["role"] in ("melody", "piano")]
    reference = float(np.mean(melody)) if melody else -20.0
    n = max(a.shape[1] for _, a in parts.values()) + ir.shape[1]
    dry, send = np.zeros((2, n)), np.zeros((2, n))
    for name, (entry, audio) in parts.items():
        gain = 10 ** ((reference + entry["gain_db"] - playing_db(audio)) / 20)
        placed = pan(audio * gain, entry["pan"])
        dry[:, : placed.shape[1]] += placed
        send[:, : placed.shape[1]] += placed * entry["reverb"]
        if not keep_parts:
            (folder / f"{name}.wav").unlink()
    wet = np.stack([fftconvolve(send[c], ir[c])[:n] for c in range(2)])
    mixed = fade_tail(dry + wet)
    meter = pyloudnorm.Meter(RATE)
    for _ in range(3):  # limiting lowers the loudness a little: measure again
        mixed *= 10 ** ((TARGET_LUFS - meter.integrated_loudness(mixed.T)) / 20)
        mixed = limit(mixed)
    out = folder.with_suffix(".wav")
    sf.write(out, mixed.T, RATE, subtype="PCM_24")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(out), "-b:a", "256k",
                    str(out.with_suffix(".mp3"))], check=True)
    print(f"{folder.name}: {mixed.shape[1] / RATE:.0f} s, {meter.integrated_loudness(mixed.T):.1f} LUFS, "
          f"peak {20 * np.log10(np.abs(mixed).max()):.1f} dBFS -> {out.with_suffix('.mp3')}")
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--sfizz", default="sfizz_render")
    parser.add_argument("--vsco", type=Path, required=True)
    parser.add_argument("--vcsl", type=Path, required=True)
    parser.add_argument("--salamander", type=Path, help="needed for the salamander style")
    parser.add_argument("--keep-parts", action="store_true", help="keep each part's WAV")
    args = parser.parse_args()
    ir = hall_ir()
    for folder in sorted(p for p in args.out.iterdir() if (p / "mix.json").is_file()):
        print(f"== {folder.name}")
        libraries = {"vsco": args.vsco, "vcsl": args.vcsl, "salamander": args.salamander}
        mix_folder(folder, args.sfizz, libraries, ir, args.keep_parts)


if __name__ == "__main__":
    main()
