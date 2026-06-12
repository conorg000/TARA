"""Fabricate tiny playbook-schema .npz with planted per-condition signals, so
probe_playbook.py is verified end-to-end BEFORE the box probe (scripts-ready rule).

Planted SEPARABLE world: N orthogonal signal vectors (cond i on dims 3i:3i+3). Each
condition's hits carry its signal; near/form/none are noise. Layer 0 is pure noise
(the layer-0 sanity). Ask behaviour: YES iff own hit; one paraphrase flips two answers
(exercise the K1 drop). Action behaviour: '+'-joined flagged-condition set.

EXPECTED per condition: floor HIGH, k2_hit_near HIGH, k2_near_none ~0.5, SPECIFICITY
HIGH (orthogonal -> ~1.0 vs every other hit), selectivity high, shuffle ~0.5, layer-0
~0.5, transfer HIGH. Interference: mean pairwise cosine ~0 (orthogonal pure dirs). If the
script reports a topic-confound or low specificity here, the analysis is broken, not data.

Usage:
  ./.venv/bin/python probe_playbook_smoke.py
  ./.venv/bin/python probe_playbook.py --acts-dir /tmp/pb_smoke \
      --flag-vocab /tmp/pb_smoke/flag_vocab.json --out /tmp/probe_playbook_smoke.json
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

OUT = Path("/tmp/pb_smoke")
POSITIONS = ["message_last", "message_mean", "final", "pre_message_final"]
CONDS = ["data_deletion", "fraud_report", "implicit_legal_threat"]
NL, D = 4, 16
RNG = np.random.RandomState(0)


def build_docs():
    docs = []
    for ci, cond in enumerate(CONDS):
        for i in range(1, 11):
            stem = f"{cond}_{i:02d}"
            docs.append(dict(id=f"{cond}_hit_{i:02d}", doccond=cond, cell="hit", stem=stem, ci=ci))
            docs.append(dict(id=f"{cond}_near_{i:02d}", doccond=cond, cell="near", stem=stem, ci=ci))
    for i in range(1, 8):
        docs.append(dict(id=f"neutral_form_{i:02d}", doccond="neutral", cell="form",
                         stem=f"neutral_form_{i:02d}", ci=-1))
    for i in range(1, 8):
        docs.append(dict(id=f"neutral_none_{i:02d}", doccond="neutral", cell="none",
                         stem=f"neutral_none_{i:02d}", ci=-1))
    return docs


def make_acts(docs):
    A = RNG.normal(scale=1.0, size=(len(docs), NL, D))
    for n, doc in enumerate(docs):
        if doc["cell"] == "hit":
            s = np.zeros(D); s[3 * doc["ci"]: 3 * doc["ci"] + 3] = 4.0
            A[n, 1:, :] += s
    return A


def save(prefix, docs, behaviour):
    common = dict(
        ids=np.array([d["id"] for d in docs]),
        labels=np.array([0] * len(docs), dtype=np.int8),
        groups=np.array([d["stem"] for d in docs]),
        behaviour=np.array(behaviour),
        generated_text=np.array([""] * len(docs)),
        doccond=np.array([d["doccond"] for d in docs]),
        cell=np.array([d["cell"] for d in docs]),
        message_token=np.array([10] * len(docs)),
        seq_len=np.array(RNG.randint(40, 120, size=len(docs))),
    )
    for pos in POSITIONS:
        A = make_acts(docs) if pos != "pre_message_final" \
            else RNG.normal(scale=1.0, size=(len(docs), NL, D))
        np.savez(f"{prefix}__{pos}.npz", activations=A.astype(np.float16),
                 meta=json.dumps({"position": pos, "framing": "smoke"}), **common)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    docs = build_docs()
    for cond in CONDS:
        for k in (1, 2, 3):
            beh = ["YES" if (d["cell"] == "hit" and d["doccond"] == cond) else "NO" for d in docs]
            if k == 2:
                beh[0] = "NO"; beh[2] = "YES"   # flip 2 -> K1 drops them
            save(OUT / f"playbook_ask_{cond}_p{k}", docs, beh)
    beh_act = []
    for d in docs:
        beh_act.append(d["doccond"] if d["cell"] == "hit" else "NOFLAG")
    save(OUT / "playbook_action", docs, beh_act)
    (OUT / "flag_vocab.json").write_text(json.dumps({c: c.replace("_", "-") for c in CONDS}))
    print(f"wrote fabricated playbook activations to {OUT} ({len(docs)} docs, {len(POSITIONS)} positions)")
    print(f"now run: ./.venv/bin/python probe_playbook.py --acts-dir {OUT} "
          f"--flag-vocab {OUT}/flag_vocab.json --out /tmp/probe_playbook_smoke.json")


if __name__ == "__main__":
    main()
