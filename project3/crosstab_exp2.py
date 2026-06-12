"""CPU step: the Move-1 cross-tab — was Exp 2's flagging genuinely rule-dependent per-document?

Plan: plan_move1_crosstab.md. The summary's "binding lives on the decision side" claim
presumes a legal letter gets flagged under the legal rule and NOT under the medical rule.
This script verifies that per-document and emits the behaviour-matched doc list Move 4 needs.

Behaviour sources, in order of preference (per pass):
  1. the original extraction npz `behaviour` arrays:  <acts-dir>/exp2_<pass>__<position>.npz
     (any position — behaviour is per-doc and identical across positions)
  2. regenerated greedy behaviour JSONs:               <beh-dir>/crosstab_beh_<pass>.json
     (from crosstab_behaviour_gpu.py / run_crosstab_behaviour.sh)
Required passes: action_legal, action_medical. Optional: ask_{legal,medical}_p{1,2,3}
(adds the consistency-filtered ask-label column + the per-doc behavioural rule-flip read).

Pre-registered reading bands (plan_move1_crosstab.md), on the pooled 64 design hits:
  VERIFIED    matching-rule flag rate >= 0.70 AND swapped-rule flag rate <= 0.25
  UNDERMINED  matching - swapped < 0.10   (flagging essentially rule-independent)
  NOISY       otherwise
Truncated generations (JSON sources carry the flag) are excluded from rate denominators
and reported — a truncation is a non-answer, not an omission (the A5 lesson).

Usage:
    python crosstab_exp2.py --beh-dir acts            # after run_crosstab_behaviour.sh
    python crosstab_exp2.py --acts-dir acts           # if the original npz are recovered
Outputs: crosstab_exp2.json (full join + summary), crosstab_behaviour_matched.json (Move 4),
and verbatim tables on stdout (paste into runlog.md).
Smoke (fabricated behaviour, no GPU/API): python crosstab_smoke.py
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

ACTION_PASSES = ["action_legal", "action_medical"]
ASK_PASSES = [f"ask_{cond}_p{k}" for cond in ("legal", "medical") for k in (1, 2, 3)]
GROUP_ORDER = [("legal", "hit"), ("legal", "near"), ("medical", "hit"), ("medical", "near"),
               ("neutral", "form"), ("neutral", "none")]
BANDS = dict(verified_matching=0.70, verified_swapped=0.25, undermined_gap=0.10)


def load_pass(name: str, acts_dir: str | None, beh_dir: str | None):
    """Return ({id: {behaviour, cell, doccond, truncated}}, source_path) or (None, None)."""
    if acts_dir:
        cands = sorted(glob.glob(f"{acts_dir}/exp2_{name}__*.npz"))
        if cands:
            import numpy as np
            d = np.load(cands[0], allow_pickle=True)
            recs = {str(i): dict(behaviour=str(b), cell=str(c), doccond=str(dc), truncated=None)
                    for i, b, c, dc in zip(d["ids"], d["behaviour"], d["cell"], d["doccond"])}
            return recs, cands[0]
    if beh_dir:
        p = Path(beh_dir) / f"crosstab_beh_{name}.json"
        if p.exists():
            data = json.loads(p.read_text())
            recs = {r["id"]: dict(behaviour=r["behaviour"], cell=r["cell"], doccond=r["doccond"],
                                  truncated=bool(r.get("truncated", False)))
                    for r in data["records"]}
            return recs, str(p)
    return None, None


def rate(num: int, den: int) -> str:
    return f"{num}/{den} ({num / den:.0%})" if den else "0/0 (—)"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--acts-dir", default="acts", help="dir with original exp2_*__<pos>.npz (preferred source)")
    ap.add_argument("--beh-dir", default="acts", help="dir with crosstab_beh_*.json (regenerated source)")
    ap.add_argument("--out", default="crosstab_exp2.json")
    ap.add_argument("--matched-out", default="crosstab_behaviour_matched.json")
    args = ap.parse_args()

    # ---- load ----------------------------------------------------------------
    actions, sources = {}, {}
    for name in ACTION_PASSES:
        recs, src = load_pass(name, args.acts_dir, args.beh_dir)
        if recs is None:
            raise SystemExit(
                f"missing required pass {name!r}: no {args.acts_dir}/exp2_{name}__*.npz and no "
                f"{args.beh_dir}/crosstab_beh_{name}.json.\nGenerate it on a GPU box with "
                f"run_crosstab_behaviour.sh (generation-only, minutes) — NOT OpenRouter.")
        actions[name], sources[name] = recs, src

    asks = {}
    for name in ASK_PASSES:
        recs, src = load_pass(name, args.acts_dir, args.beh_dir)
        if recs is not None:
            asks[name], sources[name] = recs, src
    ask_available = {cond: all(f"ask_{cond}_p{k}" in asks for k in (1, 2, 3))
                     for cond in ("legal", "medical")}

    al, am = actions["action_legal"], actions["action_medical"]
    ids = sorted(al)
    if set(al) != set(am):
        raise SystemExit("action passes cover different ids — wrong/partial behaviour files")
    for i in ids:
        if (al[i]["cell"], al[i]["doccond"]) != (am[i]["cell"], am[i]["doccond"]):
            raise SystemExit(f"cell/doccond metadata disagrees across action passes for {i}")

    def ask_label(cond: str, i: str) -> str | None:
        """Consistency-filtered own-answer label (probe_exp2 K1 rule): all 3 clear AND agree."""
        if not ask_available[cond]:
            return None
        votes = [asks[f"ask_{cond}_p{k}"][i]["behaviour"] for k in (1, 2, 3)]
        if all(v in ("YES", "NO") for v in votes) and len(set(votes)) == 1:
            return votes[0]
        return "INCONSISTENT"

    # ---- per-doc join ----------------------------------------------------------
    per_doc, excluded = {}, []
    for i in ids:
        trunc = bool(al[i]["truncated"]) or bool(am[i]["truncated"])
        rec = dict(cell=al[i]["cell"], doccond=al[i]["doccond"],
                   flag_legal=al[i]["behaviour"] == "FLAG",
                   flag_medical=am[i]["behaviour"] == "FLAG",
                   truncated=trunc,
                   ask_legal=ask_label("legal", i), ask_medical=ask_label("medical", i))
        per_doc[i] = rec
        if trunc:
            excluded.append(i)
    live = [i for i in ids if i not in set(excluded)]

    print(f"sources: " + " | ".join(f"{k}: {v}" for k, v in sorted(sources.items())))
    print(f"docs: {len(ids)} total, {len(excluded)} truncated-excluded "
          f"({excluded if excluded else 'none'})\n")

    # ---- Table 1: cell x rule flag rates ---------------------------------------
    print("== Table 1: flag rate by cell x active rule ==")
    print(f"{'doccond/cell':<16} {'n':>3}  {'flag@legal':>14}  {'flag@medical':>14}")
    table1 = []
    for dc, cl in GROUP_ORDER:
        g = [i for i in live if per_doc[i]["doccond"] == dc and per_doc[i]["cell"] == cl]
        nl = sum(per_doc[i]["flag_legal"] for i in g)
        nm = sum(per_doc[i]["flag_medical"] for i in g)
        table1.append(dict(doccond=dc, cell=cl, n=len(g), flag_legal=nl, flag_medical=nm))
        print(f"{dc + '/' + cl:<16} {len(g):>3}  {rate(nl, len(g)):>14}  {rate(nm, len(g)):>14}")

    # ---- hits: per-doc 2x2, matching vs swapped --------------------------------
    def hits_2x2(domain: str, subset: list[str]) -> dict:
        own = "flag_legal" if domain == "legal" else "flag_medical"
        other = "flag_medical" if domain == "legal" else "flag_legal"
        h = [i for i in subset if per_doc[i]["doccond"] == domain and per_doc[i]["cell"] == "hit"]
        both = sum(per_doc[i][own] and per_doc[i][other] for i in h)
        m_only = sum(per_doc[i][own] and not per_doc[i][other] for i in h)
        s_only = sum(per_doc[i][other] and not per_doc[i][own] for i in h)
        neither = len(h) - both - m_only - s_only
        return dict(domain=domain, n=len(h), both=both, matching_only=m_only,
                    swapped_only=s_only, neither=neither,
                    matching=both + m_only, swapped=both + s_only)

    print("\n== Table 2: hits — flagged under matching vs swapped rule (per-doc 2x2) ==")
    print(f"{'hits':<10} {'n':>3} {'matching':>12} {'swapped':>12} {'both':>5} "
          f"{'match-only':>10} {'swap-only':>9} {'neither':>8}")
    hits = {}
    for dom in ("legal", "medical"):
        x = hits_2x2(dom, live)
        hits[dom] = x
        print(f"{dom:<10} {x['n']:>3} {rate(x['matching'], x['n']):>12} "
              f"{rate(x['swapped'], x['n']):>12} {x['both']:>5} {x['matching_only']:>10} "
              f"{x['swapped_only']:>9} {x['neither']:>8}")
    n_h = hits["legal"]["n"] + hits["medical"]["n"]
    pooled = dict(n=n_h,
                  matching=hits["legal"]["matching"] + hits["medical"]["matching"],
                  swapped=hits["legal"]["swapped"] + hits["medical"]["swapped"])
    pooled["matching_rate"] = pooled["matching"] / n_h if n_h else float("nan")
    pooled["swapped_rate"] = pooled["swapped"] / n_h if n_h else float("nan")
    print(f"{'POOLED':<10} {n_h:>3} {rate(pooled['matching'], n_h):>12} {rate(pooled['swapped'], n_h):>12}")

    # ---- verdict against the pre-registered bands ------------------------------
    mr, sr = pooled["matching_rate"], pooled["swapped_rate"]
    if mr - sr < BANDS["undermined_gap"]:
        verdict = "UNDERMINED"
    elif mr >= BANDS["verified_matching"] and sr <= BANDS["verified_swapped"]:
        verdict = "VERIFIED"
    else:
        verdict = "NOISY"
    print(f"\n== Verdict (pre-registered bands, pooled hits) ==")
    print(f"matching {mr:.0%} vs swapped {sr:.0%}  ->  {verdict}"
          f"   (VERIFIED: >= {BANDS['verified_matching']:.0%} & <= {BANDS['verified_swapped']:.0%};"
          f" UNDERMINED: gap < {BANDS['undermined_gap']:.0%})")

    # ---- K1-core secondary (hits the probe could actually use) ------------------
    k1 = None
    if all(ask_available.values()):
        core = [i for i in live
                if per_doc[i]["cell"] == "hit"
                and per_doc[i]["ask_legal" if per_doc[i]["doccond"] == "legal" else "ask_medical"] == "YES"]
        cm = sum(per_doc[i]["flag_legal" if per_doc[i]["doccond"] == "legal" else "flag_medical"] for i in core)
        cs = sum(per_doc[i]["flag_medical" if per_doc[i]["doccond"] == "legal" else "flag_legal"] for i in core)
        k1 = dict(n=len(core), matching=cm, swapped=cs)
        print(f"\nK1-core hits (own-ask consistent YES): {rate(cm, len(core))} matching, "
              f"{rate(cs, len(core))} swapped")
        # behavioural rule-flip on the ask side, per-doc, for the record
        flips = {d: dict(own_yes=0, other_yes=0, n=0) for d in ("legal", "medical")}
        for i in live:
            r = per_doc[i]
            if r["cell"] != "hit":
                continue
            d = r["doccond"]
            flips[d]["n"] += 1
            flips[d]["own_yes"] += r[f"ask_{d}"] == "YES"
            flips[d]["other_yes"] += r["ask_medical" if d == "legal" else "ask_legal"] == "YES"
        for d, f in flips.items():
            print(f"ask-side flip, {d} hits: own-question YES {rate(f['own_yes'], f['n'])}, "
                  f"other-question YES {rate(f['other_yes'], f['n'])}")
    else:
        print("\n(ask passes unavailable — ask_label column and K1-core line omitted)")

    # ---- over-flag localisation -------------------------------------------------
    print("\n== Table 3: non-hit flags (over-flagging), by cell x rule ==")
    overflag = []
    for dc, cl in GROUP_ORDER:
        if cl == "hit":
            continue
        g = [i for i in live if per_doc[i]["doccond"] == dc and per_doc[i]["cell"] == cl]
        nl = sum(per_doc[i]["flag_legal"] for i in g)
        nm = sum(per_doc[i]["flag_medical"] for i in g)
        overflag.append(dict(doccond=dc, cell=cl, n=len(g), flag_legal=nl, flag_medical=nm))
        print(f"{dc + '/' + cl:<16} {len(g):>3}  {rate(nl, len(g)):>14}  {rate(nm, len(g)):>14}")

    # ---- behaviour-matched list (Move 4 input) -----------------------------------
    matched_both = [i for i in live if per_doc[i]["flag_legal"] and per_doc[i]["flag_medical"]]
    matched_neither = [i for i in live if not per_doc[i]["flag_legal"] and not per_doc[i]["flag_medical"]]
    by_cell = {}
    for i in matched_both + matched_neither:
        key = f"{per_doc[i]['doccond']}/{per_doc[i]['cell']}"
        by_cell[key] = by_cell.get(key, 0) + 1
    print(f"\nbehaviour-matched: {len(matched_both)} flagged-both, {len(matched_neither)} flagged-neither "
          f"(by cell: {by_cell})")

    Path(args.matched_out).write_text(json.dumps(dict(
        note="Docs with the SAME action under both Exp 2 rules — the behaviour-matched cells for "
             "Move 4's decision-adjacent reads (plan_move4_spontaneity_ladder.md). A probe signal "
             "that separates rule-conditions WITHIN these docs cannot be reading about-to-act.",
        sources=sources, flagged_both=matched_both, flagged_neither=matched_neither,
        counts_by_cell=by_cell,
        per_doc={i: per_doc[i] for i in matched_both + matched_neither}), indent=1))

    Path(args.out).write_text(json.dumps(dict(
        meta=dict(sources=sources, bands=BANDS, n_docs=len(ids), excluded_truncated=excluded,
                  ask_available=ask_available),
        summary=dict(table1=table1, hits=hits, pooled=pooled, verdict=verdict,
                     k1_core=k1, overflag=overflag,
                     matched=dict(flagged_both=len(matched_both), flagged_neither=len(matched_neither))),
        per_doc=per_doc), indent=1))
    print(f"\nwrote {args.out} and {args.matched_out}")
    print("Next: paste the tables + verdict into runlog.md and update the summary doc per the plan's bands.")


if __name__ == "__main__":
    main()
