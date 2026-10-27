"""Arranges the test's carols for real instrument samples, without any AI
model: one MIDI file per instrument, in four styles, plus mix.json (the hall,
and each part's instrument, role, stereo position and tone) for
render_samples.py:

    python arrange.py out/sampled [--songs wish silent-night] [--styles piano chill bells orchestra]

The carols are the public-domain melodies and chords of make_source.py. Every
style plays an intro (the last phrase, an octave up), the verses (the last one
fuller) and a held last chord, slowing down over the last two bars. The parts
are written from the same chords, beat by beat, so they always agree:
- piano (VCSL's Steinway B; "salamander": the Salamander Grand Piano, CC-BY
  3.0, by Alexander Holm): the melody over a flowing left hand, with sustain
  pedal; in the last verse a chord tone a third to a sixth under the longer
  notes sings with the melody;
- chill: the Steinway slower and softer, for quiet listening: open broken
  chords that leave room, the melody a little behind the beat, longer breaths
  at the phrase ends, a darker tone and a larger hall; a short tune is played
  three times, the middle time an octave up;
- bells: hand chimes, then vibraphone on the melody, soft and at the tune's
  own pitch, a glockenspiel only over the last phrase, on a harp and, in the
  last verse, a soft string pad;
- orchestra: flute, then violins on the melody, a flute descant over the last
  verse, on a harp and a string pad, basses plucked then bowed, horns from the
  middle of the last verse, a soft timpani roll under the last chord.
Sustained parts hold the tones two chords share, move their other tones to
the nearest tone of the next chord, and swell with each phrase (expression,
CC11). Instruments come from two CC0 sample libraries: VS Chamber Orchestra 2
Community Edition ("vsco", SFZ branch) and the Versilian Community Sample
Library ("vcsl", sfz branch).
"""

import argparse
import itertools
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import mido

import make_source

TICKS = 480  # per quarter note
EIGHTH = TICKS // 2
BAR = 3 * TICKS  # both carols are in 3/4
HOLD_SECONDS = 4.5  # the longest a held note sounds: sustained samples are not looped, the shortest last about 5 s

# Root pitch class, and the chord's intervals above the root.
CHORDS = {"C": (0, (0, 4, 7)), "F": (5, (0, 4, 7)), "G": (7, (0, 4, 7)), "G7": (7, (0, 4, 7, 10)),
          "D7": (2, (0, 4, 7, 10)), "E7": (4, (0, 4, 7, 10)), "Am": (9, (0, 3, 7))}

# Sample libraries: (library, SFZ file in it). The softer sample layers end at
# velocity 62 (strings, flute), 65 (piano), 83 (vibraphone, glockenspiel), 100
# (harp) and 41 (horns, the two softest); hand chimes and sleigh bells have one.
INSTRUMENTS = {
    "piano": ("vcsl", "Chordophones/Zithers/Grand Piano, Steinway B.sfz"),
    "salamander": ("salamander", "Salamander Grand Piano V3.sfz"),
    "chimes": ("vcsl", "Idiophones/Struck Idiophones/Hand Chimes.sfz"),
    "vibes": ("vcsl", "Idiophones/Struck Idiophones/Vibraphone - Soft Mallets.sfz"),
    "glock": ("vcsl", "Idiophones/Struck Idiophones/Glockenspiel.sfz"),
    "harp": ("vcsl", "Chordophones/Composite Chordophones/Concert Harp.sfz"),
    "sleigh": ("vcsl", "Idiophones/Struck Idiophones/Sleigh Bells.sfz"),
    "flute": ("vsco", "FluteSusVib.sfz"),
    "violins": ("vsco", "ViolinEnsSusVib.sfz"),
    "violas": ("vsco", "ViolaEnsSusVib.sfz"),
    "cellos": ("vsco", "CelloEnsSusVib.sfz"),
    "basses": ("vsco", "ContrabassSusVB-Quiet.sfz"),
    "basses-pizz": ("vsco", "ContrabassPizz.sfz"),
    "horns": ("vsco", "FHornSus.sfz"),
    "timpani": ("vsco", "TimpaniRolls.sfz"),
}
# Each instrument's tone, for render_samples.py: a high-pass and a low-pass
# (Hz), a high shelf (Hz, dB): the bells and the sustained parts lose some
# edge and the hiss of their recordings; and the piano's release samples (the
# dampers' sound as keys are let go, all at once when the pedal lifts)
# turned down (dB).
TONES = {
    "piano": {"release_db": -15},
    "chimes": {"shelf": [5000, -4]},
    "vibes": {"shelf": [6000, -3]},
    "glock": {"lowpass": 9000, "shelf": [5000, -5]},
    "harp": {"shelf": [8000, -2]},
    "sleigh": {"shelf": [6000, -6]},
    "flute": {"lowpass": 12000, "shelf": [8000, -2]},
    "violins": {"lowpass": 12000, "shelf": [7000, -2]},
    "violas": {"highpass": 80, "lowpass": 10000, "shelf": [6000, -3]},
    "cellos": {"highpass": 40, "lowpass": 9000, "shelf": [5000, -3]},
    "basses": {"highpass": 30, "lowpass": 6000},
    "basses-pizz": {"highpass": 30, "lowpass": 6000},
    "horns": {"highpass": 60, "lowpass": 8000},
    "timpani": {"highpass": 35},
}
# How loud each kind of part sits against the melody (dB of its loudness when playing).
ROLES = {"melody": 0.0, "piano": 0.0, "descant": -9.0, "harp": -4.0, "pad": -10.0, "bass": -8.0,
         "low": -12.0, "sparkle": -16.0, "drum": -17.0}


