"""Masters a mixed piece toward the sound of two reference recordings of soft
Christmas piano (the user's; only their sound was measured, as the numbers
below): render_samples.py calls master() on each mix, before it sets the
loudness. In order:

- balance: a piece leaning more than 1 dB to one side has that side turned
  down until it leans 1 dB;
- tone: a steep high-pass under 40 Hz, then the piece's long-term spectrum
  (third-octave bands over the moments that sound, against its 250 Hz-1 kHz
  level) moved toward the references' (TARGET): the difference is smoothed
  over about an octave, so the notes a tune happens to dwell on do not count,
  and applied by at most 3 dB a band, never upwards above 2 kHz (from 2.5 to
  6 kHz lay the rustle the samples' hiss made) nor under 80 Hz;
- air: the references' highs (8-16 kHz) rise and fall with their notes, while
  the piano's own were cut with its hiss; air is made again from the piece's
  2-6 kHz, whose loud moments a soft saturation lends overtones (on the quiet
  hiss it stays linear and adds none), high-passed at 5 kHz and mixed in
  AIR_DB under the piece in its loud moments;
- width: the side (left minus right) brought to the references' level against
  the middle, by at most 3 dB narrower or 1.5 dB wider;
- level: the references hold their loudness within a few dB, so a slow
  leveller pulls the 1.5 s level toward its median at 4:1, by at most 8 dB
  down and 6 dB up, turning down over 0.6 s and back up over 2.5 s; silences
  and the last 10 s, where the piece rings out, are not lifted. The quiet
  moments it lifts would bring up the samples' faint hiss with them, so the
  piece's highs are then hushed in its quietest moments (dehiss, by up to 8 dB).

Each step takes a strength from 0 (off) to 1 (as described).
"""

import numpy as np
from scipy.ndimage import uniform_filter1d
from scipy.signal import butter, sosfilt, sosfiltfilt, stft

RATE = 44100
CENTRES = np.array([31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600,
                    2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000])
# The references' long-term spectrum, the two averaged (dB against their 250 Hz-1 kHz level).
TARGET = np.array([-33.4, -29.2, -25.9, -10.2, -10.2, -8.0, -6.3, -3.1, 2.0, -1.5, 1.7, 0.2, -0.5, 2.2, -1.1,
                   -3.8, -7.0, -8.7, -12.4, -15.3, -19.7, -24.6, -23.8, -26.1, -27.4, -26.1, -33.1, -34.2])
SIDE_DB = -2.9  # side against middle, both references
AIR_DB = -40.0  # made air under the whole in the loud moments (their 8-16 kHz: -38 and -54 dB)


def band_levels(audio: np.ndarray) -> np.ndarray:
    """Third-octave levels of the long-term spectrum over the moments that sound
    (within 40 dB of the loudest), against the 250 Hz-1 kHz level (dB)."""
    f, _, spec = stft(audio.mean(axis=0), RATE, nperseg=8192, noverlap=6144)
    power = np.abs(spec) ** 2
    total = 10 * np.log10(power.sum(axis=0) + 1e-20)
    mean = power[:, total > total.max() - 40].mean(axis=1)
    levels = np.array([10 * np.log10(mean[(f >= c / 2 ** (1 / 6)) & (f < c * 2 ** (1 / 6))].sum() + 1e-30)
                       for c in CENTRES])
    mids = (CENTRES >= 250) & (CENTRES <= 1000)
    return levels - 10 * np.log10(np.mean(10 ** (levels[mids] / 10)))


def dehiss(audio: np.ndarray, split: float = 2500, most_db: float = 10.0, over_db: float = 10.0,
           release: float = 0.12) -> np.ndarray:
    """Hushes the highs in their quiet moments, where they hold little but the
    hiss of the samples (a dozen voices of it at once under a piano's pedal):
    above split Hz, whenever their level comes within over_db of their quiet
    floor (the tenth percentile while the part sounds), they are turned down,
    by up to most_db; brighter moments pass untouched. The gain opens at once
    (smoothed over 5 ms, centred, so it is open by an attack) and closes over
    the release time."""
    low = sosfiltfilt(butter(4, split, "low", fs=RATE, output="sos"), audio, axis=-1)  # no phase shift
    high = audio - low
    level = np.sqrt(np.maximum(uniform_filter1d((high ** 2).mean(axis=0), int(0.01 * RATE)), 0) + 1e-20)
    sounding = level > level.max() * 10 ** (-60 / 20)
    floor = np.percentile(level[sounding], 10)
    gain = np.clip(level / (floor * 10 ** (over_db / 20)), 10 ** (-most_db / 20), 1)
    step = 1 / (release * RATE)
    n = np.arange(len(gain))
    gain = np.minimum(1, np.exp(np.maximum.accumulate(np.log(gain) + n * step) - n * step))
    return low + high * uniform_filter1d(gain, int(0.005 * RATE))


def balance(audio: np.ndarray, most_db: float = 1.0) -> tuple[np.ndarray, float]:
    rms = np.sqrt(np.mean(audio ** 2, axis=1))
    lean = 20 * np.log10(rms[0] / rms[1])
    if abs(lean) > most_db:
        audio = audio.copy()
        audio[0 if lean > 0 else 1] *= 10 ** (-(abs(lean) - most_db) / 20)
    return audio, lean


