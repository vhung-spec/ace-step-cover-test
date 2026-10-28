"""Bossa nova sketches: a tune (tunes.py) arranged in one of a few styles as
one MIDI file per instrument plus mix.json (room, levels, pan, tone), the
format ../render_samples.py plays:

    python bossa/arrange_bossa.py out/bossa --styles guitar-cafe piano-bossa ...

What the arranger knows of the genre (from the literature on bossa nova, not
yet from measurements of the user's references):

- the guitar's batida: the thumb on the bass strings on beats 1 and 3 (the
  surdo's pulse), the fingers plucking the chord on a syncopated two-bar
  figure (PATTERNS), a chord change anticipated by an eighth when a pluck
  falls just before it; chords short and muted, three tones over the bass;
- the double bass: the root on 1 and the fifth on 3, each led into by an
  eighth before it (the surdo's "dotted quarter and eighth"), or plainly on
  1 and 3;
- brushes: a slow stir on the snare every half bar, the rim (cross-stick)
  playing the bossa clave with the guitar, the hi-hat's foot on 2 and 4, a
  soft kick with the bass; a shaker in eighths;
- the harmony: maj7, maj9, 6/9, m7, m9, m6, m7b5, dim7, 7, 9, 13, 7b9,
  7b13, 7#11, 7sus4, 9sus4; the comping instruments voice each chord without
  its root (the bass has it) and move each voice as little as it can, so the
  inner lines slide by half steps;
- tempos of 100-140 quarter notes a minute, the eighths straight but laid
  back a little off the beat; quiet, close, intimate dynamics.

Every style plays a short intro (two bars: the user disliked a long one),
the tune once or twice, and a held last chord with a slight ritardando.
"""

import argparse
import json
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path

import mido

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tunes import STEPS, TUNES, Tune  # noqa: E402

TICKS = 480  # per quarter note
EIGHTH = TICKS // 2


class Part:
    """The notes of one instrument, (tick, note, velocity, length), and how it
    sits in the mix (gain_db: its level against the melody, if not its role's)."""

    def __init__(self, instrument: str, role: str, pan: float, reverb: float, tone: dict):
        self.instrument, self.role, self.pan, self.reverb, self.tone = instrument, role, pan, reverb, dict(tone)
        self.notes = []
        self.gain_db = None

    def add(self, tick: int, note: int, velocity: int, length: int) -> None:
        self.notes.append((max(0, int(tick)), int(note), max(1, min(127, int(velocity))), max(30, int(length))))


def untangle(notes: list) -> list:
    """The notes in time order, none struck while its key still sounds (a
    note-off ends every voice of its key): the earlier one ends just before."""
    by_key, result = {}, []
    for note in sorted(notes):
        by_key.setdefault(note[1], []).append(note)
    for same in by_key.values():
        kept = [same[0]]
        for tick, key, velocity, length in same[1:]:
            start, _, held_velocity, held = kept[-1]
            if tick - start < 40:
                kept[-1] = (start, key, max(held_velocity, velocity), max(held, tick + length - start))
                continue
            if start + held > tick - 10:
                kept[-1] = (start, key, held_velocity, tick - 10 - start)
            kept.append((tick, key, velocity, length))
        result += kept
    return sorted(result)


def write_part(part: Part, tempos: list, path: Path, beats: int) -> None:
    messages = []
    for tick, note, velocity, length in untangle(part.notes):
        messages.append((tick + length, 0, mido.Message("note_off", note=note, velocity=0)))
        messages.append((tick, 2, mido.Message("note_on", note=note, velocity=velocity)))
    for tick, bpm in tempos:
        messages.append((tick, -1, mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm))))
    midi = mido.MidiFile(ticks_per_beat=TICKS)
    track = mido.MidiTrack()
    midi.tracks.append(track)
    track.append(mido.MetaMessage("time_signature", numerator=beats, denominator=4))
    now = 0
    for tick, _, message in sorted(messages, key=lambda m: (m[0], m[1])):
        track.append(message.copy(time=tick - now))
        now = tick
    track.append(mido.MetaMessage("end_of_track", time=8 * TICKS))  # where rendering stops: time to ring
    midi.save(path)

# A chord's tones above its root (semitones), by the kind its name ends with.
KINDS = {"": (0, 4, 7), "m": (0, 3, 7), "maj7": (0, 4, 7, 11), "maj9": (0, 4, 7, 11, 14), "6": (0, 4, 7, 9),
         "69": (0, 4, 7, 9, 14), "m7": (0, 3, 7, 10), "m9": (0, 3, 7, 10, 14), "m6": (0, 3, 7, 9),
         "m69": (0, 3, 7, 9, 14), "m7b5": (0, 3, 6, 10), "dim7": (0, 3, 6, 9), "7": (0, 4, 7, 10),
         "9": (0, 4, 7, 10, 14), "13": (0, 4, 7, 10, 14, 21), "7b9": (0, 4, 7, 10, 13),
         "7b13": (0, 4, 7, 10, 20), "7#11": (0, 4, 7, 10, 18), "7sus4": (0, 5, 7, 10), "9sus4": (0, 5, 7, 10, 14), "sus4": (0, 5, 7)}
# The tones the comping plays over the bass, by kind: the third and seventh
# (the chord's quality) and its colour; a fourth voice for the keyboards.
COLOURS = {"": (4, 7, 0, 12), "m": (3, 7, 0, 12), "maj7": (4, 11, 7, 14), "maj9": (4, 11, 14, 7),
           "6": (4, 9, 7, 14), "69": (4, 9, 14, 7), "m7": (3, 10, 7, 14), "m9": (3, 10, 14, 7),
           "m6": (3, 9, 7, 14), "m69": (3, 9, 14, 7), "m7b5": (3, 10, 6, 0), "dim7": (3, 9, 6, 0),
           "7": (4, 10, 7, 14), "9": (4, 10, 14, 7), "13": (4, 10, 21, 14), "7b9": (4, 10, 13, 7),
           "7b13": (4, 10, 20, 14), "7#11": (4, 10, 18, 14), "7sus4": (5, 10, 7, 14), "9sus4": (5, 10, 14, 7),
           "sus4": (5, 7, 0, 14)}


