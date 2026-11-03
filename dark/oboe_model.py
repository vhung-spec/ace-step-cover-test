"""A modelled oboe: no recording, every note made from the oboe's sound as
measured, then written as samples and an SFZ file for render_samples.py to
play, as dark/piano_model.py does for the pianos (which builds these too,
when a mix sheet names one):

    python dark/oboe_model.py <out> [--keys 60 62 ...]

A note is a reed's tone, held:
- its harmonics as measured on the nearest sampled notes (RECIPES: a note's
  first 24, between the two nearest by key), and above them, the oboe's
  spectral envelope: strongest from
  300 Hz to 1.3 kHz (the reed's formant near 1.2 kHz), falling 15 dB by
  1.6 kHz and 30 by 2 kHz, a weak shelf to 4 kHz, little above; the lowest
  notes' fundamentals weak. Measured on VSCO 2 CE's oboe (CC0): every soft
  and loud sample's harmonics, steady part, pooled in third octaves (dB of
  a harmonic against its note); the loud ones a little brighter at 1.2 and
  3-4 kHz. A fixed ripple (+-2.5 dB, a fifth of an octave apart) stands for
  the bore's own unevenness, the same for every note;
- every harmonic's strength read at its own moving frequency, so as the
  pitch sways the harmonics rise and fall through the envelope, as a real
  oboe's vibrato colours its tone;
- a vibrato (5 Hz, +-7 cents, as measured on the vibrato samples) growing in
  after the note has settled (0.3-1.1 s), its speed and depth wandering a
  little; the pitch drifting a few cents; a slight scoop up into the note;
- every harmonic wandering a little on its own (+-1 dB, about twice a
  second), as a player's breath and lips never hold still;
- breath: noise between the harmonics, 1-5 kHz, 42 dB under them, a little
  burst of it as the reed speaks.
Fitted by LAION CLAP's likeness (music; both under 150 Hz removed, where
the recordings hold their microphones' rumble) to four soft notes of the
samples: the envelope alone 0.64, the recipes 0.69, less breath (42 dB
under, against 33) 0.72-0.74; the straight and vibrato samples to each other
0.89. More breath, pitch jitter, a slower onset or a room all fell;
- the onset: the note speaking in 35 ms, its upper harmonics a little after
  the lower; the level easing up 1.5 dB over its first 1.5 s and breathing
  (+-0.4 dB, slow), so a long held note never stands still.
Two layers (soft, loud), each its envelope, at the same level: the SFZ makes
a note louder with its velocity. Samples are 16 s long (OBOE_SECONDS in
compose.py lets a note sound 15), mono, one a key: no note is pitch-shifted.
"""

import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

