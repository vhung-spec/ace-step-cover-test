"""Parts written by Composer's Assistant 2 into one of our arrangements.

The user, on Jingle Bells' felt piano with a bed of strings (version 6):
"the bed's lines aren't nice yet, they don't feel of a piece with the song;
look to recordings, or find open-source tools that can fix this". Composer's
Assistant 2 (M. Malandro, github.com/m-malandro/composers-assistant-REAPER,
MIT; its models trained only on public-domain and permissively licensed
MIDI) is such a tool: a T5 transformer that fills in the empty parts of a
piece, hearing the rest. It is made for the REAPER editor (an empty MIDI item
on a track asks it to fill those bars); this does as its REAPER script does
(rpr_ca_functions.get_nn_input_from_project, write_nn_output_to_project),
without REAPER.

A plan (versions/<song>/ai/<name>.plan.json) names the version whose parts
the model hears (its piano, heard as one piano, or a part each as its own
instrument by its General MIDI program), the parts it writes (an instrument
by its program, in spans of bars, each with the keys asked for there and how
they move: CA2's own controls) and the takes (seeds):

    python infill.py jingle-bells/ai/strings out --ca2 <the release's Scripts/composers_assistant_v2>

It writes four bars at a time, hearing the four before (with what it has
written there) and one ahead, which it writes again with the next four.
Each take goes to out/<name>-take<seed>.json: the parts, in our ticks, and
each window's input and output, to look at. The arranger lays a take in
(Style.written).
"""
import argparse
import json
import random
import sys
import time
from pathlib import Path

import arrange
from arrange import TICKS

CLICKS = 960  # CA2 reads a piece at 960 clicks a quarter note, as REAPER gives it
WINDOW, BEFORE, AHEAD = 4, 4, 1  # bars written at a time, heard before them, written ahead
HEARD_AGAIN = 45  # the velocity the model hears its own notes at, in the next windows
CONTROLS = (("vert", "vert_note_onset_density"), ("classes", "vert_note_onset_n_pitch_classes_on_avg"),
            ("horiz", "horiz_note_onset_density"), ("rhythm", "horiz_note_onset_irregularity"),
            ("step", "pitch_step_prob"), ("leap", "pitch_leap_prob"))  # in the order CA2 was trained with


class Model:
    """Composer's Assistant 2: its own code and its infill model, from its
    release's folder (Scripts/composers_assistant_v2)."""

    def __init__(self, folder: Path):
        sys.path.insert(0, str(folder))
        import constants
        import encoding_functions
        import midisong
        import nn_str_functions
        import preprocessing_functions
        import unjoined_vocab_tokenizer
        import torch
        import transformers
        self.cs, self.enc, self.ms, self.nns, self.pre, self.torch = (
            constants, encoding_functions, midisong, nn_str_functions, preprocessing_functions, torch)
        self.cpq = midisong.extended_lcm(constants.QUANTIZE)  # its clicks a quarter note once quantized: 24
        self.tokenizer = unjoined_vocab_tokenizer.UnjoinedTokenizer("unjoined_include_note_duration_commands")
        path = folder / constants.UNJOINED_PATH_TO_MODELS / "infill" / "finetuned_epoch_49_0" / "model"
        self.net = transformers.T5ForConditionalGeneration.from_pretrained(path).eval()

    def song(self, arr: arrange.Arrangement, tracks: dict, bars: int):
        """Our parts ({program: [(tick, note, velocity, length)]}) as CA2's
        MidiSongByMeasure, built and quantized as its REAPER script builds it."""
        ms, scale = self.ms, CLICKS // TICKS
        ends = [k * arr.bar * scale for k in range(bars + 1)]
        tempos = [ms.TempoChange(val=[bpm for t, bpm in arr.tempos if t <= k * arr.bar][-1], click=end)
                  for k, end in enumerate(ends)]
        song = ms.MidiSong(cpq=CLICKS, tempo_changes=tempos)
        for program, notes in tracks.items():
            track = ms.Track(inst=program, name=str(program))
            track.notes = [ms.Note(pitch=n, vel=v, click=t * scale, end=(t + l) * scale)
                           for t, n, v, l in notes if (t + l) * scale < ends[-1]]
            song.tracks.append(track)
        song.sort_tracks_by_inst()
        self.pre.apply_simplified_drum_map(song)
        song = ms.MidiSongByMeasure.from_MidiSong(song, measure_endpoints=ends, consume_calling_song=True)
        song.quantize_notes_by_measure(q=self.cs.QUANTIZE)
        song.change_cpq(self.cpq)
        self.enc.transpose_into_acceptable_ranges_TT(song)
        for track in song.tracks:
            track.sort()
        return song

    def controls(self, part: dict, low: int, high: int) -> str:
        """A part's controls, at the end of the model's input (as CA2's track
        options give them): how many notes sound at once (vert), how often
        notes start (horiz), steps and leaps, and its lowest and highest
        keys, loosely (or strictly, with "strict")."""
        enc = self.enc
        text = "".join(enc.instruction_str(part[key], measure) for key, measure in CONTROLS if key in part)
        kind = "strict" if part.get("strict") else "loose"
        return text + enc.instruction_str(low, f"lowest_note_{kind}") + enc.instruction_str(high, f"highest_note_{kind}")

    def write(self, text: str, seed: int, temperature: float) -> tuple:
        """The model's answer to an input: (input tokens, its output), sampled
        as CA2 samples (top-p 0.85)."""
        torch, tokenizer = self.torch, self.tokenizer
        torch.manual_seed(seed)
        ids = tokenizer.Encode(text)
        with torch.no_grad():
            out = self.net.generate(input_ids=torch.tensor([ids], dtype=torch.long), num_return_sequences=1,
                                    do_sample=True, temperature=temperature, top_p=0.85, min_length=2,
                                    max_new_tokens=3300, decoder_start_token_id=tokenizer.pad_id(),
                                    pad_token_id=tokenizer.pad_id(), bos_token_id=tokenizer.bos_id(),
                                    eos_token_id=tokenizer.eos_id(), use_cache=True)
        return len(ids), tokenizer.Decode([x.item() for x in out[0][1:]])

    def notes(self, instructions: list, tick: int, program: int) -> list:
        """A bar's notes, (tick, note, length), from the model's instructions:
        d: the length of the notes after it, w: a wait, N: a note (in its
        clicks); a note's key brought by octaves into its instrument's range."""
        low, high = self.cs.ACCEPTABLE_NOTE_RANGE_BY_INST_RPR[program]
        per, bar = TICKS // self.cpq, 4 * self.cpq
        notes, length, at = set(), self.cpq // 2, 0
        for instruction in instructions:
            kind, _, value = instruction.partition(":")
            if kind == "d":
                length = int(value)
            elif kind == "w":
                at += int(value)
            elif kind == "N" and at < bar:
                key = int(value)
                while key < low:
                    key += 12
                while key > high:
                    key -= 12
                notes.add((tick + at * per, key, max(1, length) * per))
        return sorted(notes)


