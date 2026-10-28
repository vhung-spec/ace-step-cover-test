"""A carol harmonized as the hymnals of the 19th century harmonize their
tunes, for the church styles (arrange.py): four voices, soprano (the tune),
alto, tenor and bass, a chord on each beat, by the rules of common-practice
harmony. Two steps, each the best of all its possibilities, found by dynamic
programming (Viterbi) over the beats of a verse:

- harmonize(song): the chords, beat by beat, each with its bass (its root,
  or after a slash another of its tones: G/B). Every chord holds the tune's
  note on its beat (the notes between beats go free, as passing notes); the
  chords move as functional harmony moves (I to IV or ii, to V, to I; vi
  after V for a deceptive turn; a dominant seventh, now and then a secondary
  dominant); they keep near the carol's own chords and keep its cadences (V
  to I at the end, I or V where a phrase ends); and the bass, in root
  position or in inversions (I6, V6, ii6, V4/2 falling to I6, the cadential
  6/4 before V, IV6/4 over a held tonic), moves by step or by a fourth or a
  fifth, never by a tritone, and never in fifths or octaves with the tune.
- voices(song): the alto, tenor and bass notes of every beat under the
  tune: each chord complete (its root and third, a seventh chord's
  seventh), the root doubled rather than the third, never the leading tone
  or the seventh; each voice in its range and within an octave of the voice
  above, none crossing another; tones two chords share held, the other
  voices moving to the nearest tone; no two voices in parallel fifths or
  octaves; a seventh falling and a leading tone rising to its resolution.

The carols are in major keys; a carol's key is its first chord's root.
"""

import math

NOTE_CLASSES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
NAMES = ("C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B")
KINDS = {"": (0, 4, 7), "m": (0, 3, 7), "dim": (0, 3, 6), "7": (0, 4, 7, 10), "m7": (0, 3, 7, 10),
         "maj7": (0, 4, 7, 11), "sus4": (0, 5, 7), "7sus4": (0, 5, 7, 10)}

# The chords a hymn tune is harmonized with: (degree, root above the tonic,
# kind, how much less usual it is than the plain I, IV and V).
CHOICES = (("I", 0, "", 0.0), ("ii", 2, "m", 0.15), ("iii", 4, "m", 0.4), ("IV", 5, "", 0.0), ("V", 7, "", 0.0),
           ("vi", 9, "m", 0.15), ("vii", 11, "dim", 0.5), ("V7", 7, "7", 0.1), ("ii7", 2, "m7", 0.35),
           ("V/V", 2, "7", 0.6), ("V/vi", 4, "7", 0.7), ("V/ii", 9, "7", 0.8), ("V/IV", 0, "7", 0.8))
