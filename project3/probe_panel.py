"""CPU step (Move 2 / separability): the PANEL probe + registered verdict battery.

Runs on the .npz from extract_panel.py. Tests the Move-2 claim: *per-condition
recognition directions stay separable and specific within one shared multi-rule
context* (plan_move2_separability.md — anchors frozen there).

Per condition (legal, medical), per read position, per layer:

  TRAIN a recognition direction on the panel ASK passes. Labels = the model's OWN
  answers, K1 consistency-filtered across the 3 paraphrases; activations rotate the
  paraphrase per item (format-confound guard). **The `both` cell is EXCLUDED from
  training** — the lattice audit (make_panel.py) showed both-docs make the other
  condition's seeking mildly predictive of the label, which would bias each direction
  TOWARD encoding the other condition (toward a false "collapsed"). Both-docs are
  scored as held-out targets instead, so composition is a generalization test.

  From document-disjoint OOF scores (pair-disjoint GroupKFold on meta.pair_stem):
   - FLOOR        : own-condition hits vs none (want >= 0.90) — in-panel readability.
   - CROSSFIRE    : OTHER-condition hits vs none — THE KILL-SWITCH.
                    <= 0.65 pass | >= 0.75 collapsed | between: gray.
   - COMPOSITION  : both-docs (held out) vs none (want >= 0.80).
   - K2-in-panel  : own hits vs own register-matched near (>= 0.80); near vs none (<= 0.65).
   - form (diag)  : generic advice-seeking on a neutral topic vs none — diagnostic only:
                    high => the direction reads generic seeking, not the condition.
   - ACTION pass  : the same four reads cross-pass into the multi-rule action context
                    (transfer / crossfire_action / composition_action).
   - junk (K4)    : selectivity = recog - best arbitrary-property decode (length hi/lo,
                    crc32 id parity — crc32, not hash(): stable across processes).
   - shuffle      : label-shuffle ~0.5 (at the selected layer; avg over 10 perms).
   - geometry     : cosine(direction_legal, direction_medical) per layer — descriptive.

  Headline numbers are LAYER-ROBUST MEDIANS over layers with recog > 0.9 (the Exp 2
  K3 lesson: best-layer reads of a *different* metric cherry-pick excursions); the
  best-recog layer is reported alongside. Verdict reads the medians at message_last.

Usage (after extract_panel.sh writes acts/panel_{ask,action}*__<pos>.npz):
    ./.venv/bin/python probe_panel.py --acts-dir acts --out probe_panel.json
Smoke (fabricated activations, verifies the whole path + expected pattern):
    ./.venv/bin/python probe_panel_smoke.py
    ./.venv/bin/python probe_panel.py --acts-dir /tmp/panel_smoke --out /tmp/probe_panel_smoke.json
"""

from __future__ import annotations

import argparse
import json
import zlib
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

from train_probe import diffmeans_scores, logreg_scores, pooled_oof_auroc, make_cv_splitter
from cross_pass_probe import cross_pass_score

DEFAULT_POSITIONS = ["message_last", "message_mean", "final", "pre_message_final"]
CONDS = ["legal", "medical"]
N_SHUFFLE = 10
RECOG_BAND = 0.9   # layers with recog above this form the layer-robust median band


