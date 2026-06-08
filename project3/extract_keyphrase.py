"""GPU step: dump residual-stream activations for the KEYPHRASE probe (v4).

Differs from extract_activations.py (the category-track extractor) in three ways that the
keyphrase probe needs:

1. MULTIPLE read positions, not just the final prompt token. In one forward pass we record,
   for every layer, the residual stream at:
     - final    : last prompt token (pre-generation) — the canonical, cross-pass-matched read.
     - name_last: last token of the watchlist NAME where it sits in the document — the trigger
                  locus, least contaminated by the downstream task, plausibly most transferable.
     - doc_last : last token of the document body.
     - doc_mean : mean over the document-body tokens (position-free, robust).
   We pick the best position x layer later on CPU; we only get one shot on the box, so we
   over-capture positions (cheap in the same forward pass) rather than re-run.

2. FRAMING-AWARE behaviour grading, re-derived locally (deterministic greedy) so recognition
   and action come from the SAME model build as the activations:
     - recognition framings (ask/loadedask/plainask/swapwl): grade [YES]/[NO] (markers.classify)
     - action framings (action/checkaction): grade FLAG via markers.flag_action(text, watchlist)

3. groups = the matched-PAIR stem (id minus trailing a/b/s) so train_probe --split-mode group
   and cross_pass_probe --split-mode pair keep a pair's two halves in the same CV fold.

Output: one .npz per position, named <out-prefix>__<position>.npz, each with the SAME schema
extract_activations.py uses (activations [N, L+1, D], labels, ids, groups, behaviour,
generated_text, meta) so train_probe.py / cross_pass_probe.py consume them unchanged. Plus
`terms`, `watchlists` (JSON), and the located token indices for auditing.

Usage (on the box):
    python extract_keyphrase.py --model Qwen/Qwen3-32B \
        --dataset inputs/watchlist_v4_ask.json --out-prefix acts/v4_ask
CPU dry-run (tiny model, a few items — verifies the whole path incl. span-finding):
    python extract_keyphrase.py --model Qwen/Qwen3-0.6B --device cpu --dtype float32 \
        --dataset inputs/watchlist_v4_ask.json --out-prefix /tmp/smoke_v4_ask --max-examples 4
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from markers import classify, flag_action

RECOG_FRAMINGS = {"ask", "loadedask", "plainask", "swapwl"}
ACTION_FRAMINGS = {"action", "checkaction"}
DEFAULT_POSITIONS = ["final", "name_last", "doc_last", "doc_mean"]


def git_commit() -> str:
    import subprocess
    here = Path(__file__).resolve().parent
    try:
        sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=here,
                                      stderr=subprocess.DEVNULL).decode().strip()
        dirty = subprocess.call(["git", "diff", "--quiet", "HEAD"], cwd=here,
                                stderr=subprocess.DEVNULL) != 0
        return f"{sha}{'-dirty' if dirty else ''}"
    except Exception:
        return "unknown"


def build_prompt(tokenizer, system: str, user: str) -> str:
    """Render the chat prompt, no-think regime, with the assistant generation header.
    `/no_think` matches the behavioural gate's system suffix; enable_thinking=False keeps the
    Qwen3 template from adding a think opener, so the final token is the clean generation
    position."""
    messages = [{"role": "system", "content": system + " /no_think"},
                {"role": "user", "content": user}]
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True,
                                         enable_thinking=False)


def doc_of(record: dict) -> str:
    """The document body (no framing tail), as it appears verbatim in the prompt."""
    if record["meta"].get("doc"):
        return record["meta"]["doc"]
    return record["user"].split("Document:\n", 1)[1].split("\n\n", 1)[0]


def tokens_in_span(offsets, start: int, end: int) -> list[int]:
    """Indices of tokens whose character span [o0,o1) overlaps [start,end). Special tokens
    (offset (0,0)) have zero width and never overlap a positive span."""
    out = []
    for i, (o0, o1) in enumerate(offsets):
        if o1 > o0 and o0 < end and o1 > start:
            out.append(i)
    return out


def locate(prompt: str, offsets, doc_body: str, term: str) -> tuple[list[int], list[int]]:
    """Token indices of (document body, trigger name). The name is searched WITHIN the
    document span so we never pick up the same name where it appears in the system watchlist."""
    d0 = prompt.rfind(doc_body)
    if d0 < 0:
        raise ValueError(f"document body not found in prompt: {doc_body[:60]!r}...")
    d1 = d0 + len(doc_body)
    n0 = prompt.find(term, d0, d1)
    if n0 < 0:
        raise ValueError(f"term {term!r} not found inside the document span")
    doc_tok = tokens_in_span(offsets, d0, d1)
    name_tok = tokens_in_span(offsets, n0, n0 + len(term))
    if not doc_tok or not name_tok:
        raise ValueError("empty token span (tokenizer offset mismatch?)")
    return doc_tok, name_tok


def position_indices(seq_len: int, doc_tok: list[int], name_tok: list[int]) -> dict:
    """Map each named position to the token index/indices it reads."""
    return {
        "final": [seq_len - 1],
        "name_last": [name_tok[-1]],
        "doc_last": [doc_tok[-1]],
        "doc_mean": doc_tok,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="Qwen/Qwen3-32B")
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--out-prefix", required=True, help="writes <prefix>__<position>.npz")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16", choices=["bfloat16", "float16", "float32"])
    ap.add_argument("--positions", default=",".join(DEFAULT_POSITIONS))
    ap.add_argument("--max-examples", type=int, default=None)
    ap.add_argument("--no-generate", action="store_true", help="skip behaviour grading (activations only)")
    ap.add_argument("--max-new-tokens", type=int, default=None, help="override (default 8 recog / 320 action)")
    args = ap.parse_args()

    positions = args.positions.split(",")
    bad = set(positions) - set(DEFAULT_POSITIONS)
    if bad:
        raise SystemExit(f"unknown positions {bad}; choose from {DEFAULT_POSITIONS}")

    records = json.loads(Path(args.dataset).read_text())
    if args.max_examples:
        records = records[: args.max_examples]
    framing = records[0]["meta"]["framing"]
    if any(r["meta"]["framing"] != framing for r in records):
        raise SystemExit("dataset mixes framings; extract one framing per file")
    is_action = framing in ACTION_FRAMINGS
    if framing not in RECOG_FRAMINGS | ACTION_FRAMINGS:
        raise SystemExit(f"unknown framing {framing!r}")
    max_new = args.max_new_tokens or (320 if is_action else 8)

    commit, created = git_commit(), datetime.now(timezone.utc).isoformat()
    print(f"code: git {commit} | {created} | dataset={args.dataset} | framing={framing} | positions={positions}")

    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dtype = {"bfloat16": torch.bfloat16, "float16": torch.float16, "float32": torch.float32}[args.dtype]
    print(f"Loading {args.model} ({args.dtype}) on {args.device} ...")
    tokenizer = AutoTokenizer.from_pretrained(args.model, use_fast=True)
    if not tokenizer.is_fast:
        raise SystemExit("need a fast tokenizer for offset mapping (token-position location)")
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=dtype)
    model.to(args.device).eval()
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    # accumulators: per position -> list of [L, D]; plus shared metadata columns
    acc = {p: [] for p in positions}
    labels, ids, groups, behaviour, generated, terms, wls = [], [], [], [], [], [], []
    nameidx, docidx, seqlens = [], [], []

    for k, r in enumerate(records):
        prompt = build_prompt(tokenizer, r["system"], r["user"])
        enc = tokenizer(prompt, return_tensors="pt", return_offsets_mapping=True)
        offsets = enc.pop("offset_mapping")[0].tolist()
        inputs = {kk: vv.to(model.device) for kk, vv in enc.items()}
        seq_len = inputs["input_ids"].shape[1]

        term = r["meta"]["term"]
        doc_tok, name_tok = locate(prompt, offsets, doc_of(r), term)
        posidx = position_indices(seq_len, doc_tok, name_tok)

        with torch.no_grad():
            out = model(**inputs, output_hidden_states=True, use_cache=False)
        # hidden_states: tuple (L+1) of [1, seq, D]
        for p in positions:
            idx = posidx[p]
            # mean over the position's token(s) at each layer -> [L+1, D]
            vec = np.stack([hs[0, idx, :].float().mean(0).cpu().numpy() for hs in out.hidden_states], axis=0)
            acc[p].append(vec)

        ans = ""
        gen_text = ""
        if not args.no_generate:
            with torch.no_grad():
                gen = model.generate(**inputs, max_new_tokens=max_new, do_sample=False,
                                     pad_token_id=tokenizer.pad_token_id)
            gen_text = tokenizer.decode(gen[0][seq_len:], skip_special_tokens=True).strip()
            if is_action:
                ans = "FLAG" if flag_action(gen_text, r["meta"]["watchlist"]) else "NOFLAG"
            else:
                ans = classify(gen_text, "YES", "NO")

        labels.append(int(r["label"])); ids.append(r["id"])
        groups.append(r["id"][:-1])  # matched-pair stem (w4_0000a/b/s -> w4_0000)
        behaviour.append(ans); generated.append(gen_text)
        terms.append(term); wls.append(json.dumps(r["meta"]["watchlist"]))
        nameidx.append(name_tok[-1]); docidx.append(doc_tok[-1]); seqlens.append(seq_len)
        print(f"[{k+1}/{len(records)}] {r['id']} gt={r['label_name']:>8} {('beh='+ans) if ans else ''} "
              f"seq={seq_len} name_tok={name_tok[-1]} doc_tok={doc_tok[-1]}")

    meta = {
        "model": args.model, "dtype": args.dtype, "git_commit": commit, "created_utc": created,
        "torch_version": torch.__version__, "transformers_version": transformers.__version__,
        "dataset_path": args.dataset, "framing": framing, "num_examples": len(records),
        "no_think": True, "generate": not args.no_generate, "max_new_tokens": max_new,
        "groups_note": "matched-pair stem (id minus trailing a/b/s) for pair-disjoint CV",
        "sample_prompt": build_prompt(tokenizer, records[0]["system"], records[0]["user"]),
    }
    common = dict(
        labels=np.array(labels, dtype=np.int8), ids=np.array(ids), groups=np.array(groups),
        behaviour=np.array(behaviour), generated_text=np.array(generated),
        terms=np.array(terms), watchlists=np.array(wls),
        name_token=np.array(nameidx), doc_token=np.array(docidx), seq_len=np.array(seqlens),
    )
    for p in positions:
        activations = np.stack(acc[p], axis=0).astype(np.float32)  # [N, L+1, D]
        m = {**meta, "position": p, "num_transformer_layers": activations.shape[1] - 1,
             "hidden_dim": activations.shape[2],
             "token_position": {
                 "final": "last prompt token (pre-generation)",
                 "name_last": "last token of the watchlist name in the document",
                 "doc_last": "last token of the document body",
                 "doc_mean": "mean over document-body tokens",
             }[p]}
        out_path = f"{args.out_prefix}__{p}.npz"
        np.savez(out_path, activations=activations, meta=json.dumps(m), **common)
        print(f"saved {out_path}  activations={activations.shape}")

    if not args.no_generate:
        if is_action:
            print(f"behaviour: FLAG {behaviour.count('FLAG')} / NOFLAG {behaviour.count('NOFLAG')}")
        else:
            corr = sum((b == "YES") == (l == 1) for b, l in zip(behaviour, labels))
            print(f"behaviour: YES {behaviour.count('YES')} / NO {behaviour.count('NO')} / "
                  f"UNCLEAR {behaviour.count('UNCLEAR')} | acc vs label {corr/len(labels):.3f}")


if __name__ == "__main__":
    main()
