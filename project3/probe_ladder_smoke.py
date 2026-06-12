"""Fabricated-data smoke for probe_ladder.py — no GPU, no real activations. Plants a known
structure (a compound direction; a hit-vs-near signal present in the rule-PRESENT read arm but
NOT the rule-ABSENT arm) and checks probe_ladder.analyze recovers it: PRESENT hit-near high,
ABSENT hit-near ~chance, components readable. Verifies the whole path (consistency + correctness
filter, paraphrase rotation, cross-pass pair-OOF, component controls, verdict). Usage:
  python probe_ladder_smoke.py
"""
import json
import tempfile
from pathlib import Path

import numpy as np

import probe_ladder

RNG = np.random.RandomState(0)
L, D = 6, 32                         # tiny: 5 transformer layers + embedding, 32 dims
SIGLAYER = 3
CELLS = (["hit"] * 24 + ["near"] * 24 + ["form"] * 16 + ["none"] * 16)
COND = "refund_over_500"


def stem(cell, i):
    return f"{COND}_pair_{i:02d}" if cell in ("hit", "near") else f"{COND}_{cell}_{i:02d}"


def ids_groups():
    idx = {"hit": 0, "near": 0, "form": 0, "none": 0}
    ids, groups = [], []
    for c in CELLS:
        idx[c] += 1
        ids.append(f"{COND}_{c}_{idx[c]:02d}"); groups.append(stem(c, idx[c]))
    return ids, groups


def acts_with(ab_for):
    """[N,L+1,D] noise; plant the A-component on dim0 and the B-component on dim1 at SIGLAYER,
    where ab_for(cell) -> (a_value, b_value). Separate dims so component controls are honest."""
    A = RNG.randn(len(CELLS), L + 1, D).astype(np.float32) * 0.4
    for n, c in enumerate(CELLS):
        a, bv = ab_for(c)
        A[n, SIGLAYER, 0] += 2.0 * a
        A[n, SIGLAYER, 1] += 2.0 * bv
    return A


def save(prefix, position, acts, beh, arm=""):
    ids, groups = ids_groups()
    labels = np.array([1 if c == "hit" else 0 for c in CELLS], np.int8)
    np.savez(f"{prefix}__{position}.npz", activations=acts,
             ids=np.array(ids), labels=labels, groups=np.array(groups),
             behaviour=np.array(beh), cell=np.array(CELLS),
             arm=np.array([arm] * len(CELLS)), doccond=np.array([COND] * len(CELLS)),
             candidate=np.array([COND] * len(CELLS)), qtype=np.array([""] * len(CELLS)),
             seq_len=np.array([60] * len(CELLS)), message_token=np.array([10] * len(CELLS)),
             meta=json.dumps({"position": position}))


def main():
    d = Path(tempfile.mkdtemp())
    pre = f"{d}/ladder_{COND}"
    # true cell structure: A present on hit+near, B present on hit+form.
    a_of = lambda c: 1.0 if c in ("hit", "near") else 0.0
    b_of = lambda c: 1.0 if c in ("hit", "form") else 0.0
    comp_beh = ["YES" if c == "hit" else "NO" for c in CELLS]
    A_beh = ["YES" if c in ("hit", "near") else "NO" for c in CELLS]
    B_beh = ["YES" if c in ("hit", "form") else "NO" for c in CELLS]
    # ask/component passes carry the full (A,B) structure (the question elicits both).
    full_ab = lambda c: (a_of(c), b_of(c))
    # PRESENT read arm: rule lets B be computed -> full (A,B). ABSENT: B not computed -> B=0
    # everywhere, so hit==near (chance) and compB collapses, while A still reads.
    absent_ab = lambda c: (a_of(c), 0.0)
    flag_present = ["FLAG" if c == "hit" else "NOFLAG" for c in CELLS]
    flag_absent = ["NOFLAG"] * len(CELLS)

    for position in probe_ladder.DEFAULT_POSITIONS:
        for k in (1, 2, 3):
            save(f"{pre}_ask_compound_p{k}", position, acts_with(full_ab), comp_beh)
        save(f"{pre}_ask_compA", position, acts_with(full_ab), A_beh)
        save(f"{pre}_ask_compB", position, acts_with(full_ab), B_beh)
        save(f"{pre}_read_present", position, acts_with(full_ab), flag_present, arm="present")
        save(f"{pre}_read_absent", position, acts_with(absent_ab), flag_absent, arm="absent")

    b = probe_ladder.analyze(COND, str(d), "message_mean", seed=0)
    bb = b["best"]
    print(f"kept={b['n_kept']} hit={b['n_hit']} near={b['n_near']} "
          f"(dropped {b['n_drop_consistency']}+{b['n_drop_correctness']})")
    print(f"best L{b['best_layer']}: PRESENT hit-near={bb['present_hit_near']:.3f} "
          f"ABSENT={bb['absent_hit_near']:.3f} delta={bb['delta']:+.3f}")
    print(f"compA p/a={b['compA']['present']:.2f}/{b['compA']['absent']:.2f} "
          f"compB p/a={b['compB']['present']:.2f}/{b['compB']['absent']:.2f}")
    print(f"FLAG present={b['flag_present']} absent={b['flag_absent']}")
    print(f"verdict: {probe_ladder.verdict(COND, b)}")

    checks = {
        "kept all 80": b["n_kept"] == 80,
        "PRESENT hit-near high (>0.8)": bb["present_hit_near"] > 0.8,
        "ABSENT hit-near ~chance (<0.7)": bb["absent_hit_near"] < 0.7,
        "delta positive": bb["delta"] > 0.15,
        "compA reads both arms": min(b["compA"].values()) > 0.8,
        "best layer is the planted one": b["best_layer"] == SIGLAYER,
        "verdict = RULE-RESTORED": probe_ladder.verdict(COND, b).startswith("RULE-RESTORED"),
    }
    print("\n" + "\n".join(f"  [{'PASS' if ok else 'FAIL'}] {n}" for n, ok in checks.items()))
    raise SystemExit(0 if all(checks.values()) else 1)


if __name__ == "__main__":
    main()
