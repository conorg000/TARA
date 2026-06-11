"""Type-composition audit for Thread-1 (the registered A2 self-selection control).

Compliance (silent-suppressed) docs are SELF-SELECTED — the model chose which to comply
on — and keyphrase omissions are type-skewed (locations/units omit, persons rarely flagged
elsewhere). So the headline comp-vs-defiance separation could be a doc-TYPE confound rather
than a recognition difference. This stratifies the same pair-OOF projection by entity type
(unit / location / person, read from the action input JSON) and recomputes the contrasts
WITHIN type. If the picture survives within-type, it isn't a type artifact.

Reuses probe_keyphrase's exact machinery (recognition trained on the model's own ask
answer; document-disjoint pair-OOF diff-of-means). Run on the well-powered 1b arm.

Usage:
  python probe_typeaudit.py --ask acts/thread1/v6_ask --action acts/thread1/v6l6_action \
      --loadedask acts/thread1/v6l6_plainask --action-input inputs/watchlist_v6_l6_action_H5.json
"""

from __future__ import annotations

import argparse
import json
from collections import Counter

import numpy as np
from sklearn.metrics import roc_auc_score

from probe_keyphrase import load_npz, by_id, pair_oof
from train_probe import diffmeans_scores, pooled_oof_auroc, make_cv_splitter


def auroc(pos, neg):
    if len(pos) < 1 or len(neg) < 1:
        return float("nan")
    return roc_auc_score([1] * len(pos) + [0] * len(neg), np.concatenate([pos, neg]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ask", required=True)
    ap.add_argument("--action", required=True)
    ap.add_argument("--loadedask", required=True)
    ap.add_argument("--action-input", required=True, help="the action input JSON (for id -> entity type)")
    ap.add_argument("--positions", default="doc_mean,post_name_mean")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    type_of = {r["id"]: r["group"] for r in json.loads(open(args.action_input).read())}

    for pos in args.positions.split(","):
        ask = load_npz(args.ask, pos); act = load_npz(args.action, pos); lda = load_npz(args.loadedask, pos)
        a_row, l_row = by_id(act), by_id(lda)
        keep = [k for k, b in enumerate(ask["beh"]) if b in ("YES", "NO")]
        y = np.array([1 if ask["beh"][k] == "YES" else 0 for k in keep])
        g_arr = np.array([ask["groups"][k] for k in keep])
        ids_keep = [ask["ids"][k] for k in keep]

        pres_ids = [i for i in ids_keep if i.endswith("a") and i in a_row]
        comp_ids = [i for i in pres_ids if i in l_row and lda["beh"][l_row[i]] == "YES" and act["beh"][a_row[i]] == "NOFLAG"]
        def_ids = [i for i in pres_ids if act["beh"][a_row[i]] == "FLAG"]
        absent_ids = [i for i in ids_keep if i.endswith("b") and i in a_row]

        cv = make_cv_splitter("group", g_arr, args.seed)
        folds = list(cv.split(np.zeros((len(g_arr), 1)), y, g_arr))
        fold_of = {}
        for f, (_t, te) in enumerate(folds):
            for k in te:
                fold_of[g_arr[k]] = f
        n_folds = len(folds)

        # best layer by in-pass recognition (consistent with probe_thread1)
        best_li = max(range(ask["acts"].shape[1]),
                      key=lambda li: pooled_oof_auroc(ask["acts"][keep][:, li, :], y, g_arr, cv, diffmeans_scores))
        Xask = ask["acts"][keep][:, best_li, :]

        def oof(ids):
            rows = [a_row[i] for i in ids]
            return pair_oof(Xask, y, g_arr, fold_of, n_folds, act["acts"][rows][:, best_li, :], [i[:-1] for i in ids])

        s_comp = {i: s for i, s in zip(comp_ids, oof(comp_ids))}
        s_def = {i: s for i, s in zip(def_ids, oof(def_ids))}
        s_abs = oof(absent_ids)

        print(f"\n===== {pos}  (best L{best_li}) =====")
        comp_types = Counter(type_of[i] for i in comp_ids)
        def_types = Counter(type_of[i] for i in def_ids)
        print(f"compliance n={len(comp_ids)} types={dict(comp_types)}")
        print(f"defiance   n={len(def_ids)} types={dict(def_types)}")
        print(f"overall: comp-vs-defiance {auroc(list(s_comp.values()), list(s_def.values())):.3f}  "
              f"comp-vs-absent {auroc(list(s_comp.values()), s_abs):.3f}  "
              f"(comp mean {np.mean(list(s_comp.values())):.0f} / def {np.mean(list(s_def.values())):.0f} / abs {np.mean(s_abs):.0f})")
        print("  within-type (controls the self-selection skew):")
        for t in ("unit", "location", "person"):
            ct = [s_comp[i] for i in comp_ids if type_of[i] == t]
            dt = [s_def[i] for i in def_ids if type_of[i] == t]
            cvd = auroc(ct, dt)
            note = "" if (len(ct) >= 5 and len(dt) >= 5) else "  (underpowered)"
            print(f"    {t:9s} comp n={len(ct):2d} def n={len(dt):3d}  comp-vs-defiance {cvd:.3f}"
                  f"  (comp mean {np.mean(ct):.0f}/def {np.mean(dt):.0f}){note}" if ct else
                  f"    {t:9s} comp n=0 — no compliance of this type")


if __name__ == "__main__":
    main()
