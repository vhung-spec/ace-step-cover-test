"""Rates how good audio sounds with Meta's Audiobox Aesthetics model
(facebook/audiobox-aesthetics), on four 1-10 scales:
- PQ, production quality: clean, clear, well recorded (low = harsh, noisy,
  muffled, cheap-sounding);
- CE, content enjoyment: how much a listener would enjoy it;
- CU, content usefulness: how usable it is as material for a creator;
- PC, production complexity: how many sounds and layers it has.

    python judge.py out/            # every .mp3/.wav below these folders
    python judge.py a.mp3 b.wav

Needs torch, torchaudio, librosa and the audiobox_aesthetics package.
"""

import json
import sys
from pathlib import Path

AXES = ("PQ", "CE", "CU", "PC")
RATE = 16000


class Aesthetics:
    def __init__(self):
        import torch
        from audiobox_aesthetics.infer import initialize_predictor

        self.torch = torch
        self.predictor = initialize_predictor()  # weights from Hugging Face

    def rate(self, path: Path) -> dict:
        import librosa

        # Read here, not by the package: newer torchaudio needs extra codecs to read files.
        y, _ = librosa.load(path, sr=RATE, mono=True)
        wav = self.torch.from_numpy(y).unsqueeze(0)
        result = self.predictor.forward([{"path": wav, "sample_rate": RATE}])[0]
        return {axis: round(float(result[axis]), 2) for axis in AXES}


def audio_files(paths: list[str]) -> list[Path]:
    files = []
    for name in paths:
        path = Path(name)
        if path.is_dir():
            found = sorted(p for p in path.rglob("*") if p.suffix in (".mp3", ".wav"))
            # the same take as WAV and MP3: rate the WAV only
            files += [p for p in found if not (p.suffix == ".mp3" and p.with_suffix(".wav") in found)]
        else:
            files.append(path)
    return files


def main(paths: list[str]) -> int:
    judge = Aesthetics()
    rows = []
    for path in audio_files(paths):
        row = {"file": str(path), **judge.rate(path)}
        rows.append(row)
        print(json.dumps(row), flush=True)
    lines = ["| file | PQ quality | CE enjoyment | CU usefulness | PC complexity |",
             "|---|---|---|---|---|"]
    lines += [f"| {r['file']} | {r['PQ']} | {r['CE']} | {r['CU']} | {r['PC']} |" for r in rows]
    print("\n" + "\n".join(lines))
    return 0 if rows else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
