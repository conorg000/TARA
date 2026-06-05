"""The pivot experiment (advisor step 1+2): truth-probe vs BELIEF-probe, and the litmus.

Everything so far trained the probe on GROUND TRUTH (is the item restricted). That
probe decodes truth — which on v3-L0 diverges from the model's own recognition (the
direct-ask showed the model calls 24/33 silent misses "not restricted"). So
probe-high + action-low was never evidence of "knew but didn't act"; it was a
ground-truth oracle sitting next to a model that disagrees with the label.

This script builds the probe the project actually wants: trained on the MODEL'S OWN
ANSWER, not on truth. Two changes from train_probe, nothing else:
  1. Activations come from the ACTION rollout (engagement: recognition while doing
     the task, with nothing pointing attention at the condition).
  2. Labels come from the model's DIRECT-ASK answer (says-restricted vs says-not),
     aligned by id. Truth labels are discarded for the belief probe.

The litmus (advisor step 2) — the single decisive read:
  Take the items where truth=restricted but the model said NO (the co-failure /
  silent-miss set). The TRUTH probe reads them HIGH (it follows truth). A genuine
  recognition detector — the BELIEF probe — should read them LOW (it follows the
  model's mistaken belief).
    - Belief reads LOW  -> a recognition axis distinct from truth exists. Proceed.
    - Belief reads HIGH -> no internal "I think it's fine" separate from truth that
      we can decode here (or too few disagreement items to learn one).

Honest caveats this script is built to surface, not hide:
  * A PASS proves belief != truth. It does NOT prove belief != action: on v3-L0 the
    model's ask-answer and its action almost always agree, so a probe trained on ask
    labels is ~the same probe as one trained on action labels. Separating belief from
    action needs a lever where ask=YES while action=NO (the load regime). We print the
    ask-vs-action agreement so this is explicit.
  * A FAIL is weaker than a PASS: belief and truth agree ~82% here, so the diff-of-means
    direction is dominated by the agreement bulk and looks like the truth axis almost by
    construction. logreg has more freedom to find a minority belief direction, so we run
    BOTH and read them per the usual diffmean-trustworthy / logreg-upper-bound convention.

Usage:
    python belief_probe.py \
        --action activations_conditions_v3_obj0_action.npz \
        --ask    activations_conditions_v3_obj0_ask.npz
"""

from __future__ import annotations

import argparse
import json
import socket
from datetime import datetime, timezone

import numpy as np
from sklearn.metrics import roc_auc_score

from train_probe import logreg_scores, diffmeans_scores, make_cv_splitter


def oof(score_fn, X, y, cv):
    """Pooled out-of-fold scores, aligned to the input order (each item scored once, held out)."""
    out = np.full(len(y), np.nan)
    for tr, te in cv.split(X, y, None):
        out[te] = score_fn(X, y, tr, te)
    assert not np.isnan(out).any(), "some item was never held out"
    return out


