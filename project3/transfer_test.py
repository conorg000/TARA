"""Cross-taxonomy transfer test (Step 2): does the recognition probe generalise to a
taxonomy it never saw?

Trains the diff-of-means recognition direction on the SOURCE dataset (v2) and applies it,
unchanged, to the TARGET dataset (v2b) — a disjoint taxonomy. If detection holds, the
probe reads an abstract "condition fired" feature, not taxonomy-specific cues; the monitor
generalises. If it collapses to ~0.5, it was fit to the source taxonomy.

Reports, per layer:
  - within-source : diff-of-means OOF AUROC on v2 (our honest baseline, ~0.71 @ L19)
  - within-target : diff-of-means OOF AUROC on v2b (does the signal even exist there? ceiling)
  - TRANSFER      : direction trained on ALL of v2, scored on v2b (the headline)
  - shuffle-trans : transfer of a direction trained on SHUFFLED v2 labels (~0.5 control)

diff-of-means is the trustworthy probe (r5); logreg shown alongside transfer for reference.

Usage:
    python transfer_test.py --source activations_conditions_v2.npz \
        --target activations_conditions_v2b.npz --layers 16,17,18,19,20,21
"""

from __future__ import annotations

import argparse

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

from train_probe import diffmeans_scores, logreg_scores, pooled_oof_auroc, make_cv_splitter


def diffmeans_direction(Xtr, ytr):
    """Fit the standardiser + diff-of-means direction on the source; return both."""
    scaler = StandardScaler().fit(Xtr)
    Z = scaler.transform(Xtr)
    direction = Z[ytr == 1].mean(axis=0) - Z[ytr == 0].mean(axis=0)
    return scaler, direction


def transfer_auroc(Xs, ys, Xt, yt, fit_fn):
    """Train on ALL of source, score target. fit_fn returns (scaler, direction)."""
    scaler, direction = fit_fn(Xs, ys)
    scores = scaler.transform(Xt) @ direction
    return roc_auc_score(yt, scores)


def logreg_transfer_auroc(Xs, ys, Xt, yt):
    scaler = StandardScaler().fit(Xs)
    clf = LogisticRegression(max_iter=1000, C=1.0).fit(scaler.transform(Xs), ys)
    return roc_auc_score(yt, clf.predict_proba(scaler.transform(Xt))[:, 1])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--layers", default="16,17,18,19,20,21")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    src = np.load(args.source, allow_pickle=True)
    tgt = np.load(args.target, allow_pickle=True)
    As, ys = src["activations"], src["labels"].astype(int)
    At, yt = tgt["activations"], tgt["labels"].astype(int)
    cv = make_cv_splitter("random", None, args.seed)

    layers = [int(x) for x in args.layers.split(",")]
    print(f"source: {args.source} (N={len(ys)})  ->  target: {args.target} (N={len(yt)})")
    print("diff-of-means is the trustworthy metric; logreg-transfer shown for reference.\n")
    print(f"{'layer':>5} | {'within-src':>10} | {'within-tgt':>10} | {'TRANSFER':>9} | {'shuf-trans':>10} | {'lr-trans':>8}")
    print("-" * 70)

    # one shuffled source labelling, reused across layers
    ys_shuf = ys.copy()
    np.random.default_rng(args.seed).shuffle(ys_shuf)

    rows = []
    for li in layers:
        Xs, Xt = As[:, li, :], At[:, li, :]
        within_s = pooled_oof_auroc(Xs, ys, None, cv, diffmeans_scores)
        within_t = pooled_oof_auroc(Xt, yt, None, cv, diffmeans_scores)
        trans = transfer_auroc(Xs, ys, Xt, yt, diffmeans_direction)
        shuf = transfer_auroc(Xs, ys_shuf, Xt, yt, diffmeans_direction)
        lr_trans = logreg_transfer_auroc(Xs, ys, Xt, yt)
        rows.append((li, within_s, within_t, trans, shuf, lr_trans))
        print(f"{li:>5} | {within_s:>10.3f} | {within_t:>10.3f} | {trans:>9.3f} | {shuf:>10.3f} | {lr_trans:>8.3f}")

    print("-" * 70)
    best = max(rows, key=lambda r: r[3])
    print(f"\nBest TRANSFER (diff-of-means): layer {best[0]}  AUROC {best[3]:.3f}")
    print(f"  within-source {best[1]:.3f} | within-target {best[2]:.3f} | shuffle-transfer {best[4]:.3f}")
    print("\nReading: transfer ≈ within-target ⇒ the recognition direction is taxonomy-agnostic")
    print("(monitor generalises). transfer ≈ shuffle (~0.5) ⇒ it was source-specific.")


if __name__ == "__main__":
    main()