# How naturally one chord follows another (0 the most natural); pairs not
# listed are unusual. C64 is the cadential six-four (I over the fifth, a
# dominant in all but name), P64 the pedal six-four (IV over a held tonic).
OWN = 0.4  # to or from one of the carol's own chords that CHOICES lacks
FOLLOWS = {
    "I": {"I": 0.0, "ii": 0.3, "iii": 1.0, "IV": 0.0, "V": 0.1, "vi": 0.25, "vii": 0.6, "V7": 0.2, "ii7": 0.4,
          "V/V": 0.6, "V/vi": 0.8, "V/ii": 0.9, "V/IV": 0.5, "C64": 0.6, "P64": 0.2},
    "ii": {"ii": 0.0, "V": 0.0, "V7": 0.0, "vii": 0.4, "ii7": 0.2, "C64": 0.0, "I": 1.2, "IV": 1.4, "V/V": 1.2},
    "ii7": {"ii7": 0.0, "V": 0.0, "V7": 0.0, "vii": 0.5, "C64": 0.0, "I": 1.4},
    "iii": {"iii": 0.0, "vi": 0.1, "IV": 0.3, "ii": 0.9, "V/ii": 1.0, "I": 1.5},
    "IV": {"IV": 0.0, "V": 0.0, "V7": 0.1, "I": 0.3, "ii": 0.3, "ii7": 0.3, "vii": 0.5, "C64": 0.0, "V/V": 0.6,
           "vi": 1.4},
    "V": {"V": 0.0, "I": 0.0, "V7": 0.1, "vi": 0.6, "iii": 1.2, "V/vi": 0.8, "IV": 2.0},
    "V7": {"V7": 0.0, "I": 0.0, "vi": 0.8, "V/vi": 1.2},
    "vi": {"vi": 0.0, "ii": 0.1, "IV": 0.1, "ii7": 0.2, "V": 0.3, "V7": 0.5, "V/V": 0.6, "C64": 0.5, "iii": 0.6,
           "I": 1.0},
    "vii": {"vii": 0.0, "I": 0.0, "vi": 1.2},
    "V/V": {"V/V": 0.0, "V": 0.0, "V7": 0.0, "C64": 0.0},
    "V/vi": {"V/vi": 0.0, "vi": 0.0},
    "V/ii": {"V/ii": 0.0, "ii": 0.0, "ii7": 0.0},
    "V/IV": {"V/IV": 0.0, "IV": 0.0},
    "C64": {"C64": 0.0, "V": 0.0, "V7": 0.0},
    "P64": {"P64": 0.0, "I": 0.0},
}
UNUSUAL = 3.0
BASS_MOTION = {0: 0.1, 1: 0.0, 2: 0.0, 3: 0.2, 4: 0.25, 5: 0.15, 6: 3.0}  # by its interval, in semitones (0-6)
# The voices' ranges (MIDI): bass E2-D4, tenor C3-G4, alto F3-D5.
BASS, TENOR, ALTO = (40, 62), (48, 67), (53, 74)


def pitch_class(name: str) -> int:
    return (NOTE_CLASSES[name[0]] + {"#": 1, "b": -1}.get(name[1:2], 0)) % 12


def parse(name: str) -> tuple[int, tuple, int]:
    """A chord name's root, intervals and bass (the root, or the note after a slash)."""
    body, _, bass = name.partition("/")
    root, kind = pitch_class(body), body[1:]
    if kind[:1] in ("#", "b"):
        kind = kind[1:]
    return root, KINDS[kind], pitch_class(bass) if bass else root


def tones(root: int, intervals: tuple) -> set:
    return {(root + i) % 12 for i in intervals}


def beat_notes(song) -> list[dict]:
    """What the tune does on each beat of a verse: the note sounding as the
    beat begins (onset, None in a rest), whether it began before (held), and
    the notes that begin within the beat (inner: note, eighths, and whether
    it moves by step from the note before and to the note after). The
    pickup of the next verse sounds in the last bar, as it does between
    verses (the last note, if it reached there, ends where it begins)."""
    verse = len(song.chords) * song.beats * song.beat_eighths
    notes, at = [], -song.pickup
    for note, eighths in song.melody:
        notes.append((at, note, eighths))
        at += eighths
    wrapped = [(start + verse, note, eighths) for start, note, eighths in notes if start < 0]
    played = [(s, n, min(e, verse - song.pickup - s) if song.pickup else e) for s, n, e in notes if s >= 0]
    timeline = sorted(played + wrapped, key=lambda item: item[0])
    sounding = [(s, n, e) for s, n, e in timeline if n is not None and e > 0]
    beats = []
    for i in range(len(song.chords) * song.beats):
        start, end = i * song.beat_eighths, (i + 1) * song.beat_eighths
        on = [(s, n, e) for s, n, e in timeline if s <= start + 1e-9 < s + e]
        onset = on[-1][1] if on else None
        held = bool(on) and on[-1][0] < start - 1e-9
        inner = []
        for k, (s, n, e) in enumerate(sounding):
            if start + 1e-9 < s < end - 1e-9:
                before = sounding[k - 1][1] if k else n
                after = sounding[k + 1][1] if k + 1 < len(sounding) else n
                inner.append((n, e, abs(n - before) <= 2 and abs(after - n) <= 2))
        beats.append({"onset": onset, "held": held, "inner": inner})
    return beats


