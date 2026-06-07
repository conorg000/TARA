"""Step 2 (plan_07_june): train-on-ask / test-on-action cross-pass probe.

The idea that makes this confound-proof: train the recognition probe ONLY on the
ASK pass (the model is doing pure recognition there, no action to take), freeze it,
then apply it to the ACTION pass. A probe that has never seen an action cannot be
reading "about to act" — so if it fires on the action pass, it's reading recognition.

This script does the laptop-side analysis on the two .npz files produced by
extract_v6.sh (ask + action passes of conditions_v6, same items, Qwen3-32B no-think):

  1. Re-grade each pass's behaviour from the saved generated_text with the
     bracket-tolerant parser (markers.classify), so labels match the gate.
  2. Recognition label y := the model's ASK answer (YES=1 / NO=0), dropping unclear.
  3. Per layer:
       - in-pass (ask) OOF AUROC  — sanity: does the probe read recognition within
         the ask pass at all? (diff-of-means led, logreg as upper bound.)
       - CROSS-PASS AUROC         — freeze the probe on ALL ask activations, score
         the ACTION activations of the same items vs the same y. THIS is the Step-2
         result: does the ask-trained recognition direction survive into the action
         pass?
  4. Step-3 PREVIEW at the best cross-pass layer: among restricted items the action
     PROCEEDED on, the frozen probe's score for ask-YES (recognise-but-proceed) vs
     ask-NO (genuine miss). Tiny N at baseline — a preview, not the measurement.

Lead with diff-of-means (low-capacity, trustworthy); treat logreg as an upper bound
(project convention, CLAUDE.md). High cross-pass AUROC = transfer = green light for
Step 3. Collapse = recognition differs across passes; study that before load.

Usage:
    ./.venv/bin/python cross_pass_probe.py \
        --ask activations_conditions_v6_ask_32b.npz \
        --action activations_conditions_v6_action_32b.npz
"""

from __future__ import annotations

import argparse
import json

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

from markers import classify
from train_probe import logreg_scores, diffmeans_scores, pooled_oof_auroc, make_cv_splitter


def load_pass(npz_path: str, pos: str, neg: str):
    """Load one pass; return (acts[N,L+1,D], id->row, regraded answer per row)."""
    d = np.load(npz_path, allow_pickle=True)
    acts = d["activations"]
    ids = [str(x) for x in d["ids"]]
    labels = d["labels"].astype(int)
    groups = [str(x) for x in d["groups"]]
    # Prefer re-grading the saved generation (bracket-tolerant); fall back to the
    # stored behaviour field if generated_text wasn't captured.
    if "generated_text" in d:
        ans = [classify(str(t), pos, neg) for t in d["generated_text"]]
    elif "behaviour" in d:
        m = {"escalate": pos.upper(), "proceed": neg.upper(), "unclear": "UNCLEAR"}
        ans = [m.get(str(b), "UNCLEAR") for b in d["behaviour"]]
    else:
        raise SystemExit(f"{npz_path}: no generated_text or behaviour — rerun extract with --generate")
    return acts, ids, labels, groups, ans


def cross_pass_score(X_train, y_train, X_test, kind):
    """Freeze a probe on ASK (X_train, y_train), return its scores on ACTION X_test."""
    scaler = StandardScaler().fit(X_train)
    Xtr = scaler.transform(X_train)
    if kind == "logreg":
        clf = LogisticRegression(max_iter=1000, C=1.0).fit(Xtr, y_train)
        return clf.predict_proba(scaler.transform(X_test))[:, 1]
    direction = Xtr[y_train == 1].mean(axis=0) - Xtr[y_train == 0].mean(axis=0)
    return scaler.transform(X_test) @ direction


