"""CPU step: train linear probes on the dumped activations and report AUROC.

Reads the `.npz` from extract_activations.py and, for every captured layer,
trains a linear probe to predict the label (escalate / proceed) from the
final-prompt-token activation. Reports AUROC per layer.

What a high AUROC means with *this* dataset
--------------------------------------------
The dataset is built so nothing on the surface predicts the label: every
destination country appears equally as escalate and proceed, and restricted
status is arbitrary per example (set by that example's randomised list). So a
probe can only score above chance by reading whether the model recognised the
destination is on the current list — i.e. the condition-recognition signal we
are after. (See make_dataset.py for the full argument.)

Pure numpy + scikit-learn, so it runs in a second on a laptop. Iterate freely
once the GPU step has dumped activations.

Splits
------
- random (default): stratified k-fold. Fine here because, unlike the old paired
  dataset, there are no near-duplicate examples to leak across the split.
- group: leave-country-out (GroupKFold on destination). A stronger test — the
  probe must flag/clear destinations it never saw in training. If the condition
  signal is genuine it should transfer to unseen countries; if it were keyed on
  specific country tokens, this is where it would fall apart.

Both report pooled out-of-fold AUROC (every example scored once while held out,
then one AUROC over all of them), plus a single held-out split for reference.

Usage
-----
    python train_probe.py --activations activations.npz
    python train_probe.py --activations activations.npz --split-mode group
    python train_probe.py --activations activations.npz --layers 8,16,24
"""

from __future__ import annotations

import argparse
import json

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold, GroupShuffleSplit, StratifiedKFold, train_test_split
from sklearn.preprocessing import StandardScaler

# Pre-registered decision thresholds (project3/README.md).
GO_THRESHOLD = 0.80
KILL_THRESHOLD = 0.65


def logreg_scores(X, y, train_idx, test_idx):
    """Fit a standardised logistic-regression probe on train, score test."""
    scaler = StandardScaler().fit(X[train_idx])
    clf = LogisticRegression(max_iter=1000, C=1.0)
    clf.fit(scaler.transform(X[train_idx]), y[train_idx])
    return clf.predict_proba(scaler.transform(X[test_idx]))[:, 1]


def diffmeans_scores(X, y, train_idx, test_idx):
    """Fit a difference-of-means probe on train, score test.

    Direction = mean(positive activations) - mean(negative activations) in
    standardised space; the test score is the projection onto that direction.
    A one-direction probe that can't really overfit — a useful cross-check that
    a high logreg AUROC isn't just high-dimensional overfitting.
    """
    scaler = StandardScaler().fit(X[train_idx])
    Xtr = scaler.transform(X[train_idx])
    ytr = y[train_idx]
    direction = Xtr[ytr == 1].mean(axis=0) - Xtr[ytr == 0].mean(axis=0)
    return scaler.transform(X[test_idx]) @ direction


def pooled_oof_auroc(X, y, groups, splitter, score_fn):
    """Collect out-of-fold scores across all folds, then compute one AUROC.

    `groups` is None for stratified k-fold (passing it would trigger a noisy
    'groups is ignored' warning) and the destination array for GroupKFold.
    """
    oof = np.full(len(y), np.nan)
    for train_idx, test_idx in splitter.split(X, y, groups):
        oof[test_idx] = score_fn(X, y, train_idx, test_idx)
    assert not np.isnan(oof).any(), "some samples were never held out"
    return roc_auc_score(y, oof)


def single_split_auroc(X, y, groups, split_mode, test_frac, seed, score_fn):
    """A single held-out split, for reference alongside the pooled metric."""
    if split_mode == "group":
        gss = GroupShuffleSplit(n_splits=1, test_size=test_frac, random_state=seed)
        train_idx, test_idx = next(gss.split(X, y, groups))
    else:
        idx = np.arange(len(y))
        train_idx, test_idx = train_test_split(idx, test_size=test_frac, random_state=seed, stratify=y)
    return roc_auc_score(y[test_idx], score_fn(X, y, train_idx, test_idx))


def make_cv_splitter(split_mode, groups, seed):
    if split_mode == "group":
        return GroupKFold(n_splits=min(5, len(np.unique(groups))))
    return StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)