def parse(name: str) -> tuple[int, str]:
    """(root pitch class, kind) of a chord name such as Bb7#11 or F#m7b5."""
    root, kind = STEPS[name[0]], name[1:]
    if kind[:1] in ("#", "b") and kind[1:] in KINDS:
        root, kind = (root + (1 if kind[0] == "#" else -1)) % 12, kind[1:]
    if kind not in KINDS:
        raise KeyError(f"chord {name!r}: unknown kind {kind!r}")
    return root, kind


def fifth(name: str) -> int:
    """The interval of a chord's fifth (a diminished one where it has it)."""
    return 6 if parse(name)[1] in ("m7b5", "dim7") else 7


def nearest(pc: int, target: int, low: int, high: int) -> int:
    """The note of a pitch class nearest a target, within low-high."""
    options = [n for n in range(low, high + 1) if n % 12 == pc % 12]
    return min(options, key=lambda n: abs(n - target))


def voicings(name: str, voices: int, low: int, high: int) -> list:
    """Every way to lay a chord's colour tones (COLOURS) between two notes,
    each tone once, spanning at most an octave and a sixth."""
    root, kind = parse(name)
    pcs = [(root + i) % 12 for i in COLOURS[kind][:voices]]
    found = []

    def place(i: int, chosen: list):
        if i == len(pcs):
            ordered = sorted(chosen)
            if ordered[-1] - ordered[0] <= 21 and len(set(ordered)) == len(ordered):
                found.append(ordered)
            return
        for n in range(low, high + 1):
            if n % 12 == pcs[i]:
                place(i + 1, chosen + [n])

    place(0, [])
    return found


def voice_lead(previous: list | None, name: str, voices: int, low: int, high: int, centre: int,
               ceiling: int | None = None) -> list:
    """The voicing of a chord nearest the previous one (each voice moving as
    little as it can: inner lines move by steps), kept under a ceiling (the
    melody) when it can be, and near the middle of its range."""
    options = voicings(name, voices, low, high)
    if ceiling is not None:
        under = [v for v in options if v[-1] < ceiling]
        options = under or options
    if not options:
        raise ValueError(f"no voicing of {name} in {low}-{high}")

    def cost(v: list) -> float:
        drift = abs(sum(v) / len(v) - centre) * 0.6
        # a half step between neighbours is a rub, muddy low down; a whole step low down too
        rub = sum(4 if b - a == 1 else 2 if b - a == 2 and a < 60 else 0 for a, b in zip(v, v[1:]))
        if previous is None or len(previous) != len(v):
            return drift + rub
        return sum(abs(a - b) for a, b in zip(v, previous)) + drift * 0.5 + rub

    return min(options, key=cost)


# The fingers' plucks over two bars of eighths (0-15), and the thumb's.
PATTERNS = {
    # the batida as it is usually transcribed from Joao Gilberto's playing
    "batida": [0, 2, 3, 5, 7, 9, 10, 12, 14],
    # the bossa clave (3-2): sparser, the rim click's figure
    "clave": [0, 3, 6, 10, 13],
    # every off-beat eighth: what the user's bossa references measure (their
    # comping strongest on the "and"s, the 4& most of all)
    "offbeats": [1, 3, 5, 7, 9, 11, 13, 15],
    # a lazy café figure: on 1, the "and" of 2, and anticipating the next bar
    "lazy": [0, 3, 7, 8, 11, 15],
}
CLAVE = [0, 3, 6, 10, 13]


