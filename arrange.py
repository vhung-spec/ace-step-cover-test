"""Arranges the test's carols for real instrument samples, without any AI
model: one MIDI file per instrument, in several styles, plus mix.json (the
hall, and each part's instrument, role, stereo position and tone) for
render_samples.py:

    python arrange.py out/sampled [--songs wish silent-night first-noel ...] [--styles ballad pulse ...]
        [--pianos grand piano knight yamaha ep]

pulse, after the first of the user's two reference recordings, and the gentle
piano styles are played on VCSL's Yamaha upright, softer and closer (heard
against the Steinway B grand with its highs open, "grand", the user preferred
it); ballad, after the second, on a Rhodes electric piano (the user: "quite
close" to it); piano on the Steinway with its highs cut. --pianos plays them
on others to compare (the Steinway: piano or grand, the Knight upright:
knight, the Yamaha: yamaha, the Rhodes: ep; such pieces' names end in the
piano's name).

The carols are public-domain melodies and chords: We Wish You a Merry
Christmas and Silent Night (make_source.py), The First Noel, Joy to the
World, O Holy Night, Jingle Bells and Deck the Halls (carols.py), in 3/4,
2/4, 4/4 and 12/8, each in its own key. Every style but pulse plays an
intro (the last phrase, an octave up), then the verses (the last one fuller)
and a held last chord, slowing down over the last two bars. The parts are written from the
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
- ballad and pulse, after the user's two reference recordings of slow pop
  Christmas piano: a grand played fully, not hushed; a deep bass (A1 to G#2)
  struck with every chord, now and then on its third as a bass line walks;
  the middle of the keyboard moving in eighths under the pedal; the tune an
  octave up, in a middle verse with a third or sixth under its longer notes,
  in the last doubled an octave down; a few tones rising over a phrase's last
  held note; the last chord rolled from the deep bass; all in a small room
  (0.8 s) with little of it, as the references sound close by (the user:
  "very close to the ear"; in a 2.8 s hall ours sounded "as if in a big
  room"):
  - ballad (about 72 bpm): the tune's last phrase as the intro; the bass
    walking the chord a beat at a time; the middle hand two tones an eighth,
    low and high by turns, up and down the chord from C3-B3; a faint synth pad
    under it all (instruments/pad.sfz, sfizz's own oscillators), as the second
    reference lays one; the carol's chords coloured as that reference's are
    (reharmonize: vi7 for some tonic bars, ii7 for some subdominant ones, ii7
    opening a dominant bar, where the tune allows); played on a Rhodes: one
    note in ten of that reference carries a Rhodes tine's lone partial, 7.2
    times its pitch (the Yamaha's partials fall smoothly), and on the Rhodes
    the tagger hears the piece as it hears the reference, barely as a piano
    (layered 6 or 12 dB under the Yamaha instead, the Rhodes changed little);
    the Rhodes, recorded straight from the instrument and nearly mono, widened
    by a stereo chorus, as the reference is wide from each note's attack
    (ballad-plain: without it; the user keeps both);
  - pulse (about 88 bpm): straight into the tune, its pickup alone (the user
    wanted its 10 s intro gone: the tune's last chords in free time, rolled
    from the deep bass to a slow top line, which pulse-clear keeps); a
    heartbeat of eighths, each chord's root and fifth (the octave on the
    beats), the bass struck
    as each chord comes and its fifth halfway through the bar; and the first
    reference's other instruments: in the first verse a glockenspiel softly
    doubling the tune (pulse-hall-plain: the piano alone), then a flute
    singing it (with a gentle vibrato) while the piano follows softly, then a
    vibraphone doubling it over a harp and soft strings; the user keeps four
    versions of it: pulse (the small room), pulse-near (a 1.2 s room, sends
    at 0.6 times), pulse-hall and pulse-hall-plain (the 2.8 s hall);
  - ballad-clear, pulse-clear (on the Steinway grand, in the 2.8 s hall): the
    same, each beat's notes blooming and fading as the references' do (the
    pedal taken again on every beat, the bass held a beat, the middle hand
    lifted after its eighth), and brighter (the piano's highs raised from
    6 kHz);
- bells: the vibraphone with hand chimes an octave up, where bells sing, a
  glockenspiel glinting on the longer notes (it sounds an octave above its
  keys), a harp, a soft string bed, a tubular bell tolling each verse in;
- orchestra: flute, then violins on the melody, a flute descant over the last
  verse, on a harp and a string pad, basses plucked then bowed, horns from the
  middle of the last verse, a soft timpani roll under the last chord;
- the church styles, a carol as a church sings it: the hymnal's four voices
  (chorale.py: soprano the tune, alto, tenor and bass, a chord on each beat,
  its bass line moving through inversions) on a pipe organ (VCSL's, sampled
  by Simon Dalzell of Ivy Audio: the quiet manual, its pedal for the bass),
  in a cathedral's long hall (4.5 s), the voices breathing at each phrase's
  end, an Amen (IV, I) after the last verse, a bell tolling the piece in and
  out (church-organ: a tubular bell; the others GeneralUser GS's bell tower):
  - church-organ: the organ alone, the last verse a little fuller (its loud
    manual and pedal joining softly); church-organ-plain: the same on the
    carol's own chords, to hear what the hymn harmony brings;
  - church-choir: the organ gives out the tune (the intro and the first
    verse), then a choir sings the four voices (GeneralUser GS's Concert
    Choir, played by FluidSynth), the organ softly under it;
  - church-festive: church-choir, its last verse with brass doubling the
    voices (trumpets, trombones, tuba), the loud organ, and a timpani roll
    under the Amen;
  - chapel: a small Renaissance organ and a choir singing "ooh", softly, in a
    smaller hall (2.6 s), no bells;
  - church-organ-near, church-organ-plain-near, church-choir-near,
    church-festive-near, chapel-near: the same closer by, in the small room
    of ballad and pulse (0.8 s, sends at 0.45 times), as the user asked;
  - easier to listen to, on a phone too, as the user asked (the organ's held
    voices sat low and muffled there): church-piano-near, the hymn on the
    gentle Yamaha upright, its tune on top, strings from the second verse, a
    choir humming far under the last; church-organ-clear-near, the organ
    with its tune alone on the bright loud manual, the voices under it
    lighter;
  - the clear organ joined by other instruments and by voices humming, as the
    user asked: church-organ-ensemble-near, a harp from the first verse, a
    choir humming ("ooh") alto and tenor from the second, in the last verse
    the tune hummed softly under the organ's, violas and a flute descant;
    church-organ-hum-near, the voices forward: the choir humming alto and
    tenor from the first verse and the tune itself in the second, the harp
    from the second verse, violas in the last;
  - that organ softer and more relaxing, as the user asked ("too heavy"):
    church-organ-soft-near, church-organ-ensemble-near on the quiet manual's
    stopped flute and the quiet pedal; church-organ-small-near, on the small
    Renaissance organ (its 8' and 4' flutes for the tune, the 8' under it);
    both swelling and ebbing with each phrase, a little slower.
- played as a person plays them, as the user asked ("too even"): felt-4k-human
  and church-organ-soft-human-near, felt-4k and church-organ-soft-near with
  their accompaniment breathing with each phrase (calm in its first bar,
  moving in the middle, its chord laid down and left to ring in the last) and
  a player's shaping (perform): the tempo swinging over each phrase, the tune
  swelling to its peak and falling away, its higher and longer notes a little
  louder, less random jitter; and so the earlier styles the user keeps:
  pulse-human, ballad-human (their middle hand and harp breathing),
  orchestra-gentle-human (its harp breathing), church-piano-human-near and
  church-organ-small-human-near;
- simulated instruments in place of recorded ones, as the user asked to try,
  made by sfizz's own oscillators (instruments/*.sfz: a soft pipe organ and
  its pedal, a tine electric piano, a felt piano, a church bell):
  church-organ-synth-human-near, ballad-synth-human, felt-synth-human.
Sustained parts hold the tones two chords share, move their other tones to
the nearest tone of the next chord, and swell with each phrase (expression,
CC11). Instruments come from two CC0 sample libraries: VS Chamber Orchestra 2
Community Edition ("vsco", SFZ branch) and the Versilian Community Sample
Library ("vcsl", sfz branch); the Rhodes from jRhodes3d by Jeff Learman
("jrhodes": free to use in music; its samples, CC BY-NC 4.0 to pass on, are
fetched when rendering and never kept here); the choir and the bell tower
from the GeneralUser GS soundfont by S. Christian Collins ("generaluser":
free for any music making, commercial too), played by FluidSynth.
"""

import argparse
import bisect
import dataclasses
import itertools
import json
import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import mido

import carols
import chorale
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
        kind = name[1:].partition("/")[0]  # a bass after a slash (G/B) leaves the chord as it is
        if kind[:1] in ("#", "b"):
            root, kind = (root + (1 if kind[0] == "#" else -1)) % 12, kind[1:]
        self[name] = (root, KINDS[kind])
        return self[name]


CHORDS = ChordBook()

