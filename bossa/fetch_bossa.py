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
  layers by velocity, round robins at random;
- meatbass: Karoryfer's Meatbass (the same 1958 Otto Rubner double bass,
  recorded anew), CC0: its pizzicato, four velocity layers and four round
  robins a note, mapped by bossa_meatbass_pizz.sfz;
- rusty: Karoryfer's Big Rusty Drums, CC0: a full kit sampled with sticks,
  brushes and mallets. bossa_rusty_kit.sfz plays the bossa nova kit from it,
  each sound from its close microphone with the overheads under it: the
  cross-stick (side stick: the "tall" one, woody, and the plain one,
  brighter), the hi-hat closed tight (stick, or brush), its foot, the kick,
  the brush on the snare and its stir, the ride with a brush;
- virtuosity: Versilian Studios' Virtuosity Drums, CC0: a pop kit played
  with sticks and its Latin percussion, recorded by eight microphones.
  bolero_kit.sfz is its full kit (every technique: the cross-stick, rolls,
  muted and open hi-hats) from the three microphones it plays by default
  (the kick's, the snare's, the overheads), the percussion (congas,
  bongos, shakers, guiro, claves) close and from the overheads; the other
  microphones' samples are not fetched;
- shiny: Karoryfer's Shinyguitar, an archtop (steel strings) recorded by a
  microphone and its pickup, CC0. bossa_shiny_acoustic.sfz is its own
  main.sfz with the microphone alone (the blend at 127, one voice), its
  notes (four layers, four round robins) and its noises (the strings
  muted, a chuck, on 18-21); only the microphone's samples are fetched.

The guitar of the University of Iowa (MIS) comes from iowa_guitar.py.

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
    "meatbass": ("https://github.com/sfzinstruments/karoryfer.meatbass", "ac9e859564bda286ab5ec672d00ff1aa2fef2895"),
    "rusty": ("https://github.com/sfzinstruments/karoryfer.big-rusty-drums", "f07ce00df34a46b6b08375be56fe116cf15782bc"),
    "emily": ("https://github.com/sfzinstruments/karoryfer.emilyguitar", "b4920dc662fd9cad6dcaccdeecffdd91c8725d8c"),
    "fashionbass": ("https://github.com/sfzinstruments/karoryfer.fashionbass", "0703973b300a6bacb837602be9b588ab64732a72"),
    "virtuosity": ("https://github.com/sfzinstruments/virtuosity_drums", "9f04cf9a734527edfbb0a4eee1f674e45bbf71bc"),
    "shiny": ("https://github.com/sfzinstruments/karoryfer.shinyguitar", "57243cca85277dbcc120ce17c6178032f93c80f3"),
}
# Libraries played straight from one of their own SFZ files: (the file, the
# folders it plays from are found in it)
MAPPED = {"emily": "emily_clean.sfz", "fashionbass": "fashionbass_clean.sfz"}
# Each one's tuning put right (cents, every region): Fashionbass rang 12
# cents sharp in the first rumba sketches (YIN on 144 notes, quartiles +9 and
# +16); Emilyguitar +4, left as it is
MAPPED_TUNE = {"fashionbass": -12}
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


NOTE_CLASSES = {"c": 0, "db": 1, "d": 2, "eb": 3, "e": 4, "f": 5, "gb": 6, "g": 7, "ab": 8, "a": 9, "bb": 10, "b": 11}


