"""GPU step (generation-only, NO activations): regenerate Exp 2 keeper behaviour for Move 1.

The Move-1 cross-tab (plan_move1_crosstab.md) needs the per-document greedy behaviour of
the Exp 2 keeper: FLAG/NOFLAG under each rule (the 2 action passes) and YES/NO per ask
paraphrase (the 6 ask passes, for the consistency-filtered ask-label column). That record
lived in the extraction npz `behaviour` arrays, which stayed on the Exp 2 GPU box; this
script regenerates it WITHOUT activation capture — minutes of GPU, not hours.

Fidelity to the original run (extract_exp2.py, by construction):
  - identical prompt build (imported from extract_exp2: same chat template, /no_think)
  - identical greedy decoding (do_sample=False) and max_new_tokens (256 action / 32 ask)
  - identical behaviour parsing (markers.classify / markers.flag_action, no watchlist arg)
  - one-document-at-a-time generation (no batching/padding => deterministic parity)

OpenRouter is NOT an acceptable substitute here: the cross-tab is a verification claim and
the standing rule is greedy-on-GPU is the truth (OpenRouter routing wobble over-counts).

Usage (GPU box, one pass):
    python crosstab_behaviour_gpu.py --model Qwen/Qwen3-32B \
        --dataset inputs/exp2_keeper_action_legal.json \
        --out acts/crosstab_beh_action_legal.json
All 8 passes: bash run_crosstab_behaviour.sh
CPU dry-run (tiny model, 4 items — plumbing only, numbers are meaningless):
    python crosstab_behaviour_gpu.py --model Qwen/Qwen3-0.6B --device cpu \
        --dtype float32 --dataset inputs/exp2_keeper_action_legal.json \
        --out /tmp/ct_dry.json --max-examples 4
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from extract_exp2 import ACTION_FRAMINGS, RECOG_FRAMINGS, build_prompt, git_commit
from markers import classify, flag_action


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="Qwen/Qwen3-32B")
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--out", required=True, help="output behaviour JSON")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16", choices=["bfloat16", "float16", "float32"])
    ap.add_argument("--max-examples", type=int, default=None)
    ap.add_argument("--max-new-tokens", type=int, default=None, help="override (default 256 action / 32 ask)")
    args = ap.parse_args()

    records = json.loads(Path(args.dataset).read_text())
    if args.max_examples:
        records = records[: args.max_examples]
    framing = records[0]["meta"]["framing"]
    if any(r["meta"]["framing"] != framing for r in records):
        raise SystemExit("dataset mixes framings; one framing per file")
    if framing not in RECOG_FRAMINGS | ACTION_FRAMINGS:
        raise SystemExit(f"unknown framing {framing!r}")
    is_action = framing in ACTION_FRAMINGS
    max_new = args.max_new_tokens or (256 if is_action else 32)

    commit, created = git_commit(), datetime.now(timezone.utc).isoformat()
    print(f"code: git {commit} | {created} | dataset={args.dataset} | framing={framing} | generation-only")

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dtype = {"bfloat16": torch.bfloat16, "float16": torch.float16, "float32": torch.float32}[args.dtype]
    print(f"Loading {args.model} ({args.dtype}) on {args.device} ...")
    tokenizer = AutoTokenizer.from_pretrained(args.model, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)
    model.to(args.device).eval()
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    out_records = []
    n_trunc = 0
    for k, r in enumerate(records):
        prompt = build_prompt(tokenizer, r["system"], r["user"])
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        seq_len = inputs["input_ids"].shape[1]
        with torch.no_grad():
            gen = model.generate(**inputs, max_new_tokens=max_new, do_sample=False,
                                 pad_token_id=tokenizer.pad_token_id)
        new = gen[0][seq_len:]
        truncated = bool(len(new) >= max_new and int(new[-1]) != tokenizer.eos_token_id)
        n_trunc += truncated
        gen_text = tokenizer.decode(new, skip_special_tokens=True).strip()
        beh = ("FLAG" if flag_action(gen_text) else "NOFLAG") if is_action else classify(gen_text, "YES", "NO")

        m = r["meta"]
        rec = dict(id=r["id"], label=int(r["label"]), cell=m["cell"], doccond=m["doccond"],
                   pair_stem=m["pair_stem"], behaviour=beh, truncated=truncated,
                   generated_text=gen_text)
        for key in ("rulecond", "askcond", "paraphrase"):
            if key in m:
                rec[key] = m[key]
        out_records.append(rec)
        print(f"[{k+1}/{len(records)}] {r['id']} beh={beh}{' TRUNC' if truncated else ''}")

    out = dict(
        meta=dict(model=args.model, dtype=args.dtype, git_commit=commit, created_utc=created,
                  dataset_path=args.dataset, framing=framing, num_examples=len(records),
                  max_new_tokens=max_new, no_think=True, generation_only=True,
                  decode="greedy do_sample=False, one doc at a time (parity with extract_exp2.py)"),
        records=out_records,
    )
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=1))
    if is_action:
        flags = sum(r["behaviour"] == "FLAG" for r in out_records)
        print(f"behaviour: FLAG {flags} / NOFLAG {len(out_records) - flags}")
    else:
        yes = sum(r["behaviour"] == "YES" for r in out_records)
        unc = sum(r["behaviour"] == "UNCLEAR" for r in out_records)
        print(f"behaviour: YES {yes} / NO {len(out_records) - yes - unc} / UNCLEAR {unc}")
    if n_trunc:
        print(f"WARNING: {n_trunc}/{len(out_records)} generations hit the {max_new}-token cap without EOS")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
