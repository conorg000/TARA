"""Move 3 — length-confound control for the playbook panel probe.

The N-condition panel pools conditions with different characteristic message lengths
(data_deletion ~216 chars, fraud_report ~349, implicit_legal_threat ~312). A length-only
baseline already separates the conditions (AUROC 0.96-0.99) and the nears from the neutral
`none` cell (0.998-1.0) — matching the probe's specificity (1.0) and near-none (~0.95).
So those reads are suspected to be LENGTH, not recognition. The matched-pair hit-vs-near
contrast is length-balanced by construction (length-only AUROC ~0.5) so it should be immune.

This script confirms it by RESIDUALISING activations on seq_len, per-fold and leak-free
(fit the per-dimension linear-in-length slope on the train fold only, subtract it from all),
then re-measuring. The analog of Move 2's panel_topic_removal but for length.

Reports, per condition at message_last, raw vs length-removed:
  floor (own-hit vs none), hit_near (own-hit vs own-near), near_none (own-near vs none),
  specificity (own-hit vs all-other-hits). Layer-robust median over the raw recog>0.9 band.

Expected if the diagnosis is right: hit_near holds (recognition, length-immune);
specificity and near_none collapse toward chance (they were length).

Usage:
  ./.venv/bin/python probe_playbook_lengthcontrol.py --acts-dir acts --out probe_playbook_lengthcontrol.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from probe_playbook import (load_npz, consistency_filter, rotating_acts, auroc, panel_oof,
                            RECOG_BAND)
from train_probe import make_cv_splitter


def residualise_on_length(X, L, fold_of, stems):
    """Per-dimension leak-free partialling-out of seq_len. For each fold f, fit slope b_d =
    cov(X_d, L)/var(L) and intercept on the TRAIN rows (fold != f), then for the TEST rows
    (fold == f) subtract b_d*(L - Lbar_train). Returns residualised X (same shape)."""
    Xr = X.astype(np.float64).copy()
    folds = sorted(set(fold_of.values()))
    for f in folds:
        tr = np.array([fold_of[s] != f for s in stems])
        te = np.array([fold_of[s] == f for s in stems])
        if tr.sum() < 2 or te.sum() == 0:
            continue
        Ltr = L[tr].astype(np.float64)
        Lbar = Ltr.mean()
        var = ((Ltr - Lbar) ** 2).sum()
        if var <= 0:
            continue
        # slope per dim from train; subtract predicted-from-length from test rows
        b = ((X[tr].astype(np.float64) - X[tr].astype(np.float64).mean(0)) *
             (Ltr - Lbar)[:, None]).sum(0) / var
        Xr[te] = X[te].astype(np.float64) - np.outer(L[te].astype(np.float64) - Lbar, b)
    return Xr


def analyze(cond, conds, acts_dir, seed):
    others = [c for c in conds if c != cond]
    ask_ps = [load_npz(f"{acts_dir}/playbook_ask_{cond}_p{k}", "message_last") for k in (1, 2, 3)]
    kept, y_all, _ = consistency_filter(ask_ps)
    base = ask_ps[0]
    cellk = [base["cell"][i] for i in kept]
    docck = [base["doccond"][i] for i in kept]
    stemsk = [base["groups"][i] for i in kept]
    seqk = np.array([base["seq_len"][i] for i in kept], dtype=float)
    Xrot = rotating_acts(ask_ps, kept)
    ytr = y_all
    gtr = np.array(stemsk)

    def mask(pred):
        return np.array([pred(docck[j], cellk[j]) for j in range(len(stemsk))])
    is_own_hit = mask(lambda d, c: c == "hit" and d == cond)
    is_own_near = mask(lambda d, c: c == "near" and d == cond)
    is_none = mask(lambda d, c: c == "none")
    is_any_other_hit = mask(lambda d, c: c == "hit" and d in others)

    cv = make_cv_splitter("group", gtr, seed)
    folds = list(cv.split(np.zeros((len(gtr), 1)), ytr, gtr))
    n_folds = len(folds)
    fold_of = {}
    for f, (_t, te) in enumerate(folds):
        for k in te:
            fold_of[gtr[k]] = f

    n_layers = Xrot.shape[1]
    rows = []
    for li in range(n_layers):
        X = Xrot[:, li, :]
        Xres = residualise_on_length(X, seqk, fold_of, gtr)
        out = {"layer": li}
        for tag, XX in (("raw", X), ("lenrm", Xres)):
            s = panel_oof(XX, ytr, gtr, fold_of, n_folds, XX, gtr)
            out[f"recog_{tag}"] = auroc(s[ytr == 1], s[ytr == 0])
            out[f"floor_{tag}"] = auroc(s[is_own_hit], s[is_none])
            out[f"hitnear_{tag}"] = auroc(s[is_own_hit], s[is_own_near])
            out[f"nearnone_{tag}"] = auroc(s[is_own_near], s[is_none])
            out[f"spec_{tag}"] = auroc(s[is_own_hit], s[is_any_other_hit])
        rows.append(out)

    band = [r for r in rows if r["recog_raw"] > RECOG_BAND]

    def med(key):
        v = [r[key] for r in band if not np.isnan(r[key])]
        return float(np.median(v)) if v else float("nan")
    keys = ["floor", "hitnear", "nearnone", "spec"]
    res = {"n_band_layers": len(band), "n_own_hit": int(is_own_hit.sum()),
           "n_own_near": int(is_own_near.sum()), "n_none": int(is_none.sum())}
    for k in keys:
        res[f"{k}_raw"] = med(f"{k}_raw")
        res[f"{k}_lenrm"] = med(f"{k}_lenrm")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--acts-dir", default="acts")
    ap.add_argument("--flag-vocab", default="playbook_flag_vocab.json")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="probe_playbook_lengthcontrol.json")
    args = ap.parse_args()
    conds = list(json.loads(Path(args.flag_vocab).read_text()).keys())

    report = {"_position": "message_last", "_note": "raw vs length-residualised (leak-free), "
              "layer-robust median over raw recog>0.9 band"}
    print(f"{'condition':24s} {'metric':9s} {'raw':>7s} {'len-removed':>12s}  read")
    print("-" * 70)
    for cond in conds:
        r = analyze(cond, conds, args.acts_dir, args.seed)
        report[cond] = r
        for k, label in (("hitnear", "hit-near"), ("nearnone", "near-none"),
                         ("spec", "specificity"), ("floor", "floor")):
            raw, lr = r[f"{k}_raw"], r[f"{k}_lenrm"]
            drop = raw - lr
            tag = ("RECOGNITION survives" if k == "hitnear" and lr >= 0.75 else
                   "was LENGTH (collapses)" if k in ("nearnone", "spec") and lr < 0.75 and drop > 0.15 else
                   "survives length-removal" if k in ("spec",) and lr >= 0.80 else "")
            print(f"{cond:24s} {label:9s} {raw:7.3f} {lr:12.3f}  {tag}")
        print(f"{'':24s} (band {r['n_band_layers']} layers; n_own_hit {r['n_own_hit']} "
              f"n_own_near {r['n_own_near']} n_none {r['n_none']})")
    Path(args.out).write_text(json.dumps(report, indent=2))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
