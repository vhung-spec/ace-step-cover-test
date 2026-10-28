"""Renders the parts written by arrange.py with real instrument samples and
mixes them into one piece per folder:

    python render_samples.py out/sampled --sfizz path/to/sfizz_render --vsco <VSCO-2-CE> --vcsl <VCSL>
        [--salamander <SalamanderGrandPiano>] [--jrhodes <jRhodes3d>]

(instruments of our own, such as the synth pad, are in instruments/)

- each part is played by sfizz_render from its SFZ instrument (mix.json), at
  the samples' own rate (44.1 kHz: no resampling for a note at a sampled
  pitch) with sfizz's best interpolation (a 72-point windowed sinc, its own
  choice for offline work), then played again louder or quieter until its
  peaks sit between -20 and
  -1 dBFS: sfizz writes 16-bit WAV, which clips above full scale and turns
  grainy when a quiet part is turned up afterwards. A piano's release samples
  (the dampers, which all sound at once when the pedal lifts) can be turned
  down;
- each part gets its tone (high-pass, low-pass, high shelf; hissing parts
  have their highs hushed in their quiet moments), and its loudness
  while it plays is set against the melody's by its role (arrange.ROLES), so
  libraries recorded at different levels still sit right; its stereo image is
  narrowed as asked and centred (samples recorded with spaced microphones
  lean to one side, some notes far more than others), then it is placed in
  the stereo field;
- a hall reverb: a synthetic impulse response (noise in bands, each dying at
  its own rate, the highs soonest and quietest, the highs also building up
  slowest, with no single echo standing out), so no recording of a real hall
  and no licence is needed; what goes into it is cut above 6 kHz, so hammer
  and bow noise do not ring on as a hiss; a style may ask for a smaller room
  (a shorter rt60: it answers sooner) and send less into it (wet), for a
  sound close by rather than across a hall;
- a style may lay a soft hush (dark pink noise) under the music, as sleep
  music does;
- the mix is mastered (master.py): a piece leaning more than 1 dB to one side
  is evened out, and the steps toward two reference recordings' sound (tone,
  air, width, a slow leveller) work as strongly as its style asks (mix.json;
  all off for now); with --premaster, the piece before its master is saved as
  well, as loud, to compare;
- the piece loses its rumble below 30 Hz and is brought to -16 LUFS (YouTube
  plays music at about -14), a look-ahead limiter keeping peaks below -1.5
  dBFS; its gain glides, never jumps (a jump clicks), and it takes at most
  3 dB off a peak: a piece that would need more is left a little quieter
  (down to -19 LUFS). The last notes fade out over the reverb's tail; the
  piece is saved as <folder>.wav and <folder>.mp3 (LAME, 320 kbit/s), and
  the log shows how much was limited, how the left and right sides balance
  and how much hiss shows (each part's, and the piece's, in its quietest
  moments).
"""

import argparse
import json
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from pathlib import Path

import numpy as np
import pyloudnorm
import soundfile as sf
from scipy.ndimage import maximum_filter1d, uniform_filter1d
from scipy.signal import butter, fftconvolve, lfilter, sosfilt, sosfiltfilt, welch

import master
from master import dehiss

RATE = 44100  # the samples' own rate
TARGET_LUFS = -16.0
QUIETEST_LUFS = -19.0  # a piece with strong peaks may be this quiet rather than limited hard
CEILING_DB = -1.5  # peaks rise a little in MP3 encoding
MOST_LIMITING_DB = 3.0


