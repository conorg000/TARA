"""Move 3 / Step 4 — keeper construction-validation reconciliation (OpenRouter coarse).

For each surviving condition's loaded multi-rule ASK pass (3 paraphrases), reconcile the
model's YES/NO by CELL and by DOCCOND. The Step-4 bar (PLAYBOOK): the keeper must
reproduce the pre-test pattern at scale — own-hit YES-rate >= 75%, own-near false-fire
<= ~15% on the matched pairs. Also previews specificity behaviourally (other conditions'
hits should read NO under this condition's question) and reports K1 consistency (the
fraction of own hit+near docs unanimous across the 3 paraphrases) — the labels the GPU
probe will keep.

Usage: ./.venv/bin/python observe_playbook_validate.py
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

# newest log per dataset wins
logs: dict[str, str] = {}
for p in sorted(glob.glob("logs/*.eval")):
    try:
        dp = (read_eval_log(p, header_only=True).eval.task_args or {}).get("dataset_path", "")
    except Exception:
        continue
    for cond in CONDS:
        for k in range(1, K + 1):
            if dp.endswith(f"playbook_ask_{cond}_p{k}.json"):
                logs[f"{cond}/p{k}"] = p


def doccond_of(item_id: str) -> str:
    # ids: <cond>_<cell>_NN  with cond possibly containing underscores; cell in hit/near/form/none
    parts = item_id.rsplit("_", 2)
    return parts[0]


def cell_of(item_id: str) -> str:
    return item_id.rsplit("_", 2)[1]


summary = {}
for askcond in CONDS:
    missing = [k for k in range(1, K + 1) if f"{askcond}/p{k}" not in logs]
    if missing:
        print(f"\n=== {askcond}: SKIPPED (missing paraphrase(s) {missing}) ===")
        continue

    # answers[id] = [YES/NO/UNCLEAR per paraphrase]
    answers: dict[str, list[str]] = defaultdict(list)
    for k in range(1, K + 1):
        for s in read_eval_log(logs[f"{askcond}/p{k}"]).samples:
            answers[str(s.id)].append(classify(s.output.completion or "", "YES", "NO"))

    def maj_yes(ids):
        return sum(Counter(answers[i])["YES"] * 2 > K for i in ids)

    def unanim(ids):
        return sum(len(set(answers[i])) == 1 and answers[i][0] != "UNCLEAR" for i in ids)

    own_hit = [i for i in answers if cell_of(i) == "hit" and doccond_of(i) == askcond]
    own_near = [i for i in answers if cell_of(i) == "near" and doccond_of(i) == askcond]
    other_hit = [i for i in answers if cell_of(i) == "hit" and doccond_of(i) != askcond]
    form = [i for i in answers if cell_of(i) == "form"]
    none = [i for i in answers if cell_of(i) == "none"]

    hit_yes = maj_yes(own_hit) / max(len(own_hit), 1)
    near_fire = maj_yes(own_near) / max(len(own_near), 1)
    other_fire = maj_yes(other_hit) / max(len(other_hit), 1)
    form_fire = maj_yes(form) / max(len(form), 1)
    none_fire = maj_yes(none) / max(len(none), 1)
    core = own_hit + own_near
    consistency = unanim(core) / max(len(core), 1)

    hit_pass = hit_yes >= 0.75
    near_pass = near_fire <= 0.15
    gate = hit_pass and near_pass

    print(f"\n=== {askcond} (loaded multi-rule ask) ===")
    print(f"  own-hit  YES {maj_yes(own_hit):>2}/{len(own_hit):<2} = {hit_yes:.0%}  {'PASS' if hit_pass else 'FAIL'} (>=75%)")
    print(f"  own-near YES {maj_yes(own_near):>2}/{len(own_near):<2} = {near_fire:.0%}  {'PASS' if near_pass else 'FAIL'} (<=15%)")
    print(f"  other-hit YES {maj_yes(other_hit):>2}/{len(other_hit):<2} = {other_fire:.0%}  (specificity preview — want low)")
    print(f"  form YES {maj_yes(form):>2}/{len(form):<2} = {form_fire:.0%} | none YES {maj_yes(none):>2}/{len(none):<2} = {none_fire:.0%}")
    print(f"  K1 consistency (own hit+near unanimous /3) = {consistency:.0%}")
    print(f"  -> STEP 4 construction: {'PASS' if gate else 'CONCERN'}")
    summary[askcond] = dict(hit_yes=round(hit_yes, 3), near_fire=round(near_fire, 3),
                            other_hit_fire=round(other_fire, 3), form_fire=round(form_fire, 3),
                            none_fire=round(none_fire, 3), consistency=round(consistency, 3),
                            step4_pass=gate)

if summary:
    Path("playbook_validate_summary.json").write_text(json.dumps(summary, indent=2))
    print("\nWrote playbook_validate_summary.json")
