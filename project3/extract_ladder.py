"""GPU step: dump residual-stream activations for MOVE 4 (the spontaneity ladder).

The Exp-2 extractor with a new dataset axis (plan_move4_spontaneity_ladder.md). Two
framings, identical position machinery to extract_exp2.py:
  ladder_ask   -> [YES]/[NO]   (the compound/component question supplies the condition;
                  greedy answers are the probe's TRAINING LABELS) — RECOG framing.
  ladder_read  -> FLAG or not  (a neutral triage task + a standing rule; NO question — the
                  PURE-READING pass where the finding lives) — ACTION framing.

The decisive read is hit-vs-near (A and B vs A and not B) WITHIN each read arm
(present = compound rule; absent = placebo rule), scored by the ask-trained compound
direction cross-pass, document-disjoint (pair_stem groups hit_NN with near_NN).

Per-doc meta carried into the npz for the probe to slice: candidate, rung, family, cell,
qtype (compound/compA/compB/read), arm (present/absent/""), pair_stem, message. Output
schema matches extract_exp2 / keyphrase (<prefix>__<position>.npz) so the probe consumes
it unchanged.

Usage (box):
    python extract_ladder.py --model Qwen/Qwen3-32B \
        --dataset inputs/ladder_refund_over_500_ask_compound_p1.json \
        --out-prefix acts/ladder_refund_over_500_ask_compound_p1
CPU dry-run:
    python extract_ladder.py --model Qwen/Qwen3-0.6B --device cpu --dtype float32 \
        --dataset inputs/ladder_refund_over_500_read_present.json --out-prefix /tmp/smoke --max-examples 4
Span-finding/grouping is checked WITHOUT a model by extract_ladder_selftest.py.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from markers import classify, flag_action

RECOG_FRAMINGS = {"ladder_ask"}
ACTION_FRAMINGS = {"ladder_read"}

DEFAULT_POSITIONS = [
    "message_mean", "message_first", "message_last", "final",
    "question_mean", "pre_message_final", "post_message_mean",
]
GEN_POSITIONS = ["gen_first", "gen_prefix_mean"]
GEN_PREFIX_K = 16

POS_DESC = {
    "message_mean": "mean over message-body tokens (primary)",
    "message_first": "first message token (message onset)",
    "message_last": "last message token (recognition likely crystallizes here)",
    "final": "last prompt token (pre-generation; decision-adjacent)",
    "question_mean": "leading span before the message (ask question / triage instruction + rule)",
    "pre_message_final": "last token before the message — positional negative control (~0.5 expected)",
    "post_message_mean": "span after the message (the response-instruction tail)",
    "gen_first": "first generated token (2nd forward over prompt+generation)",
    "gen_prefix_mean": f"mean over the first {GEN_PREFIX_K} generated tokens (where FLAG forms)",
}


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
    messages = [{"role": "system", "content": system + " /no_think"},
                {"role": "user", "content": user}]
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True,
                                         enable_thinking=False)


def tokens_in_span(offsets, start: int, end: int) -> list[int]:
    return [i for i, (o0, o1) in enumerate(offsets) if o1 > o0 and o0 < end and o1 > start]


def locate_message(prompt: str, message: str) -> tuple[int, int]:
    m0 = prompt.rfind(message)
    if m0 < 0:
        raise ValueError(f"message body not found in prompt: {message[:60]!r}...")
    return m0, m0 + len(message)


def position_indices(offsets, seq_len: int, m0: int, m1: int) -> dict:
    msg_tok = tokens_in_span(offsets, m0, m1)
    if not msg_tok:
        raise ValueError("empty message token span (offset mismatch?)")
    mfirst, mlast = msg_tok[0], msg_tok[-1]
    lead_tok = [i for i, (o0, o1) in enumerate(offsets) if o1 > o0 and o1 <= m0] or [mfirst]
    post_tok = [i for i, (o0, o1) in enumerate(offsets)
                if o1 > o0 and o0 >= m1 and i < seq_len - 1] or [seq_len - 1]
    return {
        "message_mean": msg_tok, "message_first": [mfirst], "message_last": [mlast],
        "final": [seq_len - 1], "question_mean": lead_tok,
        "pre_message_final": [max(0, mfirst - 1)], "post_message_mean": post_tok,
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
    ap.add_argument("--no-generate", action="store_true")
    ap.add_argument("--no-gen-prefix", action="store_true")
    ap.add_argument("--save-dtype", default="float16", choices=["float16", "float32"])
    ap.add_argument("--max-new-tokens", type=int, default=None, help="override (default 32 ask / 256 read)")
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
    if framing not in RECOG_FRAMINGS | ACTION_FRAMINGS:
        raise SystemExit(f"unknown framing {framing!r}")
    is_action = framing in ACTION_FRAMINGS
    max_new = args.max_new_tokens or (256 if is_action else 32)

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

    gen_capture = is_action and not args.no_generate and not args.no_gen_prefix
    save_np = np.float16 if args.save_dtype == "float16" else np.float32
    acc = {p: [] for p in positions}
    if gen_capture:
        acc.update({p: [] for p in GEN_POSITIONS})
    print(f"positions: prefill={positions}" + (f" + gen={GEN_POSITIONS}" if gen_capture else "")
          + f" | save_dtype={args.save_dtype}")
    labels, ids, groups, behaviour, generated = [], [], [], [], []
    doccond, cell, candidate, qtype, arm = [], [], [], [], []
    msgidx, seqlens = [], []
    n_trunc = 0

    for k, r in enumerate(records):
        prompt = build_prompt(tokenizer, r["system"], r["user"])
        enc = tokenizer(prompt, return_tensors="pt", return_offsets_mapping=True)
        offsets = enc.pop("offset_mapping")[0].tolist()
        inputs = {kk: vv.to(model.device) for kk, vv in enc.items()}
        seq_len = inputs["input_ids"].shape[1]

        m0, m1 = locate_message(prompt, r["meta"]["message"])
        posidx = position_indices(offsets, seq_len, m0, m1)

        with torch.no_grad():
            out = model(**inputs, output_hidden_states=True, use_cache=False)
        for p in positions:
            idx = posidx[p]
            vec = np.stack([hs[0, idx, :].float().mean(0).cpu().numpy() for hs in out.hidden_states], axis=0)
            acc[p].append(vec)

        ans, gen_text = "", ""
        if not args.no_generate:
            with torch.no_grad():
                gen = model.generate(**inputs, max_new_tokens=max_new, do_sample=False,
                                     pad_token_id=tokenizer.pad_token_id)
            new = gen[0][seq_len:]
            if len(new) >= max_new and int(new[-1]) != tokenizer.eos_token_id:
                n_trunc += 1
            gen_text = tokenizer.decode(new, skip_special_tokens=True).strip()
            ans = ("FLAG" if flag_action(gen_text) else "NOFLAG") if is_action else classify(gen_text, "YES", "NO")

        if gen_capture:
            if len(new) > 0:
                kk = min(GEN_PREFIX_K, len(new))
                ext = gen[:, : seq_len + kk]
                with torch.no_grad():
                    out2 = model(input_ids=ext, output_hidden_states=True, use_cache=False)
                gpos = list(range(seq_len, seq_len + kk))
                acc["gen_first"].append(
                    np.stack([hs[0, seq_len, :].float().cpu().numpy() for hs in out2.hidden_states], axis=0))
                acc["gen_prefix_mean"].append(
                    np.stack([hs[0, gpos, :].float().mean(0).cpu().numpy() for hs in out2.hidden_states], axis=0))
            else:
                z = np.stack([hs[0, seq_len - 1, :].float().cpu().numpy() for hs in out.hidden_states], axis=0)
                acc["gen_first"].append(z); acc["gen_prefix_mean"].append(z)

        m = r["meta"]
        labels.append(int(r["label"])); ids.append(r["id"]); groups.append(m["pair_stem"])
        behaviour.append(ans); generated.append(gen_text)
        doccond.append(m["doccond"]); cell.append(m["cell"]); candidate.append(m["candidate"])
        qtype.append(m.get("qtype", "")); arm.append(m.get("arm", ""))
        msgidx.append(posidx["message_last"][0]); seqlens.append(seq_len)
        print(f"[{k+1}/{len(records)}] {r['id']} gt={r['label_name']:>8} {('beh='+ans) if ans else ''} "
              f"seq={seq_len} group={m['pair_stem']}")

    meta = {
        "model": args.model, "dtype": args.dtype, "git_commit": commit, "created_utc": created,
        "torch_version": torch.__version__, "transformers_version": transformers.__version__,
        "dataset_path": args.dataset, "framing": framing, "num_examples": len(records),
        "no_think": True, "generate": not args.no_generate, "max_new_tokens": max_new,
        "save_dtype": args.save_dtype, "gen_prefix": gen_capture, "gen_prefix_k": GEN_PREFIX_K,
        "groups_note": "meta.pair_stem (hit_NN + near_NN share a stem) for pair-disjoint CV",
        "candidate": records[0]["meta"]["candidate"], "rung": records[0]["meta"]["rung"],
        "family": records[0]["meta"]["family"],
        "sample_prompt": build_prompt(tokenizer, records[0]["system"], records[0]["user"]),
    }
    common = dict(
        labels=np.array(labels, dtype=np.int8), ids=np.array(ids), groups=np.array(groups),
        behaviour=np.array(behaviour), generated_text=np.array(generated),
        doccond=np.array(doccond), cell=np.array(cell), candidate=np.array(candidate),
        qtype=np.array(qtype), arm=np.array(arm),
        message_token=np.array(msgidx), seq_len=np.array(seqlens),
    )
    for p in acc:
        activations = np.stack(acc[p], axis=0).astype(save_np)
        m = {**meta, "position": p, "num_transformer_layers": activations.shape[1] - 1,
             "hidden_dim": activations.shape[2], "token_position": POS_DESC.get(p, p)}
        out_path = f"{args.out_prefix}__{p}.npz"
        np.savez(out_path, activations=activations, meta=json.dumps(m), **common)
        print(f"saved {out_path}  activations={activations.shape} {activations.dtype}")

    if not args.no_generate:
        if n_trunc:
            print(f"WARNING: {n_trunc}/{len(records)} generations hit the {max_new}-token cap without EOS.")
        if is_action:
            print(f"behaviour: FLAG {behaviour.count('FLAG')} / NOFLAG {behaviour.count('NOFLAG')}")
        else:
            corr = sum((b == "YES") == (l == 1) for b, l in zip(behaviour, labels))
            print(f"behaviour: YES {behaviour.count('YES')} / NO {behaviour.count('NO')} / "
                  f"UNCLEAR {behaviour.count('UNCLEAR')} | acc vs label {corr/len(labels):.3f}")


if __name__ == "__main__":
    main()
