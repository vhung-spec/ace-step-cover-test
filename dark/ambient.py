"""Dark ambient ("Không gian u tối"): slow, dark space music, long evolving
sounds, deep bells, almost no tune. The second dark style of this bench
(branch dark-khac, beside the dark piano of dark-piano), using its tools:
pieces written as data in dark/pieces/ (a style whose "kind" is "ambient":
compose.py hands them here), MIDI and a mix sheet per piece, played and
mixed by render_samples.py. Every instrument here is modelled, made from
numbers, no recording and no licence:

    python dark/ambient.py <out> [--keys 48 55 ...] [--models amb-pad ...]

builds the samples and SFZ files (dark/piano_model.py builds those the
pieces name, with its own), as dark/oboe_model.py does:

- amb-pad: a dark analogue pad: three sawtooths a side, a few cents apart,
  each drifting, a sine under them, through a low-pass that slowly opens
  and closes (two filtered copies crossfaded, 17-29 s a breath), a slow
  swell of its level; looped (30 s), so a note is held as long as a piece
  asks, swelling in over 3.5 s and fading over 6;
- amb-choir: a far-off choir on "oo": eight voices (four a side), each a
  voice's harmonics through the formants of a dark "oo" (400, 800 Hz, little
  above 2.6 kHz), each its own slight vibrato, pitch and breath; looped;
- amb-sub: a deep sine with a whisper of its octave, breathing; looped;
- amb-bell: a large bell struck softly with a felt mallet: its hum two
  octaves under the note, its prime an octave under, the minor-third tierce,
  the fifth, the nominal (the key's note) and a few upper partials, each
  split into two a fraction of a hertz apart, so they beat, the higher dying
  sooner; ringing up to 24 s;
- amb-glass: a soft glass/bowl tone, nearly pure: the note, a faint octave
  and twelfth, slow beating, a long ring; for the few notes of a tune.

The pieces (compose_ambient): chords held as long as they last, a tone
common to two chords held across them; layers, per section:
  pad (the chord, three or four tones, low and middle), choir (the chord's
  colour tones above the pad), sub (the root, deep), bells (the section's
  melody on the bell, if any), glass (its melody on the glass), toll (a low
  bell on the chord's root at each chord, or every toll_every chords),
  drone (compose.py's drone); "answer", a second line beside the melody,
  played on the bell (as the cellos answer the piano in the dark piano).
dyn, 0-1, sets every layer's strength; a section's "swell" lets it grow
through the section.
"""

import argparse
import json
import math
import random
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfiltfilt

RATE = 44100
LOOP_SECONDS = 30.0  # the looped part of a held sound
LEAD = 4.0  # seconds before the loop begins (the loop's crossfade comes from them)
FADE = 3.0  # the loop's crossfade

MODELS = {
    # attack, release (s), velocity tracking (%), keys
    "amb-pad": {"attack": 3.5, "release": 6.0, "veltrack": 60, "keys": range(31, 80), "loop": True},
    "amb-choir": {"attack": 4.0, "release": 6.0, "veltrack": 60, "keys": range(43, 80), "loop": True},
    "amb-sub": {"attack": 4.0, "release": 6.0, "veltrack": 50, "keys": range(19, 52), "loop": True},
    "amb-bell": {"attack": 0.006, "release": 4.0, "veltrack": 80, "keys": range(36, 90), "loop": False},
    "amb-glass": {"attack": 0.03, "release": 5.0, "veltrack": 75, "keys": range(48, 96), "loop": False},
}


def hz(key: int) -> float:
    return 440.0 * 2 ** ((key - 69) / 12)


def wander(n: int, rng: np.random.Generator, rate: float) -> np.ndarray:
    """A slow random line, about -1..1, changing about `rate` times a second."""
    points = max(4, int(n / RATE * rate) + 3)
    knots = rng.standard_normal(points)
    return np.interp(np.arange(n), np.linspace(0, n, points), knots) / 1.2