@dataclass
class Song:
    name: str
    bpm: float
    melody: list  # (MIDI note, length in eighths), the pickup first
    pickup: int  # eighths of melody before the first bar
    chords: list  # per bar, one chord name per beat
    intro_bars: int  # the last bars of the tune, played as the intro


def per_beat(names: str) -> list:
    return [[name] * 3 if "|" not in name else name.split("|") for name in names.split()]


SONGS = {
    "wish": Song("wish", 120, make_source.MELODY, 2,
                 per_beat("C F D7 G E7 Am F|G|G C"), 2),
    "silent-night": Song("silent-night", 84, make_source.SILENT_NIGHT, 0,
                         per_beat("C C C C G7 G7 C C F F C C F F C C G7 G7 C C C G7 C C"), 4),
}


def busy(notes: list, key: int, tick: int, length: int) -> bool:
    """Whether a key sounds, among some notes, at any time between two ticks."""
    return any(n == key and t < tick + length and tick < t + l for t, n, _, l in notes)


class Part:
    """The notes of one instrument, (tick, note, velocity, length), its pedal and
    expression (CC11) changes, and how it sits in the mix."""

    def __init__(self, instrument: str, role: str, pan: float, reverb: float, fits: Callable):
        self.instrument, self.role, self.pan, self.reverb = instrument, role, pan, reverb
        self.tone = dict(TONES.get(instrument, {}))
        self.fits = fits  # whether a note held from one tick to another stays within its sample
        self.notes, self.pedal, self.expression, self.voicing = [], [], [], []
        self.latest = {}  # key: index of its latest note

    def add(self, tick: int, note: int, velocity: int, length: int, tie: bool = False) -> None:
        """Adds a note. With tie, a key still sounding is held on rather than
        struck again (a tone two chords share), while its sample lasts."""
        tick, note, length = max(0, int(tick)), int(note), max(30, int(length))
        index = self.latest.get(note)
        if tie and index is not None:
            start, _, held_velocity, held = self.notes[index]
            if start + held >= tick - 30 and self.fits(start, tick + length):
                self.notes[index] = (start, note, held_velocity, max(held, tick + length - start))
                return
        self.latest[note] = len(self.notes)
        self.notes.append((tick, note, max(1, min(127, int(velocity))), length))


