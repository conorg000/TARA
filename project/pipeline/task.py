"""Inspect task: analyst-escalation pilot.

For each scenario in the pilot dataset:
1. Inject the analyst persona system prompt.
2. Send the user message to the eval-target model.
3. Capture the response.
4. Grade with action_judge LLM-as-judge against the rubric.

Run with:
    inspect eval pipeline/task.py --model openrouter/qwen/qwen3-32b
"""

from inspect_ai import Task, task
from inspect_ai.model import GenerateConfig
from inspect_ai.solver import generate, system_message

from pipeline.data import load_scenarios
from pipeline.prompts import PERSONA_PROMPT
from pipeline.scorers import action_judge


# Reproducibility-relevant defaults. Agent runs at deployment-shaped T=0.7
# (matches typical production defaults; gives us natural variance for pass^k
# later). Note that the model identifier 'openrouter/qwen/qwen3-32b' is a
# route, not a dated snapshot — OpenRouter does not always expose stable
# pin-able versions. Document the route + run date in any results writeup.
AGENT_TEMPERATURE = 0.7


@task
def analyst_escalation_pilot() -> Task:
    """Pilot eval for analyst-agent escalation behaviour.

    Returns an Inspect Task that runs the 10 pilot scenarios end-to-end:
    persona-prompted Qwen call → response → LLM-as-judge grade vs ground truth.
    """
    return Task(
        dataset=load_scenarios(),
        solver=[
            # Prepend the analyst persona as a system message before every call.
            system_message(PERSONA_PROMPT),
            # Generate the agent's response.
            generate(),
        ],
        scorer=action_judge(),
        config=GenerateConfig(temperature=AGENT_TEMPERATURE),
    )