def tone(audio: np.ndarray, strength: float, most_db: float = 3.0) -> tuple[np.ndarray, np.ndarray]:
    audio = sosfiltfilt(butter(4, 40, "high", fs=RATE, output="sos"), audio, axis=-1)
    difference = TARGET - band_levels(audio)
    smooth = np.convolve(np.pad(difference, 2, mode="edge"), np.array([1, 2, 3, 2, 1]) / 9, mode="valid")
    gains = np.clip(strength * smooth, -most_db, most_db)
    cut_only = (CENTRES > 2000) | (CENTRES < 80)
    gains[cut_only] = np.minimum(gains[cut_only], 0)
    spectrum = np.fft.rfft(audio, axis=-1)
    f = np.fft.rfftfreq(audio.shape[1], 1 / RATE)
    curve = np.interp(np.log10(np.maximum(f, 1)), np.log10(CENTRES), gains)
    return np.fft.irfft(spectrum * 10 ** (curve / 20), n=audio.shape[1], axis=-1), gains


def frames_db(x: np.ndarray, hop: int) -> np.ndarray:
    n = x.shape[-1] // hop
    return 10 * np.log10(np.mean(x[..., : n * hop].reshape(-1, n, hop) ** 2, axis=(0, 2)) + 1e-20)


def air(audio: np.ndarray, strength: float) -> tuple[np.ndarray, float]:
    band = sosfiltfilt(butter(2, [2000, 6000], "band", fs=RATE, output="sos"), audio, axis=-1)
    drive = 3.0 / (np.percentile(np.abs(band), 99.5) + 1e-9)  # the band's loud peaks well into the curve
    overtones = np.tanh(band * drive) / drive - band
    overtones = sosfiltfilt(butter(4, 5000, "high", fs=RATE, output="sos"), overtones, axis=-1)
    hop = RATE // 20
    whole, made = frames_db(audio, hop), frames_db(overtones, hop)
    loud = whole >= np.percentile(whole, 90)
    gain_db = min(20.0, AIR_DB - float(np.median(made[loud] - whole[loud])))
    return audio + strength * overtones * 10 ** (gain_db / 20), gain_db


def width(audio: np.ndarray, strength: float) -> tuple[np.ndarray, float]:
    mid, side = (audio[0] + audio[1]) / 2, (audio[0] - audio[1]) / 2
    now = 10 * np.log10(np.mean(side ** 2) / (np.mean(mid ** 2) + 1e-20) + 1e-20)
    change = float(np.clip(strength * (SIDE_DB - now), -3.0, 1.5))
    side = side * 10 ** (change / 20)
    return np.stack([mid + side, mid - side]), change


def level(audio: np.ndarray, strength: float, ratio: float = 4.0, most_down: float = 8.0, most_up: float = 6.0,
          fall: float = 0.6, rise: float = 2.5) -> tuple[np.ndarray, float, float]:
    hop = RATE // 20
    weighted = sosfilt(butter(2, 100, "high", fs=RATE, output="sos"), audio.mean(axis=0))
    power = uniform_filter1d(weighted ** 2, int(1.5 * RATE))  # centred: it sees a loud bar coming
    n = len(power) // hop
    db = 10 * np.log10(power[hop // 2:: hop][:n] + 1e-20)
    tail = max(1, n - 10 * RATE // hop)
    sounding = db[:tail] > db[:tail].max() - 30
    middle = float(np.median(db[:tail][sounding]))
    gain = np.clip((middle - db) * (1 - 1 / ratio) * strength, -most_down, most_up)
    gain = np.where(gain > 0, gain * np.clip((db - (middle - 25)) / 10, 0, 1), gain)  # silences stay silent
    gain[tail:] = np.minimum(gain[tail:], gain[tail - 1])  # the ring-out is not lifted
    smoothed, g = np.empty(n), gain[0]
    down, up = np.exp(-hop / (fall * RATE)), np.exp(-hop / (rise * RATE))
    for i, target in enumerate(gain):
        a = down if target < g else up
        g = a * g + (1 - a) * target
        smoothed[i] = g
    per_sample = np.interp(np.arange(audio.shape[1]), np.arange(n) * hop + hop / 2, smoothed)
    spread = lambda x: float(np.percentile(x[:tail][sounding], 95) - np.percentile(x[:tail][sounding], 10))
    return audio * 10 ** (per_sample / 20), spread(db), spread(db + smoothed)


def master(audio: np.ndarray, tone_strength: float = 1.0, air_strength: float = 1.0, width_strength: float = 1.0,
           level_strength: float = 1.0) -> tuple[np.ndarray, str]:
    """The mastered piece (2 x samples) and a line saying what was done."""
    audio, lean = balance(audio)
    notes = [f"leaned {lean:+.1f} dB"]
    if tone_strength > 0:
        audio, gains = tone(audio, tone_strength)
        notes.append("tone " + " ".join(f"{c:g}:{g:+.1f}" for c, g in zip(CENTRES, gains) if abs(g) >= 0.5))
    if air_strength > 0:
        audio, gain_db = air(audio, air_strength)
        notes.append(f"air made {gain_db:+.0f} dB")
    if width_strength > 0:
        audio, change = width(audio, width_strength)
        notes.append(f"side {change:+.1f} dB")
    if level_strength > 0:
        audio, before, after = level(audio, level_strength)
        notes.append(f"level spread {before:.1f} -> {after:.1f} dB")
        audio = dehiss(audio, most_db=8 * level_strength)  # the quiet moments it lifted keep their hiss down
    return audio, "; ".join(notes)
