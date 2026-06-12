"""Move 3 — lexical ablation: mask the trigger lexicon so the surface cue is gone, to test
whether RECOGNITION survives in the activations when the WORDS can no longer separate.

The TF-IDF baseline showed hit-vs-near is lexically trivial (AUROC ~0.99), so the probe's
high hit-near is not yet evidence of recognition. This builds a masked copy of the keeper
content where, in BOTH hit and near, the discriminating lexicon is replaced by a neutral
placeholder. The mask list per condition = the curated trigger regex tokens UNION the top
TF-IDF discriminative n-grams (the exact tokens the lexical classifier exploits).

After masking we verify TF-IDF hit-near collapses to ~0.5 (the surface cue is genuinely
gone). Then (GPU) we re-extract and re-probe: if the probe's hit-near stays high while
TF-IDF on the masked text is ~0.5, the model has computed an intent representation that is
NOT in the surface tokens -> genuine recognition. If it collapses too, the signal was surface.

Writes playbook_content_masked.json (same shape as playbook_content.json: form/none copied
through unmasked — they carry no trigger).

Usage: ./.venv/bin/python playbook_mask.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold

from playbook_surface_baselines import REGEX, CONDS

PLACEHOLDER = "[...]"


def top_tfidf_tokens(hits, nears, k=30):
    """The n-grams a lexical classifier leans on to tell hit from near (|coef| ranked)."""
    texts = hits + nears
    y = np.array([1] * len(hits) + [0] * len(nears))
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=5000)
    X = vec.fit_transform(texts)
    clf = LogisticRegression(max_iter=2000, C=4.0).fit(X, y)
    names = np.array(vec.get_feature_names_out())
    order = np.argsort(-np.abs(clf.coef_[0]))
    toks = []
    for idx in order[: k * 2]:
        for w in names[idx].split():       # split bigrams into words
            if len(w) >= 3 and w.isalpha():
                toks.append(w)
        if len(set(toks)) >= k:
            break
    return sorted(set(toks))


def build_mask_regex(cond, hits, nears):
    """Curated regex tokens UNION top TF-IDF tokens -> one word-boundary regex."""
    curated = set(re.findall(r"[a-z]{3,}", REGEX[cond].pattern.lower()))
    curated -= {"action", "right", "the", "and", "while", "small", "claims", "take", "further"}  # stopwordy
    learned = set(top_tfidf_tokens(hits, nears, k=30))
    toks = sorted({t for t in (curated | learned) if len(t) >= 3}, key=len, reverse=True)
    # match whole words / prefixes (so 'delete','deleted','deletion' all go)
    return re.compile(r"\b(" + "|".join(re.escape(t) for t in toks) + r")\w*\b", re.I), toks


def mask_text(rx, text):
    return rx.sub(PLACEHOLDER, text)


def tf_hitnear(hits, nears):
    texts = hits + nears
    y = np.array([1] * len(hits) + [0] * len(nears))
    groups = np.array(list(range(len(hits))) + list(range(len(nears))))  # pair stems
    s = np.full(len(y), np.nan)
    gkf = GroupKFold(n_splits=5)
    for tr, te in gkf.split(texts, y, groups):
        if len(set(y[tr])) < 2:
            s[te] = 0.0; continue
        vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=5000)
        Xtr = vec.fit_transform([texts[i] for i in tr])
        clf = LogisticRegression(max_iter=2000, C=4.0).fit(Xtr, y[tr])
        s[te] = clf.decision_function(vec.transform([texts[i] for i in te]))
    return roc_auc_score(y, s)


def main():
    content = json.loads(Path("playbook_content.json").read_text())
    out = {}
    report = {}
    print(f"{'condition':22s} | TF-IDF hit-near  raw -> masked | #mask tokens | sample masked hit")
    print("-" * 110)
    for cond in CONDS:
        pairs = content[cond]
        hits = [p["hit"] for p in pairs]
        nears = [p["near"] for p in pairs]
        rx, toks = build_mask_regex(cond, hits, nears)
        mhits = [mask_text(rx, h) for h in hits]
        mnears = [mask_text(rx, n) for n in nears]
        raw = tf_hitnear(hits, nears)
        masked = tf_hitnear(mhits, mnears)
        out[cond] = [{"hit": mh, "near": mn} for mh, mn in zip(mhits, mnears)]
        report[cond] = {"tfidf_hitnear_raw": round(float(raw), 3),
                        "tfidf_hitnear_masked": round(float(masked), 3),
                        "n_mask_tokens": len(toks), "mask_tokens": toks}
        print(f"{cond:22s} | {raw:.3f} -> {masked:.3f}              | {len(toks):>3d}          | {mhits[0][:60]}")
    out["form"] = content["form"]      # no trigger -> copied through
    out["none"] = content["none"]
    Path("playbook_content_masked.json").write_text(json.dumps(out, indent=2))
    Path("playbook_mask_report.json").write_text(json.dumps(report, indent=2))
    print("\nwrote playbook_content_masked.json + playbook_mask_report.json")
    print("Masking worked iff TF-IDF hit-near dropped toward ~0.5. Then GPU re-extract + re-probe:")
    print("  the probe's hit-near on MASKED activations vs this ~0.5 surface floor = the recognition test.")


if __name__ == "__main__":
    main()
