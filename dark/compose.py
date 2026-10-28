"""Dark piano: original pieces written as data (dark/pieces/*.json), arranged
for sampled instruments: one MIDI file per instrument and a mix.json per
piece, for render_samples.py to play and mix, as arrange.py does for the
carols:

    python dark/compose.py out/dark [--pieces dem-mua bong-ma ...]

A piece is a short score, the shape an AI composer is asked to write:

    {"title": "...", "bpm": 66, "beats": 4, "piano": "felt", "bass_low": 33,
     "room": {"rt60": 1.0, "wet": 0.5}, "noise_db": -30,
     "sections": [{"bars": 8, "chords": "Dm | Bb | F | C/E | ...",
                   "melody": "r:1 A4:1 D5:1.5 E5:0.5 | F5:3 ...",
                   "texture": "arp", "dyn": 0.4, "layers": ["drone", "cello"]}]}

- chords: bar by bar, split by |; a bar may hold several chords, each its
  share of the bar, or as many beats as `Dm:3 C:1` says. A chord is a root
  (C, F#, Bb), a kind (m, 5, sus2, sus4, 7, m7, maj7, m6, add9, madd9, m9,
  dim, dim7, m7b5, aug, 7b9, mmaj7) and a bass under it (/E);
- melody: notes (A4, Bb3, F#5; C4 is middle C) or rests (r), each with its
  length in beats; `+` joins notes struck together (D5+F5:2); | between bars
  is checked against the bar's length;
- bass_low: the lowest note the left hand's bass may take (33, A1; 40, E2,
  keeps the piano out of the deep bass); piano_tone changes the piano's tone
  for render_samples.py (lowpass, lowpass_order, width: above 1 widens it);
- hold: the longest (beats) an accompanying note is held; pedal_beats: the
  pedal taken again this often within a chord (else once a chord); lh_soft:
  the left hand this much softer (velocity), all to keep it light and clear;
- texture, the piano's left hand: arp (broken chords in eighths, up and
  back from a deep bass), flow (lighter: a bass held under two tones above
  it, rocking in eighths), ostinato (three tones of the chord circling in
  eighths in the middle of the keyboard, a low toll on each bar), blocks (the
  chord rolled from a deep octave and held), sparse (a deep note, a soft
  rolled chord after it, an inner tone later in the bar), pulse (a low
  octave beating as a heart does), none;
- dyn: 0 (barely touched) to 1 (fully); the melody rises and falls with each
  phrase within it;
- layers: drone (a low tonic and fifth from sfizz's own oscillators,
  instruments/drone.sfz), cello (the chords' bass line, bowed), cello-melody
  (the tune an octave down), strings (soft violas and cellos holding the
  chords), basses (the deepest roots), violin (a solo violin on the tune),
  octave (the piano doubling the tune an octave down).

The piano breathes on the last beat of every four bars, a section marked
rit slows over its last two bars, and the piece slows into its last chord,
held a bar longer, rolled from the bass. Instruments: VCSL (CC0) for the
pianos, VSCO 2 CE (CC0) for the strings, fetched when rendering
(fetch_samples.py), never kept here.
"""

import argparse
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arrange import TONES, write_part  # noqa: E402  (the repository root's arranger)

TICKS = 480
EIGHTH = TICKS // 2
HOLD_SECONDS = 4.2  # sustained samples are not looped: a longer note is struck again
PIECES = Path(__file__).parent / "pieces"

NOTE_CLASSES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
KINDS = {"": (0, 4, 7), "m": (0, 3, 7), "5": (0, 7), "sus2": (0, 2, 7), "sus4": (0, 5, 7), "7": (0, 4, 7, 10),
         "m7": (0, 3, 7, 10), "maj7": (0, 4, 7, 11), "m6": (0, 3, 7, 9), "add9": (0, 4, 7, 14),
         "madd9": (0, 3, 7, 14), "m9": (0, 3, 7, 10, 14), "dim": (0, 3, 6), "dim7": (0, 3, 6, 9),
         "m7b5": (0, 3, 6, 10), "aug": (0, 4, 8), "7b9": (0, 4, 7, 10, 13), "mmaj7": (0, 3, 7, 11),
         "7sus4": (0, 5, 7, 10)}

