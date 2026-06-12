"""Move 3 — surface-feature baselines: does the probe's recognition signal beat what a
regex and a bag-of-words classifier get from the raw text?

The project claim is RECOGNITION, not surface string-matching. The probe's hit-vs-near
separation is only evidence of recognition if it BEATS what surface lexical features
achieve on the same lattice. This script measures, per condition, two text-only baselines
on the keeper content (playbook_content.json), document-disjoint (pair_stem CV):

  (1) REGEX  — a hand-written matcher a practitioner might deploy. Reports hit-detect,
      near-false-fire, specificity (own-hit vs other-hit). Doubles as a FUZZY-BAND check:
      if a regex already nails the condition, it was below the band and a probe is moot.
  (2) TF-IDF logistic — bag-of-words upper bound on lexical separability. Reports the same
      AUROCs the probe reports (hit-near, floor, specificity), so they compare head-to-head.

A probe metric is only "recognition" insofar as it EXCEEDS the TF-IDF lexical number.

Usage: ./.venv/bin/python playbook_surface_baselines.py --out playbook_surface_baselines.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold

CONDS = ["data_deletion", "fraud_report", "implicit_legal_threat"]

# Practitioner regexes (deliberately reasonable, not strawmen). Case-insensitive.
REGEX = {
    # deletion/erasure verb in the vicinity of a personal-data/record object
    "data_deletion": re.compile(
        r"\b(delet\w*|eras\w*|wipe\w*|destroy\w*|dispos\w*|remov\w*|forget|forgotten|"
        r"right to be forgotten|withdraw\w* consent)\b", re.I),
    # explicit dishonesty / fraud lexicon
    "fraud_report": re.compile(
        r"\b(fraud\w*|fiddl\w*|cheat\w*|dishonest\w*|deceiv\w*|deceptio\w*|scam\w*|"
        r"fals\w*|pretend\w*|lying|lied|swindl\w*|fake\w*|illegal\w*|undeclar\w*)\b", re.I),
    # naive "legal escalation" lexicon — expected to FAIL on implicit threats (fuzzy-band)
    "implicit_legal_threat": re.compile(
        r"\b(sue\w*|lawyer\w*|solicitor\w*|court\w*|legal action|litigat\w*|ombudsman|"
        r"tribunal|small claims|take .* further|escalat\w*|my rights)\b", re.I),
}


def auroc(pos, neg):
    if not len(pos) or not len(neg):
        return float("nan")
    return roc_auc_score([1] * len(pos) + [0] * len(neg), np.concatenate([pos, neg]))


def regex_fires(rx, text):
    return 1 if rx.search(text) else 0


def tfidf_oof(texts, y, groups):
    """Document-disjoint OOF logistic on TF-IDF; returns per-doc decision score."""
    texts = np.array(texts, dtype=object)
    y = np.array(y)
    groups = np.array(groups)
    scores = np.full(len(y), np.nan)
    n_splits = min(5, len(set(groups)))
    gkf = GroupKFold(n_splits=n_splits)
    for tr, te in gkf.split(texts, y, groups):
        if len(set(y[tr])) < 2:
            scores[te] = 0.0
            continue
        vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=5000)
        Xtr = vec.fit_transform(texts[tr])
        clf = LogisticRegression(max_iter=2000, C=4.0).fit(Xtr, y[tr])
        Xte = vec.transform(texts[te])
        scores[te] = clf.decision_function(Xte)
    return scores


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="playbook_surface_baselines.json")
    args = ap.parse_args()
    content = json.loads(Path("playbook_content.json").read_text())

    # assemble the lattice: per cond hit/near (paired stems) + shared none
    docs = []
    for cond in CONDS:
        for i, p in enumerate(content[cond], 1):
            docs.append(dict(cond=cond, cell="hit", text=p["hit"], stem=f"{cond}_{i:02d}"))
            docs.append(dict(cond=cond, cell="near", text=p["near"], stem=f"{cond}_{i:02d}"))
    for i, m in enumerate(content["none"], 1):
        docs.append(dict(cond="neutral", cell="none", text=m, stem=f"none_{i:02d}"))

    report = {}
    print(f"{'condition':22s} | {'REGEX hit/near/spec':28s} | {'TF-IDF hit-near / floor / spec':32s}")
    print("-" * 92)
    for cond in CONDS:
        rx = REGEX[cond]
        own_hit = [d for d in docs if d["cond"] == cond and d["cell"] == "hit"]
        own_near = [d for d in docs if d["cond"] == cond and d["cell"] == "near"]
        other_hit = [d for d in docs if d["cell"] == "hit" and d["cond"] != cond]
        none = [d for d in docs if d["cell"] == "none"]

        # (1) regex
        hit_fire = np.mean([regex_fires(rx, d["text"]) for d in own_hit])
        near_fire = np.mean([regex_fires(rx, d["text"]) for d in own_near])
        other_fire = np.mean([regex_fires(rx, d["text"]) for d in other_hit])
        rx_hitnear = auroc(np.array([regex_fires(rx, d["text"]) for d in own_hit]),
                           np.array([regex_fires(rx, d["text"]) for d in own_near]))
        rx_spec = auroc(np.array([regex_fires(rx, d["text"]) for d in own_hit]),
                        np.array([regex_fires(rx, d["text"]) for d in other_hit]))

        # (2) TF-IDF — hit-near (the key surface control), floor, specificity
        hn = own_hit + own_near
        y_hn = [1] * len(own_hit) + [0] * len(own_near)
        s = tfidf_oof([d["text"] for d in hn], y_hn, [d["stem"] for d in hn])
        tf_hitnear = auroc(s[:len(own_hit)], s[len(own_hit):])

        fl = own_hit + none
        y_fl = [1] * len(own_hit) + [0] * len(none)
        sfl = tfidf_oof([d["text"] for d in fl], y_fl, [d["stem"] for d in fl])
        tf_floor = auroc(sfl[:len(own_hit)], sfl[len(own_hit):])

        sp = own_hit + other_hit
        y_sp = [1] * len(own_hit) + [0] * len(other_hit)
        ssp = tfidf_oof([d["text"] for d in sp], y_sp, [d["stem"] for d in sp])
        tf_spec = auroc(ssp[:len(own_hit)], ssp[len(own_hit):])

        report[cond] = dict(
            regex=dict(hit_fire=round(float(hit_fire), 3), near_fire=round(float(near_fire), 3),
                       other_hit_fire=round(float(other_fire), 3),
                       hit_near_auroc=round(float(rx_hitnear), 3), specificity=round(float(rx_spec), 3)),
            tfidf=dict(hit_near_auroc=round(float(tf_hitnear), 3), floor=round(float(tf_floor), 3),
                       specificity=round(float(tf_spec), 3)))
        print(f"{cond:22s} | hit {hit_fire:.2f} near {near_fire:.2f} spec {rx_spec:.2f}      "
              f"| hit-near {tf_hitnear:.3f} floor {tf_floor:.3f} spec {tf_spec:.3f}")

    Path(args.out).write_text(json.dumps(report, indent=2))
    print(f"\nwrote {args.out}")
    print("\nRead: the PROBE's hit-near must EXCEED tfidf hit-near to claim recognition-not-surface.")
    print("If regex hit-fire is high AND near-fire low, the condition was below the fuzzy band (regex wins).")


if __name__ == "__main__":
    main()
