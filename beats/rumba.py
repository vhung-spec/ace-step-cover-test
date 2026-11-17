"""Rumba guitar instrumentals (hòa tấu rumba guitar, nhạc không lời) on real
sampled instruments, in the format ../render_samples.py plays:

    python beats/rumba.py out/bossa --styles rumba-guitar rumba-guitar-dien rumba-sax

What the arranger plays, as measured on three such instrumentals the user
sent as the style they want (their audio and the measurements stay in the
session's scratchpad; nothing of their tunes is used):
- 92-97 bpm, straight eighths (the off-beat eighth at 0.48 of the beat);
- the kick on 1, the "and" of 2 and 3, the "and" of 4 lighter; the bass on
  1 (its strongest), the "and" of 2, 3, and the "and" of 4, where it takes
  the next bar's root early;
- the rhythm guitar strummed in eighths, its "ands" the loudest (the "and"
  of 4 most of all); the hi-hat in eighths, its beats louder, a shaker's
  sixteenths under it;
- the lead, a guitar plucking the tune note by note (acoustic above all,
  by the tags; held notes barely shaken, 10-16 cents, few slides);
- warm: most of the energy at 250-500 Hz, 60-120 Hz 7-8 dB under the
  total, little above 4 kHz (22 dB under); the drums strong (percussive
  energy 4.6-7 dB under the harmonic); a long room (about 2.9 s); the lows
  in mono, the rest moderately wide (side 10 dB under mid).

Assumed (not measured): the cross-stick on 2 and 4, the fills (dồn) at
the phrases' ends and a crash on each section's first beat, the double
stops (a third to a sixth under held melody notes), the light congas and
the strings in the refrains.

The sketches play an original tune, Nắng Sớm (A minor, 16 bars), twice
after a four-bar intro on its last phrase.
"""

import argparse
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "bossa"))

from arrange_bossa import (EIGHTH, KINDS, TICKS, Part, Sketch, ending, fifth, nearest, parse,  # noqa: E402
                           string_pad, voice_lead)
from bolero import (INSTRUMENTS as BOLERO_INSTRUMENTS, SIXTEENTH, TONES as BOLERO_TONES, V_CONGA_MUTED,  # noqa: E402
                    V_CRASH, V_HAT, V_HAT_FOOT, V_HTOM, V_KICK, V_LTOM, V_SHAKE_DOWN, V_SHAKE_UP, V_SNARE, V_TUMBA,
                    V_XSTICK, Style, make, wheel)
from tunes import Tune, check, chords, melody  # noqa: E402

# An original tune for the sketches: A minor, verse (A) and refrain (B), the
# melody's lengths in eighths; notes on the "and" of a beat held over the
# next one, as rumba melodies lean.
NANG_SOM = Tune(
    "nang-som", "Nắng Sớm",
    melody("""
r:1 E4:1 A4:1 B4:1 C5:3 B4:1 | A4:2 D5:3 C5:1 A4:2 | r:1 B4:1 D5:1 G5:3 F5:1 E5:5 | r:2 C5:1 D5:1 |
F5:3 E5:1 D5:2 C5:1 A4:1 | D5:3 C5:1 A4:2 F4:1 A4:1 | A4:3 B4:1 G#4:2 B4:1 D5:1 | C5:6 r:2 |
r:1 A4:1 C5:1 F5:5 | G5:3 F5:1 D5:2 E5:2 | E5:3 D5:1 B4:2 G4:1 B4:1 | C5:2 B4:2 A4:4 |
r:1 A4:1 D5:1 F5:5 | G5:2 F5:2 D5:2 B4:2 | C5:3 B4:1 G#4:2 B4:1 D5:1 | A4:8 |"""),
    chords(["Am", "Dm", "G7", "C", "F", "Dm", "Esus4 E7", "Am",
            "F", "G", "Em", "Am", "Dm", "G7", "E7", "Am"]),
    bpm=95, about="original (Bokin, 2026), rumba in A minor", sections=[(0, "A"), (8, "B")], final="Am")
check(NANG_SOM)
TUNES = {NANG_SOM.name: NANG_SOM}