# Instrument: (library, SFZ file, tone for render_samples.py).
INSTRUMENTS = {
    # VCSL's Yamaha upright: the user's choice for gentle piano, dark and clean.
    "upright": ("vcsl", "Chordophones/Zithers/Upright Piano, Yamaha.sfz", dict(TONES["yamaha"])),
    # the same, as the felt-hammered pianos sound: its highs rolled off
    "felt": ("vcsl", "Chordophones/Zithers/Upright Piano, Yamaha.sfz", TONES["yamaha"] | {"lowpass": 1100}),
    # the Steinway B, its highs open (fetch_samples.py hushes its hiss)
    "grand": ("vcsl", "Chordophones/Zithers/Grand Piano, Steinway B.sfz", dict(TONES["grand"])),
    "cellos": ("vsco", "CelloEnsSusVib-Quiet.sfz", dict(TONES["cellos"])),
    "violas": ("vsco", "ViolaEnsSusVib-Quiet.sfz", dict(TONES["violas"])),
    "basses": ("vsco", "ContrabassSusVB-Quiet.sfz", dict(TONES["basses"])),
    "violin": ("vsco", "SViolinVib-Quiet.sfz", dict(TONES["violins"]) | {"width": 0.5}),
    "drone": ("local", "drone.sfz", {"highpass": 30}),
}
# How loud each part sits against the piano (dB while it plays).
ROLES = {"piano": 0.0, "bass": -9.0, "melody2": -6.0, "pad": -12.0, "low": -13.0, "drone": -15.0}


def note_number(name: str) -> int:
    match = re.fullmatch(r"([A-G])([#b]?)(-?\d)", name)
    if not match:
        raise ValueError(f"not a note: {name}")
    letter, accidental, octave = match.groups()
    return 12 * (int(octave) + 1) + NOTE_CLASSES[letter] + {"#": 1, "b": -1, "": 0}[accidental]


def chord(name: str) -> tuple:
    """(bass pitch class, pitch classes of the chord, root pitch class)."""
    name, _, bass = name.partition("/")
    match = re.fullmatch(r"([A-G][#b]?)(.*)", name)
    if not match or match.group(2) not in KINDS:
        raise ValueError(f"not a chord: {name}")
    root = note_number(match.group(1) + "4") % 12
    tones = [(root + i) % 12 for i in KINDS[match.group(2)]]
    return (note_number(bass + "4") % 12 if bass else root), tones, root


def above(pitch_class: int, low: int) -> int:
    """The lowest note of a pitch class at or above low."""
    return low + (pitch_class - low) % 12


class Part:
    def __init__(self, instrument: str, role: str, pan: float, reverb: float):
        self.instrument, self.role, self.pan, self.reverb = instrument, role, pan, reverb
        self.tone = dict(INSTRUMENTS[instrument][2])
        self.notes, self.pedal, self.expression, self.bends = [], [], [], []

    def add(self, tick: float, note: int, velocity: float, length: float) -> None:
        self.notes.append((max(0, int(tick)), int(note), max(1, min(127, int(velocity))), max(30, int(length))))


