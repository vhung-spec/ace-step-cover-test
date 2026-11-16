"""Plays and mixes the bossa nova sketches with ../render_samples.py (sfizz,
each part's tone and level, the room, loudness), from the libraries
../fetch_samples.py and fetch_bossa.py put in one folder:

    python bossa/render_bossa.py out/bossa --sfizz path/to/sfizz_render --libs libs
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import render_samples  # noqa: E402

_sfz_copy = render_samples.sfz_copy


def sfz_copy(sfz: Path, part: str, db: float, tone: dict) -> Path:
    """render_samples.sfz_copy, the part's level set in every <global> of
    the file, not only its first: Virtuosity Drums opens one a microphone,
    and each <global> starts afresh (the level set in the first would move
    the kick's microphone alone)."""
    copy = _sfz_copy(sfz, part, db, tone)
    text = copy.read_text()
    line = f"global_volume={db:g}"
    first = text.find("<global>") + len("<global>")
    copy.write_text(text[:first] + text[first:].replace("<global>", f"<global>\n{line}"))
    return copy


render_samples.sfz_copy = sfz_copy  # render_part looks it up by name


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--sfizz", default="sfizz_render")
    parser.add_argument("--libs", type=Path, required=True)
    parser.add_argument("--keep-parts", action="store_true", help="keep each part's WAV (to check a part alone)")
    args = parser.parse_args()
    libraries = {name: args.libs / name for name in ("vcsl", "vsco", "jrhodes", "freepats", "smolken", "swirly",
                                                      "meatbass", "rusty", "iowa", "emily", "fashionbass",
                                                      "virtuosity")}
    libraries["local"] = Path(__file__).resolve().parent.parent / "instruments"  # our own (the synth pad)
    for folder in sorted(p for p in args.out.iterdir() if (p / "mix.json").is_file()):
        print(f"== {folder.name}", flush=True)
        sheet = json.loads((folder / "mix.json").read_text())
        for entry in sheet["parts"]:  # an instrument that could not be fetched: its stand-in
            if not (libraries[entry["library"]] / entry["sfz"]).is_file() and "fallback" in entry:
                print(f"  {entry['part']}: {entry['library']} is missing, played on {entry['fallback']['library']}",
                      flush=True)
                entry.update({k: entry["fallback"][k] for k in ("library", "sfz", "tone")})
        (folder / "mix.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False))
        render_samples.mix_folder(folder, args.sfizz, libraries, keep_parts=args.keep_parts)


if __name__ == "__main__":
    main()