INSTRUMENTS = BOLERO_INSTRUMENTS | {
    # FreePats' Spanish classical guitar (CC0) by its own mapping, to set against Iowa's
    "nylon-fp": ("freepats", "SpanishClassicalGuitar-20190618.sfz"),
}
TONES = BOLERO_TONES | {
    # The first sketches against the references: 20-60 Hz 20 dB short, 8-16
    # kHz 6-10 dB short, 0.5-2 kHz 2 dB over, the drums 3-4 dB under, wider
    # (side 5-8 dB under mid, theirs 10). So the guitars keep their top, the
    # kit and shaker their sheen, the images narrower.
    "lead-nylon": {"highpass": 100, "width": 0.3},
    "rhythm-nylon": {"highpass": 120, "width": 0.6},
    "lead-electric": {"highpass": 120, "lowpass": 9000, "width": 0.0, "chorus": 0.25},
    "lead-sax": {"highpass": 110, "lowpass": 9000, "width": 0.3},
    "kit-warm": {"highpass": 30, "width": 0.6},
    "rumba-shaker": {"highpass": 400, "width": 0.4},
    "fashionbass": {"highpass": 28, "lowpass": 2500, "width": 0.0},
}
ROLES = {"melody": 0.0, "guitar": -5.0, "bass": -1.0, "kit": -3.0, "congas": -13.0, "maracas": -18.0,
         "pad": -15.0}
# A guitar's strum over a bar of eighths: (eighth, stroke, loudness): its
# "ands" the loudest, the "and" of 4 most of all, beat 2 the softest (as the
# references' guitar band rises).
STRUM = [(0, "down", -3), (1, "up", -6), (2, "down", -16), (3, "up", 0), (4, "down", -5), (5, "up", -2),
         (6, "down", -9), (7, "up", 6)]


def bar_of(sk: Sketch, tick: int) -> tuple[int, int]:
    """(the tune's bar, 0-15, negative in the intro; the pass)."""
    if tick < sk.intro:
        return (tick - sk.intro) // sk.bar, -1
    t = tick - sk.intro
    return (t % sk.length) // sk.bar, t // sk.length


def fill_of(sk: Sketch, bar_tick: int) -> str | None:
    """The fill closing a bar: "long" into a section (and out of the intro,
    into the last chord), "short" at the end of a section's first phrase."""
    k, _ = bar_of(sk, bar_tick)
    following = bar_tick + sk.bar
    if following == sk.intro or following >= sk.end or (k >= 0 and k % 8 == 7):
        return "long"
    return "short" if k >= 0 and k % 4 == 3 else None


def lead_line(sk: Sketch, part: Part, velocity: int, harmony: bool = True, hammer: bool = False) -> None:
    """The tune plucked note by note, the notes on a beat a little louder,
    after an intro on its last phrase; a held note (3 eighths or more) on a
    beat (half of those of 4 eighths or more) doubled by the chord's highest
    tone a third to a sixth under it, a guitarist's double stop. hammer: a third of the held notes reached by a
    hammer-on from the scale's step under them (a quick grace note, the
    note itself softer, unplucked). (A tremolo on held notes, tried for the
    nylon's short ring, made PaSST hear a harp, 0.58, and no guitar.)"""
    tune = sk.melody()
    first = sk.starts[0] + (len(sk.tune.chords) - 4) * sk.bar
    notes = [(t - first, n, l) for t, n, l, p in tune if p == 0 and t >= first]
    notes += [(t, n, l) for t, n, l, _ in tune]
    scale = {9, 11, 0, 2, 4, 5, 7, 8}  # A minor, harmonic G# with it
    for tick, note, length in notes:
        on_beat = tick % TICKS == 0
        v = velocity + (4 if on_beat else 0) + sk.rng.randint(-4, 3)
        at = sk.lay_back(tick, 4)
        if hammer and length >= 3 * EIGHTH and sk.rng.random() < 0.35:
            grace = next(g for g in (note - 2, note - 1) if g % 12 in scale)
            part.add(at - 45, grace, v - 4, 50)
            part.add(at + 5, note, v - 8, length - 15)
        else:
            part.add(at, note, v, length - 10)
        if harmony and on_beat and length >= 4 * EIGHTH and sk.rng.random() < 0.5:
            root, kind = parse(sk.chord_at(tick))
            tones = {(root + i) % 12 for i in KINDS[kind]}
            below = [n for n in range(note - 9, note - 2) if n % 12 in tones]
            if below:
                part.add(at + 12, max(below), v - 20, length - 20)  # under the tune, not over it


def vibrato(sk: Sketch, part: Part, cents: float, rate: float = 4.0) -> None:
    """A light shake on each held note (as measured: 10-16 cents peak to
    peak), from 300 ms in; at rest again when it ends."""
    shaken = []
    for tick, note, velocity, length in sorted(part.notes, key=lambda n: (n[0], -n[1])):
        if length < 3 * EIGHTH or any(abs(tick - t) < 40 for t in shaken[-2:]):  # a double stop's lower note
            continue
        shaken.append(tick)
        step = max(1, int(round(0.012 * sk.bpm / 60 * TICKS)))  # every 12 ms
        begin = tick + int(0.3 * sk.bpm / 60 * TICKS)
        for t in range(begin, tick + length, step):
            seconds = (t - begin) / TICKS * 60 / sk.bpm
            part.bends.append((t, wheel(cents / 2 * min(1, seconds / 0.4) * math.sin(2 * math.pi * rate * seconds))))
        part.bends.append((tick + length, 0))


