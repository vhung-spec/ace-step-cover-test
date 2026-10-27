"""Fetches, at pinned commits, only the instruments that arrange.py's parts use
from the two CC0 sample libraries, and makes their SFZ files readable on Linux
(forward slashes in the sample paths):

    python fetch_samples.py out/sampled libs

libs/vsco is VS Chamber Orchestra 2 Community Edition (SFZ branch), libs/vcsl
the Versilian Community Sample Library (sfz branch), both by Versilian Studios.
"""

import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

LIBRARIES = {
    "vsco": ("https://github.com/sgossner/VSCO-2-CE", "6dd651d55dde97fd4028699be9d4481f26917891"),
    "vcsl": ("https://github.com/sgossner/VCSL", "dfcf4a4918771eee884b96ad4493de82ef84daf6"),
}


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
        for entry in json.loads(sheet.read_text()):
            needed.setdefault(entry["library"], set()).add(entry["sfz"])
    for name, sfz_files in sorted(needed.items()):
        url, commit = LIBRARIES[name]
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
        folders = set()
        for sfz in sfz_files:
            folders |= sample_folders(dest / sfz, dest)
        with patterns.open("a") as f:  # then the samples they play
            f.writelines(f"/{folder}/\n" for folder in sorted(folders))
        git(dest, "sparse-checkout", "reapply")
        for sfz in sfz_files:  # Windows paths in the SFZ files
            path = dest / sfz
            path.write_text(path.read_text(errors="replace").replace("\\", "/"))
        wavs = list(dest.rglob("*.wav"))
        pointers = [w for w in wavs if w.stat().st_size < 200 and w.read_bytes().startswith(b"version https://git-lfs")]
        if pointers:
            git(dest, "lfs", "install", "--local")
            git(dest, "lfs", "pull")
        size = sum(w.stat().st_size for w in dest.rglob("*.wav"))
        print(f"{name}: {len(sfz_files)} instruments, {len(folders)} sample folders, "
              f"{len(wavs)} samples, {size / 1e6:.0f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
