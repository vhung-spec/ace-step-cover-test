"""A modelled piano: no recording, no AI, every note made from the physics
of a piano's strings, then written as samples and an SFZ file, so the same
mixer (render_samples.py) plays it as it plays a sampled instrument:

    python dark/piano_model.py <arrangements> <out>

builds, in <out>, every model the arrangements' mix sheets name (library
"model"), with the keys their parts play: <out>/<model>.sfz and
<out>/<model>/k<key>_v<layer>.flac. `--all` builds every key.

A note is the sound of its strings, struck:
- partials at the string's own, slightly stretched frequencies: a stiff
  string's inharmonicity, least in the tenor, more in the short bass strings
  of an upright and most in the treble;
- their strengths shaped by the felt hammer, which passes the partials below
  its corner and fewer and fewer above it (the corner higher the harder the
  key is struck: a soft note is darker), by the strike point (an eighth of
  the way along, so the 8th and 16th partials are weak), by a felt between
  hammers and strings muffling the highs alike for every strength, and by
  the soundboard, which sends out little below ~180 Hz (an upright's: its
  bass notes are heard by their upper partials) and answers each frequency
  a little differently (rough_db);
- each partial dying in two stages, a quick prompt sound and a slow
  aftersound, the higher partials sooner, the treble sooner than the bass
  (decay_s: the aftersound's 1/e time at middle C);
- two or three strings to a key above the bass, a little out of tune with
  each other, struck together: their partials drift apart and beat;
- a soft onset, the hammer's thud and click, the soundboard's lowest modes
  rung by every strike, and, if asked, the other strings ringing along (halo)
  or a brighter first moment (strike);
- heard in stereo from the player's seat: the bass a little to the left, the
  treble to the right, and the two sides' partials a little apart in phase
  (as two microphones hear a soundboard), more so the higher they are.
The hammer, felt and soundboard were fitted (least squares over the partials
H2-H6) to the user's choice, the Yamaha upright through H3's tone, key group
by key group, and to the user's references' tune; the decay to the
references' (the tune's fundamental 3-6 dB down 250 ms on).
Velocity layers: the same note struck at several strengths, each its own
brightness, all at the same loudness: the SFZ makes a note louder with its
velocity (sfizz's own curve, as the upright's), so loudness is smooth across
layers. The dampers stop a note within release_s of its key (and pedal)
lifting; the top keys have no dampers, as on a piano. Every key is sampled at
its own pitch, so no note is pitch-shifted.
"""

import argparse
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import mido
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

RATE = 44100
KEYS = range(21, 109)  # A0 to C8
LAYERS = ((1, 36, 28), (37, 52, 44), (53, 68, 60), (69, 90, 80), (91, 127, 110))  # velocities a layer plays, and its strike
UNDAMPED = 89  # F6 up: no dampers
BODY_HZ = (52.0, 66.0, 83.0)  # the soundboard's lowest modes
_NODES = np.random.default_rng(5).standard_normal(64)  # the soundboard's unevenness, an eighth of an octave apart


def BOARD(freq: np.ndarray) -> np.ndarray:
    """The soundboard's uneven answer (about -1 to 1) at each frequency: fixed
    random steps an eighth of an octave apart from 40 Hz, joined smoothly,
    with no slope over two octaves (it colours each note, not the balance)."""
    smooth = np.convolve(_NODES, [0.25, 0.5, 0.25], "same")
    smooth = smooth - np.convolve(smooth, np.ones(17) / 17, "same")
    smooth /= smooth.std()
    return np.interp(np.log2(np.maximum(freq, 40) / 40) * 8, np.arange(len(smooth)), smooth)


