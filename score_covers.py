"""Scores the covers made by cover.py against their source and writes
<out>/report.md, <out>/scores.json and a spectrogram per cover. Runs with
ACE-Step's Python (torch, transformers) plus librosa:

    $ACE_VENV/bin/python score_covers.py out

ACE-Step keeps a cover's length and timing, so the source and the cover are
compared moment by moment:
- melody: share of the source's melody notes (melody.json) whose pitch class
  is among the strongest in the cover while the note should sound; "chance"
  is the same for the cover played backwards;
- harmony: pitch-class (chroma) similarity, rescaled so that 0 is the source
  against itself played backwards (same notes, wrong time) and 1 is identical;
- key shift: the transposition (semitones) that matches best;
- rhythm: correlation of the note-onset strength over time;
- sound change: distance between average timbres (MFCC), 0 = same sound;
- style: CLAP (laion/clap-htsat-unfused) similarity to the caption, against
  the source's, and the closest of a few style labels;
- level: peak level, clipped samples, near-silent stretches.
"""

import json
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

SR = 22050
HOP = 1024
CLAP_MODEL = "laion/clap-htsat-unfused"
MELODY_FILE = Path("source") / "melody.json"
STYLE_LABELS = [
    "solo piano",
    "jazz piano trio with upright bass and brushed drums",
    "orchestral music with strings and bells",
    "rock band with electric guitars",
    "electronic dance music",
    "choir singing",
]


def _unit(features: np.ndarray) -> np.ndarray:
    return features / (np.linalg.norm(features, axis=0, keepdims=True) + 1e-9)


def harmony(source: np.ndarray, cover: np.ndarray) -> dict:
    a = _unit(librosa.feature.chroma_cqt(y=source, sr=SR, hop_length=HOP))
    b = _unit(librosa.feature.chroma_cqt(y=cover, sr=SR, hop_length=HOP))
    n = min(a.shape[1], b.shape[1])
    a, b = a[:, :n], b[:, :n]
    per_shift = [float(np.mean(np.sum(a * np.roll(b, -k, axis=0), axis=0))) for k in range(12)]
    chance = float(np.mean(np.sum(a * a[:, ::-1], axis=0)))
    shift = int(np.argmax(per_shift))

    def rescale(raw: float) -> float:
        return round((raw - chance) / max(1 - chance, 1e-6), 3)

    # A cover in another key still keeps the melody: "harmony" is measured in
    # the best-matching key, "key_shift" says which.
    return {"harmony_same_key": rescale(per_shift[0]), "harmony": rescale(per_shift[shift]),
            "harmony_chance": round(chance, 3), "key_shift": shift if shift <= 6 else shift - 12}


def melody_hits(y: np.ndarray, notes: list[dict], shift: int = 0) -> float:
    """Share of melody notes whose pitch class (moved by `shift` semitones) is
    within 75 % of the strongest pitch class while the note should sound."""
    hop = 512
    chroma = librosa.feature.chroma_cqt(y=y, sr=SR, hop_length=hop)
    times = librosa.frames_to_time(np.arange(chroma.shape[1]), sr=SR, hop_length=hop)
    hits = 0
    for note in notes:
        frames = (times >= note["start"] + 0.04) & (times < note["end"] - 0.04)
        if frames.any():
            mean = chroma[:, frames].mean(axis=1)
            hits += mean[(note["pitch"] + shift) % 12] >= 0.75 * mean.max()
    return round(100 * hits / len(notes), 1)


def rhythm(source: np.ndarray, cover: np.ndarray) -> dict:
    a = librosa.onset.onset_strength(y=source, sr=SR, hop_length=HOP)
    b = librosa.onset.onset_strength(y=cover, sr=SR, hop_length=HOP)
    n = min(len(a), len(b))
    tempo_a = float(np.atleast_1d(librosa.beat.beat_track(y=source, sr=SR)[0])[0])
    tempo_b = float(np.atleast_1d(librosa.beat.beat_track(y=cover, sr=SR)[0])[0])
    return {"rhythm": round(float(np.corrcoef(a[:n], b[:n])[0, 1]), 3),
            "tempo_source": round(tempo_a), "tempo_cover": round(tempo_b)}


