"""Fetches, at pinned commits, the bossa nova sketches' own instruments (the
others, VCSL, VSCO-2-CE and jRhodes3d, come from ../fetch_samples.py), and
writes the SFZ files the arranger plays them by:

    python bossa/fetch_bossa.py out/bossa libs

- freepats: FreePats' Spanish Classical Guitar (nylon strings, recorded 2008
  by roberto@zenvoid.org), CC0. One velocity layer, so the arranger's
  SpanishClassicalGuitar-bossa.sfz darkens soft notes (a low-pass following
  velocity) and damps released notes sooner (a plucked chord in the batida
  is muted by the hand);
- smolken: D. Smolken's Double Bass (a 1958 Otto Rubner, pizzicato), CC0,
  through Karoryfer Samples;
- swirly: Karoryfer's Swirly Drums, a kit played with brushes, CC0. Only the
  sounds the sketches use are fetched (brush stirs, snare taps and rim, the
  hi-hat's foot, the cajon kick), and bossa_brushes.sfz maps them: velocity
  layers by velocity, round robins at random.

No sample is ever kept in the repository: they are fetched here, at build
time, from the libraries' own repositories.
"""

import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

LIBRARIES = {
    "freepats": ("https://github.com/freepats/spanish-classical-guitar", "6f4eb1b092acc88f5448cea1a0001bd07b971af8"),
    "smolken": ("https://github.com/sfzinstruments/dsmolken.double-bass", "c2985eb647109d2a8f30a70071e3e163339d7396"),
    "swirly": ("https://github.com/sfzinstruments/karoryfer.swirly-drums", "c40dafe0011cb2e54c0c220ff0fa308a11fc60f5"),
}
GUITAR = "SpanishClassicalGuitar-20190618.sfz"
# The brush kit: key -> (sample folder, file pattern, opcodes)
KIT = {
    36: ("cajon_kick", r"cajon_kick_vl(\d+)_rr(\d+)_front\.wav", "loop_mode=one_shot"),
    37: ("snare_edge", r"snare_edge_vl(\d+)_rr(\d+)_top\.wav", "loop_mode=one_shot"),
    38: ("snare_main", r"snare_hit_vl(\d+)_rr(\d+)_top\.wav", "loop_mode=one_shot"),
    42: ("hat_closed", r"hh_closed_vl(\d+)_rr(\d+)\.wav", "loop_mode=one_shot"),
    44: ("hat_foot", r"hh_foot_vl(\d+)_rr(\d+)\.wav", "loop_mode=one_shot"),
    47: ("snare_stir", r"stir_dl4_rr(\d+)\.wav", "ampeg_release=0.3"),
    48: ("snare_stir", r"stir_dl3_rr(\d+)\.wav", "ampeg_release=0.3"),
}


def git(dest: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(dest), *args], check=True)


def fetch(name: str, root: Path, patterns: list) -> Path:
    url, commit = LIBRARIES[name]
    dest = root / name
    dest.mkdir(parents=True, exist_ok=True)
    git(dest, "init", "-q")
    git(dest, "remote", "add", "origin", url)
    git(dest, "config", "core.sparseCheckout", "true")
    (dest / ".git" / "info").mkdir(parents=True, exist_ok=True)
    (dest / ".git" / "info" / "sparse-checkout").write_text("".join(f"{p}\n" for p in patterns))
    git(dest, "fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", commit)
    git(dest, "checkout", "-q", "FETCH_HEAD")
    return dest


def guitar(root: Path) -> None:
    dest = fetch("freepats", root, ["/*"])
    text = (dest / GUITAR).read_text()
    # every region: released notes die in 0.35 s; soft notes darker (no velocity layers of its own)
    text = text.replace("<region>", "<region>\n ampeg_release=0.35 fil_type=lpf_2p cutoff=1500 fil_veltrack=4200")
    (dest / "SpanishClassicalGuitar-bossa.sfz").write_text(text)
    print(f"freepats: {len(list((dest / 'samples').glob('*.flac')))} guitar samples")


def bass(root: Path) -> None:
    dest = fetch("smolken", root, ["/*.sfz", "/LICENSE", "/readme.txt"])
    sfz = dest / "d_smolken_rubner_bass_pizz.sfz"
    text = sfz.read_text(errors="replace").replace("\\", "/")  # Windows paths
    folders = {str(PurePosixPath(s.strip()).parent) for s in re.findall(r"sample=([^\n]+?\.wav)", text)}
    with (dest / ".git" / "info" / "sparse-checkout").open("a") as f:
        f.writelines(f"/{folder}/\n" for folder in sorted(folders))
    git(dest, "sparse-checkout", "reapply")
    sfz.write_text(text)
    print(f"smolken: {len(list(dest.rglob('*.wav')))} bass samples")


def drums(root: Path) -> None:
    folders = sorted({folder for folder, _, _ in KIT.values()})
    dest = fetch("swirly", root, ["/license"] + [f"/Samples/{f}/" for f in folders])
    lines = ["// The brush kit for the bossa nova sketches, from Karoryfer's Swirly Drums (CC0)"]
    for key, (folder, pattern, opcodes) in KIT.items():
        found = []
        for wav in sorted((dest / "Samples" / folder).glob("*.wav")):
            m = re.fullmatch(pattern, wav.name)
            if m:
                layer, rr = (int(m.group(1)), int(m.group(2))) if m.lastindex == 2 else (1, int(m.group(1)))
                found.append((layer, rr, wav.relative_to(dest).as_posix()))
        layers = sorted({layer for layer, _, _ in found})
        lines.append(f"<group> key={key} pitch_keycenter={key} {opcodes} amp_veltrack=70")
        for i, layer in enumerate(layers):
            lovel, hivel = 1 + 127 * i // len(layers), 127 * (i + 1) // len(layers)
            takes = [s for lay, _, s in found if lay == layer]
            for j, sample in enumerate(takes):
                lines.append(f"<region> sample={sample} lovel={lovel} hivel={hivel} "
                             f"lorand={j / len(takes):.4f} hirand={(j + 1) / len(takes):.4f}")
        print(f"swirly: key {key} {folder}: {len(layers)} layers, {len(found)} samples")
    (dest / "bossa_brushes.sfz").write_text("\n".join(lines) + "\n")


def main(out: str, libs: str) -> int:
    needed = {entry["library"] for sheet in Path(out).glob("*/mix.json")
              for entry in json.loads(sheet.read_text())["parts"]}
    root = Path(libs)
    for name, step in (("freepats", guitar), ("smolken", bass), ("swirly", drums)):
        if name in needed:
            step(root)
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
