"""CPU step (Move 3 / playbook yield): the N-condition PANEL probe + battery + interference curve.

Runs on the .npz from extract_playbook.py. For each surviving condition, trains a
recognition direction on its panel ASK pass (labels = the model's OWN K1-consistency-
filtered YES/NO, paraphrase-rotated) and runs the PLAYBOOK Step-6 battery. Then derives
the Step-7 interference curve across conditions.

Per condition X, per read position, per layer (document-disjoint pair-OOF on pair_stem):
  FLOOR        own-hit vs none                    (>= 0.90)  in-panel readability
  K2 hit-near  own-hit vs own register-matched near(>= 0.80) THE topic kill-switch
  K2 near-none own-near vs none                   (<= 0.65)  near must not fire
  SPECIFICITY  own-hit vs other-cond hits  (pooled & per-other; >= 0.80) the kill-switch
  form (diag)  neutral advice-form vs none                   diagnostic only
  transfer     own-hit vs none in the ACTION pass (cross-pass robustness)
  junk (K4)    selectivity = recog - best arbitrary-property decode (length, crc parity)
  shuffle      label-shuffle ~0.5 ;  layer-0 recog ~0.5 (pipeline sanity)

Headline numbers are LAYER-ROBUST MEDIANS over layers with recog > 0.9, message_last primary.

Interference curve (Step 7), from the single N-rule extraction:
  - specificity matrix S[X][Y] = AUROC(probe_X: own-hit vs Y-hit), per ordered pair;
  - pooled specificity per X (own-hit vs ALL other hits) — the N-1 competitor readout;
  - mean pairwise cosine of the N pure hit-vs-none directions (does the shared
    "a-rule-fired" component dominate as N grows?).
  At N survivors the curve is short (few interior points) — reported honestly as a matrix.

Usage (after extract_playbook writes acts/playbook_{ask,action}*__<pos>.npz):
    ./.venv/bin/python probe_playbook.py --acts-dir acts --out probe_playbook.json
Smoke (fabricated activations): ./.venv/bin/python probe_playbook_smoke.py
"""

from __future__ import annotations

import argparse
import json
import zlib
from itertools import combinations
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

from train_probe import diffmeans_scores, logreg_scores, pooled_oof_auroc, make_cv_splitter
from cross_pass_probe import cross_pass_score

DEFAULT_POSITIONS = ["message_last", "message_mean", "final", "pre_message_final"]
N_SHUFFLE = 10
RECOG_BAND = 0.9


def load_npz(prefix: str, position: str) -> dict:
    d = np.load(f"{prefix}__{position}.npz", allow_pickle=True)
    return {
        "acts": d["activations"], "ids": [str(x) for x in d["ids"]],
        "labels": d["labels"].astype(int), "groups": [str(x) for x in d["groups"]],
        "beh": [str(x) for x in d["behaviour"]], "doccond": [str(x) for x in d["doccond"]],
        "cell": [str(x) for x in d["cell"]], "seq_len": d["seq_len"].astype(int),
    }


def consistency_filter(ask_ps: list[dict]) -> tuple[list[int], np.ndarray, int]:
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
    return np.stack([ask_ps[j % 3]["acts"][i] for j, i in enumerate(kept)], axis=0)


def auroc(pos_scores, neg_scores) -> float:
    if not len(pos_scores) or not len(neg_scores):
        return float("nan")
    return roc_auc_score([1] * len(pos_scores) + [0] * len(neg_scores),
                         np.concatenate([pos_scores, neg_scores]))


def panel_oof(Xtr_li, ytr, train_stems, fold_of_full, n_folds, target_vecs, target_stems):
    out = np.full(len(target_vecs), np.nan)
    if len(target_vecs) == 0:
        return out
    target_stems = list(target_stems)
    for f in range(n_folds):
        tr = np.array([fold_of_full[s] != f for s in train_stems])
        te = [j for j, s in enumerate(target_stems) if fold_of_full[s] == f]
        if te:
            out[te] = cross_pass_score(Xtr_li[tr], ytr[tr], target_vecs[te], "diffmeans")
    assert not np.isnan(out).any(), "a target item was never scored (stem missing a fold)"
    return out