class Arrangement:
    """The timeline every part follows: intro, verses, the last chord, and its tempo."""

    def __init__(self, song: Song, verses: int = 2, tempo: float = 1.0, breath: float = 0.92, seed: int = 7):
        self.song, self.rng = song, random.Random(seed)
        self.bpm = song.bpm * tempo
        self.intro = song.intro_bars * BAR
        self.verse = len(song.chords) * BAR
        self.phrase = 4 * BAR
        self.verses = [self.intro + k * self.verse for k in range(verses)]  # each verse's first downbeat
        self.last = verses - 1  # the last verse's number
        self.end = self.verses[-1] + self.verse  # the last note's bar ends here
        self.tempos = self.tempo_map(breath)
        self.parts: dict[str, Part] = {}

    def part(self, name: str, instrument: str, role: str, pan: float, reverb: float = 0.3) -> Part:
        if name not in self.parts:
            self.parts[name] = Part(instrument, role, pan, reverb,
                                    lambda start, end: self.seconds(start, end) <= HOLD_SECONDS)
        return self.parts[name]

    def tempo_map(self, breath: float) -> list:
        """(tick, bpm): a breath on the last beat of every four-bar phrase, as a
        player would take, and slowing over the last two bars to the held chord."""
        bpm, changes = self.bpm, [(0, self.bpm)]
        slow_from = self.end - 2 * BAR
        for downbeat in self.verses:
            for bar in range(3, len(self.song.chords), 4):
                last_beat = downbeat + bar * BAR + 2 * TICKS
                if last_beat + TICKS <= slow_from:
                    changes += [(last_beat, bpm * breath), (last_beat + TICKS, bpm)]
        for beat in range(7):
            changes.append((slow_from + beat * TICKS, bpm * (1 - 0.05 * (beat + 1))))
        return sorted(changes)

    def seconds(self, start: int, end: int) -> float:
        """How long the music between two ticks lasts."""
        total, changes = 0.0, self.tempos + [(math.inf, 0)]
        for (tick, bpm), (following, _) in zip(changes, changes[1:]):
            overlap = min(end, following) - max(start, tick)
            if overlap > 0:
                total += overlap / TICKS * 60 / bpm
        return total

    def jitter(self, ticks: int = 8) -> int:  # a player is never exactly on the grid
        return self.rng.randint(-ticks, ticks)

    def chord_at(self, tick: int) -> str:
        """The chord sounding at a tick: the intro uses the tune's last bars, the
        ring-out after the last verse the first chord (the tonic)."""
        bars = self.song.chords
        if tick < self.intro:
            bar = len(bars) - self.song.intro_bars + tick // BAR
        elif tick >= self.end:
            return bars[0][0]
        else:
            bar = (tick - self.intro) % self.verse // BAR
        return bars[bar][tick % BAR // TICKS]

    def chord_spans(self, start: int, end: int):
        """(tick, length, chord) for each run of one chord between two ticks."""
        spans, tick = [], start
        while tick < end:
            chord, length = self.chord_at(tick), TICKS
            while tick + length < end and self.chord_at(tick + length) == chord and (tick + length) % BAR:
                length += TICKS
            spans.append((tick, length, chord))
            tick += length
        return spans

    def melody(self):
        """(tick, note, length, verse, position in the verse 0-1) of the tune: the intro
        (the last bars an octave up, verse -1), then every verse."""
        song, notes = self.song, []
        tune, tick = [], -song.pickup * EIGHTH
        for note, eighths in song.melody:
            tune.append((tick, note, eighths * EIGHTH))
            tick += eighths * EIGHTH
        first_intro_tick = (len(song.chords) - song.intro_bars) * BAR
        intro_end = self.intro - song.pickup * EIGHTH  # where the first verse's pickup starts
        for start, note, length in tune:  # the intro: the last phrase, an octave up
            if start >= first_intro_tick:
                at = start - first_intro_tick
                notes.append((at, note + 12, min(length, intro_end - at), -1, 1.0))
        for verse, downbeat in enumerate(self.verses):
            for index, (start, note, length) in enumerate(tune):
                if verse < self.last and start + length >= self.verse and song.pickup:
                    length -= song.pickup * EIGHTH  # room for the next verse's pickup
                if verse == self.last and index == len(tune) - 1:
                    length += BAR  # the last note rings on
                notes.append((downbeat + start, note, length, verse, index / max(1, len(tune) - 1)))
        return notes


def chord_notes(chord: str, low: int, high: int) -> list:
    root, intervals = CHORDS[chord]
    classes = {(root + i) % 12 for i in intervals}
    return [n for n in range(low, high + 1) if n % 12 in classes]


def bass_note(chord: str, low: int = 36) -> int:
    root = CHORDS[chord][0]
    return low + (root - low) % 12


def low_bass(chord: str) -> int:
    """The root an octave under the cellos' (for the double basses), not below E1."""
    note = bass_note(chord) - 12
    return note if note >= 28 else note + 12


def third(chord: str) -> int:
    return CHORDS[chord][1][1]


def open_chord(chord: str) -> tuple:
    """A roomy voicing: the root, the fifth above it, the third an octave higher (a tenth)."""
    root = bass_note(chord)
    return root, root + 7, root + 12 + third(chord)


def harmony_below(chord: str, note: int) -> int | None:
    """The chord tone a third to a sixth under a melody note, to sing with it."""
    below = [n for n in chord_notes(chord, note - 9, note - 3)]
    return below[-1] if below and below[-1] >= 59 else None


def shape(position: float) -> float:
    """Phrase dynamics: 0 at the start and end of a verse, 1 in the middle."""
    return 1 - abs(position - 0.5) * 2


def flowing_bass(arr: Arrangement, part: Part, start: int, end: int, velocity: int, octave: int = 0,
                 avoid: list = ()) -> None:
    """A left hand / harp in 3/4: the bass on the beat, then the chord broken
    upwards and back in eighths, beat by beat with that beat's chord. Keys the
    melody is holding (avoid) are left to it."""
    for tick in range(start - start % TICKS, end, TICKS):
        if tick < start:
            continue
        chord, beat = arr.chord_at(tick), tick % BAR // TICKS
        root = bass_note(chord) + octave
        if beat == 0:
            pair = (root, root + 7)
        elif beat == 1:
            pair = (root + 12, root + 12 + third(chord))
        else:
            top = root + 12 + 10 if len(CHORDS[chord][1]) == 4 else root + 19
            pair = (top, root + 12 + third(chord))
        for i, note in enumerate(pair):
            at, length = tick + i * EIGHTH + arr.jitter(), EIGHTH * (3 if i == 0 else 2)
            velocity_now = velocity + (8 if beat == 0 and i == 0 else 0) + arr.rng.randint(-3, 3)
            if not busy(avoid, note, at, length):
                part.add(at, note, velocity_now, length)


def broken_chords(arr: Arrangement, part: Part, start: int, end: int, velocity: int, avoid: list = ()) -> None:
    """A roomy left hand in quarter notes: each beat one tone of its chord's open
    voicing, the root, the fifth, the tenth, left to ring under the pedal."""
    for tick in range(start, end, TICKS):
        chord, beat = arr.chord_at(tick), tick % BAR // TICKS
        note, at = open_chord(chord)[beat], tick + arr.jitter(5)
        velocity_now = velocity + (6 if beat == 0 else 0) + arr.rng.randint(-2, 2)
        if not busy(avoid, note, at, 2 * TICKS):
            part.add(at, note, velocity_now, 2 * TICKS)


def rolling(arr: Arrangement, part: Part, start: int, end: int, velocity: int, avoid: list = ()) -> None:
    """The left hand in eighths, up its chord's open voicing and back down:
    root, fifth, tenth, twelfth (or the seventh), tenth, fifth."""
    for tick in range(start, end, EIGHTH):
        chord = arr.chord_at(tick)
        root, fifth, tenth = open_chord(chord)
        intervals = CHORDS[chord][1]
        top = root + 12 + intervals[3] if len(intervals) == 4 else root + 19
        note, at = (root, fifth, tenth, top, tenth, fifth)[tick % BAR // EIGHTH], tick + arr.jitter(5)
        velocity_now = velocity + (6 if tick % BAR == 0 else 0) + arr.rng.randint(-2, 2)
        if not busy(avoid, note, at, 3 * EIGHTH):
            part.add(at, note, velocity_now, 3 * EIGHTH)


def pedal_by_chord(arr: Arrangement, part: Part, start: int, end: int) -> None:
    for tick, length, _ in arr.chord_spans(start, end):
        part.pedal.append((tick + 40, 127))
        part.pedal.append((tick + length - 25, 0))


def voice_lead(previous: list, chord: str, low: int, high: int, count: int = 2) -> list:
    """count tones of a chord between two notes, as near as they can be to the
    previous voicing (tones the chords share stay put), with the chord's third,
    and its seventh if it has one, before its root; none a step apart."""
    root, intervals = CHORDS[chord]
    third_class = (root + intervals[1]) % 12
    seventh = (root + intervals[3]) % 12 if len(intervals) == 4 else None
    best, best_cost = None, math.inf
    for combo in itertools.combinations(chord_notes(chord, low, high), count):
        classes = {n % 12 for n in combo}
        if len(classes) < count or any(b - a < 3 for a, b in zip(combo, combo[1:])):
            continue
        cost = (0 if third_class in classes else 6) + (3 if seventh is not None and seventh not in classes else 0)
        cost += 1 if root in classes else 0
        if previous:
            cost += sum(abs(a - b) for a, b in zip(sorted(previous), combo))
        else:
            cost += sum(abs(n - (low + high) / 2) for n in combo) / 2
        if cost < best_cost:
            best, best_cost = list(combo), cost
    return best or previous


def breathe(arr: Arrangement, part: Part, low: int, high: int, start: int = 0) -> None:
    """Expression (CC11), an eighth at a time from start: rising to the middle of
    each phrase (the intro is one) and falling at its end, as players breathe
    with the tune; over the last chord it swells a little and dies away."""
    for tick in range(start, arr.end, EIGHTH):
        if tick < arr.intro:
            begin, length = 0, arr.intro
        else:
            begin, length = arr.intro + (tick - arr.intro) // arr.phrase * arr.phrase, arr.phrase
        part.expression.append((tick, round(low + (high - low) * math.sin(math.pi * (tick - begin) / length))))
    steps = 2 * BAR // EIGHTH
    for i in range(steps):
        x = 0.25 + 0.75 * i / (steps - 1)
        part.expression.append((arr.end + i * EIGHTH, round(low + (high - low) * math.sin(math.pi * x))))


def gliss(arr: Arrangement, harp: Part, tick: int, length: int, chord: str, low: int, high: int,
          velocity: int) -> None:
    """A harp glissando up a chord's tones (its pedals set to the chord), from low
    to high within length ticks."""
    notes = chord_notes(chord, low, high)
    for i, note in enumerate(notes):
        harp.add(tick + i * length // len(notes), note, velocity + 8 * i // len(notes), BAR)


def strings(arr: Arrangement, start: int, end: int, velocity: int) -> None:
    """Held chords: the root in the cellos, two more tones in the violas, each
    chord voiced from the one before."""
    cellos = arr.part("cellos", "cellos", "bass", 0.35, reverb=0.35)
    violas = arr.part("violas", "violas", "pad", 0.15, reverb=0.35)
    for tick, length, chord in arr.chord_spans(start, end):
        cellos.add(tick + arr.jitter(6), bass_note(chord), velocity + 4, length + 20, tie=True)
        violas.voicing = voice_lead(violas.voicing, chord, 52, 67)
        for note in violas.voicing:
            violas.add(tick + arr.jitter(6), note, velocity, length + 20, tie=True)


def descant(arr: Arrangement, part: Part, start: int, end: int, velocity: int) -> None:
    """A slow line over the tune: one chord tone per chord, at least a minor third
    above the melody sounding with it, moving to the nearest tone."""
    tune = [(t, n, l) for t, n, l, verse, _ in arr.melody() if verse == arr.last]
    previous = None
    for tick, length, chord in arr.chord_spans(start, end):
        top = max((n for t, n, l in tune if t < tick + length and tick < t + l), default=67)
        options = chord_notes(chord, max(72, top + 3), 86)
        if not options:
            previous = None
            continue
        note = min(options, key=lambda n: abs(n - (previous or 76)))
        part.add(tick + arr.jitter(6), note, velocity, length + 20, tie=True)
        previous = note


def held_keys(notes: list, tick: int) -> set:
    return {n for t, n, _, l in notes if t <= tick < t + l}


def arrange_piano(arr: Arrangement, instrument: str = "piano") -> None:
    piano = arr.part("piano", instrument, "piano", 0.0, reverb=0.25)
    for tick, note, length, verse, position in arr.melody():
        if verse < 0:
            velocity = 52 + 6 * position
        elif verse < arr.last:
            velocity = 66 + 12 * shape(position)
        else:
            velocity = 80 + 14 * shape(position)
        piano.add(tick + arr.jitter(5), note, velocity + arr.rng.randint(-3, 3), length - 15)
        if verse == arr.last and (length >= TICKS or tick % BAR == 0):  # the last verse sings in thirds and sixths
            second = harmony_below(arr.chord_at(tick), note)
            if second is not None:
                piano.add(tick + arr.jitter(5), second, velocity - 18, length - 15)
    tune = list(piano.notes)
    flowing_bass(arr, piano, 0, arr.verses[0], 40, avoid=tune)
    flowing_bass(arr, piano, arr.verses[0], arr.verses[-1], 48, avoid=tune)
    flowing_bass(arr, piano, arr.verses[-1], arr.end, 56, avoid=tune)
    pedal_by_chord(arr, piano, 0, arr.end)
    held = held_keys(tune, arr.end + 100)  # the melody's last note
    for note, velocity in ((36, 60), (48, 54), (55, 50), (64, 50), (72, 46)):  # the last chord, rolled
        if note not in held:
            piano.add(arr.end + (note - 36) * 3, note, velocity, BAR * 2)
    piano.pedal += [(arr.end + 20, 127), (arr.end + 2 * BAR, 0)]  # held, then let go


def arrange_chill(arr: Arrangement) -> None:
    piano = arr.part("piano", "piano", "piano", 0.0, reverb=0.32)
    piano.tone["shelf"] = [5000, -3]  # a softer, darker tone
    for tick, note, length, verse, position in arr.melody():
        lift = shape(position)
        if verse < 0:
            velocity = 40 + 6 * position
        elif verse < arr.last:
            velocity = 46 + 10 * lift
            if verse > 0:  # the middle time of three: an octave up, light as a music box
                note, velocity = note + 12, velocity - 4
        else:
            velocity = 50 + 12 * lift
        at = tick + 10 + arr.jitter(6)  # a little behind the beat: unhurried
        piano.add(at, note, velocity + arr.rng.randint(-2, 2), length - 10)
        if verse == arr.last and (length >= TICKS or tick % BAR == 0):
            second = harmony_below(arr.chord_at(tick), note)
            if second is not None:
                piano.add(at - 12, second, velocity - 16, length - 10)  # just before the tune: gently rolled
    tune = list(piano.notes)
    for tick, length, chord in arr.chord_spans(0, arr.verses[0]):  # the intro: open chords, slowly rolled
        for i, note in enumerate(open_chord(chord)):
            if not busy(tune, note, tick + i * 40, length):
                piano.add(tick + i * 40 + arr.jitter(4), note, 36 - 2 * i, length)
    broken_chords(arr, piano, arr.verses[0], arr.verses[-1], 38, avoid=tune)
    rolling(arr, piano, arr.verses[-1], arr.end, 34, avoid=tune)
    pedal_by_chord(arr, piano, 0, arr.end)
    held = held_keys(tune, arr.end + 100)  # the melody's last note
    for i, (note, velocity) in enumerate(((36, 46), (43, 42), (52, 40), (60, 40), (64, 38), (67, 36))):
        if note not in held:  # the last chord, rolled slowly
            piano.add(arr.end + i * 50, note, velocity, 3 * BAR)
    piano.add(arr.end + TICKS + 40, 84, 30, 2 * BAR)  # and a high C, soft as a far bell
    piano.pedal += [(arr.end + 20, 127), (arr.end + 3 * BAR, 0)]


def arrange_bells(arr: Arrangement) -> None:
    chimes = arr.part("chimes", "chimes", "melody", 0.2, reverb=0.4)
    vibes = arr.part("vibes", "vibes", "melody", -0.2, reverb=0.4)
    glock = arr.part("glock", "glock", "sparkle", 0.3, reverb=0.45)
    harp = arr.part("harp", "harp", "harp", -0.4, reverb=0.35)
    for tick, note, length, verse, position in arr.melody():
        lift = shape(position)
        if verse < 0 or verse == arr.last:  # the intro (an octave up already) and the last verse: vibraphone
            vibes.add(tick + arr.jitter(4), note, (46 if verse < 0 else 54) + 10 * lift, length)
            if verse == arr.last and tick >= arr.end - arr.phrase:  # a glint over the last phrase
                glock.add(tick + arr.jitter(4), note + 12, 40 + 6 * lift, length)
        else:
            chimes.add(tick + arr.jitter(4), note, 58 + 10 * lift, length)
    flowing_bass(arr, harp, 0, arr.verses[0], 48)
    flowing_bass(arr, harp, arr.verses[0], arr.verses[-1], 54)
    flowing_bass(arr, harp, arr.verses[-1], arr.end, 50)
    gliss(arr, harp, arr.verses[-1] - TICKS, TICKS, arr.chord_at(arr.verses[-1] - TICKS), 55, 84, 46)
    strings(arr, arr.verses[-1], arr.end + 2 * BAR, 42)
    for name in ("cellos", "violas"):
        breathe(arr, arr.parts[name], 84, 112, start=arr.verses[-1])
    tonic = arr.chord_at(arr.end)
    for i, note in enumerate(chord_notes(tonic, 60, 72)):  # the end: a soft chord on the hand chimes
        chimes.add(arr.end + i * 60, note, 50, 2 * BAR)
    harp.add(arr.end, bass_note(tonic), 56, 2 * BAR)
    gliss(arr, harp, arr.end + TICKS, 2 * TICKS, tonic, 60, 96, 40)


def arrange_orchestra(arr: Arrangement) -> None:
    flute = arr.part("flute", "flute", "melody", -0.1, reverb=0.35)
    violins = arr.part("violins", "violins", "melody", -0.35, reverb=0.35)
    glock = arr.part("glock", "glock", "sparkle", 0.3, reverb=0.45)
    for tick, note, length, verse, position in arr.melody():
        lift = shape(position)
        if verse < arr.last:  # the intro (an octave up already) and the first verse: the flute, softly
            flute.add(tick + arr.jitter(4), note, (48 if verse < 0 else 52) + 8 * lift, length - 10)
        else:  # the violins, from their soft layer into the full one at the height of the verse
            violins.add(tick + arr.jitter(4), note, 52 + 20 * lift, length + 20)
            if tick >= arr.end - arr.phrase:
                glock.add(tick + arr.jitter(4), note + 12, 40, length)
    harp = arr.part("harp", "harp", "harp", -0.45, reverb=0.35)
    flowing_bass(arr, harp, 0, arr.verses[0], 48, octave=12)
    flowing_bass(arr, harp, arr.verses[0], arr.verses[-1], 52)
    flowing_bass(arr, harp, arr.verses[-1], arr.end, 44, octave=12)
    gliss(arr, harp, arr.verses[-1] - TICKS, TICKS, arr.chord_at(arr.verses[-1] - TICKS), 55, 86, 48)
    strings(arr, 0, arr.verses[-1], 40)
    strings(arr, arr.verses[-1], arr.end + 2 * BAR, 54)
    pizz = arr.part("basses-pizz", "basses-pizz", "low", 0.45, reverb=0.3)
    for tick, _, chord in arr.chord_spans(arr.verses[0], arr.verses[-1]):
        if tick % BAR == 0:  # plucked on the downbeats of the first verse
            pizz.add(tick + arr.jitter(4), low_bass(chord), 54, TICKS)
    basses = arr.part("basses", "basses", "low", 0.45, reverb=0.35)
    for tick, length, chord in arr.chord_spans(arr.verses[-1], arr.end + 2 * BAR):
        basses.add(tick + arr.jitter(6), low_bass(chord), 60, length + 20, tie=True)
    horns = arr.part("horns", "horns", "pad", 0.2, reverb=0.4)
    middle = arr.verses[-1] + arr.verse // 2
    for tick, length, chord in arr.chord_spans(middle, arr.end + 2 * BAR):
        horns.voicing = voice_lead(horns.voicing, chord, 53, 65)
        for note in horns.voicing:
            horns.add(tick + arr.jitter(6), note, 40, length + 20, tie=True)
    flute_descant = arr.part("descant", "flute", "descant", 0.15, reverb=0.4)
    descant(arr, flute_descant, arr.verses[-1] + arr.phrase, arr.end, 50)
    timpani = arr.part("timpani", "timpani", "drum", 0.0, reverb=0.4)
    timpani.add(arr.end, 48, 46, 2 * BAR)  # a soft roll under the last chord
    if arr.song.name == "wish":  # a sleigh ride for the lively tune: one shake a bar in the last verse
        sleigh = arr.part("sleigh", "sleigh", "drum", 0.4, reverb=0.25)
        for tick in range(arr.verses[-1], arr.end, BAR):
            sleigh.add(tick + arr.jitter(6), 60, 46, TICKS)
    tonic = arr.chord_at(arr.end)
    harp.add(arr.end, bass_note(tonic), 58, 2 * BAR)
    gliss(arr, harp, arr.end + TICKS, 2 * TICKS, tonic, 60, 96, 42)
    breathe(arr, flute, 100, 120)
    breathe(arr, violins, 100, 120, start=arr.verses[-1])
    breathe(arr, flute_descant, 84, 112, start=arr.verses[-1] + arr.phrase)
    for name in ("cellos", "violas"):
        breathe(arr, arr.parts[name], 86, 116)
    breathe(arr, basses, 86, 116, start=arr.verses[-1])
    breathe(arr, horns, 80, 112, start=middle)


@dataclass
class Style:
    arrange: Callable
    tempo: float = 1.0  # times the carol's own tempo
    breath: float = 0.92  # the tempo of the last beat of each phrase, times the tempo
    hall: float = 2.2  # the hall's reverb time (s)
    repeat_short: bool = False  # play a short tune (eight bars or fewer) three times


STYLES = {
    "piano": Style(arrange_piano),
    "salamander": Style(lambda arr: arrange_piano(arr, "salamander")),
    "chill": Style(arrange_chill, tempo=0.82, breath=0.86, hall=2.6, repeat_short=True),
    "bells": Style(arrange_bells, hall=2.6),
    "orchestra": Style(arrange_orchestra, hall=2.4),
}


def untangle(notes: list) -> tuple[list, int]:
    """The notes in time order, none struck while its key still sounds: a
    note-off ends every voice of its key (in sfizz as in MIDI), which would cut
    the later note short to a scratch. The earlier note ends just before the
    later one instead, and two notes struck together on a key become one.
    Returns the notes and how many it changed."""
    by_key, changed, result = {}, 0, []
    for note in sorted(notes):
        by_key.setdefault(note[1], []).append(note)
    for same in by_key.values():
        kept = [same[0]]
        for tick, key, velocity, length in same[1:]:
            start, _, held_velocity, held = kept[-1]
            if tick - start < 40:  # struck together: one note, the louder and the longer
                kept[-1] = (start, key, max(held_velocity, velocity), max(held, tick + length - start))
                changed += 1
                continue
            if start + held > tick - 10:
                kept[-1] = (start, key, held_velocity, tick - 10 - start)
                changed += 1
            kept.append((tick, key, velocity, length))
        result += kept
    return sorted(result), changed


def write_part(part: Part, tempos: list, path: Path) -> int:
    notes, changed = untangle(part.notes)
    messages = []
    for tick, note, velocity, length in notes:
        messages.append((tick + length, 0, mido.Message("note_off", note=note, velocity=0)))
        messages.append((tick, 2, mido.Message("note_on", note=note, velocity=velocity)))
    for tick, value in part.pedal:
        messages.append((max(0, tick), 1, mido.Message("control_change", control=64, value=value)))
    for tick, value in part.expression:
        messages.append((max(0, tick), 1, mido.Message("control_change", control=11, value=value)))
    for tick, bpm in tempos:
        messages.append((tick, -1, mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm))))
    midi = mido.MidiFile(ticks_per_beat=TICKS)
    track = mido.MidiTrack()
    midi.tracks.append(track)
    track.append(mido.MetaMessage("time_signature", numerator=3, denominator=4))
    now = 0
    for tick, _, message in sorted(messages, key=lambda m: (m[0], m[1])):
        track.append(message.copy(time=tick - now))
        now = tick
    track.append(mido.MetaMessage("end_of_track", time=8 * TICKS))  # where rendering stops: time to ring
    midi.save(path)
    return changed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--songs", nargs="+", default=list(SONGS), choices=list(SONGS))
    parser.add_argument("--styles", nargs="+", default=["piano", "chill", "bells", "orchestra"],
                        choices=list(STYLES))
    args = parser.parse_args()
    for name in args.songs:
        for style_name in args.styles:
            song, style = SONGS[name], STYLES[style_name]
            verses = 3 if style.repeat_short and len(song.chords) <= 8 else 2
            arr = Arrangement(song, verses, style.tempo, style.breath)
            style.arrange(arr)
            folder = args.out / f"{name}-{style_name}"
            folder.mkdir(parents=True, exist_ok=True)
            sheet, untangled = [], 0
            for part_name, part in arr.parts.items():
                untangled += write_part(part, arr.tempos, folder / f"{part_name}.mid")
                library, sfz = INSTRUMENTS[part.instrument]
                sheet.append({"part": part_name, "library": library, "sfz": sfz, "role": part.role,
                              "gain_db": ROLES[part.role], "pan": part.pan, "reverb": part.reverb,
                              "tone": part.tone, "notes": len(part.notes)})
            (folder / "mix.json").write_text(json.dumps({"hall": {"rt60": style.hall}, "parts": sheet}, indent=2))
            print(f"{folder.name}: {arr.bpm:.0f} bpm, {len(arr.verses)} verses, {len(sheet)} parts "
                  f"({', '.join(p['part'] for p in sheet)}), {arr.seconds(0, arr.end + 2 * BAR):.0f} s, "
                  f"{untangled} repeated notes untangled")


if __name__ == "__main__":
    main()