def saw(phase: np.ndarray, step: np.ndarray) -> np.ndarray:
    """A band-limited sawtooth (polyBLEP) from a phase in cycles and its step per sample."""
    p = phase % 1.0
    out = 2 * p - 1
    t = p / step
    near = t < 1
    out[near] -= (t[near] * 2 - t[near] ** 2 - 1)
    t = (p - 1) / step
    near = t > -1
    out[near] -= (t[near] ** 2 + 2 * t[near] + 1)
    return out


def lowpass(x: np.ndarray, corner: float, order: int = 4) -> np.ndarray:
    corner = min(corner, 0.45 * RATE)
    return sosfiltfilt(butter(order, corner, "low", fs=RATE, output="sos"), x)


def pad(key: int, n: int, rng: np.random.Generator) -> np.ndarray:
    f0 = hz(key)
    out = np.zeros((2, n))
    t = np.arange(n) / RATE
    for side in range(2):
        voices = np.zeros(n)
        for cents in ((-9, -2, 6), (-6, 3, 9))[side]:
            drift = cents + 2.5 * wander(n, rng, 0.08)
            step = f0 * 2 ** (drift / 1200) / RATE
            voices += saw(rng.random() + np.cumsum(step), step)
        voices /= 3
        sine = np.sin(2 * np.pi * f0 * t + rng.random() * 6.28)
        dark = lowpass(voices, max(2.5 * f0, 420))
        open_ = lowpass(voices, max(6 * f0, 1300))
        period = rng.uniform(17, 29)
        breath = 0.5 - 0.5 * np.cos(2 * np.pi * t / period + rng.random() * 6.28)  # 0..1
        breath = breath ** 1.5
        out[side] = dark * (1 - 0.6 * breath) + open_ * 0.6 * breath + 0.5 * sine
        out[side] *= 10 ** ((1.2 * wander(n, rng, 0.1)) / 20)
    return out


# A dark "oo": formants (Hz, bandwidth, dB)
VOWEL = [(390, 90, 0.0), (800, 110, -8.0), (2600, 160, -30.0), (3300, 200, -38.0)]


def formant_gain(freq: np.ndarray) -> np.ndarray:
    gain = np.full_like(freq, 10 ** (-48 / 20))
    for centre, width, db in VOWEL:
        gain += 10 ** (db / 20) / (1 + ((freq - centre) / (width / 2)) ** 2)
    return gain


def choir(key: int, n: int, rng: np.random.Generator) -> np.ndarray:
    f0 = hz(key)
    out = np.zeros((2, n))
    count = max(1, int(4000 / f0))
    harmonics = np.arange(1, count + 1)
    amps = formant_gain(harmonics * f0) / harmonics ** 0.6  # the voice's own fall, then the vowel
    amps[harmonics * f0 < 140] *= 0.5
    for side in range(2):
        for _ in range(4):
            rate = rng.uniform(4.6, 5.6)
            depth = rng.uniform(8, 16) * (0.6 + 0.4 * (wander(n, rng, 0.2) + 1) / 2)  # cents
            cents = rng.uniform(-10, 10) + 3 * wander(n, rng, 0.1) + depth * np.sin(
                2 * np.pi * np.cumsum(rate * (1 + 0.04 * wander(n, rng, 0.3))) / RATE)
            phase = 2 * np.pi * np.cumsum(f0 * 2 ** (cents / 1200)) / RATE
            level = 10 ** (2.0 * wander(n, rng, 0.25) / 20)
            voice = np.zeros(n)
            for k, a in zip(harmonics, amps):
                if a > 10 ** (-60 / 20):
                    voice += a * np.sin(k * phase + rng.random() * 6.28)
            out[side] += voice * level
    return out


