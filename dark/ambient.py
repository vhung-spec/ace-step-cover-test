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
- amb-wind: wind in a hollow, faintly at the note, in gusts; looped;
- amb-pulse: a heartbeat's deep thud;
- amb-organ: a pipe organ far off, soft flue ranks; looped;
- amb-drop: a water drop in a cave pool;
- amb-box: an old music box, a little out of tune;
- amb-bowl: a singing bowl, rubbed, wobbling slowly;
- amb-bowed: a low string section, soft, from its harmonics through a string
  body's resonances, each player's own vibrato; looped; amb-bowsolo: one such
  voice singing a tune, a fuller vibrato;
- amb-thunder: thunder far off, its roll only, deep;
- amb-waves: the sea far off at night, soft swells of deep surf (for sleep);
- darkwave: amb-synbass (a dark synth bass, its filter snapping shut),
  amb-arp (a cold, hollow synth pluck), amb-kick and amb-snare (a soft beat);
  cinematic: amb-timpani (soft-mallet timpani, its kettle's modes);
- amb-pluck: a plucked zither-like string (Karplus-Strong), darker as it dies;
- amb-glass: a soft glass/bowl tone, nearly pure: the note, a faint octave
  and twelfth, slow beating, a long ring; for the few notes of a tune.

The pieces (compose_ambient): chords held as long as they last, a tone
common to two chords held across them; layers, per section:
  pad (the chord, three or four tones, low and middle), choir (the chord's
  colour tones above the pad), sub (the root, deep), bells (the section's
  melody on the bell, if any), glass (its melody on the glass), toll (a low
  bell on the chord's root at each chord, or every toll_every chords),
  drone (compose.py's drone), wind (wind sounding the chord's root and
  fifth), pulse (a heartbeat on the root every pulse_beats), shimmer (soft
  high glass on the chord's tones, at random), organ (the chord on the
  organ), bowl (a singing bowl on the root, every bowl_every chords), box
  (the melody on the music box, before glass and bells), strings (low bowed
  strings holding the chord), solo (the melody sung on one bowed string,
  before all others), thunder (far thunder at a chord, thunder_odds), waves (the sea),
  felt (the dark piano's felt piano, barely touched, the chord's tones every
  felt_beats; with a melody, the tune on it before all others), bassline
  (synth bass in eighths), arp (an arpeggio in eighths, arp16: sixteenths),
  beat (kick and snare; kick_and: a kick between), timpani (a stroke a
  chord, or "timpani": "roll" in a section, swelling with it), pluck (the
  melody on the plucked string, first of all), pluckarp (the chord broken on
  it, pluck_beats); bass_step (the bassline's note length, beats), felt_chords
  (the felt piano's chords whole), answer_on "solo" (the answer on the string), pianoarp (the ambient piano breaking the chord
  in eighths, arp_quarters: quarters; keys_range), improv (a melody improvised
  through the section on this instrument: felt, keys, glass, pluck, box, bells
  or solo; motif: improvised once over motif_bars and repeated;
  improv_range, improv_density; the score's mode: aeolian, dorian, lydian,
  major, pentatonic; seed), tune_on (the
  instrument the section's tune is played on, before the order above), drops (water drops on the chord's tones, drops_per_bar); "answer", a second line beside the melody,
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
    "amb-wind": {"attack": 5.0, "release": 7.0, "veltrack": 60, "keys": range(40, 84), "loop": True},
    "amb-pulse": {"attack": 0.002, "release": 0.4, "veltrack": 70, "keys": range(24, 48), "loop": False,
                  "seconds": 2.0},
    "amb-organ": {"attack": 0.25, "release": 1.5, "veltrack": 50, "keys": range(36, 85), "loop": True},
    "amb-drop": {"attack": 0.001, "release": 0.5, "veltrack": 70, "keys": range(60, 97), "loop": False,
                 "seconds": 2.5},
    "amb-box": {"attack": 0.001, "release": 1.5, "veltrack": 70, "keys": range(60, 97), "loop": False,
                "seconds": 6.0},
    "amb-bowl": {"attack": 0.4, "release": 6.0, "veltrack": 70, "keys": range(43, 80), "loop": False,
                 "seconds": 24.0},
    "amb-bowed": {"attack": 1.2, "release": 3.0, "veltrack": 60, "keys": range(28, 80), "loop": True},
    "amb-bowsolo": {"attack": 0.35, "release": 1.2, "veltrack": 60, "keys": range(36, 84), "loop": True},
    "amb-thunder": {"attack": 0.01, "release": 3.0, "veltrack": 60, "keys": range(24, 36), "loop": False,
                    "seconds": 12.0},
    "amb-waves": {"attack": 6.0, "release": 8.0, "veltrack": 50, "keys": range(40, 56), "loop": True},
    # darkwave and the cinematic: struck sounds, played to their end whatever the note's length (one_shot)
    "amb-synbass": {"attack": 0.003, "release": 0.25, "veltrack": 60, "keys": range(26, 56), "loop": False,
                    "seconds": 3.0},
    "amb-arp": {"attack": 0.003, "release": 0.4, "veltrack": 60, "keys": range(52, 90), "loop": False,
                "seconds": 2.5},
    "amb-kick": {"attack": 0.001, "release": 0.3, "veltrack": 70, "keys": range(24, 37), "loop": False,
                 "seconds": 1.2, "one_shot": True},
    "amb-snare": {"attack": 0.001, "release": 0.3, "veltrack": 70, "keys": range(36, 44), "loop": False,
                  "seconds": 1.0, "one_shot": True},
    "amb-timpani": {"attack": 0.001, "release": 2.5, "veltrack": 80, "keys": range(33, 58), "loop": False,
                    "seconds": 6.0, "one_shot": True},
    "amb-pluck": {"attack": 0.001, "release": 1.2, "veltrack": 70, "keys": range(40, 90), "loop": False,
                  "seconds": 5.0},
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


def wind(key: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """Wind through a hollow, sounding faintly at the note: noise through three narrow bands around it whose
    weights wander (the pitch bends a few per cent), in gusts, over a dark rush under 300 Hz; nothing above
    2 kHz (no hiss)."""
    from scipy.signal import butter as _b, sosfiltfilt as _f
    f0 = hz(key)
    out = np.zeros((2, n))
    for side in range(2):
        noise = rng.standard_normal(n)
        tone = np.zeros(n)
        for k, shift in enumerate((0.97, 1.0, 1.03)):
            band = _f(_b(2, [f0 * shift / 1.04, f0 * shift * 1.04], "band", fs=RATE, output="sos"), noise)
            weight = np.clip(0.5 + 0.6 * wander(n, rng, 0.15), 0, 1)
            tone += band * weight / np.sqrt(np.mean(band ** 2) + 1e-12)
        rush = lowpass(rng.standard_normal(n), 300, 2)
        rush /= np.sqrt(np.mean(rush ** 2)) + 1e-12
        gust = np.clip(0.55 + 0.45 * wander(n, rng, 0.12), 0.1, 1.2)
        out[side] = lowpass((tone + 0.35 * rush) * gust, 2000, 4)
    return out


def pulse(key: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """A heartbeat's thud: a deep sine falling half an octave into its note in 50 ms, dying in 0.4 s, a soft
    knock of felt on it."""
    f0 = hz(key)
    t = np.arange(n) / RATE
    freq = f0 * (1 + 0.5 * np.exp(-t / 0.025))
    tone = np.sin(2 * np.pi * np.cumsum(freq) / RATE) * np.exp(-t / 0.22) * (1 - np.exp(-t / 0.003))
    knock = lowpass(rng.standard_normal(n) * np.exp(-t / 0.012), 400, 2) * 0.15
    mono = tone + knock
    return np.stack([mono, mono])


def organ(key: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """A pipe organ far off in a stone hall: two soft flue ranks a few cents apart (8' with 4', a little
    2 2/3' and 2', and a 16' under the middle and upper notes), each pipe's level breathing a little;
    nothing above 3.5 kHz."""
    f0 = hz(key)
    t = np.arange(n) / RATE
    ranks = [(1, 0), (2, -7), (3, -15), (4, -16), (6, -24)] + ([(0.5, -9)] if key >= 48 else [])
    out = np.zeros((2, n))
    for side in range(2):
        for cents in ((-2.0, 1.5), (-1.0, 2.5))[side]:
            for ratio, db in ranks:
                freq = f0 * ratio * 2 ** (cents / 1200)
                if freq > 3500:
                    continue
                level = 10 ** ((db + 0.6 * wander(n, rng, 0.2)) / 20)
                out[side] += level * np.sin(2 * np.pi * freq * t + rng.random() * 6.28)
    return out


def drop(key: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """A water drop falling into a still pool in a cave: a pure tone rising a little as the bubble rings
    (a fifth of its pitch in 30 ms), dying in a third of a second, placed at random between the sides."""
    f0 = hz(key)
    t = np.arange(n) / RATE
    freq = f0 * (1 + 0.2 * (1 - np.exp(-t / 0.03)))
    tone = np.sin(2 * np.pi * np.cumsum(freq) / RATE) * np.exp(-t / 0.12) * (1 - np.exp(-t / 0.0015))
    tone += 0.25 * np.sin(2 * np.pi * np.cumsum(freq * 2.0) / RATE) * np.exp(-t / 0.05)
    place = rng.uniform(0.2, 0.8)
    return np.stack([tone * np.sqrt(1 - place), tone * np.sqrt(place)])


def box(key: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """An old music box's tine, a little out of tune (each key its own -14..+14 cents): the note, the
    tine's own high partials (5.4 and 13.3 times, dying fast), a faint hollow body under it; ringing 4 s."""
    f0 = hz(key) * 2 ** (rng.uniform(-14, 14) / 1200)
    t = np.arange(n) / RATE
    tone = np.sin(2 * np.pi * f0 * t) * np.exp(-t / 1.4)
    for ratio, db, ring in ((5.4, -20, 0.2), (13.3, -32, 0.05)):
        if f0 * ratio < 4500:
            tone += 10 ** (db / 20) * np.sin(2 * np.pi * f0 * ratio * t + rng.random() * 6.28) * np.exp(-t / ring)
    tone += 0.12 * np.sin(2 * np.pi * f0 / 2 * t) * np.exp(-t / 0.4)  # the box's hollow
    tone *= 1 - np.exp(-t / 0.0008)
    place = rng.uniform(0.35, 0.65)
    return np.stack([tone * np.sqrt(1 - place), tone * np.sqrt(place)])


def bowl(key: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """A singing bowl rubbed with a wooden stick: its modes (1, 2.71, 5.15 times the note), each split in
    two a few hertz apart, so it wobbles slowly; swelling in as it is rubbed, ringing on long after."""
    f0 = hz(key)
    t = np.arange(n) / RATE
    swell = np.minimum(1, t / 3.0) ** 1.5 * np.exp(-np.maximum(0, t - 5.0) / 6.0)
    mono = np.zeros(n)
    for ratio, db in ((1, 0), (2.71, -9), (5.15, -20)):
        freq = f0 * ratio
        if freq > 5000:
            continue
        wobble = rng.uniform(1.5, 4.0) * (1 if ratio == 1 else 1.6)
        for sign in (-1, 1):
            mono += 0.5 * 10 ** (db / 20) * np.sin(2 * np.pi * (freq + sign * wobble / 2) * t + rng.random() * 6.28)
    mono *= swell
    return np.stack([mono, np.roll(mono, int(0.011 * RATE))])  # the same bowl, one side a little later: wide, even


# A bowed string's body: its resonances (Hz, bandwidth, dB), the lower ones strongest: a dark section sound.
BODY = [(280, 160, 0.0), (520, 220, -2.0), (1100, 420, -7.0), (2400, 800, -16.0)]


def body_gain(freq: np.ndarray) -> np.ndarray:
    gain = np.full_like(freq, 10 ** (-30 / 20))
    for centre, width, db in BODY:
        gain += 10 ** (db / 20) / (1 + ((freq - centre) / (width / 2)) ** 2)
    return gain


def bowed_voices(key: int, n: int, rng: np.random.Generator, players: int, depth_cents: float,
                 spread_cents: float) -> np.ndarray:
    """Bowed strings, made from their harmonics (a bowed string's 1/k, through the body's resonances),
    each player their own vibrato (5-6 Hz, growing in), tuning and bow pressure, wandering a little."""
    f0 = hz(key)
    harmonics = np.arange(1, max(2, int(4000 / f0)) + 1)
    amps = body_gain(harmonics * f0) / harmonics
    out = np.zeros((2, n))
    t = np.arange(n) / RATE
    for side in range(2):
        for _ in range(players):
            rate = rng.uniform(5.0, 6.0)
            depth = depth_cents * rng.uniform(0.7, 1.2) * np.minimum(1, t / 1.0)
            cents = rng.uniform(-spread_cents, spread_cents) + 2 * wander(n, rng, 0.1) + depth * np.sin(
                2 * np.pi * np.cumsum(rate * (1 + 0.05 * wander(n, rng, 0.3))) / RATE)
            phase = 2 * np.pi * np.cumsum(f0 * 2 ** (cents / 1200)) / RATE
            pressure = 10 ** (1.5 * wander(n, rng, 0.3) / 20)
            voice = np.zeros(n)
            for k, a in zip(harmonics, amps):
                voice += a * np.sin(k * phase + rng.random() * 6.28)
            out[side] += voice * pressure
    return out


def bowed(key: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """A low string section, soft, playing as one: four players a side."""
    return bowed_voices(key, n, rng, 4, 9.0, 7.0)


def bowsolo(key: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """One cello-like voice singing a tune: a fuller vibrato, a single player (the two sides the same
    player through a slightly different place in the room)."""
    one = bowed_voices(key, n, rng, 1, 16.0, 0.0)[0]
    return np.stack([one, np.roll(one, int(0.009 * RATE))])


def thunder(key: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """Thunder far away: no crack, only the roll: deep noise (under 220 Hz) in a few overlapping rumbles
    over its first 3 s, each dying over 2-4 s."""
    t = np.arange(n) / RATE
    out = np.zeros((2, n))
    for side in range(2):
        noise = lowpass(rng.standard_normal(n), 220, 4)
        env = np.zeros(n)
        for _ in range(rng.integers(3, 6)):
            at = rng.uniform(0, 3.0)
            env += rng.uniform(0.4, 1.0) * np.where(t >= at, (1 - np.exp(-(t - at) / 0.25)) *
                                                     np.exp(-np.maximum(0, t - at) / rng.uniform(1.5, 3.5)), 0)
        out[side] = noise * env
    return out


def waves(key: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """The sea at night, far off, for sleep: soft swells of deep surf, one every 7.5 s (four to the loop,
    so the loop never jumps), each rising darker to brighter and falling back; the key sets nothing but
    the seed. Nothing above 1.2 kHz: a hush, never a hiss."""
    t = np.arange(n) / RATE
    out = np.zeros((2, n))
    for side in range(2):
        noise = rng.standard_normal(n)
        deep, wash = lowpass(noise, 280, 2), lowpass(noise, 1100, 4)
        deep /= np.sqrt(np.mean(deep ** 2)); wash /= np.sqrt(np.mean(wash ** 2))
        phase = 2 * np.pi * t / 7.5 + side * 0.6 + rng.random() * 0.4
        swell = (0.5 - 0.5 * np.cos(phase)) ** 2  # 0..1, rising slowly, breaking, falling away
        level = 0.35 + 0.65 * swell * (0.85 + 0.15 * wander(n, rng, 0.2))
        out[side] = (deep * (1 - 0.5 * swell) + wash * 0.6 * swell) * level
    return out


def synbass(key: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """A dark synth bass (darkwave): two sawtooths a few cents apart and a sine an octave under, its
    filter snapping shut after the note speaks (bright for 0.1 s, then dark), the level easing to 60 %."""
    f0 = hz(key)
    t = np.arange(n) / RATE
    step = f0 / RATE
    raw = saw(rng.random() + np.cumsum(np.full(n, step * 2 ** (-6 / 1200))), np.full(n, step)) \
        + saw(rng.random() + np.cumsum(np.full(n, step * 2 ** (6 / 1200))), np.full(n, step))
    bright, dark = lowpass(raw, max(8 * f0, 700), 2), lowpass(raw, max(2 * f0, 160), 4)
    shut = np.exp(-t / 0.08)
    tone = bright * shut + dark * (1 - shut) + 0.9 * np.sin(np.pi * f0 * t)
    tone *= (0.6 + 0.4 * np.exp(-t / 0.3)) * (1 - np.exp(-t / 0.002))
    return np.stack([tone, tone])


def arp(key: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """A cold synth pluck for arpeggios: a hollow (odd-harmonic) tone, soft-edged (nothing above 3.5 kHz),
    dying in half a second, two voices a few cents apart, one a side."""
    f0 = hz(key)
    t = np.arange(n) / RATE
    out = np.zeros((2, n))
    for side, cents in enumerate((-5, 5)):
        f = f0 * 2 ** (cents / 1200)
        for k in range(1, 40, 2):
            if f * k > 3500:
                break
            out[side] += np.sin(2 * np.pi * f * k * t + rng.random() * 6.28) / k * np.exp(-t * (2 + 0.6 * k))
    return out * (1 - np.exp(-t / 0.002))


def kick(key: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """A soft, deep kick drum: a sine falling from 2.4 times its note to it in 60 ms, dying in 0.3 s, a
    muffled click on it."""
    f0 = hz(key)
    t = np.arange(n) / RATE
    freq = f0 * (1 + 1.4 * np.exp(-t / 0.03))
    tone = np.sin(2 * np.pi * np.cumsum(freq) / RATE) * np.exp(-t / 0.18)
    click = lowpass(rng.standard_normal(n) * np.exp(-t / 0.004), 1500, 2) * 0.25
    mono = (tone + click) * (1 - np.exp(-t / 0.0007))
    return np.stack([mono, mono])


def snare(key: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """A soft snare, brushed rather than cracked: a short drum tone (190 Hz) and its wires (noise between
    1 and 5 kHz) dying in a tenth of a second; nothing harsh above."""
    from scipy.signal import butter as _b, sosfiltfilt as _f
    t = np.arange(n) / RATE
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05)
    out = np.zeros((2, n))
    for side in range(2):
        wires = _f(_b(2, [1000, 5000], "band", fs=RATE, output="sos"), rng.standard_normal(n)) * np.exp(-t / 0.09)
        wires /= np.abs(wires).max() + 1e-12
        out[side] = (body + 0.7 * wires) * (1 - np.exp(-t / 0.001))
    return out


# A timpani's modes (ratio to the note, level, ring s)
TIMPANI = [(1.0, 1.0, 3.0), (1.504, 0.5, 1.8), (1.742, 0.3, 1.2), (2.0, 0.35, 1.4), (2.245, 0.2, 1.0),
           (2.494, 0.15, 0.8)]


def timpani(key: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """A timpani struck with soft mallets: its kettle's modes (the note, then 1.5, 1.74, 2, 2.25 and 2.5
    times), the pitch settling a little as it rings, the felt's thump."""
    f0 = hz(key)
    t = np.arange(n) / RATE
    glide = 1 + 0.012 * np.exp(-t / 0.08)
    out = np.zeros((2, n))
    for side in range(2):
        for ratio, level, ring in TIMPANI:
            out[side] += level * rng.uniform(0.85, 1.0) * np.exp(-t / ring) * np.sin(
                2 * np.pi * np.cumsum(f0 * ratio * glide) / RATE + rng.random() * 6.28)
        out[side] += lowpass(rng.standard_normal(n) * np.exp(-t / 0.02), 300, 2) * 0.4
    return out * (1 - np.exp(-t / 0.002))


def pluck(key: int, n: int, rng: np.random.Generator) -> np.ndarray:
    """A plucked silk-and-steel string, as a zither's (Karplus-Strong: a burst of soft noise circulating in
    a delay the length of the note's period, losing a little of its highs each pass, so it rings darker
    as it dies), plucked a fifth of the way along, through a small wooden body; ringing 3-4 s."""
    f0 = hz(key)
    period = RATE / f0
    N = int(period)
    frac = period - N
    out = np.zeros((2, n))
    for side in range(2):
        y = np.zeros(n + N + 3)
        burst = lowpass(rng.standard_normal(N + 2), min(3000, 6 * f0), 2)
        burst -= 0.5 * np.roll(burst, int(N / 5))  # plucked a fifth along: its fifth harmonics weaker
        y[:N + 2] = burst / (np.abs(burst).max() + 1e-12)
        ring = 6.0 * (220 / f0) ** 0.3  # to -60 dB, s: the bass rings longer
        loss = 10 ** (-3 / (ring * f0))
        pos = N + 2
        while pos < n + N + 3:  # a period at a time: each sample from the ones a period (and a little) before
            end = min(pos + N, n + N + 3)
            a, b, c2 = y[pos - N:end - N], y[pos - N - 1:end - N - 1], y[pos - N - 2:end - N - 2]
            y[pos:end] = loss * ((1 - frac) * 0.5 * (a + b) + frac * 0.5 * (b + c2))
            pos = end
        tone = y[:n]
        t = np.arange(n) / RATE
        tone = tone + 0.25 * lowpass(tone, 400, 2)  # the wooden body
        out[side] = tone * (1 - np.exp(-t / 0.0008))
    return out


SYNTHS = {"amb-pad": pad, "amb-choir": choir, "amb-sub": sub, "amb-bell": bell, "amb-glass": glass, "amb-wind": wind, "amb-pulse": pulse, "amb-organ": organ,
          "amb-drop": drop, "amb-box": box, "amb-bowl": bowl,
          "amb-bowed": bowed, "amb-bowsolo": bowsolo, "amb-thunder": thunder, "amb-waves": waves,
          "amb-synbass": synbass, "amb-arp": arp, "amb-kick": kick, "amb-snare": snare, "amb-timpani": timpani,
          "amb-pluck": pluck}


def sample(job: tuple) -> None:
    name, key, path = job
    rng = np.random.default_rng(key * 101 + sum(map(ord, name)))
    model = MODELS[name]
    seconds = LEAD + LOOP_SECONDS if model["loop"] else model.get("seconds", 24.0)
    n = int(seconds * RATE)
    audio = SYNTHS[name](key, n, rng)
    if model["loop"]:  # the loop's end crossfaded into what comes before its start, so it runs on unbroken
        start, fade = int(LEAD * RATE), int(FADE * RATE)
        w = np.sin(0.5 * np.pi * np.arange(fade) / fade)
        audio[:, n - fade:] = audio[:, n - fade:] * np.cos(0.5 * np.pi * np.arange(fade) / fade) \
            + audio[:, start - fade:start] * w
        level = np.sqrt(np.mean(audio[:, start:] ** 2))
    else:
        level = np.sqrt(np.mean(audio[:, : int(min(1.0, seconds / 4) * RATE)] ** 2))
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
        if model.get("one_shot"):
            region += " loop_mode=one_shot"
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
    "wind": ("amb-wind", "pad", -8.0, 0.0, 0.6),
    "pulse": ("amb-pulse", "low", -6.0, 0.0, 0.15),
    "shimmer": ("amb-glass", "pad", -12.0, 0.0, 0.9),
    "organ": ("amb-organ", "piano", 0.0, 0.0, 0.85),
    "drops": ("amb-drop", "pad", -12.0, 0.0, 0.85),
    "box": ("amb-box", "melody2", -3.0, 0.0, 0.6),
    "bowl": ("amb-bowl", "pad", -6.0, 0.0, 0.3),
    "strings": ("amb-bowed", "piano", -2.0, 0.0, 0.6),
    "solo": ("amb-bowsolo", "melody2", -1.0, -0.1, 0.55),
    "thunder": ("amb-thunder", "low", -6.0, 0.0, 0.5),
    "waves": ("amb-waves", "pad", -9.0, 0.0, 0.2),
    "felt": ("model-dream", "melody2", -5.0, 0.0, 0.6),
    "keys": ("model-dream", "piano", 0.0, 0.0, 0.6),
    "keysarp": ("model-dream", "piano", -3.0, 0.0, 0.6),
    "bassline": ("amb-synbass", "bass", -3.0, 0.0, 0.1),
    "arp": ("amb-arp", "pad", -7.0, 0.0, 0.45),
    "kick": ("amb-kick", "low", -4.0, 0.0, 0.08),
    "snare": ("amb-snare", "pad", -10.0, 0.0, 0.35),
    "timpani": ("amb-timpani", "low", -2.0, 0.0, 0.5),
    "pluck": ("amb-pluck", "melody2", -3.0, 0.1, 0.55),
    "pluckarp": ("amb-pluck", "pad", -9.0, -0.15, 0.6),
}

MODES = {"aeolian": (0, 2, 3, 5, 7, 8, 10), "dorian": (0, 2, 3, 5, 7, 9, 10), "lydian": (0, 2, 4, 6, 7, 9, 11),
         "major": (0, 2, 4, 5, 7, 9, 11), "pentatonic": (0, 3, 5, 7, 10)}


def improvise(piece, c, section: dict, start: int, end: int, rng: random.Random, tonic: int, mode: str,
              low: int, high: int, density: float) -> list:
    """A melody made up as it goes, as a player improvising slowly at night: phrases of two to four bars,
    each followed by a rest of one to three bars; notes of one to three beats (a few halves), each a step
    or two along the scale from the last (now and then a leap of a third or fourth, then back), the line
    rising through the first half of a phrase and falling through the second; a note held two beats or
    more, and every phrase's last, always one of the chord's own tones, so nothing rubs. density: about
    how many notes a bar. Returns (tick, note, beats)."""
    scale = sorted({(tonic + i) % 12 for i in MODES[mode]})
    pitches = [n for n in range(low, high + 1) if n % 12 in scale]
    chord_at = lambda tick: next((n for t, l, n in piece.spans if t <= tick < t + l), piece.spans[-1][2])
    notes, tick = [], start + rng.choice([0, c.TICKS, 2 * c.TICKS])
    index = len(pitches) // 2
    while tick < end - piece.bar:
        bars = rng.choice([2, 3, 3, 4])
        phrase_end = min(end - c.TICKS, tick + bars * piece.bar)
        begin = tick
        third = len(pitches) // 3  # each phrase sets out from the middle of the range, so it never sinks
        index = rng.randrange(third, max(third + 1, 2 * third))
        previous = None
        while tick < phrase_end:
            longest = max(1.0, min(3.0, 2.0 / max(0.3, density)))
            beats = rng.choice([b for b in (0.5, 1.0, 1.5, 2.0, 3.0) if b <= longest + 0.5] or [1.0])
            if beats == 0.5 and rng.random() < 0.5:
                beats = 1.0
            through = (tick - begin) / max(1, phrase_end - begin)
            lean = 1 if through < 0.5 else -1  # up, then down
            move = rng.choice([1, 1, 1, 2, 2]) * (lean if rng.random() < 0.7 else -lean)
            if rng.random() < 0.12:
                move = lean * rng.choice([3, 4])
            if not 0 <= index + move < len(pitches):  # at the edge of the range: turn back
                move = -move
            index = max(0, min(len(pitches) - 1, index + move))
            note = pitches[index]
            length = round(beats * c.TICKS)
            last = tick + length >= phrase_end
            tones = c.chord(chord_at(tick))[1]
            if (beats >= 2 or last) and note % 12 not in tones:  # held: a chord tone, the nearest
                note = min((n for n in pitches if n % 12 in tones), key=lambda n: (abs(n - note), n), default=note)
                index = pitches.index(note) if note in pitches else index
            if note == previous:  # not the same note again: one step toward the middle
                index += 1 if index < len(pitches) // 2 else -1
                note = pitches[index]
            previous = note
            if last:
                length = max(length, 2 * c.TICKS)
            notes.append((tick, note, length / c.TICKS))
            tick += length
        tick += rng.choice([1, 2, 2, 3]) * piece.bar  # a breath between phrases
        tick -= (tick - start) % c.TICKS
    return notes


def compose_ambient(score: dict, folder: Path) -> str:
    import compose as c  # dark/compose.py: its pieces, chords and parts
    from arrange import write_part

    piece = c.Piece(score)
    rng = random.Random(score.get("seed", 11))
    gains = score.get("gains", {})

    def part(name: str):
        instrument, role, _, pan, reverb = PARTS[name]
        if name in ("keys", "keysarp") and score.get("keys"):  # the ambient piano: another of the modelled pianos
            instrument = score["keys"]
        made = name not in piece.parts
        p = piece.part(name, instrument, role, pan, reverb)
        if made and name == "felt":  # the dark piano's dreamy felt piano, softer still, its strike eased
            p.tone.update({"attack": 0.06, "lowpass": 2500, "lowpass_order": 2, "width": 0.8})
            p.cap = 46
        if made and name in ("keys", "keysarp"):  # ambient piano: the same dreamy piano, clearer, a little narrower
            p.tone.update({"attack": 0.02, "lowpass": 4500, "lowpass_order": 2, "width": 0.8})
            p.tone.update(score.get("keys_tone", {}))
            if p.tone.get("lowpass") is None:
                p.tone.pop("lowpass", None)
            p.cap = 72
        return p

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
        for layer in ("pad", "choir", "sub", "wind", "organ", "strings", "waves"):
            if layer not in wanted:
                continue
            if layer == "pad":
                voices["pad"] = c.voice(voices["pad"], tones, *score.get("pad_range", [43, 67]), 4)
                notes = sorted(set(voices["pad"]))
                low = c.above(bass, score.get("pad_range", [43])[0] - 7)
                notes = sorted(set([low] + notes[1:]))
            elif layer == "choir":
                colour = [t for t in tones if t != root] or tones
                voices["choir"] = c.voice(voices["choir"], colour, *score.get("choir_range", [60, 76]), 3)
                notes = sorted(set(voices["choir"]))
            elif layer == "organ":  # the organ: the chord in the middle, its bass an octave and more under
                voices["organ"] = c.voice(voices.get("organ", [55, 60, 64]), tones, *score.get("organ_range", [52, 72]), 3)
                notes = sorted(set(voices["organ"] + [c.above(bass, 36)]))
            elif layer == "strings":  # low strings: the chord low and close, its bass under it
                voices["strings"] = c.voice(voices.get("strings", [50, 55, 58]), tones,
                                            *score.get("strings_range", [45, 64]), 3)
                notes = sorted(set(voices["strings"] + [c.above(bass, 33)]))
            elif layer == "waves":  # the sea: one held note (its key only seeds the sound)
                notes = [48]
            elif layer == "wind":  # the wind sounding the chord's root and fifth, low-middle
                notes = sorted({c.above(root, 45), c.above((root + 7) % 12, 52)})
            else:
                notes = [c.above(bass, score.get("sub_low", 26))]
            ends = None if (nxt and layer in nxt_wanted) else tick + length + (tail if not nxt else piece.ms(800))
            hold(layer, notes, tick, ends, strength(tick, {"pad": 0, "choir": -6, "sub": -4, "wind": -2, "organ": -4, "strings": -2, "waves": 0}[layer]))
        if "thunder" in wanted and rng.random() < section.get("thunder_odds", 0.5):  # thunder far off, now and then
            part("thunder").add(tick + rng.randrange(0, max(1, length // 2)), 24 + rng.randrange(12),
                                strength(tick, 0, 40, 50), piece.bar * 2)
        if "bassline" in wanted:  # darkwave's bass: eighths on the chord's bass, an octave up on every fourth
            low = c.above(bass, score.get("bass_low", 28))
            step = round(section.get("bass_step", 0.5) * c.TICKS)
            octave = step == c.EIGHTH  # eighths leap the octave on every fourth; longer notes stay put
            for k, at in enumerate(range(tick, tick + length, step)):
                part("bassline").add(at, low + (12 if octave and k % 4 == 3 else 0),
                                     strength(at, -2 if k % 2 else 4, 40, 40), step - 20)
        if "arp" in wanted:  # a cold arpeggio: the chord's tones up and down in eighths (sixteenths if asked)
            ladder = [n for n in range(*score.get("arp_range", [57, 77])) if n % 12 in tones][:5]
            order = ladder + ladder[-2:0:-1]
            step = c.EIGHTH // (2 if section.get("arp16") else 1)
            for k, at in enumerate(range(tick, tick + length, step)):
                part("arp").add(at, order[k % len(order)], strength(at, 4 if k % 4 == 0 else -2, 34, 36), step * 2)
        if "beat" in wanted:  # a soft, steady beat: the kick on one and three, the snare on two and four
            for b in range(0, length // c.TICKS):
                at = tick + b * c.TICKS
                if b % 2 == 0:
                    part("kick").add(at, 31, strength(at, 6, 50, 40), c.TICKS)
                    if section.get("kick_and") and b % 4 == 2:
                        part("kick").add(at + c.EIGHTH, 31, strength(at, -4, 44, 36), c.TICKS)
                else:
                    part("snare").add(at, 38, strength(at, 0, 46, 40), c.TICKS)
        if "timpani" in wanted:  # timpani on the chord's root: a stroke a chord, or a roll that swells
            note = c.above(root, score.get("timpani_low", 38))
            if section.get("timpani") == "roll":
                step = c.TICKS // 4
                for k, at in enumerate(range(tick, tick + length, step)):
                    part("timpani").add(at + rng.randint(-6, 6), note, strength(at, -14 + rng.uniform(-3, 3), 34, 60),
                                        step * 4)
            else:
                part("timpani").add(tick, note, strength(tick, 6, 46, 60), piece.bar * 2)
        if "pianoarp" in wanted:  # ambient piano: a low bass note, then the chord's tones up and down in
            # eighths across an octave and a half, softly, each left to ring under the pedal
            arp = part("keysarp")
            low = c.above(bass, score.get("arp_bass_low", 38))
            ladder = [n for n in range(*score.get("keys_range", [55, 76])) if n % 12 in tones][:6]
            order = [low] + ladder + ladder[-2:0:-1]
            step = c.EIGHTH * (2 if section.get("arp_quarters") else 1) // (2 if section.get("arp_sixteenths") else 1)
            for k, at in enumerate(range(tick, tick + length, step)):
                n = order[k % len(order)]
                arp.add(at + piece.ms(rng.gauss(0, 14)), n, strength(at, (6 if k == 0 else 0) - 6, 30, 26) + rng.uniform(-3, 3),
                        3 * step)
            arp.pedal += [(tick - 10, 0), (tick + 30, 100)]
        if "felt" in wanted:  # a felt piano, barely touched, the chord's tones rising and falling slowly
            ladder = [n for n in range(*score.get("felt_range", [55, 72])) if n % 12 in tones]
            step = round(section.get("felt_beats", 2) * c.TICKS)
            order = ladder + ladder[-2:0:-1] if len(ladder) > 2 else ladder
            felt = part("felt")
            if section.get("felt_chords"):  # the chord itself, softly, its tones a breath apart
                for at in range(tick, tick + length, step):
                    for j, n in enumerate(ladder[:4]):
                        felt.add(at + piece.ms(25 * j + rng.gauss(0, 10)), n, strength(at, -8 - j, 30, 14), step)
                felt.pedal += [(tick - 10, 0), (tick + 30, 100)]
                ladder = []
            for k, at in enumerate(range(tick, tick + length, step) if ladder else []):
                felt.add(at + piece.ms(rng.gauss(0, 20)), order[(index * 3 + k) % len(order)],
                         strength(at, -8, 30, 14), 2 * step)
            felt.pedal += [(tick - 10, 0), (tick + 30, 100)]
        if "pluckarp" in wanted:  # the zither slowly breaking the chord, a note a beat (pluck_beats)
            ladder = [n for n in range(*score.get("pluck_range", [52, 72])) if n % 12 in tones][:5]
            step = round(section.get("pluck_beats", 1) * c.TICKS)
            for k, at in enumerate(range(tick, tick + length, step)):
                part("pluckarp").add(at + piece.ms(rng.gauss(0, 15)), ladder[k % len(ladder)],
                                     strength(at, 0 if k == 0 else -4, 36, 30), 3 * step)
        if "bowl" in wanted:  # a singing bowl on the chord's root, rubbed, every bowl_every chords
            if index % section.get("bowl_every", 2) == 0:
                part("bowl").add(tick + piece.ms(rng.uniform(0, 300)), c.above(root, score.get("bowl_low", 55)),
                                 strength(tick, 0, 34, 50), piece.bar * 3)
        if "toll" in wanted:
            every = section.get("toll_every", 1)
            if index % every == 0:
                note = c.above(root, score.get("toll_low", 48))
                part("toll").add(tick + piece.ms(rng.uniform(0, 150)), note, strength(tick, 4, 30, 50), piece.bar * 4)
        if "pulse" in wanted:  # a heartbeat on the root, deep: lub-dub, at the section's own rate
            beat = round(section.get("pulse_beats", piece.beats) * c.TICKS)
            note = c.above(root, 28)
            for at in range(tick, tick + length, beat):
                v = strength(at, 0, 34, 50)
                part("pulse").add(at, note, v, c.TICKS)
                part("pulse").add(at + round(0.32 * c.TICKS), note, v - 10, c.TICKS)
        if "drops" in wanted:  # drops in a cave: the chord's tones, high, a few a bar, at random
            high = [n for n in range(62, 85) if n % 12 in tones]
            for _ in range(round(section.get("drops_per_bar", 3) * length / piece.bar)):
                at = tick + rng.randrange(0, length)
                part("drops").add(at, rng.choice(high), strength(at, -4, 28, 40), c.TICKS)
        if "shimmer" in wanted:  # glass, high and soft, on the chord's tones, at random, about twice a bar
            high = [n for n in range(72, 87) if n % 12 in tones]
            for _ in range(max(1, round(2 * length / piece.bar))):
                at = tick + rng.randrange(0, length)
                part("shimmer").add(at, rng.choice(high), strength(at, -6, 26, 30), piece.bar * 2)
    tonic = c.chord(score["sections"][0]["chords"].split("|")[0].split()[0].split(":")[0])[2]
    irng = random.Random(score.get("seed", 11) * 31 + 7)
    for start, end, section in piece.sections:  # improv: a melody made up as it goes (improvise)
        on = section.get("improv")
        if not on:
            continue
        low, high = section.get("improv_range", score.get("improv_range", [57, 76]))
        if section.get("motif"):  # a melody made up once over the first motif_bars, then played again and again
            cycle = section.get("motif_bars", 8) * piece.bar
            once = improvise(piece, c, section, start, min(end, start + cycle + piece.bar), irng, tonic,
                             score.get("mode", "aeolian"), low, high, section.get("improv_density", 1.2))
            once = [(at, n, b) for at, n, b in once if at < start + cycle]
            made = [(at + k * cycle, n, b) for k in range((end - start) // cycle) for at, n, b in once]
        else:
            made = improvise(piece, c, section, start, end, irng, tonic,
                             score.get("mode", "aeolian"), low, high, section.get("improv_density", 1.2))
        for at, n, beats in made:
            length = round(beats * c.TICKS)
            v = strength(at, 0, 32, 30) + irng.uniform(-3, 3)
            at += piece.ms(irng.gauss(0, 30))  # never quite on the grid
            if on == "solo":
                part("solo").add(at, n, v, length + piece.ms(150))
            elif on == "felt":
                part("felt").add(at, n, v - 2, length + c.TICKS)
            elif on == "keys":  # the ambient piano's tune, clearer than its arpeggio
                part("keys").add(at, n, v + 8, length + c.TICKS)
            else:  # glass, pluck, box, bells: struck and left to ring
                part(on).add(at, n, v, max(length, 2 * c.TICKS))
    for t, notes, length in piece.tune:  # the tune: on the bell or the glass, struck and left ringing
        section = piece.section_at(t)
        on = section.get("layers", [])
        if section.get("tune_on"):  # the section names the tune's instrument itself
            on = [section["tune_on"]]
        if "pluck" in on:  # the tune on the plucked zither, a little ornament (a grace note a step under) on long notes
            for n in notes:
                at = t + piece.ms(rng.gauss(0, 12))
                if length >= 2 * c.TICKS and len(notes) == 1:
                    part("pluck").add(at - piece.ms(90), n - 2, strength(t, -6, 34, 40), c.EIGHTH)
                part("pluck").add(at, n, strength(t, 2, 36, 46), length + c.TICKS)
            continue
        if "felt" in on:  # the tune on the felt piano, softly, each note left to ring
            for n in notes:
                part("felt").add(t + piece.ms(rng.gauss(0, 20)), n, strength(t, -2, 32, 12), length + c.TICKS)
            continue
        if "solo" in on:  # the tune sung on the solo string, held, each note into the next
            for n in notes:
                part("solo").add(t + piece.ms(rng.gauss(0, 15)), n, strength(t, 2, 36, 46), length + piece.ms(120))
            continue
        layer = "box" if "box" in on else "glass" if "glass" in on else "bells"
        for n in notes:
            at = t + piece.ms(rng.gauss(0, 25))
            part(layer).add(at, n, strength(t, 6, 34, 50), max(length, piece.bar * 2))
    for start, end, section in piece.sections:  # an answer: a second line, on the bell, low, under the tune
        tick = start
        for token in section.get("answer", "").replace("|", " ").split():
            pitches, _, beats = token.partition(":")
            if pitches != "r":
                for n in pitches.split("+"):
                    if section.get("answer_on") == "solo":  # the answer sung on the solo string, held
                        part("solo").add(tick + piece.ms(rng.gauss(0, 15)), c.note_number(n),
                                         strength(tick, 0, 34, 46), round(float(beats or 1) * c.TICKS) + piece.ms(150))
                    else:
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
    mix = {"hall": {"rt60": room["rt60"], "wet": room.get("wet", 1.0), "even": score.get("even_hall", False)},
           "parts": sheet,
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