def sfz_copy(sfz: Path, part: str, db: float, tone: dict) -> Path:
    """A copy of an SFZ file for one part, next to it (its sample paths are
    relative), with every region turned up or down by db (sfizz's
    global_volume opcode), its release samples, if any, by the tone's
    release_db, and, if the tone says halo false, a piano's samples recorded
    with the pedal down (all strings free to ring along) left out: every note
    plays its pedal-up sample, the pedal still holding it; with pedal_noise
    false, the pedal's own thump and squeak (played as it goes down and up)
    are left out too. The tone's set_cc ({controller: 0-1}) sets where the
    instrument's controllers start (the Rhodes' stereo width is its mod wheel)."""
    text = sfz.read_text(errors="replace")
    for cc, value in tone.get("set_cc", {}).items():
        setting = f"set_hdcc{cc}={value:g}"
        if re.search(rf"\bset_hdcc{cc}=", text):
            text = re.sub(rf"\bset_hdcc{cc}=\S+", setting, text)
        elif "<control>" in text:
            text = text.replace("<control>", f"<control>\n{setting}", 1)
        else:
            text = f"<control>\n{setting}\n{text}"
    line = f"global_volume={db:g}"
    if "<global>" in text:
        text = text.replace("<global>", f"<global>\n{line}", 1)
    else:
        text = f"<global>\n{line}\n{text}"
    if tone.get("release_db") is not None:
        amplitude = 100 * 10 ** (tone["release_db"] / 20)
        text = re.sub(r"trigger=release\b", f"trigger=release\namplitude={amplitude:.3f}", text)
    if tone.get("halo") is False:
        text = "".join(g for g in re.split(r"(?=<group>)", text) if "locc64=65" not in g).replace("hicc64=64", "hicc64=127")
    if tone.get("pedal_noise") is False:
        text = "".join(g for g in re.split(r"(?=<group>)", text) if "on_locc64" not in g)
    copy = sfz.with_name(f".{sfz.stem}.{part}.{db:+g}dB.sfz")
    copy.write_text(text)
    return copy


def render_part(sfizz: str, sfz: Path, part: str, midi: Path, wav: Path, tone: dict) -> np.ndarray:
    """Plays one part; rendering stops at the MIDI file's end of track (8 beats
    after its last event): without that, sfizz_render waits for full silence,
    which some instruments never reach."""
    db = 0.0
    for attempt in range(5):
        started = time.time()
        subprocess.run([sfizz, "--sfz", str(sfz_copy(sfz, part, db, tone)), "--midi", str(midi),
                        "--wav", str(wav), "--samplerate", str(RATE), "--polyphony", "256", "--quality", "10",
                        "--use-eot"], check=True, capture_output=True, timeout=600)
        print(f"    {part} at {db:+g} dB: {time.time() - started:.0f} s", flush=True)
        audio, rate = sf.read(wav, always_2d=True, dtype="float32")
        if rate != RATE:
            raise ValueError(f"{wav}: {rate} Hz")
        peak = 20 * np.log10(np.abs(audio).max() + 1e-12)
        if peak > -0.1:  # clipped
            db -= 12
        elif peak < -20 and attempt < 4 and db < 30:
            db = min(30, db + round(-8 - peak))
        else:
            break
    else:
        raise RuntimeError(f"{part}: no level without clipping")
    return audio.T if audio.shape[1] == 2 else np.repeat(audio.T, 2, axis=0)


def high_shelf(freq: float, db: float) -> tuple:
    """Biquad coefficients of a high shelf (RBJ's audio EQ cookbook, slope 1)."""
    a = 10 ** (db / 40)
    w = 2 * np.pi * freq / RATE
    cos, alpha = np.cos(w), np.sin(w) / np.sqrt(2)
    b = np.array([a * ((a + 1) + (a - 1) * cos + 2 * np.sqrt(a) * alpha), -2 * a * ((a - 1) + (a + 1) * cos),
                  a * ((a + 1) + (a - 1) * cos - 2 * np.sqrt(a) * alpha)])
    den = np.array([(a + 1) - (a - 1) * cos + 2 * np.sqrt(a) * alpha, 2 * ((a - 1) - (a + 1) * cos),
                    (a + 1) - (a - 1) * cos - 2 * np.sqrt(a) * alpha])
    return b / den[0], den / den[0]


