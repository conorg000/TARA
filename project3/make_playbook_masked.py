"""Move 3 — build the MASKED panel passes (lexical-ablation control) from
playbook_content_masked.json, reusing make_playbook_keeper's machinery. Prefix 'pbmask'.

Emits inputs/pbmask_ask_<cond>_p{1,2,3}.json + inputs/pbmask_action.json + pbmask_flag_vocab.json,
identical in structure to the playbook_* passes but carrying the masked hit/near messages
(form/none unchanged). Used to test whether recognition survives when the trigger lexicon
is gone (model behaviour on OpenRouter first; then GPU re-extract + re-probe).

Usage: ./.venv/bin/python make_playbook_masked.py
"""

from __future__ import annotations

import json
from pathlib import Path

from make_playbook_keeper import (survivors, build_system, load_docs,
                                   ASK_USER_TMPL, ACTION_USER_TMPL)


def main() -> None:
    here = Path(__file__).parent
    spec = json.loads((here / "playbook_conditions.json").read_text())["conditions"]
    content = json.loads((here / "playbook_content_masked.json").read_text())
    conds = survivors()
    system = build_system(conds, spec)
    docs = load_docs(conds, content)

    for askcond in conds:
        for k, question in enumerate(spec[askcond]["questions"], start=1):
            records = []
            for d in docs:
                expect_yes = (d["cell"] == "hit" and d["doccond"] == askcond)
                records.append({
                    "id": d["id"], "label": 1 if expect_yes else 0,
                    "label_name": "escalate" if expect_yes else "proceed",
                    "group": d["cell"], "system": system,
                    "user": ASK_USER_TMPL.format(question=question, message=d["message"]),
                    "meta": {"doccond": d["doccond"], "cell": d["cell"], "askcond": askcond,
                             "paraphrase": k, "framing": "playbook_ask", "archetype": d["archetype"],
                             "message": d["message"], "pair_stem": d["pair_stem"]},
                })
            out = here / f"inputs/pbmask_ask_{askcond}_p{k}.json"
            out.write_text(json.dumps(records, indent=2))
            print(f"Wrote {out.name} ({len(records)} docs)")

    records = []
    for d in docs:
        expect = {c: (d["cell"] == "hit" and d["doccond"] == c) for c in conds}
        any_flag = any(expect.values())
        records.append({
            "id": d["id"], "label": 1 if any_flag else 0,
            "label_name": "escalate" if any_flag else "proceed",
            "group": d["cell"], "system": system,
            "user": ACTION_USER_TMPL.format(message=d["message"]),
            "meta": {"doccond": d["doccond"], "cell": d["cell"], "archetype": d["archetype"],
                     "expect_flags": expect, "framing": "playbook_action",
                     "message": d["message"], "pair_stem": d["pair_stem"]},
        })
    (here / "inputs/pbmask_action.json").write_text(json.dumps(records, indent=2))
    (here / "pbmask_flag_vocab.json").write_text(
        json.dumps({c: spec[c]["flag_name"] for c in conds}, indent=2))
    print(f"Wrote pbmask_action.json ({len(records)} docs) + pbmask_flag_vocab.json")


if __name__ == "__main__":
    main()