def sub(key: int, n: int, rng: np.random.Generator) -> np.ndarray:
    f0 = hz(key)
    t = np.arange(n) / RATE
    out = np.zeros((2, n))
    tone = np.sin(2 * np.pi * f0 * t) + 0.12 * np.sin(4 * np.pi * f0 * t + 1.0) + 0.04 * np.sin(6 * np.pi * f0 * t)
    swell = 10 ** (1.5 * wander(n, rng, 0.06) / 20)
    out[0] = out[1] = tone * swell
    return out


# A bell's partials: (ratio to the nominal, the key's note), level dB, ring (s to -60 dB, at 220 Hz nominal)
BELL = [(0.25, -4, 30), (0.5, 0, 22), (0.6, -5, 16), (0.75, -12, 11), (1.0, -3, 13), (1.26, -16, 7),
        (1.5, -20, 6), (2.0, -22, 4.5), (2.6, -30, 3), (3.3, -36, 2)]


def bell(key: int, n: int, rng: np.random.Generator, partials=BELL, soft: float = 1.0) -> np.ndarray:
    f0 = hz(key)
    t = np.arange(n) / RATE
    out = np.zeros((2, n))
    for ratio, db, ring in partials:
        freq = f0 * ratio
        if freq > 6000 or freq < 25:
            continue
        ring *= (220 / f0) ** 0.45
        level = 10 ** (db / 20) * (1 if freq < 1500 else 10 ** (-soft * 6 * math.log2(freq / 1500) / 20))
        for side in range(2):
            split = rng.uniform(0.15, 0.6)
            for sign in (-1, 1):
                env = np.exp(-6.91 * t / (ring * rng.uniform(0.9, 1.1)))
                out[side] += 0.5 * level * env * rng.uniform(0.8, 1.0) * np.sin(
                    2 * np.pi * (freq + sign * split / 2) * t + rng.random() * 6.28)
    onset = 1 - np.exp(-t / 0.004)  # the felt's soft touch
    thump = lowpass(rng.standard_normal(n) * np.exp(-t / 0.03), 250, 2) * 0.05
    return out * onset + thump


GLASS = [(1.0, 0, 14), (2.0, -18, 8), (3.0, -30, 5), (4.0, -38, 3)]


def glass(key: int, n: int, rng: np.random.Generator) -> np.ndarray:
    return bell(key, n, rng, GLASS, soft=1.5)


SYNTHS = {"amb-pad": pad, "amb-choir": choir, "amb-sub": sub, "amb-bell": bell, "amb-glass": glass}


def sample(job: tuple) -> None:
    name, key, path = job
    rng = np.random.default_rng(key * 101 + sum(map(ord, name)))
    model = MODELS[name]
    seconds = LEAD + LOOP_SECONDS if model["loop"] else 24.0
    n = int(seconds * RATE)
    audio = SYNTHS[name](key, n, rng)
    if model["loop"]:  # the loop's end crossfaded into what comes before its start, so it runs on unbroken
        start, fade = int(LEAD * RATE), int(FADE * RATE)
        w = np.sin(0.5 * np.pi * np.arange(fade) / fade)
        audio[:, n - fade:] = audio[:, n - fade:] * np.cos(0.5 * np.pi * np.arange(fade) / fade) \
            + audio[:, start - fade:start] * w
        level = np.sqrt(np.mean(audio[:, start:] ** 2))
    else:
        level = np.sqrt(np.mean(audio[:, : int(1.0 * RATE)] ** 2))
        audio[:, -int(0.5 * RATE):] *= np.linspace(1, 0, int(0.5 * RATE))
    audio *= 0.1 / (level + 1e-12)
    peak = np.abs(audio).max()
    if peak > 0.98:
        audio *= 0.98 / peak
    sf.write(path, audio.T.astype(np.float32), RATE, subtype="PCM_16")


