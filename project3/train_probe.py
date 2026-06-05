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
import socket
from datetime import datetime, timezone

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

    pos, neg = y == 1, y == 0
    missed = pos & (behaviour != "escalate")       # should-escalate cases the model didn't escalate
    alarm = neg & (behaviour == "escalate")        # should-proceed cases the model escalated
    n_missed, n_alarm = int(missed.sum()), int(alarm.sum())
    missed_caught = int((probe_pred[missed] == 1).sum()) if n_missed else 0
    alarm_caught = int((probe_pred[alarm] == 0).sum()) if n_alarm else 0

    print("\n=== Recognition (probe) vs behaviour (model output) ===")
    print(f"layer {layer}, probe threshold 0.5 on out-of-fold probability")
    print(f"  behaviour parsed: {int((behaviour == 'escalate').sum())} escalate / "
          f"{int((behaviour == 'proceed').sum())} proceed / {int((behaviour == 'unclear').sum())} unclear")
    print(f"  behavioural accuracy vs ground truth: {beh_correct.mean():.3f}")
    print(f"  probe accuracy @ layer {layer} (thresh 0.5): {probe_correct.mean():.3f}")

    # The monitor payoff: should-escalate cases the model behaviourally MISSED —
    # did the probe catch them?
    if n_missed > 0:
        print(f"\n  should-escalate behavioural MISSES: {n_missed}/{int(pos.sum())}")
        print(f"    of those, probe correctly flagged escalate: {missed_caught}/{n_missed} "
              f"({missed_caught / n_missed:.2f})   <-- the monitor payoff")
    else:
        print("\n  no behavioural misses on should-escalate cases — nothing for the probe to "
              "catch here; need a harder setting to test the monitor claim.")

    if n_alarm > 0:
        print(f"  should-proceed behavioural FALSE ALARMS: {n_alarm}/{int(neg.sum())}")
        print(f"    of those, probe correctly said proceed: {alarm_caught}/{n_alarm} ({alarm_caught / n_alarm:.2f})")

    print("\n  2x2  (rows: probe correct?   cols: behaviour correct?)")
    print("            behav OK   behav WRONG")
    print(f"   probe OK    {int((probe_correct & beh_correct).sum()):>5}      {int((probe_correct & ~beh_correct).sum()):>5}   <- probe right where behaviour wrong")
    print(f"   probe WRONG {int((~probe_correct & beh_correct).sum()):>5}      {int((~probe_correct & ~beh_correct).sum()):>5}")

    return {
        "layer": int(layer),
        "behaviour_accuracy": float(beh_correct.mean()),
        "probe_accuracy": float(probe_correct.mean()),
        "behaviour_counts": {
            "escalate": int((behaviour == "escalate").sum()),
            "proceed": int((behaviour == "proceed").sum()),
            "unclear": int((behaviour == "unclear").sum()),
        },
        "monitor_payoff": {
            "should_escalate_misses": n_missed,
            "probe_caught": missed_caught,
            "fraction": (missed_caught / n_missed) if n_missed else None,
        },
        "false_alarms": {
            "should_proceed_false_alarms": n_alarm,
            "probe_caught": alarm_caught,
            "fraction": (alarm_caught / n_alarm) if n_alarm else None,
        },
        "confusion_2x2": {
            "probe_ok_behav_ok": int((probe_correct & beh_correct).sum()),
            "probe_ok_behav_wrong": int((probe_correct & ~beh_correct).sum()),
            "probe_wrong_behav_ok": int((~probe_correct & beh_correct).sum()),
            "probe_wrong_behav_wrong": int((~probe_correct & ~beh_correct).sum()),
        },
    }


def verdict(auroc: float) -> str:
    if auroc > GO_THRESHOLD:
        return "GO (strong signal — proceed to deeper work)"
    if auroc >= KILL_THRESHOLD:
        return "AMBIGUOUS (design a harder test)"
    return "KILL (signal too weak — pivot or drop the idea)"


def write_results_json(out_path, args, meta, results, best_li, best_lr_oof, n, n_pos, hidden_dim, n_layers, decomposition):
    """Persist the run's numbers + provenance to a durable, parseable JSON record.

    Stdout dies with a frozen terminal; this file doesn't. It's also what gets read
    straight into runlog.md — no hand-transcription. Carries the full reproducibility
    footprint: git commit + the torch/transformers/sklearn versions actually used,
    and UTC timestamps (so the record means the same instant on any machine).
    """
    import sklearn

    record = {
        "analysis_utc": datetime.now(timezone.utc).isoformat(),
        "host": socket.gethostname(),
        "activations_file": args.activations,
        "model": meta.get("model"),
        "dtype": meta.get("dtype"),
        "enable_thinking": meta.get("enable_thinking"),
        "dataset_path": meta.get("dataset_path"),
        "git_commit": meta.get("git_commit"),
        "extraction_utc": meta.get("created_utc"),
        "env": {
            "torch": meta.get("torch_version"),
            "transformers": meta.get("transformers_version"),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "split_mode": args.split_mode,
        "seed": args.seed,
        "n": int(n),
        "n_escalate": int(n_pos),
        "n_proceed": int(n - n_pos),
        "hidden_dim": int(hidden_dim),
        "n_hidden_state_indices": int(n_layers),
        "per_layer": [
            {"layer": int(li), "logreg_oof": float(lr), "diffmean_oof": float(dm), "logreg_split": float(sp)}
            for (li, lr, dm, sp) in results
        ],
        "best_layer_logreg_oof": int(best_li),
        "best_logreg_oof_auroc": float(best_lr_oof),
        "verdict": verdict(best_lr_oof),
        "decomposition": decomposition,
    }
    with open(out_path, "w") as f:
        json.dump(record, f, indent=2)
    print(f"\nWrote results record: {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--activations", default="activations.npz")
    parser.add_argument("--split-mode", default="random", choices=["random", "group"],
                        help="random = stratified k-fold (default). group = leave-country-out (harder generalisation).")
    parser.add_argument("--layers", default="all",
                        help="Comma-separated hidden-state indices to probe (e.g. 8,16,24), or 'all'.")
    parser.add_argument("--test-frac", type=float, default=0.2, help="Held-out fraction for the single split.")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--results-out", default=None,
                        help="Path for the durable JSON results record (default: alongside the .npz, "
                             "e.g. activations_foo.results.json). Pass '' to skip writing it.")
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

    decomposition = None
    if "behaviour" in data:
        decomposition = decompose(activations[:, best_li, :], y, data["behaviour"], best_li, cv, cv_groups)

    if args.results_out != "":
        out_path = args.results_out or (args.activations.rsplit(".npz", 1)[0] + ".results.json")
        write_results_json(out_path, args, meta, results, best_li, best_lr_oof, n, int(y.sum()),
                           hidden_dim, n_layers, decomposition)


if __name__ == "__main__":
    main()
