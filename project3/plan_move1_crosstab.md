# Move 1 — Cross-tab: was Exp 2's behaviour genuinely rule-dependent?

**Dated:** 2026-06-12. **Status:** CODE READY — setup complete and smoke-tested; awaiting
one short GPU session. Registration below is now FROZEN (code encodes the bands).

## Execution status (2026-06-12)

- **Step 1 DONE — behaviour record is NOT local.** `acts/` holds only the keyphrase
  v4/v6 passes and `thread1/`; no `exp2_*` npz ever came home. All 8 keeper input files
  exist locally (`inputs/exp2_keeper_*.json`, 184 ids identical across passes,
  metadata verified: action passes carry `meta.rulecond`, asks carry
  `meta.askcond`+`paraphrase`). The GPU fallback (step 2) is therefore the live path —
  unless the Exp 2 box is still alive, in which case pulling any one
  `acts/exp2_<pass>__<position>.npz` per pass also works (the analysis auto-prefers npz).
- **Step 2 READY (GPU, deferred) — [crosstab_behaviour_gpu.py](crosstab_behaviour_gpu.py)
  + [run_crosstab_behaviour.sh](run_crosstab_behaviour.sh).** Generation-only greedy
  rerun (no activation capture; prompt build imported from extract_exp2.py, parsing from
  markers.py, one-doc-at-a-time decoding — parity with the original run by construction).
  **To run on the box:** `bash run_crosstab_behaviour.sh` (commit first for a clean SHA;
  ~minutes on an A100; 2 required action passes + 6 cheap ask passes) → pull
  `acts/crosstab_beh_*.json` to the laptop.
- **Step 3 READY (CPU, deferred until behaviour lands) —
  [crosstab_exp2.py](crosstab_exp2.py).** **To run:** `python crosstab_exp2.py --beh-dir acts`.
  Prints the three verbatim tables + verdict; writes `crosstab_exp2.json` and
  `crosstab_behaviour_matched.json` (Move 4's input). Smoke-tested end-to-end on
  fabricated behaviour with hand-computed expectations:
  `python crosstab_smoke.py` → 13/13 checks PASS (rates, verdict band, truncation
  exclusion, K1-core, matched lists, over-flag localisation).
- **Step 4 PENDING** (runlog entry + summary-doc wording) — blocked on real results.
- **Analysis details pinned at setup (now frozen):** UNDERMINED is operationalised as
  matching−swapped < 10 points (the band the plan stated qualitatively); truncated
  generations are excluded from rate denominators and reported (the A5 lesson — a
  truncation is a non-answer, not an omission); the K1-core secondary line restricts
  hits to own-ask consistent-YES docs when the ask passes are available.
**Parent:** [exp_summary_12_06_2026.md](exp_summary_12_06_2026.md) move 1.
**Depends on:** nothing. **Feeds:** Move 4 (the behaviour-matched doc list).
**Compute:** CPU only, unless the behaviour record is lost (see step 2 fallback).

## The move

The summary's claim "the binding lives on the decision side" presumes Exp 2's *actions*
tracked the active rule per-document — legal letters flagged under the legal rule and
not under the medical one. That was inferred from aggregate flag counts (legal 56/184,
medical 63/184, vs 32 true hits each), never shown per-document. One cross-tab settles
it. It also produces the behaviour-matched doc list Move 4 needs.

## Context for the executing agent

- Read [CLAUDE.md](CLAUDE.md) first (reporting rules), then the Exp 2 runlog entry
  (`runlog.md` 2026-06-12) and [exp2_fuzzy_outcome.md](exp2_fuzzy_outcome.md).
- The Exp 2 keeper is `exp2_keeper_*` (registered in [datasets.md](datasets.md)):
  184 docs = 32 register-matched hit/near pairs per condition + 28 form + 28 none.
  Inputs regenerate deterministically from [make_exp2_keeper.py](make_exp2_keeper.py)
  + `exp2_content.json`.
- **Greedy is the truth.** OpenRouter behaviour is coarse-only in this project (it
  over-counts no-flag events — standing lesson). A verification claim cannot be scored
  on OpenRouter numbers, so if the greedy record is lost it must be regenerated greedy.
- **File hygiene:** all new artifacts carry the `crosstab_` prefix. Import existing
  machinery; never edit shared scripts (`probe_exp2.py`, `make_exp2_keeper.py`, …).

## Steps

1. **(CPU) Locate the greedy behaviour record.** The per-doc FLAG/NOFLAG for both
   action passes lives in the extraction npz `behaviour` arrays
   (`acts/exp2_action_legal__<pos>.npz`, `acts/exp2_action_medical__<pos>.npz` — any
   single position suffices; behaviour is per-doc, identical across positions).
   `probe_exp2.json` does NOT contain per-doc records. Check the laptop `acts/` dir
   first; if absent, check whether the Exp 2 GPU box is still alive and pull (or read
   on-box and pull a JSON, per the thread-1 flaky-link precedent).
2. **(GPU, fallback only — small)** If the npz are gone and the box is dead: regenerate
   the keeper inputs, run a **generation-only** greedy pass (no activation capture) of
   the two action prompts over the 184 docs on a rented GPU. This is minutes of compute;
   do NOT substitute OpenRouter. Record the rerun in runlog as the behaviour source.
3. **(CPU) Build the cross-tab** (`crosstab_exp2.py`, new file). Join per document:
   `id, cell (hit/near/form/none), domain (legal/medical), flag_under_legal,
   flag_under_medical, ask_label (consistency-filtered, from the ask passes or
   recomputed via probe_exp2.py's filter)`. Emit:
   - the full cell × rule flag-rate table (verbatim into runlog);
   - per-doc 2×2 for hits: flagged-under-matching × flagged-under-swapped, with the
     discordant counts both ways;
   - over-flag localisation: which cells the ~24–31 non-hit flags land in, per rule,
     and whether *those* are rule-dependent;
   - `crosstab_behaviour_matched.json` — the docs with the SAME action under both
     rules (split by flagged-both / flagged-neither), for Move 4.
4. **(CPU) Write up:** runlog entry (table verbatim + read), one-line status update in
   the summary doc, and soften/confirm the "binding lives elsewhere" wording per the
   outcome bands below.

## Registration

- **Question answered:** did flagging condition on the prompt's rule per-document —
  the behavioural premise under "comprehension is rule-independent, behaviour isn't"?
- **Pre-registered reading bands (on the 32+32 true hits):**
  - **VERIFIED:** most hits are discordant in the right direction (flagged under
    matching, not under swapped) — say ≥70% flagged-matching AND ≤25% flagged-swapped.
    The dissociation premise stands as written.
  - **NOISY:** rule-dependence present but a substantial minority (>25%) of hits flag
    under the swapped rule too. Premise stands, stated with the measured noise; the
    over-flag analysis becomes part of the story.
  - **UNDERMINED:** hit flagging is essentially rule-independent. The summary's
    "behaviour is rule-dependent" claim is rewritten, and Move 4's motivation is
    re-examined before it runs.
- **Commitments:** report the full table verbatim, including ugly cells; no dropping
  the over-flags. This is a verification with no preferred outcome — both directions
  are actionable. No kill condition; the deliverables are the table and
  `crosstab_behaviour_matched.json` regardless.

## Budget

≈ $0 (CPU) in the expected path; ≤ ~$5 GPU if the fallback regeneration is needed.