# Sample libraries: (library, SFZ file in it). The softer sample layers end at
# velocity 62 (strings, flute), 65 (piano), 83 (vibraphone, glockenspiel), 100
# (harp) and 41 (horns, the two softest); hand chimes and sleigh bells have one;
# the Rhodes has five, crossfaded, the softest to 60.
INSTRUMENTS = {
    "piano": ("vcsl", "Chordophones/Zithers/Grand Piano, Steinway B.sfz"),
    "grand": ("vcsl", "Chordophones/Zithers/Grand Piano, Steinway B.sfz"),  # the same, its highs open
    "salamander": ("salamander", "Salamander Grand Piano V3.sfz"),
    "knight": ("vcsl", "Chordophones/Zithers/Upright Piano, Knight.sfz"),  # two softer, closer uprights
    "yamaha": ("vcsl", "Chordophones/Zithers/Upright Piano, Yamaha.sfz"),
    "chimes": ("vcsl", "Idiophones/Struck Idiophones/Hand Chimes.sfz"),
    "vibes": ("vcsl", "Idiophones/Struck Idiophones/Vibraphone - Soft Mallets.sfz"),
    "glock": ("vcsl", "Idiophones/Struck Idiophones/Glockenspiel.sfz"),
    "harp": ("vcsl", "Chordophones/Composite Chordophones/Concert Harp.sfz"),
    "sleigh": ("vcsl", "Idiophones/Struck Idiophones/Sleigh Bells.sfz"),
    "pad": ("local", "pad.sfz"),  # our own synth pad (instruments/pad.sfz), sfizz's oscillators
    "ep": ("jrhodes", "jRhodes3d-st.sfz"),  # a 1977 Rhodes Mark I, a mild chorus in its stereo samples
    "tubular": ("vcsl", "Idiophones/Struck Idiophones/Tubular Bells 1.sfz"),
    "flute": ("vsco", "FluteSusNV.sfz"),  # without vibrato: the vibrato samples wobble on long notes
    "violins": ("vsco", "ViolinEnsSusVib.sfz"),
    "violas": ("vsco", "ViolaEnsSusVib.sfz"),
    "cellos": ("vsco", "CelloEnsSusVib.sfz"),
    "basses": ("vsco", "ContrabassSusVB-Quiet.sfz"),
    "basses-pizz": ("vsco", "ContrabassPizz.sfz"),
    "horns": ("vsco", "FHornSus.sfz"),
    "timpani": ("vsco", "TimpaniRolls.sfz"),
    # the church styles' organs: a church organ's quiet and loud manuals and
    # pedals (samples of about 12 s, from C2), and a small Renaissance organ's
    # 8' stop (samples of about 6 s)
    "organ": ("vcsl", "Aerophones/Edge-blown Aerophones/Pipe Organ - Quiet.sfz"),
    "organ-loud": ("vcsl", "Aerophones/Edge-blown Aerophones/Pipe Organ - Loud.sfz"),
    "pedal": ("vcsl", "Aerophones/Edge-blown Aerophones/Pipe Organ - Quiet Pedal.sfz"),
    "pedal-loud": ("vcsl", "Aerophones/Edge-blown Aerophones/Pipe Organ - Loud Pedal.sfz"),
    "chamber-organ": ("vcsl", "Aerophones/Edge-blown Aerophones/Renaissance Organ - 8'.sfz"),
    "chamber-organ-48": ("vcsl", "Aerophones/Edge-blown Aerophones/Renaissance Organ - 4'+8'.sfz"),  # 8' and 4' together
    "trumpets": ("vsco", "TrumpetSus.sfz"),
    "trombones": ("vsco", "TromboneSus.sfz"),
    "tuba": ("vsco", "TubaSus.sfz"),
    # GeneralUser GS presets (bank:program), played by FluidSynth
    "choir": ("generaluser", "GeneralUser-GS.sf2#0:52"),  # Concert Choir, singing "ah"
    "oohs": ("generaluser", "GeneralUser-GS.sf2#0:53"),  # Voice Oohs
    "bell-tower": ("generaluser", "GeneralUser-GS.sf2#11:14"),  # Bell Tower
    # simulated instruments, as the user asked to try: made by sfizz's own
    # oscillators (instruments/*.sfz), no recording and no licence
    "organ-synth": ("local", "organ-synth.sfz"),  # a soft pipe organ: stopped 8' flute and 4' flute
    "pedal-synth": ("local", "pedal-synth.sfz"),  # its pedal: an 8' stopped flute
    "ep-synth": ("local", "ep-synth.sfz"),  # a tine electric piano
    "felt-synth": ("local", "felt-synth.sfz"),  # a soft piano, as felt hammers sound
    "bell-synth": ("local", "bell-synth.sfz"),  # a church bell
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
    # fetch_samples.py now fades each Steinway sample's highs out once its note
    # has died into that hiss (and leaves out the top of a soft note, hiss
    # alone): ballad and pulse play it with its highs open, as bright as the
    # reference recordings' grand.
    "grand": {"release_db": -60},
    # The Knight upright's soft samples hiss a little (69-75 dB under the note),
    # so it is treated as the Steinway; its pedal's thumps are left out. The
    # Yamaha upright's soft samples are dark and clean (hiss 107-115 dB under
    # the note), but some were recorded with their channels in opposite
    # polarity (fetch_samples.py turns one over).
    "knight": {"release_db": -60, "pedal_noise": False, "lowpass": 6000, "dehiss": True},
    "yamaha": {"release_db": -60},
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
    # The Rhodes' samples are clean (above 4 kHz 125 dB under the note); its
    # harder layers bark, so its highs are eased from 7 kHz. It was recorded
    # straight from the instrument, nearly mono, while the references are wide
    # from each note's attack: its samples' own mild chorus is widened (its mod
    # wheel: 0.5 as recorded, 1 three times), and a stereo chorus is added.
    "ep": {"highpass": 60, "lowpass": 7000, "set_cc": {"1": 0.75}, "chorus": 0.7},
    "tubular": {"lowpass": 4000, "lowpass_order": 4, "width": 0.5, "dehiss": True},
    "flute": {"lowpass": 8000, "shelf": [6000, -2], "width": 0.5},
    "violins": {"lowpass": 6500, "lowpass_order": 4, "shelf": [5000, -2], "width": 0.8, "dehiss": True},
    "violas": {"highpass": 80, "lowpass": 6000, "lowpass_order": 4, "shelf": [4000, -2], "width": 0.8, "dehiss": True},
    "cellos": {"highpass": 40, "lowpass": 5000, "lowpass_order": 4, "shelf": [3500, -2], "width": 0.8, "dehiss": True},
    "basses": {"highpass": 30, "lowpass": 4000, "lowpass_order": 4, "width": 0.7},
    "basses-pizz": {"highpass": 30, "lowpass": 5000, "width": 0.7},
    "horns": {"highpass": 60, "lowpass": 3000, "lowpass_order": 4, "width": 0.7},
    "timpani": {"highpass": 35, "width": 0.7},
    # The organs' manual samples were recorded by two microphones set apart:
    # for a pipe's nearly pure tone the two sides arrive a millisecond or two
    # apart, in phase for one note and out of phase for the next (summed, some
    # notes lost 10 dB and more, and the organ's lows ran out of phase in the
    # mix). Only the left microphone is used; the hall gives the width. The
    # pedals' long waves stay in phase, so they keep both sides.
    "organ": {"channel": "left"},
    "organ-loud": {"channel": "left"},
    "chamber-organ": {"channel": "left"},
    "chamber-organ-48": {"channel": "left"},
    "pedal": {"width": 0.6},
    "pedal-loud": {"width": 0.6},
    "trumpets": {"highpass": 80, "lowpass": 6000, "lowpass_order": 4, "width": 0.7, "dehiss": True},
    "trombones": {"highpass": 50, "lowpass": 4500, "lowpass_order": 4, "width": 0.7, "dehiss": True},
    "tuba": {"highpass": 30, "lowpass": 3000, "lowpass_order": 4, "width": 0.7},
    # the simulated instruments are mono and clean (no hiss): the electric piano
    # gets the sampled Rhodes's stereo chorus, a little less
    "ep-synth": {"highpass": 60, "chorus": 0.6},
    "bell-synth": {"lowpass": 8000},
}
# How loud each kind of part sits against the melody (dB of its loudness when playing).
ROLES = {"melody": 0.0, "piano": 0.0, "descant": -9.0, "harp": -4.0, "pad": -10.0, "bass": -8.0, "shimmer": -12.0,
         "arp": -7.0, "jingle": -18.0, "haze": -20.0,
         "bells": -8.0, "bed": -13.0, "low": -12.0, "toll": -14.0, "sparkle": -16.0, "drum": -17.0,
         "voices": -2.0, "hum": -6.0}


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


PITCH_NAMES = ("C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B")


def reharmonize(song: "Song") -> "Song":
    """The carol's chords coloured as the slow pop ballads colour them (the
    second reference moves ii-V-I-vi, about two chords in five minor; the
    carols' own, Silent Night's all major): in a run of bars on the tonic every
    second becomes the sixth's minor seventh (vi7 holds all the tonic's tones:
    C -> Am7); in a run on the subdominant every second becomes the second's
    minor seventh (ii7: F -> Dm7); a bar on the dominant after one that is not
    ii7 opens with ii7 for its first half (its first beat in 3/4), each only
    where the tune's notes there (those on a beat, or a beat long) are its
    tones. The first bar and the last two stay as they are."""
    tonic = CHORDS[song.chords[0][0]][0]
    vi7, ii7 = PITCH_NAMES[(tonic + 9) % 12] + "m7", PITCH_NAMES[(tonic + 2) % 12] + "m7"
    bar_eighths = song.beats * song.beat_eighths
    tune, at = [], -song.pickup
    for note, eighths in song.melody:
        if note is not None:
            tune.append((at, note % 12, eighths))
        at += eighths

    def fits(name: str, start: float, end: float) -> bool:
        tones = {(CHORDS[name][0] + i) % 12 for i in CHORDS[name][1]}
        beats = [start + k * song.beat_eighths for k in range(round((end - start) / song.beat_eighths))]
        for begin, pc, length in tune:
            on_beat = any(begin <= b < begin + length for b in beats)
            if (on_beat or (start <= begin < end and length >= song.beat_eighths)) and pc not in tones:
                return False
        return True

    def role(name: str) -> str:
        root, intervals = CHORDS[name]
        if intervals[1] != 4:
            return "minor"
        return {0: "I", 5: "IV", 7: "V"}.get((root - tonic) % 12, "other")

    chords, run = [list(bar) for bar in song.chords], {"I": 0, "IV": 0}
    for b in range(1, len(chords) - 2):
        bar = chords[b]
        kind = role(bar[0]) if len(set(bar)) == 1 else "moving"
        for name in run:
            run[name] = run[name] + 1 if kind == name else 0
        start = b * bar_eighths
        if kind == "I" and run["I"] % 2 == 0 and fits(vi7, start, start + bar_eighths):
            chords[b] = [vi7] * song.beats
        elif kind == "IV" and run["IV"] % 2 == 0 and fits(ii7, start, start + bar_eighths):
            chords[b] = [ii7] * song.beats
        elif kind == "V" and chords[b - 1][-1] != ii7:
            half = max(1, song.beats // 2)
            if fits(ii7, start, start + half * song.beat_eighths):
                chords[b] = [ii7] * half + bar[half:]
    return dataclasses.replace(song, chords=chords)


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
        self.notes, self.pedal, self.expression, self.voicing, self.bends = [], [], [], [], []
        self.latest = {}  # key: index of its latest note
        self.leading = 0  # its first notes that are the tune, where the tune is not found by its keys (perform)

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
                 free_intro: bool = False, piano: str = "piano", intro: bool = True):
        self.song, self.rng, self.piano = song, random.Random(seed), piano  # piano: the instrument playing piano
        self.bpm = song.bpm * tempo
        self.beat = song.beat_eighths * EIGHTH  # a quarter note, or a dotted quarter in 6/8 and 12/8
        self.bar = song.beats * self.beat
        self.meter = (song.beats, song.beat_eighths)
        tonic = CHORDS[song.chords[0][0]][0]
        self.scale = {(tonic + step) % 12 for step in (0, 2, 4, 5, 7, 9, 11)}  # the carols are in major keys
        # A free intro (chords alone, in rubato) runs over the tune's last bars,
        # twice as many while that is under 8 s. With no intro the first verse
        # starts at once, its pickup (if any) alone before the first downbeat.
        self.free_intro, self.intro_bars = free_intro, song.intro_bars if intro else 0
        while free_intro and intro and 2 * self.intro_bars <= len(song.chords) and self.seconds_at(self.intro_bars) < 8:
            self.intro_bars *= 2
        self.intro = self.intro_bars * self.bar if intro else round(song.pickup * EIGHTH)
        self.verse = len(song.chords) * self.bar
        self.phrase = 4 * self.bar
        self.verses = [self.intro + k * self.verse for k in range(verses)]  # each verse's first downbeat
        self.last = verses - 1  # the last verse's number
        self.end = self.verses[-1] + self.verse  # the last note's bar ends here
        self.tempos = self.tempo_map(breath)
        self.parts: dict[str, Part] = {}
        self.loose = 1.0  # the random timing (jitter) times this: less for a player shaping each phrase (perform)
        self.shift = 0  # ticks the piece was moved later for a lead-in (lead_in)

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
        return round(self.rng.randint(-ticks, ticks) * self.loose)

    def chord_at(self, tick: int) -> str:
        """The chord sounding at a tick: the intro uses the tune's last bars, the
        ring-out after the last verse the first chord (the tonic)."""
        bars = self.song.chords
        if tick < self.intro:
            if not self.intro_bars:  # no intro: the first verse's pickup, over its first chord
                return bars[0][0]
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


def breathe(arr: Arrangement, part: Part, low: int, high: int, start: int = 0, fade: int | None = None) -> None:
    """Expression (CC11), an eighth at a time from start: rising to the middle of
    each phrase (the intro is one) and falling at its end, as players breathe
    with the tune; over the last chord it swells a little and dies away (with
    fade, it only dies away, from low down to fade: the chord ends softly)."""
    for tick in range(start, arr.end, EIGHTH):
        if tick < arr.intro:
            begin, length = 0, arr.intro
        else:
            begin, length = arr.intro + (tick - arr.intro) // arr.phrase * arr.phrase, arr.phrase
        part.expression.append((tick, round(low + (high - low) * math.sin(math.pi * (tick - begin) / length))))
    steps = 2 * arr.bar // EIGHTH
    for i in range(steps):
        if fade is None:
            x = 0.25 + 0.75 * i / (steps - 1)
            part.expression.append((arr.end + i * EIGHTH, round(low + (high - low) * math.sin(math.pi * x))))
        else:
            part.expression.append((arr.end + i * EIGHTH, round(low + (fade - low) * (i / (steps - 1)) ** 0.7)))


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


def descant(arr: Arrangement, part: Part, start: int, end: int, velocity: int, ceiling: int = 86) -> None:
    """A slow line over the tune: one chord tone per chord, at least a minor third
    above the melody sounding with it, moving to the nearest tone, none over ceiling."""
    tune = [(t, n, l) for t, n, l, verse, _ in arr.melody() if verse == arr.last]
    previous = None
    for tick, length, chord in arr.chord_spans(start, end):
        top = max((n for t, n, l in tune if t < tick + length and tick < t + l), default=67)
        options = chord_notes(chord, max(72, top + 3), ceiling)
        if not options:
            previous = None
            continue
        note = min(options, key=lambda n: abs(n - (previous or 76)))
        part.add(tick + arr.jitter(6), note, velocity, length + 20, tie=True)
        previous = note


def held_keys(notes: list, tick: int) -> set:
    return {n for t, n, _, l in notes if t <= tick < t + l}


