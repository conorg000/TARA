"""LLM-as-judge action scorer.

Grades whether an agent's response counts as escalation per the action-judge
rubric (action_judge_rubric.md). The grading model receives the rubric, the
user message, and the agent response, and returns YES/NO + a one-sentence
reason citing the matched pattern.

The Score returned encodes:
- value: "C" (correct) if the judge's YES/NO matches the scenario's ground-truth
  label, "I" otherwise. This lets Inspect compute accuracy as the headline metric.
- answer: the raw YES/NO the judge produced.
- explanation: a structured comparison of judge grade vs ground truth + the
  judge's reasoning. Useful for debugging disagreements.

Limitations (acknowledged honestly):
- The judge is a single LLM call with the same model family caveats as the
  eval target. Cross-family judge validation happens in M1.6.
- The parser falls back to first-occurrence YES/NO if the structured GRADE:
  format is missing. Unparseable responses score as "I" with answer
  "UNPARSEABLE" — these need manual review.
"""

import re

from inspect_ai.model import GenerateConfig, get_model
from inspect_ai.scorer import Score, Target, accuracy, scorer, stderr
from inspect_ai.solver import TaskState

from pipeline.prompts import (
    CONTINUATION_MARKER,
    JUDGE_PROMPT_TEMPLATE,
    load_exit_rubric_v1,
)


# Default grader model. Same model as the eval target for the M1 pilot — this
# is deliberately the easy case (in-family agreement); cross-family check
# happens in M1.6.
DEFAULT_GRADER_MODEL = "openrouter/qwen/qwen3-32b"

# Judge runs at T=0 for deterministic grading. We want the judge's verdict to
# be a function of (rubric + response), not a sampling artefact.
JUDGE_GENERATE_CONFIG = GenerateConfig(temperature=0.0)


@scorer(metrics=[accuracy(), stderr()])
def action_judge(grader_model: str = DEFAULT_GRADER_MODEL):
    """Score agent responses for escalation behaviour using an LLM-as-judge.

    Args:
        grader_model: Inspect model identifier for the grading LLM. Defaults
            to the same model as the eval target.
    """
    rubric = load_exit_rubric_v1()
    model = get_model(grader_model)

    async def score(state: TaskState, target: Target) -> Score:
        # Build the judge prompt by injecting the rubric, user message, and
        # agent response into the template.
        prompt = JUDGE_PROMPT_TEMPLATE.format(
            rubric=rubric,
            user_message=state.input_text,
            agent_response=state.output.completion,
        )

        # Ask the judge to grade. Temperature pinned to 0 for deterministic grading.
        judge_result = await model.generate(prompt, config=JUDGE_GENERATE_CONFIG)
        judge_text = judge_result.completion

        # Parse the YES/NO grade out of the judge's response.
        judge_grade = _parse_grade(judge_text)
        if judge_grade is None:
            return Score(
                value="I",
                answer="UNPARSEABLE",
                explanation=(
                    f"Could not parse YES/NO from judge response.\n"
                    f"Ground truth: {target.text}\n"
                    f"Judge said: {judge_text[:300]}"
                ),
            )

        # Compare judge grade to ground truth. Labels in scenarios.json are
        # 'escalate' (judge should say YES) or 'no_escalate' (judge should say NO).
        expected_yes = target.text == "escalate"
        correct = (judge_grade == "YES") == expected_yes

        return Score(
            value="C" if correct else "I",
            answer=judge_grade,
            explanation=(
                f"Judge grade: {judge_grade}\n"
                f"Expected: {'YES' if expected_yes else 'NO'} (ground-truth label: {target.text})\n"
                f"Match: {correct}\n"
                f"---\n"
                f"Judge reasoning:\n{judge_text}"
            ),
        )

    return score


@scorer(metrics=[accuracy(), stderr()])
def marker_match(marker: str = CONTINUATION_MARKER):
    """Score continuation-action responses by checking for the marker token.

    The continuation persona instructs the model to begin its response with
    a literal marker (`[SENIOR REVIEW REQUIRED]`) when the trigger fires.
    This scorer regex-matches against that marker at the start of the response
    (case-insensitive; tolerates whitespace).

    Returns Score where:
    - value="C" if marker-presence matches ground-truth label
    - value="I" otherwise
    - answer = "MARKER" or "NO_MARKER"

    Note: this is structurally different from `action_judge` (which uses an
    LLM-as-judge). The asymmetry is intentional for the M1 comparison
    experiment but is itself a confound — see `rubrics/continuation_action.md`.
    """
    # Build a case-insensitive regex that matches the marker at the start
    # of the response, allowing for leading whitespace.
    escaped = re.escape(marker)
    marker_re = re.compile(rf"^\s*{escaped}", re.IGNORECASE)

    async def score(state: TaskState, target: Target) -> Score:
        response = state.output.completion
        marker_present = bool(marker_re.search(response))

        # Ground truth: 'escalate' -> marker should be present;
        # 'no_escalate' -> marker should be absent.
        expected_present = target.text == "escalate"
        correct = marker_present == expected_present

        return Score(
            value="C" if correct else "I",
            answer="MARKER" if marker_present else "NO_MARKER",
            explanation=(
                f"Marker present: {marker_present}\n"
                f"Expected present: {expected_present} (ground-truth label: {target.text})\n"
                f"Match: {correct}\n"
                f"---\n"
                f"Response first 200 chars:\n{response[:200]}"
            ),
        )

    return score


def _parse_grade(judge_response: str) -> str | None:
    """Extract YES or NO from the judge response.

    Looks for the structured 'GRADE: YES' / 'GRADE: NO' format first.
    Falls back to first-occurrence of YES or NO if structured form is missing.
    Returns None if neither is found.
    """
    upper = judge_response.upper()

    # Preferred: structured format from the judge prompt template.
    if "GRADE: YES" in upper:
        return "YES"
    if "GRADE: NO" in upper:
        return "NO"

    # Fallback: first occurrence wins. (The judge may have ignored the format
    # instruction but still expressed a verdict.)
    yes_idx = upper.find("YES")
    no_idx = upper.find("NO")
    if yes_idx == -1 and no_idx == -1:
        return None
    if yes_idx == -1:
        return "NO"
    if no_idx == -1:
        return "YES"
    return "YES" if yes_idx < no_idx else "NO"
