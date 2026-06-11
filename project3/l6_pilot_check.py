"""Experiment 1b pilot gate (A2, pre-registered): is greedy compliance frequent enough?

Reads the pilot extraction npz (first 40 pairs of the L6 action pass) and counts
present-doc compliance = label==1 AND behaviour NOFLAG. Gate: >= 6/40 (15%).
Below that, the deterministic compliance rate is too far under the coarse 35% and
the full 240-pair spend is re-costed before continuing (the standing lesson: the
OpenRouter coarse pass over-counts no-flag events).

Exit code 0 = proceed, 1 = stop — so extract_l6.sh can gate the full run on it.

Usage: python l6_pilot_check.py acts/l6pilot_action__final.npz
"""

import math
import sys

import numpy as np

path = sys.argv[1] if len(sys.argv) > 1 else "acts/l6pilot_action__final.npz"
z = np.load(path, allow_pickle=False)
labels, beh, ids = z["labels"], z["behaviour"], z["ids"]

present = labels == 1
n_pres = int(present.sum())
comply = present & (beh == "NOFLAG")
defy = present & (beh == "FLAG")
overflag = (labels == 0) & (beh == "FLAG")
gate_n = max(1, math.ceil(0.15 * n_pres))

print(f"pilot: {len(labels)} items, {n_pres} present")
print(f"present compliance (NOFLAG): {int(comply.sum())}/{n_pres}   "
      f"defiance (FLAG): {int(defy.sum())}/{n_pres}   "
      f"absent over-flag: {int(overflag.sum())}/{int((labels == 0).sum())}")
print(f"compliance ids: {sorted(ids[comply].tolist())}")

ok = int(comply.sum()) >= gate_n
print(f"\nA2 pilot gate (compliance >= {gate_n}/{n_pres}): {'PASS — proceed to full extraction' if ok else 'FAIL — stop; re-cost before the full run'}")
sys.exit(0 if ok else 1)