def meatbass(root: Path) -> None:
    """Meatbass's pizzicato: a sample every minor third (A0 to A3, named by
    their sounding pitch: a1 is MIDI 33), each covering the half steps either
    side; four velocity layers, four round robins at random."""
    dest = fetch("meatbass", root, ["/LICENSE", "/readme.txt", "/Samples/pizz/"])
    lines = ["// Meatbass pizzicato (Karoryfer Samples, CC0) for the bossa nova sketches",
             "<global> ampeg_release=0.22 amp_veltrack=55"]
    takes = {}
    for wav in sorted((dest / "Samples" / "pizz").glob("*.wav")):
        m = re.fullmatch(r"([a-g]b?)(\d)_vl(\d)_rr(\d)\.wav", wav.name)
        if m and m.group(1) + m.group(2) != "c4":  # c4 sounds an octave low (pYIN): left out
            key = 12 * (int(m.group(2)) + 1) + NOTE_CLASSES[m.group(1)]
            takes.setdefault((key, int(m.group(3))), []).append(wav.relative_to(dest).as_posix())
    layers = sorted({layer for _, layer in takes})
    for (key, layer), samples in sorted(takes.items()):
        i = layers.index(layer)
        lovel, hivel = 1 + 127 * i // len(layers), 127 * (i + 1) // len(layers)
        lines.append(f"<group> lokey={key - 1} hikey={key + 1} pitch_keycenter={key} lovel={lovel} hivel={hivel}")
        for j, sample in enumerate(sorted(samples)):
            lines.append(f"<region> sample={sample} lorand={j / len(samples):.4f} hirand={(j + 1) / len(samples):.4f}")
    (dest / "bossa_meatbass_pizz.sfz").write_text("\n".join(lines) + "\n")
    keys = sorted({k for k, _ in takes})
    print(f"meatbass: {len(keys)} pitches ({keys[0]}-{keys[-1]}), {len(layers)} layers, "
          f"{sum(len(v) for v in takes.values())} samples")


# The bossa kit from Big Rusty Drums: key -> sounds layered, each (folder, file
# pattern with its velocity layer and round robin, volume dB), and opcodes.
RUSTY = {
    36: ([("kick_24/kick/kick", r"k_vl(\d+)_rr(\d+)\.flac", 0), ("kick_24/kick/oh", r"k_vl(\d+)_rr(\d+)\.flac", -4)],
         "loop_mode=one_shot"),
    37: ([("snare_14/tsidestick/top", r"sn_tall_ss_vl(\d+)_rr(\d+)\.flac", 0),
          ("snare_14/tsidestick/oh", r"sn_tall_ss_vl(\d+)_rr(\d+)\.flac", -4)], "loop_mode=one_shot"),
    39: ([("snare_14/sidestick/top", r"sn_ss_vl(\d+)_rr(\d+)\.flac", 0),
          ("snare_14/sidestick/oh", r"sn_ss_vl(\d+)_rr(\d+)\.flac", -4)], "loop_mode=one_shot"),
    38: ([("snare_14/brush/top", r"sn_b_vl(\d+)_rr(\d+)\.flac", 0),
          ("snare_14/brush/oh", r"sn_b_vl(\d+)_rr(\d+)\.flac", -4)], "loop_mode=one_shot"),
    42: ([("hihat_14/tc/cl", r"ht_tc_vl(\d+)_rr(\d+)\.flac", 0), ("hihat_14/tc/oh", r"ht_tc_vl(\d+)_rr(\d+)\.flac", -4)],
         "loop_mode=one_shot"),
    44: ([("hihat_14/chik/cl", r"ht_chik_vl(\d+)_rr(\d+)\.flac", 0)], "loop_mode=one_shot"),
    46: ([("hihat_14/tc_brush/cl", r"ht_tc_b_vl(\d+)_rr(\d+)\.flac", 0),
          ("hihat_14/tc_brush/oh", r"ht_tc_b_vl(\d+)_rr(\d+)\.flac", -4)], "loop_mode=one_shot"),
    47: ([("snare_14/bstir/top", r"sn_stir_dl2_rr(\d+)\.wav", 0), ("snare_14/bstir/oh", r"sn_stir_dl2_rr(\d+)\.wav", -4)],
         "ampeg_release=0.3"),
    51: ([("ride_22/brush/cl", r"rd_b_vl(\d+)_rr(\d+)\.flac", 0), ("ride_22/brush/oh", r"rd_b_vl(\d+)_rr(\d+)\.flac", -4)],
         "loop_mode=one_shot"),
}