# The models the pieces name (their mix sheets' sfz, without .sfz): each the
# defaults below with its own changes.
DEFAULTS = {
    "hammer_hz": 300.0,  # the felt hammer's corner at middle C struck at velocity 64: partials above it fall...
    "hammer_order": 3.0,  # ...hammer_order times 6 dB an octave; the corner higher...
    "hammer_key": 0.0,  # ...2 ** hammer_key times an octave up (smaller, harder hammers)...
    "hammer_vel": 1.0,  # ...and (velocity / 64) ** hammer_vel times struck harder
    "felt_hz": 1100.0,  # a felt between hammers and strings: partials above it fall felt_order times 6 dB an octave
    "felt_order": 3.0,
    "board_hz": 180.0,  # the soundboard sends out little below this...
    "board_order": 4.0,  # ...board_order times 6 dB an octave
    "strike": 0.125,  # where the hammer meets the string, a fraction of its length
    "notch": 0.6,  # how deep the strike point's missed partials fall (0: not at all, 1: to nothing)
    "decay_s": 2.4,  # the aftersound's 1/e time at middle C...
    "decay_slope": 0.6,  # ...shorter by 2 ** decay_slope an octave up
    "prompt_ratio": 5.0,  # the prompt sound dies this many times faster
    "aftersound": 0.25,  # the aftersound's share of a partial at the start
    "decay_hz": 3000.0,  # partials die faster above this: 1 + (f / decay_hz) ** 2 times
    "detune_cents": 1.2,  # the unisons' spread
    "attack_ms": 4.0,
    "strike_db": -80.0,  # the strike's own brightness: what a harder felt (its corner strike_x times higher)
    # would add to the partials, dying within strike_ms (sooner the higher), this many dB of it; -80: none
    "strike_x": 3.0,
    "strike_ms": 40.0,
    "knock_db": -30.0,  # the hammer's thud against the note, struck at velocity 64...
    "knock_ms": 8.0,  # ...dying in about this long (longer in the bass)
    "knock_treble_db": -6.0,  # above C3 the thud softer by this much an octave, and higher (half an octave an octave)
    "rough_db": 4.0,  # the soundboard's uneven answer: partials up or down by about this much (dB), fixed per key
    "click_db": -40.0,  # the hammer's click, brighter and shorter than its thud, against the note
    "halo_db": -80.0,  # the other strings ringing along (the pedal's bloom), against the note; -80: none
    "body_db": -28.0,  # the soundboard's lowest modes (BODY_HZ), set ringing by every strike, against the note
    "body_s": 0.35,  # their 1/e time
    "body_treble_db": -12.0,  # above C3 they ring this much less an octave: a treble string stirs the board's lowest
    # modes little (rung as much as a bass note's, they were heard under the high notes as a thump, "tiếng bộp")
    "width": 0.3,  # the stereo spread (0: mono)
    "release_s": 0.3,  # the dampers
    "key_tilt_db": 0.0,  # loudness an octave up
    "treble_level_db": -4.5,  # the tune's high notes softer, as a pianist's top notes and an upright's treble are:
    "treble_from": 74,  # level up to treble_from (D5, about where the tune sits), this much down from treble_to (D6)
    "treble_to": 86,  # up (as loud as the middle, they jumped out of the tune: "tiếng bộp ... giống tiếng rè")
}
MODELS = {
    # fitted to the user's choice (the Yamaha upright as H3 plays it: its
    # partials note by note, its loudness key by key) and the references'
    # tune (its partials, its decay)
    "felt-model": {},
    # dreamier: its strings further apart (a slow shimmer), the other strings
    # ringing along, a longer aftersound
    "felt-dream": {"detune_cents": 2.5, "halo_db": -24.0, "decay_s": 3.0, "aftersound": 0.32},
    # closer: a little brighter, the felt hammer's thud and the board heard
    "felt-close": {"hammer_hz": 380.0, "knock_db": -22.0, "knock_ms": 20.0, "click_db": -36.0, "body_db": -24.0,
                   "width": 0.25},
    # Round 13, richer than felt-dream ("tiếng piano khác để nghe phong phú hơn"), each its own way:
    # a warm grand: longer strings (a soundboard that sends out the bass from 110 Hz), more partials (the felt
    # softer, its corner higher), a little brighter up the keyboard, a longer aftersound, wider
    "felt-grand": {"detune_cents": 1.6, "halo_db": -26.0, "decay_s": 3.6, "aftersound": 0.34, "board_hz": 110.0,
                   "board_order": 3.0, "hammer_hz": 380.0, "hammer_key": 0.25, "felt_hz": 1700.0, "felt_order": 2.0,
                   "body_db": -26.0, "width": 0.4},
    # clear: a harder felt, each note's first moment brighter (dying in 45 ms), its colour following the touch
    "felt-clear": {"detune_cents": 2.0, "halo_db": -26.0, "decay_s": 3.0, "aftersound": 0.3, "hammer_hz": 420.0,
                   "hammer_vel": 1.5, "felt_hz": 1900.0, "felt_order": 2.0, "strike_db": -16.0, "strike_ms": 45.0},
    # bloom: the other strings ringing along louder, a long aftersound, more of the board: a resonant wash
    "felt-bloom": {"detune_cents": 2.2, "halo_db": -16.0, "decay_s": 3.8, "aftersound": 0.4, "board_hz": 140.0,
                   "hammer_hz": 340.0, "felt_hz": 1400.0, "body_db": -24.0, "width": 0.45},
    # wood: a close, warm upright: the felt's thud and the board's wood heard, each note its own colour
    "felt-wood": {"detune_cents": 1.8, "halo_db": -28.0, "decay_s": 3.0, "aftersound": 0.3, "hammer_hz": 360.0,
                  "felt_hz": 1500.0, "board_hz": 130.0, "knock_db": -24.0, "knock_ms": 14.0, "body_db": -22.0,
                  "body_s": 0.5, "rough_db": 6.0, "width": 0.35},
}