def dm_predicted_restricted(oof_dm, y):
    """Threshold diff-of-means OOF projections at the midpoint between the two class means.

    diff-of-means scores are projections, not probabilities, so there's no 0.5; the
    principled, reproducible boundary is halfway between the positive- and negative-class
    OOF means. Returns a boolean 'called restricted' per item.
    """
    thr = 0.5 * (oof_dm[y == 1].mean() + oof_dm[y == 0].mean())
    return oof_dm > thr


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--action", required=True, help="action-framing npz (rollout activations + truth labels)")
    ap.add_argument("--ask", required=True, help="ask-framing npz (model's direct-ask answer in 'behaviour')")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--results-out", default=None, help="JSON record path (default alongside the action npz)")
    args = ap.parse_args()

    A = np.load(args.action, allow_pickle=True)
    Q = np.load(args.ask, allow_pickle=True)
    ids_a, ids_q = list(A["ids"]), list(Q["ids"])
    assert ids_a == ids_q, "action/ask npz ids are not aligned — cannot join labels"

    meta = json.loads(str(A["meta"]))
    activations = A["activations"]                                   # [N, L, D] from the ACTION rollout
    truth = A["labels"].astype(int)                                  # 1 = truly restricted
    action = np.array([str(x) for x in A["behaviour"]])             # escalate / proceed / unclear
    ask = np.array([str(x) for x in Q["behaviour"]])               # escalate(=YES) / proceed(=NO) / unclear

    # Belief label = the model's own direct-ask answer. Drop ask=unclear (no clean belief).
    clean = np.isin(ask, ["escalate", "proceed"])
    belief = (ask == "escalate").astype(int)                        # 1 = model SAYS restricted

    Xall = activations[clean]
    truth_c = truth[clean]
    belief_c = belief[clean]
    action_c = action[clean]
    n, n_layers, hidden = Xall.shape

    # The litmus subset: truth=restricted but the model SAID not-restricted.
    flip = (truth_c == 1) & (belief_c == 0)
    n_flip = int(flip.sum())

    print(f"action npz : {args.action}")
    print(f"ask    npz : {args.ask}")
    print(f"model      : {meta.get('model')}   git {meta.get('git_commit')}   extracted {meta.get('created_utc')}")
    print(f"\nUsable items (ask clean): {n}/{len(truth)}  (dropped {int((~clean).sum())} ask-unclear)")
    print(f"  truth   : {int(truth_c.sum())} restricted / {n - int(truth_c.sum())} not")
    print(f"  belief  : {int(belief_c.sum())} says-restricted / {n - int(belief_c.sum())} says-not")
    print(f"  ask vs action agreement: {float((belief_c == (action_c == 'escalate')).mean()):.3f}"
          f"   <- near 1.0 means belief-probe and action-probe share ~the same labels here (the caveat)")
    print(f"  belief vs truth agreement: {float((belief_c == truth_c).mean()):.3f}")
    print(f"\nLITMUS subset (truth=restricted & model-says-NO): {n_flip} items")
    print("  expect: TRUTH probe reads these HIGH; a real BELIEF probe reads them LOW.\n")

    cv = make_cv_splitter("random", None, args.seed)

    print(f"{'layer':>5} | {'truth_dm':>8} {'truth_lr':>8} | {'belief_dm':>9} {'belief_lr':>9}"
          f" | {'T->flip%R':>9} {'B->flip%R':>9}")
    print("-" * 78)

    rows = []
    for li in range(n_layers):
        X = Xall[:, li, :]
        # Probe vs TRUTH (the old probe) and vs BELIEF (the new probe), OOF AUROC.
        t_dm_s, t_lr_s = oof(diffmeans_scores, X, truth_c, cv), oof(logreg_scores, X, truth_c, cv)
        b_dm_s, b_lr_s = oof(diffmeans_scores, X, belief_c, cv), oof(logreg_scores, X, belief_c, cv)
        t_dm, t_lr = roc_auc_score(truth_c, t_dm_s), roc_auc_score(truth_c, t_lr_s)
        b_dm, b_lr = roc_auc_score(belief_c, b_dm_s), roc_auc_score(belief_c, b_lr_s)

        # Litmus readout: fraction of the flip items each probe CALLS restricted (logreg P>=0.5).
        t_flip_frac = float((t_lr_s[flip] >= 0.5).mean()) if n_flip else float("nan")
        b_flip_frac = float((b_lr_s[flip] >= 0.5).mean()) if n_flip else float("nan")
        # ...and the mean predicted P(restricted) on the flip items (the advisor's "~0.95 vs LOW").
        t_flip_p = float(t_lr_s[flip].mean()) if n_flip else float("nan")
        b_flip_p = float(b_lr_s[flip].mean()) if n_flip else float("nan")
        # diff-of-means version of the same litmus, midpoint threshold.
        t_flip_dm = float(dm_predicted_restricted(t_dm_s, truth_c)[flip].mean()) if n_flip else float("nan")
        b_flip_dm = float(dm_predicted_restricted(b_dm_s, belief_c)[flip].mean()) if n_flip else float("nan")

        rows.append(dict(layer=li, truth_dm=t_dm, truth_lr=t_lr, belief_dm=b_dm, belief_lr=b_lr,
                         truth_flip_frac=t_flip_frac, belief_flip_frac=b_flip_frac,
                         truth_flip_p=t_flip_p, belief_flip_p=b_flip_p,
                         truth_flip_dm_frac=t_flip_dm, belief_flip_dm_frac=b_flip_dm))
        print(f"{li:>5} | {t_dm:>8.3f} {t_lr:>8.3f} | {b_dm:>9.3f} {b_lr:>9.3f}"
              f" | {t_flip_frac:>9.2f} {b_flip_frac:>9.2f}")

    # Headline layers: where each probe is best at its OWN target (logreg OOF), per train_probe's choice.
    best_truth = max(rows, key=lambda r: r["truth_lr"])
    best_belief = max(rows, key=lambda r: r["belief_lr"])
    print("-" * 78)
    print(f"\nBest TRUTH layer  (predicts truth):       L{best_truth['layer']}  "
          f"dm {best_truth['truth_dm']:.3f} / lr {best_truth['truth_lr']:.3f}")
    print(f"Best BELIEF layer (predicts model's ask): L{best_belief['layer']}  "
          f"dm {best_belief['belief_dm']:.3f} / lr {best_belief['belief_lr']:.3f}"
          f"   <- can the rollout predict what the model would SAY? (gate: >0.5 = decodable)")

    print(f"\n=== LITMUS (the {n_flip} truth=restricted / model-says-NO items) ===")
    for name, r in [("best BELIEF layer", best_belief), ("best TRUTH layer", best_truth)]:
        print(f"  @ L{r['layer']} ({name}):")
        print(f"    TRUTH  probe calls restricted: {r['truth_flip_frac']*n_flip:.0f}/{n_flip} "
              f"({r['truth_flip_frac']:.2f}), mean P={r['truth_flip_p']:.2f}  [dm {r['truth_flip_dm_frac']:.2f}]")
        print(f"    BELIEF probe calls restricted: {r['belief_flip_frac']*n_flip:.0f}/{n_flip} "
              f"({r['belief_flip_frac']:.2f}), mean P={r['belief_flip_p']:.2f}  [dm {r['belief_flip_dm_frac']:.2f}]")

    print("\nRead: BELIEF << TRUTH on the flip items => recognition axis distinct from truth (PASS).")
    print("      BELIEF ~= TRUTH                    => no separable belief axis here (FAIL; see caveats in docstring).")

    out_path = args.results_out or (args.action.rsplit(".npz", 1)[0] + ".belief.results.json")
    if out_path:
        import sklearn
        record = {
            "analysis_utc": datetime.now(timezone.utc).isoformat(),
            "host": socket.gethostname(),
            "experiment": "belief_probe_litmus (advisor step 1+2)",
            "action_file": args.action,
            "ask_file": args.ask,
            "model": meta.get("model"),
            "git_commit_extract": meta.get("git_commit"),
            "env": {"numpy": np.__version__, "scikit_learn": sklearn.__version__},
            "n_clean": int(n),
            "n_ask_unclear_dropped": int((~clean).sum()),
            "counts": {
                "truth_restricted": int(truth_c.sum()),
                "belief_says_restricted": int(belief_c.sum()),
                "ask_vs_action_agreement": float((belief_c == (action_c == "escalate")).mean()),
                "belief_vs_truth_agreement": float((belief_c == truth_c).mean()),
                "litmus_flip_n": n_flip,
            },
            "best_truth_layer": best_truth["layer"],
            "best_belief_layer": best_belief["layer"],
            "per_layer": rows,
            "litmus": {
                "at_best_belief_layer": {
                    "layer": best_belief["layer"],
                    "truth_calls_restricted_frac": best_belief["truth_flip_frac"],
                    "belief_calls_restricted_frac": best_belief["belief_flip_frac"],
                    "truth_mean_p": best_belief["truth_flip_p"],
                    "belief_mean_p": best_belief["belief_flip_p"],
                },
                "at_best_truth_layer": {
                    "layer": best_truth["layer"],
                    "truth_calls_restricted_frac": best_truth["truth_flip_frac"],
                    "belief_calls_restricted_frac": best_truth["belief_flip_frac"],
                    "truth_mean_p": best_truth["truth_flip_p"],
                    "belief_mean_p": best_truth["belief_flip_p"],
                },
            },
        }
        with open(out_path, "w") as f:
            json.dump(record, f, indent=2)
        print(f"\nWrote results record: {out_path}")


if __name__ == "__main__":
    main()
