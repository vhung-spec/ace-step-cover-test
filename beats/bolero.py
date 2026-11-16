"""Bolero (nhạc vàng) beats for Vietnamese songs, on real sampled
instruments: one MIDI file per instrument plus mix.json, the format
../render_samples.py plays (through ../bossa/render_bossa.py):

    python beats/bolero.py out/bossa --styles bolero-moc bolero-nhac-song ...

What the arranger plays (Vietnamese guitar teaching pages, as web search
summarised them, and Latin bolero practice; not yet measured on the
user's references):
- the guitar, rải (arpeggio): the bass on 1, the three top strings rolled
  3-2-1 on 2, then strings (2 3) on the "and", (1 2) on 3, (3) on its
  "and", the bass again (the fifth) on 4; or quạt (strum): the bass on 1
  and 3 (root, then fifth), the chord struck down on 2, up on its "and",
  down on 4, up on its "and" (the Cuban bolero figure, quarter, two
  eighths, quarter, quarter, under the bass);
- the bass on 1 and 3 (root and fifth: "bass rơi 1-3"), walking a half
  step into the next bar's root on 4 when the chord changes;
- maracas in eighths, the bolero figure's strokes louder; bongos light
  (muted taps, an open tone on the "and" of 2 and of 4, a roll at the end
  of a phrase); for nhạc sống, a soft kit: the kick on 1 and 3, the
  cross-stick on 2, its "and" and 4, the hi-hat in eighths;
- the guitar phím lõm's voice: an electric guitar's notes scooped up a
  whole tone into the note (nhấn) and shaken once held (rung), as pitch
  bends: the intro (dạo đầu: the song's last phrase), a short answer after
  each sung phrase (the beat leaves the verses to the singer); or a tenor
  saxophone in its place;
- harmony: minor keys, i-iv-VII-III-VI-iv-V7-i and its relatives.

The beat itself has no melody where the singer sings; bolero-khong-loi is
the instrumental version (nhạc không lời), the guitar singing the tune.
"""

import argparse
import json
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "bossa"))

from arrange_bossa import (EIGHTH, FALLBACK, INSTRUMENTS as BASE_INSTRUMENTS, KINDS, TICKS,  # noqa: E402
                           TONES as BASE_TONES, Part, Sketch, ending, fifth, nearest, parse, string_pad, voice_lead,
                           write_part)
from tunes import Tune, check, chords, melody  # noqa: E402

# An original bolero tune for the sketches (A minor, 4/4, 66 bpm): eight
# bars of verse, eight of refrain (điệp khúc).
PHO_NHO = Tune(
    "pho-nho", "Phố Nhỏ Mưa Thưa",
    melody("""
r:2 E4:1 A4:1 C5:3 B4:1 | A4:4 r:1 F4:1 A4:1 D5:1 | D5:3 B4:1 G4:4 | r:2 E4:1 G4:1 C5:4 |
A4:3 C5:1 F5:3 E5:1 | D5:3 C5:1 A4:2 F4:2 | E4:2 G#4:2 B4:2 D5:2 | C5:6 r:2 |
r:1 A4:1 C5:1 F5:1 F5:4 | G5:3 F5:1 D5:4 | E5:3 D5:1 B4:4 | C5:2 B4:2 A4:4 |
r:1 A4:1 D5:1 E5:1 F5:4 | E5:3 C5:1 A4:4 | B4:2 D5:2 C5:2 B4:2 | A4:8 |"""),
    chords(["Am", "Dm", "G", "C", "F", "Dm", "E7", "Am",
            "F", "G", "Em", "Am", "Dm", "Am", "E7", "Am"]),
    bpm=66, about="original (Bokin, 2026), bolero in A minor", sections=[(0, "A"), (8, "B")], final="Am")
check(PHO_NHO)
TUNES = {PHO_NHO.name: PHO_NHO}