def decompose(X, y, behaviour, layer, cv, cv_groups):
    """Recognition (probe) vs behaviour (model output) at the chosen layer.

    The whole point of the project: does the probe read the trigger in cases where
    the model's *output* didn't surface it? Uses out-of-fold probe predictions
    (threshold 0.5) so the probe is never scoring examples it trained on. The best
    layer is chosen on this same data, so treat the numbers as a diagnostic.
    """
    oof = np.full(len(y), np.nan)
    for tr, te in cv.split(X, y, cv_groups):
        oof[te] = logreg_scores(X, y, tr, te)
    probe_pred = (oof >= 0.5).astype(int)

    behaviour = np.asarray(behaviour)
    gt_name = np.where(y == 1, "escalate", "proceed")
    beh_correct = behaviour == gt_name
    probe_correct = probe_pred == y

    print("\n=== Recognition (probe) vs behaviour (model output) ===")
    print(f"layer {layer}, probe threshold 0.5 on out-of-fold probability")
    print(f"  behaviour parsed: {int((behaviour == 'escalate').sum())} escalate / "
          f"{int((behaviour == 'proceed').sum())} proceed / {int((behaviour == 'unclear').sum())} unclear")
    print(f"  behavioural accuracy vs ground truth: {beh_correct.mean():.3f}")
    print(f"  probe accuracy @ layer {layer} (thresh 0.5): {probe_correct.mean():.3f}")

    # The monitor payoff: should-escalate cases the model behaviourally MISSED —
    # did the probe catch them?
    pos, neg = y == 1, y == 0
    missed = pos & (behaviour != "escalate")
    if missed.sum() > 0:
        caught = int((probe_pred[missed] == 1).sum())
        print(f"\n  should-escalate behavioural MISSES: {int(missed.sum())}/{int(pos.sum())}")
        print(f"    of those, probe correctly flagged escalate: {caught}/{int(missed.sum())} "
              f"({caught / missed.sum():.2f})   <-- the monitor payoff")
    else:
        print("\n  no behavioural misses on should-escalate cases — nothing for the probe to "
              "catch here; need a harder setting to test the monitor claim.")

    alarm = neg & (behaviour == "escalate")
    if alarm.sum() > 0:
        caught = int((probe_pred[alarm] == 0).sum())
        print(f"  should-proceed behavioural FALSE ALARMS: {int(alarm.sum())}/{int(neg.sum())}")
        print(f"    of those, probe correctly said proceed: {caught}/{int(alarm.sum())} ({caught / alarm.sum():.2f})")

    print("\n  2x2  (rows: probe correct?   cols: behaviour correct?)")
    print("            behav OK   behav WRONG")
    print(f"   probe OK    {int((probe_correct & beh_correct).sum()):>5}      {int((probe_correct & ~beh_correct).sum()):>5}   <- probe right where behaviour wrong")
    print(f"   probe WRONG {int((~probe_correct & beh_correct).sum()):>5}      {int((~probe_correct & ~beh_correct).sum()):>5}")


def verdict(auroc: float) -> str:
    if auroc > GO_THRESHOLD:
        return "GO (strong signal — proceed to deeper work)"
    if auroc >= KILL_THRESHOLD:
        return "AMBIGUOUS (design a harder test)"
    return "KILL (signal too weak — pivot or drop the idea)"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--activations", default="activations.npz")
    parser.add_argument("--split-mode", default="random", choices=["random", "group"],
                        help="random = stratified k-fold (default). group = leave-country-out (harder generalisation).")
    parser.add_argument("--layers", default="all",
                        help="Comma-separated hidden-state indices to probe (e.g. 8,16,24), or 'all'.")
    parser.add_argument("--test-frac", type=float, default=0.2, help="Held-out fraction for the single split.")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    data = np.load(args.activations, allow_pickle=True)
    activations = data["activations"]  # [N, L, D]
    y = data["labels"].astype(int)
    groups = data["groups"]
    meta = json.loads(str(data["meta"]))

    n, n_layers, hidden_dim = activations.shape
    print(f"Loaded {args.activations}")
    print(f"  model: {meta['model']}  |  N={n}  ({int(y.sum())} escalate / {n - int(y.sum())} proceed)")
    print(f"  {n_layers} hidden-state indices (index 0 = embeddings), hidden_dim={hidden_dim}")
    print(f"  split-mode: {args.split_mode}  |  CV: "
          f"{'leave-country-out (GroupKFold)' if args.split_mode == 'group' else 'stratified 5-fold'}")
    print()

    layer_indices = list(range(n_layers)) if args.layers == "all" else [int(x) for x in args.layers.split(",")]
    cv = make_cv_splitter(args.split_mode, groups, args.seed)
    # StratifiedKFold ignores groups (and warns); only GroupKFold needs them.
    cv_groups = groups if args.split_mode == "group" else None

    print(f"{'layer':>6} | {'logreg OOF':>11} | {'diffmean OOF':>12} | {'logreg split':>12}")
    print("-" * 52)
    results = []
    for li in layer_indices:
        X = activations[:, li, :]
        lr_oof = pooled_oof_auroc(X, y, cv_groups, cv, logreg_scores)
        dm_oof = pooled_oof_auroc(X, y, cv_groups, cv, diffmeans_scores)
        lr_split = single_split_auroc(X, y, groups, args.split_mode, args.test_frac, args.seed, logreg_scores)
        results.append((li, lr_oof, dm_oof, lr_split))
        label = f"{li}" + (" (emb)" if li == 0 else "")
        print(f"{label:>6} | {lr_oof:>11.3f} | {dm_oof:>12.3f} | {lr_split:>12.3f}")

    best_li, best_lr_oof, _, _ = max(results, key=lambda r: r[1])
    print("-" * 52)
    print(f"\nBest layer (logreg pooled OOF): layer {best_li}  AUROC = {best_lr_oof:.3f}")
    print(f"Pre-registered verdict: {verdict(best_lr_oof)}")
    print(f"  (thresholds: GO > {GO_THRESHOLD}, KILL < {KILL_THRESHOLD})")

    if "behaviour" in data:
        decompose(activations[:, best_li, :], y, data["behaviour"], best_li, cv, cv_groups)


if __name__ == "__main__":
    main()