def apply_tone(audio: np.ndarray, tone: dict) -> np.ndarray:
    """A part's tone: a high-pass and a low-pass (Hz; the low-pass 12 dB an
    octave, or steeper as lowpass_order asks), a high shelf (Hz, dB), and its
    highs hushed in its quiet moments if it hisses (dehiss)."""
    if tone.get("highpass"):
        audio = sosfilt(butter(2, tone["highpass"], "high", fs=RATE, output="sos"), audio, axis=-1)
    if tone.get("lowpass"):
        order = tone.get("lowpass_order", 2)
        audio = sosfilt(butter(order, tone["lowpass"], "low", fs=RATE, output="sos"), audio, axis=-1)
    if tone.get("shelf"):
        audio = lfilter(*high_shelf(*tone["shelf"]), audio, axis=-1)
    if tone.get("dehiss"):
        audio = dehiss(audio)
    return audio


def image(audio: np.ndarray, width: float) -> tuple[np.ndarray, float]:
    """A part's stereo image narrowed to width (0 mono, 1 as recorded), then
    centred: its louder side turned down and the quieter one up. Returns the
    audio and how far it leaned as recorded (dB, + to the left)."""
    lean = 20 * np.log10((np.sqrt(np.mean(audio[0] ** 2)) + 1e-12) / (np.sqrt(np.mean(audio[1] ** 2)) + 1e-12))
    mid, side = (audio[0] + audio[1]) / 2, (audio[0] - audio[1]) / 2 * width
    left, right = mid + side, mid - side
    still = 20 * np.log10((np.sqrt(np.mean(left ** 2)) + 1e-12) / (np.sqrt(np.mean(right ** 2)) + 1e-12))
    g = 10 ** (np.clip(still, -9, 9) / 40)
    return np.stack([left / g, right * g]), float(lean)


def hiss(audio: np.ndarray) -> float:
    """How much hiss shows when the music is quiet: the level from 4 to 16 kHz
    over the quietest tenth of the 50 ms moments where it sounds (within 50 dB
    of its loudest; the last 5 s, the fade, left out), under the median level
    of those moments (dB)."""
    mono = audio.mean(axis=0)
    mono = mono[: max(RATE, len(mono) - 5 * RATE)]
    high = sosfilt(butter(4, [4000, 16000], "band", fs=RATE, output="sos"), mono)
    frame = RATE // 20
    n = len(mono) // frame
    level = 10 * np.log10(np.mean(mono[: n * frame].reshape(n, frame) ** 2, axis=1) + 1e-20)
    sounding = level > level.max() - 50
    quiet = sounding & (level <= np.percentile(level[sounding], 10))
    high_level = np.mean(high[: n * frame].reshape(n, frame)[quiet] ** 2)
    return float(10 * np.log10(high_level + 1e-20) - np.median(level[sounding]))


def balance(audio: np.ndarray) -> float:
    """How much louder the left side is than the right (dB)."""
    return float(20 * np.log10((np.sqrt(np.mean(audio[0] ** 2)) + 1e-12) / (np.sqrt(np.mean(audio[1] ** 2)) + 1e-12)))


def playing_db(audio: np.ndarray) -> float:
    """Loudness (RMS, dB) over the 50 ms frames where the part plays, i.e.
    within 40 dB of its loudest frame."""
    mono = audio.mean(axis=0)
    frame = RATE // 20
    n = len(mono) // frame
    if n == 0:
        return -120.0
    rms = np.sqrt(np.mean(mono[: n * frame].reshape(n, frame) ** 2, axis=1)) + 1e-12
    db = 20 * np.log10(rms)
    return float(10 * np.log10(np.mean(10 ** (db[db > db.max() - 40] / 10))))


def pan(audio: np.ndarray, position: float) -> np.ndarray:
    """Constant-power balance, -1 left to 1 right; 0 leaves the part as recorded."""
    angle = (position + 1) * np.pi / 4
    return audio * (np.array([[np.cos(angle)], [np.sin(angle)]]) * np.sqrt(2))