# --- carried verbatim from probe_exp2.py (copied, not imported: fresh-files rule) ----
def load_npz(prefix: str, position: str) -> dict:
    d = np.load(f"{prefix}__{position}.npz", allow_pickle=True)
    return {
        "acts": d["activations"],
        "ids": [str(x) for x in d["ids"]],
        "labels": d["labels"].astype(int),
        "groups": [str(x) for x in d["groups"]],
        "beh": [str(x) for x in d["behaviour"]],
        "doccond": [str(x) for x in d["doccond"]],
        "cell": [str(x) for x in d["cell"]],
        "seq_len": d["seq_len"].astype(int),
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
# -------------------------------------------------------------------------------------


def panel_oof(Xtr_li, ytr, train_stems, fold_of_full, n_folds, target_vecs, target_stems):
    """Document-disjoint cross-pass diff-of-means. Like probe_exp2's pair_oof, but
    fold_of_full also assigns folds to stems absent from training (the held-out both
    cell, round-robin) — a direction trained on the other folds never saw them anyway."""
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


def analyze(cond: str, acts_dir: str, position: str, seed: int) -> dict:
    other = "medical" if cond == "legal" else "legal"
    ask_ps = [load_npz(f"{acts_dir}/panel_ask_{cond}_p{k}", position) for k in (1, 2, 3)]
    act = load_npz(f"{acts_dir}/panel_action", position)

    kept, y_all, n_drop = consistency_filter(ask_ps)
    base = ask_ps[0]
    cellk = [base["cell"][i] for i in kept]
    docck = [base["doccond"][i] for i in kept]
    stemsk = [base["groups"][i] for i in kept]
    idsk = [base["ids"][i] for i in kept]
    seqk = np.array([base["seq_len"][i] for i in kept])
    Xrot = rotating_acts(ask_ps, kept)                              # [Nk, L+1, D]

    # Training set: kept docs EXCLUDING the both cell (see module docstring).
    tr_idx = [j for j, c in enumerate(cellk) if c != "both"]
    both_idx = [j for j, (c, lab) in enumerate(zip(cellk, y_all))
                if c == "both" and lab == 1]                        # consistent-YES both docs
    n_both_dropped = sum(1 for c, lab in zip(cellk, y_all) if c == "both" and lab != 1)

    ytr = y_all[tr_idx]
    gtr = np.array([stemsk[j] for j in tr_idx])
    Xtr = Xrot[tr_idx]                                              # [Ntr, L+1, D]
    seqtr = seqk[tr_idx]
    idstr = [idsk[j] for j in tr_idx]

    # subset masks within training rows
    def mask(pred):
        return np.array([pred(docck[j], cellk[j]) for j in tr_idx])
    is_own_hit = mask(lambda d, c: c == "hit" and d == cond)
    is_other_hit = mask(lambda d, c: c == "hit" and d == other)
    is_own_near = mask(lambda d, c: c == "near" and d == cond)
    is_none = mask(lambda d, c: c == "none")
    is_form = mask(lambda d, c: c == "form")

    cv = make_cv_splitter("group", gtr, seed)
    folds = list(cv.split(np.zeros((len(gtr), 1)), ytr, gtr))
    n_folds = len(folds)
    fold_of_full = {}
    for f, (_tr, te) in enumerate(folds):
        for k in te:
            fold_of_full[gtr[k]] = f
    unseen = sorted({stemsk[j] for j in both_idx} - set(fold_of_full))
    for i, s in enumerate(unseen):                                  # round-robin for held-out stems
        fold_of_full[s] = i % n_folds

    # action-pass target rows by id (kept docs only — stems must resolve to a fold)
    a_row = {i: k for k, i in enumerate(act["ids"])}
    def act_targets(ids_subset):
        rows = [a_row[i] for i in ids_subset if i in a_row]
        stems = [act["groups"][r] for r in rows]
        return rows, stems
    own_hit_ids = [i for i, m in zip(idstr, is_own_hit) if m]
    other_hit_ids = [i for i, m in zip(idstr, is_other_hit) if m]
    none_ids = [i for i, m in zip(idstr, is_none) if m]
    both_ids = [idsk[j] for j in both_idx]
    tgt = {name: act_targets(idlist) for name, idlist in
           [("own_hit", own_hit_ids), ("other_hit", other_hit_ids),
            ("none", none_ids), ("both", both_ids)]}

    junk = {
        "len_hi": (seqtr > np.median(seqtr)).astype(int),
        "crc_parity": np.array([zlib.crc32(i.encode()) % 2 for i in idstr]),
    }

    n_layers = Xtr.shape[1]
    rows, dirs = [], []
    for li in range(n_layers):
        X = Xtr[:, li, :]
        s = panel_oof(X, ytr, gtr, fold_of_full, n_folds, X, gtr)   # in-pass OOF scores
        s_both = panel_oof(X, ytr, gtr, fold_of_full, n_folds,
                           Xrot[both_idx][:, li, :], [stemsk[j] for j in both_idx])
        recog_dm = auroc(s[ytr == 1], s[ytr == 0])

        a = {name: panel_oof(X, ytr, gtr, fold_of_full, n_folds,
                             act["acts"][rows_][:, li, :], stems_)
             for name, (rows_, stems_) in tgt.items()}

        junk_best = 0.0
        for jl in junk.values():
            if len(set(jl)) > 1:
                v = pooled_oof_auroc(X, jl, gtr, cv, diffmeans_scores)
                junk_best = max(junk_best, v, 1 - v)

        # two directions for geometry: the operational probe direction (all training
        # negatives — mildly ANTI-aligned across conditions by construction, since each
        # one's negatives contain the other's hits), and a "pure" hit-vs-none direction
        # (the representational read; orthogonal signals give cosine ~0 here).
        d = X[ytr == 1].astype(np.float64).mean(0) - X[ytr == 0].astype(np.float64).mean(0)
        d_pure = X[is_own_hit].astype(np.float64).mean(0) - X[is_none].astype(np.float64).mean(0)
        dirs.append((d, d_pure))
        rows.append(dict(
            layer=li, recog_dm=recog_dm,
            floor=auroc(s[is_own_hit], s[is_none]),
            crossfire=auroc(s[is_other_hit], s[is_none]),
            composition=auroc(s_both, s[is_none]),
            k2_hit_near=auroc(s[is_own_hit], s[is_own_near]),
            k2_near_none=auroc(s[is_own_near], s[is_none]),
            form_diag=auroc(s[is_form], s[is_none]),
            transfer=auroc(a["own_hit"], a["none"]),
            crossfire_action=auroc(a["other_hit"], a["none"]),
            composition_action=auroc(a["both"], a["none"]),
            junk_best=junk_best, selectivity=recog_dm - junk_best,
        ))

    best = max(rows, key=lambda r: r["recog_dm"])
    Xb = Xtr[:, best["layer"], :]
    best["recog_lr"] = pooled_oof_auroc(Xb, ytr, gtr, cv, logreg_scores)
    best["shuffle"] = float(np.mean([
        pooled_oof_auroc(Xb, np.random.RandomState(1000 * seed + p).permutation(ytr), gtr, cv,
                         diffmeans_scores) for p in range(N_SHUFFLE)]))

    robust = {k: band_median(rows, k) for k in
              ("floor", "crossfire", "composition", "k2_hit_near", "k2_near_none",
               "form_diag", "transfer", "crossfire_action", "composition_action",
               "selectivity")}
    robust["n_band_layers"] = int(sum(r["recog_dm"] > RECOG_BAND for r in rows))

    return dict(n_kept=len(kept), n_dropped=n_drop,
                n_train=len(tr_idx), n_both_scored=len(both_idx), n_both_dropped=n_both_dropped,
                n_own_hit=int(is_own_hit.sum()), n_other_hit=int(is_other_hit.sum()),
                n_near=int(is_own_near.sum()), n_none=int(is_none.sum()), n_form=int(is_form.sum()),
                best_layer=best["layer"], best=best, robust=robust, per_layer=rows,
                _dirs=np.stack([d for d, _ in dirs], axis=0),        # [L+1, D]; stripped before JSON
                _dirs_pure=np.stack([dp for _, dp in dirs], axis=0))


def verdict(robust: dict, best: dict) -> str:
    """Registered anchors (plan_move2_separability.md), read on layer-robust medians."""
    checks = [
        ("FLOOR own-hit-vs-none >= 0.90", robust["floor"] >= 0.90),
        ("COMPOSITION both-vs-none >= 0.80", robust["composition"] >= 0.80),
        ("K2 hit-vs-near >= 0.80", robust["k2_hit_near"] >= 0.80),
        ("K2 near-vs-none <= 0.65", robust["k2_near_none"] <= 0.65),
        ("K4 selectivity > +0.10", robust["selectivity"] > 0.10),
        ("shuffle ~0.5", abs(best["shuffle"] - 0.5) < 0.15),
    ]
    failed = [name for name, ok in checks if not ok]
    cf = robust["crossfire"]
    cross = ("PASS (specific)" if cf <= 0.65 else
             "COLLAPSED (generic salience) — the kill" if cf >= 0.75 else
             "GRAY (partial interference — report, no goalpost moves)")
    out = f"crossfire={cf:.3f} -> {cross}"
    if failed:
        out += " | FAILED: " + ", ".join(failed)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--acts-dir", default="acts")
    ap.add_argument("--positions", default=",".join(DEFAULT_POSITIONS))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="probe_panel.json")
    args = ap.parse_args()

    report: dict = {}
    dirs_store: dict = {}
    for cond in CONDS:
        report[cond] = {}
        for pos in args.positions.split(","):
            b = analyze(cond, args.acts_dir, pos, args.seed)
            dirs_store[(cond, pos)] = (b.pop("_dirs"), b.pop("_dirs_pure"))
            report[cond][pos] = b
            print(f"\n===== {cond.upper()} | {pos}  (train {b['n_train']}, both-scored "
                  f"{b['n_both_scored']}, K1-dropped {b['n_dropped']}) =====")
            print("layer | recog | floor | CROSSFIRE | compos | hit-near | near-none | form | transfer | selec")
            for r in b["per_layer"]:
                print(f"  {r['layer']:2d}  | {r['recog_dm']:.3f} | {r['floor']:.3f} |  {r['crossfire']:.3f}    "
                      f"| {r['composition']:.3f}  | {r['k2_hit_near']:.3f}    | {r['k2_near_none']:.3f}     "
                      f"| {r['form_diag']:.3f}| {r['transfer']:.3f}    | {r['selectivity']:+.3f}")
            rb = b["robust"]
            print(f"  >> robust medians (recog>{RECOG_BAND}, {rb['n_band_layers']} layers): "
                  f"floor {rb['floor']:.3f} | CROSSFIRE {rb['crossfire']:.3f} | compos {rb['composition']:.3f} | "
                  f"hit-near {rb['k2_hit_near']:.3f} | near-none {rb['k2_near_none']:.3f} | "
                  f"form {rb['form_diag']:.3f} | transfer {rb['transfer']:.3f} | "
                  f"cf-action {rb['crossfire_action']:.3f} | compos-action {rb['composition_action']:.3f} | "
                  f"selec {rb['selectivity']:+.3f}")
            print(f"  >> best L{b['best_layer']} recog dm {b['best']['recog_dm']:.3f} / "
                  f"lr {b['best']['recog_lr']:.3f} | shuffle {b['best']['shuffle']:.3f}")
            if pos == "pre_message_final":
                print(f"  >> [{cond}/{pos}]: NEGATIVE CONTROL — recog must be ~0.5 and the "
                      f"verdict checks are EXPECTED to fail here; any signal = pipeline leak. "
                      f"(recog at best layer: {b['best']['recog_dm']:.3f})")
            else:
                print(f"  >> VERDICT [{cond}/{pos}]: {verdict(rb, b['best'])}")

    # Geometry per position: cosine between the conditions' directions, per layer.
    # 'probe' = the operational training direction (anti-aligned-by-construction caveat);
    # 'pure'  = hit-vs-none means only — the representational read (planted-orthogonal
    # smoke gives ~0 here). Both descriptive, never gated.
    report["geometry"] = {}
    for pos in args.positions.split(","):
        (dl, dl_pure), (dm, dm_pure) = dirs_store[("legal", pos)], dirs_store[("medical", pos)]

        def cosines(a, b):
            return [float(np.dot(a[li], b[li]) /
                          (np.linalg.norm(a[li]) * np.linalg.norm(b[li]) + 1e-12))
                    for li in range(a.shape[0])]
        cos, cos_pure = cosines(dl, dm), cosines(dl_pure, dm_pure)
        band_layers = [r["layer"] for r in report["legal"][pos]["per_layer"]
                       if r["recog_dm"] > RECOG_BAND
                       and report["medical"][pos]["per_layer"][r["layer"]]["recog_dm"] > RECOG_BAND]
        med = float(np.median([cos[li] for li in band_layers])) if band_layers else float("nan")
        med_pure = float(np.median([cos_pure[li] for li in band_layers])) if band_layers else float("nan")
        report["geometry"][pos] = {"cos_per_layer": cos, "cos_band_median": med,
                                   "cos_pure_per_layer": cos_pure, "cos_pure_band_median": med_pure}
        print(f"\ngeometry [{pos}] over the shared recog>{RECOG_BAND} band: "
              f"probe-direction cos = {med:.3f} (anti-aligned-by-construction caveat) | "
              f"pure hit-vs-none cos = {med_pure:.3f}")

    Path(args.out).write_text(json.dumps(report, indent=2))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
