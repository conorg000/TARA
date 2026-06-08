"""CPU step: the keyphrase recognition probe + watchdog analysis (runs on the .npz from
extract_keyphrase.py — no GPU).

Implements the test design we settled on, per read-position, per layer:

  TRAIN  a recognition probe on the ASK pass: present (recognised) vs absent. diff-of-means
         leads, logreg as upper bound, pair-disjoint CV (GroupKFold on the matched-pair stem,
         so a pair's two halves never split across folds — the inflation bug we fixed).

  Then FREEZE the ask-trained direction and score other passes (cross-pass: a probe that never
  saw an action can't be reading "about to act"):
   - TRANSFER  : present-action vs absent-action -> does recognition survive into the action pass?
   - MEMBERSHIP: ask-present vs ask-swap (same document, name OFF the watchlist) -> the sharp
                 control, kept WITHIN the ask framing: both have the name in the text, so the
                 separation = reading membership recognition, not the name's mere presence /
                 system-user co-occurrence.
   - WATCHDOG  : the gap pile (present, recognised under load per loaded-ask, but action emitted
                 NO FLAG) vs absent-action darks, both in the ACTION framing -> does the probe
                 fire on omitted-but-recognised items?

NB framing is held constant within each test (mixing ask- and action-framed activations would
conflate the framing shift with membership). Headline per position = the best layer by in-pass
recognition AUROC. The gap pile is small (~8) so the watchdog is reported with its n; recognition,
membership and transfer are well-powered (72 each).

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

        # present items with a clear ask answer that also appear in the action pass.
        pres_ids = [i for i in ids_keep if i.endswith("a") and i in a_row]
        # the watchdog target (gap): present, recognised under load (loaded-ask YES), but the
        # action pass emitted no FLAG.
        gap_ids = [i for i in pres_ids if i in l_row
                   and lda["beh"][l_row[i]] == "YES" and act["beh"][a_row[i]] == "NOFLAG"]
        # action-framed darks for the watchdog: absent items (no hit at all).
        absent_ids = [i for i in ids_keep if i.endswith("b") and i in a_row]
        # ask-framed swap darks for the membership control: present item's stem present in swap.
        swap_ids = [i for i in pres_ids if i[:-1] in s_row]
        keep_row = {ask["ids"][kk]: j for j, kk in enumerate(keep)}  # ask id -> row in Xask
        present_jrows = [keep_row[i] for i in pres_ids]              # ask-framed present (within Xask)

        cv = make_cv_splitter("group", np.array(g), args.seed)  # pair-disjoint folds

        def auroc(pos_scores, neg_scores):
            if not len(pos_scores) or not len(neg_scores):
                return float("nan")
            return roc_auc_score([1] * len(pos_scores) + [0] * len(neg_scores),
                                 np.concatenate([pos_scores, neg_scores]))

        rows = []
        for li in range(n_layers):
            Xask = ask["acts"][keep][:, li, :]
            inpass_dm = pooled_oof_auroc(Xask, y, np.array(g), cv, diffmeans_scores)
            inpass_lr = pooled_oof_auroc(Xask, y, np.array(g), cv, logreg_scores)

            def sc(rows_idx, src):  # ask-trained diff-of-means direction, scoring src's rows
                return cross_pass_score(Xask, y, src["acts"][rows_idx][:, li, :], "diffmeans")

            # TRANSFER (action framing): present vs absent
            act_all = [a_row[i] for i in ids_keep if i in a_row]
            y_act = np.array([act["labels"][r] for r in act_all])
            transfer = roc_auc_score(y_act, sc(act_all, act)) if len(set(y_act)) == 2 else float("nan")

            # MEMBERSHIP (ASK framing): ask-present vs ask-swap — same document, differ only in
            # whether the name is on the watchlist. (present is in-sample for the diff-of-means
            # direction, which does not overfit; swap is out-of-sample.)
            s_pres_ask = cross_pass_score(Xask, y, Xask[present_jrows], "diffmeans")
            s_swap = sc([s_row[i[:-1]] for i in swap_ids], swp) if swap_ids else np.array([])
            membership = auroc(s_pres_ask, s_swap)

            # WATCHDOG (ACTION framing): gap (recognised, not flagged) vs absent-action darks
            s_gap = sc([a_row[i] for i in gap_ids], act) if gap_ids else np.array([])
            s_absent = sc([a_row[i] for i in absent_ids], act) if absent_ids else np.array([])
            watchdog = auroc(s_gap, s_absent)

            rows.append(dict(layer=li, inpass_dm=inpass_dm, inpass_lr=inpass_lr, transfer=transfer,
                             membership=membership, watchdog=watchdog,
                             gap_mean=float(np.mean(s_gap)) if len(s_gap) else float("nan"),
                             absent_mean=float(np.mean(s_absent)) if len(s_absent) else float("nan"),
                             swap_mean=float(np.mean(s_swap)) if len(s_swap) else float("nan")))

        best = max(rows, key=lambda r: r["inpass_dm"])
        report[pos] = dict(n_train=len(keep), n_present=len(pres_ids), n_gap=len(gap_ids),
                           n_absent=len(absent_ids), n_swap=len(swap_ids),
                           best_layer=best["layer"], best=best, per_layer=rows)
        print(f"\n===== position: {pos}  (train {len(keep)} | present {len(pres_ids)} | "
              f"gap {len(gap_ids)} | absent {len(absent_ids)} | swap {len(swap_ids)}) =====")
        print("layer | recog dm/lr (in-pass) | transfer | membership(ask) | watchdog gap-vs-absent")
        for r in rows:
            print(f"  {r['layer']:2d}  |   {r['inpass_dm']:.3f} / {r['inpass_lr']:.3f}     |  "
                  f"{r['transfer']:.3f}  |    {r['membership']:.3f}      |  {r['watchdog']:.3f}")
        print(f"  >> best layer {best['layer']}: recog {best['inpass_dm']:.3f} | transfer {best['transfer']:.3f} "
              f"| membership {best['membership']:.3f} | watchdog {best['watchdog']:.3f} "
              f"(gap n={len(gap_ids)}, absent n={len(absent_ids)}, swap n={len(swap_ids)})")

    Path(args.out).write_text(json.dumps(report, indent=2))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
