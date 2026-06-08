"""Follow-up to probe_keyphrase: the decisive 'noticed-but-not-acted' control.

The probe's watchdog = gap-vs-absent confounds two things: gap items HAVE a watchlisted
name, absent items don't, so the recognition direction separates them trivially. The sharp
question is whether the gap pile (present, recognised on demand per loaded-ask, but the action
pass emitted no FLAG) carries the SAME recognition signal as the FLAGGED present pile.

  gap-vs-flagged ~ 0.5  => recognition equally present whether or not it flagged
                          -> the omission is downstream of recognition ("looked, didn't act")
  gap-vs-flagged < 0.5  => gap items recognised LESS than flagged -> "didn't fully look"

We train the recognition direction on the ASK pass (diff-of-means, the honest probe), freeze it,
and score the ACTION pass groups. Same machinery as the probe's transfer/watchdog, reported with
group means and a label-shuffle sanity check. Best-by-recognition layer per position (no
watchdog cherry-picking).
"""
import numpy as np
from sklearn.metrics import roc_auc_score

POS_LAYER = {"final": 48, "doc_mean": 48, "doc_last": 51, "name_last": 22}


def load(prefix, pos):
    d = np.load(f"acts/{prefix}__{pos}.npz", allow_pickle=True)
    return dict(acts=d["activations"], ids=[str(x) for x in d["ids"]],
                beh=[str(x) for x in d["behaviour"]])


def dm_dir(X, y):
    return X[y == 1].mean(0) - X[y == 0].mean(0)


def auroc(pos, neg):
    return roc_auc_score([1] * len(pos) + [0] * len(neg), np.concatenate([pos, neg]))


rng = np.random.default_rng(0)
for pos, L in POS_LAYER.items():
    ask, act, lda = load("v4_ask", pos), load("v4_action", pos), load("v4_loadedask", pos)
    yb = np.array([1 if b == "YES" else (0 if b == "NO" else -1) for b in ask["beh"]])
    keep = yb >= 0
    Xask = ask["acts"][:, L, :]
    w = dm_dir(Xask[keep], yb[keep])

    a = {i: k for k, i in enumerate(act["ids"])}
    l = {i: k for k, i in enumerate(lda["ids"])}
    sc = act["acts"][:, L, :] @ w

    pres = [i for i in act["ids"] if i.endswith("a")]
    flagged = [i for i in pres if act["beh"][a[i]] == "FLAG"]
    gap = [i for i in pres if act["beh"][a[i]] == "NOFLAG" and i in l and lda["beh"][l[i]] == "YES"]
    miss = [i for i in pres if act["beh"][a[i]] == "NOFLAG" and i in l and lda["beh"][l[i]] == "NO"]
    absent = [i for i in act["ids"] if i.endswith("b")]
    s = lambda ids: np.array([sc[a[i]] for i in ids])
    sg, sf, sa = s(gap), s(flagged), s(absent)

    # label-shuffle sanity: shuffle ask labels, recompute direction, re-score watchdog -> ~0.5
    shuf = []
    for _ in range(50):
        yp = rng.permutation(yb[keep])
        ws = dm_dir(Xask[keep], yp)
        scs = act["acts"][:, L, :] @ ws
        shuf.append(auroc(np.array([scs[a[i]] for i in gap]),
                          np.array([scs[a[i]] for i in absent])))

    print(f"\n=== {pos}  layer {L}   (gap n={len(gap)}, flagged n={len(flagged)}, "
          f"absent n={len(absent)}, recog-miss n={len(miss)}) ===")
    print(f"  watchdog  gap-vs-absent   : {auroc(sg, sa):.3f}   (probe reproduced)")
    print(f"  CONTROL   gap-vs-flagged  : {auroc(sg, sf):.3f}   (~0.5 => gap recognised like flagged)")
    print(f"  means     gap / flag / abs: {sg.mean():+.2f} / {sf.mean():+.2f} / {sa.mean():+.2f}")
    print(f"  shuffle   gap-vs-absent   : {np.mean(shuf):.3f} ± {np.std(shuf):.3f}  (label-permuted null)")
    if pos == "final":
        print(f"  gap ids: {sorted(gap)}")
