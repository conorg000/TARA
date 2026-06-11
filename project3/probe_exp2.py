"""CPU step: the Experiment 2 fuzzy-climb probe + the K1–K4 kill battery (no GPU).

Runs on the .npz from extract_exp2.py. Tests the Exp-2 claim: *the model computes a
readable registration of an ad-hoc, prompt-specified fuzzy condition — not topic, not a
trained-in category, not generic decodability.* Recognition-decode is the FLOOR (the
category track already showed semantic recognition decodes at 0.95–0.99); the load-bearing
results are the controls.

Per condition (legal, medical), per read position, per layer:

  TRAIN a recognition direction on the ASK pass. Labels = the model's OWN ask answer,
  CONSISTENCY-FILTERED across the 3 question paraphrases (K1: keep only items where all 3
  agree; drop rate reported). Training activations rotate the paraphrase per item
  (i -> paraphrase i%3) so the direction can't key on one question's wording
  (format-confound guard). diff-of-means leads; logreg = upper bound; pair-disjoint CV on
  meta.pair_stem (hit_NN and near_NN never split across folds).

  Then, from the per-item out-of-fold scores:
   - RECOGNITION : YES vs NO (the model's own labels) — the floor.
   - K2 topic    : trigger-vs-near (hit vs register-matched near; want >=0.80) and
                   near-vs-none (want <=0.65). A topic detector fails one of these.
   - K3 rule-swap: the SAME hit documents scored under the MATCHING-rule action pass vs the
                   SWAPPED-rule action pass (want >=0.80). Only a prompt-conditioned
                   computation flips with the rule — the novelty control. Cross-pass,
                   document-disjoint (the direction never saw the action).
   - transfer    : recognition survives ask -> matching-rule action (hit vs none).
   - K4 junk     : selectivity = recognition_dm - best arbitrary-property decode
                   (message length high/low; a fixed hash-parity label). Want > +0.10.
   - shuffle     : label-shuffle must collapse to ~0.5 (leak check). layer-0 ~0.5 too.

Usage (after extract_exp2.sh writes acts/exp2_{ask,action}_*__<pos>.npz):
    python probe_exp2.py --acts-dir acts --out probe_exp2.json
Smoke (fabricated tiny activations, verifies the whole path runs): python probe_exp2_smoke.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

from train_probe import diffmeans_scores, logreg_scores, pooled_oof_auroc, make_cv_splitter
from cross_pass_probe import cross_pass_score

DEFAULT_POSITIONS = ["message_mean", "final"]
CONDS = ["legal", "medical"]
N_SHUFFLE = 10  # average the label-shuffle leak check over perms (a single perm is noisy on small n — r9 lesson)


def load_npz(prefix: str, position: str) -> dict:
    d = np.load(f"{prefix}__{position}.npz", allow_pickle=True)
    return {
        "acts": d["activations"],                      # [N, L+1, D]
        "ids": [str(x) for x in d["ids"]],
        "labels": d["labels"].astype(int),
        "groups": [str(x) for x in d["groups"]],       # meta.pair_stem
        "beh": [str(x) for x in d["behaviour"]],
        "doccond": [str(x) for x in d["doccond"]],
        "cell": [str(x) for x in d["cell"]],
        "seq_len": d["seq_len"].astype(int),
    }


def pair_oof(Xask_li, y, ask_stems, fold_of, n_folds, target_vecs, target_stems):
    """Document-disjoint cross-pass diff-of-means (carried from probe_keyphrase): each
    target item is scored by a direction trained ONLY on ask rows whose pair_stem is not in
    the target's held-out fold."""
    out = np.full(len(target_vecs), np.nan)
    if len(target_vecs) == 0:
        return out
    target_stems = list(target_stems)
    for f in range(n_folds):
        tr = np.array([fold_of[s] != f for s in ask_stems])
        te = [j for j, s in enumerate(target_stems) if fold_of[s] == f]
        if te:
            out[te] = cross_pass_score(Xask_li[tr], y[tr], target_vecs[te], "diffmeans")
    assert not np.isnan(out).any(), "a target item was never scored (stem absent from all folds)"
    return out


def auroc(pos_scores, neg_scores) -> float:
    if not len(pos_scores) or not len(neg_scores):
        return float("nan")
    return roc_auc_score([1] * len(pos_scores) + [0] * len(neg_scores),
                         np.concatenate([pos_scores, neg_scores]))


