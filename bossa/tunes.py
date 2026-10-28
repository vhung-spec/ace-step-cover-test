"""The tunes the bossa nova sketches play, written as text so a person (or a
language model) can read and write them:

- a melody is notes and rests with their lengths in eighths, "C5:3 A4:1 r:4",
  bars split by "|" (only for reading: the lengths decide where bars fall);
  a sharp is "F#4", a flat "Bb4";
- the chords are one bar per item, one to four names a bar ("Gm9 C13" is two
  beats each), with the kinds in arrange_bossa.KINDS (maj7, m9, 7b9, 13...).

Café da Tarde and Chuva Mansa are original tunes written for these sketches
(AABA in F major; sixteen bars in D minor). Jingle Bells (James Lord
Pierpont, 1857) is in the public domain: its chorus as it is sung today, with
a bossa nova reharmonisation of our own.
"""

from dataclasses import dataclass, field

STEPS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def pitch(name: str) -> int:
    """MIDI note of a name like C4 (60), F#3, Bb4."""
    letter, rest = name[0].upper(), name[1:]
    shift = 0
    while rest[:1] in ("#", "b"):
        shift += 1 if rest[0] == "#" else -1
        rest = rest[1:]
    return 12 * (int(rest) + 1) + STEPS[letter] + shift


def melody(text: str) -> list:
    """[(MIDI note or None, eighths)] from "C5:3 A4:1 | r:4"."""
    notes = []
    for item in text.replace("|", " ").split():
        name, _, length = item.partition(":")
        notes.append((None if name.lower() == "r" else pitch(name), float(length)))
    return notes


