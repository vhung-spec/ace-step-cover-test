"""Adds new parts to a piece one after the other, as the app does when a part
is added to a mix: each part, made against the piece itself, joins the mix so
far at its level times that mix's loudness. Rates the piece and every step as
remix.py does (melody kept and harmony against the piece, CLAP's closest style
label and Christmas score, Audiobox Aesthetics), and keeps every step as an
MP3 in stacked/<id>/ to listen to:

    python stack.py runs/<id> <part>:<level> [<part>:<level> ...]

runs/<id> is a downloaded "ace-cover-test" artifact whose source/source.mp3 is
the piece and source/melody.json its melody; each <part> is a new part made
for that same piece, e.g. runs/<other id>/covers/<name>/stem_01.mp3.
"""

import json
import sys
import tempfile
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

from judge import Aesthetics
from remix import RATE, mix
from score_covers import CHRISTMAS, MELODY_FILE, SR, STYLE_LABELS, Clap, harmony, melody_hits


def main(folder: str, parts: list[str]) -> int:
    run = Path(folder)
    melody = json.loads((run / MELODY_FILE).read_text())
    piece = librosa.load(run / "source" / "source.mp3", sr=RATE, mono=False)[0]
    piece_mono = librosa.resample(np.atleast_2d(piece).mean(axis=0), orig_sr=RATE, target_sr=SR)
    clap, judge = Clap(), Aesthetics()
    labels, christmas = clap.text(STYLE_LABELS), clap.text([CHRISTMAS])[0]
    mixed, name, rows = mix(piece, piece, 0.0), "the piece", []  # level 0: the piece alone
    keep = Path("stacked") / run.name
    keep.mkdir(parents=True, exist_ok=True)
    file_name = "piece"
    with tempfile.TemporaryDirectory() as work:
        for step, spec in enumerate([None, *parts]):
            if spec:
                path, level = spec.rsplit(":", 1)
                mixed = mix(mixed, librosa.load(path, sr=RATE, mono=False)[0], float(level))
                name += f" + {Path(path).parent.name} at {level}"
                file_name += f"+{Path(path).parent.name}-{level}"
            file = Path(work) / f"step{step}.wav"
            sf.write(file, mixed.T, RATE)
            sf.write(keep / f"{file_name}.mp3", mixed.T, RATE)
            mono = librosa.load(file, sr=SR, mono=True)[0]
            emb = clap.audio(file)
            rows.append({"mix": name, "melody": melody_hits(mono, melody),
                         "harmony": harmony(piece_mono, mono)["harmony_same_key"],
                         "label": STYLE_LABELS[int(np.argmax(labels @ emb))],
                         "christmas": round(float(emb @ christmas), 3), **judge.rate(file)})
            print(json.dumps(rows[-1]), flush=True)
    lines = ["| mix | melody % | harmony | closest style | Christmas | PQ | CE | PC |",
             "|---|---|---|---|---|---|---|---|"]
    lines += [f"| {r['mix']} | {r['melody']} | {r['harmony']} | {r['label']} | {r['christmas']} | "
              f"{r['PQ']} | {r['CE']} | {r['PC']} |" for r in rows]
    print("\n" + "\n".join(lines))
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1], sys.argv[2:]))
