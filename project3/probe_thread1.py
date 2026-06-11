"""CPU analysis for Thread-1 — 1b instructed suppression + D1/D4 attention arms (A2/A4).

CONSISTENT BY CONSTRUCTION with the project's keyphrase analyses: it imports and reuses
probe_keyphrase.py's exact machinery (recognition direction trained on the model's own
ASK answers; pair-disjoint GroupKFold; document-disjoint pair-OOF diff-of-means cross-pass
scoring — a direction that never saw an action can't be reading "about to act"). Only the
CELL DEFINITIONS differ from the natural-gap watchdog:

  TRAIN recognition on the ASK pass (present vs absent = the model's own YES/NO).
  Score the ACTION pass, document-disjoint, and partition present-action into
    compliance = present ∧ recognised-under-load (loadedask YES) ∧ action NOFLAG
                 — the silent-suppression cell (A2's population)
    defiance   = present ∧ action FLAG  (recognised AND acted)
  against absent-action darks.

  A2 anchors (doc_mean, best layer by in-pass recognition):
    Outcome H (recognition live under suppression): comp-vs-absent ≥ 0.90 AND
      comp-vs-defiance ≤ 0.65 (compliance reads as strongly as defiance).
    Outcome C (countermand short-circuits recognition): comp-vs-absent ≤ 0.60.
  diff-of-means leads (low-capacity → high-selectivity); layer-0 should be ~0.5.

Positions: the prefill SPAN set (present in BOTH ask & action, so a cross-pass direction
exists). gen_first/gen_prefix_mean are action-only — no ask equivalent to train on —
so they need a separate in-pass analysis, NOT this cross-pass script.

Usage (one arm; run once per arm):
  python probe_thread1.py --label 1b --ask acts/thread1/v6_ask \
      --action acts/thread1/v6l6_action --loadedask acts/thread1/v6l6_plainask
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

from probe_keyphrase import load_npz, by_id, pair_oof
from train_probe import diffmeans_scores, pooled_oof_auroc, make_cv_splitter

SPAN_POSITIONS = ["doc_mean", "final", "doc_last", "name_last", "name_mean",
                  "post_name_mean", "post_doc_mean", "pre_doc_final"]


def auroc(pos, neg):
    if not len(pos) or not len(neg):
        return float("nan")
    return roc_auc_score([1] * len(pos) + [0] * len(neg), np.concatenate([pos, neg]))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--label", required=True, help="arm name (1b / D1 / D4) — for the output")
    ap.add_argument("--ask", required=True, help="ask npz prefix (recognition training)")
    ap.add_argument("--action", required=True, help="action npz prefix (the suppression behaviour)")
    ap.add_argument("--loadedask", required=True, help="in-context recognition npz prefix (plainask under the pressure)")
    ap.add_argument("--positions", default=",".join(SPAN_POSITIONS))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    report = {}
    for pos in args.positions.split(","):
        ask = load_npz(args.ask, pos)
        act = load_npz(args.action, pos)
        lda = load_npz(args.loadedask, pos)
        a_row, l_row = by_id(act), by_id(lda)

        # ASK training labels = the model's own clean ask answer (drop unclear) — v6 §7 method.
        keep = [k for k, b in enumerate(ask["beh"]) if b in ("YES", "NO")]
        y = np.array([1 if ask["beh"][k] == "YES" else 0 for k in keep])
        g_arr = np.array([ask["groups"][k] for k in keep])
        ids_keep = [ask["ids"][k] for k in keep]
        n_layers = ask["acts"].shape[1]

        pres_ids = [i for i in ids_keep if i.endswith("a") and i in a_row]
        compliance_ids = [i for i in pres_ids if i in l_row
                          and lda["beh"][l_row[i]] == "YES" and act["beh"][a_row[i]] == "NOFLAG"]
        defiance_ids = [i for i in pres_ids if act["beh"][a_row[i]] == "FLAG"]
        absent_ids = [i for i in ids_keep if i.endswith("b") and i in a_row]

        cv = make_cv_splitter("group", g_arr, args.seed)  # pair-disjoint folds (same as probe_keyphrase)
        folds = list(cv.split(np.zeros((len(g_arr), 1)), y, g_arr))
        fold_of = {}
        for f, (_tr, te) in enumerate(folds):
            for k in te:
                fold_of[g_arr[k]] = f
        n_folds = len(folds)

        pres_stems = [i[:-1] for i in pres_ids]
        abs_stems = [i[:-1] for i in absent_ids]
        a_pres_rows = [a_row[i] for i in pres_ids]
        a_abs_rows = [a_row[i] for i in absent_ids]
        comp_pos = [pres_ids.index(i) for i in compliance_ids]  # compliance ⊂ present-action
        def_pos = [pres_ids.index(i) for i in defiance_ids]

        rows = []
        for li in range(n_layers):
            Xask = ask["acts"][keep][:, li, :]
            recog_dm = pooled_oof_auroc(Xask, y, g_arr, cv, diffmeans_scores)  # in-pass recognition

            def oof(tv, ts):  # document-disjoint pair-OOF diff-of-means (same as probe_keyphrase)
                return pair_oof(Xask, y, g_arr, fold_of, n_folds, tv, ts)

            s_pres_act = oof(act["acts"][a_pres_rows][:, li, :], pres_stems)
            s_absent = oof(act["acts"][a_abs_rows][:, li, :], abs_stems)
            s_comp = s_pres_act[comp_pos] if comp_pos else np.array([])
            s_def = s_pres_act[def_pos] if def_pos else np.array([])
            rows.append(dict(
                layer=li, recog_dm=recog_dm,
                transfer=auroc(s_pres_act, s_absent),
                comp_vs_absent=auroc(s_comp, s_absent),
                comp_vs_defiance=auroc(s_comp, s_def),
                comp_mean=float(np.mean(s_comp)) if len(s_comp) else float("nan"),
                def_mean=float(np.mean(s_def)) if len(s_def) else float("nan"),
                absent_mean=float(np.mean(s_absent)) if len(s_absent) else float("nan"),
            ))

        best = max(rows, key=lambda r: r["recog_dm"])
        report[pos] = dict(n_present=len(pres_ids), n_compliance=len(compliance_ids),
                           n_defiance=len(defiance_ids), n_absent=len(absent_ids),
                           best_layer=best["layer"], best=best, per_layer=rows)
        print(f"\n== {args.label} / {pos}  (present {len(pres_ids)} | compliance {len(compliance_ids)} "
              f"| defiance {len(defiance_ids)} | absent {len(absent_ids)}) ==")
        print("layer | recog_dm | transfer | comp-vs-absent | comp-vs-defiance")
        for r in rows:
            print(f"  {r['layer']:2d}  |  {r['recog_dm']:.3f}  |  {r['transfer']:.3f}   |   "
                  f"{r['comp_vs_absent']:.3f}       |    {r['comp_vs_defiance']:.3f}")
        print(f"  >> best L{best['layer']}: recog {best['recog_dm']:.3f} | "
              f"comp-vs-absent {best['comp_vs_absent']:.3f} | comp-vs-defiance {best['comp_vs_defiance']:.3f} "
              f"(compliance n={len(compliance_ids)}, defiance n={len(defiance_ids)}, absent n={len(absent_ids)})")

    out = args.out or f"probe_{args.label}.json"
    Path(out).write_text(json.dumps(report, indent=2))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
