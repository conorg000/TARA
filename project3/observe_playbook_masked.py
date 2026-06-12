"""Move 3 — does the model's recognition survive lexical ablation? Reads the masked-ask
OpenRouter logs (pbmask_ask_*) and reports, per condition: model maj-YES on masked own-hit
vs masked own-near, the behavioural hit-near gap, UNCLEAR rate (text-mangling check), and
K1 consistency. Compares against the unmasked validation (playbook_validate_summary.json).

If masked own-hit YES stays high and masked own-near low -> the model infers intent from
context beyond the trigger keywords (genuine semantic recognition; GPU probe worth running).
If the gap collapses (or UNCLEAR spikes) -> recognition was lexical / masking broke the text.

Usage: ./.venv/bin/python observe_playbook_masked.py
"""

import glob
import json
from collections import Counter, defaultdict
from pathlib import Path

from inspect_ai.log import read_eval_log
from markers import classify

K = 3
CONDS = [c for c in json.loads(Path("playbook_conditions.json").read_text())["conditions"]
         if json.loads(Path("playbook_screen_summary.json").read_text()).get(c, {}).get("gate_b_pass")]

logs = {}
for p in sorted(glob.glob("logs/*.eval")):
    try:
        dp = (read_eval_log(p, header_only=True).eval.task_args or {}).get("dataset_path", "")
    except Exception:
        continue
    for cond in CONDS:
        for k in range(1, K + 1):
            if dp.endswith(f"pbmask_ask_{cond}_p{k}.json"):
                logs[f"{cond}/p{k}"] = p

unmasked = json.loads(Path("playbook_validate_summary.json").read_text())
cell_of = lambda i: i.rsplit("_", 2)[1]
doccond_of = lambda i: i.rsplit("_", 2)[0]
summary = {}

for cond in CONDS:
    if any(f"{cond}/p{k}" not in logs for k in range(1, K + 1)):
        print(f"{cond}: SKIPPED (missing masked logs)"); continue
    ans = defaultdict(list)
    for k in range(1, K + 1):
        for s in read_eval_log(logs[f"{cond}/p{k}"]).samples:
            ans[str(s.id)].append(classify(s.output.completion or "", "YES", "NO"))
    maj = lambda ids: sum(Counter(ans[i])["YES"] * 2 > K for i in ids) / max(len(ids), 1)
    unclear = lambda ids: sum(a == "UNCLEAR" for i in ids for a in ans[i]) / max(K * len(ids), 1)
    own_hit = [i for i in ans if cell_of(i) == "hit" and doccond_of(i) == cond]
    own_near = [i for i in ans if cell_of(i) == "near" and doccond_of(i) == cond]
    h, n, u = maj(own_hit), maj(own_near), unclear(own_hit + own_near)
    um = unmasked.get(cond, {})
    print(f"\n=== {cond} (MASKED ask) ===")
    print(f"  own-hit YES : {h:.0%}   (unmasked {um.get('hit_yes', float('nan')):.0%})")
    print(f"  own-near YES: {n:.0%}   (unmasked {um.get('near_fire', float('nan')):.0%})")
    print(f"  hit-near gap: {h - n:+.0%}   | UNCLEAR {u:.0%} (text-mangle check)")
    verdict = ("RECOGNITION SURVIVES ablation (model infers intent beyond keywords)"
               if (h - n) >= 0.40 and u < 0.20 else
               "MANGLED (UNCLEAR high — masking broke the text, inconclusive)" if u >= 0.20 else
               "RECOGNITION WAS LEXICAL (gap collapsed without the keywords)")
    print(f"  -> {verdict}")
    summary[cond] = dict(masked_hit_yes=round(h, 3), masked_near_yes=round(n, 3),
                         gap=round(h - n, 3), unclear=round(u, 3), verdict=verdict)

if summary:
    Path("playbook_masked_behaviour.json").write_text(json.dumps(summary, indent=2))
    print("\nwrote playbook_masked_behaviour.json")
