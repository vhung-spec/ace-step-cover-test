"""Writes the test's source: "We Wish You a Merry Christmas" (a traditional
carol, public domain), first verse twice, arranged here for piano, as MIDI
and as the 48 kHz stereo WAV ACE-Step covers (rendered with FluidSynth):

    python make_source.py out/source [--soundfont /usr/share/sounds/sf2/FluidR3_GM.sf2]
"""

import argparse
import subprocess
from pathlib import Path

import mido

BPM = 132
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


def write_carol(path: Path, verses: int = 2) -> Path:
    """Piano: the melody over a waltz left hand (bass on 1, chord on 2 and 3)."""
    eighth, bar = TICKS // 2, TICKS * 3
    events = []  # (tick, note, velocity, length)
    melody_start = TICKS * 2  # the pickup is the last beat of an empty first bar
    for verse in range(verses):
        start = melody_start + verse * 8 * bar
        melody = list(MELODY)
        if verse < verses - 1:  # the last note makes room for the next pickup
            melody[-1] = (melody[-1][0], 4)
        tick = start
        for note, eighths in melody:
            events.append((tick, note, 88, eighths * eighth - 20))
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
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--soundfont", default="/usr/share/sounds/sf2/FluidR3_GM.sf2")
    args = parser.parse_args()
    midi = write_carol(args.out / "source.mid")
    raw = args.out / "source-fluidsynth.wav"
    subprocess.run(["fluidsynth", "-ni", "-g", "0.6", "-r", "48000", "-F", str(raw),
                    args.soundfont, str(midi)], check=True, capture_output=True)
    wav = args.out / "source.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-ac", "2", "-ar", "48000",
                    str(wav)], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-q:a", "2",
                    str(args.out / "source.mp3")], check=True)
    raw.unlink()
    print(f"Source: {wav} ({mido.MidiFile(midi).length:.1f} s)")


if __name__ == "__main__":
    main()