def consistency_filter(ask_ps: list[dict]) -> tuple[list[int], np.ndarray, int]:
    """Across the 3 paraphrase passes (aligned by row), keep items where all 3 ask answers
    are clear AND agree (K1). Returns (kept row indices, labels for kept, n_dropped)."""
    ids0 = ask_ps[0]["ids"]
    for a in ask_ps[1:]:
        if a["ids"] != ids0:
            raise SystemExit("paraphrase passes are not row-aligned (different ids/order)")
    kept, labels = [], []
    for i in range(len(ids0)):
        votes = [a["beh"][i] for a in ask_ps]
        if all(v in ("YES", "NO") for v in votes) and len(set(votes)) == 1:
            kept.append(i)
            labels.append(1 if votes[0] == "YES" else 0)
    return kept, np.array(labels), len(ids0) - len(kept)


def rotating_acts(ask_ps: list[dict], kept: list[int]) -> np.ndarray:
    """Per kept item j (original row i), take activations from paraphrase j%3 — the
    format-confound guard (the direction can't key on one question's wording)."""
    return np.stack([ask_ps[j % 3]["acts"][i] for j, i in enumerate(kept)], axis=0)


def analyze(cond: str, acts_dir: str, position: str, seed: int) -> dict:
    other = "medical" if cond == "legal" else "legal"
    ask_ps = [load_npz(f"{acts_dir}/exp2_ask_{cond}_p{k}", position) for k in (1, 2, 3)]
    act_match = load_npz(f"{acts_dir}/exp2_action_{cond}", position)     # matching rule
    act_swap = load_npz(f"{acts_dir}/exp2_action_{other}", position)     # swapped rule

    kept, y, n_drop = consistency_filter(ask_ps)
    base = ask_ps[0]
    cell = [base["cell"][i] for i in kept]
    doccond = [base["doccond"][i] for i in kept]
    stems = [base["groups"][i] for i in kept]
    ids = [base["ids"][i] for i in kept]
    seq = np.array([base["seq_len"][i] for i in kept])
    Xrot = rotating_acts(ask_ps, kept)                                   # [Nk, L+1, D]

    # subset masks (within kept)
    is_hit = np.array([c == "hit" and d == cond for c, d in zip(cell, doccond)])
    is_near = np.array([c == "near" and d == cond for c, d in zip(cell, doccond)])
    is_none = np.array([c == "none" for c in cell])
    hit_ids = [i for i, h in zip(ids, is_hit) if h]

    # action-pass rows for the hit docs (cross-pass targets), by id
    am_row = {i: k for k, i in enumerate(act_match["ids"])}
    as_row = {i: k for k, i in enumerate(act_swap["ids"])}
    hit_rows_m = [am_row[i] for i in hit_ids if i in am_row]
    hit_rows_s = [as_row[i] for i in hit_ids if i in as_row]
    none_ids = [i for i, n in zip(ids, is_none) if n]
    none_rows_m = [am_row[i] for i in none_ids if i in am_row]

    g = np.array(stems)
    cv = make_cv_splitter("group", g, seed)
    n_layers = Xrot.shape[1]
    folds = list(cv.split(np.zeros((len(g), 1)), y, g))
    fold_of = {}
    for f, (_tr, te) in enumerate(folds):
        for k in te:
            fold_of[g[k]] = f
    n_folds = len(folds)

    # K4 junk labels (arbitrary properties — must be much less decodable than recognition)
    junk = {
        "len_hi": (seq > np.median(seq)).astype(int),
        "hash_parity": np.array([hash(i) % 2 for i in ids]),
    }

    rows = []
    for li in range(n_layers):
        Xask = Xrot[:, li, :]
        s = pair_oof(Xask, y, g, fold_of, n_folds, Xask, g)             # per-item OOF scores
        recog_dm = auroc(s[y == 1], s[y == 0])
        k2_hit_near = auroc(s[is_hit], s[is_near])
        k2_near_none = auroc(s[is_near], s[is_none])

        s_act_hit_m = pair_oof(Xask, y, g, fold_of, n_folds, act_match["acts"][hit_rows_m][:, li, :],
                               [act_match["groups"][r] for r in hit_rows_m])
        s_act_hit_s = pair_oof(Xask, y, g, fold_of, n_folds, act_swap["acts"][hit_rows_s][:, li, :],
                               [act_swap["groups"][r] for r in hit_rows_s])
        s_act_none_m = pair_oof(Xask, y, g, fold_of, n_folds, act_match["acts"][none_rows_m][:, li, :],
                                [act_match["groups"][r] for r in none_rows_m])
        k3_swap = auroc(s_act_hit_m, s_act_hit_s)
        transfer = auroc(s_act_hit_m, s_act_none_m)

        junk_best = 0.0
        for jl in junk.values():
            if len(set(jl)) > 1:
                a = pooled_oof_auroc(Xask, jl, g, cv, diffmeans_scores)
                junk_best = max(junk_best, a, 1 - a)
        selectivity = recog_dm - junk_best
        rows.append(dict(layer=li, recog_dm=recog_dm, recog_lr=float("nan"),
                         k2_hit_near=k2_hit_near, k2_near_none=k2_near_none,
                         k3_swap=k3_swap, transfer=transfer,
                         junk_best=junk_best, selectivity=selectivity, shuffle=float("nan")))

    best = max(rows, key=lambda r: r["recog_dm"])
    # logreg upper-bound + shuffle leak-check ONLY at the diff-of-means-selected layer:
    # the per-layer 5120-dim logreg sweep is the bottleneck (1 fit, not 65).
    Xb = Xrot[:, best["layer"], :]
    best["recog_lr"] = pooled_oof_auroc(Xb, y, g, cv, logreg_scores)
    best["shuffle"] = float(np.mean([
        pooled_oof_auroc(Xb, np.random.RandomState(1000 * seed + p).permutation(y), g, cv, diffmeans_scores)
        for p in range(N_SHUFFLE)]))
    return dict(n_kept=len(kept), n_dropped=n_drop, drop_rate=round(n_drop / max(len(kept) + n_drop, 1), 3),
                n_hit=int(is_hit.sum()), n_near=int(is_near.sum()), n_none=int(is_none.sum()),
                best_layer=best["layer"], best=best, per_layer=rows)


