"""Pick the probe layer by the HONEST metric, and report the honest monitor number.

Background: train_probe / controls picked the layer where *logreg* OOF AUROC peaked.
r5 showed logreg is low-selectivity here (it reads arbitrary junk at 0.75-0.80), so
that choice inflates the headline. This sweeps every layer and selects by the
trustworthy signal instead:

    selectivity_dm(layer) = real diff-of-means AUROC
                            - max(clean control diff-of-means AUROCs)

where the clean controls are the ones r5 established as fair (shuffle labels,
destination alphabetical-half, item-IRRELEVANT membership). diff-of-means can't
overfit the way logreg can, so its selectivity is the honest recognition signal.

We report logreg too, but only as a reference / monitor-predictor upper bound.

Usage:
    python select_layer.py --activations activations_conditions_v2.npz --dataset inputs/conditions_v2.json
"""

from __future__ import annotations

import argparse
import json
import random

import numpy as np

from train_probe import logreg_scores, diffmeans_scores, pooled_oof_auroc, make_cv_splitter


def load_aligned(activations_path: str, dataset_path: str):
    data = np.load(activations_path, allow_pickle=True)
    ids = [str(i) for i in data["ids"]]
    by_id = {r["id"]: r for r in json.load(open(dataset_path))}
    return data, [by_id[i] for i in ids]


def build_controls(recs, y, seed, n_shuffles=3):
    """The clean control label sets r5 endorsed (excludes item-parity: proxies identity)."""
    controls = {}

    # shuffle: several permutations, kept as a list so we can take the worst (max).
    shuffles = []
    for s in range(n_shuffles):
        yp = y.copy()
        np.random.default_rng(seed * 1000 + s).shuffle(yp)
        shuffles.append(yp)
    controls["shuffle"] = shuffles

    # destination alphabetical half — arbitrary surface fact about the input.
    controls["dest_alpha"] = [np.array([1 if r["meta"]["destination"][0].upper() >= "M" else 0 for r in recs])]

    # item-IRRELEVANT membership — same "read the list" computation minus the item->category step.
    all_cats = sorted({r["meta"]["category"] for r in recs}
                      | {c for r in recs for c in r["meta"]["restricted_categories"]})
    irng = random.Random(seed + 7)
    yc = []
    for r in recs:
        item_cat = r["meta"]["category"]
        listed = set(r["meta"]["restricted_categories"])
        non_item = [c for c in all_cats if c != item_cat]
        in_list = [c for c in non_item if c in listed]
        out_list = [c for c in non_item if c not in listed]
        t = irng.randint(0, 1)
        yc.append(1 if (t == 1 and in_list) else 0 if (t == 0 and out_list) else (1 if in_list else 0))
    controls["item_irrelevant"] = [np.array(yc)]
    return controls


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--activations", required=True)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    data, recs = load_aligned(args.activations, args.dataset)
    activations = data["activations"]
    y = data["labels"].astype(int)
    cv = make_cv_splitter("random", None, args.seed)
    controls = build_controls(recs, y, args.seed)

    def dm(X, yc):
        return pooled_oof_auroc(X, yc, None, cv, diffmeans_scores)

    def lr(X, yc):
        return pooled_oof_auroc(X, yc, None, cv, logreg_scores)

    print(f"Activations: {args.activations} | N={len(y)} | seed={args.seed}, stratified 5-fold OOF")
    print("Selecting layer by diff-of-means selectivity vs clean controls (shuffle / dest / item-irrelevant).\n")
    print(f"{'layer':>5} | {'real_dm':>7} | {'real_lr':>7} | {'shuf':>5} | {'dest':>5} | {'irrel':>5} | {'select_dm':>9}")
    print("-" * 64)

    rows = []
    for li in range(activations.shape[1]):
        X = activations[:, li, :]
        real_dm, real_lr = dm(X, y), lr(X, y)
        shuf = max(dm(X, yp) for yp in controls["shuffle"])          # worst-case (max) clean baseline
        dest = dm(X, controls["dest_alpha"][0])
        irrel = dm(X, controls["item_irrelevant"][0])
        clean = max(shuf, dest, irrel)
        select = real_dm - clean
        rows.append((li, real_dm, real_lr, shuf, dest, irrel, select))

    for li, real_dm, real_lr, shuf, dest, irrel, select in rows:
        mark = ""
        print(f"{li:>5} | {real_dm:>7.3f} | {real_lr:>7.3f} | {shuf:>5.3f} | {dest:>5.3f} | {irrel:>5.3f} | {select:>9.3f}{mark}")

    best_sel = max(rows, key=lambda r: r[6])
    best_dm = max(rows, key=lambda r: r[1])
    print("-" * 64)
    print(f"\nMost SELECTIVE layer (honest recognition):  layer {best_sel[0]}  "
          f"diff-of-means {best_sel[1]:.3f}, selectivity {best_sel[6]:.3f}  (logreg {best_sel[2]:.3f})")
    print(f"Highest raw diff-of-means layer:            layer {best_dm[0]}  "
          f"diff-of-means {best_dm[1]:.3f}, selectivity {best_dm[6]:.3f}")
    print("\nHonest monitor headline = diff-of-means AUROC at the most-selective layer.")
    print("logreg shown for reference only (low-selectivity here; treat as upper bound).")


if __name__ == "__main__":
    main()
