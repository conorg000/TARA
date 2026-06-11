"""Fabricate tiny exp2-schema .npz with planted signal, so probe_exp2.py can be verified
end-to-end WITHOUT the GPU / real activations. The point (per the 'scripts must be ready
here before the box pulls them' rule): prove the analysis runs and computes K1–K4 sensibly.

Planted truth: a doc "satisfies the active condition" iff (its doccond == the pass's rule
AND cell == hit). We add a signal vector to such docs' activations; everything else is
noise. So the EXPECTED smoke result is: recognition high, K2 hit-near high / near-none ~0.5,
K3 swap high (a legal hit lights up under the legal action pass but not the medical one),
junk low. A couple of ask answers are flipped in one paraphrase to exercise the K1
consistency-drop path.

Usage:
  ./.venv/bin/python probe_exp2_smoke.py            # writes /tmp/exp2_smoke/*.npz
  ./.venv/bin/python probe_exp2.py --acts-dir /tmp/exp2_smoke --out /tmp/probe_exp2_smoke.json
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

OUT = Path("/tmp/exp2_smoke")
POSITIONS = ["message_mean", "final"]
NL, D = 4, 8           # layers+1, hidden dim
RNG = np.random.RandomState(0)


def build_docs():
    docs = []
    for cond in ("legal", "medical"):
        for i in range(1, 9):                      # 8 matched pairs per condition
            stem = f"{cond}_{i:02d}"
            docs.append(dict(id=f"{cond}_hit_{i:02d}", doccond=cond, cell="hit", stem=stem))
            docs.append(dict(id=f"{cond}_near_{i:02d}", doccond=cond, cell="near", stem=stem))
    for i in range(1, 7):
        docs.append(dict(id=f"neutral_form_{i:02d}", doccond="neutral", cell="form", stem=f"neutral_form_{i:02d}"))
    for i in range(1, 7):
        docs.append(dict(id=f"neutral_none_{i:02d}", doccond="neutral", cell="none", stem=f"neutral_none_{i:02d}"))
    return docs


def satisfies(doc, rule):
    return doc["doccond"] == rule and doc["cell"] == "hit"


def make_acts(docs, rule):
    """Activations [N, NL, D]: signal added (all layers but layer 0) iff the doc satisfies
    the active rule; layer 0 stays pure noise (the layer-0~0.5 sanity check)."""
    sig = np.zeros(D); sig[:3] = 4.0
    A = RNG.normal(scale=1.0, size=(len(docs), NL, D))
    for n, doc in enumerate(docs):
        if satisfies(doc, rule):
            A[n, 1:, :] += sig
    return A


def save(prefix, docs, rule, behaviour):
    common = dict(
        ids=np.array([d["id"] for d in docs]),
        labels=np.array([1 if satisfies(d, rule) else 0 for d in docs], dtype=np.int8),
        groups=np.array([d["stem"] for d in docs]),
        behaviour=np.array(behaviour),
        generated_text=np.array([""] * len(docs)),
        doccond=np.array([d["doccond"] for d in docs]),
        cell=np.array([d["cell"] for d in docs]),
        message_token=np.array([10] * len(docs)),
        seq_len=np.array(RNG.randint(40, 120, size=len(docs))),
    )
    A = make_acts(docs, rule)
    for pos in POSITIONS:
        np.savez(f"{prefix}__{pos}.npz", activations=A.astype(np.float16),
                 meta=json.dumps({"position": pos, "framing": "smoke"}), **common)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    docs = build_docs()
    for cond in ("legal", "medical"):
        for k in (1, 2, 3):
            beh = ["YES" if satisfies(d, cond) else "NO" for d in docs]
            if k == 2:                              # flip 2 answers in p2 -> K1 drops them
                beh[0] = "NO"; beh[1] = "YES"
            save(OUT / f"exp2_ask_{cond}_p{k}", docs, cond, beh)
        beh_act = ["FLAG" if satisfies(d, cond) else "NOFLAG" for d in docs]
        save(OUT / f"exp2_action_{cond}", docs, cond, beh_act)
    print(f"wrote fabricated exp2 activations to {OUT} ({len(docs)} docs, {len(POSITIONS)} positions)")
    print("now run: ./.venv/bin/python probe_exp2.py --acts-dir /tmp/exp2_smoke --out /tmp/probe_exp2_smoke.json")


if __name__ == "__main__":
    main()
