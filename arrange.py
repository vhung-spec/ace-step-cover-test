"""Arranges the test's carols for real instrument samples, without any AI
model: one MIDI file per instrument, in three styles, plus mix.json (the
instrument, role and stereo position of each part) for render_samples.py:

    python arrange.py out/sampled [--songs wish silent-night] [--styles piano bells orchestra]

The carols are the public-domain melodies and chords of make_source.py. Every
style plays an intro (the last phrase, an octave up), two verses (the second
fuller) and a held last chord, slowing down over the last two bars. The parts
are written from the same chords, beat by beat, so they always agree:
- piano: the melody over a flowing left hand, with sustain pedal; in the
  second verse a chord tone a third to a sixth under the longer notes sings
  with the melody;
- bells: glockenspiel, then hand chimes and vibraphone on the melody, over a
  harp, a soft string pad in the second verse, mark tree and sleigh bells;
- orchestra: flute, then violins on the melody, over violas, cellos, harp,
  and in the second verse basses, horns, glockenspiel, sleigh bells, timpani.
Instruments come from two CC0 sample libraries: VS Chamber Orchestra 2
Community Edition ("vsco", SFZ branch) and the Versilian Community Sample
Library ("vcsl", sfz branch).
"""

import argparse
import json
import random
from dataclasses import dataclass
from pathlib import Path

import mido

import make_source

TICKS = 480  # per quarter note
EIGHTH = TICKS // 2
BAR = 3 * TICKS  # both carols are in 3/4

# Root pitch class, and the chord's intervals above the root.
CHORDS = {"C": (0, (0, 4, 7)), "F": (5, (0, 4, 7)), "G": (7, (0, 4, 7)), "G7": (7, (0, 4, 7, 10)),
          "D7": (2, (0, 4, 7, 10)), "E7": (4, (0, 4, 7, 10)), "Am": (9, (0, 3, 7))}

# Sample libraries: (library, SFZ file in it).
INSTRUMENTS = {
    "piano": ("vcsl", "Chordophones/Zithers/Grand Piano, Steinway B.sfz"),
    "glock": ("vcsl", "Idiophones/Struck Idiophones/Glockenspiel.sfz"),
    "chimes": ("vcsl", "Idiophones/Struck Idiophones/Hand Chimes.sfz"),
    "vibes": ("vcsl", "Idiophones/Struck Idiophones/Vibraphone - Soft Mallets.sfz"),
    "harp": ("vcsl", "Chordophones/Composite Chordophones/Concert Harp.sfz"),
    "marktree": ("vcsl", "Idiophones/Struck Idiophones/Mark Trees.sfz"),
    "sleigh": ("vcsl", "Idiophones/Struck Idiophones/Sleigh Bells.sfz"),
    "tubular": ("vcsl", "Idiophones/Struck Idiophones/Tubular Bells 2.sfz"),
    "flute": ("vsco", "FluteSusVib.sfz"),
    "violins": ("vsco", "ViolinEnsSusVib.sfz"),
    "violas": ("vsco", "ViolaEnsSusVib.sfz"),
    "violas-soft": ("vsco", "ViolaEnsSusVib-Quiet.sfz"),
    "cellos": ("vsco", "CelloEnsSusVib.sfz"),
    "cellos-soft": ("vsco", "CelloEnsSusVib-Quiet.sfz"),
    "basses": ("vsco", "ContrabassSusVB-Quiet.sfz"),
    "horns": ("vsco", "FHornSus.sfz"),
    "orch-glock": ("vsco", "Glockenspiel.sfz"),
    "timpani": ("vsco", "TimpaniRolls.sfz"),
}
# How loud each kind of part sits against the melody (dB of its loudness when playing).
ROLES = {"melody": 0.0, "double": -7.0, "pad": -9.0, "bass": -7.0, "harp": -5.0, "piano": 0.0,
         "sparkle": -12.0, "bells": -6.0, "drum": -12.0}


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