def rhythm_guitar(sk: Sketch, part: Part, velocity: int, start: int, end: int) -> None:
    """The rumba strum: the thumb's bass on 1 and 3 (root, fifth), the strings
    struck down (five, from the fifth up, 6 ticks apart) and up (the top
    three) in eighths (STRUM), hard enough that its accents sound the Iowa
    guitar's loudest layer; a long fill's last
    two beats left to the drums but for a chord on 3."""
    previous = None
    for bar_tick in range(start, end, sk.bar):
        fill = fill_of(sk, bar_tick)
        for beat, interval in ((0, 0), (4, None)):
            name = sk.chord_at(bar_tick + beat * EIGHTH)
            root = parse(name)[0]
            note = nearest(root + (interval if interval is not None else fifth(name)), 45, 40, 52)
            part.add(bar_tick + beat * EIGHTH, note, velocity - 2 + sk.rng.randint(-3, 3), 2 * EIGHTH)
        for e, stroke, dv in STRUM:
            if fill == "long" and e > 4:
                continue
            tick = bar_tick + e * EIGHTH
            name = sk.chord_at(tick)
            chord = voice_lead(previous, name, 4, 50, 74, 62)
            previous = chord
            # a down stroke sweeps five strings from the fifth up, an up stroke the top three
            if stroke == "down":
                notes, gap = [nearest(parse(name)[0] + fifth(name), 47, 40, 51)] + chord, 6
            else:
                notes, gap = list(reversed(chord))[:3], 5
            at = sk.lay_back(tick, 3)
            for i, n in enumerate(notes):
                part.add(at + gap * i, n, velocity + dv - 2 * i + sk.rng.randint(-4, 3), EIGHTH - 25)


def bass_rumba(sk: Sketch, part: Part, velocity: int, start: int, end: int) -> None:
    """The bass on 1 (root), the "and" of 2 (root again, short), 3 (the
    fifth) and the "and" of 4: the next bar's root, early, held over its
    downbeat, where it sounds again."""
    previous = 33  # around A1: the references' 20-60 Hz is 8-12 dB under the total (the first sketches' 32)
    for bar_tick in range(start, end, sk.bar):
        name = sk.chord_at(bar_tick)
        root = nearest(parse(name)[0], previous, 28, 40)
        previous = root
        part.add(bar_tick, root, velocity + sk.rng.randint(-3, 3), 3 * EIGHTH - 30)
        part.add(bar_tick + 3 * EIGHTH, root, velocity - 12, EIGHTH - 20)
        mid = sk.chord_at(bar_tick + 4 * EIGHTH)
        part.add(bar_tick + 4 * EIGHTH, nearest(parse(mid)[0] + fifth(mid), root, 28, 45), velocity - 7,
                 3 * EIGHTH - 30)
        if bar_tick + sk.bar < end:
            following = sk.chord_at(bar_tick + sk.bar)
            part.add(bar_tick + 7 * EIGHTH, nearest(parse(following)[0], root, 28, 40), velocity - 5, EIGHTH + 40)