class Piece:
    def __init__(self, score: dict, seed: int = 7):
        self.score, self.rng = score, random.Random(seed)
        self.beats = score.get("beats", 4)
        self.bar = self.beats * TICKS
        self.bpm = score["bpm"]
        self.parts: dict[str, Part] = {}
        self.spans, self.tune, self.sections = [], [], []  # (tick, length, chord), (tick, notes, length)
        tick = 0
        for number, section in enumerate(score["sections"]):
            start = tick
            bars = [b.strip() for b in section["chords"].split("|")]
            if len(bars) != section["bars"]:
                raise ValueError(f"section {number}: {len(bars)} bars of chords, not {section['bars']}")
            for bar in bars:
                names = bar.split()
                shares = [float(n.split(":")[1]) if ":" in n else None for n in names]
                left = self.beats - sum(s for s in shares if s)
                even = left / max(1, sum(1 for s in shares if s is None))
                at = tick
                for name, share in zip(names, shares):
                    length = round((share or even) * TICKS)
                    self.spans.append((at, length, name.split(":")[0]))
                    at += length
                if at != tick + self.bar:
                    raise ValueError(f"section {number}: chords of `{bar}` last {(at - tick) / TICKS} beats")
                tick += self.bar
            self.read_melody(section.get("melody", ""), start, section["bars"], number)
            self.sections.append((start, tick, section))
        self.end = tick
        self.tempos = self.tempo_map()

    def read_melody(self, text: str, start: int, bars: int, number: int) -> None:
        tick = start
        for index, bar in enumerate(text.split("|") if text.strip() else []):
            bar_start = tick
            for token in bar.split():
                pitches, _, beats = token.partition(":")
                length = round(float(beats or 1) * TICKS)
                if pitches != "r":
                    self.tune.append((tick, [note_number(p) for p in pitches.split("+")], length))
                tick += length
            if tick - bar_start != self.bar:
                raise ValueError(f"section {number}, bar {index + 1} of the melody: {(tick - bar_start) / TICKS} beats")
        if text.strip() and tick != start + bars * self.bar:
            raise ValueError(f"section {number}: the melody lasts {(tick - start) / self.bar} bars, not {bars}")

    def tempo_map(self) -> list:
        changes = [(0, self.bpm)]
        for start, end, section in self.sections:
            for bar in range(3, section["bars"], 4):
                last = start + (bar + 1) * self.bar - TICKS
                if last + TICKS < end or not section.get("rit"):
                    changes += [(last, self.bpm * 0.9), (last + TICKS, self.bpm)]
            if section.get("rit") or end == self.end:
                steps = 2 * self.beats
                deepest = 0.6 if end == self.end else 0.8
                for beat in range(steps):
                    changes.append((end - 2 * self.bar + beat * TICKS, self.bpm * (1 - (1 - deepest) * (beat + 1) / steps)))
                if end != self.end:
                    changes.append((end, self.bpm))
        changes.append((self.end, self.bpm * 0.5))  # the held last chord
        return sorted(dict(changes).items())

    def seconds(self, start: int, end: int) -> float:
        total, changes = 0.0, self.tempos + [(10 ** 9, 0)]
        for (tick, bpm), (following, _) in zip(changes, changes[1:]):
            overlap = min(end, following) - max(start, tick)
            if overlap > 0:
                total += overlap / TICKS * 60 / bpm
        return total

    def part(self, name: str, instrument: str, role: str, pan: float = 0.0, reverb: float = 0.35) -> Part:
        if name not in self.parts:
            self.parts[name] = Part(instrument, role, pan, reverb)
        return self.parts[name]

    def jitter(self, ticks: int = 8) -> int:
        return self.rng.randint(-ticks, ticks)

    def section_at(self, tick: int) -> dict:
        return next(s for start, end, s in self.sections if start <= tick < end)

    def tune_between(self, start: int, end: int) -> list:
        return [n for t, notes, length in self.tune for n in notes if t < end and t + length > start]

    def held(self, part: Part, tick: int, note: int, velocity: float, length: int) -> None:
        """A sustained note, struck again on a beat when longer than its sample."""
        end = tick + length
        while tick < end:
            piece = end - tick
            while piece > TICKS and self.seconds(tick, tick + piece) > HOLD_SECONDS:
                piece -= TICKS
            part.add(tick, note, velocity, piece + (40 if tick + piece < end else 0))
            tick += piece
            velocity *= 0.92


def phrase_shape(position: float) -> float:
    """-1 to 1 over a four-bar phrase: rising to its middle, falling after."""
    return 1 - abs(2 * position - 1) * 2


def play_melody(piece: Piece, piano: Part) -> None:
    for tick, notes, length in piece.tune:
        section = piece.section_at(tick)
        position = (tick % (4 * piece.bar)) / (4 * piece.bar)
        velocity = 40 + 42 * section.get("dyn", 0.4) + 6 * phrase_shape(position) + piece.jitter(3)
        late = 10 + piece.jitter(6)  # a little behind the beat, as a player lingers
        for k, note in enumerate(sorted(notes, reverse=True)):
            piano.add(tick + late + 12 * k, note, velocity - 6 * k, length)
        if "octave" in section.get("layers", []):
            piano.add(tick + late + 6, max(notes) - 12, velocity - 12, length)


def bass_note(name: str, low: int = 31) -> int:
    return above(chord(name)[0], low)


