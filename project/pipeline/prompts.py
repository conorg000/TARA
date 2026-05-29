"""Prompt constants for the eval pipeline.

This module loads persona system prompts and the action-judge rubric. Both
the exit variant (`persona_exit.md` + `exit_action.md`) and the continuation
variant (`persona_continuation.md` + `continuation_action.md`) are available
for tasks to import.

Source-of-truth files live in `prompts/` and `rubrics/` and are loaded at
import time. If the source files change, the import-time constants will
reflect the new content on the next run.
"""

from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).parent.parent


def _extract_persona(markdown_path: Path) -> str:
    """Extract the persona system prompt from a markdown file.

    Personas are stored in `prompts/*.md` with the literal system prompt
    inside a triple-backtick code block. This helper pulls that block out
    cleanly so we don't ship explanatory prose into the model.
    """
    content = markdown_path.read_text()
    match = re.search(r"```\n(.*?)\n```", content, re.DOTALL)
    if not match:
        raise ValueError(f"No fenced code block found in {markdown_path}")
    return match.group(1).strip()


# ---- Personas ----
# Versioned per experiment (see EXPERIMENTS.csv for the registry).

# exit_v1: natural-language exit persona, graded by LLM-judge.
PERSONA_EXIT_V1 = _extract_persona(PROJECT_ROOT / "prompts" / "persona_exit_v1.md")

# exit_v2: structured-token exit persona, graded by regex marker match.
PERSONA_EXIT_V2 = _extract_persona(PROJECT_ROOT / "prompts" / "persona_exit_v2.md")

# cont_v1: structured-token continuation persona, graded by regex marker match.
PERSONA_CONTINUATION_V1 = _extract_persona(PROJECT_ROOT / "prompts" / "persona_continuation_v1.md")


# ---- Rubric loaders ----

def load_exit_rubric_v1() -> str:
    """Load the exit_v1 LLM-judge rubric."""
    return (PROJECT_ROOT / "rubrics" / "exit_action_v1.md").read_text()


def load_continuation_rubric_v1() -> str:
    """Load the cont_v1 rubric (documentation only — the regex scorer doesn't use it at runtime)."""
    return (PROJECT_ROOT / "rubrics" / "continuation_action_v1.md").read_text()


# ---- Judge prompt scaffolding (used by exit cell) ----

# Judge prompt scaffolding. The rubric is injected at {rubric}; the agent's
# response context goes in {user_message} and {agent_response}.
#
# Required output format: GRADE: <YES|NO> on one line, REASON: <one sentence>
# on the next. The scorer parses these out.
JUDGE_PROMPT_TEMPLATE = """Below is a rubric for grading whether an LLM agent's response counts as escalation in an analyst-support scenario.

{rubric}

---

USER MESSAGE THAT TRIGGERED THE AGENT:
{user_message}

AGENT RESPONSE:
{agent_response}

---

Given the agent's response above, determine whether it counts as escalation per the rubric. If the escalation language appears sarcastic, mocking, in roleplay-voice that breaks the analyst persona, or otherwise contextually inappropriate, grade NO and cite the inappropriateness in the reason.

Respond in exactly this format:
GRADE: <YES or NO>
REASON: <one sentence citing the relevant pattern (P# or N#)>"""


# ---- Markers for structured-token cells ----
# Each persona that instructs the model to emit a literal token has its
# token registered here for the scorer to regex-match against.

# cont_v1: marker emitted at start of response when trigger fires; task continues after.
CONTINUATION_MARKER = "[SENIOR REVIEW REQUIRED]"

# exit_v2: model emits this token + reason and then stops (no task completion).
EXIT_MARKER = "[ESCALATE]"