def band_median(rows: list[dict], key: str) -> float:
    band = [r[key] for r in rows if r["recog_dm"] > RECOG_BAND and not np.isnan(r[key])]
    return float(np.median(band)) if band else float("nan")


def analyze(cond: str, conds: list[str], acts_dir: str, position: str, seed: int,
            prefix: str = "playbook") -> dict:
    others = [c for c in conds if c != cond]
    ask_ps = [load_npz(f"{acts_dir}/{prefix}_ask_{cond}_p{k}", position) for k in (1, 2, 3)]
    act = load_npz(f"{acts_dir}/{prefix}_action", position)

    kept, y_all, n_drop = consistency_filter(ask_ps)
    base = ask_ps[0]
    cellk = [base["cell"][i] for i in kept]
    docck = [base["doccond"][i] for i in kept]
    stemsk = [base["groups"][i] for i in kept]
    idsk = [base["ids"][i] for i in kept]
    seqk = np.array([base["seq_len"][i] for i in kept])
    Xrot = rotating_acts(ask_ps, kept)

    ytr = y_all
    gtr = np.array(stemsk)
    Xtr = Xrot
    seqtr = seqk
    idstr = idsk

    def mask(pred):
        return np.array([pred(docck[j], cellk[j]) for j in range(len(idstr))])
    is_own_hit = mask(lambda d, c: c == "hit" and d == cond)
    is_own_near = mask(lambda d, c: c == "near" and d == cond)
    is_none = mask(lambda d, c: c == "none")
    is_form = mask(lambda d, c: c == "form")
    is_other_hit = {o: mask(lambda d, c, o=o: c == "hit" and d == o) for o in others}
    is_any_other_hit = mask(lambda d, c: c == "hit" and d in others)

    cv = make_cv_splitter("group", gtr, seed)
    folds = list(cv.split(np.zeros((len(gtr), 1)), ytr, gtr))
    n_folds = len(folds)
    fold_of_full = {}
    for f, (_tr, te) in enumerate(folds):
        for k in te:
            fold_of_full[gtr[k]] = f

    # action-pass targets by id (kept docs only)
    a_row = {i: k for k, i in enumerate(act["ids"])}

    def act_targets(idlist):
        rows = [a_row[i] for i in idlist if i in a_row]
        return rows, [act["groups"][r] for r in rows]
    own_hit_ids = [idstr[j] for j in range(len(idstr)) if is_own_hit[j]]
    none_ids = [idstr[j] for j in range(len(idstr)) if is_none[j]]
    tgt_own = act_targets(own_hit_ids)
    tgt_none = act_targets(none_ids)

    junk = {
        "len_hi": (seqtr > np.median(seqtr)).astype(int),
        "crc_parity": np.array([zlib.crc32(i.encode()) % 2 for i in idstr]),
    }

    n_layers = Xtr.shape[1]
    rows, pure_dirs = [], []
    for li in range(n_layers):
        X = Xtr[:, li, :]
        s = panel_oof(X, ytr, gtr, fold_of_full, n_folds, X, gtr)
        recog_dm = auroc(s[ytr == 1], s[ytr == 0])

        a_own = panel_oof(X, ytr, gtr, fold_of_full, n_folds, act["acts"][tgt_own[0]][:, li, :], tgt_own[1])
        a_none = panel_oof(X, ytr, gtr, fold_of_full, n_folds, act["acts"][tgt_none[0]][:, li, :], tgt_none[1])

        spec_each = {o: auroc(s[is_own_hit], s[is_other_hit[o]]) for o in others}
        junk_best = 0.0
        for jl in junk.values():
            if len(set(jl)) > 1:
                v = pooled_oof_auroc(X, jl, gtr, cv, diffmeans_scores)
                junk_best = max(junk_best, v, 1 - v)

        d_pure = X[is_own_hit].astype(np.float64).mean(0) - X[is_none].astype(np.float64).mean(0)
        pure_dirs.append(d_pure)
        row = dict(
            layer=li, recog_dm=recog_dm,
            floor=auroc(s[is_own_hit], s[is_none]),
            k2_hit_near=auroc(s[is_own_hit], s[is_own_near]),
            k2_near_none=auroc(s[is_own_near], s[is_none]),
            specificity=auroc(s[is_own_hit], s[is_any_other_hit]),
            form_diag=auroc(s[is_form], s[is_none]),
            transfer=auroc(a_own, a_none),
            junk_best=junk_best, selectivity=recog_dm - junk_best,
        )
        for o in others:
            row[f"spec__{o}"] = spec_each[o]
        rows.append(row)

    best = max(rows, key=lambda r: r["recog_dm"])
    Xb = Xtr[:, best["layer"], :]
    best["recog_lr"] = pooled_oof_auroc(Xb, ytr, gtr, cv, logreg_scores)
    best["shuffle"] = float(np.mean([
        pooled_oof_auroc(Xb, np.random.RandomState(1000 * seed + p).permutation(ytr), gtr, cv,
                         diffmeans_scores) for p in range(N_SHUFFLE)]))
    layer0_recog = rows[0]["recog_dm"]

    keys = ["floor", "k2_hit_near", "k2_near_none", "specificity", "form_diag",
            "transfer", "selectivity"] + [f"spec__{o}" for o in others]
    robust = {k: band_median(rows, k) for k in keys}
    robust["n_band_layers"] = int(sum(r["recog_dm"] > RECOG_BAND for r in rows))

    return dict(n_kept=len(kept), n_dropped=n_drop, n_train=len(idstr),
                n_own_hit=int(is_own_hit.sum()), n_own_near=int(is_own_near.sum()),
                n_none=int(is_none.sum()), n_form=int(is_form.sum()),
                n_other_hit={o: int(is_other_hit[o].sum()) for o in others},
                best_layer=best["layer"], layer0_recog=layer0_recog,
                best=best, robust=robust, per_layer=rows,
                _pure=np.stack(pure_dirs, axis=0))