def build(name: str, out: Path, keys) -> Path:
    model = MODELS[name]
    folder = out / name
    folder.mkdir(parents=True, exist_ok=True)
    lines = [f"// {name}: modelled (dark/ambient.py), no recording.", "<global>",
             f"amp_veltrack={model['veltrack']}", f"ampeg_attack={model['attack']:g}",
             f"ampeg_release={model['release']:g}", ""]
    jobs = []
    for key in sorted(k for k in keys if k in model["keys"]):
        path = folder / f"k{key}.flac"
        jobs.append((name, key, path))
        region = f"<region> sample={name}/{path.name} key={key} pitch_keycenter={key}"
        if model["loop"]:
            region += (f" loop_mode=loop_continuous loop_start={int(LEAD * RATE)}"
                       f" loop_end={int((LEAD + LOOP_SECONDS) * RATE) - 1}")
        lines.append(region)
    with ProcessPoolExecutor() as pool:
        list(pool.map(sample, jobs))
    sfz = out / f"{name}.sfz"
    sfz.write_text("\n".join(lines) + "\n")
    return sfz


# ---- the pieces ----------------------------------------------------------

# Each part: instrument, role, level against the pad (dB), pan, send into the hall
PARTS = {
    "pad": ("amb-pad", "piano", 0.0, 0.0, 0.55),
    "choir": ("amb-choir", "pad", -5.0, 0.0, 0.7),
    "sub": ("amb-sub", "low", -7.0, 0.0, 0.1),
    "bells": ("amb-bell", "melody2", -2.0, 0.15, 0.75),
    "glass": ("amb-glass", "melody2", -4.0, -0.15, 0.8),
    "toll": ("amb-bell", "low", -5.0, -0.1, 0.8),
    "drone": ("drone", "drone", -12.0, 0.0, 0.4),
}