RATE = 44100
KEYS = range(55, 92)  # G3 to G6 (the oboe's own lowest is A#3)
SECONDS = 16.0
CONTROL = 64  # samples between control points (pitch, strengths)
LAYERS = ((1, 56, "soft"), (57, 127, "loud"))
# The spectral envelope (Hz, dB of a harmonic against its note's whole), smoothed from the measurement.
ENVELOPES = {
    "soft": [(150, -40), (250, -27), (315, -7), (400, -6.5), (500, -6.5), (630, -9), (794, -11), (1000, -7),
             (1260, -4.5), (1587, -15.5), (2000, -31), (2520, -32), (3175, -35), (4000, -37), (5040, -40),
             (6350, -55), (8000, -64), (10079, -69), (12699, -70)],
    "loud": [(150, -40), (250, -27.5), (315, -8), (400, -10), (500, -13), (630, -13.5), (794, -8.5), (1000, -7.4),
             (1260, -2), (1587, -12.6), (2000, -28.4), (2520, -31.4), (3175, -30), (4000, -33.5), (5040, -42),
             (6350, -54), (8000, -64), (10079, -67.5), (12699, -69)],
}
# Each sampled note's harmonics 1-24 (dB to its strongest; soft, loud; both kinds of sample averaged): a key
# between two takes its recipe between theirs, by key; the harmonics above follow the envelope.
RECIPES = {
    "soft": {
        58: [-20, 0, -3, -1, 0, 0, -15, -18, -23, -27, -29, -36, -33, -35, -32, -31, -39, -38, -39, -46, -46, -47, -42, -41],
        62: [-4, -10, -10, 0, -2, -14, -34, -37, -31, -28, -28, -33, -33, -31, -31, -32, -36, -30, -33, -41, -46, -55, -50, -56],
        65: [-3, -6, 0, -4, -16, -38, -36, -33, -35, -39, -32, -31, -34, -40, -42, -48, -43, -51, -60, -63, -62, -68, -67, -57],
        70: [-2, -6, 0, -20, -19, -22, -26, -27, -34, -33, -36, -38, -41, -55, -57, -51, -59, -46, -54, -66, -65, -66, -62, -52],
        74: [0, 0, -3, -24, -19, -32, -33, -35, -33, -36, -48, -50, -58, -52, -54, -59, -58, -58, -54, -55, -62, -64, -62, -62],
        77: [-10, 0, -36, -36, -39, -36, -44, -48, -58, -69, -73, -62, -74, -70, -71, -71, -68, -72, -74, -78, -72],
        82: [0, -2, -19, -31, -20, -24, -45, -47, -44, -51, -52, -52, -54, -54, -52, -50],
        86: [0, -12, -22, -30, -34, -51, -53, -58, -55, -50, -50, -59],
        89: [0, -12, -13, -22, -44, -42, -52, -48, -56, -47],
    },
    "loud": {
        58: [-26, -12, -13, -13, 0, -7, -13, -23, -30, -31, -31, -33, -32, -42, -40, -35, -37, -39, -42, -44, -48, -50, -47, -47],
        62: [-4, -9, -4, 0, -4, -13, -25, -28, -26, -25, -23, -25, -28, -29, -28, -36, -36, -35, -35, -40, -39, -46, -51, -55],
        65: [-8, -9, -5, 0, -15, -36, -29, -24, -24, -29, -32, -32, -33, -41, -46, -43, -43, -47, -62, -58, -60, -64, -65, -57],
        70: [-11, -5, 0, -22, -30, -28, -26, -28, -30, -32, -43, -47, -43, -61, -68, -62, -63, -55, -58, -64, -69, -66, -68, -65],
        74: [-4, 0, -7, -29, -23, -28, -32, -30, -39, -39, -48, -57, -57, -56, -60, -62, -61, -60, -65, -63, -63, -66, -63, -67],
        77: [-21, 0, -40, -43, -35, -38, -48, -52, -59, -72, -69, -68, -73, -74, -74, -72, -75, -77, -79, -77, -71],
        82: [0, -11, -15, -22, -24, -33, -47, -55, -48, -60, -61, -55, -57, -59, -56, -53],
        86: [0, -9, -13, -30, -42, -50, -52, -65, -57, -47, -49, -49],
        89: [0, -12, -12, -23, -42, -39, -51, -47, -49, -47],
    },
}
_RIPPLE = np.random.default_rng(11).uniform(-2.5, 2.5, 48)  # the bore's unevenness, a fifth of an octave apart

MODELS = {
    # with a player's vibrato
    "oboe-model": {"vibrato_cents": 7.0, "vibrato_hz": 5.0, "breath_db": -42.0, "shimmer_db": 1.0},
    # held almost straight
    "oboe-model-straight": {"vibrato_cents": 1.5, "vibrato_hz": 5.0, "breath_db": -42.0, "shimmer_db": 1.0},
}


def envelope(freq: np.ndarray, layer: str) -> np.ndarray:
    """dB of a harmonic at these frequencies."""
    points = ENVELOPES[layer]
    at = np.log2(np.maximum(freq, 20.0))
    db = np.interp(at, np.log2([p[0] for p in points]), [p[1] for p in points])
    ripple = np.interp((at - np.log2(150)) * 5, np.arange(len(_RIPPLE)), _RIPPLE)
    return db + ripple


def wander(rng: np.random.Generator, n: int, hz: float) -> np.ndarray:
    """A slow random curve (std 1) changing about hz times a second, at n control points."""
    step = CONTROL / RATE
    knots = max(4, int(n * step * hz) + 4)
    curve = np.interp(np.arange(n) * step * hz, np.arange(knots), rng.standard_normal(knots))
    return (curve - curve.mean()) / (curve.std() + 1e-9)


def recipe(key: int, layer: str, count: int, f0: float) -> np.ndarray:
    """dB of harmonics 1..count at this key."""
    measured = RECIPES[layer]
    keys = sorted(measured)
    known = min(count, 24)
    rows = [np.interp(key, keys, [measured[x][k] if k < len(measured[x]) else -60.0 for x in keys]) for k in range(known)]
    for k in range(known, count):  # above: the envelope's fall from the last one known
        rows.append(rows[known - 1] + float(envelope(np.array([(k + 1) * f0]), layer)[0]
                                            - envelope(np.array([known * f0]), layer)[0]))
    return np.array(rows)


