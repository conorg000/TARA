# Scope self-awareness eval — analyst pilot

Pilot eval for whether an LLM agent reliably escalates to a human when its assigned scope is exceeded. Implementation uses [Inspect](https://inspect.aisi.org.uk/).

See `revised_project.md` for the research design.

## Setup

```bash
# from /project
pip install -e .

# .env at the repo root should contain OPENROUTER_API_KEY
# Inspect reads this env var directly; either export it or load via dotenv
export $(grep -v '^#' ../.env | xargs)
```

## Running the pilot

```bash
# from /project
inspect eval pipeline/task.py --model openrouter/qwen/qwen3-32b
```

The task:
1. Loads the 10 pilot scenarios from `data/scenarios_pilot.json`.
2. For each scenario: prepends the analyst persona system prompt (`persona_prompt.md`) and sends the user message to Qwen via OpenRouter.
3. Grades the response with the action-judge scorer — an LLM-as-judge call that applies the rubric (`action_judge_rubric.md`) and returns YES/NO escalation.
4. Compares the judge's grade to the scenario's ground-truth label.
5. Writes per-sample logs to `logs/` (Inspect's default location).

## Project layout

```
project/
├── pipeline/                   # eval code
│   ├── task.py                 # @task definition
│   ├── prompts.py              # persona + judge framing constants
│   ├── scorers.py              # action_judge LLM-as-judge scorer
│   └── data.py                 # scenarios → Inspect Samples loader
├── data/
│   └── scenarios_pilot.json    # structured scenarios (paired)
├── action_judge_rubric.md      # the rubric (source of truth for judge)
├── persona_prompt.md           # the locked analyst persona
├── scenarios_pilot.md          # human-readable scenario doc
└── revised_project.md          # research design
```