# The hall at each frequency: (Hz, decay time against rt60, level in dB per
# octave at the start of the tail). The highs die soonest, as air and soft
# walls absorb them, so the tail is warm and carries no hiss; the lows are
# kept down, so it does not boom.
HALL = np.array([(63, 1.15, -9), (125, 1.1, -4), (250, 1.05, -1), (500, 1.0, 0), (1000, 0.95, 0),
                 (2000, 0.85, -1), (4000, 0.65, -3), (8000, 0.45, -6), (16000, 0.3, -10)])


@lru_cache
def hall_ir(rt60: float, seconds: float = 4.0, predelay: float = 0.025, seed: int = 1) -> np.ndarray:
    """Stereo impulse response of a warm hall: noise in third-octave bands, each
    dying at its own rate (HALL) and building up over 30 ms (the lows) to 80
    ms (the highs), so a note's attack does not set off a burst of hiss; no
    single echo stands out; a different noise on each side, so the hall is
    wide, each band equally loud on both, so it leans to neither. A smaller
    room (rt60 under 2.2 s) answers sooner: its predelay and build-up shrink
    with its rt60."""
    small = min(1.0, rt60 / 2.2)
    predelay *= small
    rng = np.random.default_rng(seed)
    n = int(seconds * RATE)
    t = np.arange(n) / RATE
    spectrum = np.fft.rfft(rng.standard_normal((2, n)), axis=-1)
    freqs = np.fft.rfftfreq(n, 1 / RATE)
    ir = np.zeros((2, n))
    for centre in 1000 * 2 ** (np.arange(-14, 14) / 3):  # 40 Hz to 20 kHz
        band = (freqs >= centre * 2 ** (-1 / 6)) & (freqs < centre * 2 ** (1 / 6))
        decay, level = (np.interp(np.log2(centre), np.log2(HALL[:, 0]), HALL[:, k]) for k in (1, 2))
        onset = np.interp(np.log2(centre), np.log2([250, 8000]), [0.03, 0.08]) * small
        tail = np.fft.irfft(spectrum * band, n=n, axis=-1) * np.exp(-6.91 * t / (rt60 * decay))
        tail *= 1 - np.exp(-t / onset)  # the reflections build up
        tail /= np.sqrt(np.mean(tail ** 2, axis=-1, keepdims=True))  # every band as loud, on both sides
        ir += tail * 10 ** (level / 20)
    ir = np.concatenate([np.zeros((2, int(predelay * RATE))), ir], axis=1)
    return ir / np.sqrt(np.sum(ir ** 2) / 2)


def noise_bed(n: int, seed: int = 2) -> np.ndarray:
    """A soft, dark hush (pink noise between 120 and 1200 Hz, a different noise
    on each side), as the sleep-music recordings lay under their piano; fading
    in over 2 s and out over the last 3 s. Its loudness is 0 dB RMS."""
    rng = np.random.default_rng(seed)
    pink = lfilter([0.049922035, -0.095993537, 0.050612699, -0.004408786],  # -3 dB an octave (Paul Kellet)
                   [1, -2.494956002, 2.017265875, -0.522189400], rng.standard_normal((2, n)), axis=-1)
    hush = sosfilt(butter(2, [120, 1200], "band", fs=RATE, output="sos"), pink, axis=-1)
    hush /= np.sqrt(np.mean(hush ** 2, axis=-1, keepdims=True))
    fade = np.minimum(1, np.minimum(np.arange(n) / (2 * RATE), (n - np.arange(n)) / (3 * RATE)))
    return hush * fade