def take(model: Model, plan: dict, arr: arrange.Arrangement, seed: int) -> dict:
    """One take of the plan's parts, written window by window."""
    rng = random.Random(seed)
    parts, temperature = plan["parts"], plan.get("temperature", 1.0)
    hear = plan.get("hear", ["piano"])  # our parts it hears: as one piano, or each its own instrument (by program)
    heard = {program: [n for name in hear if hear[name] == program for n in arr.parts[name].notes]
             for program in set(hear.values())} if isinstance(hear, dict) else {0: [n for name in hear
                                                                                 for n in arr.parts[name].notes]}
    programs = {name: part["program"] for name, part in parts.items()}
    written = {name: [] for name in parts}
    first = min(span[0] for part in parts.values() for span in part["spans"])
    last = max(span[1] for part in parts.values() for span in part["spans"])
    bars = max(last, arr.end // arr.bar + 2) + 4
    windows = []
    for start in range(first, last, WINDOW):
        stop = min(start + WINDOW, last)
        song = model.song(arr, heard | {programs[name]: [(t, n, HEARD_AGAIN, l) for t, n, l in notes]
                                        for name, notes in written.items()}, bars)
        index = {track.inst: i for i, track in enumerate(song.tracks)}
        name_of = {index[program]: name for name, program in programs.items()}
        masks, controls = [], {}
        for name, part in parts.items():
            span = next((s for s in part["spans"] if s[0] <= start < s[1]), None)
            if span:
                masks += [(index[programs[name]], bar) for bar in range(start, min(stop + AHEAD, span[1]))]
                controls[index[programs[name]]] = model.controls(part, span[2], span[3])
        if not masks:
            continue
        masks.sort(key=lambda mask: (mask[1], mask[0]))
        rng.shuffle(masks)  # the model was trained with its masks' labels in random order (PERMUTE_MASKS)
        offset = rng.randint(0, 255 - (len(masks) - 1))
        text, _ = model.enc.encode_midisongbymeasure_with_masks(
            song, note_off_treatment="duration", mask_locations=masks,
            measure_slice=(max(0, start - BEFORE), max(bar for _, bar in masks) + 1),
            include_heads_for_empty_masked_measures=True, return_labels_too=False, extra_id_st=offset,
            extra_id_max=255, commands_at_end=controls)
        asked = {name_of[track] for track, _ in masks}
        for attempt in range(3):  # again, if a part was left silent through the window
            began = time.time()
            tokens, output = model.write(text, seed * 100003 + start * 10 + attempt, temperature)
            by_label = model.nns.instructions_by_extra_id(output)
            new = {name: [] for name in parts}
            for i, (track, bar) in enumerate(masks):
                if bar < stop:
                    new[name_of[track]] += model.notes(by_label.get(f"<extra_id_{offset + i}>", []),
                                                       bar * arr.bar, programs[name_of[track]])
            print(f"take {seed}, bars {start}-{stop - 1}: {tokens} tokens in, {len(output)} characters out, "
                  f"{time.time() - began:.0f} s; " + ", ".join(f"{name} {len(new[name])}" for name in sorted(asked)),
                  flush=True)
            if all(new[name] for name in asked):
                break
        for name in parts:
            written[name] += new[name]
        windows.append({"bars": [start, stop], "attempts": attempt + 1, "input": text, "output": output})
    return {"parts": {name: sorted(notes) for name, notes in written.items() if notes}, "windows": windows}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", help="a plan under versions/, without .plan.json (jingle-bells/ai/strings)")
    parser.add_argument("out", type=Path)
    parser.add_argument("--ca2", type=Path, required=True, help="the release's Scripts/composers_assistant_v2")
    args = parser.parse_args()
    plan = json.loads((arrange.VERSIONS / f"{args.plan}.plan.json").read_text())
    arr = arrange.version_arranged(plan["version"])[0]
    model = Model(args.ca2)
    args.out.mkdir(parents=True, exist_ok=True)
    for seed in plan.get("takes", [1]):
        result = {"plan": args.plan, "version": plan["version"], "seed": seed,
                  "model": "Composer's Assistant 2 v2.1.0 (MIT), infill"} | take(model, plan, arr, seed)
        path = args.out / f"{Path(args.plan).name}-take{seed}.json"
        path.write_text(json.dumps(result, indent=1))
        print(f"{path}: " + ", ".join(f"{name} {len(notes)} notes" for name, notes in result["parts"].items()))


if __name__ == "__main__":
    main()
