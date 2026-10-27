"""Arranges the test's carols for real instrument samples, without any AI
model: one MIDI file per instrument, in several styles, plus mix.json (the
hall, and each part's instrument, role, stereo position and tone) for
render_samples.py:

    python arrange.py out/sampled [--songs wish silent-night first-noel ...] [--styles piano chill ...]

The carols are public-domain melodies and chords: We Wish You a Merry
Christmas and Silent Night (make_source.py), The First Noel, Joy to the
World, O Holy Night, Jingle Bells and Deck the Halls (carols.py), in 3/4,
2/4, 4/4 and 12/8, each in its own key. Every style plays an intro (the last
phrase, an octave up), the verses (the last one fuller) and a held last
chord, slowing down over the last two bars. The parts are written from the
same chords, beat by beat, so they always agree:
- piano (VCSL's Steinway B; "salamander": the Salamander Grand Piano, CC-BY
  3.0, by Alexander Holm): the melody over a flowing left hand, with sustain
  pedal; in the last verse a chord tone a third to a sixth under the longer
  notes sings with the melody;
- the gentle piano styles, slower and softer than piano, with its sound, the
  melody a little behind the beat and longer breaths at the phrase ends (a
  short tune is played three times):
  - chill: open broken chords that leave room, the middle time (of three) an
    octave up;
  - lullaby: the tune an octave up throughout, like a music box, over a
    rocking left hand, slowest of all;
  - flowing: the left hand rolling in eighths, up an open chord and back;
  - hymn: soft chords under the tune, as a hymn is played;
  - piano-strings: chill, on a bed of soft strings;
  - felt: the tone of the soft sleep-music pianos (a low-pass at 900 Hz, as
    a felt-hammered piano sounds), the melody at its own pitch over a steady
    left hand rolling in eighths from the first bar; felt-noise: the same on
    a soft hush of pink noise, as baby-sleep recordings have;
- ballad and pulse, in the manner of the slow pop Christmas pianos: an intro
  in free time of the tune's last chords alone, rolled from a deep bass with
  an added ninth (or the seventh), then the tune an octave up, doubled at the
  octave in the last verse, in a longer hall:
  - ballad (about 74 bpm): the left hand in eighths up and down two octaves
    of each chord from the middle of the keyboard, its root deep under each bar;
  - pulse (about 88 bpm): a heartbeat of lightly detached eighths, the root
    and fifth of each chord (the third on the beats), the root deep under each bar;
- bells: the vibraphone with hand chimes an octave up, where bells sing, a
  glockenspiel glinting on the longer notes (it sounds an octave above its
  keys), a harp, a soft string bed, a tubular bell tolling each verse in;
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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import mido

import carols
import make_source

TICKS = 480  # per quarter note
EIGHTH = TICKS // 2
HOLD_SECONDS = 4.5  # the longest a held note sounds: sustained samples are not looped, the shortest last about 5 s

NOTE_CLASSES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
# A chord's intervals above its root, by the kind its name ends with.
KINDS = {"": (0, 4, 7), "m": (0, 3, 7), "7": (0, 4, 7, 10), "m7": (0, 3, 7, 10), "maj7": (0, 4, 7, 11),
         "dim": (0, 3, 6), "sus4": (0, 5, 7), "7sus4": (0, 5, 7, 10)}


class ChordBook(dict):
    """Root pitch class, and the chord's intervals above the root, for any
    chord name: a root (C, F#, Bb) and a kind (m, 7, m7, maj7, dim, sus4, 7sus4)."""

    def __missing__(self, name: str) -> tuple:
        root = NOTE_CLASSES[name[0]]
        kind = name[1:]
        if kind[:1] in ("#", "b"):
            root, kind = (root + (1 if kind[0] == "#" else -1)) % 12, kind[1:]
        self[name] = (root, KINDS[kind])
        return self[name]


CHORDS = ChordBook()

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
    "tubular": ("vcsl", "Idiophones/Struck Idiophones/Tubular Bells 1.sfz"),
    "flute": ("vsco", "FluteSusNV.sfz"),  # without vibrato: the vibrato samples wobble on long notes
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
# edge and the hiss of their recordings; the piano's release samples (the
# dampers' sound as keys are let go, all at once when the pedal lifts: a
# rustle) turned off (dB); and the stereo width (0 mono, 1 as recorded), narrower
# for instruments whose samples, note by note, lean far to one side (a
# vibraphone note 17 dB to the left), so a melody does not hop between ears.
# The VSCO strings and horns are cut steeply where their samples' sound
# sinks into the hiss of the recording: a violin note is 10-17 dB above it
# from 8 kHz up, a horn note 6-10 dB from 2 kHz up.
TONES = {
    # The Steinway's samples each carry a faint hiss, and with the pedal down a
    # dozen of them sound at once: a light rustle heard in every piece with the
    # piano at full range (felt, bells and orchestra had none). Of five
    # listening tests only the one cut above 6 kHz was all but free of it
    # (without the pedal-down samples, or cut at 8 kHz, it stayed); what was
    # left, from 2.5 to 6 kHz in the slow quiet pieces, is hushed in the quiet
    # moments (dehiss: 9-10 dB less hiss there, the brighter moments as they are).
    "piano": {"release_db": -60, "lowpass": 6000, "dehiss": True},
    # The bells' samples, note against the hiss of their own quiet tail: the hand
    # chimes are clean; the soft-mallet vibraphone sounds almost a pure tone, so
    # from 2 kHz up it holds little but hiss (a note 7-20 dB over it); the harp
    # turns to hiss from 5 kHz up, the glockenspiel from 8 kHz, and the tubular
    # bells, the noisiest (hiss only 52-69 dB under the note), from 4 kHz.
    "chimes": {"shelf": [5000, -3], "width": 0.3},
    "vibes": {"lowpass": 2500, "lowpass_order": 4, "width": 0.3, "dehiss": True},
    "glock": {"lowpass": 8000, "lowpass_order": 4, "shelf": [5000, -5], "width": 0.4, "dehiss": True},
    "harp": {"lowpass": 5000, "lowpass_order": 4, "width": 0.7, "dehiss": True},
    "sleigh": {"shelf": [6000, -6], "width": 0.6},
    "tubular": {"lowpass": 4000, "lowpass_order": 4, "width": 0.5, "dehiss": True},
    "flute": {"lowpass": 8000, "shelf": [6000, -2], "width": 0.5},
    "violins": {"lowpass": 6500, "lowpass_order": 4, "shelf": [5000, -2], "width": 0.8, "dehiss": True},
    "violas": {"highpass": 80, "lowpass": 6000, "lowpass_order": 4, "shelf": [4000, -2], "width": 0.8, "dehiss": True},
    "cellos": {"highpass": 40, "lowpass": 5000, "lowpass_order": 4, "shelf": [3500, -2], "width": 0.8, "dehiss": True},
    "basses": {"highpass": 30, "lowpass": 4000, "lowpass_order": 4, "width": 0.7},
    "basses-pizz": {"highpass": 30, "lowpass": 5000, "width": 0.7},
    "horns": {"highpass": 60, "lowpass": 3000, "lowpass_order": 4, "width": 0.7},
    "timpani": {"highpass": 35, "width": 0.7},
}
# How loud each kind of part sits against the melody (dB of its loudness when playing).
ROLES = {"melody": 0.0, "piano": 0.0, "descant": -9.0, "harp": -4.0, "pad": -10.0, "bass": -8.0,
         "bells": -8.0, "bed": -13.0, "low": -12.0, "toll": -14.0, "sparkle": -16.0, "drum": -17.0}


@dataclass
class Song:
    name: str
    bpm: float  # quarter notes a minute
    melody: list  # (MIDI note, or None for a rest; length in eighths), the pickup first
    pickup: float  # eighths of melody before the first bar
    chords: list  # per bar, one chord name per beat
    intro_bars: int  # the last bars of the tune, played as the intro
    beats: int = 3  # beats in a bar
    beat_eighths: int = 2  # eighths in a beat: 2, or 3 in 6/8 and 12/8
    lively: bool = False  # a sleigh ride in the orchestra
    verses: int | None = None  # times the tune is played, whatever the style (else two, three if short)
    breaths: tuple = ()  # the bars (from 0) that end a phrase, if not every fourth

    def seconds(self) -> float:
        """How long the tune lasts at its own tempo."""
        return len(self.chords) * self.beats * self.beat_eighths / 2 * 60 / self.bpm


def per_beat(names: str, beats: int = 3) -> list:
    """Chords bar by bar: a name for the whole bar, or names split by | that
    share it out (one a beat, or each over as many beats)."""
    bars = []
    for bar in names.split():
        split = bar.split("|")
        assert beats % len(split) == 0, bar
        bars.append([name for name in split for _ in range(beats // len(split))])
    return bars


SONGS = {
    "wish": Song("wish", 120, make_source.MELODY, 2,
                 per_beat("C F D7 G E7 Am F|G|G C"), 2, lively=True),
    "silent-night": Song("silent-night", 84, make_source.SILENT_NIGHT, 0,
                         per_beat("C C C C G7 G7 C C F F C C F F C C G7 G7 C C C G7 C C"), 4),
    "first-noel": Song("first-noel", 100, carols.FIRST_NOEL, 2, per_beat(carols.FIRST_NOEL_CHORDS), 4),
    "joy": Song("joy", 104, carols.JOY, 0, per_beat(carols.JOY_CHORDS, 2), 4, beats=2, verses=3,
                breaths=(3, 6, 8, 10, 12)),
    "o-holy-night": Song("o-holy-night", 72, carols.O_HOLY_NIGHT, 7, per_beat(carols.O_HOLY_NIGHT_CHORDS, 4), 2,
                         beats=4, beat_eighths=3, verses=1, breaths=(3, 8, 10, 12, 14, 16, 20)),
    "jingle-bells": Song("jingle-bells", 120, carols.JINGLE_BELLS, 0, per_beat(carols.JINGLE_BELLS_CHORDS, 4), 4,
                         beats=4, lively=True),
    "deck-the-halls": Song("deck-the-halls", 116, carols.DECK_THE_HALLS, 0,
                           per_beat(carols.DECK_THE_HALLS_CHORDS, 4), 2, beats=4, lively=True),
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

    def __init__(self, song: Song, verses: int = 2, tempo: float = 1.0, breath: float = 0.92, seed: int = 7,
                 free_intro: bool = False):
        self.song, self.rng = song, random.Random(seed)
        self.bpm = song.bpm * tempo
        self.beat = song.beat_eighths * EIGHTH  # a quarter note, or a dotted quarter in 6/8 and 12/8
        self.bar = song.beats * self.beat
        self.meter = (song.beats, song.beat_eighths)
        tonic = CHORDS[song.chords[0][0]][0]
        self.scale = {(tonic + step) % 12 for step in (0, 2, 4, 5, 7, 9, 11)}  # the carols are in major keys
        # A free intro (chords alone, in rubato) runs over the tune's last bars,
        # twice as many while that is under 8 s.
        self.free_intro, self.intro_bars = free_intro, song.intro_bars
        while free_intro and 2 * self.intro_bars <= len(song.chords) and self.seconds_at(self.intro_bars) < 8:
            self.intro_bars *= 2
        self.intro = self.intro_bars * self.bar
        self.verse = len(song.chords) * self.bar
        self.phrase = 4 * self.bar
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

    def seconds_at(self, bars: int) -> float:
        """How long some bars last at the steady tempo."""
        return bars * self.bar / TICKS * 60 / self.bpm

    def tempo_map(self, breath: float) -> list:
        """(tick, bpm): a breath on the last beat of every four-bar phrase, as a
        player would take, and slowing over the last two bars to the held chord.
        A free intro goes slower, lingering on the last beat of each bar."""
        bpm, changes = self.bpm, [(0, self.bpm)]
        if self.free_intro:
            changes = [(0, bpm * 0.85)]
            for bar in range(self.intro_bars):
                last_beat = (bar + 1) * self.bar - self.beat
                changes += [(last_beat, bpm * 0.6), (last_beat + self.beat, bpm * 0.85)]
            changes[-1] = (self.intro, bpm)
        slow_from = self.end - 2 * self.bar
        for downbeat in self.verses:
            for bar in self.song.breaths or range(3, len(self.song.chords), 4):
                last_beat = downbeat + (bar + 1) * self.bar - self.beat
                if last_beat + self.beat <= slow_from:
                    changes += [(last_beat, bpm * breath), (last_beat + self.beat, bpm)]
        steps = 2 * self.song.beats + 1  # 35 % slower by the last chord
        for beat in range(steps):
            changes.append((slow_from + beat * self.beat, bpm * (1 - 0.35 * (beat + 1) / steps)))
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
            bar = len(bars) - self.intro_bars + tick // self.bar
        elif tick >= self.end:
            return bars[0][0]
        else:
            bar = (tick - self.intro) % self.verse // self.bar
        return bars[bar][tick % self.bar // self.beat]

    def chord_spans(self, start: int, end: int):
        """(tick, length, chord) for each run of one chord between two ticks."""
        spans, tick = [], start
        while tick < end:
            chord, length = self.chord_at(tick), self.beat
            while tick + length < end and self.chord_at(tick + length) == chord and (tick + length) % self.bar:
                length += self.beat
            spans.append((tick, length, chord))
            tick += length
        return spans

    def melody(self):
        """(tick, note, length, verse, position in the verse 0-1) of the tune: the intro
        (the last bars an octave up, verse -1), then every verse."""
        song, notes = self.song, []
        pickup = round(song.pickup * EIGHTH)
        tune, tick = [], -pickup
        for note, eighths in song.melody:
            if note is not None:
                tune.append((tick, note, round(eighths * EIGHTH)))
            tick += round(eighths * EIGHTH)
        first_intro_tick = (len(song.chords) - self.intro_bars) * self.bar
        intro_end = self.intro - pickup  # where the first verse's pickup starts
        for start, note, length in tune:  # the intro: the last phrase, an octave up
            if start >= first_intro_tick:
                at = start - first_intro_tick
                notes.append((at, note + 12, min(length, intro_end - at), -1, 1.0))
        for verse, downbeat in enumerate(self.verses):
            for index, (start, note, length) in enumerate(tune):
                if verse < self.last and start + length >= self.verse and pickup:
                    length -= pickup  # room for the next verse's pickup
                if verse == self.last and index == len(tune) - 1:
                    length += self.bar  # the last note rings on
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


def ladder(chord: str, root: int) -> dict:
    """The tones a left hand breaks a chord into, from its root up: the fifth,
    the octave, the tenth, and the top (the seventh over the octave, or the twelfth)."""
    intervals = CHORDS[chord][1]
    top = root + 12 + intervals[3] if len(intervals) == 4 else root + 19
    return {"root": root, "fifth": root + 7, "octave": root + 12, "tenth": root + 12 + third(chord), "top": top}


# The left hand's figures for each meter (beats in a bar, eighths in a beat):
# flowing, beat by beat the bass and then the chord broken upwards and back in
# eighths; broken, a roomy tone on each beat; rolling, eighths up the open
# chord and back; rocking, a tone a beat rising through the bar, as a cradle rocks.
FLOWING = {(3, 2): (("root", "fifth"), ("octave", "tenth"), ("top", "tenth")),
           (4, 2): (("root", "fifth"), ("octave", "tenth"), ("top", "tenth"), ("octave", "fifth")),
           (2, 2): (("root", "fifth"), ("octave", "tenth")),
           (4, 3): (("root", "fifth", "octave"), ("tenth", "top", "tenth")) * 2,
           (2, 3): (("root", "fifth", "octave"), ("tenth", "top", "tenth"))}
BROKEN = {(3, 2): ("root", "fifth", "tenth"), (4, 2): ("root", "fifth", "tenth", "fifth"), (2, 2): ("root", "tenth"),
          (4, 3): ("root", "fifth", "tenth", "fifth"), (2, 3): ("root", "tenth")}
ROLLING = {(3, 2): ("root", "fifth", "tenth", "top", "tenth", "fifth"),
           (4, 2): ("root", "fifth", "tenth", "top", "tenth", "fifth", "octave", "fifth"),
           (2, 2): ("root", "fifth", "tenth", "fifth"),
           (4, 3): ("root", "fifth", "tenth", "top", "tenth", "fifth") * 2,
           (2, 3): ("root", "fifth", "tenth", "top", "tenth", "fifth")}
ROCKING = {(3, 2): ("root", "tenth", "top"), (4, 2): ("root", "tenth", "top", "tenth"), (2, 2): ("root", "top"),
           (4, 3): ("root", "tenth", "top", "tenth"), (2, 3): ("root", "top")}


def harmony_below(chord: str, note: int) -> int | None:
    """The chord tone a third to a sixth under a melody note, to sing with it."""
    below = [n for n in chord_notes(chord, note - 9, note - 3)]
    return below[-1] if below and below[-1] >= 59 else None


def shape(position: float) -> float:
    """Phrase dynamics: 0 at the start and end of a verse, 1 in the middle."""
    return 1 - abs(position - 0.5) * 2


def flowing_bass(arr: Arrangement, part: Part, start: int, end: int, velocity: int, octave: int = 0,
                 avoid: list = ()) -> None:
    """A left hand / harp: the bass on the beat, then the chord broken upwards
    and back in eighths, beat by beat with that beat's chord. Keys the melody is
    holding (avoid) are left to it."""
    for tick in range(start - start % arr.beat, end, arr.beat):
        if tick < start:
            continue
        chord, beat = arr.chord_at(tick), tick % arr.bar // arr.beat
        tones = ladder(chord, bass_note(chord) + octave)
        for i, name in enumerate(FLOWING[arr.meter][beat]):
            note = tones[name]
            at, length = tick + i * EIGHTH + arr.jitter(), EIGHTH * (3 if i == 0 else 2)
            velocity_now = velocity + (8 if beat == 0 and i == 0 else 0) + arr.rng.randint(-3, 3)
            if not busy(avoid, note, at, length):
                part.add(at, note, velocity_now, length)


def broken_chords(arr: Arrangement, part: Part, start: int, end: int, velocity: int, avoid: list = ()) -> None:
    """A roomy left hand in quarter notes: each beat one tone of its chord's open
    voicing, the root, the fifth, the tenth, left to ring under the pedal."""
    for tick in range(start, end, arr.beat):
        chord, beat = arr.chord_at(tick), tick % arr.bar // arr.beat
        note, at = ladder(chord, bass_note(chord))[BROKEN[arr.meter][beat]], tick + arr.jitter(5)
        velocity_now = velocity + (6 if beat == 0 else 0) + arr.rng.randint(-2, 2)
        if not busy(avoid, note, at, 2 * arr.beat):
            part.add(at, note, velocity_now, 2 * arr.beat)


def rolling(arr: Arrangement, part: Part, start: int, end: int, velocity: int, avoid: list = ()) -> None:
    """The left hand in eighths, up its chord's open voicing and back down:
    root, fifth, tenth, twelfth (or the seventh), tenth, fifth."""
    for tick in range(start, end, EIGHTH):
        chord = arr.chord_at(tick)
        note = ladder(chord, bass_note(chord))[ROLLING[arr.meter][tick % arr.bar // EIGHTH]]
        at = tick + arr.jitter(5)
        velocity_now = velocity + (6 if tick % arr.bar == 0 else 0) + arr.rng.randint(-2, 2)
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
    steps = 2 * arr.bar // EIGHTH
    for i in range(steps):
        x = 0.25 + 0.75 * i / (steps - 1)
        part.expression.append((arr.end + i * EIGHTH, round(low + (high - low) * math.sin(math.pi * x))))


def gliss(arr: Arrangement, harp: Part, tick: int, length: int, chord: str, low: int, high: int,
          velocity: int) -> None:
    """A harp glissando up a chord's tones (its pedals set to the chord), from low
    to high within length ticks."""
    notes = chord_notes(chord, low, high)
    for i, note in enumerate(notes):
        harp.add(tick + i * length // len(notes), note, velocity + 8 * i // len(notes), arr.bar)


def strings(arr: Arrangement, start: int, end: int, velocity: int, roles: tuple = ("bass", "pad")) -> None:
    """Held chords: the root in the cellos, two more tones in the violas, each
    chord voiced from the one before."""
    cellos = arr.part("cellos", "cellos", roles[0], 0.35, reverb=0.35)
    violas = arr.part("violas", "violas", roles[1], 0.15, reverb=0.35)
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
        if verse == arr.last and (length >= arr.beat or tick % arr.bar == 0):  # the last verse sings in thirds and sixths
            second = harmony_below(arr.chord_at(tick), note)
            if second is not None:
                piano.add(tick + arr.jitter(5), second, velocity - 18, length - 15)
    tune = list(piano.notes)
    flowing_bass(arr, piano, 0, arr.verses[0], 40, avoid=tune)
    flowing_bass(arr, piano, arr.verses[0], arr.verses[-1], 48, avoid=tune)
    flowing_bass(arr, piano, arr.verses[-1], arr.end, 56, avoid=tune)
    pedal_by_chord(arr, piano, 0, arr.end)
    held = held_keys(tune, arr.end + 100)  # the melody's last note
    tonic = arr.chord_at(arr.end)
    root, tenth = bass_note(tonic), bass_note(tonic) + 24 + third(tonic)
    for note, velocity in ((root, 60), (root + 12, 54), (root + 19, 50), (tenth, 50), (root + 36, 46)):  # the last chord, rolled
        if note not in held:
            piano.add(arr.end + (note - root) * 3, note, velocity, arr.bar * 2)
    piano.pedal += [(arr.end + 20, 127), (arr.end + 2 * arr.bar, 0)]  # held, then let go


def gentle_melody(arr: Arrangement, piano: Part, soft: int, loud: int, up: tuple = (), late: int = 8,
                  harmony: bool = True, intro: bool = True, octaves: bool = False) -> list:
    """The tune for the gentle piano styles, a little behind the beat
    (unhurried), growing from soft in the first verse to loud in the last, each
    verse rising to its middle; the verses in up an octave higher, light as a
    music box; in the last verse a chord tone a third to a sixth under the
    longer notes, struck just before the tune (with octaves, the tune's own
    note an octave down instead, fuller). Without intro the tune waits for the
    first verse. Returns the notes, whose keys the left hand leaves alone."""
    for tick, note, length, verse, position in arr.melody():
        if verse < 0 and not intro:
            continue
        if verse < 0:
            velocity = soft - 4 + 4 * position
        else:
            velocity = soft + (loud - soft) * verse / max(1, arr.last) + 10 * shape(position)
        note += 12 if verse in up else 0
        at = tick + late + arr.jitter(6)
        piano.add(at, note, velocity + arr.rng.randint(-2, 2), length - 10)
        if octaves and verse == arr.last and length >= arr.beat:
            piano.add(at - 12, note - 12, velocity - 16, length - 10)
        elif harmony and verse == arr.last and (length >= arr.beat or tick % arr.bar == 0):
            second = harmony_below(arr.chord_at(tick), note)
            if second is not None:
                piano.add(at - 12, second, velocity - 14, length - 10)
    return list(piano.notes)


def rolled_intro(arr: Arrangement, piano: Part, tune: list, velocity: int) -> None:
    """The intro's chords, open and slowly rolled, under the tune's last phrase."""
    for tick, length, chord in arr.chord_spans(0, arr.verses[0]):
        for i, note in enumerate(open_chord(chord)):
            if not busy(tune, note, tick + i * 40, length):
                piano.add(tick + i * 40 + arr.jitter(4), note, velocity - 2 * i, length)


def rocking(arr: Arrangement, part: Part, start: int, end: int, velocity: int, avoid: list = ()) -> None:
    """A cradle's rocking: on each beat one tone of its chord, rising through the
    bar, the root, the tenth, the twelfth (or the seventh), left to ring."""
    for tick in range(start, end, arr.beat):
        chord, beat = arr.chord_at(tick), tick % arr.bar // arr.beat
        note, at = ladder(chord, bass_note(chord))[ROCKING[arr.meter][beat]], tick + arr.jitter(5)
        velocity_now = velocity - 3 * beat + arr.rng.randint(-2, 2)
        if not busy(avoid, note, at, 2 * arr.beat):
            part.add(at, note, velocity_now, 2 * arr.beat)


def chord_end(arr: Arrangement, tick: int) -> int:
    """Where the chord sounding at a tick gives way to the next (or its bar ends)."""
    downbeat = tick - tick % arr.bar
    return next(t + l for t, l, _ in arr.chord_spans(downbeat, downbeat + arr.bar) if t <= tick < t + l)


def hymn_voices(arr: Arrangement, piano: Part, velocity: int, avoid: list) -> None:
    """Harmony as a hymn is played: on every melody note that falls on a beat (or
    lasts a beat), two chord tones under it, each a third to a sixth below the
    voice above (alto, then tenor), and the root of each chord in the bass."""
    for tick, note, length, verse, _ in arr.melody():
        if verse < 0 or (tick % arr.beat and length < arr.beat):
            continue  # the intro and the passing notes go alone
        chord, above = arr.chord_at(tick), note
        span = min(length, chord_end(arr, tick) - tick)
        for i, floor in enumerate((55, 48)):
            options = chord_notes(chord, max(floor, above - 9), above - 3)
            if not options:
                break
            above = options[-1]
            if not busy(avoid, above, tick, span):
                piano.add(tick - 4 * i + arr.jitter(4), above, velocity - 4 * i + arr.rng.randint(-2, 2), span - 10)
    for tick, length, chord in arr.chord_spans(arr.verses[0], arr.end):
        if not busy(avoid, bass_note(chord), tick, length):
            piano.add(tick + arr.jitter(4), bass_note(chord), velocity + 2, length - 10)


def gentle_end(arr: Arrangement, piano: Part, tune: list, velocity: int) -> None:
    """The last chord, open and rolled slowly up from the bass, the pedal held,
    then its keynote high up, soft as a far bell; keys the tune still holds are
    left to it."""
    held = held_keys(tune, arr.end + 100)
    tonic = arr.chord_at(arr.end)
    root, up = bass_note(tonic), third(tonic)
    rolled = ((root, 0), (root + 7, 4), (root + 12 + up, 6), (root + 24, 6), (root + 24 + up, 8), (root + 31, 10))
    for i, (note, softer) in enumerate(rolled + ((root + 48, 14),)):
        if note not in held:
            piano.add(arr.end + (i * 50 if i < len(rolled) else arr.beat + 40), note, velocity - softer, 3 * arr.bar)
    piano.pedal += [(arr.end + 20, 127), (arr.end + 3 * arr.bar, 0)]


def gentle_piano(arr: Arrangement) -> Part:
    return arr.part("piano", "piano", "piano", 0.0, reverb=0.25)


def arrange_chill(arr: Arrangement) -> None:
    piano = gentle_piano(arr)
    tune = gentle_melody(arr, piano, 54, 60, up=tuple(range(1, arr.last)))
    rolled_intro(arr, piano, tune, 40)
    broken_chords(arr, piano, arr.verses[0], arr.verses[-1], 40, avoid=tune)
    rolling(arr, piano, arr.verses[-1], arr.end, 38, avoid=tune)
    pedal_by_chord(arr, piano, 0, arr.end)
    gentle_end(arr, piano, tune, 50)


def arrange_lullaby(arr: Arrangement) -> None:
    piano = gentle_piano(arr)
    tune = gentle_melody(arr, piano, 50, 54, up=tuple(range(len(arr.verses))))
    rolled_intro(arr, piano, tune, 38)
    rocking(arr, piano, arr.verses[0], arr.end, 38, avoid=tune)
    pedal_by_chord(arr, piano, 0, arr.end)
    gentle_end(arr, piano, tune, 46)


def arrange_flowing(arr: Arrangement) -> None:
    piano = gentle_piano(arr)
    tune = gentle_melody(arr, piano, 56, 62)
    rolled_intro(arr, piano, tune, 40)
    rolling(arr, piano, arr.verses[0], arr.end, 40, avoid=tune)
    pedal_by_chord(arr, piano, 0, arr.end)
    gentle_end(arr, piano, tune, 52)


def arrange_hymn(arr: Arrangement) -> None:
    piano = gentle_piano(arr)
    tune = gentle_melody(arr, piano, 58, 62, harmony=False)
    rolled_intro(arr, piano, tune, 40)
    hymn_voices(arr, piano, 44, avoid=tune)
    pedal_by_chord(arr, piano, 0, arr.end)
    gentle_end(arr, piano, tune, 50)


def arrange_piano_strings(arr: Arrangement) -> None:
    arrange_chill(arr)
    strings(arr, arr.verses[0], arr.verses[-1], 36, roles=("bed", "bed"))
    strings(arr, arr.verses[-1], arr.end + 2 * arr.bar, 44, roles=("bed", "bed"))
    for name in ("cellos", "violas"):
        breathe(arr, arr.parts[name], 84, 112, start=arr.verses[0])


def arrange_felt(arr: Arrangement) -> None:
    piano = gentle_piano(arr)
    piano.tone["lowpass"] = 900  # the dark, round tone of felt hammers
    tune = gentle_melody(arr, piano, 50, 52)
    rolling(arr, piano, 0, arr.end, 36, avoid=tune)
    pedal_by_chord(arr, piano, 0, arr.end)
    gentle_end(arr, piano, tune, 46)


def colour(arr: Arrangement, chord: str, root: int) -> int:
    """A tone that colours a chord, an octave and more over its root: the
    seventh of a seventh chord, else the ninth where the key has it (a gentle
    added ninth, as the pop carols voice their chords), else the octave."""
    intervals = CHORDS[chord][1]
    if len(intervals) == 4:
        return root + 12 + intervals[3]
    if intervals[1] in (3, 4) and (root + 2) % 12 in arr.scale:
        return root + 26
    return root + 24


def free_intro(arr: Arrangement, piano: Part, velocity: int) -> None:
    """An intro in free time, as a pianist opens a carol: no tune yet, only the
    chords of its last bars, each rolled slowly up from a deep bass with its
    colour tone on top, and left to ring until the next."""
    for tick, length, chord in arr.chord_spans(0, arr.verses[0]):
        root, up = bass_note(chord), third(chord)
        voicing = sorted({root, root + 12, root + 19, root + 24 + up, colour(arr, chord, root), root + 31})
        for i, note in enumerate(voicing):
            piano.add(tick + i * 70 + arr.jitter(4), note, velocity - 2 * i + arr.rng.randint(-2, 2), length)


# A piano ballad's left hand for each meter: eighths from the root in the
# middle of the keyboard up two octaves of the chord, a colour tone among them.
BALLAD = {(3, 2): ("low", "fifth", "octave", "tenth", "twelfth", "colour"),
          (4, 2): ("low", "fifth", "octave", "tenth", "twelfth", "tenth", "colour", "fifth"),
          (2, 2): ("low", "fifth", "octave", "tenth"),
          (4, 3): ("low", "fifth", "octave", "tenth", "octave", "fifth", "low", "fifth", "octave", "tenth",
                   "twelfth", "colour"),
          (2, 3): ("low", "fifth", "octave", "tenth", "twelfth", "colour")}


def ballad_hand(arr: Arrangement, part: Part, start: int, end: int, velocity: int, avoid: list = ()) -> None:
    """The left hand of a slow piano ballad: eighths rising and falling through
    two octaves of the chord, from its root in the middle of the keyboard
    (none over D5, where the tune sings), and under each bar its root an
    octave lower, deep and soft, ringing under the pedal."""
    for tick in range(start, end, EIGHTH):
        chord = arr.chord_at(tick)
        root = bass_note(chord)
        tones = {"low": root + 12, "fifth": root + 19, "octave": root + 24, "tenth": root + 24 + third(chord),
                 "twelfth": root + 31, "colour": colour(arr, chord, root)}
        note = tones[BALLAD[arr.meter][tick % arr.bar // EIGHTH]]
        while note > 74:
            note -= 12
        at = tick + arr.jitter(5)
        velocity_now = velocity + (4 if tick % arr.beat == 0 else 0) + arr.rng.randint(-2, 2)
        if not busy(avoid, note, at, 3 * EIGHTH):
            part.add(at, note, velocity_now, 3 * EIGHTH)
        if tick % arr.bar == 0 and not busy(avoid, root, at, arr.bar):
            part.add(at - 6, root, velocity + 2, arr.bar)


def pulse(arr: Arrangement, part: Part, start: int, end: int, velocity: int, avoid: list = ()) -> None:
    """The heartbeat of the slow pop carols: every eighth, lightly detached, the
    chord's root and fifth together in the middle of the keyboard, its third
    added on each beat, and under each bar its root deep and soft."""
    for tick in range(start, end, EIGHTH):
        chord = arr.chord_at(tick)
        root = bass_note(chord)
        low = root + 12 if root + 12 >= 52 else root + 24
        notes = [low, low + 7] + ([low + third(chord)] if tick % arr.beat == 0 else [])
        at = tick + arr.jitter(4)
        accent = 6 if tick % arr.bar == 0 else 3 if tick % arr.beat == 0 else 0
        for note in notes:
            if not busy(avoid, note, at, EIGHTH):
                part.add(at, note, velocity + accent + arr.rng.randint(-2, 2), EIGHTH - 30)
        if tick % arr.bar == 0 and not busy(avoid, root, at, arr.bar):
            part.add(at - 6, root, velocity + 8, arr.bar)


def arrange_ballad(arr: Arrangement) -> None:
    piano = arr.part("piano", "piano", "piano", 0.0, reverb=0.32)
    tune = gentle_melody(arr, piano, 52, 62, up=tuple(range(len(arr.verses))), harmony=False, intro=False,
                         octaves=True)
    free_intro(arr, piano, 44)
    ballad_hand(arr, piano, arr.verses[0], arr.end, 38, avoid=tune)
    pedal_by_chord(arr, piano, 0, arr.end)
    gentle_end(arr, piano, tune, 50)


def arrange_pulse(arr: Arrangement) -> None:
    piano = arr.part("piano", "piano", "piano", 0.0, reverb=0.32)
    tune = gentle_melody(arr, piano, 54, 64, up=tuple(range(len(arr.verses))), harmony=False, intro=False,
                         octaves=True)
    free_intro(arr, piano, 44)
    pedal_by_chord(arr, piano, 0, arr.verses[0])  # the rolled chords ring; the pulse is played without pedal
    pulse(arr, piano, arr.verses[0], arr.end, 34, avoid=tune)
    gentle_end(arr, piano, tune, 50)


def arrange_bells(arr: Arrangement) -> None:
    vibes = arr.part("vibes", "vibes", "melody", 0.0, reverb=0.4)
    chimes = arr.part("chimes", "chimes", "bells", 0.1, reverb=0.4)
    glock = arr.part("glock", "glock", "sparkle", 0.15, reverb=0.45)
    for tick, note, length, verse, position in arr.melody():
        high = note + (0 if verse < 0 else 12)  # where bells sing (the intro is an octave up already)
        lift, at = shape(position), tick + arr.jitter(4)
        vibes.add(at, high, (48 if verse < 0 else 54 if verse < arr.last else 58) + 8 * lift, length)
        chimes.add(at, high, 54 + 8 * lift, length)
        if verse >= 0 and length >= arr.beat:  # a glint on the longer notes, two octaves over the tune
            glock.add(at, high, 36 + 6 * lift, length)
    harp = arr.part("harp", "harp", "harp", -0.25, reverb=0.35)
    flowing_bass(arr, harp, 0, arr.verses[0], 48)
    flowing_bass(arr, harp, arr.verses[0], arr.verses[-1], 54)
    flowing_bass(arr, harp, arr.verses[-1], arr.end, 50)
    gliss(arr, harp, arr.verses[-1] - arr.beat, arr.beat, arr.chord_at(arr.verses[-1] - arr.beat), 55, 84, 46)
    strings(arr, arr.verses[0], arr.verses[-1], 38, roles=("bed", "bed"))
    strings(arr, arr.verses[-1], arr.end + 2 * arr.bar, 46, roles=("bed", "bed"))
    for name in ("cellos", "violas"):
        breathe(arr, arr.parts[name], 84, 112, start=arr.verses[0])
    tubular = arr.part("tubular", "tubular", "toll", 0.2, reverb=0.45)
    for tick in (0, *arr.verses, arr.end):  # a soft toll of the keynote at the start, each verse and the last chord
        tubular.add(tick + arr.jitter(4), bass_note(arr.chord_at(arr.end)) + 24, 46, 2 * arr.bar)
    tonic = arr.chord_at(arr.end)
    held = held_keys(chimes.notes, arr.end + 100)
    for i, note in enumerate(chord_notes(tonic, 72, 84)):  # the end: a soft chord on the hand chimes
        if note not in held:
            chimes.add(arr.end + i * 60, note, 50, 2 * arr.bar)
    harp.add(arr.end, bass_note(tonic), 56, 2 * arr.bar)
    gliss(arr, harp, arr.end + arr.beat, 2 * arr.beat, tonic, 60, 96, 40)


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
    harp = arr.part("harp", "harp", "harp", -0.3, reverb=0.35)
    flowing_bass(arr, harp, 0, arr.verses[0], 48, octave=12)
    flowing_bass(arr, harp, arr.verses[0], arr.verses[-1], 52)
    flowing_bass(arr, harp, arr.verses[-1], arr.end, 44, octave=12)
    gliss(arr, harp, arr.verses[-1] - arr.beat, arr.beat, arr.chord_at(arr.verses[-1] - arr.beat), 55, 86, 48)
    strings(arr, 0, arr.verses[-1], 40)
    strings(arr, arr.verses[-1], arr.end + 2 * arr.bar, 54)
    pizz = arr.part("basses-pizz", "basses-pizz", "low", 0.45, reverb=0.3)
    for tick, _, chord in arr.chord_spans(arr.verses[0], arr.verses[-1]):
        if tick % arr.bar == 0:  # plucked on the downbeats of the first verse
            pizz.add(tick + arr.jitter(4), low_bass(chord), 54, arr.beat)
    basses = arr.part("basses", "basses", "low", 0.45, reverb=0.35)
    for tick, length, chord in arr.chord_spans(arr.verses[-1], arr.end + 2 * arr.bar):
        basses.add(tick + arr.jitter(6), low_bass(chord), 60, length + 20, tie=True)
    horns = arr.part("horns", "horns", "pad", 0.2, reverb=0.4)
    middle = arr.verses[-1] + arr.verse // 2
    for tick, length, chord in arr.chord_spans(middle, arr.end + 2 * arr.bar):
        horns.voicing = voice_lead(horns.voicing, chord, 53, 65)
        for note in horns.voicing:
            horns.add(tick + arr.jitter(6), note, 40, length + 20, tie=True)
    flute_descant = arr.part("descant", "flute", "descant", 0.15, reverb=0.4)
    descant(arr, flute_descant, arr.verses[-1] + arr.phrase, arr.end, 50)
    timpani = arr.part("timpani", "timpani", "drum", 0.0, reverb=0.4)
    timpani.add(arr.end, bass_note(arr.chord_at(arr.end)) + 12, 46, 2 * arr.bar)  # a soft roll under the last chord
    if arr.song.lively:  # a sleigh ride for a lively tune: one shake a bar in the last verse
        sleigh = arr.part("sleigh", "sleigh", "drum", 0.4, reverb=0.25)
        for tick in range(arr.verses[-1], arr.end, arr.bar):
            sleigh.add(tick + arr.jitter(6), 60, 46, arr.beat)
    tonic = arr.chord_at(arr.end)
    harp.add(arr.end, bass_note(tonic), 58, 2 * arr.bar)
    gliss(arr, harp, arr.end + arr.beat, 2 * arr.beat, tonic, 60, 96, 42)
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
    repeat_short: bool = False  # play a short tune (under 40 s at its own tempo) three times
    noise_db: float | None = None  # a hush of pink noise under the music, this far under the melody
    verses: int | None = None  # this many verses, whatever the tune's length
    piano_tone: dict | None = None  # changes to the piano part's tone (tests)
    piano_reverb: float | None = None  # the piano part's reverb send instead of its own (tests)
    bpm: float | None = None  # this tempo, when slower than the carol's own (else tempo)
    free_intro: bool = False  # open with the chords alone, in free time
    master: dict = field(default_factory=lambda: dict(MASTER))  # how strongly master.py works on it


# The master's steps (master.py), each from 0 (off) to 1: the piano styles go
# all the way toward the reference pianos; felt keeps its dark tone; bells and
# orchestra keep their own highs (no air: bells sound bright enough) and are
# moved toward the pianos' tone only half way.
MASTER = {"tone": 1.0, "air": 1.0, "width": 1.0, "level": 1.0}
FELT_MASTER = {"tone": 0.0, "air": 0.0, "width": 1.0, "level": 1.0}
BAND_MASTER = {"tone": 0.5, "air": 0.0, "width": 1.0, "level": 1.0}


STYLES = {
    "piano": Style(arrange_piano),
    "salamander": Style(lambda arr: arrange_piano(arr, "salamander")),
    "chill": Style(arrange_chill, tempo=0.8, breath=0.88, repeat_short=True),
    "lullaby": Style(arrange_lullaby, tempo=0.7, breath=0.85, repeat_short=True),
    "flowing": Style(arrange_flowing, tempo=0.85, breath=0.9, repeat_short=True),
    "hymn": Style(arrange_hymn, tempo=0.75, breath=0.85, repeat_short=True),
    "piano-strings": Style(arrange_piano_strings, tempo=0.8, breath=0.88, hall=2.4, repeat_short=True),
    "felt": Style(arrange_felt, tempo=0.8, breath=0.9, repeat_short=True, master=FELT_MASTER),
    "felt-noise": Style(arrange_felt, tempo=0.8, breath=0.9, repeat_short=True, noise_db=-22, master=FELT_MASTER),
    "ballad": Style(arrange_ballad, bpm=74, breath=0.86, hall=2.8, repeat_short=True, free_intro=True),
    "pulse": Style(arrange_pulse, bpm=88, breath=0.88, hall=2.8, repeat_short=True, free_intro=True),
    "bells": Style(arrange_bells, hall=2.6, master=BAND_MASTER),
    "orchestra": Style(arrange_orchestra, hall=2.4, master=BAND_MASTER),
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


def write_part(part: Part, tempos: list, path: Path, meter: tuple = (3, 2)) -> int:
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
    beats, eighths = meter
    track.append(mido.MetaMessage("time_signature", numerator=beats * (1 if eighths == 2 else 3),
                                  denominator=4 if eighths == 2 else 8))
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
    parser.add_argument("--styles", nargs="+", default=[s for s in STYLES if s != "salamander"],
                        choices=list(STYLES))
    args = parser.parse_args()
    for name in args.songs:
        for style_name in args.styles:
            song, style = SONGS[name], STYLES[style_name]
            verses = style.verses or song.verses or (3 if style.repeat_short and song.seconds() < 40 else 2)
            tempo = min(1.0, style.bpm / song.bpm) if style.bpm else style.tempo
            arr = Arrangement(song, verses, tempo, style.breath, free_intro=style.free_intro)
            style.arrange(arr)
            if style.piano_tone:
                arr.parts["piano"].tone.update(style.piano_tone)
            if style.piano_reverb is not None:
                arr.parts["piano"].reverb = style.piano_reverb
            folder = args.out / f"{name}-{style_name}"
            folder.mkdir(parents=True, exist_ok=True)
            sheet, untangled = [], 0
            for part_name, part in arr.parts.items():
                untangled += write_part(part, arr.tempos, folder / f"{part_name}.mid", arr.meter)
                library, sfz = INSTRUMENTS[part.instrument]
                sheet.append({"part": part_name, "library": library, "sfz": sfz, "role": part.role,
                              "gain_db": ROLES[part.role], "pan": part.pan, "reverb": part.reverb,
                              "tone": part.tone, "notes": len(part.notes)})
            mix = {"hall": {"rt60": style.hall}, "parts": sheet, "master": style.master}
            if style.noise_db is not None:
                mix["noise"] = {"db": style.noise_db}
            (folder / "mix.json").write_text(json.dumps(mix, indent=2))
            print(f"{folder.name}: {arr.bpm:.0f} bpm, {len(arr.verses)} verses, {len(sheet)} parts "
                  f"({', '.join(p['part'] for p in sheet)}), {arr.seconds(0, arr.end + 2 * arr.bar):.0f} s, "
                  f"{untangled} repeated notes untangled")


if __name__ == "__main__":
    main()