def limit(audio: np.ndarray, ceiling_db: float = CEILING_DB, attack: float = 0.008,
          release: float = 0.15) -> tuple[np.ndarray, float, float]:
    """A look-ahead limiter whose gain never jumps (a jump clicks): it falls in
    a straight line over `attack` seconds to what a peak needs, reaching it at
    the peak, and recovers at the release rate, so no sample goes over the
    ceiling. Returns the audio, the largest gain reduction (dB) and the share
    of the piece turned down by more than 1 dB."""
    ceiling = 10 ** (ceiling_db / 20)
    level = np.abs(audio).max(axis=0)
    needed = 1 - np.minimum(1, ceiling / np.maximum(level, 1e-12))  # reduction per sample, 0 to 1
    size = 2 * int(attack * RATE / 2) + 1
    ramped = uniform_filter1d(maximum_filter1d(needed, size=size), size=size)  # full at each peak
    step = 1 / (release * RATE)  # the release, in log units per sample
    n = np.arange(len(ramped))
    held = np.maximum.accumulate(np.log(ramped + 1e-12) + n * step)  # each reduction, dying away after its peak
    reduction = np.minimum(1, np.exp(held - n * step))
    out = np.clip(audio * (1 - reduction), -ceiling, ceiling)  # the clip only catches rounding
    return (out, float(20 * np.log10(1 - reduction.max() + 1e-12)),
            float(np.mean(reduction > 1 - 10 ** (-1 / 20))))


def fade_tail(audio: np.ndarray, seconds: float = 3.0) -> np.ndarray:
    """Ends the piece when it has faded 60 dB below its peak, the last seconds
    faded out, rather than on a long, barely audible tail."""
    level = np.abs(audio).max(axis=0)
    loud = np.nonzero(level > level.max() * 10 ** (-60 / 20))[0]
    audio = audio[:, : loud[-1] + 1] if len(loud) else audio
    n = min(int(seconds * RATE), audio.shape[1])
    audio[:, -n:] *= np.linspace(1, 0, n) ** 2
    return audio


def finish(mixed: np.ndarray) -> tuple[np.ndarray, float, float]:
    """The piece at TARGET_LUFS, limited by at most MOST_LIMITING_DB, or quieter
    (down to QUIETEST_LUFS) rather than limited harder: the limited piece, the
    most it took off a peak (dB) and how much of the time it took over 1 dB."""
    meter = pyloudnorm.Meter(RATE)
    loudness = meter.integrated_loudness(mixed.T)
    over = 20 * np.log10(np.abs(mixed).max()) + TARGET_LUFS - loudness - CEILING_DB - MOST_LIMITING_DB
    target = max(QUIETEST_LUFS, TARGET_LUFS - max(0.0, over))  # quieter rather than limited hard
    gain_db = target - loudness
    for _ in range(4):  # limiting lowers the loudness a little: measure again
        limited, worst, share = limit(mixed * 10 ** (gain_db / 20))
        error = target - meter.integrated_loudness(limited.T)
        if abs(error) < 0.05:
            break
        gain_db += error
    return limited, worst, share


def save(audio: np.ndarray, wav: Path) -> None:
    """Writes a piece as 24-bit WAV and as MP3 (LAME, 320 kbit/s) beside it."""
    sf.write(wav, audio.T, RATE, subtype="PCM_24")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "libmp3lame", "-b:a", "320k",
                    str(wav.with_suffix(".mp3"))], check=True)