def kit_rumba(sk: Sketch, part: Part, velocity: int, start: int, end: int) -> None:
    """The kick on 1, the "and" of 2 and 3, the "and" of 4 lighter every
    other bar (as measured); the cross-stick on 2 and 4; the hi-hat closed
    in eighths, its beats louder. A short snare fill (dồn) on beat 4 closing
    a section's first phrase, a longer one down the toms into each section;
    a crash on each section's first beat."""
    for bar_tick in range(start, end, sk.bar):
        k, _ = bar_of(sk, bar_tick)
        fill = fill_of(sk, bar_tick)
        v = velocity - (10 if k < 0 else 0)
        if k >= 0 and k % 8 == 0:
            part.add(bar_tick, V_CRASH, v + 10, 4 * TICKS)
        for e, dv in ((0, 8), (3, 4), (4, 2)):
            if not (fill == "long" and e == 4):
                part.add(bar_tick + e * EIGHTH, V_KICK, v + dv + sk.rng.randint(-3, 3), EIGHTH)
        if k % 2 and not fill:
            part.add(bar_tick + 7 * EIGHTH, V_KICK, v - 14, EIGHTH)
        busy = range(4, 8) if fill == "long" else range(6, 8) if fill == "short" else ()
        for e in (2, 6):
            if e not in busy:
                part.add(sk.lay_back(bar_tick + e * EIGHTH, 4), V_XSTICK, v + sk.rng.randint(-4, 3), EIGHTH)
        for e in range(8):
            if e not in busy:
                part.add(sk.lay_back(bar_tick + e * EIGHTH, 3), V_HAT,
                         v - (10 if e % 2 == 0 else 20) + sk.rng.randint(-4, 4), EIGHTH)
        if fill == "short":
            for i in range(4):
                part.add(bar_tick + 6 * EIGHTH + i * SIXTEENTH, V_SNARE, v - 22 + 6 * i + sk.rng.randint(-3, 3),
                         SIXTEENTH)
            part.add(bar_tick + 6 * EIGHTH, V_HAT_FOOT, v - 20, EIGHTH)
        elif fill == "long":
            soft = 10 if k < 0 else 0
            for i, key in enumerate([V_SNARE] * 4 + [V_HTOM, V_HTOM, V_LTOM, V_LTOM]):
                part.add(bar_tick + 4 * EIGHTH + i * SIXTEENTH, key, v - 18 - soft + 4 * i + sk.rng.randint(-3, 3),
                         SIXTEENTH)
            part.add(bar_tick + 4 * EIGHTH, V_HAT_FOOT, v - 20, EIGHTH)


def shaker_rumba(sk: Sketch, part: Part, velocity: int, start: int, end: int, down: int = V_SHAKE_DOWN,
                 up: int = V_SHAKE_UP) -> None:
    """A shaker in sixteenths, the eighths louder and the beats most (the
    references' hi-hat band holds sixteenths at a quarter of its beats)."""
    for bar_tick in range(start, end, sk.bar):
        for s in range(16):
            v = velocity - (0 if s % 4 == 0 else 8 if s % 2 == 0 else 18) + sk.rng.randint(-4, 4)
            part.add(sk.lay_back(bar_tick + s * SIXTEENTH, 3), down if s % 2 == 0 else up, v, SIXTEENTH)


def congas_rumba(sk: Sketch, part: Part, velocity: int, start: int, end: int) -> None:
    """Light: a muted slap on 2, the tumba open on 4 and its "and"."""
    for bar_tick in range(start, end, sk.bar):
        fill = fill_of(sk, bar_tick)
        for e, key, dv in ((2, V_CONGA_MUTED, -6), (6, V_TUMBA, 0), (7, V_TUMBA, -8)):
            if fill == "long" and e >= 4:
                continue
            part.add(sk.lay_back(bar_tick + e * EIGHTH, 6), key, velocity + dv + sk.rng.randint(-5, 4), EIGHTH)


def build(sk: Sketch, lead: str = "nylon", guitar: str = "iowa-nylon") -> None:
    """The band, and the lead: the nylon guitar (double stops), the electric
    guitar (a light shake on held notes, a chorus), or the tenor sax; the
    nylon guitars Iowa's or FreePats'. PaSST heard the nylon sketches as a
    harp (0.79, guitar 0.02) with the guitars sent 0.35-0.45 into a 2.6 s
    hall: they are sent less now (0.15, 0.25), the hall shorter."""
    kit = sk.part("kit", "virtuosity", "kit", 0.0, 0.25, TONES["kit-warm"])
    kit_rumba(sk, kit, 72, 0, sk.end)
    sh = sk.part("maracas", "virtuosity", "maracas", 0.35, 0.25, TONES["rumba-shaker"])
    shaker_rumba(sk, sh, 60, 0, sk.end)
    cg = sk.part("congas", "virtuosity", "congas", -0.35, 0.25, TONES["virtuosity-congas"])
    congas_rumba(sk, cg, 70, sk.starts[0], sk.end)
    g = sk.part("guitar", guitar, "guitar", -0.3, 0.15, TONES["rhythm-nylon"])
    rhythm_guitar(sk, g, 90, 0, sk.end)
    b = sk.part("bass", "fashionbass", "bass", 0.0, 0.05, TONES["fashionbass"])
    bass_rumba(sk, b, 84, 0, sk.end)
    va = sk.part("violas", "violas", "pad", -0.3, 0.6, TONES["violas"])
    vc = sk.part("cellos", "cellos", "pad", 0.3, 0.55, TONES["cellos"])
    for start in sk.starts:
        string_pad(sk, va, vc, 38, start + 8 * sk.bar, start + 16 * sk.bar, [])
    instrument, tone = {"nylon": (guitar, "lead-nylon"), "electric": ("emily", "lead-electric"),
                        "sax": ("sax", "lead-sax")}[lead]
    ld = sk.part("lead", instrument, "melody", 0.1, 0.25 if lead == "nylon" else 0.4, TONES[tone])
    # the nylon lead plucked hard (its loudest layer, brighter, more of a guitar's bite than a harp's)
    lead_line(sk, ld, 100 if lead == "nylon" else 72, harmony=lead != "sax", hammer=lead != "sax")
    ending(sk, sk.parts, 66)
    root = parse(sk.tune.final or sk.tune.chords[-1][-1])[0]
    ld.add(sk.end + 30, nearest(root, 69, 64, 76), 70, 6 * TICKS)
    kit.add(sk.end, V_CRASH, 86, 6 * TICKS)
    kit.add(sk.end, V_KICK, 82, EIGHTH)
    cg.add(sk.end, V_TUMBA, 70, EIGHTH)
    if lead == "electric":
        vibrato(sk, ld, 14)


