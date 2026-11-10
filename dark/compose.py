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
- piano: the piano (INSTRUMENTS): upright, felt, grand, kawai (recorded,
  CC0), salamander (recorded, CC-BY 3.0: Alexander Holm), or model, model-dream, model-close, model-grand, model-clear,
  model-bloom, model-wood, model-glass (modelled by dark/piano_model.py
  from the physics of its strings, no recording; built with the pieces);
- style: a named style (STYLES) giving every setting the piece leaves out;
  dem-diu, the user's choice for slow, muffled pieces (dem-diu-h3: as it was
  on the recorded upright, before the modelled piano);
  mo-ao, after the user's reference Dim Window as they chose it: the C5
  Kawai piano on the tune alone, two modelled oboes behind it (mo-ao-c5: on
  C5 with its left hand and a recorded oboe, round 16; mo-ao-glass: its
  first, glassy sound); mo-ao-day, the same piano with the cellos answering
  it and a thin viola line;
  tam-tau, a trio: the Salamander grand on the tune, the cellos answering
  it, a thin viola line (tam-tau-phim: the piano darker, as a keyboard's,
  with a Rhodes layered under it);
- melody_velocity: how hard the tune is struck at dyn 0 and at dyn 1 (40,
  82); velocity_cap: no key struck harder (64 keeps the Yamaha upright on its
  softest, darkest samples, which end at 65);
- loudness: the piece's loudness, LUFS (-16 unless given; YouTube plays
  music at about -14 and never turns a quieter piece up);
- human: {"amount": 0-1, "vary": true}: played as a person plays: the tempo
  breathing with each phrase, the touch and the onsets alive, the melody
  leading the left hand (amount); the left hand following the tune, the
  pedal following the harmony (vary). Absent: the machine's evenness;
- hold: the longest (beats) an accompanying note is held; pedal_beats: the
  pedal taken again this often within a chord (else once a chord); lh_soft:
  the left hand this much softer (velocity), all to keep it light and clear;
- pedal_steps: with vary, the pedal also taken again as the tune steps onto a
  note next to one the pedal still holds, so the two do not beat (a buzz);
- texture, the piano's left hand: arp (broken chords in eighths, up and
  back from a deep bass), flow (lighter: a bass held under two tones above
  it, rocking in eighths), ostinato (three tones of the chord circling in
  eighths in the middle of the keyboard, a low toll on each bar), blocks (the
  chord rolled from a deep octave and held), sparse (a deep note, a soft
  rolled chord after it, an inner tone later in the bar), pulse (a low
  octave beating as a heart does), deep (one soft deep note a chord, held
  while the chord stays), open (a deep bass held, the chord broken
  in eighths an octave and more above it, the low-mids clear), none;
- dyn: 0 (barely touched) to 1 (fully); the melody rises and falls with each
  phrase within it;