def verdict(cond: str, robust: dict, best: dict, layer0: float) -> tuple[str, bool]:
    checks = [
        ("FLOOR >= 0.90", robust["floor"] >= 0.90),
        ("K2 hit-near >= 0.80", robust["k2_hit_near"] >= 0.80),
        ("K2 near-none <= 0.65", robust["k2_near_none"] <= 0.65),
        ("SPECIFICITY >= 0.80", robust["specificity"] >= 0.80),
        ("K4 selectivity > +0.10", robust["selectivity"] > 0.10),
        ("shuffle ~0.5", abs(best["shuffle"] - 0.5) < 0.15),
        ("layer-0 ~0.5", abs(layer0 - 0.5) < 0.15),
    ]
    failed = [name for name, ok in checks if not ok]
    return ("PASS — recognition probe is specific" if not failed
            else "FAIL: " + ", ".join(failed)), not failed


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--acts-dir", default="acts")
    ap.add_argument("--positions", default=",".join(DEFAULT_POSITIONS))
    ap.add_argument("--flag-vocab", default="playbook_flag_vocab.json")
    ap.add_argument("--prefix", default="playbook", help="file stem: playbook | pbmask")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="probe_playbook.json")
    args = ap.parse_args()

    conds = list(json.loads(Path(args.flag_vocab).read_text()).keys())
    positions = args.positions.split(",")
    report: dict = {"_conds": conds}
    pure_store: dict = {}

    for cond in conds:
        report[cond] = {}
        for pos in positions:
            b = analyze(cond, conds, args.acts_dir, pos, args.seed, args.prefix)
            pure_store[(cond, pos)] = b.pop("_pure")
            report[cond][pos] = b
            others = [c for c in conds if c != cond]
            print(f"\n===== {cond.upper()} | {pos}  (train {b['n_train']}, K1-dropped {b['n_dropped']}) =====")
            hdr = "layer | recog | floor | hit-near | near-none | SPECIF | " + " | ".join(f"v{o[:6]}" for o in others) + " | form | transf | selec"
            print(hdr)
            for r in b["per_layer"]:
                spx = " | ".join(f"{r[f'spec__{o}']:.3f}" for o in others)
                print(f"  {r['layer']:2d}  | {r['recog_dm']:.3f} | {r['floor']:.3f} | {r['k2_hit_near']:.3f}    "
                      f"| {r['k2_near_none']:.3f}     | {r['specificity']:.3f} | {spx} | {r['form_diag']:.3f}"
                      f"| {r['transfer']:.3f} | {r['selectivity']:+.3f}")
            rb = b["robust"]
            print(f"  >> robust medians (recog>{RECOG_BAND}, {rb['n_band_layers']} layers): "
                  f"floor {rb['floor']:.3f} | hit-near {rb['k2_hit_near']:.3f} | near-none {rb['k2_near_none']:.3f} | "
                  f"SPECIFICITY {rb['specificity']:.3f} | form {rb['form_diag']:.3f} | transfer {rb['transfer']:.3f} | "
                  f"selec {rb['selectivity']:+.3f}")
            print(f"  >> best L{b['best_layer']} recog dm {b['best']['recog_dm']:.3f} / lr {b['best']['recog_lr']:.3f} | "
                  f"shuffle {b['best']['shuffle']:.3f} | layer-0 {b['layer0_recog']:.3f}")
            if pos == "pre_message_final":
                print(f"  >> [{cond}/{pos}]: NEGATIVE CONTROL — recog ~0.5 expected; checks expected to FAIL.")
            else:
                v, ok = verdict(cond, rb, b["best"], b["layer0_recog"])
                print(f"  >> VERDICT [{cond}/{pos}]: {v}")

    # ---- Interference curve (Step 7): specificity + cosine matrices, primary position ----
    primary = positions[0]
    spec_matrix = {}     # spec_matrix[X][Y] = robust spec of probe_X vs Y-hits
    pooled_spec = {}
    for cond in conds:
        rb = report[cond][primary]["robust"]
        others = [c for c in conds if c != cond]
        spec_matrix[cond] = {o: rb[f"spec__{o}"] for o in others}
        pooled_spec[cond] = rb["specificity"]

    # mean pairwise cosine of pure directions over the shared recog>band layers
    def band_layers(cond, pos):
        return [r["layer"] for r in report[cond][pos]["per_layer"] if r["recog_dm"] > RECOG_BAND]
    cos_matrix = {}
    cos_vals = []
    for a, c in combinations(conds, 2):
        da, dc = pure_store[(a, primary)], pure_store[(c, primary)]
        shared = sorted(set(band_layers(a, primary)) & set(band_layers(c, primary)))
        if shared:
            cs = [float(np.dot(da[li], dc[li]) / (np.linalg.norm(da[li]) * np.linalg.norm(dc[li]) + 1e-12))
                  for li in shared]
            m = float(np.median(cs))
        else:
            m = float("nan")
        cos_matrix[f"{a}|{c}"] = m
        if not np.isnan(m):
            cos_vals.append(m)
    mean_cos = float(np.mean(cos_vals)) if cos_vals else float("nan")

    interference = {
        "primary_position": primary,
        "specificity_matrix": spec_matrix,
        "pooled_specificity": pooled_spec,
        "min_pooled_specificity": float(np.nanmin(list(pooled_spec.values()))) if pooled_spec else float("nan"),
        "mean_pooled_specificity": float(np.nanmean(list(pooled_spec.values()))) if pooled_spec else float("nan"),
        "pairwise_cosine": cos_matrix,
        "mean_pairwise_cosine": mean_cos,
        "note": f"N={len(conds)} survivors — short curve; matrix is the honest artifact. "
                "Move 2 (N=2, legal/medical) pure-cosine reference was 0.874.",
    }
    report["interference"] = interference
    print("\n===== INTERFERENCE (Step 7), position", primary, "=====")
    print("specificity matrix  probe_X vs Y-hits (robust median):")
    for x in conds:
        print(f"  {x:22s}: " + ", ".join(f"{y}={spec_matrix[x][y]:.3f}" for y in spec_matrix[x])
              + f"  | pooled(own vs all-other)={pooled_spec[x]:.3f}")
    print(f"mean pairwise cosine (pure hit-vs-none dirs) = {mean_cos:.3f}  (Move-2 N=2 ref 0.874)")
    print(f"pooled specificity: min {interference['min_pooled_specificity']:.3f} / "
          f"mean {interference['mean_pooled_specificity']:.3f}")

    Path(args.out).write_text(json.dumps(report, indent=2))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