# The second production (the user, of the sketches above: "bộ sound chưa
# hay, bạn hãy tự mix theo kiểu bạn thấy hay"): an acoustic rumba as a
# producer would stack it. Shinyguitar's microphone program (fetch_bossa.py's
# bossa_shiny_acoustic.sfz): its notes, and its strings muted, a chuck, on
# 18-21.
SHINY_CHUCK = (18, 19, 20, 21)
# VCSL's cajón: hit1 (key 60) bright, the slap (centroid 790 Hz); hit2 and
# hit3 (61, 62) the bass (144 and 130 Hz)
CAJON_SLAP, CAJON_BASS, CAJON_DEEP = 60, 61, 62
# VCSL's congas: the conga muted and open, the tumba open; its small shaker
VC_CONGA_MUTED, VC_CONGA_OPEN, VC_TUMBA_OPEN = 60, 61, 65
VC_SHAKE_DOWN, VC_SHAKE_UP = 64, 65
ECHO = 3 * EIGHTH  # the lead's echo, a dotted quarter later
INSTRUMENTS |= {
    "shiny": ("shiny", "Programs/bossa_shiny_acoustic.sfz"),  # Karoryfer's Shinyguitar, an archtop (CC0)
    "cajon": ("vcsl", "Idiophones/Struck Idiophones/Cajon.sfz"),
    "vc-congas": ("vcsl", "Membranophones/Struck Membranophones/Conga.sfz"),
    "vc-shaker": ("vcsl", "Idiophones/Struck Idiophones/Shaker, Small.sfz"),
}
TONES |= {
    "steel-strum": {"highpass": 140, "lowpass": 12000, "shelf": [6000, -2], "width": 0.4},
    # Emilyguitar picked harder (its mf layer) and less chorus: PaSST heard the soft, chorused lead as keys
    "lead-electric-2": {"highpass": 120, "lowpass": 9000, "width": 0.0, "chorus": 0.12},
    "nylon-stabs": {"highpass": 160, "lowpass": 10000, "width": 0.4},
    "echo": {"highpass": 300, "lowpass": 5000, "width": 0.3},  # a darker repeat, as a tape echo's
    "warm-bass": {"highpass": 30, "lowpass": 1800, "width": 0.0},
    "cajon": {"highpass": 40, "width": 0.4},
    "vc-congas": {"highpass": 70, "width": 0.4},
    "vc-shaker": {"highpass": 500, "width": 0.4},
}
ROLES |= {"echo": -13.0, "stabs": -11.0, "cajon": -7.0}


def bend(cents: float, bend_range: float) -> int:
    """A pitch wheel value for cents, on an instrument bending bend_range
    cents at full wheel (Emilyguitar 1200; the SFZ default, the Iowa
    guitar's, 200)."""
    return int(round(max(-1.0, min(1.0, cents / bend_range)) * 8191))