- layers: drone (a low tonic and fifth from sfizz's own oscillators,
  instruments/drone.sfz), cello (the chords' bass line, bowed), cello-melody
  (the tune an octave down), strings (soft violas and cellos holding the
  chords), basses (the deepest roots), violin (a solo violin on the tune),
  octave (the piano doubling the tune an octave down), tremolo (the piano
  trembling between two tones of the chord in sixteenths, just above the
  tune), oboe (an oboe softly behind the piano, a slow line of long notes:
  the chords' colour tones, kept clear of the tune; the piece's "oboe" names
  which: oboe, oboe-vib (recorded, straight or with vibrato), oboe-model,
  oboe-model-straight (modelled); oboe_voices 2 adds a second oboe under it),
  cello-answer (the cellos answering the tune where it holds or rests: its
  last notes an octave or two down, every other time mirrored; the bass,
  held, where a section has no tune), viola-pad (the violas holding one
  thin line of the chords' colour tones, clear of the tune and the cellos),
  cello-pizz (the cellos plucking the chord's bass, octave and fifth softly,
  like drops), cello-counter (the cellos singing a slow second line under
  the tune, A2-C4: the chords' colour tones, one long note a chord, each
  nearest the last), viola-end (the violas only at each sentence's end: a long
  low-middle note from the last bar's second beat, moving to the next
  chord for two beats);
- melody_shift: the whole tune moved this many semitones (12: an octave up);
- melody_on (a section's): cello or viola, the cellos or the violas sing that
  section's tune (written in their register) and the piano leaves it; piano
  unless given;
- piano_layer: a second keyboard (INSTRUMENTS) doubling all the piano plays,
  6 dB under it (gains: piano-layer), its tone changed by piano_layer_tone.

The piano breathes on the last beat of every four bars, a section marked
rit slows over its last two bars, and the piece slows into its last chord,
held a bar longer, rolled from the bass. Instruments: VCSL (CC0) for the
pianos, the Salamander Grand Piano (CC-BY 3.0, Alexander Holm), VSCO 2 CE
(CC0) for the strings and the oboe, fetched when rendering
(fetch_samples.py), never kept here.
"""

import argparse
import json
import math
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

# The longest (s) an oboe note may be held: its samples are cut off while still sounding (the straight
# ones after 8-10 s, the vibrato ones after 6-7 s), so a longer note breathes and is played again.
OBOE_SECONDS = {"oboe": 7.0, "oboe-vib": 5.0, "oboe-model": 15.0, "oboe-model-straight": 15.0}
# The tone the user chose for the muffled pieces: C3 of the fourth round (the
# references' average spectrum against the plain upright's (B2), smoothed: a
# warmer middle, falling from 1.2 kHz), then D2 of the fifth ("bớt chói": 1-4 dB
# less from 630 Hz up), then H3 of the eighth, for a phone's speaker: 4-5 dB
# less at 125-250 Hz, no warm 300-400 Hz bump, 1.2-2.5 kHz back by 4-7 dB
# (Hz, dB; render_samples.py's eq). EQ_C3 and EQ_D2 are the earlier ones.
EQ_C3 = [
    (62, 0), (79, 0), (99, 0), (125, -2.4), (157, -2.3), (198, -1.9), (250, -1.3),
    (315, 3.1), (397, 4.6), (500, 0.2), (630, -3.3), (794, -1), (1000, 1.2), (1260, -3.9),
    (1587, -10.9), (2000, -16.3), (2520, -20.7), (3175, -23.8), (4000, -24), (5040, -24),
]
EQ_D2 = [
    (62, 0), (79, 0), (99, 0), (125, -2.4), (157, -2.3), (198, -1.9), (250, -1.3),
    (315, 3.1), (397, 4.6), (500, 0.2), (630, -4.3), (794, -3), (1000, -1.8), (1260, -7.9),
    (1587, -14.9), (2000, -20.3), (2520, -24.7), (3175, -27.8), (4000, -28), (5040, -28),
]
EQ_DEM_DIU = [
    (62, 0), (79, 0), (99, 0), (125, -5), (157, -5), (198, -4.5), (250, -4),
    (315, -1.5), (397, 0), (500, 0), (630, -4.3), (794, -3), (1000, -1.8), (1260, -4),
    (1587, -9), (2000, -13), (2520, -19), (3175, -25), (4000, -28), (5040, -28),
]
# A keyboard's piano: warmer under 400 Hz, darker from 1.2 kHz (Hz, dB).
EQ_KEYS = [(80, 2), (150, 3), (250, 2.5), (400, 1), (700, 0), (1200, -2), (2000, -6), (3000, -10), (5000, -14),
           (8000, -18)]
# Instrument: (library, SFZ file, tone for render_samples.py).
INSTRUMENTS = {
    # VCSL's Yamaha upright: the user's choice for gentle piano, dark and clean.
    "upright": ("vcsl", "Chordophones/Zithers/Upright Piano, Yamaha.sfz", dict(TONES["yamaha"])),
    # the same, as the felt-hammered pianos sound: its highs rolled off
    "felt": ("vcsl", "Chordophones/Zithers/Upright Piano, Yamaha.sfz", TONES["yamaha"] | {"lowpass": 1100}),
    # the Steinway B, its highs open (fetch_samples.py hushes its hiss)
    "grand": ("vcsl", "Chordophones/Zithers/Grand Piano, Steinway B.sfz", dict(TONES["grand"])),
    # VCSL's Kawai grand, warmer than the Steinway
    "kawai": ("vcsl", "Chordophones/Zithers/Grand Piano, Kawai.sfz", {"release_db": -60}),
    # jRhodes3d, a 1977 Rhodes Mark I by Jeff Learman (free to use in music; its samples, CC BY-NC 4.0 to pass
    # on, are fetched, never kept here): its chorus baked into its stereo samples, a little more added; its
    # highs eased from 4 kHz, mellow
    "rhodes": ("jrhodes", "jRhodes3d-st.sfz", dict(TONES["ep"]) | {"lowpass": 4000, "lowpass_order": 2}),
    # the Salamander Grand Piano (a Yamaha C5 grand, by Alexander Holm, CC-BY 3.0): sixteen strengths a
    # key, clean; its release noises and pedal left out
    "salamander": ("salamander", "Salamander Grand Piano V3.sfz", {"release_db": -60, "pedal_noise": False}),
    "cellos": ("vsco", "CelloEnsSusVib-Quiet.sfz", dict(TONES["cellos"])),
    "violas": ("vsco", "ViolaEnsSusVib-Quiet.sfz", dict(TONES["violas"])),
    # the same, darker, for one thin line behind a bare tune: their soft samples hiss (alone in the quiet
    # moments of a piece, 35-42 dB under its music; low-passed at 2 kHz, 48-49)
    "violas-dark": ("vsco", "ViolaEnsSusVib-Quiet.sfz", TONES["violas"] | {"lowpass": 2000, "lowpass_order": 4}),
    # the cellos singing a tune alone: their soft samples' hiss shows there (38-39 dB under the music in its
    # quiet moments), so their highs go from 3 kHz
    "cellos-dark": ("vsco", "CelloEnsSusVib-Quiet.sfz", TONES["cellos"] | {"lowpass": 3000, "lowpass_order": 4}),
    # the violas drawn in at a sentence's end, each note easing in (80 ms), their own colour kept: darkened at
    # 2 kHz with a 0.3 s swell, to LAION CLAP they were "piano with a synth pad" (85-95 %); as recorded (their
    # usual tone), "a piano and viola duet" first, the hiss still 56 dB under the music in its quiet moments
    "violas-end": ("vsco", "ViolaEnsSusVib-Quiet.sfz", TONES["violas"] | {"attack": 0.08}),
    # the cellos plucked (pizzicato), two takes a note in turn
    "cellos-pizz": ("vsco", "CelloEnsPizz.sfz", TONES["cellos"] | {"lowpass": 4000, "lowpass_order": 2}),
    "basses": ("vsco", "ContrabassSusVB-Quiet.sfz", dict(TONES["basses"])),
    "violin": ("vsco", "SViolinVib-Quiet.sfz", dict(TONES["violins"]) | {"width": 0.5}),
    # VSCO's oboe, held straight (no vibrato) or with it, for a soft line behind the piano: darkened as the
    # C5 piano is, a little more (EQ_C3 at 0.75; as recorded, over the C5 piano it added 16-17 dB at
    # 1.2-5 kHz, the brightest thing in the mix, now 9 and 3), its hiss hushed, each note swelling in
    # (0.15 s), narrow
    "oboe": ("vsco", "OboeSusNV.sfz", {"attack": 0.15, "highpass": 120, "eq": [list(p) for p in EQ_C3],
                                       "eq_amount": 0.75, "width": 0.5, "dehiss": True}),
    "oboe-vib": ("vsco", "OboeSusVib.sfz", {"attack": 0.15, "highpass": 120, "eq": [list(p) for p in EQ_C3],
                                            "eq_amount": 0.75, "width": 0.5, "dehiss": True}),
    # the modelled oboe (dark/oboe_model.py, built with the pieces): no recording, every note made from the
    # oboe's measured sound, held as long as a piece asks (15 s); with a player's vibrato, or straight
    "oboe-model": ("model", "oboe-model.sfz", {"attack": 0.15, "highpass": 120, "eq": [list(p) for p in EQ_C3],
                                               "eq_amount": 0.75, "width": 0.5}),
    "oboe-model-straight": ("model", "oboe-model-straight.sfz", {"attack": 0.15, "highpass": 120,
                                                                 "eq": [list(p) for p in EQ_C3], "eq_amount": 0.75,
                                                                 "width": 0.5}),
    "drone": ("local", "drone.sfz", {"highpass": 30}),
    # the modelled pianos (dark/piano_model.py, built with the pieces): no
    # recording, every note made from its strings; fitted to the Yamaha
    # upright as the user chose it (H3), dreamier, and closer
    "model": ("model", "felt-model.sfz", {}),
    "model-dream": ("model", "felt-dream.sfz", {}),
    "model-close": ("model", "felt-close.sfz", {}),
    "model-grand": ("model", "felt-grand.sfz", {}),
    "model-clear": ("model", "felt-clear.sfz", {}),
    "model-bloom": ("model", "felt-bloom.sfz", {}),
    "model-wood": ("model", "felt-wood.sfz", {}),
    "model-glass": ("model", "felt-glass.sfz", {}),
}
# Named styles: a piece's "style" fills in every setting it does not give itself.
STYLES = {
    # "Đêm dịu" as the user first chose it: C3 of the fourth round, as D2 of the
    # fifth ("D2 ổn"): slow (70-84 bpm), a light left hand (a bass held under
    # two tones rocking in eighths, let go after a beat, the pedal taken every
    # two beats, softer than the tune), the tune struck softly (38-60, never
    # above 64: the Yamaha upright's softest samples), a softer strike (25 ms)
    # and the references' tone a little darker; the bass above E2. Then clear
    # on a phone's speaker, as H3 of the eighth ("H3 nghe rõ nhất"): its tone,
    # the piano narrower (0.7), less hall (0.65), -14 LUFS. The pieces heard
    # this way keep it (dem-diu-h3).
    "dem-diu-h3": {"piano": "upright", "bass_low": 40, "texture": "flow", "hold": 1.0, "pedal_beats": 2, "lh_soft": 6,
                   "melody_velocity": [38, 60], "velocity_cap": 64,
                   "room": {"rt60": 2.8, "wet": 0.65}, "piano_reverb": 0.35, "loudness": -14,
                   "piano_tone": {"attack": 0.025, "eq": [list(p) for p in EQ_DEM_DIU], "width": 0.7}},
    # "Đêm dịu" now: played as a person plays (I3, "giống người") on the
    # modelled piano the user chose, M2 of the tenth round ("hãy làm theo
    # M2"): dark/piano_model.py's felt-dream, a softer onset (45 ms), wider
    # (0.85), a longer hall (3.6 s, 0.85); the left hand and touch as before.
    # The app plays it the same way (bokin_music/dark on the app's branch).
    # "Mờ ảo" as first heard (round 15, Mờ ảo v2), after the user's new reference ("tôi muốn phối nhạc
    # kiểu như này, màu sắc nhạc cụ kiểu như này"): glassy soft keys (felt-glass: a felt piano with an electric piano's tine), notes dying sooner,
    # less bass, a much wider image, a shorter, drier hall; a soft left hand; the
    # tune low, around the middle of the keyboard (G3-E5: the reference's sound sits an octave lower than
    # dem-diu's), a shimmer trembling just above it (layer tremolo) where the piece swells.
    "mo-ao-glass": {"piano": "model-glass", "bass_low": 40, "texture": "open", "hold": 0.75, "pedal_beats": 2,
                    "lh_soft": 8, "melody_velocity": [40, 62], "velocity_cap": 64,
                    "room": {"rt60": 2.2, "wet": 0.5}, "piano_reverb": 0.35, "loudness": -14,
                    "piano_tone": {"attack": 0.04, "width": 1.4,
                                   "eq": [[100, 0], [127, -3], [160, -5], [250, -5], [320, 0], [1250, 2], [1600, 5],
                                          [2000, 2], [2500, 0]]},
                    "human": {"amount": 1.0, "vary": True}},
    # "Mờ ảo" of round 16, as the user chose it ("tôi thích bản c5 hơn, và dùng thêm nhạc cụ oboe làm
    # nền"): the sound of C5 (VCSL's Kawai grand, the references' tone at half strength, a 2.8 s hall, the
    # light flowing left hand, played evenly) with VSCO's oboe softly behind it (layer oboe, 3 dB under a pad).
    "mo-ao-c5": {"piano": "kawai", "bass_low": 40, "texture": "flow", "hold": 1.0, "pedal_beats": 2, "lh_soft": 6,
                 "room": {"rt60": 2.8, "wet": 0.8}, "piano_reverb": 0.35, "loudness": -14,
                 "piano_tone": {"attack": 0.025, "eq": [list(p) for p in EQ_C3], "eq_amount": 0.5, "release_db": -60},
                 "gains": {"oboe": -3.0}},
    # "Mờ ảo" now ("tôi muốn không có tiếng piano đệm đều phía dưới, tiếng oboe dùng loại mô phỏng"): the C5
    # piano plays the tune alone, no left hand under it (the pedal still holds each chord), and two modelled
    # oboes behind it (dark/oboe_model.py) hold the harmony, the second on the chords' roots: 7 and 9 dB
    # under the piano (with no left hand, 15 and 17 left them adding 1 dB to the mix, barely heard).
    "mo-ao": {"piano": "kawai", "bass_low": 40, "texture": "none", "pedal_beats": 2,
              "room": {"rt60": 2.8, "wet": 0.8}, "piano_reverb": 0.35, "loudness": -14,
              "piano_tone": {"attack": 0.025, "eq": [list(p) for p in EQ_C3], "eq_amount": 0.5, "release_db": -60},
              "oboe": "oboe-model", "oboe_voices": 2, "gains": {"oboe": 5.0, "oboe2": 3.0}},
    # "Mờ ảo" with strings ("hãy thử piano + cello + viola: piano chơi chính, cello đáp câu, viola chỉ giữ
    # nền mỏng"): the C5 piano on the tune alone, the cellos answering it (layer cello-answer), the violas
    # holding one thin line under it (layer viola-pad, 10 dB under the piano).
    "mo-ao-day": {"piano": "kawai", "bass_low": 40, "texture": "none", "pedal_beats": 2,
                  "room": {"rt60": 2.8, "wet": 0.8}, "piano_reverb": 0.35, "loudness": -14,
                  "piano_tone": {"attack": 0.025, "eq": [list(p) for p in EQ_C3], "eq_amount": 0.5,
                                 "release_db": -60},
                  "gains": {"viola": 2.0}},
    # "Tam tấu" (a trio): piano, cellos, violas, as the user asked ("tiếng piano chưa phù hợp, hãy chọn tiếng
    # piano phù hợp hơn và sáng tác 1 bài mới phù hợp kiểu phối"): mo-ao-day's cellos answering the tune and
    # thin viola line, on the Salamander grand (to LAION CLAP, of the Salamander, the Steinway B, the Kawai
    # as recorded and the Kawai through C5's tone, the least "dull, muffled" and "synth pad", the most "a
    # high quality classical recording"; the Kawai through C5's tone the most muffled), played as a person
    # plays; the pieces written for it hold a note at the end of each sentence for the cellos to answer.
    "tam-tau": {"piano": "salamander", "bass_low": 40, "texture": "none", "pedal_beats": 2,
                "room": {"rt60": 2.8, "wet": 0.8}, "piano_reverb": 0.35, "loudness": -14,
                "human": {"amount": 0.8, "vary": True}, "gains": {"viola": 2.0}},
    # "Tam tấu" on keys ("tôi muốn tiếng piano trầm hơn nghe giống keyboard hơn"): the Salamander warmer and
    # darker (EQ_KEYS), narrower, a light chorus, struck within a narrower range, as a stage keyboard's
    # piano, with the Rhodes doubling it 4 dB under, as a keyboard's layered piano. To LAION CLAP the
    # warmest of four ("a warm, deep, dark piano" 0.637; the Salamander as recorded 0.578, darkened alone
    # 0.610, the Rhodes alone 0.593), and the nearest to the user's keyboard-like reference (0.815;
    # 0.746, 0.769, 0.732).
    "tam-tau-phim": {"piano": "salamander", "bass_low": 40, "texture": "none", "pedal_beats": 2,
                     "room": {"rt60": 2.8, "wet": 0.8}, "piano_reverb": 0.35, "loudness": -14,
                     "piano_tone": {"eq": [list(p) for p in EQ_KEYS], "width": 0.6, "chorus": 0.25},
                     "melody_velocity": [46, 70], "piano_layer": "rhodes",
                     "human": {"amount": 0.8, "vary": True}, "gains": {"viola": 2.0, "piano-layer": 2.0}},
    # "Song tấu" (a duo), the user's new arrangement ("1. Piano + viola: Piano chơi giai điệu thưa; viola kéo
    # những nốt trung trầm, chỉ xuất hiện cuối câu"): tam-tau-phim's keyboard piano on a sparse tune, one soft
    # deep note a chord under it (texture deep), the violas only at each sentence's end (layer viola-end,
    # 8 dB under the piano).
    "song-tau": {"piano": "salamander", "bass_low": 40, "texture": "deep", "pedal_beats": 2,
                 "room": {"rt60": 2.8, "wet": 0.8}, "piano_reverb": 0.35, "loudness": -14,
                 "piano_tone": {"eq": [list(p) for p in EQ_KEYS], "width": 0.6, "chorus": 0.25},
                 "melody_velocity": [46, 70], "piano_layer": "rhodes",
                 "human": {"amount": 0.8, "vary": True}, "gains": {"viola-end": -2.0, "piano-layer": 2.0}},
    # "Kể chuyện" (a story), the arrangement proposed when the user asked for better pieces in a style of
    # Claude's own ("bạn hãy tự sáng tác những bản khác hay hơn, phối theo kiểu bạn đề xuất"): the keyboard
    # piano tells the tune alone first, a soft deep note a chord under it; then the cellos join (a slow second
    # line, or answers from afar); at the climax the strings hold the chords and the piano rolls them; then it
    # thins to the piano again, the violas only at the sentences' ends. Each piece sets its own arc in its
    # sections' layers and textures. The last chord is struck softly (38, not 52): struck at 52 it was 5 dB
    # louder than the quiet return before it.
    "ke-chuyen": {"piano": "salamander", "bass_low": 40, "texture": "deep", "pedal_beats": 2,
                  "room": {"rt60": 2.8, "wet": 0.8}, "piano_reverb": 0.35, "loudness": -14,
                  "piano_tone": {"eq": [list(p) for p in EQ_KEYS], "width": 0.6, "chorus": 0.25},
                  "melody_velocity": [46, 72], "piano_layer": "rhodes", "ending_velocity": 38,
                  "human": {"amount": 0.8, "vary": True},
                  "gains": {"piano-layer": 2.0, "viola-end": -2.0, "cello-counter": -4.0, "violas": 2.0,
                            "cellos-pad": 2.0}},
    # "Kể chuyện" asleep ("tôi muốn các bài sẽ có không gian giống ambient hơn, tiếng piano mờ ảo hơn, nhạc
    # dễ ngủ hơn"): the same keyboard piano and strings in a hall nearly twice as long (4.8 s, everything sent
    # into it more), the piano struck softer (36-58) and wider, its hammer softened (30 ms) and its top
    # rounded off (3.2 kHz), the Rhodes under it darker; the strings swelling in slowly (0.5-0.9 s) and
    # darker; -16 LUFS. The pieces played this way are 12 % slower and softer, their climaxes low (dyn 0.5 at
    # most, sparse chords for rolled ones), with no plucks or octaves. Of Xuân muộn's trials, to LAION CLAP:
    # "ambient, dreamy piano music for sleep" 90 % (as ke-chuyen, 85 %), "a piano far away in a big, echoing
    # space" 87 % (51 %), "a gentle lullaby" 80 % (2 %; "a nostalgic, wistful melody" 97 %). The strings
    # held softly under every section, as an ambient bed, made it "a spooky, unsettling soundtrack" (50-89 %),
    # so they stay only where a piece's arc has them; the hall at 6 s, more so (96 %).
    "ke-chuyen-mo": {"piano": "salamander", "bass_low": 40, "texture": "deep", "pedal_beats": 2,
                     "room": {"rt60": 4.8, "wet": 1.0}, "piano_reverb": 0.55, "loudness": -16,
                     "piano_tone": {"eq": [list(p) for p in EQ_KEYS], "width": 0.9, "chorus": 0.4, "attack": 0.03,
                                    "lowpass": 3200},
                     "melody_velocity": [36, 58], "piano_layer": "rhodes", "piano_layer_tone": {"lowpass": 3000},
                     "ending_velocity": 30, "human": {"amount": 0.8, "vary": True},
                     "gains": {"piano-layer": 2.0, "viola-end": -2.0, "cello-counter": -4.0},
                     "tones": {"violas": {"attack": 0.9, "lowpass": 2500}, "cellos-pad": {"attack": 0.9, "lowpass": 2200},
                               "basses": {"attack": 0.9}, "viola": {"attack": 0.9},
                               "cello-counter": {"attack": 0.5, "lowpass": 2500},
                               "cello-answer": {"attack": 0.4, "lowpass": 2500},
                               "viola-end": {"attack": 0.6, "lowpass": 3000},
                               "viola-tune": {"attack": 0.3}, "cello-tune": {"attack": 0.3}}},
    "dem-diu": {"piano": "model-dream", "bass_low": 40, "texture": "flow", "hold": 1.0, "pedal_beats": 2, "lh_soft": 6,
                "melody_velocity": [38, 60], "velocity_cap": 64,
                "room": {"rt60": 3.6, "wet": 0.85}, "piano_reverb": 0.35, "loudness": -14,
                "piano_tone": {"attack": 0.045, "width": 0.85}, "human": {"amount": 1.0, "vary": True}},
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
        self.cap = 127  # the hardest a key is struck

    def add(self, tick: float, note: int, velocity: float, length: float) -> None:
        self.notes.append((max(0, int(tick)), int(note), max(1, min(self.cap, int(velocity))), max(30, int(length))))


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
        human = score.get("human") or {}
        self.human, self.vary = float(human.get("amount", 0)), bool(human.get("vary"))
        self.hrng = random.Random(seed * 7919 + 1)  # a person's liberties, apart from the machine's jitter
        self.tempos = self.human_tempo_map() if self.human else self.tempo_map()

    def ms(self, value: float) -> float:
        """Milliseconds as ticks, at the piece's own tempo."""
        return value * self.bpm * TICKS / 60000

    def phrase_at(self, tick: int) -> tuple:
        """Where a tick falls in its section's four-bar phrases: (the phrase's
        first tick, its length in bars, the bar within it, 0-1 through it)."""
        start, end, section = next(x for x in self.sections if x[0] <= tick < x[1])
        bar = (tick - start) // self.bar
        first = bar - bar % 4
        bars = min(4, section["bars"] - first)
        begin = start + first * self.bar
        return begin, bars, bar % 4, (tick - begin) / (bars * self.bar)

    def human_tempo_map(self) -> list:
        """(tick, bpm) an eighth at a time, as a person plays (human amount a):
        each phrase leans a little forward to its middle (up to 6 % times a)
        and broadens into its last two beats (8 and 22 %, each phrase by its
        own 60-120 % of that, as a player never breathes twice alike),
        hesitates as it begins (5 %); the pulse drifts from bar to bar (2.5 %,
        a random walk); the eighth before a section's highest note takes a
        breath (25 %); a section marked rit, and the piece's end, slow as
        before. Before the last two bars it never drops under 62 %."""
        a, drift, changes, breath, phrase = self.human, 0.0, [], 1.0, None
        peaks = set()
        for start, end, section in self.sections:
            tops = [(t, max(n)) for t, n, _ in self.tune if start <= t < end]
            if tops:
                high = max(n for _, n in tops)
                peaks.add(min(t for t, n in tops if n == high) - EIGHTH)
        for start, end, section in self.sections:
            for bar in range(section["bars"]):
                drift = 0.7 * drift + 0.3 * self.hrng.gauss(0, 1)
                for e in range(self.bar // EIGHTH):
                    tick = start + bar * self.bar + e * EIGHTH
                    begin, bars, in_phrase, position = self.phrase_at(tick)
                    if begin != phrase:
                        phrase, breath = begin, 0.6 + 0.6 * self.hrng.random()
                    k = (1 + a * 0.06 * math.sin(math.pi * position) - a * 0.01) * (1 + a * 0.025 * max(-2, min(2, drift)))
                    left = (begin + bars * self.bar - tick) / TICKS  # beats to the phrase's end
                    k *= (1 - a * 0.22 * breath) if left <= 1 else (1 - a * 0.08 * breath) if left <= 2 else 1
                    if in_phrase == 0 and e < 2:
                        k *= 1 - a * 0.05
                    if tick in peaks:
                        k *= 1 - a * 0.25
                    to_end = (end - tick) / TICKS
                    if (section.get("rit") or end == self.end) and to_end <= 2 * self.beats:
                        deepest = 0.6 if end == self.end else 0.8
                        k *= 1 - (1 - deepest) * (1 - (to_end - 0.5) / (2 * self.beats))
                    if self.end - tick > 2 * self.bar:
                        k = max(k, 0.62)
                    changes.append((tick, round(self.bpm * k, 3)))
        changes.append((self.end, self.bpm * 0.5))  # the held last chord
        return changes

    def read_melody(self, text: str, start: int, bars: int, number: int) -> None:
        tick = start
        for index, bar in enumerate(text.split("|") if text.strip() else []):
            bar_start = tick
            for token in bar.split():
                pitches, _, beats = token.partition(":")
                length = round(float(beats or 1) * TICKS)
                if pitches != "r":
                    shift = self.score.get("melody_shift", 0)  # the whole tune moved, in semitones
                    self.tune.append((tick, [note_number(p) + shift for p in pitches.split("+")], length))
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

    def held(self, part: Part, tick: int, note: int, velocity: float, length: int,
             most: float = HOLD_SECONDS) -> None:
        """A sustained note, struck again on a beat when longer than its
        sample (most: the longest it sounds, s)."""
        end = tick + length
        while tick < end:
            piece = end - tick
            while piece > TICKS and self.seconds(tick, tick + piece) > most:
                piece -= TICKS
            part.add(tick, note, velocity, piece + (40 if tick + piece < end else 0))
            tick += piece
            velocity *= 0.92


def phrase_shape(position: float) -> float:
    """-1 to 1 over a four-bar phrase: rising to its middle, falling after."""
    return 1 - abs(2 * position - 1) * 2


def play_melody(piece: Piece, piano: Part) -> None:
    if piece.human:
        return play_melody_human(piece, piano)
    for tick, notes, length in piece.tune:
        section = piece.section_at(tick)
        if section.get("melody_on", "piano") != "piano":
            continue
        position = (tick % (4 * piece.bar)) / (4 * piece.bar)
        soft, loud = piece.score.get("melody_velocity", (40, 82))  # at dyn 0 and 1
        velocity = soft + (loud - soft) * section.get("dyn", 0.4) + 6 * phrase_shape(position) + piece.jitter(3)
        late = 10 + piece.jitter(6)  # a little behind the beat, as a player lingers
        for k, note in enumerate(sorted(notes, reverse=True)):
            piano.add(tick + late + 12 * k, note, velocity - 6 * k, length)
        if "octave" in section.get("layers", []):
            piano.add(tick + late + 6, max(notes) - 12, velocity - 12, length)


def play_melody_human(piece: Piece, piano: Part) -> None:
    """The tune as a person plays it (human amount a): a higher note a little
    louder (0.7 a velocity a semitone over the tune's middle), each phrase
    swelling to its middle, no two notes struck quite alike (3 a); a little
    ahead of the left hand (12 a ms), as a pianist's melody leads, but the
    phrase's first note a touch late (20 a ms), the player hesitating; the
    onsets loose by 7 a ms."""
    a = piece.human
    soft, loud = piece.score.get("melody_velocity", (40, 82))
    on_piano = [(t, notes, l) for t, notes, l in piece.tune if piece.section_at(t).get("melody_on", "piano") == "piano"]
    pitches = sorted(n for _, notes, _ in on_piano for n in notes) or [72]
    middle = pitches[len(pitches) // 2]
    firsts, seen = set(), set()
    for tick, _, _ in piece.tune:
        begin = piece.phrase_at(tick)[0]
        if begin not in seen:
            seen.add(begin)
            firsts.add(tick)
    for tick, notes, length in on_piano:
        section = piece.section_at(tick)
        position = piece.phrase_at(tick)[3]
        velocity = max(30, soft + (loud - soft) * section.get("dyn", 0.4) + 6 * phrase_shape(position)
                       + a * 0.7 * (max(notes) - middle) + piece.hrng.gauss(0, 3 * a))
        late = piece.ms(20 * a if tick in firsts else -12 * a) + piece.ms(piece.hrng.gauss(0, 7 * a))
        for k, note in enumerate(sorted(notes, reverse=True)):
            piano.add(tick + late + 12 * k, note, velocity - 6 * k, length)
        if "octave" in section.get("layers", []):
            piano.add(tick + late + 6, max(notes) - 12, velocity - 12, length)


def flow_human(piece: Piece, piano: Part, tick: int, length: int, low: int, tones: list, ceiling: int,
               velocity: float, hold: int) -> None:
    """The flow (a deep bass held under tones of the chord rocking in
    eighths) as a person plays it. Its onsets loose (14 a ms), the off-beats
    a touch late (6 a ms), each note its own strength (3 a), the bass of the
    bar leaning, the hand swelling with the phrase. With vary, it follows the
    tune: under a busy tune it plays quarters, under a long note or a rest it
    fills, up and down four tones; it rocks one way, then the other; at a
    phrase's end over a held note it rolls the chord and lets it ring."""
    a = piece.human
    begin, bars, in_phrase, _ = piece.phrase_at(tick)
    bar_number = (tick - begin) // piece.bar + (begin - next(x[0] for x in piece.sections if x[0] <= tick < x[1])) // piece.bar
    tune = [(t, n, l) for t, n, l in piece.tune if tick <= t < tick + length]
    busy = len(tune) >= (4 if piece.beats % 2 == 0 else 3)
    still = all(l >= 2 * TICKS for _, _, l in tune)
    ending = in_phrase == bars - 1 and tick + length >= begin + bars * piece.bar
    tones_up = [n for n in range(low + 5, low + 22) if n % 12 in tones and n < ceiling]
    ladder = [low] + [n for k, n in enumerate(tones_up) if k == 0 or n - tones_up[k - 1] >= 3][:3]
    if piece.vary and ending and still and len(ladder) >= 3:
        for k, n in enumerate(ladder):
            piano.add(tick + piece.ms(75 * k + piece.hrng.gauss(0, 10 * a)), n,
                      max(22, velocity + 4 - 3 * k + piece.hrng.gauss(0, 3 * a)), length)
        return
    if piece.vary and still and not busy and len(ladder) == 4:
        order = [0, 1, 2, 3, 2, 1, 2, 1] if piece.beats % 2 == 0 else [0, 1, 2, 3, 2, 1]
    else:
        ladder = ladder[:3]
        if piece.vary and bar_number % 2:
            order = [0, 2, 1, 2] if piece.beats % 2 == 0 else [0, 2, 1]
        else:
            order = [0, 1, 2, 1] if piece.beats % 2 == 0 else [0, 1, 2]
    slots = range(0, length // EIGHTH, 2 if piece.vary and busy else 1)
    shape = phrase_shape(piece.phrase_at(tick)[3])
    for k in slots:
        step = order[k % len(order)] % len(ladder)
        at = tick + k * EIGHTH + piece.ms(piece.hrng.gauss(0, 14 * a) + (6 * a if k % 2 else 0))
        strength = max(22, velocity + (6 if k == 0 else 0) - 3 * step + 4 * a * shape + piece.hrng.gauss(0, 3 * a)
                       - (2 if piece.vary and busy else 0))  # never so soft a note is lost
        piano.add(max(tick - piece.ms(30), at), ladder[step], strength, length if k == 0 else min(hold, length - k * EIGHTH))


def pedal_human(piece: Piece, piano: Part) -> None:
    """The pedal as a person takes it: lifted just before each chord, pressed
    again a moment after (15-35 ms, 60-110 ms), held through a chord unless
    the tune passes outside it in the bar's second half, where it is taken
    again halfway, so the passing notes do not blur."""
    for tick, length, name in piece.spans:
        piano.pedal += [(tick - round(piece.ms(piece.hrng.uniform(15, 35))), 0),
                        (tick + round(piece.ms(piece.hrng.uniform(60, 110))), 100)]
        if length >= 4 * TICKS:
            middle = tick + length // 2
            _, tones, _ = chord(name)
            if any(n % 12 not in tones for t, notes, l in piece.tune if middle <= t < tick + length for n in notes):
                piano.pedal += [(middle - round(piece.ms(20)), 0), (middle + round(piece.ms(80)), 100)]
    if piece.score.get("pedal_steps"):
        pedal_steps(piece, piano)
    piano.pedal.append((piece.end + piece.bar, 0))


def pedal_steps(piece: Piece, piano: Part) -> None:
    """The pedal taken again as the tune steps (a semitone or a tone) onto
    a note next to one still held by the pedal: lifted just after the new
    note sounds (30-45 ms), pressed again 95-130 ms after it, the new note
    and the bass held by the fingers through it. Under the pedal the old
    note kept ringing beside the new, the two nearly pure tones beating
    35-125 times a second, heard as a buzz ("rè") on the tune's high notes;
    a pianist clears it so, the bass and the hall's wash kept."""
    rng = random.Random(len(piece.tune) * 7919 + 2)  # its own, so the rest of the piece is played as before
    lifts = sorted(t for t, v in piano.pedal if v == 0)
    held, k = set(), 0
    for tick, notes, _ in sorted(piece.tune):
        while k < len(lifts) and lifts[k] <= tick:
            held, k = set(), k + 1
        section = piece.section_at(tick)
        sounding = set(notes) | ({max(notes) - 12} if "octave" in section.get("layers", []) else set())
        if any(0 < abs(n - h) <= 2 for n in sounding for h in held):
            piano.pedal += [(tick + round(piece.ms(rng.uniform(30, 45))), 0),
                            (tick + round(piece.ms(rng.uniform(95, 130))), 100)]
            held = set()
        held |= sounding


def bass_note(name: str, low: int = 31) -> int:
    return above(chord(name)[0], low)


def left_hand(piece: Piece, piano: Part) -> None:
    previous = [57, 60, 64]
    for tick, length, name in piece.spans:
        section = piece.section_at(tick)
        texture, dyn = section.get("texture", piece.score.get("texture", "arp")), section.get("dyn", 0.4)
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
        elif texture == "flow" and (piece.human or piece.vary):
            flow_human(piece, piano, tick, length, low, tones, ceiling, velocity, hold)
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
        elif texture == "open":  # a deep bass held, then the chord broken in eighths an octave and more above
            # it, nothing between: the low-mids left clear (the user's reference's left hand)
            top = min(ceiling, low + 31)
            ladder = [n for n in range(max(low + 12, 52), top) if n % 12 in tones]
            ladder = [n for k, n in enumerate(ladder) if k == 0 or n - ladder[k - 1] >= 3][:3]
            piano.add(tick + piece.jitter(4), low, velocity + 6, length)
            order = [0, 1, 2, 1, 0, 1, 2, 1] if piece.beats % 2 == 0 else [0, 1, 2, 1, 2, 1]
            for k in range(1, length // EIGHTH) if ladder else []:
                step = order[k % len(order)] % len(ladder)
                piano.add(tick + k * EIGHTH + piece.jitter(5), ladder[step], velocity - 4 - 2 * step + (3 if k % 2 == 0 else 0),
                          min(hold, length - k * EIGHTH))
        elif texture == "deep":  # one soft deep note a chord, held while the chord stays: the sparsest left hand
            k = piece.spans.index((tick, length, name))
            if k and piece.spans[k - 1][2] == name and piece.spans[k - 1][0] + piece.spans[k - 1][1] == tick:
                continue
            hold = length
            for later, more, other in piece.spans[k + 1:]:
                if other != name or later != tick + hold:
                    break
                hold += more
            piano.add(tick + piece.jitter(4), low, velocity - 6, hold)
        elif texture == "pulse":
            for beat in range(0, length, TICKS * 2):
                for k, offset in enumerate((0, round(0.75 * TICKS))):
                    piano.add(tick + beat + offset + piece.jitter(4), low, velocity + 4 - 8 * k, TICKS)
                    piano.add(tick + beat + offset + piece.jitter(4), low + 12, velocity - 4 - 8 * k, TICKS)
            middle = voice(previous, tones, 50, min(67, ceiling))
            previous = middle
            for k, n in enumerate(middle):
                piano.add(tick + TICKS + 30 * k + piece.jitter(5), n, velocity - 12, length - TICKS)
    pedal_human(piece, piano) if piece.vary else pedal(piece, piano)


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
        if "tremolo" in wanted:  # the piano trembling between two tones of the chord just above the tune, in
            # sixteenths, softly, swelling through each chord: a glassy shimmer over it
            piano, rng = piece.parts["piano"], random.Random(start * 31 + 5)
            step = TICKS // 4
            for tick, length, name in spans:
                tune = piece.tune_between(tick, tick + length)
                floor = min(81, max(tune) + 3) if tune else 72
                pair = [n for n in range(floor, floor + 12) if n % 12 in chord(name)[1]][:2]
                count = length // step
                for k in range(count if len(pair) == 2 else 0):
                    swell = 0.5 - 0.5 * math.cos(2 * math.pi * (k + 0.5) / count)
                    piano.add(tick + k * step + rng.randint(-6, 6), pair[k % 2],
                              16 + 12 * dyn + 5 * swell + rng.uniform(-2, 2), 2 * step)  # each into the next
        for layer, instrument, shift, pan in (("violin", "violin", 0, 0.15), ("cello-melody", "cellos", -12, -0.2)):
            if layer in wanted:
                line = piece.part(layer, instrument, "melody2", pan, reverb=0.45)
                for tick, notes, length in piece.tune:
                    if start <= tick < end:
                        piece.held(line, tick + 15, max(notes) + shift, velocity + 4, length)
    oboe_line(piece)
    cello_tune(piece)
    cello_pizz(piece)
    viola_ends(piece)
    answered = cello_answers(piece)
    spans = [(t, l, n, piece.section_at(t)) for t, l, n in piece.spans]
    spans = [s for s in spans if "viola-pad" in s[3].get("layers", [])]
    counter = [(t, l, n, piece.section_at(t)) for t, l, n in piece.spans]
    counter = [s for s in counter if "cello-counter" in s[3].get("layers", [])]
    if counter:  # layer cello-counter: the cellos singing a slow second line under the tune
        line, _ = held_voice(piece, counter, 6.5, low=45, high=60, soft=36)
        play_held(piece, piece.part("cello-counter", "cellos", "melody2", -0.25, reverb=0.5), line, 6.5)
    if spans:  # layer viola-pad: the violas holding one soft, thin line of the chords' colour tones
        clear = lambda tick, length: [n for a, b, n in answered if a < tick + length and b > tick]
        line, _ = held_voice(piece, spans, 6.5, low=58, high=72, avoid=clear, soft=30)
        play_held(piece, piece.part("viola", "violas-dark", "pad", 0.3, reverb=0.55), line, 6.5)


def oboe_line(piece: Piece) -> None:
    """Layer oboe: an oboe softly behind the piano, one long note a chord, a
    slow line of the chords' colour tones (their thirds, sixths, sevenths:
    not the root or fifth, where it can), each the nearest to the one before;
    a note the next chord also holds is tied on (up to OBOE_SECONDS, and for
    two bars at most before the line moves on), never a step or a half step
    from the tune nor on its very note; under the tune where there is room
    (C4 up), else over it, within C4-A5, its sweetest notes. It comes in an
    eighth after the piano's chord, as an answer, and swells with the
    section's dyn; on the last chord it holds as the piano does. With
    oboe_voices 2, a second oboe under the first, a third to a sixth below it
    (G3 up), on the chord's root or bass where it can (with no piano under
    them, it carries the harmony's foot), a line as smooth, a little softer."""
    instrument = piece.score.get("oboe", "oboe")
    spans = [(t, l, n, piece.section_at(t)) for t, l, n in piece.spans]
    spans = [s for s in spans if "oboe" in s[3].get("layers", [])]
    if not spans:
        return
    limit = OBOE_SECONDS[instrument]
    line, notes = held_voice(piece, spans, limit)
    play_held(piece, piece.part("oboe", instrument, "pad", 0.25, reverb=0.55), line, limit)
    if piece.score.get("oboe_voices", 1) > 1:
        line, _ = held_voice(piece, spans, limit, above=notes)
        play_held(piece, piece.part("oboe2", instrument, "pad", -0.25, reverb=0.55), line, limit)


def held_voice(piece: Piece, spans: list, limit: float, above: list = None, low: int = 60, high: int = 81,
               avoid=None, soft: float = 38) -> tuple:
    """One held line ([start, end, note, velocity]) and its note at each
    span (None where it rests), between low and high (under the tune where
    there is room), its velocity soft + 26 x dyn; given the first oboe's
    notes (above), the second oboe's. avoid(tick, length): other notes it
    keeps as clear of as of the tune."""
    line, previous, picked = [], None, []
    floor, ceiling = low, high
    for i, (tick, length, name, section) in enumerate(spans):
        tune = piece.tune_between(tick, tick + length)
        others = tune + (avoid(tick, length) if avoid else [])
        bass, tones, root = chord(name)
        if above is None:
            prefer = [pc for pc in tones if (pc - root) % 12 not in (0, 7)]
            low, high = floor, ceiling
            if tune and min(tune) - 3 >= low + 4:
                high = min(high, min(tune) - 3)
            elif tune:
                low = max(low, max(tune) + 3)
        elif above[i] is None:
            picked.append(None)
            previous = None
            continue
        else:
            prefer, low, high = [root, bass], max(55, above[i] - 9), above[i] - 3
        fits = [n for n in range(low, high + 1)
                if n % 12 in tones and (above is None or n % 12 != above[i] % 12)]
        clear = [n for n in fits if all(abs(n - t) > 2 and (n - t) % 12 not in (1, 11) for t in others)]
        choices = clear or [n for n in fits if n not in others]
        if not choices:
            picked.append(None)
            previous = None
            continue
        target = previous if previous is not None else (low + high) // 2
        kept = (tick - line[-1][0]) if line and line[-1][2] == previous and line[-1][1] == tick else 0
        note = min(choices, key=lambda n: (abs(n - target) + (0 if n % 12 in prefer else 2)
                                           + (4 if n == previous and kept >= 2 * piece.bar - EIGHTH else 0), -n))
        velocity = min(62, soft + 26 * section.get("dyn", 0.4)) - (0 if above is None else 4)
        if (line and note == line[-1][2] and line[-1][1] == tick
                and piece.seconds(line[-1][0], tick + length + EIGHTH + 30) <= limit):
            line[-1][1] = tick + length  # tied on
        else:
            line.append([tick + EIGHTH, tick + length, note, velocity])
        previous = note
        picked.append(note)
    if line and line[-1][1] == piece.end:
        line[-1][1] += piece.bar
    return line, picked


def play_held(piece: Piece, part: Part, line: list, limit: float) -> None:
    for k, (start, end, note, velocity) in enumerate(line):
        joined = k + 1 < len(line) and line[k + 1][0] - EIGHTH == end
        stop = end + (EIGHTH + 30 if joined else 0)  # into the next note, a breath's overlap
        piece.held(part, start, note, velocity, stop - start, most=limit)


# Who may sing a section's tune instead of the piano (melody_on): part, instrument, pan.
# The violas singing alone hiss more than the cellos (low-passed at 3 kHz, 41 dB under the music in its quiet
# moments, against 45-49 for the other pieces), so they sing on violas-dark (2 kHz: 47).
SINGERS = {"cello": ("cello-tune", "cellos-dark", -0.15), "viola": ("viola-tune", "violas-dark", 0.2)}


def cello_tune(piece: Piece) -> None:
    """A section marked melody_on cello (or viola): its tune sung by the
    cellos (written in their register, C2-A4; the violas', C3-E5), legato,
    each note into the next, swelling with the section's dyn, instead of the
    piano (which only plays that section's texture, if any)."""
    for singer, (name, instrument, pan) in SINGERS.items():
        notes = [(t, n, l) for t, n, l in piece.tune if piece.section_at(t).get("melody_on") == singer]
        if not notes:
            continue
        part = piece.part(name, instrument, "melody2", pan, reverb=0.45)
        for k, (tick, pitches, length) in enumerate(notes):
            dyn = piece.section_at(tick).get("dyn", 0.4)
            joined = k + 1 < len(notes) and notes[k + 1][0] == tick + length
            for note in pitches:
                piece.held(part, tick + 10, note, 50 + 26 * dyn, length + (40 if joined else 0), most=6.5)


def viola_ends(piece: Piece) -> None:
    """Layer viola-end: the violas only at the end of each sentence (the last
    bar of every four, and of a section): from that bar's second beat, one
    long note low in the middle (D3-E4), a tone of the chord, its root or
    third where it can, nearest the last they played but not the note they
    came in on last time, never a half step (or a minor ninth) from the
    tune; held into the next sentence's first
    beat, where it moves to the nearest tone of the new chord for two beats
    and stops (at the piece's end it holds into the last chord half a bar)."""
    if not any("viola-end" in s.get("layers", []) for _, _, s in piece.sections):
        return
    part = piece.part("viola-end", "violas-end", "melody2", 0.25, reverb=0.55)

    def chord_at(tick: int) -> str:
        return next(s[2] for s in piece.spans if s[0] <= tick < s[0] + s[1])

    def pick(name: str, near: int, start: int, stop: int, used: set = frozenset()) -> int:
        bass, tones, root = chord(name)
        tune = piece.tune_between(start, stop)
        prefer = {root, tones[1] if len(tones) > 1 else root}
        fits = [n for n in range(50, 65) if n % 12 in tones]
        clear = [n for n in fits if all((n - t) % 12 not in (1, 11) for t in tune)] or fits
        return min(clear, key=lambda n: (abs(n - near) + (0 if n % 12 in prefer else 1.5) + (6 if n in used else 0), n))

    previous, last_entry = 57, set()
    for start, end, section in piece.sections:
        if "viola-end" not in section.get("layers", []):
            continue
        dyn = section.get("dyn", 0.4)
        bars = section["bars"]
        for bar in [b for b in range(bars) if b % 4 == 3 or b == bars - 1]:
            begin = start + bar * piece.bar + TICKS
            turn = start + (bar + 1) * piece.bar
            first = pick(chord_at(begin), previous, begin, turn, last_entry)  # not as it came in last time
            velocity = 42 + 24 * dyn
            if turn >= piece.end:  # the last chord: held into it half a bar, then let go (its release rings on)
                piece.held(part, begin, first, velocity, turn - begin + piece.bar // 2, most=6.5)
                previous = first
                continue
            after = min(turn + 2 * TICKS, piece.end + piece.bar)
            second = pick(chord_at(turn), first, turn, after)
            last_entry = {first}
            if second == first:
                piece.held(part, begin, first, velocity, after - begin, most=6.5)
            else:
                piece.held(part, begin, first, velocity, turn - begin + 40, most=6.5)
                part.add(turn + 10, second, velocity - 6, after - turn)
            previous = second


def cello_pizz(piece: Piece) -> None:
    """Layer cello-pizz: the cellos plucking softly, like drops falling: the
    chord's bass on its first beat, its octave half a beat after the second,
    its fifth on the last beat (in 3/4, the bass and the octave only)."""
    spans = [s for s in piece.spans if "cello-pizz" in piece.section_at(s[0]).get("layers", [])]
    if not spans:
        return
    pizz = piece.part("cello-pizz", "cellos-pizz", "bass", -0.2, reverb=0.5)
    for tick, length, name in spans:
        dyn = piece.section_at(tick).get("dyn", 0.4)
        low = bass_note(name, 36)
        fifth = low + 7 if (low + 7) % 12 in chord(name)[1] else low + 12
        steps = [(0, low, 0), (3 * EIGHTH, low + 12, -8)] + ([(length - TICKS, fifth, -5)] if length >= 4 * TICKS else [])
        for at, note, softer in steps:
            if at < length:
                pizz.add(tick + at + piece.jitter(4), note, 46 + 24 * dyn + softer, TICKS)


def cello_answers(piece: Piece) -> list:
    """Layer cello-answer: the cellos answering the piano's tune. Where the
    tune holds a note three beats or more, or rests a beat or more, the
    cellos take the space left (from the held note's second beat, or the
    rest) to the tune's next note: the tune's last notes (up to three, the
    held one last) one or two octaves down (around G3), a beat each, the
    last held a beat into the tune's next phrase; every other answer turned
    upside down (its steps mirrored, kept in the tune's key). Its last note
    is a tone of the chord under it, no note sits a half step (or a minor
    ninth) from the tune's, and none repeats the one before. At most one answer every two bars, none
    shorter than two beats. Where a section has no tune (an opening, a
    close), the cellos hold the chords' bass instead, softly. Returns the
    notes played, (tick, end, note), for the parts that keep clear of them."""
    tune = piece.tune
    played = []
    wanted = lambda tick: "cello-answer" in piece.section_at(tick).get("layers", [])
    if not any(wanted(t) for t, _, _ in piece.spans):
        return played
    cello = piece.part("cello-answer", "cellos", "melody2", -0.25, reverb=0.5)
    key = {n % 12 for _, notes, _ in tune for n in notes}
    for start, end, section in piece.sections:  # no tune: the bass, held
        if "cello-answer" in section.get("layers", []) and not piece.tune_between(start, end):
            for tick, length, name in [s for s in piece.spans if start <= s[0] < end]:
                hold = length + (piece.bar if tick + length == piece.end else 0)
                note = bass_note(name, 38)
                piece.held(cello, tick + 30, note, 40 + 20 * section.get("dyn", 0.4), hold, most=6.5)
                played.append((tick, tick + hold, note))
    last, count = -10 ** 9, 0
    for i, (tick, notes, length) in enumerate(tune):
        if not wanted(tick):
            continue
        following = tune[i + 1][0] if i + 1 < len(tune) else piece.end
        if length >= 3 * TICKS:
            begin = tick + TICKS
        elif following - (tick + length) >= TICKS:
            begin = tick + length
        else:
            continue
        beats = (following - begin) // TICKS
        if beats < 2 or begin - last < 2 * piece.bar:
            continue
        tail = [max(n) for _, n, _ in tune[max(0, i - 2): i + 1]][-beats:]
        if count % 2:  # upside down: the same steps, mirrored
            tail = [tail[0] - (n - tail[0]) for n in tail]
        shift = -12 * round((sum(tail) / len(tail) - 55) / 12)
        line = [n + shift for n in tail]
        dyn = piece.section_at(tick).get("dyn", 0.4)
        for k, note in enumerate(line):
            at = begin + k * TICKS
            name = next(s[2] for s in piece.spans if s[0] <= at < s[0] + s[1])
            _, tones, _ = chord(name)
            sounding = piece.tune_between(at, at + TICKS)
            if k == len(line) - 1 and note % 12 not in tones:  # it ends on the chord
                note = min((n for n in range(note - 4, note + 5) if n % 12 in tones), key=lambda n: (abs(n - note), n))
            elif note % 12 not in key | set(tones):  # a mirrored step out of the key
                note = next(n for n in (note - 1, note + 1, note - 2, note + 2) if n % 12 in key | set(tones))
            if any((note - s) % 12 in (1, 11) for s in sounding):
                note = min((n for n in range(note - 4, note + 5) if n % 12 in tones
                            and all((n - s) % 12 not in (1, 11) for s in sounding)),
                           key=lambda n: (abs(n - note), n), default=note)
            if k and note == line[k - 1]:  # moved onto the note before: the answer moves on instead
                allowed = set(tones) if k == len(line) - 1 else key | set(tones)
                note = min((n for n in range(note - 4, note + 5) if n != line[k - 1] and n % 12 in allowed
                            and all((n - s) % 12 not in (1, 11) for s in sounding)),
                           key=lambda n: (abs(n - note), n), default=note)
            line[k] = note
        for k, note in enumerate(line):
            at = begin + k * TICKS
            stop = following + TICKS if k == len(line) - 1 else at + TICKS + 30  # legato; the last into the next phrase
            velocity = 46 + 24 * dyn - 3 * k
            cello.add(at + piece.jitter(5), note, velocity, stop - at)
            played.append((at, stop, note))
        last, count = begin, count + 1
    return played


def ending(piece: Piece, piano: Part) -> None:
    """The last chord rolled from the deep bass, held a bar longer, struck at
    ending_velocity (52 unless the score asks; the tune's last notes 6 over)."""
    tick, length, name = piece.spans[-1]
    bass, tones, _ = chord(name)
    low = above(bass, piece.score.get("bass_low", 33) - 5)
    roll = [low, low + 12] + [n for n in range(low + 13, low + 32) if n % 12 in tones][:4]
    piano.notes = [n for n in piano.notes if n[0] < tick]
    strike = piece.score.get("ending_velocity", 52)
    for k, n in enumerate(roll):
        piano.add(tick + 70 * k, n, strike - 2 * k, length + piece.bar)
    last = [n for t, notes, _ in piece.tune for n in notes if t >= tick]
    for n in last:
        piano.add(tick + 70 * len(roll), n, strike + 6, length + piece.bar)


def compose(score: dict, folder: Path) -> str:
    score = STYLES.get(score.get("style"), {}) | score  # the piece's own settings win
    piece = Piece(score)
    piano = piece.part("piano", score.get("piano", "upright"), "piano", 0.0, reverb=score.get("piano_reverb", 0.35))
    piano.cap = score.get("velocity_cap", 127)
    if score.get("piano_tone"):
        piano.tone.update(score["piano_tone"])
    play_melody(piece, piano)
    left_hand(piece, piano)
    layers(piece)
    ending(piece, piano)
    if score.get("piano_layer"):  # a second keyboard doubling every note the piano plays, as a keyboard's layered sound
        double = piece.part("piano-layer", score["piano_layer"], "melody2", 0.0, reverb=score.get("piano_reverb", 0.35))
        double.notes, double.pedal, double.cap = list(piano.notes), list(piano.pedal), piano.cap
        double.tone.update(score.get("piano_layer_tone", {}))
    folder.mkdir(parents=True, exist_ok=True)
    sheet = []
    for name, part in piece.parts.items():
        write_part(part, piece.tempos, folder / f"{name}.mid", (piece.beats, 2))
        library, sfz, _ = INSTRUMENTS[part.instrument]
        sheet.append({"part": name, "library": library, "sfz": sfz, "role": part.role,
                      "gain_db": ROLES[part.role] + score.get("gains", {}).get(name, 0.0), "pan": part.pan,
                      "reverb": part.reverb, "tone": part.tone | score.get("tones", {}).get(name, {}),
                      "notes": len(part.notes)})
    room = score.get("room", {"rt60": 1.2})
    mix = {"hall": {"rt60": room["rt60"], "wet": room.get("wet", 1.0)}, "parts": sheet,
           "master": {"tone": 0.0, "air": 0.0, "width": 0.0, "level": 0.0}}
    if score.get("noise_db") is not None:
        mix["noise"] = {"db": score["noise_db"]}
    if score.get("loudness") is not None:  # LUFS, -16 unless asked
        mix["loudness"] = score["loudness"]
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
