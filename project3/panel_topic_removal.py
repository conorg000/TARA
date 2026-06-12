"""Move 2 — the DECISIVE recognition-vs-topic decomposition (analysis-only, existing acts).

The legal/medical panel confounds CONDITION with TOPIC: legal-advice-seeking docs carry
legal vocabulary, medical ones medical vocabulary. So "the directions separate"
(specificity 0.97) could mostly mean "the model represents legal-topic vs medical-topic"
— which a KEYWORD FILTER could do too. Beating keyword filters is the whole point of
probes, so we must decompose: is the cross-condition separation RECOGNITION (the model's
advice-seeking judgment, no-regex) or TOPIC (vocabulary, regex-able)?

Method — project out the topic axis, re-measure (per-fold, leak-free):
  Within each CV fold, from the TRAIN rows only:
    d_topic = centroid(own_near) - centroid(other_near)
      (nears are register-matched, NOT-seeking, differ ONLY in topic -> the clean topic axis)
    Orthogonalize every activation against d_topic  (x_perp = x - (x.d_hat) d_hat).
    Train the recognition direction (diff-of-means, own-ask YES vs NO) in BOTH the raw and
    the topic-removed space; score the held-out fold.
  Then on the pooled OOF scores:
    specificity_raw  = AUROC(own_hit vs other_hit)   in raw space   (= panel specificity)
    specificity_perp = AUROC(own_hit vs other_hit)   AFTER topic removal   <-- THE NUMBER
    topic_near_perp  = AUROC(own_near vs other_near)  after removal  (sanity: should -> ~0.5)
    hit_near_perp    = AUROC(own_hit  vs own_near)    after removal  (seeking should survive)
    recog_perp       = AUROC(YES vs NO)               after removal  (recognition should survive)

Reading:
  specificity_perp stays HIGH (>=0.80) and hit_near_perp HIGH while topic_near_perp ~0.5
    -> genuine RECOGNITION-domain separability beyond topic. The panel beats keywords.
  specificity_perp DROPS toward 0.5 (tracking topic_near_perp)
    -> the cross-condition separation was TOPIC; the panel is a keyword-equivalent here.

Single-axis removal is conservative (topic may be multi-dim); topic_near_perp reports how
much topic the one axis captured. If it stays high, topic is multi-dim -> escalate to a
multi-axis removal (--topic-rank k).

Usage (on the box):
  /venv/main/bin/python panel_topic_removal.py --acts-dir acts \
      --positions message_last,message_mean --out panel_topic_removal.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from probe_panel import load_npz, consistency_filter, rotating_acts, auroc, RECOG_BAND
from train_probe import make_cv_splitter

CONDS = ["legal", "medical"]


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def orth(X, dirs):
    """Remove each unit direction in `dirs` (list) from rows of X (Gram-Schmidt-style;
    dirs are made mutually orthonormal first)."""
    Xp = X.astype(np.float64).copy()
    basis = []
    for d in dirs:
        d = d.astype(np.float64).copy()
        for b in basis:
            d = d - (d @ b) * b
        d = unit(d)
        if np.linalg.norm(d) > 1e-9:
            basis.append(d)
    for b in basis:
        Xp = Xp - np.outer(Xp @ b, b)
    return Xp


def analyze(cond: str, acts_dir: str, position: str, seed: int, topic_rank: int) -> dict:
    other = "medical" if cond == "legal" else "legal"
    ask_ps = [load_npz(f"{acts_dir}/panel_ask_{cond}_p{k}", position) for k in (1, 2, 3)]
    kept, y_all, _ = consistency_filter(ask_ps)
    base = ask_ps[0]
    cellk = [base["cell"][i] for i in kept]
    docck = [base["doccond"][i] for i in kept]
    stemsk = [base["groups"][i] for i in kept]
    Xrot = rotating_acts(ask_ps, kept)

    tr = [j for j, c in enumerate(cellk) if c != "both"]
    ytr = y_all[tr]
    gtr = np.array([stemsk[j] for j in tr])
    Xtr = Xrot[tr]

    def mask(pred):
        return np.array([pred(docck[j], cellk[j]) for j in tr])
    own_hit = mask(lambda d, c: c == "hit" and d == cond)
    other_hit = mask(lambda d, c: c == "hit" and d == other)
    own_near = mask(lambda d, c: c == "near" and d == cond)
    other_near = mask(lambda d, c: c == "near" and d == other)

    cv = make_cv_splitter("group", gtr, seed)
    folds = list(cv.split(np.zeros((len(gtr), 1)), ytr, gtr))

    rows = []
    for li in range(Xtr.shape[1]):
        X = Xtr[:, li, :].astype(np.float64)
        s_raw = np.full(len(X), np.nan)
        s_perp = np.full(len(X), np.nan)
        for tr_i, te_i in folds:
            trm = np.zeros(len(X), bool); trm[tr_i] = True
            # topic axis (axes) from TRAIN nears only
            tdirs = []
            on, ot = trm & own_near, trm & other_near
            if on.any() and ot.any():
                tdirs.append(X[on].mean(0) - X[ot].mean(0))           # mean-difference topic axis
                if topic_rank >= 2:
                    # 2nd, higher-capacity topic axis: a logistic boundary own-near vs other-near
                    # (captures topic variance the centroid diff misses). Removing it is a
                    # CONSERVATIVE test — over-removal can only understate recognition.
                    from sklearn.linear_model import LogisticRegression
                    Xn = np.vstack([X[on], X[ot]]); yn = np.r_[np.ones(on.sum()), np.zeros(ot.sum())]
                    mu, sd = Xn.mean(0), Xn.std(0) + 1e-6
                    lr = LogisticRegression(C=1.0, max_iter=2000).fit((Xn - mu) / sd, yn)
                    tdirs.append((lr.coef_[0] / sd))                  # back to raw-activation space
            Xp = orth(X, tdirs) if tdirs else X
            # recognition direction (diff-of-means) trained on TRAIN rows, raw and perp
            pos, neg = trm & (ytr == 1), trm & (ytr == 0)
            d_raw = unit(X[pos].mean(0) - X[neg].mean(0))
            d_perp = unit(Xp[pos].mean(0) - Xp[neg].mean(0))
            s_raw[te_i] = X[te_i] @ d_raw
            s_perp[te_i] = Xp[te_i] @ d_perp
        rows.append(dict(
            layer=li,
            recog_raw=auroc(s_raw[ytr == 1], s_raw[ytr == 0]),
            recog_perp=auroc(s_perp[ytr == 1], s_perp[ytr == 0]),
            specificity_raw=auroc(s_raw[own_hit], s_raw[other_hit]),
            specificity_perp=auroc(s_perp[own_hit], s_perp[other_hit]),     # THE number
            hit_near_perp=auroc(s_perp[own_hit], s_perp[own_near]),
            topic_near_raw=auroc(s_raw[own_near], s_raw[other_near]),
            topic_near_perp=auroc(s_perp[own_near], s_perp[other_near]),    # sanity ~0.5
        ))

    def med(key):
        band = [r[key] for r in rows if r["recog_raw"] > RECOG_BAND and not np.isnan(r[key])]
        return float(np.median(band)) if band else float("nan")
    keys = ["recog_raw", "recog_perp", "specificity_raw", "specificity_perp",
            "hit_near_perp", "topic_near_raw", "topic_near_perp"]
    robust = {k: med(k) for k in keys}
    robust["n_band_layers"] = int(sum(r["recog_raw"] > RECOG_BAND for r in rows))
    return dict(robust=robust, per_layer=rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--acts-dir", default="acts")
    ap.add_argument("--positions", default="message_last,message_mean")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--topic-rank", type=int, default=1)
    ap.add_argument("--out", default="panel_topic_removal.json")
    args = ap.parse_args()

    report = {}
    for cond in CONDS:
        report[cond] = {}
        for pos in args.positions.split(","):
            b = analyze(cond, args.acts_dir, pos, args.seed, args.topic_rank)
            report[cond][pos] = b
            r = b["robust"]
            survived = r["specificity_perp"] >= 0.80
            verdict = ("RECOGNITION beyond topic" if survived and r["hit_near_perp"] >= 0.80
                       else "separation was TOPIC" if r["specificity_perp"] <= 0.65
                       else "PARTIAL / GRAY")
            print(f"\n== {cond.upper()} / {pos}  (recog>{RECOG_BAND}, {r['n_band_layers']} layers) ==")
            print(f"  specificity  raw {r['specificity_raw']:.3f}  ->  AFTER topic-removal {r['specificity_perp']:.3f}   [{verdict}]")
            print(f"  topic-near   raw {r['topic_near_raw']:.3f}  ->  after removal {r['topic_near_perp']:.3f}  (sanity: should drop toward 0.5)")
            print(f"  hit-near after removal {r['hit_near_perp']:.3f}  (seeking should survive) | recog raw {r['recog_raw']:.3f} -> perp {r['recog_perp']:.3f}")
    Path(args.out).write_text(json.dumps(report, indent=2))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