def compose_ambient(score: dict, folder: Path) -> str:
    import compose as c  # dark/compose.py: its pieces, chords and parts
    from arrange import write_part

    piece = c.Piece(score)
    rng = random.Random(score.get("seed", 11))
    gains = score.get("gains", {})

    def part(name: str):
        instrument, role, _, pan, reverb = PARTS[name]
        return piece.part(name, instrument, role, pan, reverb)

    def strength(tick: int, base: float, low: float = 30, span: float = 60) -> float:
        start, end, section = next(x for x in piece.sections if x[0] <= tick < x[1])
        dyn = section.get("dyn", 0.4)
        swell = section.get("swell", 0.0) * (tick - start) / max(1, end - start)
        return low + span * min(1.0, max(0.0, dyn + swell)) + base + rng.uniform(-3, 3)

    tail = piece.bar  # the last chord rings a bar longer
    held = {}  # (part, note): [start, velocity] of a tone still sounding

    def hold(name: str, notes: list, tick: int, end: int, velocity: float) -> None:
        """These notes sound from tick: a note already sounding goes on; one not wanted any more ends."""
        p = part(name)
        for key in [k for k in held if k[0] == name and k[1] not in notes]:
            start, v = held.pop(key)
            p.add(start, key[1], v, tick - start + piece.ms(400))
        for n in notes:
            if (name, n) not in held:
                held[(name, n)] = [tick + rng.randint(0, int(piece.ms(700))), velocity]
        if end is not None:
            for key in [k for k in held if k[0] == name]:
                start, v = held.pop(key)
                p.add(start, key[1], v, end - start)

    tonic = c.chord(score["sections"][0]["chords"].split("|")[0].split()[0].split(":")[0])[2]
    for start, end, section in piece.sections:  # drone: compose.py's low tonic and fifth, through the section
        if "drone" in section.get("layers", []):
            for n in (c.above(tonic, 26), c.above(tonic, 26) + 7):
                part("drone").add(start, n, 70, end - start + (tail if end == piece.end else 0))
    voices = {"pad": [45, 52, 57, 60], "choir": [64, 67, 71]}
    spans = piece.spans
    for index, (tick, length, name) in enumerate(spans):
        section = piece.section_at(tick)
        wanted = section.get("layers", ["pad"])
        nxt = spans[index + 1] if index + 1 < len(spans) else None
        nxt_wanted = piece.section_at(nxt[0]).get("layers", []) if nxt else []
        bass, tones, root = c.chord(name)
        for layer in ("pad", "choir", "sub"):
            if layer not in wanted:
                continue
            if layer == "pad":
                voices["pad"] = c.voice(voices["pad"], tones, 43, 67, 4)
                notes = sorted(set(voices["pad"]))
                low = c.above(bass, 36)
                notes = sorted(set([low] + notes[1:]))
            elif layer == "choir":
                colour = [t for t in tones if t != root] or tones
                voices["choir"] = c.voice(voices["choir"], colour, 60, 76, 3)
                notes = sorted(set(voices["choir"]))
            else:
                notes = [c.above(bass, score.get("sub_low", 26))]
            ends = None if (nxt and layer in nxt_wanted) else tick + length + (tail if not nxt else piece.ms(800))
            hold(layer, notes, tick, ends, strength(tick, {"pad": 0, "choir": -6, "sub": -4}[layer]))
        if "toll" in wanted:
            every = section.get("toll_every", 1)
            if index % every == 0:
                note = c.above(root, score.get("toll_low", 48))
                part("toll").add(tick + piece.ms(rng.uniform(0, 150)), note, strength(tick, 4, 30, 50), piece.bar * 4)
    for t, notes, length in piece.tune:  # the tune: on the bell or the glass, struck and left ringing
        section = piece.section_at(t)
        layer = "glass" if "glass" in section.get("layers", []) else "bells"
        for n in notes:
            at = t + piece.ms(rng.gauss(0, 25))
            part(layer).add(at, n, strength(t, 6, 34, 50), max(length, piece.bar * 2))
    for start, end, section in piece.sections:  # an answer: a second line, on the bell, low, under the tune
        tick = start
        for token in section.get("answer", "").replace("|", " ").split():
            pitches, _, beats = token.partition(":")
            if pitches != "r":
                for n in pitches.split("+"):
                    part("bells").add(tick + piece.ms(rng.gauss(0, 25)), c.note_number(n),
                                      strength(tick, 2, 32, 50), piece.bar * 2)
            tick += round(float(beats or 1) * c.TICKS)
        if tick not in (start, end):
            raise ValueError(f"an answer lasting {(tick - start) / piece.bar} bars, not {(end - start) // piece.bar}")

    folder.mkdir(parents=True, exist_ok=True)
    sheet = []
    for name, p in piece.parts.items():
        write_part(p, piece.tempos, folder / f"{name}.mid", (piece.beats, 2))
        library, sfz, _ = c.INSTRUMENTS[p.instrument]
        sheet.append({"part": name, "library": library, "sfz": sfz, "role": p.role,
                      "gain_db": PARTS[name][2] + gains.get(name, 0.0), "pan": p.pan,
                      "reverb": p.reverb, "tone": p.tone, "notes": len(p.notes)})
    room = score.get("room", {"rt60": 6.0, "wet": 1.0})
    mix = {"hall": {"rt60": room["rt60"], "wet": room.get("wet", 1.0)}, "parts": sheet,
           "master": {"tone": 0.0, "air": 0.0, "width": 0.0, "level": 0.0},
           "loudness": score.get("loudness", -16)}
    (folder / "mix.json").write_text(json.dumps(mix, indent=2))
    return (f"{folder.name}: ambient, {piece.bpm} bpm, {piece.end // piece.bar} bars, "
            f"{piece.seconds(0, piece.end + piece.bar):.0f} s, parts {', '.join(piece.parts)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--models", nargs="+", default=list(MODELS))
    parser.add_argument("--keys", nargs="+", type=int)
    args = parser.parse_args()
    for name in args.models:
        print(build(name, args.out, args.keys or MODELS[name]["keys"]), flush=True)


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()