class Part:
    """The notes of one instrument: (tick, note, velocity, length) and pedal changes."""

    def __init__(self, instrument: str, role: str, pan: float, reverb: float = 0.3):
        self.instrument, self.role, self.pan, self.reverb = instrument, role, pan, reverb
        self.notes, self.pedal = [], []

    def add(self, tick: int, note: int, velocity: int, length: int) -> None:
        self.notes.append((max(0, int(tick)), int(note), max(1, min(127, int(velocity))), max(30, int(length))))


class Arrangement:
    """The timeline every part follows: intro, two verses, the last chord."""

    def __init__(self, song: Song, seed: int = 7):
        self.song, self.rng = song, random.Random(seed)
        self.intro = song.intro_bars * BAR
        self.verse = len(song.chords) * BAR
        self.verses = [self.intro + k * self.verse for k in range(2)]  # each verse's first downbeat
        self.end = self.verses[1] + self.verse  # the last note's bar ends here...
        self.length = self.end + BAR  # ...and one more bar lets it ring
        self.parts: dict[str, Part] = {}

    def part(self, name: str, instrument: str, role: str, pan: float, reverb: float = 0.3) -> Part:
        if name not in self.parts:
            self.parts[name] = Part(instrument, role, pan, reverb)
        return self.parts[name]

    def jitter(self, ticks: int = 8) -> int:  # a player is never exactly on the grid
        return self.rng.randint(-ticks, ticks)

    def chord_at(self, tick: int) -> str:
        """The chord sounding at a tick: the intro uses the tune's last bars, the
        ring-out bar the first chord (the tonic)."""
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
        (the last bars an octave up, verse -1), then both verses."""
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
                if verse == 0 and start + length >= self.verse and song.pickup:
                    length -= song.pickup * EIGHTH  # room for the second verse's pickup
                if verse == 1 and index == len(tune) - 1:
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


def third(chord: str) -> int:
    return CHORDS[chord][1][1]


def triad_notes(chord: str, low: int, high: int) -> list:
    root, intervals = CHORDS[chord]
    classes = {(root + i) % 12 for i in intervals[:3]}
    return [n for n in range(low, high + 1) if n % 12 in classes]


def harmony_below(chord: str, note: int) -> int | None:
    """The chord tone a third to a sixth under a melody note, to sing with it."""
    below = [n for n in chord_notes(chord, note - 9, note - 3)]
    return below[-1] if below and below[-1] >= 59 else None


def shape(position: float) -> float:
    """Phrase dynamics: 0 at the start and end of a verse, 1 in the middle."""
    return 1 - abs(position - 0.5) * 2


def flowing_bass(arr: Arrangement, part: Part, start: int, end: int, velocity: int, octave: int = 0,
                 verse_peak: int = 6) -> None:
    """A left hand / harp in 3/4: the bass on the beat, then the chord broken
    upwards and back in eighths, beat by beat with that beat's chord."""
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
            accent = 8 if beat == 0 and i == 0 else 0
            part.add(tick + i * EIGHTH + arr.jitter(), note, velocity + accent + arr.rng.randint(-3, 3),
                     EIGHTH * (3 if i == 0 else 2))


def pedal_by_chord(arr: Arrangement, part: Part, start: int, end: int) -> None:
    for tick, length, _ in arr.chord_spans(start, end):
        part.pedal.append((tick + 40, 127))
        part.pedal.append((tick + length - 25, 0))


def arrange_piano(arr: Arrangement) -> None:
    piano = arr.part("piano", "piano", "piano", 0.0, reverb=0.25)
    for tick, note, length, verse, position in arr.melody():
        if verse < 0:
            velocity = 52 + 6 * position
        elif verse == 0:
            velocity = 66 + 12 * shape(position)
        else:
            velocity = 80 + 14 * shape(position)
        piano.add(tick + arr.jitter(5), note, velocity + arr.rng.randint(-3, 3), length - 15)
        if verse == 1 and (length >= TICKS or tick % BAR == 0):  # the second verse sings in thirds and sixths
            second = harmony_below(arr.chord_at(tick), note)
            if second is not None:
                piano.add(tick + arr.jitter(5), second, velocity - 18, length - 15)
    flowing_bass(arr, piano, 0, arr.verses[0], 40)
    flowing_bass(arr, piano, arr.verses[0], arr.verses[1], 48)
    flowing_bass(arr, piano, arr.verses[1], arr.end, 56)
    pedal_by_chord(arr, piano, 0, arr.end)
    for note, velocity in ((36, 60), (48, 54), (55, 50), (64, 50), (72, 46)):  # the last chord, rolled
        piano.add(arr.end + (note - 36) * 3, note, velocity, BAR * 2)
    piano.pedal.append((arr.end + 20, 127))


