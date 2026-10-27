"""Renders the parts written by arrange.py with real instrument samples and
mixes them into one piece per folder:

    python render_samples.py out/sampled --sfizz path/to/sfizz_render --vsco <VSCO-2-CE> --vcsl <VCSL>
        [--salamander <SalamanderGrandPiano>]

- each part is played by sfizz_render from its SFZ instrument (mix.json),
  then played again louder or quieter until its peaks sit between -20 and
  -1 dBFS: sfizz writes 16-bit WAV, which clips above full scale and turns
  grainy when a quiet part is turned up afterwards. A piano's release samples
  (the dampers, which all sound at once when the pedal lifts) can be turned
  down;
- each part gets its tone (high-pass, low-pass, high shelf), and its loudness
  while it plays is set against the melody's by its role (arrange.ROLES), so
  libraries recorded at different levels still sit right; then it is placed
  in the stereo field;
- a hall reverb: a synthetic impulse response (noise in bands, each dying at
  its own rate, the highs soonest and quietest, building up over the first
  30 ms, with no single echo standing out), so no recording of a real hall
  and no licence is needed;
- the piece loses its rumble below 30 Hz and is brought to -16 LUFS (YouTube
  plays music at about -14), a look-ahead limiter keeping peaks below -1
  dBFS, and its last notes fade out over the reverb's tail; it is saved as
  <folder>.wav and <folder>.mp3.
"""

import argparse
import json
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from pathlib import Path

import numpy as np
import pyloudnorm
import soundfile as sf
from scipy.ndimage import maximum_filter1d
from scipy.signal import butter, fftconvolve, lfilter, sosfilt

RATE = 48000
TARGET_LUFS = -16.0


def sfz_copy(sfz: Path, part: str, db: float, release_db: float | None = None) -> Path:
    """A copy of an SFZ file for one part, next to it (its sample paths are
    relative), with every region turned up or down by db (sfizz's
    global_volume opcode) and its release samples, if any, by release_db."""
    text = sfz.read_text(errors="replace")
    line = f"global_volume={db:g}"
    if "<global>" in text:
        text = text.replace("<global>", f"<global>\n{line}", 1)
    else:
        text = f"<global>\n{line}\n{text}"
    if release_db is not None:
        text = re.sub(r"trigger=release\b", f"trigger=release\namplitude={100 * 10 ** (release_db / 20):.1f}", text)
    copy = sfz.with_name(f".{sfz.stem}.{part}.{db:+g}dB.sfz")
    copy.write_text(text)
    return copy


def render_part(sfizz: str, sfz: Path, part: str, midi: Path, wav: Path, release_db: float | None) -> np.ndarray:
    """Plays one part; rendering stops at the MIDI file's end of track (8 beats
    after its last event): without that, sfizz_render waits for full silence,
    which some instruments never reach."""
    db = 0.0
    for attempt in range(5):
        started = time.time()
        subprocess.run([sfizz, "--sfz", str(sfz_copy(sfz, part, db, release_db)), "--midi", str(midi),
                        "--wav", str(wav), "--samplerate", str(RATE), "--polyphony", "256", "--quality", "3",
                        "--use-eot"], check=True, capture_output=True, timeout=600)
        print(f"    {part} at {db:+g} dB: {time.time() - started:.0f} s", flush=True)
        audio, rate = sf.read(wav, always_2d=True, dtype="float32")
        if rate != RATE:
            raise ValueError(f"{wav}: {rate} Hz")
        peak = 20 * np.log10(np.abs(audio).max() + 1e-12)
        if peak > -0.1:  # clipped
            db -= 12
        elif peak < -20 and attempt < 4 and db < 30:
            db = min(30, db + round(-8 - peak))
        else:
            break
    else:
        raise RuntimeError(f"{part}: no level without clipping")
    return audio.T if audio.shape[1] == 2 else np.repeat(audio.T, 2, axis=0)


def high_shelf(freq: float, db: float) -> tuple:
    """Biquad coefficients of a high shelf (RBJ's audio EQ cookbook, slope 1)."""
    a = 10 ** (db / 40)
    w = 2 * np.pi * freq / RATE
    cos, alpha = np.cos(w), np.sin(w) / np.sqrt(2)
    b = np.array([a * ((a + 1) + (a - 1) * cos + 2 * np.sqrt(a) * alpha), -2 * a * ((a - 1) + (a + 1) * cos),
                  a * ((a + 1) + (a - 1) * cos - 2 * np.sqrt(a) * alpha)])
    den = np.array([(a + 1) - (a - 1) * cos + 2 * np.sqrt(a) * alpha, 2 * ((a - 1) - (a + 1) * cos),
                    (a + 1) - (a - 1) * cos - 2 * np.sqrt(a) * alpha])
    return b / den[0], den / den[0]


