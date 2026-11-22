"""Two soft instruments made here, no recording, written as samples and an SFZ
file as dark/piano_model.py writes its pianos (it builds these too, when a
piece's mix sheet names them):

- pad-soft: a thin, warm pad for the middle register. Each note three voices
  a few cents apart (left, centre, right), each a handful of partials falling
  away fast above ~1 kHz (no edge, no bass under it), breathing slowly (two
  slow swells of a few per cent, out of step); the SFZ fades it in over 1.6 s
  and out over 2.8 s, so it comes and goes with no attack.
- guitar-nylon: a nylon string plucked softly with the fingertip. The
  partials of a nearly harmonic string, their strengths set by where it is
  plucked (a sixth of the way along) and by the fingertip (a soft, rounded
  pluck: the harder, the brighter), each dying the sooner the higher it is
  (1.2 s to 1/e at 200 Hz);
  two polarisations a hair apart, so the note beats and settles as a real
  string's does; a guitar body's two warm resonances (about 210 and 400 Hz)
  and its roll-off above 3 kHz; a tiny, soft pluck noise; no squeak of a
  finger sliding on a wound string (there is none to make).
"""

import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import soundfile as sf

RATE = 44100
KEYS = range(48, 85)  # C3 to C6: both are meant for the middle register only
MODELS = {
    "pad-soft": {"seconds": 16.0, "detune_cents": 5.0, "partials": 10, "corner_hz": 1000.0, "tilt": 1.3,
                 "breath_hz": (0.11, 0.17), "breath": 0.06, "attack_s": 1.6, "release_s": 2.8},
    "guitar-nylon": {"seconds": 5.0, "pluck_at": 1 / 6, "inharmonicity": 1.2e-5, "tau_s": 1.2,
                     "body_hz": ((210.0, 4.0, 2.0), (400.0, 3.0, 2.5)), "rolloff_hz": 3000.0, "beat_hz": 0.35,
                     "release_s": 0.6},
}
# Velocity layers of the guitar: (lowest, highest, the fingertip's corner in Hz: a firmer pluck is brighter).
GUITAR_LAYERS = ((0, 55, 1300.0), (56, 90, 1900.0), (91, 127, 2600.0))


def frequency(key: int) -> float:
    return 440.0 * 2 ** ((key - 69) / 12)


def pad_note(key: int, p: dict, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(p["seconds"] * RATE)
    t = np.arange(n) / RATE
    out = np.zeros((2, n))
    f0 = frequency(key)
    for voice, (cents, left, right) in enumerate(((-p["detune_cents"], 0.75, 0.35), (0.0, 0.55, 0.55),
                                                  (p["detune_cents"], 0.35, 0.75))):
        f = f0 * 2 ** (cents / 1200)
        swell = 1 + p["breath"] * np.sin(2 * np.pi * p["breath_hz"][voice % 2] * t + rng.uniform(0, 2 * np.pi))
        wave = np.zeros(n)
        for k in range(1, p["partials"] + 1):
            fk = k * f
            if fk > 6000:
                break
            amp = k ** -p["tilt"] / (1 + (fk / p["corner_hz"]) ** 4)
            wave += amp * np.sin(2 * np.pi * fk * t + rng.uniform(0, 2 * np.pi))
        out[0] += left * wave * swell
        out[1] += right * wave * swell
    fade_in, fade_out = int(0.02 * RATE), int(1.5 * RATE)
    out[:, :fade_in] *= np.linspace(0, 1, fade_in)
    out[:, -fade_out:] *= np.linspace(1, 0, fade_out)
    return out


def guitar_note(key: int, corner: float, p: dict, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(p["seconds"] * RATE)
    t = np.arange(n) / RATE
    f0 = frequency(key)
    out = np.zeros((2, n))
    for k in range(1, 40):
        fk = k * f0 * np.sqrt(1 + p["inharmonicity"] * k * k)
        if fk > 9000:
            break
        amp = abs(np.sin(np.pi * k * p["pluck_at"])) / k ** 1.1      # where it is plucked
        amp /= 1 + (fk / corner) ** 2                               # the fingertip: a soft, rounded pluck
        amp /= 1 + (fk / p["rolloff_hz"]) ** 4                      # the body's roll-off
        for centre, gain_db, width in p["body_hz"]:                 # the body's warm resonances
            amp *= 1 + (10 ** (gain_db / 20) - 1) / (1 + ((fk - centre) / (centre / width)) ** 2)
        if fk < 110:
            amp *= (fk / 110) ** 2                                  # no boom under it
        tau = p["tau_s"] * (fk / 200.0) ** -0.75                   # the higher, the sooner it dies
        phase = rng.uniform(0, 2 * np.pi)
        for side, (shift, share, slower) in enumerate(((0.0, 0.6, 1.0), (p["beat_hz"], 0.4, 1.35))):
            wave = share * amp * np.exp(-t / (tau * slower)) * np.sin(2 * np.pi * (fk + shift) * t + phase)
            out[0] += wave * (0.62 if side == 0 else 0.38)
            out[1] += wave * (0.38 if side == 0 else 0.62)
    noise = rng.normal(0, 1, int(0.012 * RATE)) * np.exp(-np.arange(int(0.012 * RATE)) / (0.003 * RATE))
    noise = np.convolve(noise, np.ones(8) / 8, mode="same") * 0.004   # a tiny, soft pluck
    out[:, : len(noise)] += noise
    attack = int(0.003 * RATE)
    out[:, :attack] *= np.linspace(0, 1, attack)
    fade = int(0.3 * RATE)
    out[:, -fade:] *= np.linspace(1, 0, fade)
    return out


def sample(job: tuple) -> None:
    name, p, key, layer, path = job
    if name == "pad-soft":
        audio = pad_note(key, p, seed=key)
        level = np.sqrt(np.mean(audio[:, int(2 * RATE): int(6 * RATE)] ** 2))
    else:
        audio = guitar_note(key, GUITAR_LAYERS[layer][2], p, seed=key * 10 + layer)
        level = np.sqrt(np.mean(audio[:, : int(0.3 * RATE)] ** 2))
    audio *= 0.08 / level
    sf.write(path, audio.T.astype(np.float32), RATE, subtype="PCM_16")


def build(name: str, out: Path, keys) -> Path:
    """The instrument's samples for these keys and its SFZ file."""
    p = MODELS[name]
    folder = out / name
    folder.mkdir(parents=True, exist_ok=True)
    lines = [f"// {name}, made by dark/soft_model.py: no recording.", f"// {json.dumps(p)}", "<global>"]
    jobs = []
    if name == "pad-soft":
        lines += [f"ampeg_attack={p['attack_s']:g}", f"ampeg_release={p['release_s']:g}", "amp_veltrack=60", ""]
        for key in sorted(keys):
            path = folder / f"k{key}.flac"
            jobs.append((name, p, key, 0, path))
            lines.append(f"<region> sample={name}/{path.name} key={key} pitch_keycenter={key}")
    else:
        lines += [f"ampeg_release={p['release_s']:g}", "amp_veltrack=80", ""]
        for key in sorted(keys):
            for layer, (low, high, _) in enumerate(GUITAR_LAYERS):
                path = folder / f"k{key}_v{layer}.flac"
                jobs.append((name, p, key, layer, path))
                lines.append(f"<region> sample={name}/{path.name} key={key} pitch_keycenter={key} "
                             f"lovel={low} hivel={high}")
    with ProcessPoolExecutor() as pool:
        list(pool.map(sample, jobs))
    sfz = out / f"{name}.sfz"
    sfz.write_text("\n".join(lines) + "\n")
    return sfz
