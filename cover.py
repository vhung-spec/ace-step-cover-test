"""Covers the source with ACE-Step 1.5 once per plan entry, loading the
model once. Run with ACE-Step's Python, from ACE-Step's folder (it finds its
code and settings there), with $ACESTEP_CHECKPOINTS_DIR set:

    cd $ACE_DIR && $ACE_VENV/bin/python /path/to/cover.py \
        --source out/source/source.wav --out out \
        [--model acestep-v15-turbo] [--plan '[{...}]']

Plan entries: {"name", "caption", "strength", "noise" (optional),
"lyrics" (optional; none: instrumental), "task" (optional: "cover", the
app's, or "cover-nofsq", which conditions on the source without FSQ
quantization), "flow_edit_source_caption" (optional: turns on ACE-Step's
flow-edit overlay, which paints the source toward the caption; this text
describes the source), "reference" (optional: the name of an earlier entry
whose take is the cover's reference audio, the sound to follow)}. An entry
with "task": "text2music" makes a new piece from its caption instead
("duration" in seconds, default 30), e.g. a reference for later covers.

Base model only: "task": "lego" with "track" (one of ACE-Step's track names,
e.g. "strings", "percussion") makes that one instrument's part to play along
with the source; the part is kept as stem_01.wav and mixed with the source
into take_01.wav. "task": "complete" with "tracks" (a list) arranges those
instruments around the source; its output is the take. "source_from" (the
name of an earlier entry) uses that entry's take as the source, to stack
layers.

Every entry may set "steps" (default 8 on turbo models, 50 on the others),
"shift" (default 3 on turbo, 1 on the others) and, on the others,
"guidance" (default 7). The app's covers use the turbo model, 8 steps,
shift 3, no language model, no INT8 quantization. Each cover goes to
<out>/covers/<name>/ (source.wav, take_01.wav/.mp3, settings.json);
<out>/plan_results.json lists them all.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

SEED = 1
LAYER_LEVEL = 0.7  # a lego part's loudness (RMS) in the mix, against the source's
DEFAULT_PLAN = Path(__file__).with_name("plan.json")


def cover_steps(strength: float, noise: float, steps: int = 8, shift: float = 3.0) -> tuple[int, int]:
    """(steps that follow the source, steps run), split as ACE-Step does: the
    timesteps are 1 - i/steps, shifted; a noise above 0 starts from the
    source's own sound at the timestep nearest 1 - noise and skips the steps
    before it; strength is a share of the steps that are left, rounded down."""
    schedule = [1 - i / steps for i in range(steps)]
    if shift != 1.0:
        schedule = [shift * t / (1 + (shift - 1) * t) for t in schedule]
    if noise > 0:
        start = min(schedule, key=lambda t: abs(t - (1 - noise)))
        schedule = schedule[schedule.index(start):]
    return int(len(schedule) * strength), len(schedule)


def mix(source: Path, part: Path, out: Path) -> None:
    """The source plus a new part at LAYER_LEVEL of the source's loudness,
    peaking at -1 dBFS."""
    a, rate = sf.read(source, always_2d=True)
    b, part_rate = sf.read(part, always_2d=True)
    if rate != part_rate:
        raise ValueError(f"source at {rate} Hz, part at {part_rate} Hz")
    a, b = (np.repeat(x, 2, axis=1) if x.shape[1] == 1 else x for x in (a, b))
    n = max(len(a), len(b))
    a, b = (np.pad(x, ((0, n - len(x)), (0, 0))) for x in (a, b))

    def rms(x: np.ndarray) -> float:
        return float(np.sqrt(np.mean(x ** 2))) + 1e-9

    mixed = a + b * min(LAYER_LEVEL * rms(a) / rms(b), 4.0)  # capped: a near-silent part stays quiet
    sf.write(out, mixed * 10 ** (-1 / 20) / (np.abs(mixed).max() + 1e-9), rate)


def mp3(wav: Path) -> None:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-q:a", "2",
                    str(wav.with_suffix(".mp3"))], check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--model", default="acestep-v15-turbo")
    parser.add_argument("--plan", default="", help="JSON list of entries; empty: plan.json")
    args = parser.parse_args()
    plan = json.loads(args.plan) if args.plan.strip() else json.loads(DEFAULT_PLAN.read_text())
    source = args.source.resolve()
    out = args.out.resolve()
    turbo = "turbo" in args.model

    import torch

    from acestep.constants import TASK_INSTRUCTIONS
    from acestep.gpu_config import get_gpu_config, set_global_gpu_config
    from acestep.handler import AceStepHandler
    from acestep.inference import GenerationConfig, GenerationParams, generate_music
    from acestep.llm_inference import LLMHandler

    torch.set_num_threads(os.cpu_count() or 1)
    gpu = get_gpu_config()
    set_global_gpu_config(gpu)
    print(f"torch {torch.__version__}, CUDA {torch.cuda.is_available()}, "
          f"{os.cpu_count()} CPU threads, ACE-Step profile {gpu.tier}, model {args.model}", flush=True)

    started = time.time()
    dit = AceStepHandler()
    status, ok = dit.initialize_service(
        project_root=os.getcwd(),
        config_path=args.model,
        device="auto",
        use_flash_attention=False,
        compile_model=False,
        offload_to_cpu=False,
        offload_dit_to_cpu=False,
        quantization=None,
    )
    if not ok:
        print(f"ACE-Step could not load its model: {status}", flush=True)
        return 1
    print(f"Model loaded in {time.time() - started:.0f} s", flush=True)
    llm = LLMHandler()  # never initialized: covers do not use the language model

    results = []

    def fail(entry: dict, run: Path, error: str) -> None:
        print(f"=== {entry['name']}: FAILED: {error}", flush=True)
        results.append({**entry, "ok": False, "seconds": 0, "run_dir": str(run), "error": error})
        (out / "plan_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))

    for entry in plan:
        run = out / "covers" / entry["name"]
        run.mkdir(parents=True, exist_ok=True)
        task = entry.get("task", "cover")
        lyrics = entry.get("lyrics", "")
        steps = int(entry.get("steps", 8 if turbo else 50))
        if turbo:
            steps = min(steps, 20)  # ACE-Step runs turbo models for at most 20 steps
        shift = float(entry.get("shift", 3.0 if turbo else 1.0))
        guidance = None if turbo else float(entry.get("guidance", 7.0))
        common = dict(
            caption=entry["caption"],
            lyrics=lyrics or "[Instrumental]",
            instrumental=not lyrics,
            vocal_language=entry.get("language", "en"),
            inference_steps=steps,
            seed=SEED,
            shift=shift,
            thinking=False,
            use_cot_metas=False,
            use_cot_caption=False,
            use_cot_language=False,
            **({} if guidance is None else {"guidance_scale": guidance}),
        )
        if task == "text2music":  # a new piece, e.g. a reference for later covers
            following, steps_run = 0, steps
            print(f"\n=== {entry['name']}: text2music, {entry.get('duration', 30)} s"
                  f"\n    {entry['caption']}", flush=True)
            params = GenerationParams(task_type=task, duration=float(entry.get("duration", 30)),
                                      **common)
        else:
            entry_source = source
            if entry.get("source_from"):  # stack on an earlier entry's take
                entry_source = out / "covers" / entry["source_from"] / "take_01.wav"
                if not entry_source.is_file():
                    fail(entry, run, f"no source {entry['source_from']}")
                    continue
            shutil.copy(entry_source, run / "source.wav")
            reference = None
            if entry.get("reference"):
                reference_take = out / "covers" / entry["reference"] / "take_01.wav"
                if not reference_take.is_file():
                    fail(entry, run, f"no reference {entry['reference']}")
                    continue
                reference = run / "reference.wav"
                shutil.copy(reference_take, reference)
            if task in ("lego", "complete"):
                following, steps_run = 0, steps
                if task == "lego":
                    instruction = TASK_INSTRUCTIONS["lego"].format(TRACK_NAME=entry["track"].upper())
                    extra = {"repainting_start": 0.0, "repainting_end": -1}
                else:
                    instruction = TASK_INSTRUCTIONS["complete"].format(
                        TRACK_CLASSES=" | ".join(t.upper() for t in entry["tracks"]))
                    extra = {"duration": round(sf.info(run / "source.wav").duration, 2)}
                print(f"\n=== {entry['name']}: {instruction} ({steps} steps, guidance {guidance})"
                      f"{' on ' + entry['source_from'] if entry.get('source_from') else ''}"
                      f"\n    {entry['caption']}", flush=True)
                params = GenerationParams(
                    task_type=task,
                    instruction=instruction,
                    src_audio=str(run / "source.wav"),
                    reference_audio=str(reference) if reference else None,
                    **common,
                    **extra,
                )
            else:
                noise = float(entry.get("noise", 0))
                following, steps_run = cover_steps(entry["strength"], noise, steps, shift)
                flow_edit = ({"flow_edit_morph": True,
                              "flow_edit_source_caption": entry["flow_edit_source_caption"]}
                             if entry.get("flow_edit_source_caption") else {})
                print(f"\n=== {entry['name']}: {task}{' + flow edit' if flow_edit else ''}"
                      f"{' + reference ' + entry['reference'] if reference else ''}, strength "
                      f"{entry['strength']} ({following} of {steps_run} steps follow the source), "
                      f"noise {noise}, guidance {guidance}\n    {entry['caption']}", flush=True)
                params = GenerationParams(
                    task_type=task,
                    instruction=TASK_INSTRUCTIONS[task],
                    src_audio=str(run / "source.wav"),
                    reference_audio=str(reference) if reference else None,
                    audio_cover_strength=entry["strength"],
                    cover_noise_strength=noise,
                    **common,
                    **flow_edit,
                )
        config = GenerationConfig(batch_size=1, use_random_seed=False, seeds=[SEED],
                                  audio_format="wav")
        take_started = time.time()
        try:
            result = generate_music(dit, llm, params, config, save_dir=str(run / ".ace"))
            ok = bool(result.success and result.audios and result.audios[0]["path"])
            error = None if ok else (result.error or result.status_message)
        except Exception as err:  # one failed cover must not stop the others
            ok, error = False, f"{type(err).__name__}: {err}"
        seconds = round(time.time() - take_started, 1)
        if ok:
            take = run / "take_01.wav"
            try:
                if task == "lego":  # the new part alone, then the part with its source
                    stem = run / "stem_01.wav"
                    shutil.move(result.audios[0]["path"], stem)
                    mp3(stem)
                    mix(run / "source.wav", stem, take)
                else:
                    shutil.move(result.audios[0]["path"], take)
                mp3(take)
            except Exception as err:  # e.g. a part that cannot be mixed
                ok, error = False, f"{type(err).__name__}: {err}"
        shutil.rmtree(run / ".ace", ignore_errors=True)
        (run / "settings.json").write_text(json.dumps(
            {**entry, "model": args.model, "seed": SEED, "steps": steps, "shift": shift,
             "guidance": guidance, "steps_following_source": following, "steps_run": steps_run,
             "takes": [{"generation_seconds": seconds}] if ok else [], "error": error},
            indent=2, ensure_ascii=False))
        results.append({**entry, "ok": ok, "seconds": seconds, "run_dir": str(run),
                        "error": error})
        # Written after every cover: a run cut short still leaves its scores.
        (out / "plan_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
        print(f"=== {entry['name']}: {'done' if ok else 'FAILED: ' + str(error)} in {seconds:.0f} s",
              flush=True)
    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
