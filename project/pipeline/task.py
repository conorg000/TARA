"""Inspect tasks: analyst-escalation experiments.

Each @task function corresponds to one row in `experiments.md`. Task names
match the experiment IDs there. Tasks share scenarios and persona structure
but differ on the cell-specific variables (action type, spec format, scorer).

Each task accepts a `dataset_path` parameter so the same experiment design
can be run against different scenario datasets. The runlog row captures
which dataset was used.

- `analyst_exit_v1`: natural-language exit persona, LLM-judge scorer.
- `analyst_exit_v2`: structured-token exit persona, regex marker scorer.
- `analyst_cont_v1`: structured-token continuation persona, regex marker scorer.

Run with:
    inspect eval pipeline/task.py@analyst_exit_v2 \\
        --model openrouter/qwen/qwen3-32b --epochs 5 \\
        -T dataset_path=data/scenarios_v2.json
"""

from inspect_ai import Task, task
from inspect_ai.model import GenerateConfig
from inspect_ai.solver import generate, system_message

from pipeline.data import load_scenarios
from pipeline.prompts import (
    CONTINUATION_MARKER,
    EXIT_MARKER,
    PERSONA_CONTINUATION_V1,
    PERSONA_EXIT_V1,
    PERSONA_EXIT_V2,
)
from pipeline.scorers import action_judge, marker_match


# Reproducibility-relevant default. Agent runs at deployment-shaped T=0.7
# (matches typical production defaults; gives us natural variance for pass^k).
AGENT_TEMPERATURE = 0.7

# Default dataset for tasks that don't override it.
DEFAULT_DATASET = "data/scenarios_pilot.json"


@task
def analyst_exit_v1(dataset_path: str = DEFAULT_DATASET) -> Task:
    """Exit_v1: natural-language exit persona + LLM-judge grading.

    Original M1 pilot configuration. Persona uses a natural-language directive
    ("escalate to a senior analyst, do not attempt"). Scorer runs the
    action_judge LLM-as-judge against the exit_action_v1 rubric (with N8
    nullifier).
    """
    return Task(
        dataset=load_scenarios(dataset_path),
        solver=[
            system_message(PERSONA_EXIT_V1),
            generate(),
        ],
        scorer=action_judge(),
        config=GenerateConfig(temperature=AGENT_TEMPERATURE),
    )


@task
def analyst_exit_v2(dataset_path: str = DEFAULT_DATASET) -> Task:
    """Exit_v2: structured-token exit persona + regex marker grading.

    Methodology-aligned mirror of cont_v1. Persona instructs the model to
    emit the literal `[ESCALATE]` token and stop. Scorer regex-matches
    against the marker at the start of the response. Cell holds spec format
    and grading methodology fixed; the only difference from cont_v1 is the
    action type (exit vs continuation).
    """
    return Task(
        dataset=load_scenarios(dataset_path),
        solver=[
            system_message(PERSONA_EXIT_V2),
            generate(),
        ],
        scorer=marker_match(marker=EXIT_MARKER),
        config=GenerateConfig(temperature=AGENT_TEMPERATURE),
    )


@task
def analyst_cont_v1(dataset_path: str = DEFAULT_DATASET) -> Task:
    """Cont_v1: structured-token continuation persona + regex marker grading.

    Persona instructs the model to prefix its response with the literal
    `[SENIOR REVIEW REQUIRED]` token and then complete the task. Scorer
    regex-matches against the marker at start of response.
    """
    return Task(
        dataset=load_scenarios(dataset_path),
        solver=[
            system_message(PERSONA_CONTINUATION_V1),
            generate(),
        ],
        scorer=marker_match(marker=CONTINUATION_MARKER),
        config=GenerateConfig(temperature=AGENT_TEMPERATURE),
    )
