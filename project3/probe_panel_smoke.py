"""Fabricate tiny panel-schema .npz with planted per-condition signals, so probe_panel.py
is verified end-to-end BEFORE the box run (scripts-ready-before-GPU rule).

Planted truth (the SEPARABLE world): two ORTHOGONAL signal vectors — sig_L on dims 0:3,
sig_M on dims 3:6. legal hits carry sig_L, medical hits carry sig_M, both-docs carry
BOTH, near/form/none are noise. Layer 0 stays pure noise (the layer-0 sanity check).
Ask behaviour: YES iff (own hit or both); one paraphrase flips two answers to exercise
the K1 drop path. Action behaviour: per-rule FLAG strings (FLAG-BOTH on both docs).

EXPECTED smoke result per condition: floor HIGH, CROSSFIRE ~0.5 (pass), composition
HIGH, k2_hit_near HIGH, near-none ~0.5, transfer HIGH, crossfire_action ~0.5,
geometry cosine ~0 at signal layers. If the script reports collapse here, the analysis
is broken, not the model.

Usage:
  ./.venv/bin/python probe_panel_smoke.py
  ./.venv/bin/python probe_panel.py --acts-dir /tmp/panel_smoke --out /tmp/probe_panel_smoke.json
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

OUT = Path("/tmp/panel_smoke")
POSITIONS = ["message_last", "message_mean", "final", "pre_message_final"]
NL, D = 4, 12          # layers+1, hidden dim
RNG = np.random.RandomState(0)


def build_docs():
    docs = []
    for cond in ("legal", "medical"):
        for i in range(1, 11):                       # 10 matched pairs per condition
            stem = f"{cond}_{i:02d}"
            docs.append(dict(id=f"{cond}_hit_{i:02d}", doccond=cond, cell="hit", stem=stem))
            docs.append(dict(id=f"{cond}_near_{i:02d}", doccond=cond, cell="near", stem=stem))
    for i in range(1, 9):
        docs.append(dict(id=f"both_both_{i:02d}", doccond="both", cell="both", stem=f"both_both_{i:02d}"))
    for i in range(1, 8):
        docs.append(dict(id=f"neutral_form_{i:02d}", doccond="neutral", cell="form", stem=f"neutral_form_{i:02d}"))
    for i in range(1, 8):
        docs.append(dict(id=f"neutral_none_{i:02d}", doccond="neutral", cell="none", stem=f"neutral_none_{i:02d}"))
    return docs


def seeks(doc, cond):
    return (doc["cell"] == "hit" and doc["doccond"] == cond) or doc["cell"] == "both"


def make_acts(docs):
    """[N, NL, D]; signals on layers 1+ only — pre_message_final gets NO signal anywhere
    (it is the negative-control position and must read ~0.5)."""
    sig = {"legal": np.zeros(D), "medical": np.zeros(D)}
    sig["legal"][0:3] = 4.0
    sig["medical"][3:6] = 4.0
    A = RNG.normal(scale=1.0, size=(len(docs), NL, D))
    for n, doc in enumerate(docs):
        for cond in ("legal", "medical"):
            if seeks(doc, cond):
                A[n, 1:, :] += sig[cond]
    return A


def save(prefix, docs, behaviour, with_signal=True):
    common = dict(
        ids=np.array([d["id"] for d in docs]),
        labels=np.array([0] * len(docs), dtype=np.int8),     # probe reads beh, not labels
        groups=np.array([d["stem"] for d in docs]),
        behaviour=np.array(behaviour),
        generated_text=np.array([""] * len(docs)),
        doccond=np.array([d["doccond"] for d in docs]),
        cell=np.array([d["cell"] for d in docs]),
        message_token=np.array([10] * len(docs)),
        seq_len=np.array(RNG.randint(40, 120, size=len(docs))),
    )
    for pos in POSITIONS:
        A = make_acts(docs) if (with_signal and pos != "pre_message_final") \
            else RNG.normal(scale=1.0, size=(len(docs), NL, D))
        np.savez(f"{prefix}__{pos}.npz", activations=A.astype(np.float16),
                 meta=json.dumps({"position": pos, "framing": "smoke"}), **common)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    docs = build_docs()
    for cond in ("legal", "medical"):
        for k in (1, 2, 3):
            beh = ["YES" if seeks(d, cond) else "NO" for d in docs]
            if k == 2:                                # flip 2 answers in p2 -> K1 drops them
                beh[0] = "NO"; beh[2] = "YES"
            save(OUT / f"panel_ask_{cond}_p{k}", docs, beh)
    beh_act = []
    for d in docs:
        l, m = seeks(d, "legal"), seeks(d, "medical")
        beh_act.append("FLAG-BOTH" if (l and m) else "FLAG-LEGAL" if l
                       else "FLAG-MEDICAL" if m else "NOFLAG")
    save(OUT / "panel_action", docs, beh_act)
    print(f"wrote fabricated panel activations to {OUT} ({len(docs)} docs, {len(POSITIONS)} positions)")
    print("now run: ./.venv/bin/python probe_panel.py --acts-dir /tmp/panel_smoke "
          "--out /tmp/probe_panel_smoke.json")


if __name__ == "__main__":
    main()
