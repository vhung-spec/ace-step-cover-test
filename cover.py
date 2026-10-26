"""Covers the source with ACE-Step 1.5 once per plan entry, loading the
model once. Run with ACE-Step's Python, from ACE-Step's folder (it finds its
code and settings there), with $ACESTEP_CHECKPOINTS_DIR set:

    cd $ACE_DIR && $ACE_VENV/bin/python /path/to/cover.py \
        --source out/source/source.wav --out out [--plan '[{...}]']

Plan entries: {"name", "caption", "strength", "noise" (optional),
"lyrics" (optional; none: instrumental), "task" (optional: "cover", the
app's, or "cover-nofsq", which conditions on the source without FSQ
quantization), "flow_edit_source_caption" (optional: turns on ACE-Step's
flow-edit overlay, which paints the source toward the caption; this text
describes the source)}. The other settings are the ones the app uses for
covers: turbo model, 8 steps, shift 3, no language model, no INT8
quantization. Each cover goes to <out>/covers/<name>/ (source.wav,
take_01.wav/.mp3, settings.json); <out>/plan_results.json lists them all.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

MODEL = "acestep-v15-turbo"
STEPS, SHIFT = 8, 3.0
SEED = 1
DEFAULT_PLAN = Path(__file__).with_name("plan.json")


def cover_steps(strength: float, noise: float) -> tuple[int, int]:
    """(steps that follow the source, steps run), split as ACE-Step's turbo
    model does: a noise above 0 starts from the source's own sound at the
    timestep nearest 1 - noise and skips the steps before it; strength is a
    share of the steps that are left, rounded down."""
    schedule = [SHIFT * t / (1 + (SHIFT - 1) * t) for t in (1 - i / STEPS for i in range(STEPS))]
    if noise > 0:
        start = min(schedule, key=lambda t: abs(t - (1 - noise)))
        schedule = schedule[schedule.index(start):]
    return int(len(schedule) * strength), len(schedule)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--plan", default="", help="JSON list of entries; empty: plan.json")
    args = parser.parse_args()
    plan = json.loads(args.plan) if args.plan.strip() else json.loads(DEFAULT_PLAN.read_text())
    source = args.source.resolve()
    out = args.out.resolve()

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
          f"{os.cpu_count()} CPU threads, ACE-Step profile {gpu.tier}", flush=True)

    started = time.time()
    dit = AceStepHandler()
    status, ok = dit.initialize_service(
        project_root=os.getcwd(),
        config_path=MODEL,
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
    for entry in plan:
        run = out / "covers" / entry["name"]
        run.mkdir(parents=True, exist_ok=True)
        shutil.copy(source, run / "source.wav")
        lyrics = entry.get("lyrics", "")
        noise = float(entry.get("noise", 0))
        following, steps = cover_steps(entry["strength"], noise)
        task = entry.get("task", "cover")
        flow_edit = ({"flow_edit_morph": True,
                      "flow_edit_source_caption": entry["flow_edit_source_caption"]}
                     if entry.get("flow_edit_source_caption") else {})
        print(f"\n=== {entry['name']}: {task}{' + flow edit' if flow_edit else ''}, strength "
              f"{entry['strength']} ({following} of {steps} steps follow the source), noise {noise}"
              f"\n    {entry['caption']}", flush=True)
        params = GenerationParams(
            task_type=task,
            instruction=TASK_INSTRUCTIONS[task],
            src_audio=str(run / "source.wav"),
            reference_audio=None,
            caption=entry["caption"],
            lyrics=lyrics or "[Instrumental]",
            instrumental=not lyrics,
            vocal_language=entry.get("language", "en"),
            audio_cover_strength=entry["strength"],
            cover_noise_strength=noise,
            inference_steps=STEPS,
            seed=SEED,
            shift=SHIFT,
            thinking=False,
            use_cot_metas=False,
            use_cot_caption=False,
            use_cot_language=False,
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
            shutil.move(result.audios[0]["path"], take)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(take), "-q:a", "2",
                            str(take.with_suffix(".mp3"))], check=False)
        shutil.rmtree(run / ".ace", ignore_errors=True)
        (run / "settings.json").write_text(json.dumps(
            {**entry, "model": MODEL, "seed": SEED, "steps_following_source": following,
             "steps_run": steps, "takes": [{"generation_seconds": seconds}] if ok else [],
             "error": error}, indent=2, ensure_ascii=False))
        results.append({**entry, "ok": ok, "seconds": seconds, "run_dir": str(run),
                        "error": error})
        # Written after every cover: a run cut short still leaves its scores.
        (out / "plan_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
        print(f"=== {entry['name']}: {'done' if ok else 'FAILED: ' + str(error)} in {seconds:.0f} s",
              flush=True)
    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