def inharmonicity(key: int) -> float:
    """B of f_n = n f0 sqrt(1 + B n^2): least around D3, more in the bass's
    short wound strings (an upright's) and most in the treble."""
    if key >= 50:
        return 10 ** (-3.83 + 0.038 * (key - 50))
    return 10 ** (-3.83 + 0.025 * (50 - key))


def strings(key: int) -> int:
    return 1 if key < 32 else 2 if key < 45 else 3


def lowpass(freq: np.ndarray, corner: float, order: float) -> np.ndarray:
    return 1 / np.sqrt(1 + (freq / corner) ** (2 * order))


def partials(key: int, velocity: int, p: dict, harder: float = 1.0) -> tuple:
    """The partials' frequencies and strengths, struck at velocity (by a felt
    `harder` times brighter: its corner that much higher)."""
    f0 = 440 * 2 ** ((key - 69) / 12)
    n = np.arange(1, 81)
    freq = n * f0 * np.sqrt(1 + inharmonicity(key) * n * n)
    hammer = p["hammer_hz"] * harder * 2 ** (p["hammer_key"] * (key - 60) / 12) * (velocity / 64) ** p["hammer_vel"]
    amp = (1 - p["notch"] * (1 - np.abs(np.sin(np.pi * n * p["strike"])))) \
        * lowpass(freq, hammer, p["hammer_order"]) * lowpass(freq, p["felt_hz"], p["felt_order"]) \
        / np.sqrt(1 + (p["board_hz"] / freq) ** (2 * p["board_order"]))
    if p["rough_db"]:  # the soundboard answers every frequency differently: a fixed, uneven curve, and each
        # key's bridge position its own unevenness on top
        amp = amp * 10 ** ((p["rough_db"] * (BOARD(freq) + 0.5 * np.random.default_rng(key).standard_normal(len(n)))) / 20)
    keep = (freq < 9000) & (amp > amp.max() * 10 ** (-90 / 20)) if harder == 1.0 else partials(key, velocity, p)[2]
    return freq[keep], amp[keep], keep


