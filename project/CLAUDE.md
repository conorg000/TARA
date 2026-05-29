# CLAUDE.md

Operating instructions for working in this directory. Project context is in [revised_project.md](revised_project.md); architectural overview is in [README.md](README.md). This file is the **how-to** for keeping experiments organised as they grow.

---

## The structure (what lives where)

- **`experiments.md`** — registry of experiment designs. One section per design (persona × scorer × action type × spec format).
- **`runlog.md`** — table of runs. One row per `inspect eval` execution. Links back to experiment design + raw `.eval` log.
- **`prompts/persona_<name>_v<n>.md`** — versioned persona system prompts. Each file has a header explaining what's in it and what varies from the previous version.
- **`rubrics/<name>_v<n>.md`** — versioned grading rubrics (for LLM-judge experiments). Regex-scored experiments may still have a rubric file for documentation.
- **`pipeline/task.py`** — Inspect `@task` functions, one per row in `experiments.md`. Task names match the experiment id.
- **`pipeline/scorers.py`** — scorer implementations (LLM-judge, regex marker match, classification).
- **`data/scenarios_pilot.json`** — the 10 paired scenarios used by all exit/cont experiments.
- **`data/capability_baseline.json`** — items used by the capability baseline.
- **`logs/`** — raw Inspect `.eval` files. Each is self-contained (captures the runtime config). Don't delete.

---

## Adding a new experiment

When you want to test a new persona, scorer, action style, or other design variant:

1. **Pick an experiment ID.** Format: `<short_label>_v<n>`. Examples: `exit_v3`, `cont_v2`, `cont_softdirective_v1`. Keep it short and descriptive.
2. **Create the persona file** at `prompts/persona_<label>_v<n>.md`. Include a header explaining what this variant changes relative to the previous version. The literal persona text goes in a triple-backtick code block (parsed by `pipeline/prompts.py`).
3. **(If LLM-judge scorer)** Create a rubric file at `rubrics/<label>_v<n>.md`.
4. **Register the persona constant** in `pipeline/prompts.py` (the loader uses `_extract_persona`).
5. **Add a `@task` function** in `pipeline/task.py`. Name it `analyst_<experiment_id>`. Wire up the persona + scorer + GenerateConfig.
6. **Add a section** to `experiments.md` for the new id with all metadata + clickable links to the persona/rubric files.

**Don't edit v1 files in place.** Each variant is a new versioned file. Historical runs in `runlog.md` reference specific versions; overwriting v1 invalidates the history.

---

## Adding a new dataset

Datasets are tracked separately from experiment designs — the same experiment id can be run against multiple datasets, and each run's row in `runlog.md` records which dataset was used.

To add a new dataset:

1. Save it as `data/scenarios_<name>.json` in the same shape as `data/scenarios_pilot.json` (array of `{id, pair_id, label, user_message, trigger_type, notes}` objects).
2. No code changes needed — every task accepts a `dataset_path` parameter and dispatches via `load_scenarios()`.
3. Run with `-T dataset_path=data/scenarios_<name>.json`.

Don't edit existing dataset files in place. If the change is more than a typo, create a new dataset file with a fresh name.

---

## Running an experiment

```bash
# from /project, after sourcing OPENROUTER_API_KEY
inspect eval pipeline/task.py@<task_name> \
    --model openrouter/qwen/qwen3-32b \
    --epochs <k> \
    -T dataset_path=data/scenarios_v2.json
```

- **`--epochs k`** controls trials per scenario. Use **k=5** for headline runs (gives pass^k variance bounds). Use **k=1** or **`--limit 1`** for smoke tests.
- **`-T dataset_path=...`** selects which dataset the task runs against. Default is `data/scenarios_pilot.json` (set in task.py). Pass an explicit path when running on a different dataset (e.g. expanded sets).
- **Temperature** is set in `pipeline/task.py` per-task (currently `T=0.7` for agent calls, `T=0.0` for judge calls). Don't override at the CLI unless you mean to.
- **Cost** is small — full 10-scenario × k=5 run is ~$0.10 on Qwen 3 32B; 40-scenario × k=5 run ~$0.50.

After the run finishes, Inspect prints a log path like `logs/2026-05-27T22-41-45-00-00_analyst-exit-v2_8ZAzTohsr5xHSiEZ37f2Wc.eval`.

---

## Logging a run in `runlog.md`

After each run, **prepend** a row at the top of the table in `runlog.md`:

```markdown
| Run ID | Experiment | Dataset | Time | T | k | N | Acc | URUP | ARSP | Log | Notes |
| 2026-05-27T2242_cont_v1_k5 | [cont_v1](experiments.md#cont_v1) | [scenarios_pilot.json](data/scenarios_pilot.json) | 2026-05-27 22:42 | 0.7 | 5 | 10 | 0.84 | 0.04 | 0.28 | [.eval](logs/...) | One-sentence interpretation + follow-ups. |
```

Field rules:
- **`Run ID`** format: `YYYY-MM-DDTHHMM_<short_label>`. Short label can be experiment-id-plus-context (`exit_v2`, `cont_v1_k5`, `exit_v1_smoke`).
- **`Experiment`** is a markdown link to the matching section in `experiments.md` (anchor = experiment id).
- **`Dataset`** is a markdown link to the dataset JSON file the run used. Captures the dataset dimension separately from the experiment design.
- **`Time`** is human-readable; use the timestamp from the log filename.
- **`T`** = temperature, **`k`** = epochs, **`N`** = number of scenarios.
- **`Acc`, `URUP`, `ARSP`** are decimals (0.84 not 84%). Leave `URUP`/`ARSP` blank with `—` for tasks that don't have those metrics (capability baseline, single-sample smoke tests).
- **`Log`** is a relative link to the `.eval` file with display text `.eval`.
- **`Notes`** is one or two sentences: the headline observation + any follow-up flagged.

To compute URUP/ARSP from a log file, dump it with `inspect log dump <path>` and split samples by ground-truth label.

---

## What NOT to do

- **Don't** overwrite versioned files when iterating. New variant = new version number.
- **Don't** add a `@task` function without a matching row in `experiments.md`. The registry must stay in sync with the code.
- **Don't** delete `.eval` log files even if a run was a mistake. Add a note in `runlog.md` saying the run was a mistake; keep the log for reproducibility.
- **Don't** edit `RUNLOG_legacy.md` — it's archived from before the experiments/runlog split. Just leave it.
- **Don't** report headline numbers from k=1 runs as findings. Single-trial at T>0 is noisy; pass^k at k≥5 is the bar for reportable numbers.

---

## Things to flag in the notes when relevant

- **Methodology asymmetry** between cells being compared (e.g. LLM-judge vs regex-match). This bit us once — the original exit_v1 vs cont_v1 comparison looked like a 30pp gap that mostly disappeared once methodology was aligned.
- **N8 nullifier sensitivity** for LLM-judge experiments. Whether a response counts as escalation is sensitive to how strictly N8 is applied; record the rubric version explicitly.
- **Eval-awareness** if running scenarios that look obviously like safety tests — the model may behave differently from realistic deployment.
- **Sample size caveats** — 10 scenarios at k=5 gives wide CIs. Anything below ~30 scenarios per cell is hypothesis-generating, not finding-confirming.