def rusty(root: Path) -> None:
    folders = sorted({folder for sounds, _ in RUSTY.values() for folder, _, _ in sounds})
    dest = fetch("rusty", root, ["/LICENSE"] + [f"/Samples/{f}/" for f in folders])
    lines = ["// The bossa nova kit from Karoryfer's Big Rusty Drums (CC0)"]
    for key, (sounds, opcodes) in RUSTY.items():
        for folder, pattern, volume in sounds:
            found = []
            for path in sorted((dest / "Samples" / folder).iterdir()):
                m = re.fullmatch(pattern, path.name)
                if m:
                    layer, rr = (int(m.group(1)), int(m.group(2))) if m.lastindex == 2 else (1, int(m.group(1)))
                    found.append((layer, rr, path.relative_to(dest).as_posix()))
            if not found:
                print(f"rusty: key {key}: nothing in {folder}")
                continue
            layers = sorted({layer for layer, _, _ in found})
            lines.append(f"<group> key={key} pitch_keycenter={key} volume={volume} {opcodes} amp_veltrack=75")
            for i, layer in enumerate(layers):
                lovel, hivel = 1 + 127 * i // len(layers), 127 * (i + 1) // len(layers)
                same = sorted((rr, s) for lay, rr, s in found if lay == layer)
                for j, (_, sample) in enumerate(same):
                    lines.append(f"<region> sample={sample} lovel={lovel} hivel={hivel} "
                                 f"lorand={j / len(same):.4f} hirand={(j + 1) / len(same):.4f}")
            print(f"rusty: key {key} {folder}: {len(layers)} layers, {len(found)} samples")
    (dest / "bossa_rusty_kit.sfz").write_text("\n".join(lines) + "\n")


def mapped(name: str, root: Path) -> None:
    """A Karoryfer library played by its own SFZ file (MAPPED): Emilyguitar
    (an Epiphone electric, four velocity layers, three round robins, CC0),
    Fashionbass (a jazz bass, five layers, three round robins, CC0); their
    Windows sample paths turned to forward slashes, only the folders the
    file plays fetched."""
    sfz_name = MAPPED[name]
    dest = fetch(name, root, ["/*.sfz", "/LICENSE", "/readme.txt"])
    sfz = dest / sfz_name
    text = sfz.read_text(errors="replace").replace("\\", "/")
    if name in MAPPED_TUNE:
        if "tune=" in text:
            raise RuntimeError(f"{name}: {sfz_name} tunes some regions itself")
        text = text.replace("<region>", f"<region> tune={MAPPED_TUNE[name]}")
    folders = {str(PurePosixPath(s.strip()).parent) for s in re.findall(r"sample=([^\n]+?\.(?:wav|flac))", text)}
    with (dest / ".git" / "info" / "sparse-checkout").open("a") as f:
        f.writelines(f"/{folder}/\n" for folder in sorted(folders))
    git(dest, "sparse-checkout", "reapply")
    sfz.write_text(text)
    print(f"{name}: {sfz_name}, {len(list(dest.rglob('*.wav')))} samples")


# Virtuosity Drums' microphones the bolero kit plays: those its full kit
# plays by default (the mid, room and vintage ones start at zero)
VIRTUOSITY_MICS = ("kickmic", "snaremic", "oh")


