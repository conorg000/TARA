# Move 3 — Playbook yield study: turning 2-for-2 into a repeatability claim

**Dated:** 2026-06-12. **Status:** FLESHED DRAFT — freezes when execution starts.
**Parent:** [exp_summary_12_06_2026.md](exp_summary_12_06_2026.md) move 3.
**Depends on:** Move 2's verdict (panel recipe vs single-probe recipe — start after it).
**Compute:** mostly OpenRouter + CPU; one batched GPU session for all surviving keepers.

## The move

What this project built beyond the generic probe recipe is a validation battery and a
cheap probeability pre-test. "Robustly repeatable pipeline" is an empirical claim
currently resting on ~two conditions (watchlist keyphrase; legal/medical
advice-seeking). The experiment that earns it: codify the recipe, run it **cold** on
5–8 fresh conditions in the fuzzy band, and report yield, cost, and failure modes.
The deliverable is the playbook itself plus its measured statistics — a 6-of-8 with
characterised failures is worth more to practitioners than another tuned 2-for-2.

## Context for the executing agent

- Read [CLAUDE.md](CLAUDE.md) and the full Exp 2 chain in `runlog.md` (Screen B →
  construction validation → keeper) — that chain IS the recipe being codified.
- **The fuzzy band** (selection criterion for conditions): *no regex exists, but the
  model judges crisply* — measured, not assumed, by the pre-test. Below the band a
  string-match wins; above it (vague topics, unstable judgments) there is no stable
  signal. Screen B's failures (override_attempt 88%, cancel_intent 83%/17%) are the
  calibration points for what "marginal" looks like.
- **Reference implementations to imitate, not edit:** pre-test
  [make_screen_b.py](make_screen_b.py) + [observe_screen_b.py](observe_screen_b.py)
  (48-item lattice: 12 hit / 12 near / 12 form / 12 none; 3 question paraphrases;
  `inspect_gate.py@screening_ask` on `openrouter/qwen/qwen3-32b`, no-think, T=0);
  construction validation [make_exp2_validate.py](make_exp2_validate.py) (register-
  matched near twins — the load-bearing design move); keeper
  [make_exp2_keeper.py](make_exp2_keeper.py) (subagent-drafted content, hand-audited);
  extraction [extract_exp2.py](extract_exp2.py); battery [probe_exp2.py](probe_exp2.py)
  (K1 consistency filter, paraphrase rotation, K2 near controls, K4 junk selectivity,
  shuffle, positional negative control, message-local reads).
- **File hygiene:** all new artifacts carry the `playbook_` prefix. Build
  parameterised-by-condition tooling (`playbook_conditions.json` as the spec; fresh
  `make_playbook_screen.py`, `make_playbook_keeper.py`, `extract_playbook.py`,
  `probe_playbook.py`) rather than forking per condition or editing Exp 2 scripts.
- OpenRouter may be blasted freely during screening and prompt-shaping; **no coarse
  number is ever a finding** — keeper verdicts come from the greedy GPU extraction.

## Steps

1. **(CPU) Write `PLAYBOOK.md` first** — the recipe as a checklist, written *before*
   the cold runs so deviations are detectable: (i) define the condition + its near
   confusable; (ii) probeability pre-test; (iii) register-matched keeper build;
   (iv) behavioural construction validation; (v) GPU extraction (message-relative
   positions, fp16); (vi) probe + kill battery; (vii) in-context calibration note.
   Each step names its reference implementation (above) and its pass/fail bar.
2. **(CPU) Select and register conditions.** Pick 5–8 from a candidate pool, diverse
   in domain, deliberately including 1–2 expected-marginal. Candidate pool to draw
   from (executing agent finalises): seeking financial advice; complaint demanding
   compensation; request to delete personal data; reporting suspected fraud;
   requesting someone else's personal information; message written on behalf of a
   third party; implicit threat of legal action; request to expedite/queue-jump.
   **Before running anything, register predictions per condition** (pass/marginal/fail
   + main risk), A6-style, so the finalists can't be retrofitted.
3. **(OpenRouter, blast freely) Probeability pre-test per condition** — the Screen B
   pattern: 48-item lattice, 3 paraphrases. Gate per condition (same as Gate B):
   core consistency ≥ 90%, near false-fire ≤ 10%. **A pre-test kill counts in the
   yield denominator** — record and move on, no redesign rounds in cold mode.
4. **(CPU + OpenRouter) Keeper build + construction validation for the gos.** Register-
   matched pairs at Exp 2 scale (~32 pairs + form + none per condition), subagent-
   drafted, hand-audited, then the behavioural validation pass. Per cold-run
   discipline, fixes here are limited to what PLAYBOOK.md prescribes (e.g. dropping a
   failed item); anything beyond that demotes the condition to "assisted."
5. **(GPU) One batched extraction session for ALL surviving keepers** — amortise the
   box setup; same position set and fp16 convention as Exp 2. Commit before the run.
6. **(CPU) Battery per condition** (`probe_playbook.py`): recognition floor, K1 drop
   rate, K2 hit-vs-near + near-vs-none, K4 selectivity, shuffle, layer-0, negative
   control; `message_last` primary, layer-robust medians reported. (K3 rule-swap is
   NOT part of the per-condition battery — that question lives in Move 4.)
7. **(CPU) Package:** `playbook_yield.md` — the yield table (condition × outcome ×
   cost × hours × which control killed it), failure-mode map, and the finalised
   PLAYBOOK.md with any amendments logged. Runlog + datasets.md updated throughout.

## Registration

- **Question answered:** does the recipe repeat without per-condition tinkering, and
  where does it fail?
- **What is reported (committed up front):**
  - **Yield = N validated / N attempted**, where attempted includes pre-test kills —
    no silent drops, ever.
  - Per-failure classification: label instability (K1/pre-test) / topic confound (K2) /
    junk decodability (K4) / construction fault / other.
  - Dollar cost and wall-clock hours per condition, including the kills.
  - Cold/assisted status per condition, with every deviation logged in the run record
    and folded into PLAYBOOK.md as an amendment.
- **Cold-run discipline (the load-bearing commitment):** no tuning beyond what
  PLAYBOOK.md prescribes. An off-script fix is allowed but demotes that condition to
  "assisted" — the headline yield is the cold yield.
- **Success criterion:** characterised yield, not a perfect score. 8/8 achieved by
  quiet tinkering is a failed study; 5/8 with a crisp failure-mode map is a successful
  one.
- **Composes with:** Move 2 (if separability passed, PLAYBOOK.md is written as a panel
  recipe and the yield study's conditions can share prompts); Move 4 (its boundary
  result becomes the playbook's "what you can't probe for" section).

## Budget

Pre-tests ≈ $1–2 per condition (OpenRouter). Keepers + validation ≈ $2–5 per surviving
condition. One batched A100 session ≈ $30–60 total. Expected total ≈ $50–90.