def arrange_piano(arr: Arrangement, instrument: str | None = None) -> None:
    piano = arr.part("piano", instrument or arr.piano, "piano", 0.0, reverb=0.25)
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
                  harmony: bool = True, intro: bool = True, octaves: bool = False, swell: float = 10) -> list:
    """The tune for the gentle piano styles, a little behind the beat
    (unhurried), growing from soft in the first verse to loud in the last, each
    verse rising to its middle (by swell); the verses in up an octave higher, light as a
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
            velocity = soft + (loud - soft) * verse / max(1, arr.last) + swell * shape(position)
        note += 12 if verse in up else 0
        at = tick + late + arr.jitter(6)
        piano.add(at, note, velocity + arr.rng.randint(-2, 2), length - 10)
        if octaves and verse == arr.last and length >= arr.beat:
            piano.add(at - 12, note - 12, velocity - 20, length - 10)
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
    return arr.part("piano", arr.piano, "piano", 0.0, reverb=0.25)


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


def arrange_felt(arr: Arrangement, bright: bool = False, breathing: bool = False) -> None:
    """With bright, the tune is struck a little harder, into the Yamaha's
    brighter layer of samples (from velocity 66) at the height of each phrase,
    the left hand and the last chord a little harder too. With breathing, the
    left hand breathes with each phrase (breathing_hand) instead of rolling
    the same eighths through every bar."""
    piano = gentle_piano(arr)
    piano.tone["lowpass"] = 900  # the dark, round tone of felt hammers
    tune = gentle_melody(arr, piano, *((64, 66) if bright else (50, 52)))
    if breathing:
        breathing_hand(arr, piano, 0, arr.end, 36, tune)
    else:
        rolling(arr, piano, 0, arr.end, 42 if bright else 36, avoid=tune)
    pedal_by_chord(arr, piano, 0, arr.end)
    gentle_end(arr, piano, tune, 56 if bright else 46)


# The user found the pieces "too even" ("đều quá"), lacking a player's ease
# and softness: the left hand rolled the same eighths through every bar, the
# notes kept to the grid but for random jitter, and the tempo moved only at
# phrase ends. A player breathes with each phrase: the accompaniment and the
# tempo below follow it (phrase_spans: the phrases as the tempo map breathes).
def phrase_spans(arr: Arrangement) -> list:
    """(start, end) of every phrase, in ticks before any lead-in: the intro, as
    one, then each verse's phrases, each ending where the tempo map breathes
    (the song's breaths, or every fourth bar), the last at the verse's end."""
    spans = [(0, arr.intro)] if arr.intro_bars else []
    ends = sorted({bar + 1 for bar in arr.song.breaths or range(3, len(arr.song.chords), 4)}
                  | {len(arr.song.chords)})
    for downbeat in arr.verses:
        start = downbeat
        for bar in ends:
            end = downbeat + bar * arr.bar
            if end > start:
                spans.append((start, end))
                start = end
    return spans


def arch(x: float, peak: float = 0.6) -> float:
    """A phrase's arch (the KTH performance rules' phrase arch): 0 at its ends,
    1 at its peak, a little after its middle."""
    return math.sin(math.pi * min(1.0, max(0.0, x)) ** (math.log(0.5) / math.log(peak)))


def rolled_chords(arr: Arrangement, part: Part, start: int, end: int, velocity: int, avoid: list = (),
                  octave: int = 0, spread: int = 24) -> None:
    """Each chord between two ticks laid down once, its open tones (root,
    fifth, tenth, top) rolled slowly up from the bass, spread ticks apart,
    and left to ring to its end."""
    for tick, length, chord in arr.chord_spans(start, end):
        tones = ladder(chord, bass_note(chord) + octave)
        for i, name in enumerate(("root", "fifth", "tenth", "top")):
            at = tick + i * spread + arr.jitter(3)
            if not busy(avoid, tones[name], at, tick + length - at):
                part.add(at, tones[name], velocity - 2 * i + arr.rng.randint(-2, 2), tick + length - at)


def breathing_hand(arr: Arrangement, part: Part, start: int, end: int, velocity: int, avoid: list = (),
                   moving: Callable = None, calm: Callable | None = rocking, octave: int = 0) -> None:
    """An accompaniment breathing with each phrase: its first bar calm (calm:
    a tone a beat rising through the bar; None, moving as the others), its
    middle bars moving (moving: rolling eighths, up the chord and back), its
    last bar its chord laid down, rolled slowly from the bass (octave: so many
    semitones up), and left to ring while the tune ends the phrase. Bars
    outside every phrase (a lone pickup) are left out."""
    moving = moving or rolling
    for phrase_start, phrase_end in phrase_spans(arr):
        bars = (phrase_end - phrase_start) // arr.bar
        for k in range(bars):
            bar = phrase_start + k * arr.bar
            if bar < start or bar >= end:
                continue
            bar_end = min(bar + arr.bar, end)
            if k == bars - 1 and bars > 1:
                rolled_chords(arr, part, bar, bar_end, velocity - 2, avoid, octave=octave)
            elif k == 0 and calm:
                calm(arr, part, bar, bar_end, velocity, avoid)
            else:
                moving(arr, part, bar, bar_end, velocity, avoid=avoid)


def breathing_harp(arr: Arrangement, harp: Part, start: int, end: int, velocity: int, octave: int = 0) -> None:
    """A harp breaking the chords in eighths (flowing_bass) between two ticks,
    breathing with each phrase: on its last bar it lays the chord down,
    rolled slowly, and lets it ring."""
    for phrase_start, phrase_end in phrase_spans(arr):
        last_bar = phrase_end - arr.bar
        if phrase_end > start and phrase_start < end:
            flowing_bass(arr, harp, max(phrase_start, start), min(last_bar, end), velocity, octave=octave)
            rolled_chords(arr, harp, max(last_bar, start), min(phrase_end, end), velocity - 2, octave=octave,
                          spread=30)


# ballad and pulse follow the user's two reference recordings, slow pop piano
# carols (measured for their sound and manner only; nothing of theirs is
# copied). Against them the earlier, hushed versions on the Yamaha upright
# lacked some 20 dB of deep bass (63 Hz) and 25-30 dB of brightness (4-8 kHz),
# and their left hand was thin: the references strike a deep bass with every
# chord (1-2 a second, as loud as the rest) and keep the middle of the
# keyboard moving in eighths, two or three tones at a time, under the pedal
# (6-7 notes a second), the tune an octave up over it. Their harmony is the
# carol's own, plain (an added ninth in 4-11 % of beats), the bass now and then
# on a chord's third. So both are played on the Steinway grand, fully rather
# than hushed: the tune and the bass from its brighter middle layer.
DEEP = 33  # the deep bass's lowest root, A1: every root falls between A1 and G#2
MIDDLE = 48  # the middle hand's lowest root, C3
BRIGHT = 66  # the Steinway's brighter middle layer of samples starts at this velocity


def tune_floor(tune: list, tick: int, length: int) -> int:
    """The lowest key the tune holds between two ticks (128 when it rests)."""
    return min((n for t, n, _, l in tune if t < tick + length and tick < t + l), default=128)


def walking_bass(chord: str, previous: int | None, downbeat: bool) -> int:
    """A chord's deep bass note: its root, A1 to G#2; but a chord arriving
    within a bar whose third lies a step from the bass before it (and whose
    root does not) puts its third in the bass, as a bass line walks (C, G/B, Am)."""
    root = bass_note(chord, DEEP)
    if downbeat or previous is None:
        return root
    under = DEEP + (CHORDS[chord][0] + third(chord) - DEEP) % 12
    return under if abs(under - previous) <= 2 < abs(root - previous) else root


def deep_bass(arr: Arrangement, part: Part, start: int, end: int, velocity: int, walk: bool = False,
              hold: int | None = None) -> None:
    """The deep bass: as each chord comes, its bass note (walking_bass), struck
    firmly and left to ring (with hold, its key held that long at most); at
    the head of each phrase doubled an octave up. In a bar of one chord, its
    fifth a second time, softer, halfway through it (on the second beat in
    3/4); or, walking, a tone of the chord on every beat after the first: the
    fifth, the octave, the fifth."""
    previous, half = None, {(3, 2): 1, (4, 2): 2, (4, 3): 2}.get(arr.meter)
    held = (lambda length: min(length, hold)) if hold else (lambda length: length)
    for tick, length, chord in arr.chord_spans(start, end):
        downbeat = tick % arr.bar == 0
        note = previous = walking_bass(chord, previous, downbeat)
        at = tick + arr.jitter(4)
        part.add(at, note, velocity - (0 if downbeat else 6) + arr.rng.randint(-2, 2), held(length))
        if tick == start or any(0 <= tick - v < arr.verse and (tick - v) % arr.phrase == 0 for v in arr.verses):
            part.add(at + 6, note + 12, velocity - 8 + arr.rng.randint(-2, 2), held(length))
        if walk:  # from the root, whichever tone the bass took
            for beat, step in zip(range(arr.beat, length, arr.beat), (7, 12, 7)):
                part.add(tick + beat + arr.jitter(4), bass_note(chord, DEEP) + step,
                         velocity - 12 + arr.rng.randint(-2, 2), held(length - beat))
        elif downbeat and half and length == arr.bar:
            part.add(tick + half * arr.beat + arr.jitter(4), note + 7, velocity - 12 + arr.rng.randint(-2, 2),
                     held(length - half * arr.beat))


def under_tune(arr: Arrangement, part: Part, tune: list, tick: int, notes: list, velocity: int, length: int) -> None:
    """Strikes the middle hand's notes at a tick, those at or over the tune (or
    two semitones under it) an octave lower, and none on a key the tune holds."""
    ceiling = tune_floor(tune, tick, length) - 2
    for note in notes:
        while note > ceiling and note - 12 >= MIDDLE:
            note -= 12
        if note <= ceiling and not busy(tune, note, tick, length):
            part.add(tick, note, velocity + arr.rng.randint(-2, 2), length)


# The ballad's middle hand, eighth by eighth: two tones of the chord at a time,
# low and high by turns, rising and falling through it from its root (C3 to B3).
PAIRS = {(3, 2): (("root", "fifth"), ("octave", "tenth"), ("fifth", "octave"), ("tenth", "twelfth"),
                  ("octave", "tenth"), ("fifth", "octave")),
         (4, 2): (("root", "fifth"), ("octave", "tenth"), ("fifth", "octave"), ("tenth", "twelfth"),
                  ("root", "fifth"), ("octave", "tenth"), ("fifth", "octave"), ("tenth", "octave")),
         (2, 2): (("root", "fifth"), ("octave", "tenth"), ("fifth", "octave"), ("tenth", "twelfth")),
         (4, 3): (("root", "fifth"), ("octave", "tenth"), ("fifth", "octave")) * 4,
         (2, 3): (("root", "fifth"), ("octave", "tenth"), ("fifth", "octave")) * 2}


def rolling_pairs(arr: Arrangement, part: Part, start: int, end: int, velocity: int, tune: list,
                  length: int = 2 * EIGHTH) -> None:
    """The ballad's middle hand: every eighth two tones of the chord (PAIRS),
    each key held `length` ticks, the beats a little stronger."""
    for tick in range(start, end, EIGHTH):
        chord = arr.chord_at(tick)
        root = bass_note(chord, MIDDLE)
        tones = {"root": root, "fifth": root + 7, "octave": root + 12, "tenth": root + 12 + third(chord),
                 "twelfth": root + 19}
        accent = 6 if tick % arr.bar == 0 else 3 if tick % arr.beat == 0 else 0
        notes = [tones[name] for name in PAIRS[arr.meter][tick % arr.bar // EIGHTH]]
        under_tune(arr, part, tune, tick + arr.jitter(4), notes, velocity + accent, length)


def pulse_hand(arr: Arrangement, part: Part, start: int, end: int, velocity: int, tune: list,
               length: int = EIGHTH) -> None:
    """The pulse's middle hand, the heartbeat of the slow pop carols: every
    eighth the chord's root and fifth together in the middle of the keyboard
    (E3 to D#4), the octave over them on the beats, each key held `length` ticks."""
    for tick in range(start, end, EIGHTH):
        chord = arr.chord_at(tick)
        root = bass_note(chord)
        low = root + 12 if root + 12 >= 52 else root + 24
        notes = [low, low + 7] + ([low + 12] if tick % arr.beat == 0 else [])
        accent = 6 if tick % arr.bar == 0 else 3 if tick % arr.beat == 0 else 0
        under_tune(arr, part, tune, tick + arr.jitter(3), notes, velocity + accent, length)


def cover_melody(arr: Arrangement, piano: Part, velocity: int, intro: bool = True,
                 aside: tuple = (0, 0)) -> list:
    """The tune an octave up (the intro's, the last phrase, is already), sung
    out evenly: each verse a little fuller than the one before, rising a little
    to its middle; in a middle verse its longer notes sung with a chord tone a
    third to a sixth under them, in the last (from its middle, if it is the
    only one) doubled an octave down. Where a phrase ends on a note held two
    beats or more, a few tones of the chord rise softly over it in eighths, as
    a pianist fills the breath. Between the ticks `aside` another instrument
    sings the tune, and the piano only follows it, softly and alone. Returns
    the tune's notes."""
    fills = []
    for tick, note, length, verse, position in arr.melody():
        if verse < 0 and not intro:
            continue
        note += 0 if verse < 0 else 12
        sung = velocity - (6 if verse < 0 else 0) + 3 * min(max(verse, 0), 2) + 5 * shape(position)
        at = tick + 4 + arr.jitter(4)
        if aside[0] <= tick < aside[1]:
            piano.add(at, note, sung - 18 + arr.rng.randint(-2, 2), length - 10)
            continue
        piano.add(at, note, sung + arr.rng.randint(-2, 2), length - 10)
        long = length >= arr.beat
        if verse == arr.last and long and (verse > 0 or position >= 0.5):
            piano.add(at - 8, note - 12, sung - 12, length - 10)
        elif 0 < verse < arr.last and long:
            second = harmony_below(arr.chord_at(tick), note)
            if second is not None:
                piano.add(at - 8, second, sung - 14, length - 10)
        if verse >= 0 and length >= 2 * arr.beat:
            bar = (tick - arr.verses[verse]) // arr.bar
            if bar in (arr.song.breaths or range(3, len(arr.song.chords), 4)):
                fills.append((tick + arr.beat, note, length - arr.beat, sung))
    tune = list(piano.notes)
    for tick, note, length, sung in fills:
        tones = chord_notes(arr.chord_at(tick), note + 3, min(note + 16, 91))[:min(3, length // EIGHTH - 1)]
        for i, tone in enumerate(tones):
            piano.add(tick + i * EIGHTH + arr.jitter(4), tone, sung - 20 + 2 * i, length - i * EIGHTH - 10)
    return tune


def free_intro(arr: Arrangement, piano: Part, velocity: int, top: int) -> list:
    """An intro in free time, as a pianist opens a carol: no tune yet, only the
    chords of its last bars, each rolled up from a deep bass (A1 to G#2)
    through an open chord to a top tone high up that moves to the nearest tone
    of the next chord (a slow tune of its own, from top), left to ring.
    Returns that top line: (tick, note, length)."""
    line = []
    for tick, length, chord in arr.chord_spans(0, arr.verses[0]):
        root, up = bass_note(chord, DEEP), third(chord)
        top = min(chord_notes(chord, 74, 88), key=lambda n: abs(n - top))
        voicing = sorted({root, root + 12, root + 19, root + 24 + up, root + 31, top})
        for i, note in enumerate(voicing):
            loud = velocity + (8 if i == 0 else 6 if note == top else -2 * i)
            piano.add(tick + i * 45 + arr.jitter(4), note, loud + arr.rng.randint(-2, 2), length)
        line.append((tick + (len(voicing) - 1) * 45, top, length))
    return line


def cover_end(arr: Arrangement, piano: Part, tune: list, velocity: int) -> None:
    """The last chord: its deep root with the octave, the chord rolled up from
    them, the pedal held; a beat later its keynote high up, soft as a far
    bell. Keys the tune still holds are left to it."""
    held = held_keys(tune, arr.end + 100)
    tonic = arr.chord_at(arr.end)
    root, up = bass_note(tonic, DEEP), third(tonic)
    rolled = ((root, -6), (root + 12, 0), (root + 19, 6), (root + 24, 6), (root + 24 + up, 8), (root + 31, 10),
              (root + 36, 10))
    for i, (note, softer) in enumerate(rolled):
        if note not in held:
            piano.add(arr.end + i * 45, note, velocity - softer, 3 * arr.bar)
    if root + 48 not in held:
        piano.add(arr.end + arr.beat + 40, root + 48, velocity - 14, 3 * arr.bar)
    piano.pedal += [(arr.end + 20, 127), (arr.end + 3 * arr.bar, 0)]


def pedal_by_beat(arr: Arrangement, part: Part, start: int, end: int) -> None:
    """The pedal taken again on every beat: what the hands have let go of rings
    through its beat and is then damped, so each beat's notes bloom and fade
    (the keys still held, the tune's long notes and the bass, ring on)."""
    for tick in range(start, end, arr.beat):
        part.pedal += [(tick + 40, 127), (tick + arr.beat - 25, 0)]


# The clear versions (ballad-clear, pulse-clear): heard close up, the
# references' accompaniment blooms and fades note by note (the middle of the
# keyboard swinging 4.5-6 dB within a quarter second, against 2.6-3.1 dB in
# ballad and pulse, whose pedal holds a whole chord), and their highs are
# brighter (8 kHz: 14 dB over ballad and pulse). So the pedal is taken again
# on every beat, the bass held a beat, the middle hand lifted after its eighth,
# and the piano's highs raised (a shelf, +8 dB from 6 kHz).
CLEAR_TONE = {"shelf": [6000, 8]}


# The instruments the two references play besides their piano, as two
# AudioSet taggers (PaSST, two checkpoints) heard them window by window,
# against our piano-only pieces (Piano 0.21-0.38 there, 0.05 in the
# references), with the notes' overtones and the tune's vibrato measured:
# - the first (pulse): a glockenspiel-like bell doubling the tune, with a
#   tinkle, in its first half (Glockenspiel 0.06-0.21, "Jingle, tinkle"
#   0.04-0.14; ours 0.001-0.003); a flute singing the tune in the middle
#   (Flute 0.06-0.21; held notes with a 5.2 Hz, +-9 cent vibrato); harp and
#   vibraphone at the end (0.04-0.12), faint strings;
# - the second (ballad): a softer, purer piano tone (Electric piano 0.65 on
#   its opening notes) over a synth pad (Synthesizer 0.04-0.18; ours 0.005-0.026).
VIBRATO = (5.2, 9.0)  # Hz, cents


def band_sections(arr: Arrangement) -> tuple:
    """Where the first reference's colours change (ticks, on bar lines): from
    the first the flute sings the tune (before it, the glockenspiel doubles
    it), from the second the harp, vibraphone and strings join. With three
    verses or more, the middle ones are the flute's and the last the close;
    with two, the second's first half is the flute's; with one, its third quarter."""
    verses, bars = arr.verses, lambda ticks: arr.bar * round(ticks / arr.bar)
    if len(verses) >= 3:
        return verses[1], verses[-1]
    if len(verses) == 2:
        return verses[1], verses[1] + bars(arr.verse / 2)
    return verses[0] + bars(arr.verse / 2), verses[0] + bars(3 * arr.verse / 4)


def vibrato(arr: Arrangement, part: Part, tick: int, length: int, delay: float = 0.25, ramp: float = 0.3) -> None:
    """A flautist's vibrato on a held note, as pitch bends (sfizz bends +-2
    semitones): none for its first quarter second, then growing over 0.3 s to
    the reference flute's (VIBRATO); back to true pitch as it ends."""
    per_second = arr.bpm * TICKS / 60  # ticks a second, near enough
    if length / per_second < delay + 0.2:
        return
    rate, cents = VIBRATO
    full, start = cents / 200 * 8191, tick + int(delay * per_second)
    for at in range(start, tick + length - 20, 12):
        seconds = (at - start) / per_second
        part.bends.append((at, round(full * min(1.0, seconds / ramp) * math.sin(2 * math.pi * rate * seconds))))
    part.bends.append((tick + length - 10, 0))


# The first verse's sparkle, by the user's ear: a mark tree's sweep as the
# piece began (run 18) did not please, nor sleigh bells shaken in time with a
# glockenspiel's note every second bar (run 19: "the ding does not fit, the
# sleigh bells a little coarse"), though close up the first reference's
# sparkle sounds like those; the glockenspiel softly doubling the tune (run
# 18, the arrangement liked) stays: heard against the piano alone in the
# first verse (run 20), the user chose it, and keeps both for the channel.
def band(arr: Arrangement, bells: bool = True, breathing: bool = False) -> None:
    """The first reference's other instruments around the piano: with bells, a
    glockenspiel (it sounds an octave over its keys) doubling the tune softly
    in the first verse; from `flute` the flute singing the tune; from `close`
    the vibraphone doubling the tune, a harp breaking the chords in eighths and
    soft strings holding them."""
    flute_from, close_from = band_sections(arr)
    glock = arr.part("glock", "glock", "shimmer", 0.2, reverb=0.45) if bells else None
    flute = arr.part("flute", "flute", "melody", -0.1, reverb=0.38)
    vibes = arr.part("vibes", "vibes", "shimmer", -0.2, reverb=0.4)
    for tick, note, length, verse, position in arr.melody():
        if verse < 0:
            continue
        at, high = tick + 4 + arr.jitter(3), note + 12  # the tune an octave up, as the piano sings it
        if tick < flute_from:
            if glock:
                glock.add(at, high, 42 + 6 * shape(position), min(length, arr.bar))
        elif tick < close_from:
            flute.add(at, high, 56 + 12 * shape(position), length + 20)
            vibrato(arr, flute, at, length)
        else:
            vibes.add(at, high, 48 + 8 * shape(position), length)
    harp = arr.part("harp", "harp", "arp", -0.3, reverb=0.35)
    if breathing:
        breathing_harp(arr, harp, close_from, arr.end, 50, octave=12)
    else:
        flowing_bass(arr, harp, close_from, arr.end, 50, octave=12)
    tonic = arr.chord_at(arr.end)
    harp.add(arr.end, bass_note(tonic) + 12, 54, 2 * arr.bar)
    gliss(arr, harp, arr.end + arr.beat, 2 * arr.beat, tonic, 60, 96, 42)
    strings(arr, close_from, arr.end + 2 * arr.bar, 40, roles=("bed", "bed"))
    for name in ("cellos", "violas"):
        breathe(arr, arr.parts[name], 84, 110, start=close_from)


def pad_chords(arr: Arrangement, part: Part, start: int, end: int, velocity: int) -> None:
    """The second reference's pad: each chord held in three tones between G3 and
    C5, each moving to the nearest tone of the next (tones two chords share held on)."""
    for tick, length, chord in arr.chord_spans(start, end):
        part.voicing = voice_lead(part.voicing, chord, 55, 72, count=3)
        for note in part.voicing:
            part.add(tick + arr.jitter(6), note, velocity, length + 30, tie=True)


def arrange_ballad(arr: Arrangement, clear: bool = False, breathing: bool = False) -> None:
    """After the second reference: the tune's last phrase as the intro, then
    the verses over the deep bass and the rolling pairs, a synth pad under it
    all, swelling with each phrase. With breathing, the rolling pairs breathe
    with each phrase: on its last bar the chord is laid down, rolled slowly,
    and left to ring."""
    piano = arr.part("piano", arr.piano, "piano", 0.0, reverb=0.32)
    tune = cover_melody(arr, piano, BRIGHT + 8)
    deep_bass(arr, piano, 0, arr.end, BRIGHT + 4, walk=True, hold=arr.beat if clear else None)
    if breathing:
        breathing_hand(arr, piano, 0, arr.end, 54, tune, calm=None, octave=12,
                       moving=lambda arr, part, start, end, velocity, avoid: rolling_pairs(arr, part, start, end,
                                                                                           velocity, tune))
    else:
        rolling_pairs(arr, piano, 0, arr.end, 54, tune, length=EIGHTH if clear else 2 * EIGHTH)
    (pedal_by_beat if clear else pedal_by_chord)(arr, piano, 0, arr.end)
    cover_end(arr, piano, tune, BRIGHT)
    # the pad far under the piano: at its first level (the role pad) it tagged
    # Synthesizer 0.18 and Ambient 0.35 against the reference's 0.03 and 0.07
    pad = arr.part("pad", "pad", "haze", 0.0, reverb=0.4)
    pad_chords(arr, pad, 0, arr.end + 2 * arr.bar, 56)
    breathe(arr, pad, 76, 108)


def arrange_pulse(arr: Arrangement, clear: bool = False, bells: bool = True, breathing: bool = False) -> None:
    """After the first reference: the verses (with a free intro, after rolled
    chords in free time) over the deep bass and the pulse, with its
    glockenspiel (if bells), flute, harp, vibraphone and strings (band). With
    breathing, the pulse and the harp breathe with each phrase: on its last
    bar the chord is laid down, rolled slowly, and left to ring."""
    piano = arr.part("piano", arr.piano, "piano", 0.0, reverb=0.32)
    tune = cover_melody(arr, piano, BRIGHT + 8, intro=False, aside=band_sections(arr))
    if arr.free_intro:
        free_intro(arr, piano, BRIGHT - 4, tune[0][1] if tune else 76)
    deep_bass(arr, piano, arr.verses[0], arr.end, BRIGHT + 4, hold=arr.beat if clear else None)
    if breathing:
        breathing_hand(arr, piano, arr.verses[0], arr.end, 50, tune, calm=None, octave=12,
                       moving=lambda arr, part, start, end, velocity, avoid: pulse_hand(arr, part, start, end,
                                                                                         velocity, tune))
    else:
        pulse_hand(arr, piano, arr.verses[0], arr.end, 50, tune, length=EIGHTH - 40 if clear else EIGHTH)
    if clear:
        pedal_by_chord(arr, piano, 0, arr.verses[0])  # the rolled chords ring
        pedal_by_beat(arr, piano, arr.verses[0], arr.end)
    else:
        pedal_by_chord(arr, piano, 0, arr.end)
    cover_end(arr, piano, tune, BRIGHT)
    band(arr, bells, breathing)


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


def arrange_orchestra(arr: Arrangement, turns: bool = False, calm: bool = False, build: float = 1.0,
                      breathing: bool = False) -> None:
    """Flute, then violins on the tune (with turns, in a longer piece, the two
    take it by turns in the middle verses), a flute descant over the last
    verse, on a harp and a string pad, basses plucked then bowed, horns from
    the middle of the last verse, a soft timpani roll under the last chord.
    The last phrase sparkles with a glockenspiel and the harp sweeps up to the
    top of its range over the last chord; calm, as the user asked ("not going
    up so high, then off"), ends low instead: no glockenspiel, the descant
    kept under A5, the harp breaking the last chord downwards into the deep
    tonic, and every held part dying away over it rather than stopping.
    build (0 to 1) is how far the last verse rises over the others: 1, the
    whole orchestra (the violins into their loud layer, a fuller string pad,
    horns, the descant, a harp glissando into it, timpani and, for a lively
    tune, sleigh bells); less, as the user asked ("still too much of a climax
    near the end"), the violins, the pad, the basses and the descant grow only
    that much, and under 0.75 the horns, the glissando, the timpani and the
    bells stay out, at 0 the descant too. With breathing, the harp breathes
    with each phrase: on its last bar it lays the chord down, rolled slowly,
    and lets it ring."""
    flute = arr.part("flute", "flute", "melody", -0.1, reverb=0.35)
    violins = arr.part("violins", "violins", "melody", -0.35, reverb=0.35)
    glock = None if calm else arr.part("glock", "glock", "sparkle", 0.3, reverb=0.45)
    for tick, note, length, verse, position in arr.melody():
        lift = shape(position)
        if verse == arr.last:  # the violins, from their soft layer into the full one at the height of the verse
            violins.add(tick + arr.jitter(4), note, 48 + 4 * build + (12 + 8 * build) * lift, length + 20)
            if glock and tick >= arr.end - arr.phrase:
                glock.add(tick + arr.jitter(4), note + 12, 40, length)
        elif turns and verse > 0 and verse % 2 == 1:  # every other middle verse: the violins, softly
            violins.add(tick + arr.jitter(4), note, 48 + 12 * lift, length + 20)
        else:  # the intro (an octave up already), the first verse and every other one: the flute, softly
            flute.add(tick + arr.jitter(4), note, (48 if verse < 0 else 52) + 8 * lift, length - 10)
    full = build >= 0.75
    harp = arr.part("harp", "harp", "harp", -0.3, reverb=0.35)
    harp_play = breathing_harp if breathing else flowing_bass
    harp_play(arr, harp, 0, arr.verses[0], 48, octave=12)
    harp_play(arr, harp, arr.verses[0], arr.verses[-1], 52)
    harp_play(arr, harp, arr.verses[-1], arr.end, 44, octave=12)
    if full:
        gliss(arr, harp, arr.verses[-1] - arr.beat, arr.beat, arr.chord_at(arr.verses[-1] - arr.beat), 55, 86, 48)
    strings(arr, 0, arr.verses[-1], 40)
    strings(arr, arr.verses[-1], arr.end + 2 * arr.bar, round(40 + 14 * build))
    pizz = arr.part("basses-pizz", "basses-pizz", "low", 0.45, reverb=0.3)
    for tick, _, chord in arr.chord_spans(arr.verses[0], arr.verses[-1]):
        if tick % arr.bar == 0:  # plucked on the downbeats of the first verse
            pizz.add(tick + arr.jitter(4), low_bass(chord), 54, arr.beat)
    basses = arr.part("basses", "basses", "low", 0.45, reverb=0.35)
    for tick, length, chord in arr.chord_spans(arr.verses[-1], arr.end + 2 * arr.bar):
        basses.add(tick + arr.jitter(6), low_bass(chord), round(52 + 8 * build), length + 20, tie=True)
    horns, middle = None, arr.verses[-1] + arr.verse // 2
    if full:
        horns = arr.part("horns", "horns", "pad", 0.2, reverb=0.4)
        for tick, length, chord in arr.chord_spans(middle, arr.end + 2 * arr.bar):
            horns.voicing = voice_lead(horns.voicing, chord, 53, 65)
            for note in horns.voicing:
                horns.add(tick + arr.jitter(6), note, 40, length + 20, tie=True)
    flute_descant = None
    if build > 0:
        flute_descant = arr.part("descant", "flute", "descant", 0.15, reverb=0.4)
        descant(arr, flute_descant, arr.verses[-1] + arr.phrase, arr.end, round(40 + 10 * build),
                ceiling=81 if calm else 86)
    if full:
        timpani = arr.part("timpani", "timpani", "drum", 0.0, reverb=0.4)
        timpani.add(arr.end, bass_note(arr.chord_at(arr.end)) + 12, 46, 2 * arr.bar)  # a soft roll under the last chord
        if arr.song.lively:  # a sleigh ride for a lively tune: one shake a bar in the last verse
            sleigh = arr.part("sleigh", "sleigh", "drum", 0.4, reverb=0.25)
            for tick in range(arr.verses[-1], arr.end, arr.bar):
                sleigh.add(tick + arr.jitter(6), 60, 46, arr.beat)
    tonic = arr.chord_at(arr.end)
    if calm:  # the chord's tones from the middle of the keyboard down, an eighth apart, into the deep tonic
        falling = chord_notes(tonic, 55, 76)[::-1]
        for i, note in enumerate(falling):
            harp.add(arr.end + i * EIGHTH, note, 50 - 2 * i, 2 * arr.bar)
        harp.add(arr.end + len(falling) * EIGHTH, bass_note(tonic), 46, 2 * arr.bar)
    else:
        harp.add(arr.end, bass_note(tonic), 58, 2 * arr.bar)
        gliss(arr, harp, arr.end + arr.beat, 2 * arr.beat, tonic, 60, 96, 42)
    fade = 24 if calm else None
    breathe(arr, flute, 100, 120, fade=fade)
    breathe(arr, violins, 100, 120, start=arr.verses[min(1, arr.last) if turns else -1], fade=fade)
    if flute_descant:
        breathe(arr, flute_descant, 84, 112, start=arr.verses[-1] + arr.phrase, fade=fade)
    for name in ("cellos", "violas"):
        breathe(arr, arr.parts[name], 86, 116, fade=fade)
    breathe(arr, basses, 86, 116, start=arr.verses[-1], fade=fade)
    if horns:
        breathe(arr, horns, 80, 112, start=middle, fade=fade)


# The church styles. Their hall's two sides share their echo below 250 Hz
# (render_samples.hall_ir), so an organ's held low notes, nearly pure tones,
# echo alike on both sides instead of in phase for one note and opposite for
# the next; and what goes into it sways slowly in pitch (render_samples.sway,
# SWAY), so the hall answers every held note about as strongly: still, a few
# rang it 10 dB over the rest (Silent Night's levels spread over 12 dB, its
# dry organ over 5; swayed, 6). Each part sends less into it than at first
# (SEND: the hall had stood 7 dB over the dry organ). A hymn is sung and played legato, every voice holding
# its note while it repeats it, and breathing where a phrase ends: there the
# voices let go a little before the tune's next phrase begins.
TOGETHER = 250.0  # Hz
SWAY = 0.0025  # s
SEND = 0.4  # each church part's send into the hall
BREATH = 100  # ticks
ORGAN_SECONDS = 10.0  # the church organ's samples last about 12 s
CHAMBER_SECONDS = 6.0  # the Renaissance organ's about 6.5 s


def hymn_beats(arr: Arrangement) -> list:
    """(tick, soprano, alto, tenor, bass, verse) on every beat: the intro (verse
    -1, the tune's last bars), then each verse, voiced by chorale.voices for
    the carol's chords (after the last verse's last note its chord is held:
    no pickup follows it)."""
    song = arr.song
    voices = chorale.voices(song, song.chords)
    final = chorale.last_note_beat(song)
    intro = arr.intro_bars * song.beats
    beats = [(j * arr.beat, *voices[len(voices) - intro + j], -1) for j in range(intro)]
    for verse, downbeat in enumerate(arr.verses):
        for i, voice in enumerate(voices):
            beats.append((downbeat + i * arr.beat, *(voices[final] if verse == arr.last and i > final else voice),
                          verse))
    return beats


def breath_points(arr: Arrangement) -> set:
    """Where the voices breathe: as the tune's note on each phrase's last
    downbeat ends (its next phrase beginning), and as the intro's and every
    verse's last note ends (the last verse's, where the Amen begins)."""
    tune = [(t, l, verse) for t, _, l, verse, _ in arr.melody()]
    points = {arr.end}
    rests = chorale.cadence_beats(arr.song) | {chorale.last_note_beat(arr.song)}
    for verse, downbeat in enumerate(arr.verses[:-1]):
        for beat in rests:
            tick = downbeat + beat * arr.beat
            points |= {t + l for t, l, v in tune if v == verse and t <= tick < t + l}
    for beat in rests - {chorale.last_note_beat(arr.song)}:
        tick = arr.verses[-1] + beat * arr.beat
        points |= {t + l for t, l, v in tune if v == arr.last and t <= tick < t + l}
    intro = [t + l for t, l, v in tune if v < 0]
    if intro:
        points.add(max(intro))
    return points


def phrased(notes: list, points: set) -> list:
    """The notes (tick, note, length) breathing at the points: a note sounding
    into a point lets go BREATH ticks before it, and one held across it
    sounds again from it."""
    out = []
    for tick, note, length in sorted(notes):
        for point in sorted(points):
            if tick < point - BREATH < tick + length:
                out.append((tick, note, point - BREATH - tick))
                tick, length = point, tick + length - point
                if length <= BREATH:
                    break
        else:
            out.append((tick, note, length))
    return [n for n in out if n[2] > 0]


def hymn_voice(beats: list, index: int, start: int, end: int, beat: int) -> list:
    """One voice of hymn_beats (1 alto, 2 tenor, 3 bass) between two ticks:
    (tick, note, length), a note held on while the voice repeats it."""
    notes = []
    for tick, *voices, _ in beats:
        if start <= tick < end:
            note = voices[index]
            if notes and notes[-1][1] == note and sum(notes[-1][::2]) == tick:
                notes[-1] = (notes[-1][0], note, notes[-1][2] + beat)
            else:
                notes.append((tick, note, beat))
    return notes


def sing(arr: Arrangement, part: Part, beats: list, points: set, start: int, end: int, voices: tuple,
         velocity: int, tune: bool = True, longest: float | None = None) -> None:
    """Plays some of the four voices between two ticks on a part: the tune (its
    own notes, the intro's at the tune's pitch) if `tune`, and the voices
    numbered (1 alto, 2 tenor, 3 bass), breathing with the phrases; with
    longest, no note held longer than its samples last (seconds)."""
    notes = [(t, n - (12 if verse < 0 else 0), min(l, end - t)) for t, n, l, verse, _ in arr.melody()
             if start <= t < end] if tune else []
    for index in voices:
        notes += hymn_voice(beats, index, start, end, arr.beat)
    for tick, note, length in phrased(notes, points):
        if longest:
            while length > 0 and arr.seconds(tick, tick + length) > longest:
                length -= EIGHTH
        part.add(tick + arr.jitter(4), note, velocity + arr.rng.randint(-2, 2), length - 10)


def amen(arr: Arrangement, beats: list, parts: list) -> None:
    """The Amen after the last verse, IV for a bar, then I held for two
    (chorale.amen): parts are (part, voices played: 0 soprano, 1 alto, 2
    tenor, 3 bass, velocity, longest note in seconds or None)."""
    last = next(voices for tick, *voices, verse in reversed(beats) if verse == arr.last)
    chords = chorale.amen(arr.song, tuple(last))
    for part, voices, velocity, longest in parts:
        for k, chord in enumerate(chords):
            tick = arr.end + k * arr.bar
            length = arr.bar - BREATH if k == 0 else 2 * arr.bar
            if longest:
                while arr.seconds(tick, tick + length) > longest:
                    length -= EIGHTH
            for index in voices:
                part.add(tick + arr.jitter(4), chord[index], velocity - 6 * k, length)


def lead_in(arr: Arrangement, seconds: float) -> int:
    """Moves the whole piece later, by whole beats lasting at least `seconds`
    at its tempo, for what comes before its intro (a bell). Returns the ticks."""
    ticks = math.ceil(seconds * arr.bpm / 60 * TICKS / arr.beat) * arr.beat
    for part in arr.parts.values():
        part.notes = [(t + ticks, n, v, l) for t, n, v, l in part.notes]
        part.pedal = [(t + ticks, v) for t, v in part.pedal]
        part.expression = [(t + ticks, v) for t, v in part.expression]
        part.bends = [(t + ticks, v) for t, v in part.bends]
    arr.tempos = [(0, arr.bpm)] + [(t + ticks, bpm) for t, bpm in arr.tempos]
    arr.shift += ticks
    return ticks


def toll(arr: Arrangement, part: Part, start: int, notes: list, seconds: float, velocity: int) -> None:
    """A bell struck once for each note, `seconds` apart at the tempo from start."""
    tick = start
    for k, note in enumerate(notes):
        part.add(tick, note, velocity - 4 * k, 4 * arr.bar)
        bpm = next(b for t, b in reversed(arr.tempos) if t <= tick)
        tick += round(seconds * bpm / 60 * TICKS)


def arrange_church(arr: Arrangement, choir: str | None = None, festive: bool = False, chapel: bool = False,
                   bell: str | None = "bell-tower") -> None:
    """The organ gives out the tune (the intro), then plays the verses in four
    voices, or the first only, a choir (choir: its instrument) singing the
    others, the organ softly under it; the last verse a little fuller (the
    loud organ joining softly; festive: the loud organ, brass doubling the
    voices and a timpani roll under the Amen); then the Amen. chapel: a small
    Renaissance organ, its bass on the same stop. A bell (bell: its
    instrument) tolls the piece in, before the intro, and out after the Amen."""
    beats, points = hymn_beats(arr), breath_points(arr)
    organ = "chamber-organ" if chapel else "organ"
    longest = CHAMBER_SECONDS if chapel else ORGAN_SECONDS
    pickup = math.ceil(round(arr.song.pickup * EIGHTH) / arr.beat) * arr.beat  # a verse begins with its pickup
    sung = arr.verses[min(1, arr.last)] - pickup if choir else arr.end
    lead = arr.part("organ", organ, "melody", 0.0, reverb=SEND)
    pedal = arr.part("pedal", organ if chapel else "pedal", "bass", 0.0, reverb=SEND)
    sing(arr, lead, beats, points, 0, sung, (1, 2), 80, longest=longest)
    sing(arr, pedal, beats, points, 0, sung, (3,), 80, tune=False, longest=longest)
    under = [(lead, (0, 1, 2), 80, longest), (pedal, (3,), 80, longest)]
    if choir:
        high = arr.part("choir-high", choir, "melody", -0.2, reverb=SEND)
        low = arr.part("choir-low", choir, "voices", 0.2, reverb=SEND)
        sing(arr, high, beats, points, sung, arr.end, (1,), 84)
        sing(arr, low, beats, points, sung, arr.end, (2, 3), 80, tune=False)
        soft = arr.part("organ-soft", organ, "bed", 0.0, reverb=SEND)
        soft_pedal = arr.part("pedal-soft", organ if chapel else "pedal", "low", 0.0, reverb=SEND)
        sing(arr, soft, beats, points, sung, arr.end, (1, 2), 80, longest=longest)
        sing(arr, soft_pedal, beats, points, sung, arr.end, (3,), 80, tune=False, longest=longest)
        under = [(soft, (0, 1, 2), 80, longest), (soft_pedal, (3,), 80, longest),
                 (high, (0, 1), 74, None), (low, (2, 3), 70, None)]
        for part, low_level in ((high, 96), (low, 92)):
            breathe(arr, part, low_level, 118, start=sung, fade=56)
    last = arr.verses[-1] - pickup
    if not chapel:  # the last verse a little fuller
        full = arr.part("organ-loud", "organ-loud", "pad" if festive else "bed", 0.0, reverb=SEND)
        full_pedal = arr.part("pedal-loud", "pedal-loud", "low", 0.0, reverb=SEND)
        sing(arr, full, beats, points, last, arr.end, (1, 2), 80, longest=longest)
        sing(arr, full_pedal, beats, points, last, arr.end, (3,), 80, tune=False, longest=longest)
        under += [(full, (0, 1, 2), 80, longest), (full_pedal, (3,), 80, longest)]
    if festive:  # brass doubling the voices
        brass = [(arr.part("trumpets", "trumpets", "pad", -0.25, reverb=0.5), (), True),
                 (arr.part("trombones", "trombones", "pad", 0.25, reverb=0.5), (1, 2), False),
                 (arr.part("tuba", "tuba", "low", 0.1, reverb=0.5), (3,), False)]
        for part, voices, tune in brass:
            sing(arr, part, beats, points, last, arr.end, voices, 60, tune=tune, longest=4.0)
            breathe(arr, part, 90, 116, start=last, fade=60)
        under += [(brass[0][0], (0,), 54, 4.0), (brass[1][0], (1, 2), 54, 4.0), (brass[2][0], (3,), 54, 4.0)]
        timpani = arr.part("timpani", "timpani", "drum", 0.0, reverb=0.45)
        timpani.add(arr.end + arr.bar, bass_note(arr.chord_at(arr.end)) + 12, 44, 2 * arr.bar)
    amen(arr, beats, under)
    if bell:
        church_bell(arr, bell)


def church_bell(arr: Arrangement, bell: str) -> None:
    """A bell (its instrument) tolling the piece in, before the intro (the
    piece moved later for it), and out after the Amen."""
    tonic = CHORDS[arr.chord_at(arr.end)][0]
    low = (48 if bell == "bell-tower" else 60) + (tonic - (48 if bell == "bell-tower" else 60)) % 12
    # the dominant under the tonic, or over it where the tubular bells (C4-F5) have none under
    dominant = low - 5 if bell == "bell-tower" or low - 5 >= 60 else low + 7
    ticks = lead_in(arr, 6.0)
    bells = arr.part("bell", bell, "bells", 0.15, reverb=0.6)
    toll(arr, bells, 0, [low, dominant, low], 2.0, 60)
    toll(arr, bells, ticks + arr.end + arr.bar + arr.beat, [low, low, low], 2.4, 54)


# The user found the church pieces hard to listen to, on a phone above all:
# the organ's held four voices sat in 100-250 Hz, the tune no clearer than
# the voices under it, so a phone's speaker (nothing under ~350 Hz) played
# them 8 dB quieter, muffled. Two lighter ways, the tune clear on top:
STRINGS_SECONDS = 4.4  # the strings' samples last about 5 s


def arrange_church_piano(arr: Arrangement) -> None:
    """The hymn on the gentle Yamaha upright: the tune on top, struck into the
    piano's brighter layer as pulse plays it (it carries on a phone), alto,
    tenor and bass softly under it, each struck as its note changes and held
    while it stays (chorale.voices), the pedal taken again with each chord;
    from the second verse soft strings holding alto, tenor and bass (violas,
    cellos, as the orchestra's pad); in the last verse a choir humming
    ("ooh") alto and tenor far under it; the Amen; a tubular bell tolling the
    piece in and out."""
    beats, points = hymn_beats(arr), breath_points(arr)
    piano = gentle_piano(arr)
    for tick, note, length, verse, position in arr.melody():
        velocity = (60 if verse < 0 else 66 + 3 * min(verse, 2)) + 4 * shape(position)
        piano.add(tick + 6 + arr.jitter(4), note - (12 if verse < 0 else 0), velocity + arr.rng.randint(-2, 2),
                  length - 10)
    tune = list(piano.notes)
    piano.leading = len(tune)
    for index, velocity in ((1, 44), (2, 42), (3, 50)):
        for tick, note, length in phrased(hymn_voice(beats, index, 0, arr.end, arr.beat), points):
            if not busy(tune, note, tick, length):
                piano.add(tick + 10 * index + arr.jitter(4), note, velocity + arr.rng.randint(-2, 2), length - 10)
    pedal_by_chord(arr, piano, 0, arr.end)
    pickup = math.ceil(round(arr.song.pickup * EIGHTH) / arr.beat) * arr.beat
    second = arr.verses[min(1, arr.last)] - pickup
    violas = arr.part("violas", "violas", "bed", 0.15, reverb=SEND)
    cellos = arr.part("cellos", "cellos", "bed", 0.35, reverb=SEND)
    sing(arr, violas, beats, points, second, arr.end, (1, 2), 50, tune=False, longest=STRINGS_SECONDS)
    sing(arr, cellos, beats, points, second, arr.end, (3,), 52, tune=False, longest=STRINGS_SECONDS)
    for part in (violas, cellos):
        breathe(arr, part, 84, 110, start=second, fade=40)
    last = arr.verses[-1] - pickup
    choir = arr.part("choir", "oohs", "haze", 0.0, reverb=SEND)
    sing(arr, choir, beats, points, last, arr.end, (1, 2), 70, tune=False)
    breathe(arr, choir, 90, 116, start=last, fade=50)
    amen(arr, beats, [(piano, (0, 1, 2, 3), 54, None), (violas, (1, 2), 50, STRINGS_SECONDS),
                      (cellos, (3,), 52, STRINGS_SECONDS), (choir, (1, 2), 64, None)])
    piano.pedal += [(arr.end + 20, 127), (arr.end + arr.bar - 25, 0), (arr.end + arr.bar + 20, 127),
                    (arr.end + 3 * arr.bar, 0)]
    church_bell(arr, "tubular")


def arrange_church_clear(arr: Arrangement) -> None:
    """The organ, its tune clear: the tune alone on the loud manual's bright
    diapason (its overtones carry on a phone), alto and tenor under it on the
    quiet manual, softer and without their lowest lows (high-passed at 140
    Hz), the bass on the loud pedal, whose overtones a phone still plays,
    softer still; the last verse a little fuller (alto and tenor on the loud
    manual too, softly); the Amen; a tubular bell tolling the piece in and out."""
    beats, points = hymn_beats(arr), breath_points(arr)
    tune = arr.part("tune", "organ-loud", "melody", 0.0, reverb=SEND)
    inner = arr.part("organ", "organ", "pad", 0.0, reverb=SEND)
    inner.tone["highpass"] = 140
    pedal = arr.part("pedal", "pedal-loud", "low", 0.0, reverb=SEND)
    sing(arr, tune, beats, points, 0, arr.end, (), 80, longest=ORGAN_SECONDS)
    sing(arr, inner, beats, points, 0, arr.end, (1, 2), 80, tune=False, longest=ORGAN_SECONDS)
    sing(arr, pedal, beats, points, 0, arr.end, (3,), 80, tune=False, longest=ORGAN_SECONDS)
    pickup = math.ceil(round(arr.song.pickup * EIGHTH) / arr.beat) * arr.beat
    last = arr.verses[-1] - pickup
    fuller = arr.part("organ-loud", "organ-loud", "bed", 0.0, reverb=SEND)
    fuller.tone["highpass"] = 140
    sing(arr, fuller, beats, points, last, arr.end, (1, 2), 80, tune=False, longest=ORGAN_SECONDS)
    amen(arr, beats, [(tune, (0,), 80, ORGAN_SECONDS), (inner, (1, 2), 80, ORGAN_SECONDS),
                      (pedal, (3,), 80, ORGAN_SECONDS), (fuller, (1, 2), 80, ORGAN_SECONDS)])
    church_bell(arr, "tubular")


# The user asked for the clear organ joined by other instruments and by voices
# humming ("tiếng ngân nga"): GeneralUser GS's choir singing "ooh", as in
# chapel. What joins the organ takes the place of its held voices rather than
# doubling them, and keeps out of the lows, so the tune stays clear on a phone.
HUM = 120.0  # Hz: the humming voices' high-pass
# The user then found the organ "too heavy" and asked for it softer and more
# relaxing. Its loud manual's open diapason is the brightest of the organs
# (2-5 kHz 15 dB under the whole tone, its harmonics up to the sixth within 20
# dB of the fundamental) and its level pulses (2.6 dB, about once a second);
# the loud pedal is as bright. Softer registrations, each (tune, voices under
# it, bass, the samples' length in seconds): the quiet manual's stopped flute
# (nearly a pure tone, its third harmonic 9 dB under the fundamental) on the
# quiet pedal; or the small Renaissance organ, its 8' and 4' flutes together
# for the tune (a pure tone and its octave: clear on a phone, never sharp),
# the 8' alone under it. Played softly they swell and ebb with each phrase, as
# an organ's swell box lets them (expression), and a little slower.
ORGANS = {"loud": ("organ-loud", "organ", "pedal-loud", ORGAN_SECONDS),
          "flutes": ("organ", "organ", "pedal", ORGAN_SECONDS),
          "small": ("chamber-organ-48", "chamber-organ", "chamber-organ", CHAMBER_SECONDS),
          # simulated, as the user asked to try: its notes last as long as held
          "synth": ("organ-synth", "organ-synth", "pedal-synth", 60.0)}


def arrange_church_ensemble(arr: Arrangement, hum: bool = False, organ: str = "loud",
                            breathing: bool = False, bell: str = "tubular") -> None:
    """The organ of arrange_church_clear, joined verse by verse: from the
    first verse a harp breaking each chord gently upwards and back in eighths;
    from the second a choir humming ("ooh") alto and tenor in place of the
    quiet manual; in the last verse the choir humming the tune too, softly
    under the organ's, violas holding alto and tenor, and a flute's slow
    descant over the verse's second half; the Amen, the harp falling through
    its last chord; a tubular bell tolling the piece in and out. With hum,
    the voices forward: the choir humming alto and tenor from the first
    verse, and in the second (when there are three or more) the tune itself
    as the melody, the organ's tune resting and its quiet manual holding alto
    and tenor; the harp from the second verse; no flute. organ: its
    registration (ORGANS); a soft one swells and ebbs with each phrase. With
    breathing, the harp breathes with each phrase too: on its last bar it lays
    the chord down, rolled slowly, and lets it ring. bell: the bell's instrument."""
    beats, points = hymn_beats(arr), breath_points(arr)
    lead, under_lead, bass, longest = ORGANS[organ]
    pickup = math.ceil(round(arr.song.pickup * EIGHTH) / arr.beat) * arr.beat  # a verse begins with its pickup
    first, second, last = (arr.verses[0] - pickup, arr.verses[min(1, arr.last)] - pickup,
                           arr.verses[-1] - pickup)
    hummed = (second, arr.verses[2] - pickup) if hum and arr.last >= 2 else None  # the verse the choir hums the tune
    tune = arr.part("tune", lead, "melody", 0.0, reverb=SEND)
    inner = arr.part("organ", under_lead, "pad", 0.0, reverb=SEND)
    inner.tone["highpass"] = 140
    pedal = arr.part("pedal", bass, "low", 0.0, reverb=SEND)
    sing(arr, pedal, beats, points, 0, arr.end, (3,), 80, tune=False, longest=longest)
    if hummed:
        sing(arr, tune, beats, points, 0, hummed[0], (), 80, longest=longest)
        sing(arr, tune, beats, points, hummed[1], arr.end, (), 80, longest=longest)
        hum_tune = arr.part("hum-tune", "oohs", "melody", -0.1, reverb=SEND)
        sing(arr, hum_tune, beats, points, *hummed, (), 76)
        breathe(arr, hum_tune, 96, 120, start=hummed[0], fade=60)
        hum_tune.expression = [(t, v) for t, v in hum_tune.expression if t < hummed[1]]
    else:
        sing(arr, tune, beats, points, 0, arr.end, (), 80, longest=longest)
    hum_from = first if hum else second
    sing(arr, inner, beats, points, 0, hum_from, (1, 2), 80, tune=False, longest=longest)
    voices = arr.part("hum", "oohs", "hum", 0.15, reverb=SEND)
    voices.tone["highpass"] = HUM
    if hummed:  # the organ holds alto and tenor while the choir hums the tune
        sing(arr, inner, beats, points, *hummed, (1, 2), 80, tune=False, longest=longest)
        sing(arr, voices, beats, points, hum_from, hummed[0], (1, 2), 72, tune=False)
        sing(arr, voices, beats, points, hummed[1], arr.end, (1, 2), 72, tune=False)
    else:
        sing(arr, voices, beats, points, hum_from, arr.end, (1, 2), 72, tune=False)
    breathe(arr, voices, 90, 116, start=hum_from, fade=50)
    harp = arr.part("harp", "harp", "arp", -0.3, reverb=SEND)
    harp_from = second if hum else first
    if breathing:
        breathing_harp(arr, harp, harp_from + pickup, arr.end, 46, octave=12)
    else:
        flowing_bass(arr, harp, harp_from + pickup, arr.end, 46, octave=12)
    violas = arr.part("violas", "violas", "bed", 0.3, reverb=SEND)
    sing(arr, violas, beats, points, last, arr.end, (1, 2), 50, tune=False, longest=STRINGS_SECONDS)
    breathe(arr, violas, 84, 110, start=last, fade=40)
    under = [(tune, (0,), 80, longest), (pedal, (3,), 80, longest), (voices, (1, 2), 66, None),
             (violas, (1, 2), 50, STRINGS_SECONDS)]
    if organ != "loud":  # the soft organ swells and ebbs with each phrase
        for part, low, high in ((tune, 92, 118), (inner, 84, 108), (pedal, 88, 110)):
            breathe(arr, part, low, high, fade=56)
    if not hum:
        high = arr.part("hum-high", "oohs", "pad", -0.15, reverb=SEND)
        sing(arr, high, beats, points, last, arr.end, (), 70)
        breathe(arr, high, 86, 112, start=last, fade=50)
        flute = arr.part("descant", "flute", "descant", 0.2, reverb=SEND)
        descant(arr, flute, arr.verses[-1] + arr.phrase, arr.end, 46, ceiling=81)
        breathe(arr, flute, 84, 112, start=arr.verses[-1] + arr.phrase, fade=36)
        under.append((high, (0,), 64, None))
    amen(arr, beats, under)
    tonic = arr.chord_at(arr.end)  # the Amen's last chord: from the middle of the keyboard down, into the deep tonic
    falling = chord_notes(tonic, 55, 76)[::-1]
    for i, note in enumerate(falling):
        harp.add(arr.end + arr.bar + i * EIGHTH, note, 48 - 2 * i, 2 * arr.bar)
    harp.add(arr.end + arr.bar + len(falling) * EIGHTH, bass_note(tonic), 44, 2 * arr.bar)
    church_bell(arr, bell)


# A player, after the arrangement (perform): the tempo swings over each phrase
# as the KTH performance rules' phrase arch has it (slower at its ends, a
# little faster just after its middle, around the arrangement's own tempo and
# its breaths), the tune swells to each phrase's peak and falls away, its
# higher and longer notes a little louder (high loud, duration contrast), the
# parts under it swell less, and the random jitter shrinks (loose), so the
# timing is shaped rather than scattered. Only instruments whose sound follows
# the velocity are touched (VELOCITY); the others swell by expression.
VELOCITY = {"piano", "grand", "knight", "yamaha", "salamander", "ep", "harp", "ep-synth", "felt-synth"}


@dataclass
class Perform:
    rubato: float = 0.08  # the tempo's swing over a phrase, as a share of it
    peak: float = 0.6  # where in the phrase the arch peaks
    swell: float = 6.0  # the tune's velocity over the phrase: up to about this over, and under, its own
    under: float = 4.0  # the same for the parts under the tune
    high: float = 3.0  # the tune's velocity per octave over its phrase's mean pitch
    long: float = 2.0  # the tune's velocity for a note twice a beat long (as much less for half a beat)
    loose: float = 0.5  # the random jitter, times this
    ceiling: int = 127  # the highest velocity (the felt piano stays in its soft samples, under 66)


def humane_tempos(arr: Arrangement, how: Perform) -> list:
    """The tempo map, every eighth, its tempo swinging over each phrase."""
    spans = phrase_spans(arr)
    starts = [start for start, _ in spans]
    centre = sum(arch(i / 400, how.peak) for i in range(400)) / 400  # so a phrase keeps its length, near enough

    def swing(tick: int) -> float:
        t = tick - arr.shift
        i = bisect.bisect_right(starts, t) - 1
        if i < 0 or t >= spans[i][1]:
            return 1.0
        start, end = spans[i]
        return 1 + how.rubato * (arch((t - start) / (end - start), how.peak) - centre)

    last = arr.tempos[-1][0] + 4 * arr.bar
    tempos, k = [], 0
    for tick in sorted(set(range(0, last, EIGHTH)) | {t for t, _ in arr.tempos}):
        while k + 1 < len(arr.tempos) and arr.tempos[k + 1][0] <= tick:
            k += 1
        bpm = arr.tempos[k][1] * swing(tick)
        if not tempos or abs(tempos[-1][1] - bpm) > 1e-6:
            tempos.append((tick, bpm))
    return tempos


def perform(arr: Arrangement, how: Perform) -> None:
    """The arrangement played as a person plays it (Perform)."""
    spans = phrase_spans(arr)
    starts = [start for start, _ in spans]
    centre = sum(arch(i / 400, how.peak) for i in range(400)) / 400

    def phrase(tick: int) -> int | None:
        i = bisect.bisect_right(starts, tick - arr.shift) - 1
        return i if i >= 0 and tick - arr.shift < spans[i][1] else None

    sung = {}  # the tune's keys: their ticks, before any lead-in
    for tick, note, _, _, _ in arr.melody():
        for key in (note, note + 12):  # an octave up in some verses
            sung.setdefault(key, []).append(tick)

    def in_tune(part: Part, index: int, tick: int, note: int) -> bool:
        if part.leading:
            return index < part.leading
        return part.role == "melody" or any(abs(tick - arr.shift - t) <= 30 for t in sung.get(note, ()))

    for part in arr.parts.values():
        if part.instrument not in VELOCITY:
            continue
        tune = [(phrase(t), n) for k, (t, n, _, _) in enumerate(part.notes)
                if phrase(t) is not None and in_tune(part, k, t, n)]
        means = {i: sum(n for j, n in tune if j == i) / sum(1 for j, _ in tune if j == i) for i in {j for j, _ in tune}}
        played = []
        for k, (tick, note, velocity, length) in enumerate(part.notes):
            i = phrase(tick)
            if i is not None:
                start, end = spans[i]
                rise = arch((tick - arr.shift - start) / (end - start), how.peak) - centre
                if in_tune(part, k, tick, note):
                    velocity += (2 * how.swell * rise + how.high * (note - means[i]) / 12
                                 + how.long * max(-1.0, min(1.0, math.log2(length / arr.beat))))
                else:
                    velocity += 2 * how.under * rise
                velocity = max(1, min(how.ceiling, round(velocity)))
            played.append((tick, note, velocity, length))
        part.notes = played
    arr.tempos = humane_tempos(arr, how)


@dataclass
class Style:
    arrange: Callable
    tempo: float = 1.0  # times the carol's own tempo
    breath: float = 0.92  # the tempo of the last beat of each phrase, times the tempo
    hall: float = 2.2  # the hall's reverb time (s); under 2.2 a smaller room, answering sooner
    wet: float = 1.0  # every part's send into it, times this: less, and the sound is closer
    repeat_short: bool = False  # play a short tune (under 40 s at its own tempo) three times
    noise_db: float | None = None  # a hush of pink noise under the music, this far under the melody
    together: float = 0.0  # the hall's two sides alike below this (Hz): render_samples.hall_ir
    sway: float = 0.0  # what goes into the hall swayed slowly in pitch, this deep (s): render_samples.sway
    verses: int | None = None  # this many verses, whatever the tune's length
    seconds: float | None = None  # as many verses (2 to 6) as last about this long
    piano_tone: dict | None = None  # changes to the piano part's tone
    piano_reverb: float | None = None  # the piano part's reverb send instead of its own (tests)
    bpm: float | None = None  # this tempo, when slower than the carol's own (else tempo)
    free_intro: bool = False  # open with the chords alone, in free time
    intro: bool = True  # an intro before the first verse; without one the tune starts at once
    master: dict = field(default_factory=lambda: dict(MASTER))  # how strongly master.py works on it
    piano: str = "piano"  # the instrument its piano part is played on
    reharm: bool = False  # the carol's chords coloured as the pop ballads colour them (reharmonize)
    harmony: str | None = None  # "chorale": the carol harmonized as a hymnal does (chorale.harmonize)
    perform: Perform | None = None  # played as a person plays it, shaping each phrase (perform)


# The gentle styles are played on the Yamaha upright: of the three pianos
# (the Steinway grand, the Knight and Yamaha uprights), the user heard it as
# the softest and best for relaxing piano; piano keeps the Steinway grand.
GENTLE_PIANO = "yamaha"


# The master's steps (master.py), each from 0 (off) to 1. All are off: heard
# against the same pieces unmastered, the mastered ones sounded rough ("re")
# and less good, the made air above all (a saturation's overtones of whole
# chords). Only its balance, always on, still evens out a piece leaning more
# than 1 dB to one side.
MASTER = {"tone": 0.0, "air": 0.0, "width": 0.0, "level": 0.0}


STYLES = {
    "piano": Style(arrange_piano),
    "salamander": Style(lambda arr: arrange_piano(arr, "salamander")),
    "chill": Style(arrange_chill, tempo=0.8, breath=0.88, repeat_short=True, piano=GENTLE_PIANO),
    "lullaby": Style(arrange_lullaby, tempo=0.7, breath=0.85, repeat_short=True, piano=GENTLE_PIANO),
    "flowing": Style(arrange_flowing, tempo=0.85, breath=0.9, repeat_short=True, piano=GENTLE_PIANO),
    "hymn": Style(arrange_hymn, tempo=0.75, breath=0.85, repeat_short=True, piano=GENTLE_PIANO),
    "piano-strings": Style(arrange_piano_strings, tempo=0.8, breath=0.88, hall=2.4, repeat_short=True,
                           piano=GENTLE_PIANO),
    "felt": Style(arrange_felt, tempo=0.8, breath=0.9, repeat_short=True, piano=GENTLE_PIANO),
    # felt brighter, as the user asked: its low-pass opened from 900 Hz to 2 or
    # 4 kHz, or taken away
    "felt-2k": Style(arrange_felt, tempo=0.8, breath=0.9, repeat_short=True, piano=GENTLE_PIANO,
                     piano_tone={"lowpass": 2000}),
    "felt-4k": Style(arrange_felt, tempo=0.8, breath=0.9, repeat_short=True, piano=GENTLE_PIANO,
                     piano_tone={"lowpass": 4000}),
    "felt-open": Style(arrange_felt, tempo=0.8, breath=0.9, repeat_short=True, piano=GENTLE_PIANO,
                       piano_tone={"lowpass": None}),
    # brighter still: the soft samples are dark however open the filter (2-4
    # kHz some 37 dB under 200-1000 Hz), so the tune reaches the bright layer
    "felt-bright": Style(lambda arr: arrange_felt(arr, bright=True), tempo=0.8, breath=0.9, repeat_short=True,
                         piano=GENTLE_PIANO, piano_tone={"lowpass": None}),
    "felt-noise": Style(arrange_felt, tempo=0.8, breath=0.9, repeat_short=True, noise_db=-22, piano=GENTLE_PIANO),
    # ballad and pulse in a small room (0.8 s), with little of it: the user hears
    # the references "very close to the ear", and ours in a 2.8 s hall "as if in
    # a big room"; of 1.2 s at 0.6 times the sends and 0.8 s at 0.45, they chose
    # the closer (ballad either, with or without the Rhodes' chorus).
    "ballad": Style(arrange_ballad, bpm=72, breath=0.9, hall=0.8, wet=0.45, repeat_short=True, piano="ep",
                    reharm=True),
    # the user keeps the Rhodes ballad both with its chorus and without (the
    # listening page's 11 and 10)
    "ballad-plain": Style(arrange_ballad, bpm=72, breath=0.9, hall=0.8, wet=0.45, repeat_short=True, piano="ep",
                          reharm=True, piano_tone={"chorus": 0}),
    # pulse goes straight into the tune: the user wanted its 10 s of rolled
    # chords in free time, the intro pulse-clear keeps, gone. Of its versions
    # the user keeps four for the channel (the listening page's 9, 8, 7, 6):
    # the small room, the 1.2 s room, and the old 2.8 s hall with the
    # glockenspiel or with the piano alone in the first verse.
    "pulse": Style(arrange_pulse, bpm=88, breath=0.9, hall=0.8, wet=0.45, repeat_short=True, intro=False,
                   piano=GENTLE_PIANO),
    "pulse-near": Style(arrange_pulse, bpm=88, breath=0.9, hall=1.2, wet=0.6, repeat_short=True, intro=False,
                        piano=GENTLE_PIANO),
    "pulse-hall": Style(arrange_pulse, bpm=88, breath=0.9, hall=2.8, repeat_short=True, intro=False,
                        piano=GENTLE_PIANO),
    "pulse-hall-plain": Style(lambda arr: arrange_pulse(arr, bells=False), bpm=88, breath=0.9, hall=2.8,
                              repeat_short=True, intro=False, piano=GENTLE_PIANO),
    "ballad-clear": Style(lambda arr: arrange_ballad(arr, clear=True), bpm=72, breath=0.9, hall=2.8,
                          repeat_short=True, piano="grand", piano_tone=CLEAR_TONE),
    "pulse-clear": Style(lambda arr: arrange_pulse(arr, clear=True), bpm=88, breath=0.9, hall=2.8,
                         repeat_short=True, free_intro=True, piano="grand", piano_tone=CLEAR_TONE),
    "bells": Style(arrange_bells, hall=2.6),
    "orchestra": Style(arrange_orchestra, hall=2.4),
    # orchestra longer, as the user asked: verses enough for about two and a
    # half minutes, the flute and the violins taking the tune by turns
    "orchestra-long": Style(lambda arr: arrange_orchestra(arr, turns=True), hall=2.4, seconds=150),
    # the user keeps the longer orchestra, but not its ending ("going up so
    # high, then off"): it now ends low and dies away (calm)
    "orchestra-long-calm": Style(lambda arr: arrange_orchestra(arr, turns=True, calm=True), hall=2.4, seconds=150),
    # still "too much of a climax near the end": the last verse rising only a
    # little (gentle), or no more than the others (flat)
    "orchestra-gentle": Style(lambda arr: arrange_orchestra(arr, turns=True, calm=True, build=0.4), hall=2.4,
                              seconds=150),
    "orchestra-flat": Style(lambda arr: arrange_orchestra(arr, turns=True, calm=True, build=0.0), hall=2.4,
                            seconds=150),
    # a carol as a church sings it (arrange_church), in a cathedral's 4.5 s hall
    # whose lows sound alike on both sides (TOGETHER)
    "church-organ": Style(lambda arr: arrange_church(arr, bell="tubular"), tempo=0.8, breath=0.85, hall=4.5,
                          seconds=150, harmony="chorale", together=TOGETHER, sway=SWAY),
    "church-organ-plain": Style(lambda arr: arrange_church(arr, bell="tubular"), tempo=0.8, breath=0.85, hall=4.5,
                                seconds=150, together=TOGETHER, sway=SWAY),
    "church-choir": Style(lambda arr: arrange_church(arr, choir="choir"), tempo=0.8, breath=0.85, hall=4.5,
                          seconds=150, harmony="chorale", together=TOGETHER, sway=SWAY),
    "church-festive": Style(lambda arr: arrange_church(arr, choir="choir", festive=True), tempo=0.8, breath=0.85,
                            hall=4.5, seconds=150, harmony="chorale", together=TOGETHER, sway=SWAY),
    "chapel": Style(lambda arr: arrange_church(arr, choir="oohs", chapel=True, bell=None), tempo=0.75, breath=0.85,
                    hall=2.6, seconds=150, harmony="chorale", together=TOGETHER, sway=SWAY),
}
# The church styles closer by, as the user asked ("no big hall"): each in the
# small room ballad and pulse are played in (0.8 s, sends at 0.45 times),
# the rest as it is.
for _name in ("church-organ", "church-organ-plain", "church-choir", "church-festive", "chapel"):
    STYLES[f"{_name}-near"] = dataclasses.replace(STYLES[_name], hall=0.8, wet=0.45)
# Easier to listen to, on a phone too (arrange_church_piano, arrange_church_clear), close by.
STYLES["church-piano-near"] = dataclasses.replace(STYLES["church-organ-near"], arrange=arrange_church_piano,
                                                  piano=GENTLE_PIANO)
STYLES["church-organ-clear-near"] = dataclasses.replace(STYLES["church-organ-near"], arrange=arrange_church_clear)
# The clear organ joined by other instruments and humming voices, as the user
# asked (arrange_church_ensemble): the instruments forward, or the voices.
STYLES["church-organ-ensemble-near"] = dataclasses.replace(STYLES["church-organ-near"],
                                                           arrange=arrange_church_ensemble)
STYLES["church-organ-hum-near"] = dataclasses.replace(STYLES["church-organ-near"],
                                                      arrange=lambda arr: arrange_church_ensemble(arr, hum=True))
# That organ softer and more relaxing, as the user asked ("too heavy"): its
# flutes, or the small Renaissance organ, swelling with each phrase, and a
# little slower (0.74 of the carol's tempo, the other church styles 0.8).
STYLES["church-organ-soft-near"] = dataclasses.replace(
    STYLES["church-organ-near"], arrange=lambda arr: arrange_church_ensemble(arr, organ="flutes"), tempo=0.74)
STYLES["church-organ-small-near"] = dataclasses.replace(
    STYLES["church-organ-near"], arrange=lambda arr: arrange_church_ensemble(arr, organ="small"), tempo=0.74)
# Played as a person plays them (perform), as the user asked ("too even",
# lacking ease and softness): the felt piano, its left hand breathing with each
# phrase, and the soft-flute organ, its harp breathing too; each beside its
# earlier self (felt-4k, church-organ-soft-near) to compare.
FELT_PLAYER = Perform(rubato=0.10, swell=6.0, under=4.0, high=3.0, long=2.0, loose=0.5, ceiling=65)
HYMN_PLAYER = Perform(rubato=0.06, swell=4.0, under=4.0, high=0.0, long=0.0, loose=0.5)
STYLES["felt-4k-human"] = dataclasses.replace(
    STYLES["felt-4k"], arrange=lambda arr: arrange_felt(arr, breathing=True), perform=FELT_PLAYER)
STYLES["church-organ-soft-human-near"] = dataclasses.replace(
    STYLES["church-organ-soft-near"], perform=HYMN_PLAYER,
    arrange=lambda arr: arrange_church_ensemble(arr, organ="flutes", breathing=True))
# The earlier styles the user keeps, played so too, as the user asked: pulse
# and ballad (their middle hand and harp breathing, the tune in its bright
# samples as before, the tempo swinging a little less: their pulse is their
# own), the orchestra (its harp breathing), the hymn on the piano and on the
# small organ.
POP_PLAYER = Perform(rubato=0.07, swell=6.0, under=4.0, high=3.0, long=2.0, loose=0.5)
# (the hymn's piano no louder at its peaks than before: shaped wider, its Silent
# Night peaked enough that the mixer left it 2.4 dB quieter rather than limit it)
HYMN_PIANO_PLAYER = Perform(rubato=0.06, swell=4.0, under=4.0, high=3.0, long=2.0, loose=0.5, ceiling=80)
STYLES["pulse-human"] = dataclasses.replace(
    STYLES["pulse"], arrange=lambda arr: arrange_pulse(arr, breathing=True), perform=POP_PLAYER)
STYLES["ballad-human"] = dataclasses.replace(
    STYLES["ballad"], arrange=lambda arr: arrange_ballad(arr, breathing=True), perform=POP_PLAYER)
STYLES["orchestra-gentle-human"] = dataclasses.replace(
    STYLES["orchestra-gentle"], perform=Perform(rubato=0.08, loose=0.5),
    arrange=lambda arr: arrange_orchestra(arr, turns=True, calm=True, build=0.4, breathing=True))
STYLES["church-piano-human-near"] = dataclasses.replace(STYLES["church-piano-near"], perform=HYMN_PIANO_PLAYER)
STYLES["church-organ-small-human-near"] = dataclasses.replace(
    STYLES["church-organ-small-near"], perform=HYMN_PLAYER,
    arrange=lambda arr: arrange_church_ensemble(arr, organ="small", breathing=True))
# Simulated instruments in place of recorded ones, as the user asked to try
# (made by sfizz's oscillators, instruments/*.sfz), each on a player's style:
# the soft organ and its bell, the Rhodes of ballad, the felt piano.
STYLES["church-organ-synth-human-near"] = dataclasses.replace(
    STYLES["church-organ-soft-human-near"],
    arrange=lambda arr: arrange_church_ensemble(arr, organ="synth", breathing=True, bell="bell-synth"))
STYLES["ballad-synth-human"] = dataclasses.replace(STYLES["ballad-human"], piano="ep-synth")
STYLES["felt-synth-human"] = dataclasses.replace(STYLES["felt-4k-human"], piano="felt-synth")


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


def write_part(part: Part, tempos: list, path: Path, meter: tuple = (3, 2), program: tuple | None = None) -> int:
    """One part as a MIDI file; program (bank, program) selects a soundfont's
    preset (GeneralUser GS) before the first note. Returns how many repeated
    notes were untangled."""
    notes, changed = untangle(part.notes)
    messages = []
    if program:
        messages += [(0, -1, mido.Message("control_change", control=0, value=program[0])),
                     (0, -1, mido.Message("program_change", program=program[1]))]
    for tick, note, velocity, length in notes:
        messages.append((tick + length, 0, mido.Message("note_off", note=note, velocity=0)))
        messages.append((tick, 2, mido.Message("note_on", note=note, velocity=velocity)))
    for tick, value in part.pedal:
        messages.append((max(0, tick), 1, mido.Message("control_change", control=64, value=value)))
    for tick, value in part.expression:
        messages.append((max(0, tick), 1, mido.Message("control_change", control=11, value=value)))
    for tick, value in part.bends:
        messages.append((max(0, tick), 1, mido.Message("pitchwheel", pitch=value)))
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
    parser.add_argument("--styles", nargs="+", default=["ballad", "pulse"], choices=list(STYLES))
    parser.add_argument("--pianos", nargs="+", choices=["piano", "grand", "knight", "yamaha", "ep"],
                        help="play the piano styles on these instead of each style's own (a piece each; one "
                             "on another piano than its style's ends in -piano, -grand, -knight, -yamaha or -ep)")
    args = parser.parse_args()
    for piano_choice, name, style_name in itertools.product(args.pianos or [None], args.songs, args.styles):
        song, style = SONGS[name], STYLES[style_name]
        song = reharmonize(song) if style.reharm else song
        if style.harmony == "chorale":
            song = dataclasses.replace(song, chords=chorale.harmonize(song))
        piano = piano_choice or style.piano
        tempo = min(1.0, style.bpm / song.bpm) if style.bpm else style.tempo
        verses = style.verses or song.verses or (
            max(2, min(6, math.ceil(style.seconds / (song.seconds() / tempo)))) if style.seconds
            else 3 if style.repeat_short and song.seconds() < 40 else 2)
        arr = Arrangement(song, verses, tempo, style.breath, free_intro=style.free_intro, piano=piano,
                          intro=style.intro)
        if style.perform:
            arr.loose = style.perform.loose
        style.arrange(arr)
        if style.perform:
            perform(arr, style.perform)
        if piano != style.piano and all(p.instrument != piano for p in arr.parts.values()):
            continue  # a style without a piano (bells, orchestra) is played once
        if style.piano_tone:
            arr.parts["piano"].tone.update(style.piano_tone)
        if style.piano_reverb is not None:
            arr.parts["piano"].reverb = style.piano_reverb
        folder = args.out / (f"{name}-{style_name}" + (f"-{piano}" if piano != style.piano else ""))
        folder.mkdir(parents=True, exist_ok=True)
        sheet, untangled = [], 0
        for part_name, part in arr.parts.items():
            library, sfz = INSTRUMENTS[part.instrument]
            preset = tuple(int(x) for x in sfz.partition("#")[2].split(":")) if "#" in sfz else None
            untangled += write_part(part, arr.tempos, folder / f"{part_name}.mid", arr.meter, preset)
            sheet.append({"part": part_name, "library": library, "sfz": sfz, "role": part.role,
                          "gain_db": ROLES[part.role], "pan": part.pan, "reverb": part.reverb,
                          "tone": part.tone, "notes": len(part.notes)})
        hall = ({"rt60": style.hall} | ({"wet": style.wet} if style.wet != 1.0 else {})
                | ({"together": style.together} if style.together else {})
                | ({"sway": style.sway} if style.sway else {}))
        mix = {"hall": hall, "parts": sheet, "master": style.master}
        if style.noise_db is not None:
            mix["noise"] = {"db": style.noise_db}
        (folder / "mix.json").write_text(json.dumps(mix, indent=2))
        print(f"{folder.name}: {arr.bpm:.0f} bpm, {len(arr.verses)} verses, {len(sheet)} parts "
              f"({', '.join(p['part'] for p in sheet)}), {arr.seconds(0, arr.end + 2 * arr.bar):.0f} s, "
              f"{untangled} repeated notes untangled")


if __name__ == "__main__":
    main()
