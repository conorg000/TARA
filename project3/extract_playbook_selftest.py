"""Verify extract_playbook.py's span-finding + CV grouping + labels on the real playbook
inputs — no GPU (token-level checks optional with --model).

For EVERY record: meta.message locatable with non-empty leading+trailing spans; CV groups
pair hit_NN with near_NN (form/none singletons); ask label = YES iff own-condition hit;
action label = 1 iff any condition's flag expected, and expect_flags matches the cell.

Usage:
  ./.venv/bin/python extract_playbook_selftest.py
  ./.venv/bin/python extract_playbook_selftest.py --model Qwen/Qwen3-0.6B   # + token-level
"""

from __future__ import annotations

import argparse
import glob
import json
from collections import Counter

from extract_playbook import DEFAULT_POSITIONS, build_prompt, locate_message, position_indices


def char_checks(records: list[dict]) -> list[str]:
    errs = []
    for r in records:
        m = r["meta"]
        msg, user = m["message"], r["user"]
        i = user.rfind(msg)
        if i < 0:
            errs.append(f"{r['id']}: message not found in user prompt"); continue
        if i == 0:
            errs.append(f"{r['id']}: no leading span before message")
        if i + len(msg) >= len(user):
            errs.append(f"{r['id']}: no trailing span after message")
        if m["framing"] == "playbook_ask":
            want = 1 if (m["cell"] == "hit" and m["doccond"] == m["askcond"]) else 0
            if r["label"] != want:
                errs.append(f"{r['id']}: ask label {r['label']} != expected {want}")
        else:  # playbook_action
            expect = m["expect_flags"]
            for c, v in expect.items():
                want_c = (m["cell"] == "hit" and m["doccond"] == c)
                if v != want_c:
                    errs.append(f"{r['id']}: action expect_flags[{c}]={v} != {want_c}")
            if r["label"] != (1 if any(expect.values()) else 0):
                errs.append(f"{r['id']}: action label {r['label']} != expected")
    return errs


def group_checks(records: list[dict]) -> list[str]:
    errs = []
    by_stem: dict[str, list] = {}
    for r in records:
        by_stem.setdefault(r["meta"]["pair_stem"], []).append((r["meta"]["doccond"], r["meta"]["cell"]))
    for stem, members in by_stem.items():
        cells = sorted(c for _, c in members)
        if cells == ["hit", "near"]:
            continue
        if len(members) == 1 and members[0][1] in ("form", "none"):
            continue
        errs.append(f"group {stem}: unexpected membership {members}")
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
        offsets, seq_len = enc["offset_mapping"], len(enc["input_ids"])
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
    ap.add_argument("--model", default=None, help="if set, also run token-level checks")
    args = ap.parse_args()

    files = sorted(glob.glob("inputs/playbook_ask_*.json")) + ["inputs/playbook_action.json"]
    n_ask = len(glob.glob("inputs/playbook_ask_*.json"))
    if n_ask % 3 != 0 or n_ask == 0:
        raise SystemExit(f"expected 3*N ask files, found {n_ask} — run make_playbook_keeper.py first")

    total, all_errs, group_summary = 0, [], None
    for f in files:
        records = json.loads(open(f).read())
        total += len(records)
        errs = char_checks(records) + group_checks(records)
        print(f"{f.split('/')[-1]:42s} {len(records):>4d} records  "
              f"{'OK' if not errs else f'{len(errs)} ERROR(S)'}")
        for e in errs[:8]:
            print(f"    - {e}")
        all_errs += errs
        if group_summary is None:
            group_summary = Counter(r["meta"]["pair_stem"] for r in records)

    paired = sum(1 for c in group_summary.values() if c == 2)
    singles = sum(1 for c in group_summary.values() if c == 1)
    print(f"\ngroups (per file): {paired} matched pairs (hit+near) + {singles} singletons "
          f"(form/none) = {len(group_summary)} CV groups over {sum(group_summary.values())} docs")
    print(f"ask files: {n_ask} ({n_ask // 3} conditions x 3 paraphrases) + 1 action")

    if args.model:
        print(f"\nToken-level checks with {args.model} ...")
        try:
            sample = json.loads(open(files[0]).read())[:12]
            terrs, n = token_checks(sample, args.model)
            print(f"  resolved all {len(DEFAULT_POSITIONS)} positions on {n} prompts"
                  + (f"  — {len(terrs)} ERROR(S)" if terrs else "  — OK"))
            all_errs += terrs
        except Exception as e:
            print(f"  (skipped token-level: {type(e).__name__}: {e})")

    print("\n" + ("ALL CHECKS PASS — extract_playbook.py is span/group/label-ready for the box."
                  if not all_errs else f"{len(all_errs)} PROBLEM(S) — fix before extracting."))
    raise SystemExit(1 if all_errs else 0)


if __name__ == "__main__":
    main()
