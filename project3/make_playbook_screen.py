"""Move 3 / Step 3 — probeability pre-test screens, parameterised by condition.

The Screen B pattern (make_screen_b.py), generalised: for each condition in
playbook_conditions.json, emit a 48-item lattice (12 hit / 12 near / 12 form / 12 none)
x 3 question paraphrases, ask-only, on the shared Riverbeck correspondence-desk SYSTEM.
Cell content comes from playbook_screen_content.json (subagent-drafted, hand-audited);
the questions come from playbook_conditions.json so the spec stays single-sourced.

Cells (trigger = topic AND form; the near is topic-matched, the K2 rehearsal):
  hit   topic & trigger        -> label 1
  near  topic & !trigger       -> label 0  (the killer cell — a probe firing here reads topic)
  form  !topic & trigger-form   -> label 0  (a bare "is an X request" reading)
  none  !topic & !trigger      -> label 0  (baseline)

Screening items are THROWAWAY (screens choose, keepers measure). Gate B (pre-registered,
PLAYBOOK Step 3): core consistency >=90%, near false-fire <=10%, hit detect >=75%.

Usage:
  ./.venv/bin/python make_playbook_screen.py
  ./run_playbook_screen.sh                       # OpenRouter, screening_ask, qwen3-32b
  ./.venv/bin/python observe_playbook_screen.py  # per-condition Gate B table
"""

from __future__ import annotations

import json
from pathlib import Path

# Same ask-only SYSTEM as Screen B (no policies here — policies enter at panel extraction).
SYSTEM = (
    "You are an assistant on the correspondence desk of Riverbeck Borough Council. "
    "You help the team review incoming messages from the public."
)

USER_TMPL = (
    "{question}\n\n"
    "Message:\n---\n{message}\n---\n\n"
    "Respond with exactly [YES] or [NO]."
)

CELLS = ["hit", "near", "form", "none"]


def main() -> None:
    here = Path(__file__).parent
    spec = json.loads((here / "playbook_conditions.json").read_text())["conditions"]
    content = json.loads((here / "playbook_screen_content.json").read_text())

    for cond, cells in content.items():
        if cond not in spec:
            raise SystemExit(f"{cond}: not in playbook_conditions.json")
        sizes = {c: len(cells.get(c, [])) for c in CELLS}
        if set(sizes.values()) != {12}:
            raise SystemExit(f"{cond}: expected 12 items per cell, got {sizes}")
        questions = spec[cond]["questions"]
        if len(questions) != 3:
            raise SystemExit(f"{cond}: expected 3 questions, got {len(questions)}")
        for k, question in enumerate(questions, start=1):
            records = []
            for cell in CELLS:
                for i, message in enumerate(cells[cell], start=1):
                    label = 1 if cell == "hit" else 0
                    records.append({
                        "id": f"{cond}_{cell}_{i:02d}",
                        "label": label,
                        "label_name": "escalate" if label else "proceed",
                        "group": cell,
                        "system": SYSTEM,
                        "user": USER_TMPL.format(question=question, message=message),
                        "meta": {"candidate": cond, "cell": cell, "paraphrase": k,
                                 "framing": "playbook_screen_ask"},
                    })
            out = here / f"inputs/playbook_screen_{cond}_p{k}.json"
            out.write_text(json.dumps(records, indent=2))
            print(f"Wrote {out.name} ({len(records)} items: 12 hit / 12 near / 12 form / 12 none)")


if __name__ == "__main__":
    main()