def virtuosity(root: Path) -> None:
    """bolero_kit.sfz: Virtuosity Drums' 02-full-kit.sfz with only the
    sections of VIRTUOSITY_MICS (each microphone opens a <global> of its
    own) and the percussion heard by them, on the General MIDI keys of its
    keymaps/default (the hi-hat closed on 42, open on 46): the keymap.sfz
    the kit includes is its e-drum one, every hi-hat on 42 opened as far as
    the pedal's CC 4 says, and CC 4 starts at 0, wide open (the first
    render's closed hi-hats all rang open)."""
    dest = fetch("virtuosity", root, ["/LICENSE", "/Programs/"] + [f"/Samples/{m}/" for m in VIRTUOSITY_MICS]
                 + ["/Samples/perc/close/", "/Samples/perc/oh/"])
    programs = dest / "Programs"
    head, *sections = re.split(r"(?=<global>)", (programs / "02-full-kit.sfz").read_text())
    if '#include "keymaps/keymap.sfz"' not in head or not (programs / "keymaps/default/keymap.sfz").is_file():
        raise RuntimeError("virtuosity: 02-full-kit.sfz no longer includes keymaps/keymap.sfz")
    head = head.replace('#include "keymaps/keymap.sfz"', '#include "keymaps/default/keymap.sfz"')
    kept = [s for s in sections if re.search(r'#include "mappings/(?:' + "|".join(VIRTUOSITY_MICS) + r')_all\.sfz"', s)]
    if len(kept) != len(VIRTUOSITY_MICS):
        raise RuntimeError(f"virtuosity: {len(kept)} of the microphones' sections found in 02-full-kit.sfz")
    kept = [re.sub(r'#include "mappings/mutecurves\.sfz"\s*', "", s) for s in kept]
    text = ("// The bolero kit: Virtuosity Drums' full kit (Versilian Studios, CC0) from its kick, snare and\n"
            "// overhead microphones; written by bossa/fetch_bossa.py\n" + head + "".join(kept)
            + '#include "mappings/mutecurves.sfz"\n')
    (programs / "bolero_kit.sfz").write_text(text)
    samples = sum(1 for f in (dest / "Samples").rglob("*") if f.suffix in (".wav", ".flac"))
    print(f"virtuosity: bolero_kit.sfz, {len(kept)} microphones, {samples} samples")


def shiny(root: Path) -> None:
    """bossa_shiny_acoustic.sfz: Shinyguitar's main.sfz (its controls, its
    envelope and tone filter) playing the microphone alone, one voice: its
    sample folder set (main.sfz leaves $sample_dir to the player that loads
    its bank), its blend at 127 (all microphone), only acoustic_one.sfz (the
    notes) and acoustic_noises.sfz (the muted strings and the body's knocks)
    included, their Windows paths turned to forward slashes."""
    dest = fetch("shiny", root, ["/LICENSE", "/readme.txt", "/Programs/", "/Samples/acoustic/"])
    programs = dest / "Programs"
    for name in ("acoustic_one.sfz", "acoustic_noises.sfz"):
        path = programs / name
        path.write_text(path.read_text(errors="replace").replace("\\", "/"))
    text = (programs / "main.sfz").read_text(errors="replace")
    for old, new in (("default_path=$sample_dir/", "default_path=../Samples/"), ("set_cc100=0", "set_cc100=127")):
        if old not in text:
            raise RuntimeError(f"shiny: main.sfz has no {old!r}")
        text = text.replace(old, new)
    keep = ('#include "acoustic_one.sfz"', '#include "acoustic_noises.sfz"')
    text = "\n".join(line for line in text.splitlines() if not line.startswith("#include") or line.strip() in keep)
    (programs / "bossa_shiny_acoustic.sfz").write_text("// Shinyguitar's microphone alone; written by bossa/fetch_bossa.py\n"
                                                        + text + "\n")
    print(f"shiny: bossa_shiny_acoustic.sfz, {len(list((dest / 'Samples' / 'acoustic').glob('*.wav')))} samples")


def main(out: str, libs: str) -> int:
    needed = set()
    for sheet in Path(out).glob("*/mix.json"):
        for entry in json.loads(sheet.read_text())["parts"]:
            needed |= {entry["library"], entry.get("fallback", {}).get("library")}
    root = Path(libs)
    steps = [("freepats", guitar), ("smolken", bass), ("swirly", drums), ("meatbass", meatbass), ("rusty", rusty)]
    steps += [(name, lambda r, n=name: mapped(n, r)) for name in MAPPED] + [("virtuosity", virtuosity), ("shiny", shiny)]
    for name, step in steps:
        if name in needed:
            step(root)
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
