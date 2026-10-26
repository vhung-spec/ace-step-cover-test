"""Mixes the new parts of lego runs into their sources at several loudness
levels and rates every mix: CLAP's closest style label and Christmas score
(score_covers.py), Audiobox Aesthetics' quality and enjoyment (judge.py).
Shows which level of a new part makes the piece sound like the part's style
without spoiling it:

    python remix.py runs/<run id> [runs/<run id> ...]

The folders are downloaded "ace-cover-test" artifacts: covers/<name>/
stem_01.mp3 is a new part, source/source.mp3 the piece it was made for
(covers/<earlier>/take_01.mp3 when the entry stacked on an earlier take).
"""

import json
import sys
import tempfile
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

from judge import Aesthetics
from score_covers import CHRISTMAS, STYLE_LABELS, Clap

LEVELS = (0.4, 0.7, 1.0, 1.4)
RATE = 48000


def mix(source: np.ndarray, part: np.ndarray, level: float) -> np.ndarray:
    n = max(len(source), len(part))
    source, part = (np.pad(x, (0, n - len(x))) for x in (source, part))

    def rms(x: np.ndarray) -> float:
        return float(np.sqrt(np.mean(x ** 2))) + 1e-9

    mixed = source + part * min(level * rms(source) / rms(part), 4.0)
    return mixed * 10 ** (-1 / 20) / (np.abs(mixed).max() + 1e-9)


def main(folders: list[str]) -> int:
    clap, judge = Clap(), Aesthetics()
    labels, christmas = clap.text(STYLE_LABELS), clap.text([CHRISTMAS])[0]
    rows = []
    with tempfile.TemporaryDirectory() as work:
        for folder in map(Path, folders):
            for stem in sorted(folder.glob("covers/*/stem_01.mp3")):
                settings = json.loads((stem.parent / "settings.json").read_text())
                earlier = settings.get("source_from")
                source_file = (folder / "covers" / earlier / "take_01.mp3" if earlier
                               else folder / "source" / "source.mp3")
                source = librosa.load(source_file, sr=RATE, mono=True)[0]
                part = librosa.load(stem, sr=RATE, mono=True)[0]
                caption = clap.text([settings["caption"]])[0]
                for level in LEVELS:
                    path = Path(work) / f"{stem.parent.name}-{level}.wav"
                    sf.write(path, mix(source, part, level), RATE)
                    emb = clap.audio(path)
                    rows.append({
                        "part": f"{folder.name}/{stem.parent.name}", "level": level,
                        "label": STYLE_LABELS[int(np.argmax(labels @ emb))],
                        "style": round(float(emb @ caption), 3),
                        "christmas": round(float(emb @ christmas), 3),
                        **judge.rate(path),
                    })
                    print(json.dumps(rows[-1]), flush=True)
    lines = ["| part | level | closest style | style | Christmas | PQ | CE | PC |",
             "|---|---|---|---|---|---|---|---|"]
    lines += [f"| {r['part']} | {r['level']} | {r['label']} | {r['style']} | {r['christmas']} | "
              f"{r['PQ']} | {r['CE']} | {r['PC']} |" for r in rows]
    print("\n" + "\n".join(lines))
    return 0 if rows else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
