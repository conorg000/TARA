"""CPU step: the Move 4 spontaneity-ladder probe (no GPU). Runs on extract_ladder.py's npz.

The question (plan_move4_spontaneity_ladder.md): does the rule make the model compute a
compound's decisive element AT READING TIME, where comprehension alone would not — and where
is the hard boundary of the content-probe panel?

Per condition, per read position, per layer:
  TRAIN a compound direction on the ASK compound pass. Labels = the model's OWN ask answer,
  consistency-filtered across the 3 paraphrases (K1) AND correctness-filtered (a hit the model
  called NO, or a near/form/none it called YES, is dropped — these are the near-threshold
  fumbles; we don't want them poisoning the direction). Paraphrase rotated per item
  (format-confound guard). diff-of-means, pair-disjoint CV on meta.pair_stem.

  THE DECISIVE READ (plan Appendix B1/B2): hit-vs-near (A and B vs A and not B) separability
  WITHIN each pure-reading arm, scored CROSS-PASS (the ask-trained direction, never trained on a
  read pass) and document-disjoint. hit and near differ only in B, so this isolates B.
    present_hit_near : the rule (compound) is in the system prompt — the "with-rule" arm.
    absent_hit_near  : a length-matched placebo rule — the "without-rule" arm. For Family B this
                       is at chance BY CONSTRUCTION (the criterion is absent) — so it is also the
                       magnitude/recency-leak check. For Family A it is a real measurement
                       (is the world-fact spontaneously computed?).
  Headline = present_hit_near - absent_hit_near, at the layer chosen by recog_dm (independent of
  the outcome metric, so no cherry-picking).

  COMPONENT CONTROLS (construction): compA direction (is-A) must separate A-cells from non-A in
  both arms; compB direction (is-B) similarly. A compound null with a dead component is a build
  failure, reported as such.

  Behavioural complement: FLAG rates per cell in read_present (does the rule actually fire on
  hits?) — the decision-side counterpart to the reading-side probe.

Usage (after run_extract_ladder.sh writes acts/ladder_*__<pos>.npz):
    python probe_ladder.py --acts-dir acts --out probe_ladder.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from train_probe import diffmeans_scores, make_cv_splitter, pooled_oof_auroc
from probe_exp2 import pair_oof, auroc, consistency_filter, rotating_acts

DEFAULT_POSITIONS = ["message_mean", "message_last", "final"]
CONDS = ["advice_deadline", "refund_over_500", "complaint_6months", "medical_rx_drug"]


def load_npz(prefix: str, position: str) -> dict:
    d = np.load(f"{prefix}__{position}.npz", allow_pickle=True)
    return {
        "acts": d["activations"], "ids": [str(x) for x in d["ids"]],
        "labels": d["labels"].astype(int), "groups": [str(x) for x in d["groups"]],
        "beh": [str(x) for x in d["behaviour"]], "cell": [str(x) for x in d["cell"]],
        "arm": [str(x) for x in d["arm"]], "seq_len": d["seq_len"].astype(int),
    }


def flag_rates(read: dict) -> dict:
    """FLAG rate per cell on a read pass (behavioural complement)."""
    out = {}
    for c in ("hit", "near", "form", "none"):
        rows = [i for i, cc in enumerate(read["cell"]) if cc == c]
        out[c] = round(sum(read["beh"][i] == "FLAG" for i in rows) / max(len(rows), 1), 3)
    return out


def single_label(ask: dict) -> tuple[list[int], np.ndarray]:
    """Clear-answer rows + model labels for a single-paraphrase ask pass (components)."""
    kept, y = [], []
    for i, b in enumerate(ask["beh"]):
        if b in ("YES", "NO"):
            kept.append(i); y.append(1 if b == "YES" else 0)
    return kept, np.array(y)


def component_read(askc: dict, read: dict, pos_cells: set, position_layers: int,
                   seed: int) -> list[float]:
    """Per layer: train the component direction on its ask pass, score the read pass
    cross-pass (document-disjoint), AUROC(pos-cells vs neg-cells) in that arm."""
    kept, y = single_label(askc)
    if len(set(y)) < 2:
        return [float("nan")] * position_layers
    stems = [askc["groups"][i] for i in kept]
    Xask = askc["acts"][kept]
    g = np.array(stems)
    cv = make_cv_splitter("group", g, seed)
    folds = list(cv.split(np.zeros((len(g), 1)), y, g))
    fold_of = {}
    for f, (_tr, te) in enumerate(folds):
        for k in te:
            fold_of[g[k]] = f
    # read targets: only docs whose stem appears in the ask fold map
    tgt = [i for i, s in enumerate(read["groups"]) if s in fold_of]
    tcells = [read["cell"][i] for i in tgt]
    tstems = [read["groups"][i] for i in tgt]
    is_pos = np.array([c in pos_cells for c in tcells])
    out = []
    for li in range(position_layers):
        s = pair_oof(Xask[:, li, :], y, g, fold_of, len(folds),
                     read["acts"][tgt][:, li, :], tstems)
        out.append(auroc(s[is_pos], s[~is_pos]))
    return out


def analyze(cond: str, acts_dir: str, position: str, seed: int) -> dict:
    pre = f"{acts_dir}/ladder_{cond}"
    ask_ps = [load_npz(f"{pre}_ask_compound_p{k}", position) for k in (1, 2, 3)]
    askA = load_npz(f"{pre}_ask_compA", position)
    askB = load_npz(f"{pre}_ask_compB", position)
    read = {"present": load_npz(f"{pre}_read_present", position),
            "absent": load_npz(f"{pre}_read_absent", position)}

    # compound direction: consistency- AND correctness-filtered model labels
    kept, ymodel, n_drop_consis = consistency_filter(ask_ps)
    base = ask_ps[0]
    cell = [base["cell"][i] for i in kept]
    # correctness filter: hit must be YES(1); near/form/none must be NO(0)
    gt = np.array([1 if c == "hit" else 0 for c in cell])
    correct = (ymodel == gt)
    sel = [j for j in range(len(kept)) if correct[j]]
    n_drop_correct = len(kept) - len(sel)
    y = gt[sel]
    cell = [cell[j] for j in sel]
    stems = [base["groups"][kept[j]] for j in sel]
    ids = [base["ids"][kept[j]] for j in sel]
    Xrot = rotating_acts(ask_ps, [kept[j] for j in sel])     # [Nk, L+1, D]

    g = np.array(stems)
    cv = make_cv_splitter("group", g, seed)
    n_layers = Xrot.shape[1]
    folds = list(cv.split(np.zeros((len(g), 1)), y, g))
    fold_of = {}
    for f, (_tr, te) in enumerate(folds):
        for k in te:
            fold_of[g[k]] = f

    # decisive eval docs (clean hit / clean near), mapped into each read pass by id
    hit_ids = [i for i, c in zip(ids, cell) if c == "hit"]
    near_ids = [i for i, c in zip(ids, cell) if c == "near"]

    def read_rows(arm, want_ids):
        rmap = {i: k for k, i in enumerate(read[arm]["ids"])}
        return [rmap[i] for i in want_ids if i in rmap and read[arm]["groups"][rmap[i]] in fold_of]

    rows = []
    for li in range(n_layers):
        Xask = Xrot[:, li, :]
        s_self = pair_oof(Xask, y, g, fold_of, len(folds), Xask, g)
        recog_dm = auroc(s_self[y == 1], s_self[y == 0])
        is_hit = np.array([c == "hit" for c in cell]); is_near = np.array([c == "near" for c in cell])
        ask_hit_near = auroc(s_self[is_hit], s_self[is_near])     # reference (question elicits it)

        arm_hn = {}
        for arm in ("present", "absent"):
            hr, nr = read_rows(arm, hit_ids), read_rows(arm, near_ids)
            sh = pair_oof(Xask, y, g, fold_of, len(folds), read[arm]["acts"][hr][:, li, :],
                          [read[arm]["groups"][r] for r in hr])
            sn = pair_oof(Xask, y, g, fold_of, len(folds), read[arm]["acts"][nr][:, li, :],
                          [read[arm]["groups"][r] for r in nr])
            arm_hn[arm] = auroc(sh, sn)
        rows.append(dict(layer=li, recog_dm=recog_dm, ask_hit_near=ask_hit_near,
                         present_hit_near=arm_hn["present"], absent_hit_near=arm_hn["absent"],
                         delta=arm_hn["present"] - arm_hn["absent"]))

    # layer chosen by recog_dm (independent of the outcome metric)
    best = max(rows, key=lambda r: r["recog_dm"])
    # component controls at the same layer
    compA = {arm: component_read(askA, read[arm], {"hit", "near"}, n_layers, seed)[best["layer"]]
             for arm in ("present", "absent")}
    compB = {arm: component_read(askB, read[arm], {"hit", "form"}, n_layers, seed)[best["layer"]]
             for arm in ("present", "absent")}
    return dict(
        n_kept=len(sel), n_drop_consistency=n_drop_consis, n_drop_correctness=n_drop_correct,
        n_hit=int(sum(c == "hit" for c in cell)), n_near=int(sum(c == "near" for c in cell)),
        best_layer=best["layer"], best=best, per_layer=rows,
        compA=compA, compB=compB,
        flag_present=flag_rates(read["present"]), flag_absent=flag_rates(read["absent"]))


def verdict(cond: str, b: dict) -> str:
    """Plan prediction bands at the recog-selected layer."""
    p, a = b["best"]["present_hit_near"], b["best"]["absent_hit_near"]
    ca = min(b["compA"]["present"], b["compA"]["absent"])
    if ca < 0.75:
        return f"COMPONENT-A WEAK ({ca:.2f}) — construction issue, interpret with care"
    if p >= 0.80 and a <= 0.65:
        return "RULE-RESTORED: rule-conditioned computation at reading time"
    if p <= 0.65 and a <= 0.65:
        return "HARD BOUNDARY: not read in either arm (binding deferred to the decision)"
    if a >= 0.80:
        return "READ WITHOUT RULE: decisive element computed spontaneously (Family-A-like / leak?)"
    return f"INTERMEDIATE: present {p:.2f} / absent {a:.2f}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--acts-dir", default="acts")
    ap.add_argument("--positions", default=",".join(DEFAULT_POSITIONS))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="probe_ladder.json")
    args = ap.parse_args()

    report = {}
    for cond in CONDS:
        report[cond] = {}
        for pos in args.positions.split(","):
            try:
                b = analyze(cond, args.acts_dir, pos, args.seed)
            except FileNotFoundError as e:
                print(f"  (skip {cond}/{pos}: {e})"); continue
            report[cond][pos] = b
            print(f"\n===== {cond} | {pos}  (kept {b['n_kept']}: hit {b['n_hit']} / near {b['n_near']}; "
                  f"dropped {b['n_drop_consistency']} inconsistent + {b['n_drop_correctness']} wrong) =====")
            print("layer | recog_dm | ask hit-near | PRESENT h-n | ABSENT h-n | delta")
            for r in b["per_layer"]:
                star = " <-" if r["layer"] == b["best_layer"] else ""
                print(f"  {r['layer']:2d}  |  {r['recog_dm']:.3f}  |   {r['ask_hit_near']:.3f}    |   "
                      f"{r['present_hit_near']:.3f}   |   {r['absent_hit_near']:.3f}  | {r['delta']:+.3f}{star}")
            bb = b["best"]
            print(f"  >> best L{b['best_layer']} (by recog): PRESENT hit-near {bb['present_hit_near']:.3f} | "
                  f"ABSENT {bb['absent_hit_near']:.3f} | delta {bb['delta']:+.3f}")
            print(f"     compA present/absent {b['compA']['present']:.2f}/{b['compA']['absent']:.2f} | "
                  f"compB {b['compB']['present']:.2f}/{b['compB']['absent']:.2f}")
            print(f"     FLAG rates present {b['flag_present']} | absent {b['flag_absent']}")
            print(f"     -> {verdict(cond, b)}")

    Path(args.out).write_text(json.dumps(report, indent=2))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
