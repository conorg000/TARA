"""Does the v4 cross-pass result survive a DOCUMENT-DISJOINT split?

probe_keyphrase.py trains the cross-pass direction (transfer/membership/watchdog) on the FULL
ask set, then scores action/swap items of the SAME pairs — framing held out, documents not.
This recomputes all three the strict way: pair-out-of-fold, so a pair's action/swap/present is
ONLY ever scored by a direction trained on OTHER pairs' ask data. If the numbers hold, the
document overlap wasn't inflating them.

Per position, at the probe's headline (in-pass-recognition-best) layer; diff-of-means (lead)
and logreg (upper bound). In-sample (probe's current method) shown beside pair-OOF.
"""
import numpy as np
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score

from cross_pass_probe import cross_pass_score

POS_LAYER = {"final": 48, "name_last": 22, "doc_last": 51, "doc_mean": 48}
NFOLD = 6


def load(prefix, pos):
    d = np.load(f"acts/{prefix}__{pos}.npz", allow_pickle=True)
    return dict(acts=d["activations"], ids=[str(x) for x in d["ids"]],
                beh=[str(x) for x in d["behaviour"]])


def auroc(p, n):
    if not len(p) or not len(n):
        return float("nan")
    return roc_auc_score([1] * len(p) + [0] * len(n), np.concatenate([p, n]))


def stem(i):
    return i[:-1]


for pos, L in POS_LAYER.items():
    ask, act, lda, swp = (load(f"v4_{x}", pos) for x in ("ask", "action", "loadedask", "swap"))
    # ask training rows with a clear answer
    a_keep = [k for k, b in enumerate(ask["beh"]) if b in ("YES", "NO")]
    Xask = ask["acts"][:, L, :]
    yask = np.array([1 if ask["beh"][k] == "YES" else 0 for k in a_keep])
    ask_stem = [stem(ask["ids"][k]) for k in a_keep]
    Xask_keep = Xask[a_keep]

    a_row = {i: k for k, i in enumerate(act["ids"])}
    l_row = {i: k for k, i in enumerate(lda["ids"])}
    s_row = {stem(i): k for k, i in enumerate(swp["ids"])}

    ask_id = [ask["ids"][k] for k in a_keep]
    pres_ids = [i for i in ask_id if i.endswith("a") and i in a_row]
    gap_ids = [i for i in pres_ids if i in l_row and lda["beh"][l_row[i]] == "YES"
               and act["beh"][a_row[i]] == "NOFLAG"]
    absent_ids = [i for i in ask_id if i.endswith("b") and i in a_row]
    swap_ids = [i for i in pres_ids if stem(i) in s_row]

    Xact = act["acts"][:, L, :]
    Xswp = swp["acts"][:, L, :]

    # ---------- in-sample (probe's current method): direction on ALL ask ----------
    def insample(kind):
        d_all = lambda rows, src: cross_pass_score(Xask_keep, yask, src[rows], kind)
        # transfer: present vs absent (action)
        tp = d_all([a_row[i] for i in pres_ids], Xact)
        tn = d_all([a_row[i] for i in absent_ids], Xact)
        # membership: present(ask) vs swap
        mp = cross_pass_score(Xask_keep, yask, Xask_keep[[ask_id.index(i) for i in pres_ids]], kind)
        mn = d_all([s_row[stem(i)] for i in swap_ids], Xswp)
        # watchdog: gap vs absent (action)
        wp = d_all([a_row[i] for i in gap_ids], Xact)
        wn = tn
        return auroc(tp, tn), auroc(mp, mn), auroc(wp, wn)

    # ---------- pair-OOF: direction trained only on OTHER pairs' ask ----------
    def pair_oof(kind):
        gkf = GroupKFold(n_splits=NFOLD)
        # collect OOF scores keyed by id (action), by id (swap/present in ask)
        sc_act, sc_pres_ask, sc_swap = {}, {}, {}
        idx = np.arange(len(a_keep))
        for tr, te in gkf.split(idx, yask, ask_stem):
            tr_stems = {ask_stem[k] for k in tr}
            Xtr, ytr = Xask_keep[tr], yask[tr]
            # action items whose stem is in the TEST fold
            act_te = [i for i in (pres_ids + absent_ids) if stem(i) in {ask_stem[k] for k in te}]
            if act_te:
                s = cross_pass_score(Xtr, ytr, Xact[[a_row[i] for i in act_te]], kind)
                sc_act.update(dict(zip(act_te, s)))
            pres_te = [i for i in pres_ids if stem(i) in {ask_stem[k] for k in te}]
            if pres_te:
                s = cross_pass_score(Xtr, ytr, Xask_keep[[ask_id.index(i) for i in pres_te]], kind)
                sc_pres_ask.update(dict(zip(pres_te, s)))
            swap_te = [i for i in swap_ids if stem(i) in {ask_stem[k] for k in te}]
            if swap_te:
                s = cross_pass_score(Xtr, ytr, Xswp[[s_row[stem(i)] for i in swap_te]], kind)
                sc_swap.update(dict(zip(swap_te, s)))
        tp = np.array([sc_act[i] for i in pres_ids]); tn = np.array([sc_act[i] for i in absent_ids])
        mp = np.array([sc_pres_ask[i] for i in pres_ids]); mn = np.array([sc_swap[i] for i in swap_ids])
        wp = np.array([sc_act[i] for i in gap_ids])
        return auroc(tp, tn), auroc(mp, mn), auroc(wp, tn)

    print(f"\n=== {pos}  L{L}   (gap n={len(gap_ids)}) ===")
    for kind in ("diffmeans", "logreg"):
        it, im, iw = insample(kind)
        ot, om, ow = pair_oof(kind)
        print(f"  {kind:9s}  transfer {it:.3f}->{ot:.3f}   membership {im:.3f}->{om:.3f}   "
              f"watchdog {iw:.3f}->{ow:.3f}   (in-sample -> pair-OOF)")