def sound_change(source: np.ndarray, cover: np.ndarray) -> dict:
    a = librosa.feature.mfcc(y=source, sr=SR, n_mfcc=20)[1:].mean(axis=1)
    b = librosa.feature.mfcc(y=cover, sr=SR, n_mfcc=20)[1:].mean(axis=1)
    cosine = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
    centroid = [float(librosa.feature.spectral_centroid(y=y, sr=SR).mean()) for y in (source, cover)]
    return {"sound_change": round(1 - cosine, 3), "brightness_source_hz": round(centroid[0]),
            "brightness_cover_hz": round(centroid[1])}


def level(path: Path) -> dict:
    audio, rate = sf.read(path, always_2d=True)
    mono = audio.mean(axis=1)
    window = rate // 10
    rms = np.sqrt(np.convolve(mono ** 2, np.ones(window) / window, mode="valid")[::window])
    inner = rms[10:-10] if len(rms) > 20 else rms  # fades at the ends are expected
    return {"peak_dbfs": round(20 * np.log10(np.abs(audio).max() + 1e-9), 1),
            "clipped_pct": round(100 * float(np.mean(np.abs(audio) >= 0.999)), 3),
            "near_silent_pct": round(100 * float(np.mean(inner < 10 ** (-60 / 20))), 1)}