def left_hand(piece: Piece, piano: Part) -> None:
    previous = [57, 60, 64]
    for tick, length, name in piece.spans:
        section = piece.section_at(tick)
        texture, dyn = section.get("texture", "arp"), section.get("dyn", 0.4)
        velocity = 30 + 34 * dyn - piece.score.get("lh_soft", 0)
        hold = round(piece.score.get("hold", 99) * TICKS)  # the longest an accompanying note is held
        bass, tones, _ = chord(name)
        tune = piece.tune_between(tick, tick + length)
        ceiling = (min(tune) - 2) if tune else 72
        low = bass_note(name, piece.score.get("bass_low", 33))
        if texture == "arp":
            ladder = [low] + [n for n in range(low + 5, low + 24) if n % 12 in tones and n < ceiling]
            ladder = [ladder[0]] + [n for k, n in enumerate(ladder[1:]) if k == 0 or n - ladder[k] >= 3][:4]
            order = [0, 1, 2, 3, 4, 3, 2, 1] if piece.beats % 2 == 0 else [0, 1, 2, 3, 2, 1]
            for k in range(length // EIGHTH):
                step = order[k % len(order)] % len(ladder)
                accent = 8 if k == 0 else (3 if k % 2 == 0 else 0)
                piano.add(tick + k * EIGHTH + piece.jitter(), ladder[step], velocity + accent - 4 * (step > 2),
                          min(hold, length - k * EIGHTH))
        elif texture == "flow":
            ladder = [n for n in range(low + 5, low + 18) if n % 12 in tones and n < ceiling]
            ladder = [low] + [n for k, n in enumerate(ladder) if k == 0 or n - ladder[k - 1] >= 3][:2]
            order = [0, 1, 2, 1] if piece.beats % 2 == 0 else [0, 1, 2]
            for k in range(length // EIGHTH):
                step = order[k % len(order)] % len(ladder)
                piano.add(tick + k * EIGHTH + piece.jitter(), ladder[step], velocity + (6 if k == 0 else 0) - 3 * step,
                          length if k == 0 else min(hold, length - k * EIGHTH))
        elif texture == "ostinato":
            middle = voice(previous, tones, 52, min(72, ceiling))
            previous = middle
            order = [0, 1, 2, 1] if piece.beats % 2 == 0 else [0, 1, 2, 1, 2, 1]
            for k in range(length // EIGHTH):
                piano.add(tick + k * EIGHTH + piece.jitter(5), middle[order[k % len(order)]],
                          velocity - 4 + (5 if k % 2 == 0 else 0), EIGHTH * 2)
            if tick % piece.bar == 0:
                deep = bass_note(name, piece.score.get("bass_low", 33) - 5)
                piano.add(tick + piece.jitter(4), deep, velocity + 4, piece.bar)
                piano.add(tick + piece.jitter(4), deep + 12, velocity - 4, piece.bar)
        elif texture in ("blocks", "sparse"):
            middle = voice(previous, tones, 48, min(67, ceiling))
            previous = middle
            piano.add(tick + piece.jitter(4), low, velocity + 6, length)
            if texture == "blocks":
                piano.add(tick + piece.jitter(4), low + 12, velocity - 2, length)
                for k, n in enumerate(middle):
                    piano.add(tick + 40 + 30 * k + piece.jitter(4), n, velocity - 6, length - 40)
            else:
                for k, n in enumerate(middle):
                    piano.add(tick + EIGHTH + 45 * k + piece.jitter(6), n, velocity - 12, length - EIGHTH)
                if length >= 3 * TICKS:
                    piano.add(tick + 5 * EIGHTH + piece.jitter(8), middle[1], velocity - 16, length - 5 * EIGHTH)
        elif texture == "pulse":
            for beat in range(0, length, TICKS * 2):
                for k, offset in enumerate((0, round(0.75 * TICKS))):
                    piano.add(tick + beat + offset + piece.jitter(4), low, velocity + 4 - 8 * k, TICKS)
                    piano.add(tick + beat + offset + piece.jitter(4), low + 12, velocity - 4 - 8 * k, TICKS)
            middle = voice(previous, tones, 50, min(67, ceiling))
            previous = middle
            for k, n in enumerate(middle):
                piano.add(tick + TICKS + 30 * k + piece.jitter(5), n, velocity - 12, length - TICKS)
    pedal(piece, piano)


def voice(previous: list, tones: list, low: int, high: int, count: int = 3) -> list:
    """count tones of the chord between low and high, nearest the previous chord's."""
    choices = [n for n in range(low, max(high, low + 12)) if n % 12 in tones]
    picked = []
    for target in previous[:count]:
        free = [n for n in choices if n not in picked] or choices
        picked.append(min(free, key=lambda n: (abs(n - target), n)))
    return sorted(picked)


def pedal(piece: Piece, piano: Part) -> None:
    step = round(piece.score.get("pedal_beats", 99) * TICKS)  # pedal taken again this often within a chord
    for tick, length, _ in piece.spans:
        for at in range(tick, tick + length, step):
            piano.pedal += [(at - 15, 0), (at + 40, 100)]
    piano.pedal.append((piece.end + piece.bar, 0))


def layers(piece: Piece) -> None:
    tonic = chord(piece.score["sections"][0]["chords"].split("|")[0].split()[0].split(":")[0])[2]
    for start, end, section in piece.sections:
        wanted, dyn = section.get("layers", []), section.get("dyn", 0.4)
        velocity = 40 + 40 * dyn
        spans = [s for s in piece.spans if start <= s[0] < end]
        if "drone" in wanted:
            drone = piece.part("drone", "drone", "drone", 0.0, reverb=0.4)
            for n in (above(tonic, 26), above(tonic, 26) + 7):
                drone.add(start, n, 70, end - start + (piece.bar if end == piece.end else 0))
        if "cello" in wanted:
            cello = piece.part("cello", "cellos", "bass", -0.25, reverb=0.45)
            for tick, length, name in spans:
                piece.held(cello, tick + 20, bass_note(name, 36), velocity, length)
        if "basses" in wanted:
            basses = piece.part("basses", "basses", "low", 0.2, reverb=0.4)
            for tick, length, name in spans:
                piece.held(basses, tick + 20, bass_note(name, 28), velocity - 6, length)
        if "strings" in wanted:
            violas = piece.part("violas", "violas", "pad", 0.3, reverb=0.5)
            cellos = piece.part("cellos-pad", "cellos", "pad", -0.3, reverb=0.5)
            previous = [55, 60, 64]
            for tick, length, name in spans:
                previous = voice(previous, chord(name)[1], 50, 69)
                piece.held(cellos, tick + 30, previous[0], velocity - 4, length)
                for n in previous[1:]:
                    piece.held(violas, tick + 30, n, velocity - 6, length)
        for layer, instrument, shift, pan in (("violin", "violin", 0, 0.15), ("cello-melody", "cellos", -12, -0.2)):
            if layer in wanted:
                line = piece.part(layer, instrument, "melody2", pan, reverb=0.45)
                for tick, notes, length in piece.tune:
                    if start <= tick < end:
                        piece.held(line, tick + 15, max(notes) + shift, velocity + 4, length)


def ending(piece: Piece, piano: Part) -> None:
    """The last chord rolled from the deep bass, held a bar longer."""
    tick, length, name = piece.spans[-1]
    bass, tones, _ = chord(name)
    low = above(bass, piece.score.get("bass_low", 33) - 5)
    roll = [low, low + 12] + [n for n in range(low + 13, low + 32) if n % 12 in tones][:4]
    piano.notes = [n for n in piano.notes if n[0] < tick]
    for k, n in enumerate(roll):
        piano.add(tick + 70 * k, n, 52 - 2 * k, length + piece.bar)
    last = [n for t, notes, _ in piece.tune for n in notes if t >= tick]
    for n in last:
        piano.add(tick + 70 * len(roll), n, 58, length + piece.bar)


def compose(score: dict, folder: Path) -> str:
    piece = Piece(score)
    piano = piece.part("piano", score.get("piano", "upright"), "piano", 0.0, reverb=score.get("piano_reverb", 0.35))
    if score.get("piano_tone"):
        piano.tone.update(score["piano_tone"])
    play_melody(piece, piano)
    left_hand(piece, piano)
    layers(piece)
    ending(piece, piano)
    folder.mkdir(parents=True, exist_ok=True)
    sheet = []
    for name, part in piece.parts.items():
        write_part(part, piece.tempos, folder / f"{name}.mid", (piece.beats, 2))
        library, sfz, _ = INSTRUMENTS[part.instrument]
        sheet.append({"part": name, "library": library, "sfz": sfz, "role": part.role,
                      "gain_db": ROLES[part.role] + score.get("gains", {}).get(name, 0.0), "pan": part.pan,
                      "reverb": part.reverb, "tone": part.tone, "notes": len(part.notes)})
    room = score.get("room", {"rt60": 1.2})
    mix = {"hall": {"rt60": room["rt60"], "wet": room.get("wet", 1.0)}, "parts": sheet,
           "master": {"tone": 0.0, "air": 0.0, "width": 0.0, "level": 0.0}}
    if score.get("noise_db") is not None:
        mix["noise"] = {"db": score["noise_db"]}
    (folder / "mix.json").write_text(json.dumps(mix, indent=2))
    return (f"{folder.name}: {piece.bpm} bpm, {piece.end // piece.bar} bars, "
            f"{piece.seconds(0, piece.end + piece.bar):.0f} s, parts {', '.join(piece.parts)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--pieces", nargs="+", default=sorted(p.stem for p in PIECES.glob("*.json")))
    args = parser.parse_args()
    for name in args.pieces:
        print(compose(json.loads((PIECES / f"{name}.json").read_text()), args.out / name))


if __name__ == "__main__":
    main()
