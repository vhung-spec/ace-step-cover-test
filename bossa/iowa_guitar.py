"""The University of Iowa's nylon-string guitar made into a sampler
instrument for the bossa nova sketches:

    python bossa/iowa_guitar.py libs/iowa downloads/ [summary.json]

The University of Iowa Electronic Music Studios' Musical Instrument Samples
(MIS): a Spanish classical guitar (a Raimundo 118) recorded in their
anechoic chamber in 2011, each string played as a chromatic scale at pp, mf
and ff. "Since 1997, these recordings have been freely available on this
website and may be downloaded and used for any projects, without
restrictions." (theremin.music.uiowa.edu/MIS.html). With thanks to the
University of Iowa Electronic Music Studios.

What this does, once (the result is cached by the workflow):
- reads the guitar's page and downloads its sound files (stereo AIFF if it
  offers them, else mono, else its zip);
- cuts every file into its notes: onsets where the level jumps, each note
  from its onset to just before the next, its pitch measured (pYIN), or
  counted along the file's chromatic range when the onsets and the range
  agree; resampled to 44.1 kHz, a short fade at its end;
- writes iowa_guitar.sfz: every key from E2 up played by the sample of its
  own pitch, from the string where it lies lowest on the neck (the first
  position), a sample of the same pitch on the next string down as its
  round robin; pp, mf and ff by velocity; a little random level and pitch,
  as no two plucks are the same;
- prints, and writes as JSON, what it found: the strings, their ranges,
  the notes per dynamic, the levels and the noise floor.
"""

import json
import re
import shutil
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
from scipy.ndimage import maximum_filter1d, uniform_filter1d
from scipy.signal import resample_poly

PAGE = "https://theremin.music.uiowa.edu/MISguitar.html"
AGENT = "bokin-bossa-sketches/1.0 (GitHub Actions; fetched once, then cached)"
RATE = 44100
DYNAMICS = ("pp", "mf", "ff")
VELOCITY = {"pp": (1, 50), "mf": (51, 95), "ff": (96, 127)}  # when all three are there
NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def get(url: str, dest: Path | None = None, tries: int = 4) -> bytes | None:
    for attempt in range(tries):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": AGENT})
            with urllib.request.urlopen(request, timeout=120) as response:
                data = response.read()
            if dest is not None:
                dest.write_bytes(data)
                return None
            return data
        except Exception as error:  # noqa: BLE001  a flaky network: try again
            print(f"  {url}: {error} (try {attempt + 1})", flush=True)
            time.sleep(2 ** attempt * 2)
    raise RuntimeError(f"could not fetch {url}")


def links(html: str) -> list[str]:
    found = []
    for href in re.findall(r'href\s*=\s*["\']([^"\']+)["\']', html, flags=re.IGNORECASE):
        if re.search(r"\.(aiff?|zip)$", href, flags=re.IGNORECASE):
            url = urllib.parse.urljoin(PAGE, href.strip())
            found.append(urllib.parse.quote(url, safe=":/%?=&+"))
    return list(dict.fromkeys(found))


def note_number(name: str) -> int | None:
    m = re.fullmatch(r"([A-G])(b|#)?(-?\d)", name)
    if not m:
        return None
    return 12 * (int(m.group(3)) + 1) + NAMES[m.group(1)] + {"b": -1, "#": 1, None: 0}[m.group(2)]


def describe(stem: str) -> dict:
    """Dynamic, string and range from a file name like Guitar.ff.sulA.A2Ab3.stereo."""
    dynamic = next((d for d in re.split(r"[._ ]", stem) if d in DYNAMICS), None)
    string = re.search(r"sul_?[A-G]", stem)
    span = re.search(r"\.([A-G][b#]?\d)([A-G][b#]?\d)(?:\.|$)", stem)
    lo, hi = (note_number(span.group(1)), note_number(span.group(2))) if span else (None, None)
    return {"dynamic": dynamic, "string": string.group(0) if string else None, "lo": lo, "hi": hi}