class Clap:
    """Text-audio similarity; 10 s windows, averaged."""

    def __init__(self):
        import torch
        from transformers import ClapModel, ClapProcessor

        self.torch = torch
        self.model, info = ClapModel.from_pretrained(CLAP_MODEL, output_loading_info=True)
        self.model.eval()
        if info.get("missing_keys"):
            raise RuntimeError(f"{len(info['missing_keys'])} CLAP weights missing, "
                               f"e.g. {info['missing_keys'][:3]}")
        self.processor = ClapProcessor.from_pretrained(CLAP_MODEL)

    def audio(self, path: Path) -> np.ndarray:
        y, _ = librosa.load(path, sr=48000, mono=True)
        step = 10 * 48000
        chunks = [y[i:i + step] for i in range(0, max(len(y) - step // 2, 1), step)]
        with self.torch.no_grad():
            inputs = self.processor.feature_extractor(chunks, sampling_rate=48000, return_tensors="pt")
            emb = self.model.get_audio_features(**inputs).numpy()
        emb = emb / np.linalg.norm(emb, axis=1, keepdims=True)
        mean = emb.mean(axis=0)
        return mean / np.linalg.norm(mean)

    def text(self, texts: list[str]) -> np.ndarray:
        with self.torch.no_grad():
            inputs = self.processor.tokenizer(texts, padding=True, return_tensors="pt")
            emb = self.model.get_text_features(**inputs).numpy()
        return emb / np.linalg.norm(emb, axis=1, keepdims=True)


def spectrograms(images: list[tuple[str, np.ndarray]], path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import librosa.display
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(len(images), 1, figsize=(12, 2.6 * len(images)), squeeze=False)
    for ax, (title, y) in zip(axes[:, 0], images):
        mel = librosa.power_to_db(librosa.feature.melspectrogram(y=y, sr=SR, n_mels=96), ref=np.max)
        librosa.display.specshow(mel, sr=SR, x_axis="time", y_axis="mel", ax=ax)
        ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=80)
    plt.close(fig)


def main(out_dir: str) -> int:
    out = Path(out_dir)
    plan_file = out / "plan_results.json"
    if not plan_file.is_file():
        print("No covers to score.")
        return 1
    entries = json.loads(plan_file.read_text())
    try:
        clap = Clap()
        labels = clap.text(STYLE_LABELS)
    except Exception as err:  # the scores without CLAP still say a lot
        print(f"CLAP unavailable: {err}")
        clap = labels = None

    melody_file = out / MELODY_FILE
    melody = json.loads(melody_file.read_text()) if melody_file.is_file() else None
    scores = []
    for entry in entries:
        run = Path(entry["run_dir"]) if entry.get("run_dir") else None
        take = run / "take_01.wav" if run else None
        if not entry["ok"] or take is None or not take.is_file():
            scores.append({"name": entry["name"], "ok": False})
            continue
        source_path = run / "source.wav"
        source = librosa.load(source_path, sr=SR, mono=True)[0]
        cover = librosa.load(take, sr=SR, mono=True)[0]
        settings = json.loads((run / "settings.json").read_text())
        if melody and not scores:  # once: how the measure does on the source itself
            print(f"Melody notes found in the source itself: {melody_hits(source, melody)} %; "
                  f"in the source played backwards: {melody_hits(source[::-1], melody)} %")
        row = {"name": entry["name"], "ok": True, "strength": entry["strength"],
               "noise": entry.get("noise", 0), "caption": entry["caption"],
               "steps_following_source": settings.get("steps_following_source"),
               "cover_seconds": entry["seconds"],
               "take_seconds": (settings.get("takes") or [{}])[0].get("generation_seconds"),
               **harmony(source, cover), **rhythm(source, cover), **sound_change(source, cover),
               **level(take)}
        if melody:
            row["melody_pct"] = melody_hits(cover, melody, row["key_shift"])
            row["melody_chance_pct"] = melody_hits(cover[::-1], melody, row["key_shift"])
        if clap is not None:
            caption = clap.text([entry["caption"]])[0]
            source_emb, cover_emb = clap.audio(source_path), clap.audio(take)
            if not scores or not scores[-1].get("ok"):  # once: does CLAP tell styles apart?
                print("CLAP, source vs labels: " + ", ".join(
                    f"{label} {float(sim):.3f}" for label, sim in zip(STYLE_LABELS, labels @ source_emb)))
            row.update({
                "style_source": round(float(source_emb @ caption), 3),
                "style_cover": round(float(cover_emb @ caption), 3),
                "label_source": STYLE_LABELS[int(np.argmax(labels @ source_emb))],
                "label_cover": STYLE_LABELS[int(np.argmax(labels @ cover_emb))],
            })
        try:
            spectrograms([("source", source), (entry["name"], cover)], out / f"{entry['name']}.png")
        except Exception as err:
            print(f"No spectrogram for {entry['name']}: {err}")
        scores.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)

    (out / "scores.json").write_text(json.dumps(scores, indent=2, ensure_ascii=False))
    lines = ["| run | steps | time (s) | melody % (chance) | harmony | key shift | rhythm | "
             "tempo src→cover | sound change | style src→cover | closest style | peak dBFS | "
             "clipped % | silent % |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in scores:
        if not r["ok"]:
            lines.append(f"| {r['name']} | FAILED |" + " |" * 12)
            continue
        style = (f"{r['style_source']}→{r['style_cover']}" if "style_cover" in r else "n/a")
        lines.append(
            f"| {r['name']} | {r['steps_following_source']}/8 | {r['take_seconds']} | "
            f"{r.get('melody_pct', 'n/a')} ({r.get('melody_chance_pct', 'n/a')}) | "
            f"{r['harmony']} | {r['key_shift']} | {r['rhythm']} | "
            f"{r['tempo_source']}→{r['tempo_cover']} | {r['sound_change']} | {style} | "
            f"{r.get('label_cover', 'n/a')} | {r['peak_dbfs']} | {r['clipped_pct']} | "
            f"{r['near_silent_pct']} |")
    report = "\n".join(lines)
    (out / "report.md").write_text(report + "\n")
    print("\n" + report)
    return 0 if all(r["ok"] for r in scores) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "out"))