def arrange_bells(arr: Arrangement) -> None:
    glock = arr.part("glock", "glock", "melody", 0.25)
    chimes = arr.part("chimes", "chimes", "melody", 0.2)
    vibes = arr.part("vibes", "vibes", "double", -0.25)
    harp = arr.part("harp", "harp", "harp", -0.4)
    for tick, note, length, verse, position in arr.melody():
        if verse <= 0:
            glock.add(tick + arr.jitter(4), note + (0 if verse < 0 else 12), 70 + 10 * shape(position), length)
        else:
            chimes.add(tick + arr.jitter(4), note + 12, 78 + 10 * shape(position), length)
            vibes.add(tick + arr.jitter(4), note, 58 + 8 * shape(position), length)
    flowing_bass(arr, harp, 0, arr.end, 52, octave=12)
    pad_strings(arr, arr.verses[1], arr.end, soft=True)
    effects(arr, sleigh_from=arr.verses[1])


def pad_strings(arr: Arrangement, start: int, end: int, soft: bool, velocity: int = 48) -> None:
    """Sustained chords: the bass in the cellos, the third and fifth in the violas."""
    cellos = arr.part("cellos", "cellos-soft" if soft else "cellos", "bass", 0.35, reverb=0.35)
    violas = arr.part("violas", "violas-soft" if soft else "violas", "pad", 0.2, reverb=0.35)
    for tick, length, chord in arr.chord_spans(start, end):
        cellos.add(tick + arr.jitter(), bass_note(chord), velocity + 6, length + 30)
        upper = [n for n in chord_notes(chord, 55, 67) if n % 12 != CHORDS[chord][0]][:2]
        for note in upper:
            violas.add(tick + arr.jitter(), note, velocity, length + 30)


def effects(arr: Arrangement, sleigh_from: int | None = None) -> None:
    marktree = arr.part("marktree", "marktree", "sparkle", -0.5, reverb=0.4)
    tubular = arr.part("tubular", "tubular", "bells", 0.1, reverb=0.4)
    marktree.add(0, 60, 70, BAR * 2)  # rising shimmer into the intro
    marktree.add(arr.verses[1] - TICKS, 62, 70, BAR * 2)  # and into the second verse
    marktree.add(arr.end, 61, 64, BAR * 2)  # falling over the last chord
    for note in (72, 67):
        tubular.add(arr.end + arr.jitter(), note, 76, BAR * 2)
    if sleigh_from is not None and arr.song.name == "wish":  # a sleigh ride needs a lively tune
        sleigh = arr.part("sleigh", "sleigh", "drum", 0.4, reverb=0.2)
        for tick in range(sleigh_from, arr.end, TICKS):
            beat = tick % BAR // TICKS
            sleigh.add(tick + arr.jitter(6), 60, 70 if beat == 0 else 52, TICKS)