def mix_folder(folder: Path, sfizz: str, libraries: dict, keep_parts: bool, premaster: Path | None = None) -> Path:
    sheet = json.loads((folder / "mix.json").read_text())
    ir = hall_ir(sheet["hall"]["rt60"])
    wet_level = sheet["hall"].get("wet", 1.0)  # every part's send into it, times this

    def render(entry: dict) -> np.ndarray:
        sfz = libraries[entry["library"]] / entry["sfz"]
        return render_part(sfizz, sfz, entry["part"], folder / f"{entry['part']}.mid",
                           folder / f"{entry['part']}.wav", entry["tone"])

    with ThreadPoolExecutor(max_workers=4) as pool:  # one sfizz_render per CPU
        audios = list(pool.map(render, sheet["parts"]))
    parts = {}
    for entry, audio in zip(sheet["parts"], audios):
        peak = 20 * np.log10(np.abs(audio).max() + 1e-12)
        audio, lean = image(apply_tone(audio, entry["tone"]), entry["tone"].get("width", 1.0))
        print(f"  {entry['part']}: {audio.shape[1] / RATE:.1f} s, peak {peak:.1f} dBFS, recorded "
              f"{abs(lean):.1f} dB to the {'left' if lean > 0 else 'right'}, hiss {hiss(audio):.0f} dB", flush=True)
        parts[entry["part"]] = (entry, audio)
    melody = [playing_db(a) for e, a in parts.values() if e["role"] in ("melody", "piano")]
    reference = float(np.mean(melody)) if melody else -20.0
    n = max(a.shape[1] for _, a in parts.values()) + ir.shape[1]
    dry, send = np.zeros((2, n)), np.zeros((2, n))
    for name, (entry, audio) in parts.items():
        gain = 10 ** ((reference + entry["gain_db"] - playing_db(audio)) / 20)
        placed = pan(audio * gain, entry["pan"])
        dry[:, : placed.shape[1]] += placed
        send[:, : placed.shape[1]] += placed * entry["reverb"] * wet_level
        if not keep_parts:
            (folder / f"{name}.wav").unlink()
    send = sosfilt(butter(2, 6000, "low", fs=RATE, output="sos"), send, axis=-1)  # no hiss into the hall
    wet = np.stack([fftconvolve(send[c], ir[c])[:n] for c in range(2)])
    rumble = butter(2, 30, "high", fs=RATE, output="sos")
    mixed = fade_tail(sosfilt(rumble, dry + wet, axis=-1))
    if sheet.get("noise"):  # a hush under the music, so many dB under the melody
        mixed += noise_bed(mixed.shape[1]) * 10 ** ((reference + sheet["noise"]["db"]) / 20)
        print(f"  a hush under it all, {-sheet['noise']['db']:g} dB under the melody", flush=True)
    unmastered = mixed
    if sheet.get("master"):
        steps = sheet["master"]
        mixed, report = master.master(mixed, steps["tone"], steps["air"], steps["width"], steps["level"])
        print(f"  master: {report}", flush=True)
    meter = pyloudnorm.Meter(RATE)
    mixed, worst, share = finish(mixed)
    quarters = [balance(q) for q in np.array_split(mixed, 4, axis=1)]
    print(f"  limiter: at most {-worst:.1f} dB, {100 * share:.1f} % of the time over 1 dB; left-right balance "
          f"{balance(mixed):+.1f} dB (quarters {', '.join(f'{q:+.1f}' for q in quarters)}); hiss {hiss(mixed):.0f} dB",
          flush=True)
    out = folder.with_suffix(".wav")
    save(mixed, out)
    if premaster is not None:  # the same piece before its master, as loud, to compare
        premaster.mkdir(parents=True, exist_ok=True)
        save(finish(unmastered)[0], premaster / out.name)
        (premaster / out.name).unlink()
    print(f"{folder.name}: {mixed.shape[1] / RATE:.0f} s, hall {sheet['hall']['rt60']} s (sends x{wet_level:g}), "
          f"{meter.integrated_loudness(mixed.T):.1f} LUFS, peak {20 * np.log10(np.abs(mixed).max()):.1f} dBFS "
          f"-> {out.with_suffix('.mp3')}", flush=True)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--sfizz", default="sfizz_render")
    parser.add_argument("--vsco", type=Path, required=True)
    parser.add_argument("--vcsl", type=Path, required=True)
    parser.add_argument("--salamander", type=Path, help="needed for the salamander style")
    parser.add_argument("--jrhodes", type=Path, help="needed for the Rhodes (ballad-ep, ballad-rhodes)")
    parser.add_argument("--keep-parts", action="store_true", help="keep each part's WAV")
    parser.add_argument("--premaster", type=Path, help="also save each piece before its master here (MP3)")
    args = parser.parse_args()
    libraries = {"vsco": args.vsco, "vcsl": args.vcsl, "salamander": args.salamander, "jrhodes": args.jrhodes,
                 "local": Path(__file__).parent / "instruments"}  # our own instruments (sfizz's oscillators)
    for folder in sorted(p for p in args.out.iterdir() if (p / "mix.json").is_file()):
        print(f"== {folder.name}", flush=True)
        mix_folder(folder, args.sfizz, libraries, args.keep_parts, args.premaster)


if __name__ == "__main__":
    main()
