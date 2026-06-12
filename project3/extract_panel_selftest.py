"""Verify extract_panel.py's span-finding + CV grouping + labels on the real panel
inputs — no GPU, no model download required (token-level checks optional).

Box runs are one-shot, so before any extraction we confirm for EVERY panel record:
  - meta.message is locatable in the user prompt, with non-empty leading and trailing
    spans (so question_mean / post_message_mean populate);
  - CV groups pair hit_NN with near_NN; both/form/none are singletons;
  - ask labels match the panel rule: YES iff (own-condition hit) or (both cell);
  - action expectations match: legal hits + both expect the legal flag, medical hits
    + both expect the medical flag, near/form/none expect neither.

Usage:
  ./.venv/bin/python extract_panel_selftest.py
  ./.venv/bin/python extract_panel_selftest.py --model Qwen/Qwen3-0.6B   # + token-level
"""

from __future__ import annotations

import argparse
import glob
import json
from collections import Counter

from extract_panel import DEFAULT_POSITIONS, build_prompt, locate_message, position_indices


def expected_ask_label(meta: dict) -> int:
    return 1 if ((meta["cell"] == "hit" and meta["doccond"] == meta["askcond"])
                 or meta["cell"] == "both") else 0


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
        if r["meta"]["framing"] == "panel_ask":
            if r["label"] != expected_ask_label(r["meta"]):
                errs.append(f"{r['id']}: ask label {r['label']} != expected")
        else:  # panel_action
            m = r["meta"]
            want_l = (m["cell"] == "hit" and m["doccond"] == "legal") or m["cell"] == "both"
            want_m = (m["cell"] == "hit" and m["doccond"] == "medical") or m["cell"] == "both"
            if m["expect_flag_legal"] != want_l or m["expect_flag_medical"] != want_m:
                errs.append(f"{r['id']}: action flag expectations wrong")
            if r["label"] != (1 if (want_l or want_m) else 0):
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
        if len(members) == 1 and members[0][1] in ("both", "form", "none"):
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

    files = sorted(glob.glob("inputs/panel_ask_*.json")) + ["inputs/panel_action.json"]
    if len(files) != 7:
        raise SystemExit(f"expected 7 panel input files, found {len(files)} — run make_panel.py first")

    total, all_errs = 0, []
    group_summary = None
    for f in files:
        records = json.loads(open(f).read())
        total += len(records)
        errs = char_checks(records) + group_checks(records)
        print(f"{f.split('/')[-1]:36s} {len(records):>4d} records  "
              f"{'OK' if not errs else f'{len(errs)} ERROR(S)'}")
        for e in errs[:8]:
            print(f"    - {e}")
        all_errs += errs
        if group_summary is None:
            group_summary = Counter(r["meta"]["pair_stem"] for r in records)

    paired = sum(1 for c in group_summary.values() if c == 2)
    singles = sum(1 for c in group_summary.values() if c == 1)
    print(f"\ngroups (per file): {paired} matched pairs (hit+near) + {singles} singletons "
          f"(both/form/none) = {len(group_summary)} CV groups over {sum(group_summary.values())} docs")

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

    print("\n" + ("ALL CHECKS PASS — extract_panel.py is span/group/label-ready for the box."
                  if not all_errs else f"{len(all_errs)} PROBLEM(S) — fix before extracting."))
    raise SystemExit(1 if all_errs else 0)


if __name__ == "__main__":
    main()
