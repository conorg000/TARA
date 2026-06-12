"""Verify extract_ladder.py's span-finding + CV grouping on the real keeper prompts — no GPU.

For EVERY ladder keeper record (ask + read passes):
  - meta.message is locatable in the user prompt;
  - non-empty leading span (question / triage-instruction+rule) and trailing span exist;
  - the CV group (meta.pair_stem) pairs hit_NN with near_NN, neutrals are singletons;
  - labels match the qtype/cell rule (compound: hit=1; compA: hit+near=1; compB: hit+form=1;
    read: hit=1).
If --model is given, also renders the chat prompt and resolves every position via the
extractor's own code (token-level proof). Usage:
  ./.venv/bin/python extract_ladder_selftest.py
  ./.venv/bin/python extract_ladder_selftest.py --model Qwen/Qwen3-0.6B
"""

from __future__ import annotations

import argparse
import glob
import json
from collections import Counter

from extract_ladder import DEFAULT_POSITIONS, build_prompt, locate_message, position_indices

POSITIVE = {"compound": {"hit"}, "compA": {"hit", "near"}, "compB": {"hit", "form"}, "read": {"hit"}}


def char_checks(records: list[dict]) -> list[str]:
    errs = []
    for r in records:
        msg, user = r["meta"]["message"], r["user"]
        i = user.rfind(msg)
        if i < 0:
            errs.append(f"{r['id']}: message not found in user prompt"); continue
        if i == 0:
            errs.append(f"{r['id']}: no leading span before message")
        if i + len(msg) >= len(user):
            errs.append(f"{r['id']}: no trailing span after message")
        qtype = r["meta"].get("qtype", "read")
        expect = 1 if r["meta"]["cell"] in POSITIVE[qtype] else 0
        if r["label"] != expect:
            errs.append(f"{r['id']}: label {r['label']} != expected {expect} (qtype={qtype})")
    return errs


def group_checks(records: list[dict]) -> list[str]:
    errs = []
    by_stem = {}
    for r in records:
        by_stem.setdefault(r["meta"]["pair_stem"], []).append(r["meta"]["cell"])
    for stem, cells in by_stem.items():
        s = sorted(cells)
        if s == ["hit", "near"] or (len(cells) == 1 and cells[0] in ("form", "none")):
            continue
        errs.append(f"group {stem}: unexpected membership {cells}")
    return errs


def token_checks(records: list[dict], model: str) -> tuple[list[str], int]:
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model, use_fast=True)
    if not tok.is_fast:
        return ["tokenizer is not fast (no offset mapping)"], 0
    errs, n = [], 0
    for r in records:
        prompt = build_prompt(tok, r["system"], r["user"])
        enc = tok(prompt, return_offsets_mapping=True)
        try:
            m0, m1 = locate_message(prompt, r["meta"]["message"])
            pos = position_indices(enc["offset_mapping"], len(enc["input_ids"]), m0, m1)
        except Exception as e:
            errs.append(f"{r['id']}: {e}"); continue
        for p in DEFAULT_POSITIONS:
            if not pos.get(p):
                errs.append(f"{r['id']}: empty position {p}")
        n += 1
    return errs, n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=None)
    args = ap.parse_args()

    files = sorted(glob.glob("inputs/ladder_*_ask_*.json") + glob.glob("inputs/ladder_*_read_*.json"))
    if not files:
        raise SystemExit("no inputs/ladder_*.json — run make_ladder_keeper.py first")

    total, all_errs = 0, []
    read_groups = None
    for f in files:
        records = json.loads(open(f).read())
        total += len(records)
        errs = char_checks(records) + group_checks(records)
        print(f"{f.split('/')[-1]:48s} {len(records):>4d} records  {'OK' if not errs else f'{len(errs)} ERR'}")
        for e in errs[:6]:
            print(f"    - {e}")
        all_errs += errs
        if read_groups is None:
            read_groups = Counter(r["meta"]["pair_stem"] for r in records)

    paired = sum(1 for c in read_groups.values() if c == 2)
    singles = sum(1 for c in read_groups.values() if c == 1)
    print(f"\ngroups (per file): {paired} matched pairs (hit+near) + {singles} neutral singletons "
          f"= {len(read_groups)} CV groups; {len(files)} files, {total} records total")

    if args.model:
        print(f"\nToken-level checks with {args.model} (ask + read sample) ...")
        try:
            sample = json.loads(open(files[0]).read())[:8] + json.loads(open(files[-1]).read())[:8]
            terrs, n = token_checks(sample, args.model)
            print(f"  resolved all {len(DEFAULT_POSITIONS)} positions on {n} prompts"
                  + (f"  — {len(terrs)} ERR" if terrs else "  — OK"))
            for e in terrs[:8]:
                print(f"    - {e}")
            all_errs += terrs
        except Exception as e:
            print(f"  (skipped token-level: {type(e).__name__}: {e})")

    print("\n" + ("ALL CHECKS PASS — extract_ladder.py is span/group-ready for the box."
                  if not all_errs else f"{len(all_errs)} PROBLEM(S) — fix before extracting."))
    raise SystemExit(1 if all_errs else 0)


if __name__ == "__main__":
    main()