def arrange_orchestra(arr: Arrangement) -> None:
    flute = arr.part("flute", "flute", "melody", -0.15)
    violins = arr.part("violins", "violins", "melody", -0.35, reverb=0.35)
    glock = arr.part("glock", "orch-glock", "double", 0.3)
    last_phrase = arr.verses[1] + arr.verse - 2 * BAR * (1 if arr.song.name == "wish" else 4)
    for tick, note, length, verse, position in arr.melody():
        if verse < 0:
            flute.add(tick + arr.jitter(4), note, 62, length - 10)
            glock.add(tick + arr.jitter(4), note, 56, length)
        elif verse == 0:
            flute.add(tick + arr.jitter(4), note + 12, 64 + 12 * shape(position), length - 10)
        else:
            violins.add(tick + arr.jitter(4), note, 76 + 14 * shape(position), length + 20)
            if tick >= last_phrase:
                glock.add(tick + arr.jitter(4), note + 12, 58, length)
    harp = arr.part("harp", "harp", "harp", -0.45)
    flowing_bass(arr, harp, 0, arr.verses[1], 56, octave=12)
    flowing_bass(arr, harp, arr.verses[1], arr.end, 46, octave=12)
    pad_strings(arr, arr.verses[0], arr.verses[1], soft=False, velocity=44)
    pad_strings(arr, arr.verses[1], arr.end + BAR, soft=False, velocity=70)
    basses = arr.part("basses", "basses", "bass", 0.45, reverb=0.35)
    horns = arr.part("horns", "horns", "pad", 0.15, reverb=0.4)
    for tick, length, chord in arr.chord_spans(arr.verses[1], arr.end + BAR):
        low = bass_note(chord) - 12  # an octave under the cellos, but not below E1
        basses.add(tick + arr.jitter(), low if low >= 28 else low + 12, 70, length + 30)
        for note in triad_notes(chord, 53, 65)[:2]:
            horns.add(tick + arr.jitter(), note, 55, length + 30)
    timpani = arr.part("timpani", "timpani", "drum", 0.0, reverb=0.4)
    timpani.add(arr.end - BAR, 48, 70, BAR * 2)  # a roll under the last chord
    effects(arr, sleigh_from=arr.verses[1])


STYLES = {"piano": arrange_piano, "bells": arrange_bells, "orchestra": arrange_orchestra}


def tempo_map(arr: Arrangement) -> list:
    """(tick, bpm): a little breath on the last beat of every four-bar phrase,
    as a player would take, and slowing over the last two bars to the held chord."""
    bpm = arr.song.bpm
    changes = [(0, bpm)]
    slow_from = arr.end - 2 * BAR
    for downbeat in arr.verses:
        for bar in range(3, len(arr.song.chords), 4):
            last_beat = downbeat + bar * BAR + 2 * TICKS
            if last_beat + TICKS <= slow_from:
                changes += [(last_beat, bpm * 0.92), (last_beat + TICKS, bpm)]
    for beat in range(7):
        changes.append((slow_from + beat * TICKS, bpm * (1 - 0.05 * (beat + 1))))
    return sorted(changes)


def write_part(part: Part, tempos: list, path: Path) -> None:
    messages = []
    for tick, note, velocity, length in part.notes:
        messages.append((tick + length, 0, mido.Message("note_off", note=note, velocity=0)))
        messages.append((tick, 2, mido.Message("note_on", note=note, velocity=velocity)))
    for tick, value in part.pedal:
        messages.append((max(0, tick), 1, mido.Message("control_change", control=64, value=value)))
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
    track.append(mido.MetaMessage("end_of_track", time=TICKS))
    midi.save(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--songs", nargs="+", default=list(SONGS), choices=list(SONGS))
    parser.add_argument("--styles", nargs="+", default=list(STYLES), choices=list(STYLES))
    args = parser.parse_args()
    for name in args.songs:
        for style in args.styles:
            arr = Arrangement(SONGS[name])
            STYLES[style](arr)
            folder = args.out / f"{name}-{style}"
            folder.mkdir(parents=True, exist_ok=True)
            tempos = tempo_map(arr)
            sheet = []
            for part_name, part in arr.parts.items():
                write_part(part, tempos, folder / f"{part_name}.mid")
                library, sfz = INSTRUMENTS[part.instrument]
                sheet.append({"part": part_name, "library": library, "sfz": sfz, "role": part.role,
                              "gain_db": ROLES[part.role], "pan": part.pan, "reverb": part.reverb,
                              "notes": len(part.notes)})
            (folder / "mix.json").write_text(json.dumps(sheet, indent=2))
            seconds = mido.MidiFile(folder / f"{next(iter(arr.parts))}.mid").length
            print(f"{folder.name}: {len(sheet)} parts ({', '.join(p['part'] for p in sheet)}), {seconds:.0f} s")


if __name__ == "__main__":
    main()
