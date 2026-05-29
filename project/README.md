# Scope self-awareness eval — analyst pilot

Pilot eval for whether an LLM agent reliably escalates to a human when its assigned scope is exceeded. Implementation uses [Inspect](https://inspect.aisi.org.uk/).

See `revised_project.md` for the research design.

## Setup

```bash
# from /project
pip install -e .

# .env at the repo root should contain OPENROUTER_API_KEY
export $(grep -v '^#' ../.env | xargs)
```

## Running an experiment

Each `@task` function in `pipeline/task.py` corresponds to one row in `experiments.csv`. Run via Inspect, specifying the task name:

```bash
# Exit cell (natural-language directive, LLM-judge grading) — v1, the original M1 pilot
inspect eval pipeline/task.py@analyst_exit_v1 --model openrouter/qwen/qwen3-32b --epochs 5

# Exit cell (structured-token directive, regex grading) — v2, methodology-aligned mirror of cont_v1
inspect eval pipeline/task.py@analyst_exit_v2 --model openrouter/qwen/qwen3-32b --epochs 5

# Continuation cell (structured-token, regex grading)
inspect eval pipeline/task.py@analyst_cont_v1 --model openrouter/qwen/qwen3-32b --epochs 5

# Capability baseline (classification only)
inspect eval pipeline/capability.py --model openrouter/qwen/qwen3-32b
```

After running, append a row to the top of [runlog.md](runlog.md) with the log path + headline metrics.

## Records — where they live

| File | What's in it |
|---|---|
| [experiments.md](experiments.md) | Registry of experiment designs. One section per design (persona × scorer × action type × spec format). |
| [runlog.md](runlog.md) | History of runs as a table. One row per execution. Links to experiment design + raw `.eval` log. |
| `logs/` | Raw Inspect `.eval` log files. Self-contained for reproducibility. |
| `RUNLOG_legacy.md` | Original markdown runlog from before the experiments/runlog split. Kept for git history. |

**Adding a new experiment:** add a section to [experiments.md](experiments.md) with a fresh `id`, fill in persona path, scorer, rubric (if any), action type, spec format, and notes. Create the persona file (versioned, e.g. `prompts/persona_<name>_v1.md`). Add a `@task` function in [`pipeline/task.py`](pipeline/task.py) named to match the experiment id.

**Adding a new run:** run via `inspect eval` as above. After it finishes, prepend a row to the runlog table in [runlog.md](runlog.md) with the log path and headline metrics (accuracy, URUP, ARSP if applicable).

## Project layout

```
project/
├── pipeline/                       # eval code
│   ├── task.py                     # @task definitions (one per experiment id)
│   ├── capability.py               # capability baseline task + scorer
│   ├── prompts.py                  # persona loaders + judge framing
│   ├── scorers.py                  # action_judge (LLM-judge) + marker_match (regex)
│   └── data.py                     # scenarios → Inspect Samples loader
├── prompts/                        # versioned persona system prompts
│   ├── persona_exit_v1.md          # natural-language exit
│   ├── persona_exit_v2.md          # structured-token exit
│   └── persona_continuation_v1.md  # structured-token continuation
├── rubrics/                        # versioned action-grading rubrics
│   ├── exit_action_v1.md           # LLM-judge rubric for exit_v1
│   └── continuation_action_v1.md   # documentation for cont_v1 (regex scorer at runtime)
├── data/                           # scenario datasets
│   ├── scenarios_pilot.json        # 10 paired scenarios used by all exit/cont experiments
│   └── capability_baseline.json    # classification items
├── logs/                           # Inspect .eval files
├── experiments.csv                 # experiment design registry
├── runlog.csv                      # run history
└── revised_project.md              # research design
```
