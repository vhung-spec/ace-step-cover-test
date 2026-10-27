"""Rates finished pieces, every MP3 in a folder: Meta's Audiobox Aesthetics
(quality PQ, enjoyment CE, usefulness CU, complexity PC; judge.py) and CLAP's
closest style label and Christmas score (score_covers.py):

    python rate.py out/sampled
"""

import json
import sys
from pathlib import Path

import numpy as np

from judge import Aesthetics
from score_covers import CHRISTMAS, STYLE_LABELS, Clap


def main(folder: str) -> int:
    clap, judge = Clap(), Aesthetics()
    labels, christmas = clap.text(STYLE_LABELS), clap.text([CHRISTMAS])[0]
    rows = []
    for path in sorted(Path(folder).glob("*.mp3")):
        emb = clap.audio(path)
        rows.append({"piece": path.stem, "label": STYLE_LABELS[int(np.argmax(labels @ emb))],
                     "christmas": round(float(emb @ christmas), 3), **judge.rate(path)})
        print(json.dumps(rows[-1]), flush=True)
    lines = ["| piece | closest style | Christmas | PQ | CE | CU | PC |", "|---|---|---|---|---|---|---|"]
    lines += [f"| {r['piece']} | {r['label']} | {r['christmas']} | {r['PQ']} | {r['CE']} | {r['CU']} | "
              f"{r['PC']} |" for r in rows]
    print("\n" + "\n".join(lines))
    return 0 if rows else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