def apply_tone(audio: np.ndarray, tone: dict) -> np.ndarray:
    """A part's tone: a high-pass and a low-pass (Hz), a high shelf (Hz, dB)."""
    if tone.get("highpass"):
        audio = sosfilt(butter(2, tone["highpass"], "high", fs=RATE, output="sos"), audio, axis=-1)
    if tone.get("lowpass"):
        audio = sosfilt(butter(2, tone["lowpass"], "low", fs=RATE, output="sos"), audio, axis=-1)
    if tone.get("shelf"):
        audio = lfilter(*high_shelf(*tone["shelf"]), audio, axis=-1)
    return audio


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


# The hall at each frequency: (Hz, decay time against rt60, level in dB per
# octave at the start of the tail). The highs die soonest, as air and soft
# walls absorb them, so the tail is warm and carries no hiss; the lows are
# kept down, so it does not boom.
HALL = np.array([(63, 1.15, -9), (125, 1.1, -4), (250, 1.05, -1), (500, 1.0, 0), (1000, 0.95, 0),
                 (2000, 0.85, -1), (4000, 0.65, -3), (8000, 0.45, -6), (16000, 0.3, -10)])


@lru_cache
def hall_ir(rt60: float, seconds: float = 4.0, predelay: float = 0.025, seed: int = 1) -> np.ndarray:
    """Stereo impulse response of a warm hall: noise in third-octave bands, each
    dying at its own rate (HALL), building up over the first 30 ms with no
    single echo standing out; a different noise on each side, so the hall is
    wide."""
    rng = np.random.default_rng(seed)
    n = int(seconds * RATE)
    t = np.arange(n) / RATE
    spectrum = np.fft.rfft(rng.standard_normal((2, n)), axis=-1)
    freqs = np.fft.rfftfreq(n, 1 / RATE)
    ir = np.zeros((2, n))
    for centre in 1000 * 2 ** (np.arange(-14, 14) / 3):  # 40 Hz to 20 kHz
        band = (freqs >= centre * 2 ** (-1 / 6)) & (freqs < centre * 2 ** (1 / 6))
        decay, level = (np.interp(np.log2(centre), np.log2(HALL[:, 0]), HALL[:, k]) for k in (1, 2))
        noise = np.fft.irfft(spectrum * band, n=n, axis=-1) / np.sqrt(band.sum())  # every band as loud
        ir += noise * np.exp(-6.91 * t / (rt60 * decay)) * 10 ** (level / 20)
    ir *= 1 - np.exp(-t / 0.03)  # the reflections build up
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


def mix_folder(folder: Path, sfizz: str, libraries: dict, keep_parts: bool) -> Path:
    sheet = json.loads((folder / "mix.json").read_text())
    ir = hall_ir(sheet["hall"]["rt60"])

    def render(entry: dict) -> np.ndarray:
        sfz = libraries[entry["library"]] / entry["sfz"]
        return render_part(sfizz, sfz, entry["part"], folder / f"{entry['part']}.mid",
                           folder / f"{entry['part']}.wav", entry["tone"].get("release_db"))

    with ThreadPoolExecutor(max_workers=4) as pool:  # one sfizz_render per CPU
        audios = list(pool.map(render, sheet["parts"]))
    parts = {}
    for entry, audio in zip(sheet["parts"], audios):
        peak = 20 * np.log10(np.abs(audio).max() + 1e-12)
        print(f"  {entry['part']}: {audio.shape[1] / RATE:.1f} s, peak {peak:.1f} dBFS", flush=True)
        parts[entry["part"]] = (entry, apply_tone(audio, entry["tone"]))
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
    rumble = butter(2, 30, "high", fs=RATE, output="sos")
    mixed = fade_tail(sosfilt(rumble, dry + wet, axis=-1))
    meter = pyloudnorm.Meter(RATE)
    for _ in range(3):  # limiting lowers the loudness a little: measure again
        mixed *= 10 ** ((TARGET_LUFS - meter.integrated_loudness(mixed.T)) / 20)
        mixed = limit(mixed)
    out = folder.with_suffix(".wav")
    sf.write(out, mixed.T, RATE, subtype="PCM_24")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(out), "-b:a", "256k",
                    str(out.with_suffix(".mp3"))], check=True)
    print(f"{folder.name}: {mixed.shape[1] / RATE:.0f} s, hall {sheet['hall']['rt60']} s, "
          f"{meter.integrated_loudness(mixed.T):.1f} LUFS, peak {20 * np.log10(np.abs(mixed).max()):.1f} dBFS "
          f"-> {out.with_suffix('.mp3')}", flush=True)
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
    libraries = {"vsco": args.vsco, "vcsl": args.vcsl, "salamander": args.salamander}
    for folder in sorted(p for p in args.out.iterdir() if (p / "mix.json").is_file()):
        print(f"== {folder.name}", flush=True)
        mix_folder(folder, args.sfizz, libraries, args.keep_parts)


if __name__ == "__main__":
    main()