def note(key: int, layer: str, p: dict, seed: int) -> np.ndarray:
    """One held note, mono."""
    rng = np.random.default_rng(seed)
    n = int(SECONDS * RATE)
    m = n // CONTROL + 2
    t = np.arange(m) * CONTROL / RATE
    f0 = 440.0 * 2 ** ((key - 69) / 12)
    speed = p["vibrato_hz"] * (1 + 0.05 * wander(rng, m, 0.3))
    depth = p["vibrato_cents"] * np.clip((t - 0.3) / 0.8, 0, 1) * (1 + 0.25 * wander(rng, m, 0.2))
    cents = (depth * np.sin(2 * np.pi * np.cumsum(speed) * CONTROL / RATE + rng.uniform(0, 2 * np.pi))
             + 2.5 * wander(rng, m, 0.4) - 15 * np.exp(-t / 0.05))
    pitch = f0 * 2 ** (cents / 1200)
    level = (1 - np.exp(-t / 0.035)) * 10 ** ((1.5 * np.minimum(1, t / 1.5) - 1.5 + 0.4 * wander(rng, m, 0.7)) / 20)
    sample_t = np.arange(n) / RATE
    fine_pitch = np.interp(sample_t, t, pitch)
    phase = 2 * np.pi * np.cumsum(fine_pitch) / RATE
    out = np.zeros(n)
    count = int(14000 // f0)
    base = recipe(key, layer, count, f0)
    for k in range(1, count + 1):
        db = (base[k - 1] + envelope(k * pitch, layer) - envelope(np.array([k * f0]), layer)[0]
              + p["shimmer_db"] * wander(rng, m, 2.0))
        speak = 1 - np.exp(-t / (0.02 + 0.004 * min(k, 25)))  # the upper harmonics speak a little later
        strength = np.interp(sample_t, t, 10 ** (db / 20) * speak * level)
        out += strength * np.sin(k * phase + rng.uniform(0, 2 * np.pi))
    band = butter(2, [1000, 5000], "band", fs=RATE, output="sos")
    tone_power = np.mean(sosfilt(band, out)[int(1 * RATE): int(3 * RATE)] ** 2)  # the harmonics, 1-5 kHz
    noise = sosfilt(band, rng.standard_normal(n))
    noise *= np.sqrt(tone_power * 10 ** (p["breath_db"] / 10) / np.mean(noise ** 2))
    out += noise * np.interp(sample_t, t, level) * (1 + 3 * np.exp(-sample_t / 0.03))
    out *= np.minimum(1, (n - np.arange(n)) / (0.5 * RATE))  # faded at the sample's very end
    return out


def sample(job: tuple) -> None:
    """One key at one layer, levelled, written as FLAC."""
    p, key, layer, path, seed = job
    audio = note(key, layer, p, seed)
    audio *= 0.08 / np.sqrt(np.mean(audio[int(0.5 * RATE): int(3 * RATE)] ** 2))
    sf.write(path, audio.astype(np.float32), RATE, subtype="PCM_16")


def build(name: str, out: Path, keys) -> Path:
    """The model's samples for these keys (one process a CPU) and its SFZ file."""
    p = MODELS[name]
    folder = out / name
    folder.mkdir(parents=True, exist_ok=True)
    lines = ["// A modelled oboe (dark/oboe_model.py): no recording, every note made from the oboe's measured sound.",
             f"// {name}: {json.dumps(p)}", "<global>", "amp_veltrack=100", "ampeg_attack=0.02", "ampeg_release=0.35", ""]
    jobs = []
    for key in sorted(keys):
        for low, high, layer in LAYERS:
            path = folder / f"k{key}_{layer}.flac"
            jobs.append((p, key, layer, path, key * 10 + low))
            lines.append(f"<region> sample={name}/{path.name} key={key} pitch_keycenter={key} lovel={low} hivel={high}")
    with ProcessPoolExecutor() as pool:
        list(pool.map(sample, jobs))
    sfz = out / f"{name}.sfz"
    sfz.write_text("\n".join(lines) + "\n")
    return sfz


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--model", default="oboe-model", choices=sorted(MODELS))
    parser.add_argument("--keys", type=int, nargs="+", default=list(KEYS))
    args = parser.parse_args()
    print(build(args.model, args.out, args.keys))


if __name__ == "__main__":
    main()
