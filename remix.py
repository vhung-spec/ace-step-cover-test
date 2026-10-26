"""Mixes the new parts of lego runs into their sources at several loudness
levels and rates every mix: melody kept and harmony against the piece the
part was made for, CLAP's closest style label and Christmas score
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
from score_covers import CHRISTMAS, MELODY_FILE, SR, STYLE_LABELS, Clap, harmony, melody_hits

LEVELS = (0.0, 0.4, 0.7, 1.0, 1.4)  # 0: the piece alone, for comparison
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
                melody_file = folder / MELODY_FILE
                melody = json.loads(melody_file.read_text()) if melody_file.is_file() else None
                caption = clap.text([settings["caption"]])[0]
                for level in LEVELS:
                    path = Path(work) / f"{stem.parent.name}-{level}.wav"
                    sf.write(path, mix(source, part, level), RATE)
                    emb = clap.audio(path)
                    mixed = librosa.load(path, sr=SR, mono=True)[0]
                    kept = harmony(librosa.resample(source, orig_sr=RATE, target_sr=SR), mixed)
                    rows.append({
                        "part": f"{folder.name}/{stem.parent.name}", "level": level,
                        "melody": melody_hits(mixed, melody) if melody else None,
                        "harmony": kept["harmony_same_key"],
                        "label": STYLE_LABELS[int(np.argmax(labels @ emb))],
                        "style": round(float(emb @ caption), 3),
                        "christmas": round(float(emb @ christmas), 3),
                        **judge.rate(path),
                    })
                    print(json.dumps(rows[-1]), flush=True)
    lines = ["| part | level | melody % | harmony | closest style | style | Christmas | PQ | CE | PC |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    lines += [f"| {r['part']} | {r['level']} | {r['melody']} | {r['harmony']} | {r['label']} | "
              f"{r['style']} | {r['christmas']} | {r['PQ']} | {r['CE']} | {r['PC']} |" for r in rows]
    print("\n" + "\n".join(lines))
    return 0 if rows else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
