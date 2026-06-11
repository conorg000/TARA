"""Verify extract_exp2.py's span-finding + CV grouping on the real keeper prompts — no GPU.

The box run is one-shot, so before it we confirm here that for EVERY keeper record:
  - meta.message is locatable in the user prompt (the failure mode that crashed the
    keyphrase extractor on Exp 2: wrong delimiter / missing span);
  - there is a non-empty leading span (question/instruction) before the message and a
    non-empty trailing span after it (so question_mean / post_message_mean are populated);
  - the CV group (meta.pair_stem) pairs hit_NN with near_NN and leaves form/none singletons;
  - labels are consistent with the cell × condition (hit of the asked/ruled condition = 1).

If a fast tokenizer for --model is reachable, it ALSO renders the chat prompt and resolves
every position via the extractor's own code (tokens_in_span / position_indices), proving the
token-level path — not just the char-level assumption. Offline, the char checks still gate.

Usage:
  ./.venv/bin/python extract_exp2_selftest.py
  ./.venv/bin/python extract_exp2_selftest.py --model Qwen/Qwen3-0.6B   # also token-level
"""

from __future__ import annotations

import argparse
import glob
import json
from collections import Counter

from extract_exp2 import DEFAULT_POSITIONS, build_prompt, locate_message, position_indices


def char_checks(records: list[dict]) -> list[str]:
    errs = []
    for r in records:
        msg = r["meta"]["message"]
        user = r["user"]
        i = user.rfind(msg)
        if i < 0:
            errs.append(f"{r['id']}: message not found in user prompt"); continue
        if i == 0:
            errs.append(f"{r['id']}: no leading span before message (question/instruction missing)")
        if i + len(msg) >= len(user):
            errs.append(f"{r['id']}: no trailing span after message")
        # label sanity
        cond_key = r["meta"].get("askcond") or r["meta"].get("rulecond")
        expect = 1 if (r["meta"]["cell"] == "hit" and r["meta"]["doccond"] == cond_key) else 0
        if r["label"] != expect:
            errs.append(f"{r['id']}: label {r['label']} != expected {expect}")
    return errs


def group_checks(records: list[dict]) -> list[str]:
    errs = []
    by_stem = {}
    for r in records:
        by_stem.setdefault(r["meta"]["pair_stem"], []).append((r["meta"]["doccond"], r["meta"]["cell"]))
    for stem, members in by_stem.items():
        cells = sorted(c for _, c in members)
        if cells == ["hit", "near"]:
            continue  # a matched pair — correct
        if len(members) == 1 and members[0][1] in ("form", "none"):
            continue  # singleton neutral — correct
        errs.append(f"group {stem}: unexpected membership {members}")
    return errs


def token_checks(records: list[dict], model: str) -> tuple[list[str], int]:
    """Render each prompt and resolve every position via the extractor's real code."""
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model, use_fast=True)
    if not tok.is_fast:
        return ["tokenizer is not fast (no offset mapping)"], 0
    errs, n = [], 0
    for r in records:
        prompt = build_prompt(tok, r["system"], r["user"])
        enc = tok(prompt, return_offsets_mapping=True)
        offsets = enc["offset_mapping"]
        seq_len = len(enc["input_ids"])
        try:
            m0, m1 = locate_message(prompt, r["meta"]["message"])
            pos = position_indices(offsets, seq_len, m0, m1)
        except Exception as e:
            errs.append(f"{r['id']}: {e}"); continue
        for p in DEFAULT_POSITIONS:
            if not pos.get(p):
                errs.append(f"{r['id']}: empty position {p}")
        n += 1
    return errs, n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=None, help="if set, also run token-level checks (downloads tokenizer)")
    args = ap.parse_args()

    files = sorted(glob.glob("inputs/exp2_keeper_*.json"))
    if not files:
        raise SystemExit("no inputs/exp2_keeper_*.json — run make_exp2_keeper.py first")

    total, all_errs = 0, []
    group_summary = None
    for f in files:
        records = json.loads(open(f).read())
        total += len(records)
        errs = char_checks(records) + group_checks(records)
        tag = "OK" if not errs else f"{len(errs)} ERROR(S)"
        print(f"{f.split('/')[-1]:40s} {len(records):>4d} records  {tag}")
        for e in errs[:8]:
            print(f"    - {e}")
        all_errs += errs
        if group_summary is None:
            group_summary = Counter(r["meta"]["pair_stem"] for r in records)

    # one representative file's group structure
    paired = sum(1 for s, c in group_summary.items() if c == 2)
    singles = sum(1 for s, c in group_summary.items() if c == 1)
    print(f"\ngroups (per ask file): {paired} matched pairs (hit+near) + {singles} neutral singletons "
          f"= {len(group_summary)} CV groups over {sum(group_summary.values())} docs")

    if args.model:
        print(f"\nToken-level checks with {args.model} ...")
        try:
            sample = json.loads(open(files[0]).read())[:12]
            terrs, n = token_checks(sample, args.model)
            print(f"  resolved all {len(DEFAULT_POSITIONS)} positions on {n} prompts"
                  + (f"  — {len(terrs)} ERROR(S)" if terrs else "  — OK"))
            for e in terrs[:8]:
                print(f"    - {e}")
            all_errs += terrs
        except Exception as e:
            print(f"  (skipped token-level: {type(e).__name__}: {e})")

    print("\n" + ("ALL CHECKS PASS — extract_exp2.py is span/group-ready for the box."
                  if not all_errs else f"{len(all_errs)} PROBLEM(S) — fix before extracting."))
    raise SystemExit(1 if all_errs else 0)


if __name__ == "__main__":
    main()