def notes_in(audio: np.ndarray, rate: int) -> list[tuple[int, int]]:
    """(start, end) samples of each note: an onset where the level (10 ms)
    jumps by 12 dB or more within 60 ms, at least 0.25 s after the last."""
    mono = np.abs(audio).max(axis=1)
    hop = max(1, rate // 200)  # 5 ms
    level = 20 * np.log10(uniform_filter1d(mono, size=rate // 100)[::hop] + 1e-9)
    peak = level.max()
    onsets, last = [], -10 ** 9
    for i in range(1, len(level) - 12):
        before = level[max(0, i - 4): i].min() if i >= 4 else level[0]
        if level[i: i + 12].max() - before >= 12 and level[i: i + 12].max() > peak - 50 and i - last > 50:
            onsets.append(i)
            last = i
    spans = []
    for k, i in enumerate(onsets):
        start = max(0, i * hop - int(0.003 * rate))
        end = onsets[k + 1] * hop - int(0.01 * rate) if k + 1 < len(onsets) else len(mono)
        spans.append((start, end))
    return spans


def pitch_of(audio: np.ndarray, rate: int) -> float | None:
    mono = audio.mean(axis=1)
    part = mono[int(0.03 * rate): int(0.6 * rate)]
    if len(part) < rate // 10:
        return None
    small = librosa.resample(part, orig_sr=rate, target_sr=22050)
    f0, voiced, _ = librosa.pyin(small, fmin=70, fmax=1300, sr=22050, frame_length=2048)
    f0 = f0[voiced]
    return float(librosa.hz_to_midi(np.median(f0))) if len(f0) >= 3 else None


def trim(audio: np.ndarray, rate: int) -> np.ndarray:
    """Ends a note where it has sunk 70 dB under its peak, or into the noise,
    with a 20 ms fade."""
    env = maximum_filter1d(np.abs(audio).max(axis=1), size=max(1, rate // 50))
    floor = np.percentile(env[-max(1, len(env) // 10):], 50)
    limit = max(env.max() * 10 ** (-70 / 20), floor * 1.5)
    loud = np.nonzero(env > limit)[0]
    end = min(len(audio), (loud[-1] if len(loud) else len(audio)) + rate // 50)
    audio = audio[:end].copy()
    fade = min(len(audio), rate // 50)
    audio[-fade:] *= np.linspace(1, 0, fade)[:, None]
    return audio


def main(dest: str, downloads: str, summary_path: str | None = None) -> int:
    final = Path(dest)
    root = final.with_name(final.name + ".partial")  # moved into place only when complete
    shutil.rmtree(root, ignore_errors=True)
    raw, samples = Path(downloads), root / "samples"
    raw.mkdir(parents=True, exist_ok=True)
    samples.mkdir(parents=True, exist_ok=True)
    html = get(PAGE).decode("latin-1")
    urls = links(html)
    stereo = [u for u in urls if "stereo" in u.lower() and re.search(r"\.aiff?$", u, re.I)]
    aiffs = [u for u in urls if re.search(r"\.aiff?$", u, re.I)]
    chosen = stereo or aiffs or [u for u in urls if u.lower().endswith(".zip")]
    print(f"iowa: {len(urls)} sound links on the page, {len(stereo)} stereo AIFF; fetching {len(chosen)}", flush=True)
    for u in urls[:12]:
        print(f"  e.g. {urllib.parse.unquote(u.rsplit('/', 1)[-1])}")
    files = []
    for url in chosen:
        name = urllib.parse.unquote(url.rsplit("/", 1)[-1])
        path = raw / name
        if not path.exists():
            get(url, path)
        if name.lower().endswith(".zip"):
            with zipfile.ZipFile(path) as z:
                for member in z.namelist():
                    if re.search(r"\.aiff?$", member, re.I) and ("stereo" in member.lower() or not stereo):
                        target = raw / Path(member).name
                        if not target.exists():
                            target.write_bytes(z.read(member))
                        files.append(target)
        else:
            files.append(path)
    if any("stereo" in f.name.lower() for f in files):
        files = [f for f in files if "stereo" in f.name.lower()]
    print(f"iowa: {len(files)} files, {sum(f.stat().st_size for f in files) / 1e6:.0f} MB", flush=True)

    found = []  # (dynamic, string, midi, path, peak dB, floor dB, seconds)
    for path in sorted(files):
        info = describe(path.stem)
        if not info["dynamic"] or not info["string"]:
            print(f"  {path.name}: no dynamic or string in its name, left out")
            continue
        audio, rate = sf.read(path, always_2d=True, dtype="float32")
        spans = notes_in(audio, rate)
        expected = list(range(info["lo"], info["hi"] + 1)) if info["lo"] is not None and info["hi"] else None
        counted = expected is not None and len(expected) == len(spans)
        agree = 0
        for k, (start, end) in enumerate(spans):
            note = audio[start:end]
            measured = pitch_of(note, rate)
            if counted:
                midi = expected[k]
                agree += measured is not None and abs(measured - midi) < 0.5
            elif measured is not None and abs(measured - round(measured)) < 0.35:
                midi = int(round(measured))
            else:
                continue
            note = trim(note, rate)
            if rate != RATE:
                g = np.gcd(RATE, rate)
                note = resample_poly(note, RATE // g, rate // g, axis=0).astype("float32")
            out = samples / f"{info['dynamic']}_{info['string']}_{midi}.wav"
            peak = 20 * np.log10(np.abs(note).max() + 1e-12)
            tail = np.abs(note[-RATE // 5:]).max(axis=1) if len(note) > RATE // 5 else np.abs(note).max(axis=1)
            if out.exists() and sf.info(out).duration >= len(note) / RATE:
                continue  # a longer take of the same note is kept
            sf.write(out, note, RATE, subtype="PCM_24")
            found.append((info["dynamic"], info["string"], midi, out.name, float(peak),
                          float(20 * np.log10(np.median(tail) + 1e-12)), len(note) / RATE))
        how = f"counted along {expected[0]}-{expected[-1]}, pYIN agrees on {agree}" if counted else "by pYIN"
        print(f"  {path.name}: {rate} Hz, {audio.shape[1]} ch, {len(spans)} notes ({how})", flush=True)

    if not found:
        raise RuntimeError("no notes found")
    # keep the latest take of each (dynamic, string, midi): the files above may repeat a note
    table = {}
    for row in found:
        table[row[:3]] = row
    rows = sorted(table.values())
    # strings from lowest to highest by their lowest note: 6 (low E) ... 1 (high E)
    strings = sorted({r[1] for r in rows}, key=lambda s: min(r[2] for r in rows if r[1] == s))
    open_note = {s: min(r[2] for r in rows if r[1] == s) for s in strings}
    dynamics = [d for d in DYNAMICS if any(r[0] == d for r in rows)]
    if len(dynamics) == 3:
        ranges = VELOCITY
    else:
        ranges = {d: (1 + 127 * i // len(dynamics), 127 * (i + 1) // len(dynamics)) for i, d in enumerate(dynamics)}
    lines = ["// The University of Iowa MIS nylon-string guitar (Raimundo 118, 2011), free to use without",
             "// restrictions; mapped for the Bokin bossa nova sketches by bossa/iowa_guitar.py",
             "<control>", "default_path=samples/",
             "<global>", "ampeg_release=0.3", "amp_veltrack=45", "amp_random=1", "pitch_random=3"]
    low = min(open_note.values())
    high = max(r[2] for r in rows)
    mapped = 0
    for key in range(low, high + 1):
        for dynamic in dynamics:
            lovel, hivel = ranges[dynamic]
            here = [r for r in rows if r[0] == dynamic]
            # the nearest pitch sampled (the key's own, else within two half steps)
            pitches = sorted({r[2] for r in here}, key=lambda p: (abs(p - key), p))
            if not pitches or abs(pitches[0] - key) > 2:
                continue
            pitch = pitches[0]
            takes = sorted((r for r in here if r[2] == pitch), key=lambda r: pitch - open_note[r[1]])
            takes = [r for r in takes if pitch - open_note[r[1]] >= 0][:2]
            if not takes:
                continue
            shares = [(0.0, 1.0)] if len(takes) == 1 else [(0.0, 0.65), (0.65, 1.0)]
            for row, (lo_r, hi_r) in zip(takes, shares):
                lines.append(f"<region> sample={row[3]} key={key} pitch_keycenter={pitch} lovel={lovel} hivel={hivel} "
                             f"lorand={lo_r:.2f} hirand={hi_r:.2f}")
            mapped += 1
    (root / "iowa_guitar.sfz").write_text("\n".join(lines) + "\n")
    summary = {
        "strings": {s: {"open": open_note[s], "highest": max(r[2] for r in rows if r[1] == s),
                        "notes": {d: sum(1 for r in rows if r[1] == s and r[0] == d) for d in dynamics}}
                    for s in strings},
        "dynamics": {d: {"notes": sum(1 for r in rows if r[0] == d),
                         "median_peak_db": round(float(np.median([r[4] for r in rows if r[0] == d])), 1),
                         "median_tail_db": round(float(np.median([r[5] for r in rows if r[0] == d])), 1),
                         "median_seconds": round(float(np.median([r[6] for r in rows if r[0] == d])), 2)}
                     for d in dynamics},
        "keys": [low, high], "regions_mapped": mapped, "samples": len(rows),
    }
    print("iowa: " + json.dumps(summary), flush=True)
    if summary_path:
        Path(summary_path).write_text(json.dumps(summary, indent=1))
    shutil.rmtree(final, ignore_errors=True)
    root.rename(final)
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
