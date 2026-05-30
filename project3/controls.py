"""Probe validation controls — is the probe reading recognition, or just fitting structure?

Runs three families of control on a saved activation .npz, reusing the EXACT probe
and cross-validation machinery from train_probe.py so every number is apples-to-apples
with the real result. Fully seeded — same inputs give the same numbers every time.

  1. SHUFFLE LABELS  (Hewitt & Liang 2019 random-label control)
     Permute the real labels and re-probe. With D (1024) > N, a logistic probe can
     separate ANY labelling in-sample; this checks our out-of-fold protocol doesn't
     let that leak. Expect ~0.5. A pass means the real AUROC is not a CV artefact.
     (Validates the logreg column specifically; diff-of-means can't overfit this way.)

  2. ARBITRARY PROPERTIES  (selectivity calibration)
     Predict real-but-task-irrelevant facts about the input (destination alphabetical
     half, item-name length parity, phrasing template). Calibrates how much arbitrary
     structure is linearly decodable at all. If these score near the real task, the
     representation is a generic linear soup and the real number is less special.

  3. ITEM-IRRELEVANT MEMBERSHIP  (the sharpest, v2-specific)
     Predict whether a category the item does NOT belong to is on the restricted list.
     Same computation type as the real task (read the list) minus the item->category
     step. Much lower than real => the representation specifically encodes the
     item-cued match (recognition). Ties real => it just encodes the whole list.

All controls run at the real task's best layer, stratified k-fold OOF AUROC
(logreg + diff-of-means). Selectivity = real logreg AUROC - control logreg AUROC.

Usage:
    python controls.py --activations activations_conditions_v2.npz --dataset inputs/conditions_v2.json
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

# Reuse the SAME probe + CV as the main analysis — single source of truth.
from train_probe import logreg_scores, diffmeans_scores, pooled_oof_auroc, make_cv_splitter


def load_aligned(activations_path: str, dataset_path: str):
    """Load the npz and align dataset records to the activation order via id."""
    data = np.load(activations_path, allow_pickle=True)
    ids = [str(i) for i in data["ids"]]
    by_id = {r["id"]: r for r in json.load(open(dataset_path))}
    recs = [by_id[i] for i in ids]
    return data, recs


def both_auroc(X, y, cv):
    """logreg and diff-of-means pooled out-of-fold AUROC (groups=None => stratified)."""
    return (
        pooled_oof_auroc(X, y, None, cv, logreg_scores),
        pooled_oof_auroc(X, y, None, cv, diffmeans_scores),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--activations", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--layer", type=int, default=-1, help="Layer to probe; -1 = auto (real task's best).")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--shuffles", type=int, default=5, help="Number of random-label permutations to average.")
    args = parser.parse_args()

    data, recs = load_aligned(args.activations, args.dataset)
    activations = data["activations"]
    y = data["labels"].astype(int)
    cv = make_cv_splitter("random", None, args.seed)

    # Pick the layer: real task's best logreg OOF, unless overridden.
    if args.layer < 0:
        scores = [(li, pooled_oof_auroc(activations[:, li, :], y, None, cv, logreg_scores))
                  for li in range(activations.shape[1])]
        layer, _ = max(scores, key=lambda t: t[1])
    else:
        layer = args.layer
    X = activations[:, layer, :]

    real_lr, real_dm = both_auroc(X, y, cv)

    print(f"Activations: {args.activations}  |  N={len(y)}  |  probing layer {layer}")
    print(f"seed={args.seed}, stratified 5-fold OOF\n")
    print(f"{'task':<34} | {'logreg':>7} | {'diffmean':>8} | {'selectivity':>11} | base rate")
    print("-" * 86)
    print(f"{'REAL (escalation)':<34} | {real_lr:>7.3f} | {real_dm:>8.3f} | {'—':>11} | {y.mean():.2f}")

    def row(name, yc):
        if len(set(yc.tolist())) < 2:
            print(f"{name:<34} | {'skip':>7} | {'(one class)':>8} |")
            return
        lr, dm = both_auroc(X, yc, cv)
        print(f"{name:<34} | {lr:>7.3f} | {dm:>8.3f} | {real_lr - lr:>11.3f} | {yc.mean():.2f}")

    # --- 1. Shuffle labels (averaged over permutations) ---
    sh_lr, sh_dm = [], []
    for s in range(args.shuffles):
        yp = y.copy()
        np.random.default_rng(args.seed * 1000 + s).shuffle(yp)
        lr, dm = both_auroc(X, yp, cv)
        sh_lr.append(lr); sh_dm.append(dm)
    print(f"{'shuffle labels (mean of %d)' % args.shuffles:<34} | {np.mean(sh_lr):>7.3f} | "
          f"{np.mean(sh_dm):>8.3f} | {real_lr - np.mean(sh_lr):>11.3f} | (random)")
    print(f"{'   shuffle labels (worst of %d)' % args.shuffles:<34} | {np.max(sh_lr):>7.3f} | "
          f"{np.max(sh_dm):>8.3f} | {real_lr - np.max(sh_lr):>11.3f} |")

    # --- 2. Arbitrary / surface properties ---
    dest_alpha = np.array([1 if r["meta"]["destination"][0].upper() >= "M" else 0 for r in recs])
    item_parity = np.array([1 if len(r["meta"]["item"].replace(" ", "")) % 2 == 0 else 0 for r in recs])
    phrasing = np.array([1 if r["meta"].get("phrasing", 0) >= 2 else 0 for r in recs])
    row("junk: destination alpha-half", dest_alpha)
    row("junk: item-name length parity", item_parity)
    row("surface: phrasing template", phrasing)

    # --- 3. Item-irrelevant membership (v2 only) ---
    if "category" in recs[0]["meta"] and "restricted_categories" in recs[0]["meta"]:
        all_cats = sorted(
            {r["meta"]["category"] for r in recs}
            | {c for r in recs for c in r["meta"]["restricted_categories"]}
        )
        irng = random.Random(args.seed + 7)
        yc = []
        for r in recs:
            item_cat = r["meta"]["category"]
            listed = set(r["meta"]["restricted_categories"])
            non_item = [c for c in all_cats if c != item_cat]
            in_list = [c for c in non_item if c in listed]
            out_list = [c for c in non_item if c not in listed]
            target = irng.randint(0, 1)
            if target == 1 and in_list:
                yc.append(1)
            elif target == 0 and out_list:
                yc.append(0)
            else:
                yc.append(1 if in_list else 0)
        yc = np.array(yc)
        corr = float(np.corrcoef(y, yc)[0, 1])
        print(f"{'(item-irrelevant corr with real: %.2f)' % corr:<34} |")
        row("item-IRRELEVANT membership", yc)

    print("-" * 86)
    print("\nReading: shuffle should sit at ~0.5 (pipeline is honest). Junk/surface rows set the")
    print("baseline of 'arbitrary decodable structure'. If REAL clears them — and clears")
    print("item-irrelevant membership — the probe is reading the item-cued recognition, not soup.")


if __name__ == "__main__":
    main()
