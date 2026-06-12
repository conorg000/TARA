"""Move 4b probe — does the readable over/under boundary MOVE with the rule's threshold?

Reads extract_ladder.py npz for the threshold-shift passes (ask/read at £400/£500/£600).
Builds ONE "criterion-satisfied" direction by training on the ASK passes pooled across the
three thresholds (label = amount > the asked T; model-own answers, correctness-filtered;
document-disjoint by scenario). Then scores the pure-reading passes cross-pass and asks:

  within-rule (replication): per rule T, does read_t<T> separate over-T from under-T refunds?
  THE FLIP (headline): for SWING letters (400<amt<600) — satisfied under @400, not under @600 —
      does the same letter read higher under read@400 than read@600?  AUROC(@400 pos vs @600 neg).
      High => the readable boundary tracks the rule's parameter (prompt-parameterized computation).
  NO-FLIP control: ANCHOR letters (amt<400 unsatisfied-both; amt>600 satisfied-both) must NOT
      flip (AUROC ~0.5). This rules out the probe merely reading the rule's number from the prompt
      (which would move every letter, anchors included).

Layer chosen by the shared direction's own ask-pass OOF (independent of the flip outcome).
Usage: python probe_ladder_threshold.py --acts-dir acts --out probe_ladder_threshold.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from train_probe import make_cv_splitter
from probe_exp2 import pair_oof, auroc

DEFAULT_POSITIONS = ["message_mean", "message_last", "final"]
THRESHOLDS = [400, 500, 600]


def load_npz(prefix, position):
    d = np.load(f"{prefix}__{position}.npz", allow_pickle=True)
    return {"acts": d["activations"], "ids": [str(x) for x in d["ids"]],
            "groups": [str(x) for x in d["groups"]], "beh": [str(x) for x in d["behaviour"]],
            "cell": [str(x) for x in d["cell"]]}


def amount_of(doc_id):
    return int(doc_id.split("_")[1])


def flag_band_rates(read, T):
    """FLAG rate per amount-band in a read pass (behavioural complement)."""
    bands = {"<400": [], "400-600": [], ">600": []}
    for i, c in enumerate(read["cell"]):
        if c != "refund":
            continue
        a = amount_of(read["ids"][i])
        b = "<400" if a < 400 else (">600" if a > 600 else "400-600")
        bands[b].append(read["beh"][i] == "FLAG")
    return {k: round(np.mean(v), 2) if v else None for k, v in bands.items()}


def analyze(acts_dir, position, seed):
    asks = {T: load_npz(f"{acts_dir}/ladder_threshold_ask_t{T}", position) for T in THRESHOLDS}
    reads = {T: load_npz(f"{acts_dir}/ladder_threshold_read_t{T}", position) for T in THRESHOLDS}
    n_layers = asks[400]["acts"].shape[1]

    # ---- shared "criterion-satisfied" training set: pool ask rows across T (refunds only),
    #      label = model-own YES/NO, correctness-filtered to over/under T.
    Xtr_rows, ytr, gtr = [], [], []
    for T in THRESHOLDS:
        a = asks[T]
        for i, c in enumerate(a["cell"]):
            if c != "refund" or a["beh"][i] not in ("YES", "NO"):
                continue
            model = 1 if a["beh"][i] == "YES" else 0
            gt = 1 if amount_of(a["ids"][i]) > T else 0
            if model != gt:           # correctness filter (drop near-threshold fumbles)
                continue
            Xtr_rows.append((T, i)); ytr.append(model); gtr.append(a["groups"][i])
    ytr = np.array(ytr); gtr = np.array(gtr)
    cv = make_cv_splitter("group", gtr, seed)
    folds = list(cv.split(np.zeros((len(gtr), 1)), ytr, gtr))
    fold_of = {}
    for f, (_tr, te) in enumerate(folds):
        for k in te:
            fold_of[gtr[k]] = f

    # swing / anchor id sets (from any read pass; same pool)
    ref_ids = [reads[400]["ids"][i] for i, c in enumerate(reads[400]["cell"]) if c == "refund"]
    swing = [i for i in ref_ids if 400 < amount_of(i) < 600]
    anchors = [i for i in ref_ids if amount_of(i) < 400 or amount_of(i) > 600]

    rows = []
    for li in range(n_layers):
        Xtr = np.stack([asks[T]["acts"][i][li] for (T, i) in Xtr_rows], axis=0)
        # ask-pass self OOF (layer-selection metric, independent of the flip)
        s_self = pair_oof(Xtr, ytr, gtr, fold_of, len(folds), Xtr, gtr)
        ask_oof = auroc(s_self[ytr == 1], s_self[ytr == 0])

        # score every read pass, doc-disjoint, indexed by id
        read_score = {}
        within = {}
        for T in THRESHOLDS:
            r = reads[T]
            tgt = [i for i, c in enumerate(r["cell"]) if c == "refund" and r["groups"][i] in fold_of]
            sc = pair_oof(Xtr, ytr, gtr, fold_of, len(folds), r["acts"][tgt][:, li, :],
                          [r["groups"][i] for i in tgt])
            read_score[T] = {r["ids"][i]: sc[j] for j, i in enumerate(tgt)}
            over = np.array([read_score[T][i] for i in read_score[T]
                             if amount_of(i) > T])
            under = np.array([read_score[T][i] for i in read_score[T] if amount_of(i) < T])
            within[T] = auroc(over, under)

        def flip(ids):
            pos = np.array([read_score[400][i] for i in ids if i in read_score[400]])
            neg = np.array([read_score[600][i] for i in ids if i in read_score[600]])
            return auroc(pos, neg)

        rows.append(dict(layer=li, ask_oof=ask_oof, within_400=within[400],
                         within_500=within[500], within_600=within[600],
                         flip_swing=flip(swing), flip_anchor=flip(anchors)))

    best = max(rows, key=lambda r: r["ask_oof"])
    return dict(best_layer=best["layer"], best=best, per_layer=rows,
                n_train=len(ytr), n_swing=len(swing), n_anchor=len(anchors),
                flag={T: flag_band_rates(reads[T], T) for T in THRESHOLDS})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--acts-dir", default="acts")
    ap.add_argument("--positions", default=",".join(DEFAULT_POSITIONS))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="probe_ladder_threshold.json")
    args = ap.parse_args()

    report = {}
    for pos in args.positions.split(","):
        b = analyze(args.acts_dir, pos, args.seed)
        report[pos] = b
        bb = b["best"]
        print(f"\n===== {pos} (train {b['n_train']}, swing {b['n_swing']}, anchor {b['n_anchor']}) =====")
        print("layer | ask_oof | within@400 @500 @600 | FLIP-swing | flip-anchor(ctrl)")
        for r in b["per_layer"]:
            star = " <-" if r["layer"] == b["best_layer"] else ""
            print(f"  {r['layer']:2d}  |  {r['ask_oof']:.3f} | {r['within_400']:.3f} {r['within_500']:.3f} "
                  f"{r['within_600']:.3f} |   {r['flip_swing']:.3f}   |  {r['flip_anchor']:.3f}{star}")
        print(f"  >> best L{b['best_layer']}: FLIP(swing) {bb['flip_swing']:.3f}  vs  "
              f"anchor-ctrl {bb['flip_anchor']:.3f} | within @400/@500/@600 "
              f"{bb['within_400']:.2f}/{bb['within_500']:.2f}/{bb['within_600']:.2f}")
        print(f"     FLAG rates by band: {b['flag']}")
    Path(args.out).write_text(json.dumps(report, indent=2))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