INSTRUMENTS = BASE_INSTRUMENTS | {
    "emily": ("emily", "emily_clean.sfz"),  # Karoryfer's Emilyguitar, an electric guitar (CC0)
    "fashionbass": ("fashionbass", "fashionbass_clean.sfz"),  # Karoryfer's Fashionbass, a jazz bass (CC0)
    "maracas": ("vcsl", "Idiophones/Struck Idiophones/Shaker, Small.sfz"),
    "bongos": ("vcsl", "Membranophones/Struck Membranophones/Bongos.sfz"),
    "sax": ("vcsl", "Aerophones/Reed Aerophones/Tenor Saxophone - Vibrato.sfz"),
}
TONES = BASE_TONES | {
    # recorded straight from the pickups, nearly mono: a chorus widens it, the room carries it
    "emily": {"highpass": 120, "lowpass": 6000, "shelf": [3000, -2], "width": 0.0, "chorus": 0.35},
    "fashionbass": {"highpass": 35, "lowpass": 3000, "width": 0.0},
    "meatbass": {"highpass": 38, "lowpass": 3500, "width": 0.0},
    "iowa-nylon": {"highpass": 90, "width": 0.5},
    "maracas": {"highpass": 500, "shelf": [8000, -3], "width": 0.4},
    "bongos": {"highpass": 100, "width": 0.5},
    "sax": {"highpass": 90, "lowpass": 7500, "width": 0.6},
    "rusty": {"highpass": 45, "width": 0.6},
}
ROLES = {"melody": 0.0, "guitar": -4.0, "bass": -3.0, "drums": -10.0, "maracas": -20.0, "bongos": -15.0,
         "pad": -13.0}

BEND_RANGE = 1200  # cents a full pitch wheel bends Emilyguitar (its SFZ's bend_up)
# The kit's keys (bossa_rusty_kit.sfz) and the bongos' and maracas' (VCSL).
KICK, XSTICK, HAT = 36, 37, 42
BONGO_OPEN, BONGO_MUTED, BONGO_ROLL, BONGO_LOW = 60, 61, 62, 63
SHAKE_DOWN, SHAKE_UP = 64, 65
BOLERO_FIGURE = {0, 2, 3, 4, 6}  # quarter, two eighths, quarter, quarter: the strokes the maracas lean on


def ms_ticks(sk: Sketch, ms: float) -> int:
    return int(round(ms / 1000 * sk.bpm / 60 * TICKS))


def wheel(cents: float) -> int:
    return int(round(cents / BEND_RANGE * 8191))


