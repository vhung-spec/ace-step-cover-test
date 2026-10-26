"""Writes the test's source: "We Wish You a Merry Christmas" (a traditional
carol, public domain), first verse twice, arranged here for piano, as MIDI
and as the 48 kHz stereo WAV ACE-Step covers (rendered with FluidSynth),
plus melody.json, the melody's notes and times, for scoring:

    python make_source.py out/source [--arrangement v2] [--soundfont path.sf2]

Arrangement v1 is plain (even loudness, an oom-pah-pah left hand). v2 plays it
like a person: a soft intro, flowing broken chords, a fuller second verse,
sustain pedal, phrase dynamics, small timing and loudness variations, and a
slower last bar.
"""

import argparse
import json
import random
import subprocess
from pathlib import Path

import mido

BPM = 132  # v1
BPM_V2 = 116
TICKS = 480  # per quarter note
# Melody in C major, 3/4: (MIDI note, length in eighths). Pickup "We", then
# "wish you a merry Christmas" ... "and a happy New Year".
MELODY = [
    (67, 2),
    (72, 2), (72, 1), (74, 1), (72, 1), (71, 1),
    (69, 2), (69, 2), (69, 2),
    (74, 2), (74, 1), (76, 1), (74, 1), (72, 1),
    (71, 2), (67, 2), (67, 2),
    (76, 2), (76, 1), (77, 1), (76, 1), (74, 1),
    (72, 2), (69, 2), (67, 1), (67, 1),
    (69, 2), (74, 2), (71, 2),
    (72, 6),
]
# One chord per bar (bass note, then the chord tones), bar 7 splits F | G.
BARS = [
    [(36, (60, 64, 67))],
    [(41, (60, 65, 69))],
    [(38, (62, 66, 69, 72))],
    [(43, (59, 62, 67))],
    [(40, (59, 62, 64, 68))],
    [(45, (60, 64, 69))],
    [(41, (60, 65, 69)), (43, (59, 62, 67))],
    [(36, (60, 64, 67))],
]


def write_carol(path: Path, verses: int = 2) -> list[tuple[int, int, int]]:
    """Piano: the melody over a waltz left hand (bass on 1, chord on 2 and 3).
    Returns the melody as (note, tick, length in ticks)."""
    eighth, bar = TICKS // 2, TICKS * 3
    events = []  # (tick, note, velocity, length)
    melody_notes = []
    melody_start = TICKS * 2  # the pickup is the last beat of an empty first bar
    for verse in range(verses):
        start = melody_start + verse * 8 * bar
        melody = list(MELODY)
        if verse < verses - 1:  # the last note makes room for the next pickup
            melody[-1] = (melody[-1][0], 4)
        tick = start
        for note, eighths in melody:
            events.append((tick, note, 88, eighths * eighth - 20))
            melody_notes.append((note, tick, eighths * eighth))
            tick += eighths * eighth
        for index, chords in enumerate(BARS):
            bar_tick = start + TICKS + index * bar
            if len(chords) == 1:
                (bass, tones), = chords
                events.append((bar_tick, bass, 64, TICKS - 20))
                for beat in (1, 2):
                    events += [(bar_tick + beat * TICKS, n, 52, TICKS - 40) for n in tones]
            else:
                (bass1, tones1), (bass2, tones2) = chords
                events.append((bar_tick, bass1, 64, TICKS - 20))
                events.append((bar_tick + TICKS, bass2, 60, TICKS - 20))
                events += [(bar_tick + 2 * TICKS, n, 52, TICKS - 40) for n in tones2]
    messages = []
    for tick, note, velocity, length in events:
        messages.append((tick + length, 0, mido.Message("note_off", note=note, velocity=0)))
        messages.append((tick, 1, mido.Message("note_on", note=note, velocity=velocity)))
    midi = mido.MidiFile(ticks_per_beat=TICKS)
    track = mido.MidiTrack()
    midi.tracks.append(track)
    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM)))
    track.append(mido.MetaMessage("time_signature", numerator=3, denominator=4))
    track.append(mido.Message("program_change", program=0))
    now = 0
    for tick, _, message in sorted(messages, key=lambda m: (m[0], m[1])):
        track.append(message.copy(time=tick - now))
        now = tick
    track.append(mido.MetaMessage("end_of_track", time=TICKS * 3))  # let it ring
    path.parent.mkdir(parents=True, exist_ok=True)
    midi.save(path)
    return melody_notes


