"""Renders the parts written by arrange.py with real instrument samples and
mixes them into one piece per folder:

    python render_samples.py out/sampled --sfizz path/to/sfizz_render --vsco <VSCO-2-CE> --vcsl <VCSL>

- each part is played by sfizz_render from its SFZ instrument (mix.json),
  turned down first (sfizz writes 16-bit WAV, which would clip) and played
  again quieter if it still reaches full scale;
- each part's loudness while it plays is set against the melody's by its
  role (arrange.ROLES), so libraries recorded at different levels still sit
  right, then it is placed in the stereo field;
- a hall reverb: a synthetic impulse response (decaying noise, the highs
  dying faster), so no recording of a real hall and no licence is needed;
- the piece is brought to -16 LUFS (YouTube plays music at about -14), with
  peaks below -1 dBFS; it is saved as <folder>.wav and <folder>.mp3.
"""

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
import pyloudnorm
import soundfile as sf
from scipy.signal import butter, fftconvolve, sosfilt

RATE = 48000
TARGET_LUFS = -16.0


def quieter(sfz: Path, db: float) -> Path:
    """A copy of an SFZ file, next to it (its sample paths are relative), with
    every region turned down by db (sfizz's global_volume opcode)."""
    text = sfz.read_text(errors="replace")
    line = f"global_volume={-db:g}"
    if "<global>" in text:
        text = text.replace("<global>", f"<global>\n{line}", 1)
    else:
        text = f"<global>\n{line}\n{text}"
    copy = sfz.with_name(f".{sfz.stem}.minus{db:g}dB.sfz")
    copy.write_text(text)
    return copy


def render_part(sfizz: str, sfz: Path, midi: Path, wav: Path) -> np.ndarray:
    for headroom in (12, 24, 36):
        subprocess.run([sfizz, "--sfz", str(quieter(sfz, headroom)), "--midi", str(midi), "--wav", str(wav),
                        "--samplerate", str(RATE), "--polyphony", "256", "--quality", "3"],
                       check=True, capture_output=True)
        audio, rate = sf.read(wav, always_2d=True, dtype="float32")
        if rate != RATE:
            raise ValueError(f"{wav}: {rate} Hz")
        if np.abs(audio).max() < 0.99:
            break
        print(f"  {midi.stem}: reached full scale {headroom} dB down; again quieter")
    else:
        raise RuntimeError(f"{midi.stem} still clips 36 dB down")
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


def mix_folder(folder: Path, sfizz: str, libraries: dict, ir: np.ndarray, keep_parts: bool) -> Path:
    sheet = json.loads((folder / "mix.json").read_text())
    parts = {}
    for entry in sheet:
        sfz = libraries[entry["library"]] / entry["sfz"]
        audio = render_part(sfizz, sfz, folder / f"{entry['part']}.mid", folder / f"{entry['part']}.wav")
        parts[entry["part"]] = (entry, audio)
        print(f"  {entry['part']}: {audio.shape[1] / RATE:.1f} s, peak {20 * np.log10(np.abs(audio).max() + 1e-12):.1f} dBFS")
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
    mixed = dry + wet
    end = np.nonzero(np.abs(mixed).max(axis=0) > 10 ** (-70 / 20))[0]
    mixed = mixed[:, : end[-1] + RATE // 2] if len(end) else mixed
    loudness = pyloudnorm.Meter(RATE).integrated_loudness(mixed.T)
    mixed *= 10 ** ((TARGET_LUFS - loudness) / 20)
    peak = np.abs(mixed).max()
    if peak > 10 ** (-1 / 20):
        mixed *= 10 ** (-1 / 20) / peak
    out = folder.with_suffix(".wav")
    sf.write(out, mixed.T, RATE, subtype="PCM_24")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(out), "-b:a", "256k",
                    str(out.with_suffix(".mp3"))], check=True)
    print(f"{folder.name}: {mixed.shape[1] / RATE:.0f} s, "
          f"{pyloudnorm.Meter(RATE).integrated_loudness(mixed.T):.1f} LUFS -> {out.with_suffix('.mp3')}")
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--sfizz", default="sfizz_render")
    parser.add_argument("--vsco", type=Path, required=True)
    parser.add_argument("--vcsl", type=Path, required=True)
    parser.add_argument("--keep-parts", action="store_true", help="keep each part's WAV")
    args = parser.parse_args()
    ir = hall_ir()
    for folder in sorted(p for p in args.out.iterdir() if (p / "mix.json").is_file()):
        print(f"== {folder.name}")
        mix_folder(folder, args.sfizz, {"vsco": args.vsco, "vcsl": args.vcsl}, ir, args.keep_parts)


if __name__ == "__main__":
    main()