def nhan_rung(sk: Sketch, part: Part, tick: int, length: int, scoop: bool = True, shake: bool = True) -> None:
    """The phím lõm's left hand on one note, as pitch bends: nhấn (the note
    reached by pressing the string from a whole tone under it, in 110 ms),
    then rung (once held 280 ms, a shake of 30 cents at 5.5 Hz growing in
    over 300 ms); back to rest when it ends."""
    if scoop:
        steps = 8
        for i in range(steps + 1):
            part.bends.append((tick + ms_ticks(sk, 110) * i // steps, wheel(-200 * (1 - i / steps) ** 1.5)))
    else:
        part.bends.append((tick, 0))
    start = tick + ms_ticks(sk, 280)
    if shake and length > ms_ticks(sk, 450):
        step = max(1, ms_ticks(sk, 12))
        for t in range(start, tick + length, step):
            seconds = (t - start) / TICKS * 60 / sk.bpm
            depth = 30 * min(1.0, seconds / 0.3)
            part.bends.append((t, wheel(depth * math.sin(2 * math.pi * 5.5 * seconds))))
    part.bends.append((tick + length, 0))


def play_lead(sk: Sketch, part: Part, notes: list, velocity: int, bends: bool = True) -> None:
    """A lead line, (tick, note, length): on the guitar every note longer than
    an eighth pressed into (nhấn) and the long ones shaken (rung)."""
    for tick, note, length in notes:
        v = velocity + min(10, length // EIGHTH * 2) + sk.rng.randint(-5, 5)
        part.add(tick, note, v, max(60, length - 20))
        if bends:
            nhan_rung(sk, part, tick, max(60, length - 20), scoop=length > EIGHTH or sk.rng.random() < 0.3,
                      shake=length >= 3 * EIGHTH)


SCALE = (9, 11, 0, 2, 4, 5, 7)  # A natural minor


def answer(sk: Sketch, name: str, tick: int, low: int = 57, high: int = 72) -> list:
    """A short answer after a sung phrase: four eighths down the minor
    scale (G# over E) from the chord's fifth to its root or third."""
    root, kind = parse(name)
    scale = sorted({8 if (name in ("E", "E7") and s == 7) else s for s in SCALE})  # G# under E major or E7
    top = nearest(root + fifth(name), 66, low, high)
    steps = [n for n in range(top, low - 1, -1) if n % 12 in scale]
    line = steps[:4] if len(steps) >= 4 else steps
    tones = {(root + i) % 12 for i in KINDS[kind]}
    while len(line) > 2 and line[-1] % 12 not in tones:  # end on a chord tone
        line = line[:-1]
    lengths = [EIGHTH] * (len(line) - 1) + [2 * EIGHTH]
    out, t = [], tick
    for note, length in zip(line, lengths):
        out.append((t, note, length))
        t += length
    return out


def guitar_rai(sk: Sketch, part: Part, velocity: int, start: int, end: int) -> None:
    """Rải: bass (root) on 1; strings 3-2-1 rolled on 2; (2 3) on its "and";
    (1 2) on 3; (3) on its "and"; the bass again, the fifth, on 4."""
    previous = None
    for bar_tick in range(start, end, sk.bar):
        name = sk.chord_at(bar_tick)
        root = parse(name)[0]
        chord = voice_lead(previous, name, 3, 55, 71, 62)
        previous = chord
        low, mid, high = chord
        ring = sk.bar - 20
        part.add(bar_tick, nearest(root, 45, 40, 52), velocity - 2 + sk.rng.randint(-3, 3), 6 * EIGHTH)
        for i, note in enumerate(chord):
            part.add(bar_tick + 2 * EIGHTH + 22 * i, note, velocity - 4 - 2 * i + sk.rng.randint(-3, 3),
                     ring - 2 * EIGHTH)
        for e, notes in ((3, (mid, low)), (4, (high, mid)), (5, (low,))):
            for note in notes:
                part.add(sk.lay_back(bar_tick + e * EIGHTH, 6), note, velocity - 8 + sk.rng.randint(-4, 3),
                         ring - e * EIGHTH)
        part.add(bar_tick + 6 * EIGHTH, nearest(root + fifth(name), 45, 40, 52), velocity - 8, 2 * EIGHTH)


def guitar_quat(sk: Sketch, part: Part, velocity: int, start: int, end: int) -> None:
    """Quạt: the bass on 1 and 3 (root, then fifth), the chord struck down on
    2, up on its "and", down on 4, up on its "and"."""
    previous = None
    for bar_tick in range(start, end, sk.bar):
        name = sk.chord_at(bar_tick)
        root = parse(name)[0]
        chord = voice_lead(previous, name, 3, 55, 71, 62)
        previous = chord
        part.add(bar_tick, nearest(root, 45, 40, 52), velocity + sk.rng.randint(-3, 3), 2 * EIGHTH - 20)
        part.add(bar_tick + 4 * EIGHTH, nearest(root + fifth(name), 45, 40, 52), velocity - 6, 2 * EIGHTH - 20)
        for e, down, accent in ((2, True, 4), (3, False, -10), (6, True, 0), (7, False, -12)):
            at = sk.lay_back(bar_tick + e * EIGHTH, 4)
            notes = chord if down else list(reversed(chord))
            for i, note in enumerate(notes):
                part.add(at + 11 * i, note, velocity + accent - 2 * i + sk.rng.randint(-4, 3), EIGHTH - 30)


def bass_bolero(sk: Sketch, part: Part, velocity: int, start: int, end: int) -> None:
    """The bass on 1 and 3, root and fifth; on 4, a half step into the next
    bar's root when the chord changes."""
    previous = 38
    for bar_tick in range(start, end, sk.bar):
        name = sk.chord_at(bar_tick)
        root = parse(name)[0]
        previous = nearest(root, previous, 28, 50)
        part.add(bar_tick, previous, velocity + sk.rng.randint(-3, 3), 4 * EIGHTH - 40)
        part.add(bar_tick + 4 * EIGHTH, nearest(root + fifth(name), previous, 28, 50), velocity - 8, 2 * EIGHTH - 30)
        following = sk.chord_at(bar_tick + sk.bar)
        if bar_tick + sk.bar < end and following != name:
            target = nearest(parse(following)[0], previous, 28, 50)
            part.add(bar_tick + 6 * EIGHTH, target - 1 if target > previous else target + 1, velocity - 12,
                     2 * EIGHTH - 30)


def maracas(sk: Sketch, part: Part, velocity: int, start: int, end: int) -> None:
    for bar_tick in range(start, end, sk.bar):
        for e in range(8):
            v = velocity - (0 if e in BOLERO_FIGURE else 14) + sk.rng.randint(-5, 5)
            part.add(sk.lay_back(bar_tick + e * EIGHTH, 6), SHAKE_DOWN if e % 2 == 0 else SHAKE_UP, v, EIGHTH)


def bongos(sk: Sketch, part: Part, velocity: int, start: int, end: int) -> None:
    """Light: muted taps on the "and" of 1 and 3, an open tone on the "and"
    of 2, the low drum on the "and" of 4; a roll closing each phrase."""
    for bar_tick in range(start, end, sk.bar):
        phrase_end = ((bar_tick - sk.intro) // sk.bar) % 4 == 3
        for e, key, v in ((1, BONGO_MUTED, -14), (3, BONGO_OPEN, 0), (5, BONGO_MUTED, -14), (7, BONGO_LOW, -4)):
            if phrase_end and e == 7:
                continue
            part.add(sk.lay_back(bar_tick + e * EIGHTH, 8), key, velocity + v + sk.rng.randint(-5, 4), EIGHTH)
        if phrase_end:
            part.add(bar_tick + 6 * EIGHTH, BONGO_ROLL, velocity - 8, 2 * EIGHTH)


def kit_bolero(sk: Sketch, part: Part, velocity: int, start: int, end: int) -> None:
    """Nhạc sống's soft kit: the kick on 1 and 3 (led into on every other
    bar), the cross-stick on 2, its "and" and 4, the hi-hat in eighths."""
    sk.stir = False
    for k, bar_tick in enumerate(range(start, end, sk.bar)):
        part.add(bar_tick, KICK, velocity + sk.rng.randint(-3, 3), EIGHTH)
        part.add(bar_tick + 4 * EIGHTH, KICK, velocity - 6, EIGHTH)
        if k % 2:
            part.add(bar_tick + 7 * EIGHTH + 8, KICK, velocity - 20, EIGHTH)
        for e, v in ((2, -4), (3, -12), (6, -6)):
            part.add(sk.lay_back(bar_tick + e * EIGHTH, 6), XSTICK, velocity + v + sk.rng.randint(-4, 3), EIGHTH)
        for e in range(8):
            part.add(sk.lay_back(bar_tick + e * EIGHTH, 4), HAT, velocity - (12 if e % 2 == 0 else 20)
                     + sk.rng.randint(-4, 4), EIGHTH)


def lead_notes(sk: Sketch, beat_only: bool) -> list:
    """The lead's notes: the intro plays the song's last phrase (its last four
    bars); in a beat, an answer in the last two beats of every fourth bar;
    in the instrumental, the whole tune."""
    tune = sk.melody([0])
    first = sk.starts[0] + (len(sk.tune.chords) - 4) * sk.bar
    notes = [(t - first, n, l) for t, n, l, _ in tune if t >= first]
    if beat_only:
        for bar in range(3, len(sk.tune.chords), 4):
            tick = sk.starts[0] + bar * sk.bar + 4 * EIGHTH
            notes += answer(sk, sk.chord_at(tick), tick)
    else:
        notes += [(t, n, l) for t, n, l, _ in tune]
    return sorted(notes)


@dataclass
class Style:
    title: str
    tune: str
    bpm: float
    rt60: float
    wet: float
    build: callable = None
    about: str = ""
    extra: dict = field(default_factory=dict)


def build(sk: Sketch, comp: str = "rai", band: str = "moc", lead: str = "emily", beat_only: bool = True) -> None:
    g = sk.part("guitar", "iowa-nylon", "guitar", -0.2, 0.35, TONES["iowa-nylon"])
    (guitar_rai if comp == "rai" else guitar_quat)(sk, g, 66, 0, sk.end)
    if band == "moc":
        b = sk.part("bass", "meatbass", "bass", 0.0, 0.05, TONES["meatbass"])
        bass_bolero(sk, b, 84, sk.intro, sk.end)
        mr = sk.part("maracas", "maracas", "maracas", 0.4, 0.3, TONES["maracas"])
        maracas(sk, mr, 56, sk.intro, sk.end)
        bg = sk.part("bongos", "bongos", "bongos", -0.35, 0.3, TONES["bongos"])
        bongos(sk, bg, 64, sk.intro, sk.end)
    else:
        b = sk.part("bass", "fashionbass", "bass", 0.0, 0.05, TONES["fashionbass"])
        bass_bolero(sk, b, 80, sk.intro, sk.end)
        d = sk.part("drums", "rusty", "drums", 0.1, 0.25, TONES["rusty"])
        kit_bolero(sk, d, 60, sk.intro, sk.end)
        mr = sk.part("maracas", "maracas", "maracas", 0.4, 0.3, TONES["maracas"])
        maracas(sk, mr, 50, sk.intro, sk.end)
        va = sk.part("violas", "violas", "pad", -0.3, 0.6, TONES["violas"])
        vc = sk.part("cellos", "cellos", "pad", 0.3, 0.55, TONES["cellos"])
        string_pad(sk, va, vc, 40, sk.starts[0] + 8 * sk.bar, sk.end, [])
    instrument = "emily" if lead == "emily" else "sax"
    ld = sk.part("lead", instrument, "melody", 0.15, 0.6, TONES[instrument])
    play_lead(sk, ld, lead_notes(sk, beat_only), 72 if lead == "emily" else 70, bends=lead == "emily")
    ending(sk, sk.parts, 66)
    root = parse(sk.tune.final or sk.tune.chords[-1][-1])[0]
    play_lead(sk, ld, [(sk.end + 30, nearest(root, 69, 64, 76), 6 * TICKS)], 70, bends=lead == "emily")


STYLES = {
    "bolero-moc": Style("Bolero mộc", "pho-nho", 66, 1.8, 0.5, lambda sk: build(sk, "rai", "moc", "emily"),
                        "Guitar nylon rải, contrabass, maracas và bongo nhẹ; guitar phím lõm dạo đầu và trả câu."),
    "bolero-nhac-song": Style("Bolero nhạc sống", "pho-nho", 66, 2.0, 0.55,
                              lambda sk: build(sk, "quat", "song", "emily"),
                              "Guitar quạt, bass điện, trống nhẹ, maracas, dàn dây ở điệp khúc; phím lõm dạo đầu, trả câu."),
    "bolero-sax": Style("Bolero sax", "pho-nho", 66, 1.8, 0.5, lambda sk: build(sk, "rai", "moc", "sax"),
                        "Như Bolero mộc, kèn saxophone dạo đầu và trả câu."),
    "bolero-khong-loi": Style("Bolero không lời", "pho-nho", 66, 2.0, 0.55,
                              lambda sk: build(sk, "quat", "song", "emily", beat_only=False),
                              "Bản không lời: guitar phím lõm hát cả giai điệu trên nền nhạc sống."),
}


def make(style_name: str, out: Path, seed: int = 7) -> Path:
    style = STYLES[style_name]
    tune = TUNES[style.tune]
    sk = Sketch(tune, 1, style.bpm, seed, intro_bars=4)
    style.build(sk)
    folder = out / style_name
    folder.mkdir(parents=True, exist_ok=True)
    sheet = []
    for name, part in sk.parts.items():
        write_part(part, sk.tempos(), folder / f"{name}.mid", tune.beats)
        library, sfz = INSTRUMENTS[part.instrument]
        backup = {}
        if part.instrument in FALLBACK:
            spare = FALLBACK[part.instrument]
            backup = {"fallback": {"library": INSTRUMENTS[spare][0], "sfz": INSTRUMENTS[spare][1],
                                   "tone": TONES.get(spare, {}) | part.tone}}
        sheet.append({"part": name, "library": library, "sfz": sfz, "role": part.role, **backup,
                      "gain_db": ROLES[part.role] if part.gain_db is None else part.gain_db,
                      "pan": part.pan, "reverb": part.reverb, "tone": part.tone, "notes": len(part.notes),
                      "bends": len(part.bends)})
    mix = {"hall": {"rt60": style.rt60, "wet": style.wet, "highpass": 250}, "parts": sheet,
           "about": {"title": style.title, "tune": tune.title, "tune_about": tune.about, "bpm": style.bpm,
                     "text": style.about}}
    (folder / "mix.json").write_text(json.dumps(mix, indent=2, ensure_ascii=False))
    seconds = sk.end / TICKS * 60 / style.bpm + 5
    print(f"{folder.name}: {tune.title}, {style.bpm} bpm, about {seconds:.0f} s, parts "
          + ", ".join(f"{n}({len(p.notes)}{'/' + str(len(p.bends)) + ' bends' if p.bends else ''})"
                      for n, p in sk.parts.items()))
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