class Sketch:
    """The timeline of a piece: an intro, the tune's passes, the last chord."""

    def __init__(self, tune: Tune, passes: int, bpm: float, seed: int, intro_bars: int = 2):
        self.tune, self.passes, self.bpm = tune, passes, bpm
        self.rng = random.Random(seed)
        self.bar = tune.beats * TICKS
        self.intro = intro_bars * self.bar
        self.length = len(tune.chords) * self.bar
        self.starts = [self.intro + k * self.length for k in range(passes)]
        self.end = self.starts[-1] + self.length  # the last chord sounds from here
        self.parts: dict[str, Part] = {}
        # the intro: the tune's last two bars' chords (its turnaround), or its first chord
        last = tune.chords[-intro_bars:]
        self.intro_chords = last if len({c for bar in last for c in bar}) > 1 else [tune.chords[0]] * intro_bars

    def part(self, name: str, instrument: str, role: str, pan: float, reverb: float, tone: dict) -> Part:
        if name not in self.parts:
            self.parts[name] = Part(instrument, role, pan, reverb, tone)
        return self.parts[name]

    def chord_at(self, tick: int) -> str:
        if tick < self.intro:
            bar = tick // self.bar
            return self.intro_chords[bar][tick % self.bar // TICKS]
        if tick >= self.end:
            return self.tune.chords[-1][-1]
        t = (tick - self.intro) % self.length
        return self.tune.chords[t // self.bar][t % self.bar // TICKS]

    def tempos(self) -> list:
        """Steady, slowing by a fifth over the last bar into the held chord."""
        changes = [(0, self.bpm)]
        for beat in range(self.tune.beats):
            changes.append((self.end - self.bar + beat * TICKS, self.bpm * (1 - 0.2 * (beat + 1) / self.tune.beats)))
        return changes

    def melody(self, passes: list | None = None) -> list:
        """(tick, note, length, pass) of the tune in the given passes."""
        notes = []
        for k in passes if passes is not None else range(self.passes):
            tick = self.starts[k]
            for note, eighths in self.tune.melody:
                length = round(eighths * EIGHTH)
                if note is not None:
                    notes.append((tick, note, length, k))
                tick += length
        return notes

    def lay_back(self, tick: int, amount: int = 14) -> int:
        """Eighths off the beat a little late, the bossa lilt; a little jitter."""
        late = amount if tick % TICKS else 0
        return tick + late + self.rng.randint(-5, 5)


def melody_ceiling(tune_notes: list, tick: int, length: int) -> int | None:
    """The lowest melody note sounding between two ticks (None: rest)."""
    sounding = [n for t, n, l, _ in tune_notes if t < tick + length and tick < t + l]
    return min(sounding) if sounding else None


def guitar_batida(sk: Sketch, part: Part, pattern: str, velocity: int, tune_notes: list, start: int, end: int,
                  thumb: bool = True, ring: float | None = None, spread: int = 6) -> None:
    """The nylon guitar: the thumb's bass on 1 and 3 (root, then the fifth
    when the chord holds), the fingers' three-tone chords on the pattern, a
    pluck just before a chord change playing the coming chord."""
    hits = PATTERNS[pattern]
    previous = None
    for bar_tick in range(start, end, sk.bar):
        cycle = ((bar_tick - sk.intro) // sk.bar) % 2
        if thumb:
            for beat in (0, 2):
                tick = bar_tick + beat * TICKS
                name = sk.chord_at(tick)
                root = parse(name)[0]
                same = sk.chord_at(tick - 2 * TICKS) == name and beat == 2
                note = nearest(root + (fifth(name) if same else 0), 45, 40, 52)
                part.add(sk.lay_back(tick, 0), note, velocity - 8 + sk.rng.randint(-4, 4), int(TICKS * 1.4))
        for hit in hits:
            if hit // 8 != cycle:
                continue
            tick = bar_tick + (hit % 8) * EIGHTH
            if tick >= end:
                continue
            ahead = sk.chord_at(tick + EIGHTH)
            name = ahead if (tick % TICKS) and ahead != sk.chord_at(tick) else sk.chord_at(tick)
            ceiling = melody_ceiling(tune_notes, tick, EIGHTH)
            chord = voice_lead(previous, name, 3, 55, 72, 63, ceiling)
            previous = chord
            at = sk.lay_back(tick)
            accent = 6 if hit in (0, 3, 10) else 0
            length = int(EIGHTH * (ring or (1.7 if hit % 8 in (3, 7) else 0.9)))  # some held, most damped
            accent = 8 if ring and hit % 8 == 7 else accent  # the 4&, anticipating the next bar
            for i, note in enumerate(chord):  # plucked together, the lowest a hair first
                part.add(at + spread * i, note, velocity + accent - 2 * i + sk.rng.randint(-4, 4), length)


def keys_comp(sk: Sketch, part: Part, velocity: int, tune_notes: list, start: int, end: int,
              pattern: str = "clave", held: bool = False) -> None:
    """Piano or Rhodes comping: four-voice rootless chords on the pattern,
    held to the next hit (held) or short."""
    hits = PATTERNS[pattern]
    previous = None
    for bar_tick in range(start, end, sk.bar):
        cycle = ((bar_tick - sk.intro) // sk.bar) % 2
        mine = [bar_tick + (h % 8) * EIGHTH for h in hits if h // 8 == cycle]
        nxt = [bar_tick + sk.bar + (h % 8) * EIGHTH for h in hits if h // 8 != cycle][:1]
        for tick, following in zip(mine, mine[1:] + nxt):
            if tick >= end:
                continue
            ahead = sk.chord_at(tick + EIGHTH)
            name = ahead if (tick % TICKS) and ahead != sk.chord_at(tick) else sk.chord_at(tick)
            ceiling = melody_ceiling(tune_notes, tick, following - tick)
            chord = voice_lead(previous, name, 4, 52, 74, 63, ceiling)
            previous = chord
            length = (following - tick - 20) if held else int(EIGHTH * 1.3)
            at = sk.lay_back(tick)
            for note in chord:
                part.add(at + sk.rng.randint(0, 8), note, velocity + sk.rng.randint(-5, 3), length)


def upright_bass(sk: Sketch, part: Part, velocity: int, start: int, end: int, surdo: bool = True) -> None:
    """The double bass: root on 1, fifth on 3 (or the new chord's root), each
    led into by an eighth before it when surdo."""
    previous = 40
    for bar_tick in range(start, end, sk.bar):
        for beat in (0, 2):
            tick = bar_tick + beat * TICKS
            name = sk.chord_at(tick)
            root = parse(name)[0]
            moved = beat == 0 or sk.chord_at(tick - 2 * TICKS) != name
            note = nearest(root if moved else root + fifth(name), previous, 28, 50)
            previous = note
            if surdo:
                part.add(tick, note, velocity + sk.rng.randint(-3, 3), int(TICKS * 1.45))
                lead = tick + 3 * EIGHTH  # the eighth leading into the next half bar, tied to it in feel
                if lead < end:
                    nxt = sk.chord_at(tick + 2 * TICKS)
                    nroot = parse(nxt)[0]
                    target = nearest(nroot if (beat == 2 or nxt != name) else nroot + fifth(nxt), note, 28, 50)
                    part.add(lead + 10, target, velocity - 16 + sk.rng.randint(-3, 3), int(EIGHTH * 0.8))
            else:
                part.add(tick, note, velocity + sk.rng.randint(-3, 3), int(TICKS * 1.8))


# The brush kit's keys (fetch_bossa.py writes its SFZ from Swirly Drums' samples).
KICK, RIM, SNARE, HAT, HAT_FOOT, STIR = 36, 37, 38, 42, 44, 47


def brushes(sk: Sketch, part: Part, velocity: int, start: int, end: int, kick: bool = True) -> None:
    """A stir every half bar, the rim on the clave, the hat's foot on 2 and 4,
    a soft kick with the bass."""
    for bar_tick in range(start, end, sk.bar):
        cycle = ((bar_tick - sk.intro) // sk.bar) % 2
        for half in (0, 2 * TICKS):
            part.add(bar_tick + half, STIR, velocity - 6 + sk.rng.randint(-4, 4), 2 * TICKS)
        for hit in CLAVE:
            if hit // 8 == cycle:
                part.add(sk.lay_back(bar_tick + (hit % 8) * EIGHTH, 8), RIM, velocity - 4 + sk.rng.randint(-6, 4),
                         EIGHTH)
        for beat in (1, 3):
            part.add(bar_tick + beat * TICKS + sk.rng.randint(-4, 4), HAT_FOOT, velocity - 12, EIGHTH)
        if kick:
            for at, v in ((0, -10), (3 * EIGHTH, -22), (4 * EIGHTH, -6)):
                part.add(bar_tick + at, KICK, velocity + v, EIGHTH)


def half_time(sk: Sketch, part: Part, velocity: int, start: int, end: int) -> None:
    """The first reference's soft kit, half-time: the hi-hat closed on every
    beat (the push and pull of the eighths in its velocity), a brush tap on the
    snare on 3, a soft kick on 1 and leading into 3, the rim on the clave's
    last stroke; no stir (heard as hiss)."""
    for bar_tick in range(start, end, sk.bar):
        cycle = ((bar_tick - sk.intro) // sk.bar) % 2
        for beat in range(4):
            part.add(sk.lay_back(bar_tick + beat * TICKS, 0), HAT, velocity - (4 if beat % 2 else 12), EIGHTH)
            part.add(sk.lay_back(bar_tick + beat * TICKS + EIGHTH, 10), HAT, velocity - 24, EIGHTH)
        part.add(bar_tick + 2 * TICKS + sk.rng.randint(-4, 4), SNARE, velocity - 6, EIGHTH)
        for at, v in ((0, -4), (3 * EIGHTH, -18)):
            part.add(bar_tick + at, KICK, velocity + v, EIGHTH)
        if cycle == 1:
            part.add(sk.lay_back(bar_tick + 5 * EIGHTH, 8), RIM, velocity - 14, EIGHTH)


def bossa_kit(sk: Sketch, part: Part, velocity: int, start: int, end: int, snare: bool = True) -> None:
    """The kit the user's bossa references play (onsets above 2 kHz on every
    eighth, even): the hi-hat closed on every eighth, the rim on the bossa
    clave, a soft kick on 1 and 3 led into by the "and" of 2, a brush tap on
    the snare on 4 now and then; no stir."""
    sk.stir = False
    for bar_tick in range(start, end, sk.bar):
        cycle = ((bar_tick - sk.intro) // sk.bar) % 2
        for e in range(8):
            v = velocity - (10 if e % 2 else 4) + sk.rng.randint(-5, 5)
            part.add(sk.lay_back(bar_tick + e * EIGHTH, 6), HAT, v, EIGHTH)
        for hit in CLAVE:
            if hit // 8 == cycle:
                part.add(sk.lay_back(bar_tick + (hit % 8) * EIGHTH, 8), RIM, velocity - 6 + sk.rng.randint(-5, 3),
                         EIGHTH)
        for at, v in ((0, -6), (3 * EIGHTH, -20), (4 * EIGHTH, -4)):
            part.add(bar_tick + at, KICK, velocity + v, EIGHTH)
        if snare and cycle == 1:
            part.add(bar_tick + 3 * TICKS + sk.rng.randint(-4, 4), SNARE, velocity - 12, EIGHTH)


def string_pad(sk: Sketch, upper: Part, low: Part, velocity: int, start: int, end: int, tune_notes: list) -> None:
    """Held strings: three voice-led tones in the violas, the root in the
    cellos, a chord at a time (a new bow on each change), under the tune."""
    previous = None
    tick = start
    while tick < end:
        name, length = sk.chord_at(tick), TICKS
        while tick + length < end and sk.chord_at(tick + length) == name and length < 2 * sk.bar:
            length += TICKS
        ceiling = melody_ceiling(tune_notes, tick, length)
        chord = voice_lead(previous, name, 3, 53, 70, 60, ceiling)
        previous = chord
        for note in chord:
            upper.add(tick + sk.rng.randint(0, 20), note, velocity + sk.rng.randint(-4, 2), length - 15)
        low.add(tick, nearest(parse(name)[0], 43, 36, 50), velocity - 4, length - 15)
        tick += length


def shaker(sk: Sketch, part: Part, velocity: int, start: int, end: int) -> None:
    """Eighths, the push of the hand on the beat and the pull off it louder."""
    for tick in range(start, end, EIGHTH):
        off = tick % TICKS != 0
        part.add(sk.lay_back(tick, 10), 65 if off else 64, velocity + (6 if off else -6) + sk.rng.randint(-5, 5),
                 EIGHTH)


def play_melody(sk: Sketch, part: Part, notes: list, velocity: int, octave: int = 0, under: bool = False) -> None:
    """The tune: long notes a little louder, a phrase's start a little late;
    with under, a chord tone a third to a sixth beneath its longer notes."""
    for tick, note, length, _ in notes:
        v = velocity + min(10, length // EIGHTH * 2) + sk.rng.randint(-5, 5)
        at = tick + (10 if tick % TICKS else 0) + sk.rng.randint(-6, 6)
        part.add(at, note + octave, v, max(60, length - 30))
        if under and length >= 3 * EIGHTH:
            root, kind = parse(sk.chord_at(tick))
            tones = [(root + i) % 12 for i in KINDS[kind]]
            below = [n for n in range(note + octave - 9, note + octave - 2) if n % 12 in tones]
            if below:
                part.add(at + 8, below[-1], v - 14, max(60, length - 30))


def ending(sk: Sketch, parts: dict, velocity: int) -> None:
    """The last chord: the bass's root, the guitar or keys rolled slowly up, held."""
    name = sk.tune.final or sk.tune.chords[-1][-1]
    root = parse(name)[0]
    if sk.tune.final_note and "melody" in parts:
        parts["melody"].add(sk.end + 20, sk.tune.final_note, velocity + 4, 6 * TICKS)
    if "bass" in parts:
        parts["bass"].add(sk.end, nearest(root, 36, 28, 43), velocity, 6 * TICKS)
    for key in ("guitar", "keys"):
        if key in parts:
            chord = [nearest(root, 45, 40, 52)] + voice_lead(None, name, 4 if key == "keys" else 3, 52, 72, 62)
            for i, note in enumerate(chord):
                parts[key].add(sk.end + i * 40, note, velocity - 4 * i, 6 * TICKS)
    if "drums" in parts:
        parts["drums"].add(sk.end, RIM, velocity - 10, EIGHTH)
        if getattr(sk, "stir", True):
            parts["drums"].add(sk.end, STIR, velocity - 14, 4 * TICKS)


# Each instrument: (library, SFZ), and its tone for render_samples.py.
INSTRUMENTS = {
    "nylon": ("freepats", "SpanishClassicalGuitar-bossa.sfz"),  # written by fetch_bossa.py
    "upright": ("smolken", "d_smolken_rubner_bass_pizz.sfz"),
    "brushes": ("swirly", "bossa_brushes.sfz"),  # written by fetch_bossa.py
    "shaker": ("vcsl", "Idiophones/Struck Idiophones/Shaker, Small.sfz"),
    "yamaha": ("vcsl", "Chordophones/Zithers/Upright Piano, Yamaha.sfz"),
    "vibes": ("vcsl", "Idiophones/Struck Idiophones/Vibraphone - Soft Mallets.sfz"),
    "ep": ("jrhodes", "jRhodes3d-st.sfz"),
    "flute": ("vsco", "FluteSusNV.sfz"),
    "violins": ("vsco", "ViolinEnsSusVib.sfz"),
    "violas": ("vsco", "ViolaEnsSusVib.sfz"),
    "cellos": ("vsco", "CelloEnsSusVib.sfz"),
}
TONES = {
    "nylon": {"highpass": 70, "shelf": [7000, -2], "width": 0.6},
    "upright": {"highpass": 35, "lowpass": 4000, "width": 0.5},
    "brushes": {"highpass": 40, "width": 0.7},
    "shaker": {"highpass": 300, "shelf": [8000, -3], "width": 0.5},
    "yamaha": {"release_db": -60},
    "vibes": {"lowpass": 2500, "lowpass_order": 4, "width": 0.3, "dehiss": True},
    "ep": {"highpass": 60, "lowpass": 7000, "set_cc": {"1": 0.75}, "chorus": 0.5},
    "flute": {"lowpass": 8000, "shelf": [6000, -2], "width": 0.5},
    "violins": {"lowpass": 6500, "lowpass_order": 4, "shelf": [5000, -2], "width": 0.8, "dehiss": True},
    "violas": {"highpass": 80, "lowpass": 6000, "lowpass_order": 4, "shelf": [4000, -2], "width": 0.8, "dehiss": True},
    "cellos": {"highpass": 40, "lowpass": 5000, "lowpass_order": 4, "shelf": [3500, -2], "width": 0.8, "dehiss": True},
}
# The mix the references measured (docs: bokin bossa research): the bass
# carries most of the energy and is mono and dry; the top is dark (spectral
# centroid ~1.1-1.2 kHz against our first sketches' 2.0-2.4); brush noise and
# shaker, which a tagger heard as "steam" and "hiss", far down.
NEAR_REFS = {
    "bass": dict(gain_db=-1.0, reverb=0.03, tone={"highpass": 35, "lowpass": 2500, "width": 0.0}),
    "drums": dict(gain_db=-21.0),
    "shaker": dict(gain_db=-29.0),
    "guitar": dict(tone={"highpass": 90, "lowpass": 6000, "shelf": [3000, -4], "width": 0.4}),
}


def near_refs(sk: Sketch) -> None:
    """Applies the references' balance (NEAR_REFS) to a sketch's parts."""
    for name, change in NEAR_REFS.items():
        if name in sk.parts:
            part = sk.parts[name]
            part.gain_db = change.get("gain_db", part.gain_db)
            part.reverb = change.get("reverb", part.reverb)
            part.tone.update(change.get("tone", {}))


@dataclass
class Style:
    title: str
    tune: str
    bpm: float
    passes: int
    rt60: float  # the room's reverb time (s)
    wet: float  # sends into it, times this: less is closer
    build: callable = None
    about: str = ""
    extra: dict = field(default_factory=dict)


def build_guitar_cafe(sk: Sketch) -> None:
    """Nylon guitar's batida, double bass, brushes, a shaker; the flute sings."""
    tune = sk.melody()
    g = sk.part("guitar", "nylon", "comp", -0.3, 0.35, TONES["nylon"])
    b = sk.part("bass", "upright", "bass", 0.0, 0.2, TONES["upright"])
    d = sk.part("drums", "brushes", "drums", 0.25, 0.3, TONES["brushes"])
    s = sk.part("shaker", "shaker", "shaker", 0.5, 0.3, TONES["shaker"])
    f = sk.part("melody", "flute", "melody", 0.15, 0.45, TONES["flute"])
    guitar_batida(sk, g, "batida", 72, tune, 0, sk.end)
    upright_bass(sk, b, 82, sk.intro, sk.end)
    brushes(sk, d, 66, sk.intro, sk.end)
    shaker(sk, s, 52, sk.starts[0] + 8 * sk.bar, sk.end)
    play_melody(sk, f, tune, 74)
    ending(sk, sk.parts, 70)


def build_piano_bossa(sk: Sketch) -> None:
    """The Yamaha upright sings the tune (a third or sixth under long notes in
    the second pass) and comps on the clave; a soft guitar, bass, brushes."""
    tune = sk.melody()
    k = sk.part("keys", "yamaha", "comp", -0.2, 0.3, TONES["yamaha"])
    m = sk.part("melody", "yamaha", "melody", 0.1, 0.35, TONES["yamaha"])
    g = sk.part("guitar", "nylon", "guitar", -0.45, 0.35, TONES["nylon"])
    b = sk.part("bass", "upright", "bass", 0.0, 0.2, TONES["upright"])
    d = sk.part("drums", "brushes", "drums", 0.3, 0.3, TONES["brushes"])
    keys_comp(sk, k, 52, tune, sk.intro, sk.end, "clave")
    guitar_batida(sk, g, "lazy", 60, tune, 0, sk.end, thumb=False)
    upright_bass(sk, b, 80, 0, sk.end, surdo=False)
    brushes(sk, d, 58, sk.intro, sk.end, kick=False)
    play_melody(sk, m, sk.melody([0]), 70, 12)
    play_melody(sk, m, sk.melody([1]), 72, 12, under=True)
    ending(sk, sk.parts, 64)


def build_rhodes_lounge(sk: Sketch) -> None:
    """The Rhodes holds the chords, the vibraphone sings, bass and brushes;
    a little more room around it."""
    tune = sk.melody()
    k = sk.part("keys", "ep", "comp", -0.15, 0.4, TONES["ep"])
    v = sk.part("melody", "vibes", "melody", 0.2, 0.5, TONES["vibes"])
    b = sk.part("bass", "upright", "bass", 0.0, 0.2, TONES["upright"])
    d = sk.part("drums", "brushes", "drums", 0.3, 0.35, TONES["brushes"])
    s = sk.part("shaker", "shaker", "shaker", -0.5, 0.3, TONES["shaker"])
    keys_comp(sk, k, 58, tune, 0, sk.end, "lazy", held=True)
    upright_bass(sk, b, 82, sk.intro, sk.end)
    brushes(sk, d, 62, sk.intro, sk.end)
    shaker(sk, s, 46, sk.starts[0], sk.end)
    play_melody(sk, v, tune, 78)
    ending(sk, sk.parts, 66)


def build_xmas(sk: Sketch) -> None:
    """Jingle Bells as bossa: the guitar's batida, bass, brushes, shaker; the
    piano sings it the first time, the flute the second."""
    tune = sk.melody()
    g = sk.part("guitar", "nylon", "comp", -0.3, 0.35, TONES["nylon"])
    b = sk.part("bass", "upright", "bass", 0.0, 0.2, TONES["upright"])
    d = sk.part("drums", "brushes", "drums", 0.25, 0.3, TONES["brushes"])
    s = sk.part("shaker", "shaker", "shaker", 0.5, 0.3, TONES["shaker"])
    p = sk.part("melody", "yamaha", "melody", 0.1, 0.35, TONES["yamaha"])
    f = sk.part("flute", "flute", "melody2", 0.2, 0.45, TONES["flute"])
    guitar_batida(sk, g, "batida", 70, tune, 0, sk.end)
    upright_bass(sk, b, 82, sk.intro, sk.end)
    brushes(sk, d, 64, sk.intro, sk.end)
    shaker(sk, s, 50, sk.starts[1], sk.end)
    play_melody(sk, p, sk.melody([0]), 72, 12)
    play_melody(sk, f, sk.melody([1]), 74)
    ending(sk, sk.parts, 68)


def build_sang_em(sk: Sketch) -> None:
    """After the first reference: the Rhodes holding the chords, the Yamaha
    upright singing, a soft half-time kit, the bass deep and dry."""
    tune = sk.melody()
    k = sk.part("keys", "ep", "comp", -0.1, 0.45, TONES["ep"] | {"chorus": 0.8, "lowpass": 4500})
    m = sk.part("melody", "yamaha", "melody", 0.05, 0.4, TONES["yamaha"] | {"shelf": [4000, -3]})
    b = sk.part("bass", "upright", "bass", 0.0, 0.2, TONES["upright"])
    d = sk.part("drums", "brushes", "drums", 0.1, 0.3, TONES["brushes"] | {"lowpass": 7000, "width": 0.4})
    keys_comp(sk, k, 52, tune, 0, sk.end, "lazy", held=True)
    upright_bass(sk, b, 84, sk.intro, sk.end)
    half_time(sk, d, 60, sk.intro, sk.end)
    play_melody(sk, m, sk.melody([0]), 66)
    play_melody(sk, m, sk.melody([1]), 70, 12, under=True)
    ending(sk, sk.parts, 62)
    near_refs(sk)
    sk.parts["drums"].gain_db = -18.0


def build_day_am(sk: Sketch) -> None:
    """After the second reference: the violins sing over held violas and
    cellos, the guitar's batida soft underneath, the bass; no drums."""
    tune = sk.melody()
    v = sk.part("melody", "violins", "melody", 0.15, 0.5, TONES["violins"])
    va = sk.part("violas", "violas", "pad", -0.2, 0.5, TONES["violas"])
    vc = sk.part("cellos", "cellos", "pad", 0.2, 0.45, TONES["cellos"])
    g = sk.part("guitar", "nylon", "guitar", -0.3, 0.3, TONES["nylon"])
    b = sk.part("bass", "upright", "bass", 0.0, 0.2, TONES["upright"])
    string_pad(sk, va, vc, 50, sk.intro, sk.end, tune)
    guitar_batida(sk, g, "batida", 64, tune, 0, sk.end)
    upright_bass(sk, b, 80, sk.intro, sk.end)
    play_melody(sk, v, sk.melody([0]), 64)
    play_melody(sk, v, sk.melody([1]), 72, 12)
    ending(sk, sk.parts, 62)
    near_refs(sk)
    va.gain_db = vc.gain_db = -9.0
    g.gain_db = -6.0


def build_guitar_cafe_near(sk: Sketch) -> None:
    """Guitar café mixed as the references: deeper bass, darker, quieter brushes."""
    build_guitar_cafe(sk)
    near_refs(sk)


def build_pho(sk: Sketch) -> None:
    """After the user's bossa references: the nylon guitar's batida up front,
    the Yamaha upright singing (a third or sixth under it the second time),
    the Rhodes softly on the clave, the bass on 1 and 3 with its
    anticipations, mono and dry; a light kit with the hi-hat in eighths."""
    tune = sk.melody()
    g = sk.part("guitar", "nylon", "guitar", -0.15, 0.3,
                TONES["nylon"] | {"highpass": 80, "lowpass": 6500, "shelf": [3000, -3], "width": 0.3})
    m = sk.part("melody", "yamaha", "melody", 0.1, 0.35, TONES["yamaha"] | {"shelf": [4000, -2]})
    k = sk.part("keys", "ep", "comp", 0.3, 0.4, TONES["ep"] | {"chorus": 0.5, "lowpass": 5000})
    b = sk.part("bass", "upright", "bass", 0.0, 0.03, {"highpass": 35, "lowpass": 2500, "width": 0.0})
    d = sk.part("drums", "brushes", "drums", 0.1, 0.25, TONES["brushes"] | {"lowpass": 9000, "width": 0.5})
    guitar_batida(sk, g, "batida", 74, tune, 0, sk.end)
    keys_comp(sk, k, 46, tune, sk.intro, sk.end, "clave", held=True)
    upright_bass(sk, b, 84, sk.intro, sk.end)
    bossa_kit(sk, d, 62, sk.intro, sk.end)
    play_melody(sk, m, sk.melody([0]), 70)
    play_melody(sk, m, sk.melody(list(range(1, sk.passes))), 72, under=True)
    ending(sk, sk.parts, 66)
    g.gain_db, k.gain_db, b.gain_db, d.gain_db = -3.0, -12.0, -2.0, -13.0


def build_pho2(sk: Sketch) -> None:
    """Round 4: as build_pho, but the guitar plucks every off-beat (the 4&
    strongest) and rings longer, as loud as the piano, which plays softer;
    the Rhodes off the beat too; the kit a little louder."""
    tune = sk.melody()
    g = sk.part("guitar", "nylon", "guitar", -0.15, 0.3,
                TONES["nylon"] | {"highpass": 80, "lowpass": 7000, "shelf": [3000, -2], "width": 0.35})
    m = sk.part("melody", "yamaha", "melody", 0.1, 0.35, TONES["yamaha"] | {"shelf": [4000, -3]})
    k = sk.part("keys", "ep", "comp", 0.3, 0.4, TONES["ep"] | {"chorus": 0.5, "lowpass": 5000})
    b = sk.part("bass", "upright", "bass", 0.0, 0.03, {"highpass": 35, "lowpass": 2500, "width": 0.0})
    d = sk.part("drums", "brushes", "drums", 0.1, 0.25, TONES["brushes"] | {"lowpass": 9000, "width": 0.5})
    guitar_batida(sk, g, "offbeats", 72, tune, 0, sk.end, ring=1.6, spread=14)
    keys_comp(sk, k, 44, tune, sk.intro, sk.end, "offbeats")
    upright_bass(sk, b, 84, sk.intro, sk.end)
    bossa_kit(sk, d, 64, sk.intro, sk.end)
    play_melody(sk, m, sk.melody([0]), 64)
    play_melody(sk, m, sk.melody(list(range(1, sk.passes))), 66, under=True)
    ending(sk, sk.parts, 66)
    g.gain_db, k.gain_db, b.gain_db, d.gain_db = 1.0, -14.0, -2.0, -10.0


def build_pho3(sk: Sketch, rhodes: bool = False) -> None:
    """Round 5, clearer: the user heard round 4 as muddy and cluttered, and
    against the references it had 2-3 dB more at 120-500 Hz, 6 dB less bass
    at 60-120 Hz and 6-13 dB less air above 8 kHz. So the guitar's thumb is
    gone (the bass has the low notes), every part but the bass is cut below
    its own range, nothing is darkened, no notes under the melody, the bass
    louder, the kit a little louder; the Rhodes, if at all, only a held chord
    a bar high up; the room hears nothing under 300 Hz (mix.json)."""
    tune = sk.melody()
    g = sk.part("guitar", "nylon", "guitar", -0.2, 0.3, {"highpass": 160, "width": 0.4})
    m = sk.part("melody", "yamaha", "melody", 0.15, 0.3, TONES["yamaha"] | {"highpass": 180})
    b = sk.part("bass", "upright", "bass", 0.0, 0.0, {"highpass": 38, "lowpass": 3000, "width": 0.0})
    d = sk.part("drums", "brushes", "drums", 0.1, 0.2, TONES["brushes"] | {"highpass": 60, "width": 0.6})
    guitar_batida(sk, g, "offbeats", 72, tune, 0, sk.end, thumb=False, ring=1.4, spread=14)
    upright_bass(sk, b, 86, sk.intro, sk.end)
    bossa_kit(sk, d, 66, sk.intro, sk.end)
    play_melody(sk, m, tune, 66)
    if rhodes:
        k = sk.part("keys", "ep", "comp", 0.35, 0.35, TONES["ep"] | {"highpass": 260, "chorus": 0.7})
        previous = None
        for bar_tick in range(sk.intro, sk.end, sk.bar):
            name = sk.chord_at(bar_tick)
            previous = voice_lead(previous, name, 3, 64, 79, 71)
            for note in previous:
                k.add(bar_tick + 20 + sk.rng.randint(0, 10), note, 40 + sk.rng.randint(-3, 3), sk.bar - 40)
        k.gain_db = -15.0
    ending(sk, sk.parts, 66)
    g.gain_db, b.gain_db, d.gain_db = 0.0, 1.0, -8.0


def build_dem(sk: Sketch) -> None:
    """After the third reference: guitar and piano, the Rhodes behind, the
    bass; the kit barely there; nearly mono, a long room."""
    build_pho(sk)
    for part in sk.parts.values():
        part.tone["width"] = min(part.tone.get("width", 1.0), 0.25)
        part.pan *= 0.4
    sk.parts["drums"].gain_db = -22.0


STYLES = {
    "guitar-cafe": Style("Guitar café", "cafe", 128, 1, 0.8, 0.6, build_guitar_cafe,
                         "Guitar nylon đệm batida, contrabass, trống chổi, shaker; sáo hát giai điệu. Phòng nhỏ, rất gần."),
    "piano-bossa": Style("Piano bossa", "chuva", 104, 2, 0.9, 0.6, build_piano_bossa,
                         "Piano Yamaha hát và đệm, guitar nhẹ, contrabass, trống chổi. Chậm, buồn nhẹ, rất gần."),
    "rhodes-lounge": Style("Rhodes lounge", "cafe", 112, 1, 1.5, 0.9, build_rhodes_lounge,
                           "Rhodes giữ hợp âm, vibraphone hát, contrabass, trống chổi. Phòng rộng hơn một chút."),
    "bossa-noel": Style("Bossa Noel", "jingle", 132, 2, 0.9, 0.6, build_xmas,
                        "Jingle Bells kiểu bossa: guitar batida, contrabass, trống chổi; piano rồi sáo hát."),
    "sang-em": Style("Sáng Êm", "sang-em", 140, 2, 1.6, 0.8, build_sang_em,
                     "Theo bài mẫu 1: Rhodes giữ hợp âm, piano hát, trống nhẹ nửa nhịp, bass sâu. Phòng 1,6 giây."),
    "day-am": Style("Dây Ấm", "day-am", 136, 2, 1.6, 0.8, build_day_am,
                    "Theo bài mẫu 2: violin hát trên nền viola, cello; guitar nylon đệm nhẹ, contrabass; không trống."),
    "chieu-pho": Style("Chiều Phố", "chieu-pho", 117, 2, 2.6, 0.7, build_pho,
                       "Theo 3 bài mẫu bossa: guitar nylon đệm rõ, piano hát, Rhodes nhẹ, bass, trống nhẹ hi-hat. Phòng 2,6 giây."),
    "chieu-pho-gan": Style("Chiều Phố (gần)", "chieu-pho", 117, 2, 1.0, 0.5, build_pho,
                           "Như Chiều Phố, phòng nhỏ, nghe gần tai."),
    "cafe-dem": Style("Café Đêm", "cafe", 129, 1, 3.5, 0.6, build_dem,
                      "Theo bài mẫu thứ 3: guitar, piano, Rhodes, bass, trống rất nhẹ; gần như mono, phòng dài."),
    "cafe-pho": Style("Café Phố", "cafe", 117, 1, 2.6, 0.7, build_pho,
                      "Giai điệu Café da Tarde chơi theo kiểu Chiều Phố."),
    "chieu-pho-2": Style("Chiều Phố 2", "chieu-pho", 117, 2, 2.6, 0.7, build_pho2,
                         "Vòng 4: guitar gảy nghịch phách, to ngang piano, ngân dài hơn; trống rõ hơn chút. Phòng 2,6 giây."),
    "chieu-pho-2-gan": Style("Chiều Phố 2 (gần)", "chieu-pho", 117, 2, 1.0, 0.5, build_pho2,
                             "Như Chiều Phố 2, phòng nhỏ, nghe gần tai."),
    "chieu-pho-3": Style("Chiều Phố 3", "chieu-pho", 117, 2, 2.0, 0.45, build_pho3,
                         "Vòng 5, trong hơn: guitar, piano, bass, trống; bớt chồng tiếng ở vùng trầm-giữa, bass rõ, sáng thoáng hơn.",
                         extra={"hall_highpass": 300}),
    "chieu-pho-3-gan": Style("Chiều Phố 3 (gần)", "chieu-pho", 117, 2, 1.0, 0.4, build_pho3,
                             "Như Chiều Phố 3, phòng nhỏ.", extra={"hall_highpass": 300}),
    "chieu-pho-3-rhodes": Style("Chiều Phố 3 + Rhodes", "chieu-pho", 117, 2, 2.0, 0.45,
                                lambda sk: build_pho3(sk, rhodes=True),
                                "Như Chiều Phố 3, thêm Rhodes ngân nhẹ ở trên cao.", extra={"hall_highpass": 300}),
    "guitar-cafe-near": Style("Guitar café (mix theo mẫu)", "cafe", 128, 1, 1.2, 0.6, build_guitar_cafe_near,
                              "Như Guitar café, nhưng trộn theo bài mẫu: bass sâu hơn, tiếng tối ấm hơn, trống chổi nhỏ."),
}
# How loud each kind of part sits against the melody (dB of its loudness while it plays).
ROLES = {"melody": 0.0, "melody2": 0.0, "pad": -8.0, "comp": -6.0, "guitar": -9.0, "bass": -7.0, "drums": -15.0,
         "shaker": -21.0}


def make(style_name: str, out: Path, seed: int = 7) -> Path:
    style = STYLES[style_name]
    tune = TUNES[style.tune]
    sk = Sketch(tune, style.passes, style.bpm, seed)
    style.build(sk)
    folder = out / f"{style_name}"
    folder.mkdir(parents=True, exist_ok=True)
    sheet = []
    for name, part in sk.parts.items():
        write_part(part, sk.tempos(), folder / f"{name}.mid", tune.beats)
        library, sfz = INSTRUMENTS[part.instrument]
        sheet.append({"part": name, "library": library, "sfz": sfz, "role": part.role, "gain_db": ROLES[part.role] if part.gain_db is None else part.gain_db,
                      "pan": part.pan, "reverb": part.reverb, "tone": part.tone, "notes": len(part.notes)})
    hall = {"rt60": style.rt60, "wet": style.wet}
    if style.extra.get("hall_highpass"):
        hall["highpass"] = style.extra["hall_highpass"]
    mix = {"hall": hall, "parts": sheet,
           "about": {"title": style.title, "tune": tune.title, "tune_about": tune.about, "bpm": style.bpm,
                     "text": style.about}}
    (folder / "mix.json").write_text(json.dumps(mix, indent=2, ensure_ascii=False))
    seconds = sk.end / TICKS * 60 / style.bpm + 4
    print(f"{folder.name}: {tune.title}, {style.bpm} bpm, {style.passes} pass(es), about {seconds:.0f} s, "
          f"parts {', '.join(f'{p[0]}({len(p[1].notes)})' for p in sk.parts.items())}")
    return folder


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--styles", nargs="+", default=list(STYLES), choices=list(STYLES))
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    for name in args.styles:
        make(name, args.out, args.seed)


if __name__ == "__main__":
    main()
