"""Fetches, at pinned commits, only the instruments that arrange.py's parts use
from the two CC0 sample libraries, and makes their SFZ files readable on Linux
(forward slashes in the sample paths):

    python fetch_samples.py out/sampled libs

libs/vsco is VS Chamber Orchestra 2 Community Edition (SFZ branch), libs/vcsl
the Versilian Community Sample Library (sfz branch), both by Versilian Studios
(CC0); libs/salamander the Salamander Grand Piano V3 by Alexander Holm (CC-BY
3.0, SFZ by kinwie).
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path, PurePosixPath

import numpy as np
import soundfile as sf
from scipy.ndimage import uniform_filter1d
from scipy.signal import butter, sosfiltfilt

# Library: (repository, commit, folders always fetched: for SFZ files that
# #include their regions, whose sample paths this script does not follow).
LIBRARIES = {
    "vsco": ("https://github.com/sgossner/VSCO-2-CE", "6dd651d55dde97fd4028699be9d4481f26917891", ()),
    "vcsl": ("https://github.com/sgossner/VCSL", "dfcf4a4918771eee884b96ad4493de82ef84daf6", ()),
    "salamander": ("https://github.com/sfzinstruments/SalamanderGrandPiano",
                   "3382bf9496bba2486f5ab0de55a264d1dfc38404", ("Data", "Samples")),
}


# Instruments some of whose samples were recorded with one microphone's
# polarity inverted, so their two channels run opposite (summed, they cancel):
# the right channel of such a sample is turned over.
FLIP_POLARITY = {"Chordophones/Zithers/Upright Piano, Yamaha.sfz"}


def flip_polarity(root: Path, folders: set) -> int:
    flipped = 0
    for folder in folders:
        for wav in sorted((root / folder).glob("*.wav")):
            audio, rate = sf.read(wav, always_2d=True)
            if audio.shape[1] == 2 and np.corrcoef(audio[: 2 * rate, 0], audio[: 2 * rate, 1])[0, 1] < 0:
                audio[:, 1] *= -1
                sf.write(wav, audio, rate, subtype=sf.info(wav).subtype)
                flipped += 1
    return flipped


# Instruments whose samples carry a steady hiss above 4 kHz: the Steinway's
# soft notes rise only 16-26 dB over it there, and with the pedal down a dozen
# of them ring at once, a rustle. Each sample's highs are faded out once its
# note has died into the hiss (clean_hiss).
CLEAN_HISS = {"Chordophones/Zithers/Grand Piano, Steinway B.sfz"}
HISS_BANDS = (4000, 6000, 9000, 13500)  # Hz: the highs are cleaned band by band


def clean_hiss(audio: np.ndarray, rate: int, near_db: float = 6.0, fade: float = 50.0, most_db: float = 50.0,
               snr_db: float = 10.0) -> np.ndarray:
    """A sample (samples x channels) with its hiss hushed. Its highs are split
    into bands, each the difference of two zero-phase low-passes, so the bands
    add up to the sample exactly. In each, from the moment after the hammer's
    strike that the band's level (50 ms, both channels) has sunk to within
    near_db of its hiss floor (its median level over 40-75 % of the sample,
    long after the note's highs have gone), it fades by `fade` dB a second down
    to most_db under; a band whose strike (10 ms) is not even snr_db over the
    floor, the top of a soft note, holds nothing but hiss and is left out. The
    attack and the ring of the note are untouched (in a dozen pedalled notes,
    the hiss of their ring-out 22-45 dB lower above 6 kHz)."""
    lows = [sosfiltfilt(butter(6, edge, "low", fs=rate, output="sos"), audio, axis=0) for edge in HISS_BANDS]
    bands = [b - a for a, b in zip(lows, lows[1:] + [audio])]
    out, n = lows[0].copy(), len(audio)
    whole = uniform_filter1d((audio ** 2).mean(axis=1), max(1, int(0.01 * rate)))
    strike = int(np.argmax(whole)) + int(0.05 * rate)
    for band in bands:
        power = (band ** 2).mean(axis=1)
        level = uniform_filter1d(power, max(1, int(0.05 * rate)))
        stable = level[int(0.4 * n): int(0.75 * n)]
        floor = float(np.median(stable)) if len(stable) else 0.0
        if floor <= 0:
            out += band
            continue
        if uniform_filter1d(power, max(1, int(0.01 * rate))).max() < floor * 10 ** (snr_db / 10):
            gain = np.full(n, 10 ** (-most_db / 20))
        else:
            near = np.nonzero(level[strike:] <= floor * 10 ** (near_db / 10))[0]
            start = strike + int(near[0]) if len(near) else n
            gain = 10 ** (-np.minimum(np.maximum(np.arange(n) - start, 0) / rate * fade, most_db) / 20)
        out += band * gain[:, None]
    return out


def clean_folders(root: Path, folders: set) -> int:
    cleaned = 0
    for folder in folders:
        for wav in sorted((root / folder).glob("*.wav")):
            audio, rate = sf.read(wav, always_2d=True)
            sf.write(wav, clean_hiss(audio, rate), rate, subtype=sf.info(wav).subtype)
            cleaned += 1
    return cleaned


def git(dest: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(dest), *args], check=True)


def sample_folders(sfz: Path, root: Path) -> set:
    """The folders (relative to the library) that an SFZ file's samples are in."""
    text = sfz.read_text(errors="replace").replace("\\", "/")
    default = re.search(r"default_path=([^\n]*)", text)
    base = PurePosixPath(sfz.parent.relative_to(root).as_posix()) / (default.group(1).strip() if default else "")
    folders = set()
    for sample in re.findall(r"sample=([^\n]+?\.(?:wav|flac|ogg))", text, flags=re.IGNORECASE):
        folders.add(str((base / sample.strip()).parent))
    return folders


def main(out: str, libs: str) -> int:
    needed = {}
    for sheet in Path(out).glob("*/mix.json"):
        for entry in json.loads(sheet.read_text())["parts"]:
            needed.setdefault(entry["library"], set()).add(entry["sfz"])
    for name, sfz_files in sorted(needed.items()):
        if name not in LIBRARIES:  # "local": our own instruments, in instruments/
            continue
        url, commit, always = LIBRARIES[name]
        dest = Path(libs) / name
        dest.mkdir(parents=True, exist_ok=True)
        git(dest, "init", "-q")
        git(dest, "remote", "add", "origin", url)
        git(dest, "config", "core.sparseCheckout", "true")
        patterns = dest / ".git" / "info" / "sparse-checkout"  # first the SFZ files only
        patterns.parent.mkdir(parents=True, exist_ok=True)
        patterns.write_text("".join(f"/{f}\n" for f in sorted(sfz_files)))
        git(dest, "fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", commit)
        git(dest, "checkout", "-q", "FETCH_HEAD")
        folders = set(always)
        for sfz in sfz_files:
            folders |= sample_folders(dest / sfz, dest)
        with patterns.open("a") as f:  # then the samples they play
            f.writelines(f"/{folder}/\n" for folder in sorted(folders))
        git(dest, "sparse-checkout", "reapply")
        for sfz in sfz_files:  # Windows paths in the SFZ files
            path = dest / sfz
            path.write_text(path.read_text(errors="replace").replace("\\", "/"))
        wavs = list(dest.rglob("*.wav")) + list(dest.rglob("*.flac"))
        pointers = [w for w in wavs if w.stat().st_size < 200 and w.read_bytes().startswith(b"version https://git-lfs")]
        if pointers:
            git(dest, "lfs", "install", "--local")
            git(dest, "lfs", "pull")
        for sfz in sorted(sfz_files & FLIP_POLARITY):
            print(f"{sfz}: {flip_polarity(dest, sample_folders(dest / sfz, dest))} samples' right channel "
                  f"turned over (it ran opposite the left)")
        for sfz in sorted(sfz_files & CLEAN_HISS):
            started = time.time()
            print(f"{sfz}: {clean_folders(dest, sample_folders(dest / sfz, dest))} samples' hiss hushed "
                  f"({time.time() - started:.0f} s)", flush=True)
        size = sum(w.stat().st_size for w in wavs)
        print(f"{name}: {len(sfz_files)} instruments, {len(folders)} sample folders, "
              f"{len(wavs)} samples, {size / 1e6:.0f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