def verdict(b: dict) -> str:
    """Pre-registered kills (plan Exp 2). PASS only if all hold at the best layer."""
    k1 = b_drop = None
    checks = [
        ("K2 trigger-vs-near>=0.80", b["best"]["k2_hit_near"] >= 0.80),
        ("K2 near-vs-none<=0.65", b["best"]["k2_near_none"] <= 0.65),
        ("K3 rule-swap>=0.80", b["best"]["k3_swap"] >= 0.80),
        ("K4 selectivity>+0.10", b["best"]["selectivity"] > 0.10),
        ("shuffle~0.5", abs(b["best"]["shuffle"] - 0.5) < 0.15),
    ]
    failed = [name for name, ok in checks if not ok]
    return "ALL PASS" if not failed else "FAIL: " + ", ".join(failed)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--acts-dir", default="acts")
    ap.add_argument("--positions", default=",".join(DEFAULT_POSITIONS))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="probe_exp2.json")
    args = ap.parse_args()

    report = {}
    for cond in CONDS:
        report[cond] = {}
        for pos in args.positions.split(","):
            b = analyze(cond, args.acts_dir, pos, args.seed)
            report[cond][pos] = b
            print(f"\n===== {cond.upper()} | position {pos}  "
                  f"(kept {b['n_kept']}, dropped {b['n_dropped']} = {b['drop_rate']:.0%}; "
                  f"hit {b['n_hit']} / near {b['n_near']} / none {b['n_none']}) =====")
            print("layer | recog_dm | K2 hit-near | K2 near-none | K3 swap | transfer | selec")
            for r in b["per_layer"]:
                print(f"  {r['layer']:2d}  |  {r['recog_dm']:.3f}  | {r['k2_hit_near']:.3f}      | "
                      f"{r['k2_near_none']:.3f}       | {r['k3_swap']:.3f}   | {r['transfer']:.3f}    | "
                      f"{r['selectivity']:+.3f}")
            bb = b["best"]
            print(f"  >> best L{b['best_layer']}: recog dm {bb['recog_dm']:.3f} / lr {bb['recog_lr']:.3f} | "
                  f"K2 hit-near {bb['k2_hit_near']:.3f} / near-none {bb['k2_near_none']:.3f} | "
                  f"K3 swap {bb['k3_swap']:.3f} | transfer {bb['transfer']:.3f} | "
                  f"selec {bb['selectivity']:+.3f} | shuffle {bb['shuffle']:.3f}  ->  {verdict(b)}")

    Path(args.out).write_text(json.dumps(report, indent=2))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