def note(key: int, velocity: int, p: dict, seed: int) -> np.ndarray:
    """One note struck at velocity, stereo (2, samples), not yet levelled."""
    rng = np.random.default_rng(seed)
    after = p["decay_s"] * 2 ** (-p["decay_slope"] * (key - 60) / 12)
    seconds = float(np.clip(3 * after, 2.5, 12.0)) if key < UNDAMPED else float(np.clip(3 * after, 1.5, 4.0))
    t = np.arange(int(seconds * RATE)) / RATE
    freq, amp, _ = partials(key, velocity, p)
    slow = after / (1 + (freq / p["decay_hz"]) ** 2)
    fast = slow / p["prompt_ratio"]
    k = strings(key)
    detune = p["detune_cents"] * np.array([0.0, 1.0, -0.8])[:k] * rng.uniform(0.6, 1.4)
    share = np.array([1.0, 0.7, 0.5])[:k] / np.array([1.0, 0.7, 0.5])[:k].sum()  # the strings ring unequally
    pan = float(np.clip((key - 64) / 40, -1, 1)) * p["width"]
    gains = np.sqrt([1 - pan, 1 + pan])
    out = np.zeros((2, len(t)))
    for fn, an, ts, tf in zip(freq, amp, slow, fast):
        env = an * ((1 - p["aftersound"]) * np.exp(-t / tf) + p["aftersound"] * np.exp(-t / ts))
        apart = p["width"] * np.pi * min(1.0, fn / 1500) * rng.uniform(-1, 1)  # the two sides' phases
        for cents, part in zip(detune, share):  # the strings of a key struck together, in phase, drifting apart
            phase = 2 * np.pi * fn * 2 ** (cents / 1200) * t
            for side, shift in enumerate((-apart / 2, apart / 2)):
                out[side] += env * np.sin(phase + shift) * gains[side] * part
    peak = np.abs(out).max()  # the note itself: what the knock, the body and the halo are set against
    treble = max(0, key - 48) / 12  # octaves above C3
    if p["strike_db"] > -80:  # what a harder felt adds at first, dying within strike_ms (sooner the higher)
        bright = np.maximum(partials(key, velocity, p, p["strike_x"])[1] - amp, 0) * 10 ** (p["strike_db"] / 20)
        first = t[: int(0.3 * RATE)]
        for fn, bn in zip(freq, bright):
            if bn > 0:
                out[:, : len(first)] += bn * np.exp(-first / (p["strike_ms"] / 1000 / (1 + fn / 2000))) \
                    * np.sin(2 * np.pi * fn * first) * gains[:, None]
    onset = np.minimum(1, t / (p["attack_ms"] / 1000))
    out *= 0.5 - 0.5 * np.cos(np.pi * onset)
    if p["halo_db"] > -80:  # the strings tuned to its partials ring along, a little out of tune with them: slow to
        # rise, slow to die
        halo = np.zeros((2, len(t)))
        for fn, an in zip(freq[:8], amp[:8]):
            for side in range(2):
                halo[side] += an * np.sin(2 * np.pi * fn * 2 ** (rng.uniform(-4, 4) / 1200) * t + rng.uniform(0, 2 * np.pi))
        halo *= (1 - np.exp(-t / 0.25)) * np.exp(-t / (2 * after))
        out += halo * peak / (np.abs(halo).max() + 1e-12) * 10 ** (p["halo_db"] / 20)
    if p["knock_db"] > -80:  # the hammer's thud: a short burst of low noise, harder struck, louder and brighter
        burst = rng.standard_normal(int(0.08 * RATE))
        rise = 2 ** (treble / 2)  # a treble hammer's knock is a short tick, not a low thud
        sos = butter(2, [50 * rise, (300 + 1500 * velocity / 127) * rise], "band", fs=RATE, output="sos")
        burst = sosfilt(sos, burst) * np.exp(-np.arange(len(burst)) / RATE
                                             / (p["knock_ms"] / 1000 * (0.5 + (1 - (key - 21) / 87))))
        burst *= peak / (np.abs(burst).max() + 1e-12) * 10 ** ((p["knock_db"] + p["knock_treble_db"] * treble) / 20) \
            * velocity / 64
        out[:, : len(burst)] += burst * gains[:, None]
    if p["click_db"] > -80:
        click = rng.standard_normal(int(0.02 * RATE))
        click = sosfilt(butter(2, [700, 4000], "band", fs=RATE, output="sos"), click) * np.exp(-np.arange(len(click)) / RATE / 0.002)
        click *= peak / (np.abs(click).max() + 1e-12) * 10 ** (p["click_db"] / 20) * (velocity / 64) ** 1.5
        out[:, : len(click)] += click * gains[:, None]
    if p["body_db"] > -80:  # the soundboard's own low modes, rung by the strike: the piano's wooden weight
        body = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 2 * np.pi)) * rng.uniform(0.5, 1.0)
                   for f in BODY_HZ) * np.exp(-t / p["body_s"])
        body *= 0.5 - 0.5 * np.cos(np.pi * np.minimum(1, t / 0.01))
        body *= peak / (np.abs(body).max() + 1e-12) * 10 ** ((p["body_db"] + p["body_treble_db"] * treble) / 20) \
            * velocity / 64
        out += body * gains[:, None]
    fade = np.minimum(1, (len(t) - np.arange(len(t))) / (0.4 * RATE))  # a damper at the sample's end
    return out * fade


