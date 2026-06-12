"""Move 2 — the DECISIVE separability metric, disambiguating the pre-registered crossfire.

probe_panel.py's pre-registered kill-switch is crossfire = AUROC(other_hit vs none): "is
the other condition's hit DARK (≈ none) under probe_A?" That fired COLLAPSED (crossfire ≈1).
But AUROC(other_hit, none)=1 is AMBIGUOUS: it says other-hits rank ABOVE none, which is true
whether other-hits sit at the legal baseline (panel works, threshold between them) OR up at
own-hit level (panel broken). The clean separability number is the DIRECT comparison:

    SPECIFICITY = AUROC(own_hit vs other_hit)   on probe_A's own direction.
      ≈0.5  -> own and other seekers are ON TOP of each other -> directions collapsed.
      ≈1.0  -> probe_A ranks its own seekers above the other's -> separable / a real panel.

This is NOT a goalpost move: the pre-registered crossfire VERDICT stands and is reported as-is
(probe_panel.json). This script ADDS the disambiguator and the projection layout (where each
cell sits on the axis), so the collapse is confirmed or refuted on the clean number, per the
CLAUDE.md "too-clean result -> investigate before believing" rule.

Reuses probe_panel's exact machinery (consistency filter, paraphrase rotation, pair-disjoint
document-disjoint OOF diff-of-means), so the numbers are method-consistent with the probe.

Usage (on the box, where the acts live):
    /venv/main/bin/python panel_specificity.py --acts-dir acts --out panel_specificity.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from probe_panel import (load_npz, consistency_filter, rotating_acts, panel_oof, auroc,
                         band_median, RECOG_BAND)
from train_probe import make_cv_splitter

CONDS = ["legal", "medical"]


def analyze(cond: str, acts_dir: str, position: str, seed: int) -> dict:
    other = "medical" if cond == "legal" else "legal"
    ask_ps = [load_npz(f"{acts_dir}/panel_ask_{cond}_p{k}", position) for k in (1, 2, 3)]
    kept, y_all, _ = consistency_filter(ask_ps)
    base = ask_ps[0]
    cellk = [base["cell"][i] for i in kept]
    docck = [base["doccond"][i] for i in kept]
    stemsk = [base["groups"][i] for i in kept]
    Xrot = rotating_acts(ask_ps, kept)

    tr_idx = [j for j, c in enumerate(cellk) if c != "both"]
    ytr = y_all[tr_idx]
    gtr = np.array([stemsk[j] for j in tr_idx])
    Xtr = Xrot[tr_idx]

    def mask(pred):
        return np.array([pred(docck[j], cellk[j]) for j in tr_idx])
    is_own_hit = mask(lambda d, c: c == "hit" and d == cond)
    is_other_hit = mask(lambda d, c: c == "hit" and d == other)
    is_own_near = mask(lambda d, c: c == "near" and d == cond)
    is_other_near = mask(lambda d, c: c == "near" and d == other)   # the topic control's other half
    is_none = mask(lambda d, c: c == "none")
    is_form = mask(lambda d, c: c == "form")

    # both-docs (cell==both, consistent-YES) — never in training (excluded), so a direction
    # trained on all training rows scores them leak-free. We round-robin them onto folds.
    both_idx = [j for j, (c, lab) in enumerate(zip(cellk, y_all)) if c == "both" and lab == 1]
    both_stems = [stemsk[j] for j in both_idx]

    cv = make_cv_splitter("group", gtr, seed)
    folds = list(cv.split(np.zeros((len(gtr), 1)), ytr, gtr))
    n_folds = len(folds)
    fold_of = {}
    for f, (_tr, te) in enumerate(folds):
        for k in te:
            fold_of[gtr[k]] = f
    for i, s_ in enumerate(sorted(set(both_stems))):
        fold_of[s_] = i % n_folds

    rows = []
    for li in range(Xtr.shape[1]):
        X = Xtr[:, li, :]
        s = panel_oof(X, ytr, gtr, fold_of, n_folds, X, gtr)
        s_both = panel_oof(X, ytr, gtr, fold_of, n_folds, Xrot[both_idx][:, li, :], both_stems)
        recog = auroc(s[ytr == 1], s[ytr == 0])

        def m(mask_):  # mean projection of a cell
            return float(np.mean(s[mask_])) if mask_.any() else float("nan")
        rows.append(dict(
            layer=li, recog_dm=recog,
            specificity=auroc(s[is_own_hit], s[is_other_hit]),   # THE decisive number (hits)
            topic_near=auroc(s[is_own_near], s[is_other_near]),  # KEY CONTROL: own-near vs other-near
                                                                 #   (differ ONLY in topic; want ~0.5)
            own_vs_none=auroc(s[is_own_hit], s[is_none]),
            other_vs_none=auroc(s[is_other_hit], s[is_none]),    # = probe_panel crossfire
            both_vs_other=auroc(s_both, s[is_other_hit]),        # do both-docs outrank OTHER hits? (real composition)
            proj_own=m(is_own_hit), proj_other=m(is_other_hit),
            proj_near=m(is_own_near), proj_other_near=m(is_other_near),
            proj_both=float(np.mean(s_both)) if len(s_both) else float("nan"),
            proj_form=m(is_form), proj_none=m(is_none),
        ))
    best = max(rows, key=lambda r: r["recog_dm"])
    robust = {k: band_median(rows, k) for k in
              ("specificity", "topic_near", "own_vs_none", "other_vs_none", "both_vs_other",
               "proj_own", "proj_other", "proj_near", "proj_other_near", "proj_both",
               "proj_form", "proj_none")}
    robust["n_band_layers"] = int(sum(r["recog_dm"] > RECOG_BAND for r in rows))
    band = [r["specificity"] for r in rows if r["recog_dm"] > RECOG_BAND]
    robust["specificity_min"] = float(np.min(band)) if band else float("nan")
    robust["specificity_max"] = float(np.max(band)) if band else float("nan")
    return dict(best_layer=best["layer"], best=best, robust=robust, per_layer=rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--acts-dir", default="acts")
    ap.add_argument("--positions", default="message_last,message_mean,final")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="panel_specificity.json")
    args = ap.parse_args()

    report = {}
    for cond in CONDS:
        report[cond] = {}
        for pos in args.positions.split(","):
            b = analyze(cond, args.acts_dir, pos, args.seed)
            report[cond][pos] = b
            rb = b["robust"]
            verdict = ("SEPARABLE" if rb["specificity"] >= 0.80 else
                       "COLLAPSED" if rb["specificity"] <= 0.65 else "GRAY")
            print(f"\n== {cond.upper()} / {pos}  (robust medians, recog>{RECOG_BAND}, "
                  f"{rb['n_band_layers']} layers) ==")
            print(f"  SPECIFICITY own-vs-other-hit = {rb['specificity']:.3f} "
                  f"[layer-range {rb['specificity_min']:.3f}-{rb['specificity_max']:.3f}]  -> {verdict}")
            print(f"  TOPIC-control own-near-vs-other-near = {rb['topic_near']:.3f}  "
                  f"(differ ONLY in topic; ~0.5 = no topic confound, high = topic present)")
            print(f"  own-vs-none {rb['own_vs_none']:.3f} | other-vs-none (=crossfire) {rb['other_vs_none']:.3f} | "
                  f"both-vs-other-hit {rb['both_vs_other']:.3f} (composition)")
            print(f"  projection means: own_hit {rb['proj_own']:+.0f} | both {rb['proj_both']:+.0f} | "
                  f"other_hit {rb['proj_other']:+.0f} | own_near {rb['proj_near']:+.0f} | "
                  f"other_near {rb['proj_other_near']:+.0f} | form {rb['proj_form']:+.0f} | none {rb['proj_none']:+.0f}")
            print(f"  >> NB specificity is necessary not sufficient — see panel_topic_removal.py "
                  f"for whether it survives topic-removal (the recognition-vs-keyword test)")
    Path(args.out).write_text(json.dumps(report, indent=2))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