def chords(bars: list, beats: int = 4) -> list:
    """One list of beat-by-beat chord names per bar, from "Gm9 C13"-style bars."""
    out = []
    for bar in bars:
        names = bar.split()
        if beats % len(names):
            raise ValueError(f"{bar!r}: {len(names)} chords do not split {beats} beats")
        out.append([name for name in names for _ in range(beats // len(names))])
    return out


@dataclass
class Tune:
    name: str
    title: str
    melody: list  # (note or None, eighths), from the first downbeat
    chords: list  # per bar, a chord name a beat
    bpm: float
    beats: int = 4
    about: str = ""
    sections: list = field(default_factory=list)  # (first bar, label), for the log


def check(tune: Tune) -> None:
    total = sum(e for _, e in tune.melody)
    need = len(tune.chords) * tune.beats * 2
    if abs(total - need) > 1e-6:
        raise ValueError(f"{tune.name}: melody {total:g} eighths, chords need {need}")


CAFE_A1 = """
r:1 C5:1 A4:1 G4:1 A4:4 | r:1 D5:1 E5:2 D5:4 | C5:3 G4:1 E4:4 | r:2 F4:1 Ab4:1 B4:4 |
A4:3 Bb4:1 A4:2 G4:2 | r:1 E4:1 G4:1 A4:5 | C5:4 Eb5:4 | D5:3 C5:1 Bb4:2 G4:2 |"""
CAFE_A2 = """
r:1 C5:1 A4:1 G4:1 A4:4 | r:1 D5:1 E5:2 D5:4 | C5:3 G4:1 E4:4 | r:2 F4:1 Ab4:1 B4:4 |
A4:3 Bb4:1 A4:2 G4:2 | r:1 E4:1 G4:1 A4:5 | Bb4:3 A4:1 G4:2 Db5:2 | C5:6 r:2 |"""
CAFE_B = """
r:1 Eb5:1 D5:1 C5:1 Bb4:4 | A4:2 G4:2 A4:4 | r:1 D5:1 F5:3 D5:3 | Db5:4 C5:2 Bb4:2 |
C5:3 A4:1 E5:4 | Eb5:2 D5:2 C5:2 A4:2 | Bb4:3 A4:1 G4:4 | F4:4 E4:2 G4:2 |"""
CAFE_CHORDS_A1 = ["Fmaj9", "Bb7#11", "Am7", "Abdim7", "Gm9", "C13", "Fmaj7 D7b9", "Gm7 C7"]
CAFE_CHORDS_A2 = ["Fmaj9", "Bb7#11", "Am7", "Abdim7", "Gm9", "C13", "Gm7 C7b9", "Fmaj7"]
CAFE_CHORDS_B = ["Cm7", "F9", "Bbmaj7", "Bbm6", "Am7", "D7b9", "Gm9", "C7sus4 C7b9"]

CAFE = Tune(
    "cafe", "Café da Tarde",
    melody(CAFE_A1 + CAFE_A2 + CAFE_B + CAFE_A2),
    chords(CAFE_CHORDS_A1 + CAFE_CHORDS_A2 + CAFE_CHORDS_B + CAFE_CHORDS_A2),
    bpm=128, about="original (Bokin sketches, 2026), AABA in F major",
    sections=[(0, "A"), (8, "A"), (16, "B"), (24, "A")])

CHUVA = Tune(
    "chuva", "Chuva Mansa",
    melody("""
r:2 A4:1 C5:1 E5:4 | D5:3 C5:1 A4:4 | G4:2 Bb4:2 D5:4 | C#5:2 F5:2 E5:4 |
r:1 F5:1 E5:1 D5:1 A4:4 | E5:3 D5:1 B4:4 | Bb4:2 A4:2 F4:4 | r:2 E4:1 G4:1 Bb4:2 A4:2 |
A4:3 G4:1 E4:4 | r:1 F4:1 A4:1 D5:1 C5:4 | Bb4:3 G4:1 E4:4 | r:2 Bb4:2 C#5:2 E5:2 |
F5:4 E5:4 | D5:3 Bb4:1 G4:4 | G4:2 Bb4:2 C#5:2 Bb4:2 | D5:6 r:2 |"""),
    chords(["Dm9", "Bbmaj7", "Em7b5", "A7b13", "Dm7", "G13", "Gm9", "C13",
            "Fmaj7", "Bbmaj9", "Em7b5", "A7b9", "Dm9", "Ebmaj7", "Em7b5 A7b9", "Dm69"]),
    bpm=104, about="original (Bokin sketches, 2026), sixteen bars in D minor",
    sections=[(0, "A"), (8, "B")])

JINGLE = Tune(
    "jingle", "Jingle Bells (bossa)",
    melody("""
A4:2 A4:2 A4:4 | A4:2 A4:2 A4:4 | A4:2 C5:2 F4:3 G4:1 | A4:8 |
Bb4:2 Bb4:2 Bb4:3 Bb4:1 | Bb4:2 A4:2 A4:2 A4:1 A4:1 | A4:2 G4:2 G4:2 A4:2 | G4:4 C5:4 |
A4:2 A4:2 A4:4 | A4:2 A4:2 A4:4 | A4:2 C5:2 F4:3 G4:1 | A4:8 |
Bb4:2 Bb4:2 Bb4:3 Bb4:1 | Bb4:2 A4:2 A4:2 A4:1 A4:1 | C5:2 C5:2 Bb4:2 G4:2 | F4:8 |"""),
    chords(["Fmaj7", "Dm9", "Gm9 C9sus4", "Am7 D7b9", "Bbmaj7", "Gm9 D7b9", "Gm9 C13", "Gm7 C7b9",
            "Fmaj7", "Dm9", "Gm9 C9sus4", "Am7 D7b9", "Bbmaj7", "Gm9 D7b9", "C9sus4 C7b9", "F69"]),
    bpm=132, about="James Lord Pierpont, 1857 (public domain); the chords are our own",
    sections=[(0, "chorus")])

TUNES = {t.name: t for t in (CAFE, CHUVA, JINGLE)}
for _tune in TUNES.values():
    check(_tune)