def write_carol_v2(path: Path) -> list[tuple[int, int, int]]:
    """Expressive piano: intro (the last phrase, an octave up, soft), verse 1
    over flowing broken chords, verse 2 with the melody in octaves over octave
    bass and full chords, a held last note. Returns the melody as (note,
    tick, length in ticks)."""
    rng = random.Random(7)
    eighth, bar = TICKS // 2, TICKS * 3
    events, melody_notes, pedal = [], [], []

    def play(tick: int, note: int, velocity: int, length: int, melody: bool = False) -> None:
        tick = max(0, tick + rng.randint(-6, 6))  # a person is never exactly on the grid
        velocity = max(20, min(118, velocity + rng.randint(-4, 4)))
        events.append((tick, note, velocity, length))
        if melody:
            melody_notes.append((note, tick, length))

    def broken_chord(bar_tick: int, chords: list, velocity: int) -> None:
        if len(chords) == 1:
            (bass, tones), = chords
            play(bar_tick, bass, velocity + 8, bar - 40)
            order = [tones[0], tones[1], tones[-1], tones[1]]
            for i, note in enumerate(order):
                play(bar_tick + TICKS + i * eighth, note, velocity, eighth * 2)
        else:
            (bass1, tones1), (bass2, tones2) = chords
            play(bar_tick, bass1, velocity + 8, TICKS - 20)
            play(bar_tick + TICKS // 2, tones1[-1], velocity, eighth)
            play(bar_tick + TICKS, bass2, velocity + 6, TICKS * 2 - 40)
            for i, note in enumerate([tones2[0], tones2[1], tones2[-1]]):
                play(bar_tick + TICKS + (i + 1) * eighth, note, velocity, eighth * 2)

    def full_chords(bar_tick: int, chords: list, velocity: int) -> None:
        if len(chords) == 1:
            (bass, tones), = chords
            play(bar_tick, bass, velocity + 8, bar - 40)
            play(bar_tick, bass - 12, velocity + 4, bar - 40)
            for beat in (1, 2):
                for note in tones:
                    play(bar_tick + beat * TICKS, note, velocity, TICKS - 60)
        else:
            (bass1, tones1), (bass2, tones2) = chords
            play(bar_tick, bass1, velocity + 8, TICKS - 20)
            play(bar_tick, bass1 - 12, velocity + 4, TICKS - 20)
            play(bar_tick + TICKS, bass2, velocity + 8, TICKS * 2 - 40)
            play(bar_tick + TICKS, bass2 - 12, velocity + 4, TICKS * 2 - 40)
            for note in tones2:
                play(bar_tick + 2 * TICKS, note, velocity, TICKS - 60)

    # Intro (2 bars): "happy New Year" an octave up, soft, then the pickup.
    tick = 0
    for note, eighths in [(81, 2), (86, 2), (83, 2), (84, 4)]:
        play(tick, note, 54, eighths * eighth - 30, melody=True)
        tick += eighths * eighth
    broken_chord(0, BARS[6], 40)
    broken_chord(bar, BARS[7], 40)

    for verse in range(2):
        start = 2 * bar - TICKS + verse * 8 * bar  # the pickup: beat 3 before bar 1
        melody = list(MELODY)
        if verse == 0:
            melody[-1] = (melody[-1][0], 4)  # room for the next pickup
        else:
            melody[-1] = (melody[-1][0], 12)  # held, slowing to the end
        tick = start
        for index, (note, eighths) in enumerate(melody):
            # phrase dynamics: rise to the middle of the verse, then ease off
            shape = 1 - abs(index - len(melody) / 2) / (len(melody) / 2)
            if verse == 0:
                play(tick, note, int(60 + 14 * shape), eighths * eighth - 20, melody=True)
            else:
                play(tick, note, int(84 + 14 * shape), eighths * eighth - 20, melody=True)
                play(tick, note - 12, int(70 + 12 * shape), eighths * eighth - 20)
            tick += eighths * eighth
        for index, chords in enumerate(BARS):
            bar_tick = start + TICKS + index * bar
            if verse == 0:
                broken_chord(bar_tick, chords, 44 + 2 * min(index, 7 - index))
            elif index < 7:
                full_chords(bar_tick, chords, 56 + 2 * min(index, 7 - index))
            else:  # last bar: one long C major chord
                for note in (24, 36, 48, 55, 60, 64, 67):
                    play(bar_tick, note, 62, bar * 2)
    end = max(t + length for t, _, _, length in events)  # after the held last note
    for bar_tick in range(0, end, bar):  # pedal down just after each bar starts
        pedal.append((bar_tick + 20, 127))
        pedal.append((bar_tick + bar - 15, 0))

    messages = []
    for tick, note, velocity, length in events:
        messages.append((tick + length, 0, mido.Message("note_off", note=note, velocity=0)))
        messages.append((tick, 1, mido.Message("note_on", note=note, velocity=velocity)))
    for tick, value in pedal:
        messages.append((tick, 0 if value == 0 else 2,
                         mido.Message("control_change", control=64, value=value)))
    midi = mido.MidiFile(ticks_per_beat=TICKS)
    track = mido.MidiTrack()
    midi.tracks.append(track)
    track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM_V2)))
    track.append(mido.MetaMessage("time_signature", numerator=3, denominator=4))
    track.append(mido.Message("program_change", program=0))
    now = 0
    for tick, _, message in sorted(messages, key=lambda m: (m[0], m[1])):
        track.append(message.copy(time=tick - now))
        now = tick
    track.append(mido.MetaMessage("end_of_track", time=TICKS * 4))  # let it ring
    path.parent.mkdir(parents=True, exist_ok=True)
    midi.save(path)
    return sorted(melody_notes, key=lambda n: n[1])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--arrangement", choices=("v1", "v2"), default="v2")
    parser.add_argument("--soundfont", default="/usr/share/sounds/sf2/FluidR3_GM.sf2")
    args = parser.parse_args()
    midi = args.out / "source.mid"
    write, bpm = (write_carol, BPM) if args.arrangement == "v1" else (write_carol_v2, BPM_V2)
    seconds_per_tick = 60 / bpm / TICKS
    melody = [{"pitch": note, "start": round(tick * seconds_per_tick, 3),
               "end": round((tick + length) * seconds_per_tick, 3)}
              for note, tick, length in write(midi)]
    (args.out / "melody.json").write_text(json.dumps(melody))
    raw = args.out / "source-fluidsynth.wav"
    subprocess.run(["fluidsynth", "-ni", "-g", "0.6", "-r", "48000", "-F", str(raw),
                    args.soundfont, str(midi)], check=True, capture_output=True)
    wav = args.out / "source.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-ac", "2", "-ar", "48000",
                    str(wav)], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-q:a", "2",
                    str(args.out / "source.mp3")], check=True)
    raw.unlink()
    print(f"Source ({args.arrangement}, {Path(args.soundfont).name}): {wav} "
          f"({mido.MidiFile(midi).length:.1f} s)")


if __name__ == "__main__":
    main()
