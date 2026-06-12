"""Move 2 / Appendix A1 — does the readable legal-content axis explain Move 1's action
liberality?  (piggyback on the panel activations; single-look.)

Move 1 (cross-tab) found that under the SINGLE legal rule, 17 of 32 medical hits were
spuriously flagged `legal-advice-request`, and explicitly flagged the 17-flagged-vs-15-
unflagged split as "an eyeball read, not a formal test" (the 17 looked content-
indistinguishable from the 15). A1 makes it formal and connects behaviour to
representation:

    Score each medical doc on probe_legal (the legal recognition direction, trained on
    the panel's legal ask pass, OOF). Then ask: do the medical docs that got over-flagged
    as legal score HIGHER on probe_legal than the ones that didn't?

  AUROC(flagged-medical vs unflagged-medical) on probe_legal:
    HIGH (>=~0.70)  -> the over-flag tracks the readable content axis: the legal rule
                       fires on the medical docs that *read more legal-advice-seeking*.
                       Action liberality is explained by the content representation.
    ~0.5            -> probe_legal does NOT separate flagged from unflagged: the
                       over-flag is NOT content-graded -> it lives DOWNSTREAM of the
                       readable content (formally confirms Move 1's eyeball "no clean
                       distinction", and places the liberality after the content read).

Reuses probe_panel's exact machinery (consistency filter, paraphrase rotation, pair-
disjoint document-disjoint OOF diff-of-means). probe_legal score = OOF score at the
recognition-best layer, message_last. Behaviour label = single-legal-rule FLAG from
Move 1's crosstab_beh_action_legal.json (greedy, code c89dbce).

Usage (on the box; scp crosstab_beh_action_legal.json there first):
  /venv/main/bin/python panel_a1.py --acts-dir acts \
      --crosstab crosstab_beh_action_legal.json --out panel_a1.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import mannwhitneyu

from probe_panel import load_npz, consistency_filter, rotating_acts, panel_oof, auroc
from train_probe import make_cv_splitter


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--acts-dir", default="acts")
    ap.add_argument("--crosstab", default="crosstab_beh_action_legal.json")
    ap.add_argument("--position", default="message_last")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="panel_a1.json")
    args = ap.parse_args()

    # --- probe_legal: train on panel legal ask, OOF scores at the recog-best layer ---
    ask_ps = [load_npz(f"{args.acts_dir}/panel_ask_legal_p{k}", args.position) for k in (1, 2, 3)]
    kept, y_all, _ = consistency_filter(ask_ps)
    base = ask_ps[0]
    cellk = [base["cell"][i] for i in kept]
    docck = [base["doccond"][i] for i in kept]
    stemsk = [base["groups"][i] for i in kept]
    idsk = [base["ids"][i] for i in kept]
    Xrot = rotating_acts(ask_ps, kept)

    tr = [j for j, c in enumerate(cellk) if c != "both"]
    ytr = y_all[tr]
    gtr = np.array([stemsk[j] for j in tr])
    Xtr = Xrot[tr]
    ids_tr = [idsk[j] for j in tr]
    cell_tr = [cellk[j] for j in tr]
    doc_tr = [docck[j] for j in tr]

    cv = make_cv_splitter("group", gtr, args.seed)
    folds = list(cv.split(np.zeros((len(gtr), 1)), ytr, gtr))
    n_folds = len(folds)
    fold_of = {}
    for f, (_t, te) in enumerate(folds):
        for k in te:
            fold_of[gtr[k]] = f

    # recognition-best layer (by in-pass recog), then per-doc OOF scores there
    best_li, best_recog = 0, -1.0
    for li in range(Xtr.shape[1]):
        X = Xtr[:, li, :]
        s = panel_oof(X, ytr, gtr, fold_of, n_folds, X, gtr)
        r = auroc(s[ytr == 1], s[ytr == 0])
        if r > best_recog:
            best_recog, best_li = r, li
    s = panel_oof(Xtr[:, best_li, :], ytr, gtr, fold_of, n_folds, Xtr[:, best_li, :], gtr)
    score_by_id = {ids_tr[j]: float(s[j]) for j in range(len(ids_tr))}

    # --- behaviour labels: single-legal-rule FLAG on medical docs (Move 1 crosstab) ---
    recs = json.loads(Path(args.crosstab).read_text())["records"]
    legal_flag = {r["id"]: (r["behaviour"] == "FLAG") for r in recs}

    # --- the A1 test: among MEDICAL hits, flagged-as-legal vs not ---
    med_ids = [ids_tr[j] for j in range(len(ids_tr)) if cell_tr[j] == "hit" and doc_tr[j] == "medical"
               and ids_tr[j] in legal_flag]
    flagged = [i for i in med_ids if legal_flag[i]]
    unflag = [i for i in med_ids if not legal_flag[i]]
    sf = np.array([score_by_id[i] for i in flagged])
    su = np.array([score_by_id[i] for i in unflag])

    a1 = auroc(sf, su) if len(sf) and len(su) else float("nan")
    try:
        u, p = mannwhitneyu(sf, su, alternative="two-sided")
        p = float(p)
    except Exception:
        p = float("nan")

    # reference anchors on the same probe_legal axis
    leg_hit = np.array([score_by_id[ids_tr[j]] for j in range(len(ids_tr))
                        if cell_tr[j] == "hit" and doc_tr[j] == "legal"])
    none_s = np.array([score_by_id[ids_tr[j]] for j in range(len(ids_tr)) if cell_tr[j] == "none"])

    verdict = ("over-flag TRACKS the content axis" if a1 >= 0.70 else
               "over-flag is DOWNSTREAM of the content axis (not content-graded)" if a1 <= 0.60 else
               "GRAY / underpowered")
    out = dict(position=args.position, best_recog_layer=best_li, best_recog=round(best_recog, 4),
               n_medical_flagged=len(flagged), n_medical_unflagged=len(unflag),
               a1_auroc_flagged_vs_unflagged=round(a1, 4), mannwhitney_p=round(p, 4),
               mean_score={"medical_flagged": round(float(sf.mean()), 1) if len(sf) else None,
                           "medical_unflagged": round(float(su.mean()), 1) if len(su) else None,
                           "legal_hit": round(float(leg_hit.mean()), 1),
                           "none": round(float(none_s.mean()), 1)},
               verdict=verdict)
    print(json.dumps(out, indent=2))
    Path(args.out).write_text(json.dumps(out, indent=2))
    print(f"\nwrote {args.out}")
    print(f"\nA1: probe_legal score, medical FLAGGED-as-legal ({len(flagged)}) vs UNFLAGGED "
          f"({len(unflag)}): AUROC {a1:.3f} (p={p:.3f}) -> {verdict}")


if __name__ == "__main__":
    main()
