"""CPU step: the keyphrase recognition probe + watchdog analysis (runs on the .npz from
extract_keyphrase.py — no GPU).

Implements the test design we settled on, per read-position, per layer:

  TRAIN  a recognition probe on the ASK pass: present (recognised) vs absent. diff-of-means
         leads, logreg as upper bound, pair-disjoint CV (GroupKFold on the matched-pair stem,
         so a pair's two halves never split across folds — the inflation bug we fixed).

  Then FREEZE the ask-trained direction and score other passes (cross-pass: a probe that never
  saw an action can't be reading "about to act"):
   - TRANSFER : present-action vs absent-action  -> does recognition survive into the action pass?
   - SWAP     : present-action vs swap (same document, name OFF the watchlist) -> the sharp
                control: both have the name in the text, so separation = reading membership
                recognition, not the name's mere presence / system-user co-occurrence.
   - WATCHDOG : the gap pile (present, recognised under load per loaded-ask, but action emitted
                NO FLAG) vs the swap darks -> does the probe fire on omitted-but-recognised items?

Headline per position = the best layer by in-pass recognition AUROC, with the transfer / swap /
watchdog numbers at that layer. The gap pile is small (~8) so its numbers are reported with the
honest caveat (n shown); the swap/transfer numbers are well-powered (72 each).

Usage (after extract_keyphrase.py writes <prefix>__<pos>.npz for ask/action/loadedask/swap):
    python probe_keyphrase.py --ask acts/v4_ask --action acts/v4_action \
        --loadedask acts/v4_loadedask --swap acts/v4_swap --out probe_v4.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

from train_probe import diffmeans_scores, logreg_scores, pooled_oof_auroc, make_cv_splitter
from cross_pass_probe import cross_pass_score

DEFAULT_POSITIONS = ["final", "name_last", "doc_last", "doc_mean"]


def load_npz(prefix: str, position: str) -> dict:
    d = np.load(f"{prefix}__{position}.npz", allow_pickle=True)
    return {
        "acts": d["activations"],                       # [N, L+1, D]
        "ids": [str(x) for x in d["ids"]],
        "labels": d["labels"].astype(int),              # ground truth: 1 present / 0 absent
        "groups": [str(x) for x in d["groups"]],        # matched-pair stem
        "beh": [str(x) for x in d["behaviour"]],        # YES/NO (recog) or FLAG/NOFLAG (action)
    }


def by_id(p: dict) -> dict:
    return {i: k for k, i in enumerate(p["ids"])}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ask", required=True, help="ask npz prefix (clean recognition, probe training)")
    ap.add_argument("--action", required=True, help="action npz prefix (the behaviour)")
    ap.add_argument("--loadedask", required=True, help="loaded-ask npz prefix (recognition-under-load reference)")
    ap.add_argument("--swap", required=True, help="swap-watchlist npz prefix (dark control)")
    ap.add_argument("--positions", default=",".join(DEFAULT_POSITIONS))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="probe_keyphrase.json")
    args = ap.parse_args()

    report = {}
    for pos in args.positions.split(","):
        ask = load_npz(args.ask, pos); act = load_npz(args.action, pos)
        lda = load_npz(args.loadedask, pos); swp = load_npz(args.swap, pos)
        a_row, l_row, s_row = by_id(act), by_id(lda), {g: k for k, g in enumerate(swp["groups"])}

        # ASK training set: recognition label from the model's own ask answer (drop unclear).
        keep = [k for k, b in enumerate(ask["beh"]) if b in ("YES", "NO")]
        y = np.array([1 if ask["beh"][k] == "YES" else 0 for k in keep])
        g = [ask["groups"][k] for k in keep]
        ids_keep = [ask["ids"][k] for k in keep]
        n_layers = ask["acts"].shape[1]

        # present items present in BOTH ask and action, recognised-under-load, split by FLAG.
        pres_ids = [i for i in ids_keep if i.endswith("a") and i in a_row]
        gap_ids = [i for i in pres_ids
                   if lda["beh"][l_row[i]] == "YES" and act["beh"][a_row[i]] == "NOFLAG"] \
            if all(i in l_row for i in pres_ids) else \
            [i for i in pres_ids if i in l_row and lda["beh"][l_row[i]] == "YES"
             and act["beh"][a_row[i]] == "NOFLAG"]
        # swap darks aligned to present items by pair stem
        swap_ids = [i for i in pres_ids if i[:-1] in s_row]

        cv = make_cv_splitter("group", np.array(g), args.seed)  # pair-disjoint folds
        rows = []
        for li in range(n_layers):
            Xask = ask["acts"][keep][:, li, :]
            inpass_dm = pooled_oof_auroc(Xask, y, np.array(g), cv, diffmeans_scores)
            inpass_lr = pooled_oof_auroc(Xask, y, np.array(g), cv, logreg_scores)

            # freeze ask-trained direction; score the other passes
            def score(rows_idx, src):  # cross_pass_score trains on full ask, scores src rows
                return cross_pass_score(Xask, y, src["acts"][rows_idx][:, li, :], "diffmeans")

            act_all = [a_row[i] for i in ids_keep if i in a_row]
            y_act = np.array([act["labels"][r] for r in act_all])
            transfer = roc_auc_score(y_act, score(act_all, act)) if len(set(y_act)) == 2 else float("nan")

            pres_rows = [a_row[i] for i in pres_ids]
            swap_rows = [s_row[i[:-1]] for i in swap_ids]
            s_pres = score(pres_rows, act)
            s_swap = score(swap_rows, swp) if swap_rows else np.array([])
            # present (real hit) vs swap (name present, off-list) — the sharp test
            pres_vs_swap = (roc_auc_score([1] * len(s_pres) + [0] * len(s_swap),
                                          np.concatenate([s_pres, s_swap]))
                            if len(s_swap) else float("nan"))
            # watchdog: gap items vs swap darks
            gap_rows = [a_row[i] for i in gap_ids]
            s_gap = score(gap_rows, act) if gap_rows else np.array([])
            gap_vs_swap = (roc_auc_score([1] * len(s_gap) + [0] * len(s_swap),
                                         np.concatenate([s_gap, s_swap]))
                           if len(s_gap) and len(s_swap) else float("nan"))
            rows.append(dict(layer=li, inpass_dm=inpass_dm, inpass_lr=inpass_lr, transfer=transfer,
                             pres_vs_swap=pres_vs_swap, gap_vs_swap=gap_vs_swap,
                             gap_mean=float(np.mean(s_gap)) if len(s_gap) else float("nan"),
                             swap_mean=float(np.mean(s_swap)) if len(s_swap) else float("nan"),
                             pres_mean=float(np.mean(s_pres)) if len(s_pres) else float("nan")))

        best = max(rows, key=lambda r: r["inpass_dm"])
        report[pos] = dict(n_train=len(keep), n_present=len(pres_ids), n_gap=len(gap_ids),
                           n_swap=len(swap_ids), best_layer=best["layer"], best=best, per_layer=rows)
        print(f"\n===== position: {pos}  (train {len(keep)} | present {len(pres_ids)} | "
              f"gap {len(gap_ids)} | swap {len(swap_ids)}) =====")
        print("layer | recog dm/lr (in-pass) | transfer | pres-vs-SWAP | gap-vs-swap (watchdog)")
        for r in rows:
            print(f"  {r['layer']:2d}  |   {r['inpass_dm']:.3f} / {r['inpass_lr']:.3f}     |  "
                  f"{r['transfer']:.3f}  |   {r['pres_vs_swap']:.3f}     |  {r['gap_vs_swap']:.3f}")
        print(f"  >> best layer {best['layer']}: recog {best['inpass_dm']:.3f} | transfer {best['transfer']:.3f} "
              f"| pres-vs-swap {best['pres_vs_swap']:.3f} | gap-vs-swap {best['gap_vs_swap']:.3f} "
              f"(gap n={len(gap_ids)}, swap n={len(swap_ids)})")

    Path(args.out).write_text(json.dumps(report, indent=2))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