def sample(job: tuple) -> None:
    """One key struck at one layer's strength, levelled, written as FLAC."""
    p, key, layer, path = job
    audio = note(key, LAYERS[layer][2], p, seed=key * 10 + layer)
    level = np.sqrt(np.mean(audio[:, : int(0.3 * RATE)] ** 2))
    treble = p["treble_level_db"] * min(1.0, max(0.0, (key - p["treble_from"]) / (p["treble_to"] - p["treble_from"])))
    audio *= 0.08 / level * 10 ** ((p["key_tilt_db"] * (key - 60) / 12 + treble) / 20)
    sf.write(path, audio.T.astype(np.float32), RATE, subtype="PCM_16")


def build(name: str, out: Path, keys) -> Path:
    """The model's samples for these keys (one process a CPU) and its SFZ file."""
    p = DEFAULTS | MODELS[name]
    folder = out / name
    folder.mkdir(parents=True, exist_ok=True)
    lines = ["// A modelled piano (dark/piano_model.py): no recording, every note made from its strings.",
             f"// {name}: {json.dumps(p)}", "<global>", "amp_veltrack=100", ""]
    jobs = []
    for key in sorted(keys):
        release = p["release_s"] if key < UNDAMPED else 3.0
        for layer, (low, high, _) in enumerate(LAYERS):
            path = folder / f"k{key}_v{layer}.flac"
            jobs.append((p, key, layer, path))
            lines.append(f"<region> sample={name}/{path.name} key={key} pitch_keycenter={key} "
                         f"lovel={low} hivel={high} ampeg_release={release:g}")
    with ProcessPoolExecutor() as pool:
        list(pool.map(sample, jobs))  # the bass first: its notes take longest
    sfz = out / f"{name}.sfz"
    sfz.write_text("\n".join(lines) + "\n")
    return sfz


def wanted(arrangements: Path) -> dict:
    """{model: keys its parts play}, from the arrangements' mix sheets."""
    found = {}
    for sheet in sorted(arrangements.glob("*/mix.json")):
        for entry in json.loads(sheet.read_text())["parts"]:
            if entry["library"] != "model":
                continue
            keys = found.setdefault(Path(entry["sfz"]).stem, set())
            for message in mido.MidiFile(sheet.parent / f"{entry['part']}.mid"):
                if message.type == "note_on":
                    keys.add(message.note)
    return found


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("arrangements", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--all", action="store_true", help="every key, not only those the pieces play")
    args = parser.parse_args()
    for name, keys in wanted(args.arrangements).items():
        print(build(name, args.out, KEYS if args.all else keys), f"{len(keys)} keys", flush=True)


if __name__ == "__main__":
    main()
