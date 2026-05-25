"""Scenario loading: convert structured pilot scenarios into Inspect Samples.

The pilot dataset (data/scenarios_pilot.json) is a list of paired scenarios.
Each scenario has a ground-truth label ('escalate' or 'no_escalate') and
metadata about its trigger type and pair-id.

We expose load_scenarios() which the Inspect task calls to build its dataset.
"""

import json
from pathlib import Path

from inspect_ai.dataset import Sample


SCENARIOS_PATH = Path(__file__).parent.parent / "data" / "scenarios_pilot.json"


def load_scenarios() -> list[Sample]:
    """Load pilot scenarios and convert to Inspect Samples.

    Each Sample carries:
    - input: the user message (the agent's user-turn input)
    - target: the ground-truth label ('escalate' or 'no_escalate')
    - id: scenario id (e.g. '1A')
    - metadata: pair_id (links should/should-NOT pairs), trigger_type
      (analytical category that triggers escalation, or null for negatives),
      and free-form notes used for debugging / analysis.
    """
    with SCENARIOS_PATH.open() as f:
        scenarios = json.load(f)

    return [
        Sample(
            id=s["id"],
            input=s["user_message"],
            target=s["label"],
            metadata={
                "pair_id": s["pair_id"],
                "trigger_type": s.get("trigger_type"),
                "notes": s.get("notes", ""),
            },
        )
        for s in scenarios
    ]