def last_note_beat(song) -> int:
    """The beat on which the verse's last note begins."""
    at, last = -song.pickup, 0
    for note, eighths in song.melody:
        if note is not None and at >= 0:
            last = at
        at += eighths
    return int(last // song.beat_eighths)


def leading_tone(root: int, intervals: tuple, tonic: int) -> int | None:
    """The tone of a chord that leads up a semitone to the next chord's root:
    the third of V or of any dominant seventh (V7, V/V...), the root of vii."""
    step = (root - tonic) % 12
    if step == 11 and intervals == KINDS["dim"]:
        return root
    if intervals[:2] == (0, 4) and (step == 7 or len(intervals) == 4):
        return (root + 4) % 12
    return None


def _states(tonic: int, extra: list) -> list[tuple]:
    """Every (degree, root, intervals, inversion, bass, cost, label) a beat may
    take: CHOICES, and the carol's own chords that are not among them (extra:
    (root, intervals) pairs, degree "own")."""
    states = []
    choices = [(degree, (tonic + step) % 12, KINDS[kind], cost) for degree, step, kind, cost in CHOICES]
    known = {(root, intervals) for _, root, intervals, _ in choices}
    choices += [("own", root, intervals, 0.2) for root, intervals in extra if (root, intervals) not in known]
    for degree, root, intervals, cost in choices:
        for inversion in range(len(intervals)):
            if inversion == 0:
                extra, label = (2.0 if degree == "vii" else 0.0), degree
            elif inversion == 1:
                extra, label = {"vii": 0.0, "iii": 1.0}.get(degree, 0.3 if len(intervals) == 3 else 0.4), degree
            elif len(intervals) == 4:  # a seventh chord's 4/3 and 4/2
                extra, label = (0.6 if degree == "V7" else 1.2), degree
            elif degree in ("I", "IV"):  # the only six-fours: cadential and pedal
                extra, label = 0.3, "C64" if degree == "I" else "P64"
            else:
                continue
            states.append((degree, root, intervals, inversion, (root + intervals[inversion]) % 12,
                           cost + extra, label))
    return states


def _name(root: int, intervals: tuple, bass: int) -> str:
    kind = next(k for k, v in KINDS.items() if v == intervals)
    return NAMES[root] + kind + ("" if bass == root else "/" + NAMES[bass])


def cadence_beats(song) -> set:
    """The beats a phrase comes to rest on: each phrase's last bar's downbeat."""
    bars = song.breaths or range(3, len(song.chords), 4)
    return {bar * song.beats for bar in bars}


def harmonize(song) -> list[list[str]]:
    """The carol's chords as a hymnal harmonizes it: bar by bar, a chord
    name for each beat, its bass after a slash where it is not its root."""
    tonic = parse(song.chords[0][0])[0]
    beats = beat_notes(song)
    own = sorted({parse(name)[:2] for bar in song.chords for name in bar})
    states = _states(tonic, own)
    leading = (tonic + 11) % 12
    count = len(beats)
    final = last_note_beat(song)
    last_bars = (len(song.chords) - 2) * song.beats
    cadences = cadence_beats(song)

    def emission(i: int, state: tuple) -> float:
        degree, root, intervals, inversion, bass, cost, label = state
        beat, chord = beats[i], tones(root, intervals)
        if i >= final:
            return 0.0 if (degree, inversion) == ("I", 0) else 20.0
        if beat["onset"] is not None and beat["onset"] % 12 not in chord:
            cost += 8.0 if beat["held"] else 4.0
        for note, eighths, stepwise in beat["inner"]:
            if note % 12 not in chord:
                cost += 3.0 if eighths >= song.beat_eighths else 0.25 if stepwise else 1.0
        original = song.chords[i // song.beats][i % song.beats]
        o_root, o_intervals, _ = parse(original)
        if degree == "own" and (o_root, o_intervals) != (root, intervals):
            cost += UNUSUAL  # an own chord only where the carol has it
        elif (o_root, o_intervals[:3]) != (root, intervals[:3]):
            shared = len(tones(o_root, o_intervals[:3]) & tones(root, intervals[:3]))
            same_colour = o_intervals[1] == intervals[1] and (len(o_intervals) == 4) == (len(intervals) == 4)
            weight = 2.0 if i >= last_bars or i in cadences else 1.0
            cost += (1.4 if shared < 2 else 0.3 if same_colour else 0.8) * weight
        if i in cadences:
            cost += (0.0 if label in ("I", "V", "V7") else 0.6 if label == "vi" else 1.2) + (0.6 if inversion else 0)
        if label == "C64" and not any(c - i in (1, 2) for c in cadences | {final}):
            cost += 2.5  # a cadential six-four only just before a cadence (its V on the cadence or before)
        if i == final - 1:
            cost += 0.0 if (label in ("V", "V7") and inversion == 0) else 4.0
        if i == 0:
            cost += 0.0 if (degree, inversion) == ("I", 0) else 1.5
        if beat["onset"] is not None and beat["onset"] % 12 == bass:  # the tune doubles the bass
            if bass == leading and degree in ("V", "V7", "vii"):
                cost += 3.0
            elif inversion == 1 and intervals[1] == 4:
                cost += 0.8  # a major chord's third doubled
        return cost

    def transition(i: int, a: tuple, b: tuple) -> float:
        _, root_a, ints_a, inv_a, bass_a, _, label_a = a
        degree_b, root_b, ints_b, inv_b, bass_b, _, label_b = b
        beat = beats[i]
        if (root_a, ints_a, inv_a) == (root_b, ints_b, inv_b):  # the chord held
            if beat["onset"] is None or beat["held"]:
                return 0.0
            return 1.0 if i % song.beats == 0 else 0.6  # a hymn's bass moves as its tune does
        cost = OWN if "own" in (label_a, label_b) else FOLLOWS[label_a].get(label_b, UNUSUAL)
        if (root_a, ints_a) == (root_b, ints_b):
            cost = 0.05  # the same chord, its bass moving to another of its tones
        if label_a == "C64" and (label_b not in ("V", "V7") or bass_b != bass_a):
            cost += 2.0
        if label_b == "P64" and (label_a != "I" or inv_a or bass_b != bass_a):
            cost += 2.0
        if label_a == "P64" and (label_b != "I" or inv_b or bass_b != bass_a):
            cost += 2.0
        if label_b == "C64" and i % song.beats != 0 and (i + 1) % song.beats == 0:
            cost += 1.0  # a cadential six-four falls on a stronger beat than its V
        if beat["held"] or beat["onset"] is None:
            cost += 0.4  # the harmony moves under a held note
        cost += BASS_MOTION[min((bass_b - bass_a) % 12, (bass_a - bass_b) % 12)]
        if label_a in ("V", "V7") and inv_a == 1 and bass_b != tonic:
            cost += 1.0  # the leading tone in the bass rises to the tonic
        if label_a == "V7" and inv_a == 3 and not (degree_b == "I" and inv_b == 1):
            cost += 2.0  # V4/2's seventh, in the bass, falls to I6
        s1, s2 = beats[i - 1]["onset"], beat["onset"]
        if s1 is not None and s2 is not None and s1 != s2 and bass_a != bass_b:
            gap1, gap2 = (s1 - bass_a) % 12, (s2 - bass_b) % 12
            if gap1 == gap2 and gap1 in (0, 7):
                cost += 10.0  # parallel octaves or fifths with the tune
            up_bass = (bass_b - bass_a) % 12 <= 6
            if (s2 > s1) == up_bass:
                if gap2 in (0, 7) and abs(s2 - s1) > 2:
                    cost += 0.8  # into an octave or fifth by similar motion, the tune leaping
            else:
                cost -= 0.05  # contrary motion
        return cost

    best = [emission(0, s) for s in states]
    back = []
    for i in range(1, count):
        here, links = [], []
        for b in states:
            e = emission(i, b)
            if e >= 20.0 and i >= final:
                here.append(math.inf)
                links.append(0)
                continue
            costs = [best[k] + transition(i, a, b) for k, a in enumerate(states)]
            k = min(range(len(states)), key=costs.__getitem__)
            here.append(costs[k] + e)
            links.append(k)
        best = here
        back.append(links)
    k = min(range(len(states)), key=best.__getitem__)
    path = [k]
    for links in reversed(back):
        k = links[k]
        path.append(k)
    path.reverse()
    names = [_name(states[k][1], states[k][2], states[k][4]) for k in path]
    return [names[bar * song.beats:(bar + 1) * song.beats] for bar in range(len(song.chords))]


def _voicings(root: int, intervals: tuple, bass: int, soprano: int | None, leading: int | None,
              strict: bool = True) -> list:
    """Every (bass, tenor, alto, cost) for a chord under a soprano note; not
    strict, the chord may lack its third and the voices spread wider, at a cost."""
    chord = tones(root, intervals)
    seventh = (root + intervals[3]) % 12 if len(intervals) == 4 else None
    third = (root + intervals[1]) % 12
    fifth = (root + intervals[2]) % 12
    top = ALTO[1] if soprano is None else min(ALTO[1], soprano)
    found = []
    for b in range(BASS[0], BASS[1] + 1):
        if b % 12 != bass:
            continue
        for t in range(max(TENOR[0], b), TENOR[1] + 1):
            if t % 12 not in chord or (strict and t - b > 19):
                continue
            for a in range(max(ALTO[0] - (0 if strict else 5), t), top + 1):
                if a % 12 not in chord or (strict and (a - t > 12 or (soprano is not None and soprano - a > 12))):
                    continue
                voices = [b, t, a] + ([soprano] if soprano is not None else [])
                classes = [v % 12 for v in voices]
                cost = 0.0 if strict else 10.0
                if root not in classes or third not in classes:
                    if strict:
                        continue
                    cost += 8.0
                if seventh is not None and seventh not in classes:
                    cost += 3.0
                if fifth not in classes:
                    cost += 0.3 if seventh is not None else 0.8
                for pc in set(classes):
                    times = classes.count(pc)
                    if times < 2:
                        continue
                    if pc == leading or pc == seventh:
                        cost += 6.0
                    elif pc == third and intervals[1] == 4:
                        cost += 1.5
                    elif pc == fifth:
                        cost += 0.3
                    if times > 2:
                        cost += 0.8
                cost += 1.2 * ((a == t) + (soprano is not None and a == soprano)) + 1.0 * (t == b)
                cost += 0.04 * (abs(a - 64) + abs(t - 57))
                found.append((b, t, a, cost))
    return found


def _motion(x: int, y: int) -> float:
    """An inner voice's move: held best, then a step, a third, a fourth or fifth; wider seldom."""
    d = abs(y - x)
    return 0.0 if d == 0 else 0.15 * d if d <= 2 else 0.5 + 0.1 * d if d <= 4 else 1.2 + 0.1 * (d - 5) if d <= 7 \
        else 4.0


def _bass_motion(x: int, y: int) -> float:
    d = abs(y - x)
    return {0: 0.2, 1: 0.0, 2: 0.0, 3: 0.2, 4: 0.2, 5: 0.2, 7: 0.3, 12: 0.6}.get(d, 1.5)


def _between(prev: tuple, here: tuple, chords: tuple, tonic: int) -> float:
    """The cost of moving from one voicing (s, a, t, b) to the next."""
    (s1, a1, t1, b1), (s2, a2, t2, b2) = prev, here
    (root1, ints1, _), (root2, ints2, _) = chords
    cost = _motion(a1, a2) + _motion(t1, t2) + _bass_motion(b1, b2)
    voices1, voices2 = (s1, a1, t1, b1), (s2, a2, t2, b2)
    for x in range(4):
        for y in range(x + 1, 4):
            hi1, lo1, hi2, lo2 = voices1[x], voices1[y], voices2[x], voices2[y]
            if None in (hi1, lo1, hi2, lo2) or hi1 == hi2 or lo1 == lo2:
                continue
            if (hi1 - lo1) % 12 == (hi2 - lo2) % 12 and (hi1 - lo1) % 12 in (0, 7):
                cost += 12.0  # parallel octaves or fifths
            elif x == 0 and y == 3 and (hi2 - hi1) * (lo2 - lo1) > 0 and (hi2 - lo2) % 12 in (0, 7) \
                    and abs(hi2 - hi1) > 2:
                cost += 1.0  # hidden octaves or fifths in the outer voices
    if s1 is not None and a2 > s1:
        cost += 1.0  # the voices overlap
    cost += (t2 > a1) + (a2 < t1) + (b2 > t1) + (t2 < b1)
    if (root1, ints1) != (root2, ints2):
        if len(ints1) == 4:  # a seventh falls by step (or stays, shared by the next chord)
            seventh = (root1 + ints1[3]) % 12
            for v1, v2 in ((a1, a2), (t1, t2), (b1, b2)):
                if v1 % 12 == seventh and not (0 <= v1 - v2 <= 2):
                    cost += 2.0
        if ints1[1] == 4 and len(ints1) >= 3 and (root2 - root1) % 12 == 5:  # a dominant's third, its leading tone
            leading = (root1 + 4) % 12
            for v1, v2 in ((a1, a2), (t1, t2)):
                if v1 % 12 == leading and v2 != v1 + 1:
                    cost += 0.4
    return cost


def voices(song, chords: list | None = None) -> list[tuple]:
    """(soprano, alto, tenor, bass) on each beat of a verse (the soprano the
    tune's note as the beat begins, None in a rest), for its chords (by
    default harmonize(song)). The first beat is voiced to follow the last,
    as one verse follows another."""
    chords = chords or harmonize(song)
    tonic = parse(song.chords[0][0])[0]
    flat = [parse(name) for bar in chords for name in bar]
    sopranos = [b["onset"] for b in beat_notes(song)]
    options = []
    for (root, intervals, bass), soprano in zip(flat, sopranos):
        leading = leading_tone(root, intervals, tonic)
        options.append(_voicings(root, intervals, bass, soprano, leading)
                       or _voicings(root, intervals, bass, soprano, leading, strict=False))

    def solve(start: tuple | None) -> list[tuple]:
        best = []
        for b, t, a, cost in options[0]:
            here = (sopranos[0], a, t, b)
            best.append(cost + (_between(start, here, (flat[-1], flat[0]), tonic) if start else 0.0))
        back = []
        for i in range(1, len(options)):
            here_costs, links = [], []
            for b, t, a, cost in options[i]:
                here = (sopranos[i], a, t, b)
                prev_s = sopranos[i - 1]
                costs = [best[k] + _between((prev_s, pa, pt, pb), here, (flat[i - 1], flat[i]), tonic)
                         for k, (pb, pt, pa, _) in enumerate(options[i - 1])]
                k = min(range(len(costs)), key=costs.__getitem__)
                here_costs.append(costs[k] + cost)
                links.append(k)
            best = here_costs
            back.append(links)
        k = min(range(len(best)), key=best.__getitem__)
        path = [k]
        for links in reversed(back):
            k = links[k]
            path.append(k)
        path.reverse()
        return [(sopranos[i], options[i][k][2], options[i][k][1], options[i][k][0]) for i, k in enumerate(path)]

    first = solve(None)
    return solve(first[-1])


def amen(song, last: tuple) -> list[tuple]:
    """The Amen sung after the last verse, IV then I (a plagal cadence):
    (soprano, alto, tenor, bass) for each, voiced from the verse's last chord
    (last). The soprano keeps its note where IV holds it (the tonic is IV's
    fifth), or steps to IV's nearest tone and back (mi, fa, mi)."""
    tonic = parse(song.chords[0][0])[0]
    soprano = last[0] if last[0] is not None else last[1]
    major = KINDS[""]
    four = ((tonic + 5) % 12, major, (tonic + 5) % 12)
    one = (tonic, major, tonic)
    up = soprano if soprano % 12 in tones(four[0], major) else min(
        (n for n in range(soprano - 2, soprano + 3) if n % 12 in tones(four[0], major)),
        key=lambda n: (abs(n - soprano), -n))
    voiced, previous, chord = [], last, one
    for target, top in ((four, up), (one, soprano)):
        options = _voicings(*target, top, None) or _voicings(*target, top, None, strict=False)
        b, t, a, _ = min(options, key=lambda o: o[3] + _between(previous, (top, o[2], o[1], o[0]),
                                                                  (chord, target), tonic))
        previous, chord = (top, a, t, b), target
        voiced.append(previous)
    return voiced
