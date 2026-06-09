"""recognition_projection.py — project the behavioural groups onto the recognition direction,
and read off monitor operating points. The visual/threshold companion to gap_analysis.py.

[gap_analysis.py](gap_analysis.py) answers "is the gap recognised as strongly as flagged?" with a
single AUROC. This answers the deployment-shaped question instead: if you place every document on
the recognition axis (the probe's direction) and try to ALARM above a threshold, how much do the
groups actually overlap, and what catch-rate / false-alarm tradeoff would a monitor face?

For each read position it:
  1. picks the best layer by in-pass recognition (pooled OOF diff-of-means — NOT by how well it
     separates the gap; no cherry-picking);
  2. builds the recognition direction = full-ask diff-of-means at that layer (one axis to project
     onto), labels from the MODEL'S OWN ask answer (recognition, not ground truth);
  3. projects each action-pass group (flagged / gap / recog-miss / absent) onto it and z-scores by
     the 'absent' (no-name) baseline, so positions read as "SDs above a clean document";
  4. prints monitor operating points: thresholds that catch k of the n_gap omissions, and the
     resulting false-alarm rate on clean (absent) docs.

Read it with two caveats baked in: at small n_gap these operating points are ILLUSTRATIVE, not a
calibrated monitor; and threshold separation flatters a monitor whose true positives (silent
omissions) are rare in real deployment. Lead with diff-of-means, the honest direction.

Usage:
  python recognition_projection.py --tag v6
  python recognition_projection.py --tag v6 --positions doc_mean,final
"""
from __future__ import annotations

import argparse

import numpy as np
from sklearn.metrics import roc_auc_score

from train_probe import diffmeans_scores, pooled_oof_auroc, make_cv_splitter


def load(tag: str, role: str, pos: str) -> dict:
    d = np.load(f"acts/{tag}_{role}__{pos}.npz", allow_pickle=True)
    return dict(acts=d["activations"], ids=[str(x) for x in d["ids"]],
                groups=[str(x) for x in d["groups"]], beh=[str(x) for x in d["behaviour"]])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tag", default="v6", help="npz prefix stem, e.g. v6 -> acts/v6_ask__<pos>.npz")
    ap.add_argument("--positions", default="doc_mean,final,doc_last,name_last")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    for pos in args.positions.split(","):
        ask, act, lda = load(args.tag, "ask", pos), load(args.tag, "action", pos), load(args.tag, "loadedask", pos)
        # recognition label = the model's OWN ask answer (not ground truth); drop unclear.
        yb = np.array([1 if b == "YES" else (0 if b == "NO" else -1) for b in ask["beh"]])
        keep = yb >= 0
        y = yb[keep]
        g = np.array(ask["groups"])[keep]
        cv = make_cv_splitter("group", g, args.seed)              # pair-disjoint folds

        # best layer by in-pass recognition (the principled, non-cherry-picked choice)
        n_layers = ask["acts"].shape[1]
        recog = [pooled_oof_auroc(ask["acts"][keep][:, L, :], y, g, cv, diffmeans_scores) for L in range(n_layers)]
        L = int(np.argmax(recog))

        # projection axis: full-ask diff-of-means at the best layer, unit-normalised
        X = ask["acts"][keep][:, L, :]
        w = X[y == 1].mean(0) - X[y == 0].mean(0)
        w = w / np.linalg.norm(w)

        a = {i: k for k, i in enumerate(act["ids"])}
        l = {i: k for k, i in enumerate(lda["ids"])}
        sc = act["acts"][:, L, :] @ w

        pres = [i for i in act["ids"] if i.endswith("a")]
        flagged = [i for i in pres if act["beh"][a[i]] == "FLAG"]
        gap = [i for i in pres if act["beh"][a[i]] == "NOFLAG" and i in l and lda["beh"][l[i]] == "YES"]
        miss = [i for i in pres if act["beh"][a[i]] == "NOFLAG" and i in l and lda["beh"][l[i]] == "NO"]
        absent = [i for i in act["ids"] if i.endswith("b")]

        S = lambda ids: np.array([sc[a[i]] for i in ids])
        base = S(absent)
        mu, sd = base.mean(), base.std()
        z = lambda ids: (S(ids) - mu) / sd

        print(f"\n===== {pos}  (best-recog layer {L}, recog AUROC {recog[L]:.3f}) "
              f"— positions in SDs above the 'absent' baseline =====")
        for name, ids in [("flagged", flagged), ("GAP", gap), ("recog-miss", miss), ("absent", absent)]:
            if not ids:
                continue
            v = z(ids)
            print(f"  {name:11s} n={len(ids):3d}  mean={v.mean():+.2f}  "
                  f"[p10 {np.percentile(v, 10):+.2f} | p50 {np.percentile(v, 50):+.2f} | p90 {np.percentile(v, 90):+.2f}]")

        if gap:
            gv, abv = z(gap), z(absent)
            sep = roc_auc_score([1] * len(gv) + [0] * len(abv), np.concatenate([gv, abv]))
            print(f"  gap-vs-absent AUROC {sep:.3f}  |  monitor operating points "
                  f"(alarm if score>thr among no-flag docs; n_gap={len(gap)}):")
            ng = len(gap)
            for k in sorted({ng, max(1, round(0.75 * ng)), max(1, round(0.5 * ng))}, reverse=True):
                thr = np.sort(gv)[::-1][k - 1]
                fpr = (abv >= thr).mean()
                print(f"     catch {k}/{ng} omissions -> false-alarm on {fpr * 100:4.1f}% of clean docs   (thr {thr:+.2f} SD)")


if __name__ == "__main__":
    main()
