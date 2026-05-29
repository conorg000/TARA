"""Scenario loading: convert structured pilot scenarios into Inspect Samples.

Each task in `pipeline/task.py` calls `load_scenarios(dataset_path)` with a
specific dataset file. Defaults to the pilot dataset for backward
compatibility, but new tasks should pass an explicit path so the runlog row
can note which dataset was used.
"""

import json
from pathlib import Path

from inspect_ai.dataset import Sample


PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_DATASET = PROJECT_ROOT / "data" / "scenarios_pilot.json"


def load_scenarios(dataset_path: str | Path | None = None) -> list[Sample]:
    """Load paired scenarios from a JSON file and convert to Inspect Samples.

    Args:
        dataset_path: Path to a JSON file in the same shape as
            data/scenarios_pilot.json. Relative paths resolve against the
            project root. Defaults to data/scenarios_pilot.json.

    Each Sample carries:
    - input: the user message (the agent's user-turn input)
    - target: the ground-truth label ('escalate' or 'no_escalate')
    - id: scenario id (e.g. '1A', '11A')
    - metadata: pair_id (links should/should-NOT pairs), trigger_type
      (analytical category that triggers escalation, or null for negatives),
      and free-form notes used for debugging / analysis.
    """
    path = Path(dataset_path) if dataset_path else DEFAULT_DATASET
    if not path.is_absolute():
        path = PROJECT_ROOT / path

    with path.open() as f:
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