def crosspass_oof(Xask, Xact, y, splitter, kind, groups=None):
    """Held-out cross-pass AUROC: per fold, fit the probe on ASK[train items], score
    ACTION[test items]; pool out-of-fold, one AUROC. No item's label is ever seen in
    its own evaluation, so this isn't inflated by per-item ask/action correlation
    (the bug the 0.6B smoke caught: in-sample cross-pass exceeded held-out in-pass).

    `groups` (e.g. matched-pair stems) is passed to the splitter so both halves of a
    pair land in the same fold — without it, a pair's near-identical present/absent
    documents split across train/test and the AUROC is inflated."""
    oof = np.full(len(y), np.nan)
    for tr, te in splitter.split(Xask, y, groups):
        oof[te] = cross_pass_score(Xask[tr], y[tr], Xact[te], kind)
    assert not np.isnan(oof).any(), "some items never held out"
    return roc_auc_score(y, oof)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ask", required=True, help="ask-pass .npz")
    ap.add_argument("--action", required=True, help="action-pass .npz")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--split-mode", choices=["random", "group", "pair"], default="random",
                    help="random=stratified 5-fold; group=GroupKFold on the npz groups field; "
                         "pair=GroupKFold on the matched-pair stem (id minus trailing a/b). "
                         "Use 'pair' for matched-pair datasets (keyphrase): otherwise a pair's "
                         "near-identical present/absent halves split across train/test and inflate AUROC.")
    ap.add_argument("--out", default=None, help="results JSON (default: <action>.crosspass.json)")
    args = ap.parse_args()

    A_acts, A_ids, A_lab, A_grp, A_ans = load_pass(args.ask, "YES", "NO")
    C_acts, C_ids, C_lab, C_grp, C_ans = load_pass(args.action, "ESCALATE", "PROCEED")

    # Align by id (intersection, stable order from the ask pass).
    C_row = {i: k for k, i in enumerate(C_ids)}
    A_row = {i: k for k, i in enumerate(A_ids)}
    common = [i for i in A_ids if i in C_row]

    # Recognition label = ask answer (YES/NO); drop unclear.
    keep, y, lab, grp, act_decision = [], [], [], [], []
    for i in common:
        a = A_ans[A_row[i]]
        if a not in ("YES", "NO"):
            continue
        keep.append(i)
        y.append(1 if a == "YES" else 0)
        lab.append(int(A_lab[A_row[i]]))
        grp.append(A_grp[A_row[i]])
        act_decision.append(C_ans[C_row[i]])
    y = np.array(y); lab = np.array(lab)
    ask_rows = [A_row[i] for i in keep]
    act_rows = [C_row[i] for i in keep]
    n_layers = A_acts.shape[1]
    print(f"aligned {len(keep)} items (dropped {len(common) - len(keep)} unclear-ask); "
          f"ask-YES={int(y.sum())} ask-NO={int((1 - y).sum())}")

    # Fold groups for the chosen split mode. 'pair' derives the matched-pair stem from the id
    # (w3_0000a / w3_0000b -> w3_0000) so both halves always share a fold.
    if args.split_mode == "pair":
        cv_groups = np.array([i[:-1] for i in keep])
    elif args.split_mode == "group":
        cv_groups = np.array(grp)
    else:
        cv_groups = None
    # Safety: warn if matched pairs are present but folds aren't pair-disjoint.
    looks_paired = len(keep) and all(i[-1] in "ab" for i in keep) and len(set(i[:-1] for i in keep)) < len(keep)
    if looks_paired and args.split_mode != "pair":
        print(f"  WARNING: data looks matched-paired (ids end a/b) but --split-mode={args.split_mode}; "
              f"a pair's halves can split across train/test and inflate AUROC. Use --split-mode pair.")
    cv = make_cv_splitter("group" if cv_groups is not None else "random", cv_groups, args.seed)
    print(f"  split-mode={args.split_mode} ({len(set(map(str, cv_groups))) if cv_groups is not None else '5'} groups)")
    rows = []
    for li in range(n_layers):
        Xa = A_acts[ask_rows][:, li, :]      # ask-pass activations at layer li
        Xc = C_acts[act_rows][:, li, :]      # action-pass activations, same items
        inpass_dm = pooled_oof_auroc(Xa, y, cv_groups, cv, diffmeans_scores)
        inpass_lr = pooled_oof_auroc(Xa, y, cv_groups, cv, logreg_scores)
        cross_dm = crosspass_oof(Xa, Xc, y, cv, "diffmeans", cv_groups)
        cross_lr = crosspass_oof(Xa, Xc, y, cv, "logreg", cv_groups)
        rows.append((li, inpass_dm, inpass_lr, cross_dm, cross_lr))

    print("\nlayer | ask in-pass (dm / lr) | CROSS-PASS ask->action (dm / lr)")
    for li, idm, ilr, cdm, clr in rows:
        print(f"  {li:2d}  |   {idm:.3f} / {ilr:.3f}      |   {cdm:.3f} / {clr:.3f}")

    best = max(rows, key=lambda r: r[3])  # by cross-pass diff-of-means (trustworthy)
    bli = best[0]
    print(f"\nbest cross-pass layer (diff-of-means): L{bli}  "
          f"cross dm={best[3]:.3f} lr={best[4]:.3f}  (ask in-pass dm={best[1]:.3f})")
    verdict = ("TRANSFER (>=0.80): recognition direction survives into the action pass -> Step 3"
               if best[3] >= 0.80 else
               "WEAK (0.65-0.80): partial transfer; inspect before Step 3" if best[3] >= 0.65 else
               "NO TRANSFER (<0.65): recognition differs across passes -> study that, not load")
    print(f"verdict (cross-pass diff-of-means): {verdict}")

    # Step-3 PREVIEW at best layer: frozen ask-probe scores on the proceeded piles.
    Xa_b = A_acts[ask_rows][:, bli, :]
    Xc_b = C_acts[act_rows][:, bli, :]
    s = cross_pass_score(Xa_b, y, Xc_b, "diffmeans")  # frozen probe on action pass
    proc = np.array([d == "PROCEED" for d in act_decision])
    restr = lab == 1
    pileA = proc & restr & (y == 1)   # recognise-but-proceed
    pileB = proc & restr & (y == 0)   # genuine miss
    print(f"\nStep-3 preview @L{bli} (frozen ask-probe score on the ACTION pass):")
    print(f"  recognise-but-proceed (ask-YES, proceeded): n={int(pileA.sum())}  "
          f"mean score={s[pileA].mean():.3f}" if pileA.sum() else
          f"  recognise-but-proceed: n=0")
    print(f"  genuine miss          (ask-NO,  proceeded): n={int(pileB.sum())}  "
          f"mean score={s[pileB].mean():.3f}" if pileB.sum() else
          f"  genuine miss: n=0  (expected -- recognition near-ceiling; grow via load sweep)")

    out = args.out or args.action.replace(".npz", "") + ".crosspass.json"
    json.dump({
        "ask_npz": args.ask, "action_npz": args.action,
        "n_items": len(keep), "ask_yes": int(y.sum()), "ask_no": int((1 - y).sum()),
        "per_layer": [{"layer": li, "ask_inpass_dm": idm, "ask_inpass_lr": ilr,
                       "crosspass_dm": cdm, "crosspass_lr": clr}
                      for li, idm, ilr, cdm, clr in rows],
        "best_layer": bli, "best_crosspass_dm": best[3], "best_crosspass_lr": best[4],
        "verdict": verdict,
    }, open(out, "w"), indent=2)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