def strum_steel(sk: Sketch, part: Part, velocity: int, start: int, end: int) -> None:
    """The rumba strum on the archtop (steel strings, its microphone): down
    on 1 and 3 (five strings from the fifth up), up on the "ands" (the top
    three; the "and" of 4 the loudest), and on 2 and 4 the strings muted, a
    chuck (the golpe: the references' guitar band is weakest on 2). A long
    fill stops it after 3."""
    pattern = [(0, "down", -2), (1, "up", -8), (2, "chuck", -10), (3, "up", 0), (4, "down", -4), (5, "up", -6),
               (6, "chuck", -10), (7, "up", 4)]
    previous, chucks = None, 0
    for bar_tick in range(start, end, sk.bar):
        fill = fill_of(sk, bar_tick)
        for e, stroke, dv in pattern:
            if fill == "long" and e > 4:
                continue
            tick = bar_tick + e * EIGHTH
            at = sk.lay_back(tick, 3)
            if stroke == "chuck":
                part.add(at, SHINY_CHUCK[chucks % len(SHINY_CHUCK)], velocity + dv + sk.rng.randint(-4, 3), EIGHTH // 2)
                chucks += 1
                continue
            name = sk.chord_at(tick)
            chord = voice_lead(previous, name, 4, 50, 74, 62)
            previous = chord
            if stroke == "down":
                notes, gap = [nearest(parse(name)[0] + fifth(name), 47, 40, 51)] + chord, 7
            else:
                notes, gap = list(reversed(chord))[:3], 6
            for i, n in enumerate(notes):
                part.add(at + gap * i, n, velocity + dv - 2 * i + sk.rng.randint(-4, 3), EIGHTH - 30)


def stabs_nylon(sk: Sketch, part: Part, velocity: int, start: int, end: int) -> None:
    """The second guitar (Iowa's nylon, on the other side): three strings
    struck with the bass's rhythm, 1, the "and" of 2, 3 and the "and" of 4,
    higher up the neck, so the two guitars interlock."""
    previous = None
    for bar_tick in range(start, end, sk.bar):
        fill = fill_of(sk, bar_tick)
        for e, dv in ((0, 0), (3, 2), (4, -4), (7, 4)):
            if fill == "long" and e > 4:
                continue
            tick = bar_tick + e * EIGHTH
            chord = voice_lead(previous, sk.chord_at(tick), 3, 59, 76, 67)
            previous = chord
            at = sk.lay_back(tick, 3)
            for i, n in enumerate(chord):
                part.add(at + 5 * i, n, velocity + dv - 2 * i + sk.rng.randint(-4, 3), EIGHTH + 60)


def cajon_rumba(sk: Sketch, part: Part, velocity: int, start: int, end: int) -> None:
    """The cajón, an acoustic rumba's kit: its bass on 1, the "and" of 2 and
    3 (where the references' kick falls), the deeper bass on the "and" of 4
    every other bar; the slap on 2 and 4, ghost slaps on the last sixteenth
    of 1 and of 3. A section closes on slaps in sixteenths over beats 3 and
    4, growing; a phrase on four of them on beat 4."""
    for bar_tick in range(start, end, sk.bar):
        k, _ = bar_of(sk, bar_tick)
        fill = fill_of(sk, bar_tick)
        v = velocity - (8 if k < 0 else 0)
        # the slaps a little under the bass: on 2 and 4 they land with the chuck and the conga
        hits = [(0, CAJON_BASS, 6), (6, CAJON_BASS, 2), (8, CAJON_BASS, 0), (4, CAJON_SLAP, -2), (12, CAJON_SLAP, 0),
                (3, CAJON_SLAP, -24), (11, CAJON_SLAP, -24)]
        if k % 2 and not fill:
            hits.append((14, CAJON_DEEP, -10))
        if fill == "long":
            hits = [h for h in hits if h[0] < 8] + [(8 + i, CAJON_SLAP, -18 + 3 * i) for i in range(8)]
        elif fill == "short":
            hits = [h for h in hits if h[0] < 12] + [(12, CAJON_SLAP, -4), (13, CAJON_SLAP, -14), (14, CAJON_SLAP, -6),
                                                     (15, CAJON_SLAP, -12)]
        for s, key, dv in hits:
            part.add(sk.lay_back(bar_tick + s * SIXTEENTH, 3), key, v + dv + sk.rng.randint(-4, 3), SIXTEENTH)


def congas_vc(sk: Sketch, part: Part, velocity: int, start: int, end: int) -> None:
    """VCSL's congas: muted on 2, open soft on its "and", the tumba open on 4
    and its "and"; resting under a section's fill."""
    for bar_tick in range(start, end, sk.bar):
        fill = fill_of(sk, bar_tick)
        for e, key, dv in ((2, VC_CONGA_MUTED, -4), (3, VC_CONGA_OPEN, -14), (6, VC_TUMBA_OPEN, 0),
                           (7, VC_TUMBA_OPEN, -8)):
            if fill == "long" and e >= 4:
                continue
            part.add(sk.lay_back(bar_tick + e * EIGHTH, 6), key, velocity + dv + sk.rng.randint(-5, 4), EIGHTH)


def expressive(sk: Sketch, part: Part, bend_range: float, depth: float, rate: float, slide_share: float) -> None:
    """The lead's left hand, as pitch bends over its tune (the top note at
    each onset): a slide into a share of the held notes from a half or
    whole step under (as far as the note before lay under it), 90 ms long;
    a vibrato on held notes (depth cents peak to peak) from 250 ms in; at
    rest at each note's end. A guitarist's vibrato and slides are what a harp
    cannot do."""
    tunes = sorted(part.notes, key=lambda n: (n[0], -n[1]))
    top, last = [], -10 ** 9
    for tick, note, velocity, length in tunes:
        if tick - last > 30:
            top.append((tick, note, length))
            last = tick
    ms = sk.bpm / 60 * TICKS / 1000  # ticks a millisecond
    previous = None
    for i, (tick, note, length) in enumerate(top):
        if length < 100:  # a hammer-on's grace note
            continue
        graced = i > 0 and top[i - 1][2] < 100 and tick - top[i - 1][0] < 80
        if length >= 3 * EIGHTH:
            if (not graced and previous is not None and 1 <= note - previous <= 2
                    and sk.rng.random() < slide_share * 2):
                steps = 8
                for s in range(steps):
                    part.bends.append((tick + int(90 * ms * s / steps), bend(-100 * (note - previous) * (1 - s / steps),
                                                                             bend_range)))
                part.bends.append((tick + int(90 * ms), 0))
            begin = tick + int(250 * ms)
            step = max(1, int(12 * ms))
            for t in range(begin, tick + length - step, step):
                seconds = (t - begin) / (1000 * ms)
                swell = min(1.0, seconds / 0.35)
                part.bends.append((t, bend(depth / 2 * swell * math.sin(2 * math.pi * rate * seconds), bend_range)))
            part.bends.append((tick + length, 0))
        previous = note


def echo_of(sk: Sketch, lead: Part, name: str, pan: float) -> Part:
    """The lead repeated a dotted quarter later, softer, darker and wider in
    the room, on the other side: an echo, its bends with it."""
    echo = sk.part(name, lead.instrument, "echo", pan, 0.55, TONES["echo"])
    for tick, note, velocity, length in lead.notes:
        echo.add(tick + ECHO, note, velocity - 14, length)
    echo.bends = [(t + ECHO, v) for t, v in lead.bends]
    return echo


def build_band(sk: Sketch, lead: str = "nylon", drums: str = "cajon") -> None:
    """The second production: two guitars interlocking (the archtop's strum
    with its chucks on the left, Iowa's nylon stabs on the right), the bass
    warm and an octave down, the cajón (or the kit) with congas and a
    shaker, strings in the refrains, and the lead (the nylon guitar, or
    Emilyguitar) with vibrato, slides and hammer-ons, and its echo."""
    intro_end = sk.intro - sk.bar
    if drums == "cajon":
        cj = sk.part("cajon", "cajon", "cajon", 0.0, 0.15, TONES["cajon"])
        cajon_rumba(sk, cj, 84, intro_end, sk.end)
        cg = sk.part("congas", "vc-congas", "congas", -0.35, 0.22, TONES["vc-congas"])
        congas_vc(sk, cg, 76, sk.starts[0], sk.end)
        sh = sk.part("maracas", "vc-shaker", "maracas", 0.35, 0.2, TONES["vc-shaker"])
        shaker_rumba(sk, sh, 56, 0, sk.end, VC_SHAKE_DOWN, VC_SHAKE_UP)
    else:
        kit = sk.part("kit", "virtuosity", "kit", 0.0, 0.2, TONES["kit-warm"])
        kit_rumba(sk, kit, 64, 0, sk.end)
        cg = sk.part("congas", "virtuosity", "congas", -0.35, 0.22, TONES["virtuosity-congas"])
        congas_rumba(sk, cg, 70, sk.starts[0], sk.end)
        sh = sk.part("maracas", "virtuosity", "maracas", 0.35, 0.2, TONES["rumba-shaker"])
        sh.gain_db = -21.0  # PaSST heard maracas 0.14 at -18
        shaker_rumba(sk, sh, 52, 0, sk.end, V_SHAKE_DOWN, V_SHAKE_UP)
    g = sk.part("guitar", "shiny", "guitar", -0.5, 0.15, TONES["steel-strum"])
    strum_steel(sk, g, 84, 0, sk.end)
    st = sk.part("stabs", "iowa-nylon", "stabs", 0.5, 0.18, TONES["nylon-stabs"])
    stabs_nylon(sk, st, 80, 0, sk.end)
    b = sk.part("bass", "fashionbass", "bass", 0.0, 0.03, TONES["warm-bass"])
    bass_rumba(sk, b, 84, 0, sk.end)
    va = sk.part("violas", "violas", "pad", -0.3, 0.6, TONES["violas"])
    vc = sk.part("cellos", "cellos", "pad", 0.3, 0.55, TONES["cellos"])
    for start in sk.starts:
        string_pad(sk, va, vc, 36, start + 8 * sk.bar, start + 16 * sk.bar, [])
    instrument, tone, bend_range = {"nylon": ("iowa-nylon", "lead-nylon", 200),
                                    "electric": ("emily", "lead-electric-2", 1200)}[lead]
    ld = sk.part("lead", instrument, "melody", -0.05, 0.35, TONES[tone])
    lead_line(sk, ld, 100, harmony=True, hammer=True)
    ending(sk, sk.parts, 66)
    root = parse(sk.tune.final or sk.tune.chords[-1][-1])[0]
    ld.add(sk.end + 30, nearest(root, 69, 64, 76), 84 if lead == "nylon" else 70, 6 * TICKS)
    for i, n in enumerate(voice_lead(None, sk.tune.final or sk.tune.chords[-1][-1], 3, 59, 76, 67)):
        st.add(sk.end + 20 * i, n, 72 - 3 * i, 6 * TICKS)
    if drums == "cajon":
        cj.add(sk.end, CAJON_BASS, 90, EIGHTH)
        cj.add(sk.end, CAJON_SLAP, 80, EIGHTH)
        cg.add(sk.end, VC_TUMBA_OPEN, 76, EIGHTH)
    else:
        kit.add(sk.end, V_CRASH, 80, 6 * TICKS)
        kit.add(sk.end, V_KICK, 80, EIGHTH)
    expressive(sk, ld, bend_range, 22 if lead == "nylon" else 26, 5.5 if lead == "nylon" else 4.8, 0.25)
    echo_of(sk, ld, "echo", 0.4)


# Louder than the engine's -16 LUFS (the references: -12.7 to -15.1), the
# limiter allowed 4 dB (render_bossa.py reads it from mix.json)
LOUD = {"loudness": {"target": -15.0, "most_limiting_db": 4.0, "quietest": -17.0}}
STYLES = {
    "rumba-moc": Style("Rumba mộc", "nang-som", 96, 2.2, 0.32, lambda sk: build_band(sk, "nylon", "cajon"),
                       "Rumba mộc: guitar nylon dẫn (rung, vuốt, láy, tiếng vọng); guitar dây sắt quạt có chặn "
                       "dây bên trái, guitar nylon bắt nhịp bên phải; cajón, conga, shaker; bass ấm; dàn dây "
                       "ở điệp khúc.", extra=LOUD, passes=2),
    "rumba-trong": Style("Rumba trống", "nang-som", 96, 2.2, 0.32, lambda sk: build_band(sk, "nylon", "kit"),
                         "Như Rumba mộc, trống jazz nhẹ thay cajón.", extra=LOUD, passes=2),
    # the electric lead: PaSST heard Emilyguitar's clean lead as keys (piano 0.07), picked soft or hard
    "rumba-dien": Style("Rumba guitar điện", "nang-som", 96, 2.2, 0.32,
                        lambda sk: build_band(sk, "electric", "kit"),
                        "Như Rumba mộc, guitar điện dẫn và trống jazz nhẹ thay cajón.", extra=LOUD, passes=2),
    "rumba-guitar": Style("Rumba guitar", "nang-som", 95, 2.0, 0.36, lambda sk: build(sk, "nylon"),
                          "Hòa tấu rumba: guitar nylon dẫn giai điệu, guitar quạt, bass điện, trống, shaker, conga.",
                          passes=2),
    "rumba-guitar-fp": Style("Rumba guitar (FreePats)", "nang-som", 95, 2.0, 0.36,
                             lambda sk: build(sk, "nylon", "nylon-fp"),
                             "Như Rumba guitar, hai cây guitar nylon của FreePats.", passes=2),
    "rumba-guitar-dien": Style("Rumba guitar điện", "nang-som", 95, 2.0, 0.36, lambda sk: build(sk, "electric"),
                               "Như Rumba guitar, guitar điện (chorus, rung nhẹ) dẫn giai điệu.", passes=2),
    "rumba-sax": Style("Rumba sax", "nang-som", 95, 2.0, 0.36, lambda sk: build(sk, "sax"),
                       "Như Rumba guitar, kèn saxophone dẫn giai điệu.", passes=2),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--styles", nargs="+", default=list(STYLES), choices=list(STYLES))
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    for name in args.styles:
        make(name, args.out, args.seed, styles=STYLES, tunes=TUNES, roles=ROLES, instruments=INSTRUMENTS)


if __name__ == "__main__":
    main()
