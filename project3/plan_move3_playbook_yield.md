# Move 3 — Playbook yield study: turning 2-for-2 into a repeatability claim

**Dated:** 2026-06-12. **Status:** ✅ DONE (2026-06-12). All 7 steps run cold. Funnel killed
a condition at every stage: pre-test 3/6 → construction 2/3 → probe battery + length-control.
**Final yield (surface-controlled): 1/6** — `fraud_report` is a genuine recognition probe that
beats surface (defeats regex; model survives lexical ablation +62%; probe +0.11 over the masked-
surface ceiling). `data_deletion` downgraded (real recognition but regex-redundant + thin margin);
4 killed earlier with distinct failure codes. **Two methodological findings** (both from the
critique-driven hardening): a **length confound** (heterogeneous-length panel) and a **surface
confound** (lexically-trivial nears) — both now PLAYBOOK amendments (length-match + mandatory
surface controls). Full chain in [playbook_yield.md](playbook_yield.md); records in runlog.
**Parent:** [exp_summary_12_06_2026.md](exp_summary_12_06_2026.md) move 3.
**Depends on:** Move 2 — ✅ DONE (2026-06-12). Verdict: **panel BUILDABLE, separation is
genuine recognition** ([panel_outcome.md](panel_outcome.md)). So this IS a **panel recipe**,
not a single-probe recipe — the dependency is cleared and the design below assumes a panel.
**Compute:** mostly OpenRouter + CPU; one batched GPU session for all surviving keepers.

## The move

What this project built beyond the generic probe recipe is a validation battery and a
cheap probeability pre-test. "Robustly repeatable pipeline" is an empirical claim
currently resting on ~two conditions (watchlist keyphrase; legal/medical
advice-seeking). The experiment that earns it: codify the recipe, run it **cold** on
5–8 fresh conditions in the fuzzy band, and report yield, cost, and failure modes.
The deliverable is the playbook itself plus its measured statistics — a 6-of-8 with
characterised failures is worth more to practitioners than another tuned 2-for-2.

## Panel recipe — what Move 2 settled, and the N-condition scaling (design decision)

Move 2 proved two per-condition probes coexist in one prompt and separate on genuine
recognition. But it also measured that the two directions are **not orthogonal — they
share a large common "advice-seeking" component (cosine 0.87)**, with only a
condition-specific *residual* doing the separating. At N=2 a shared component plus a
per-condition residual is fine. **The scaling concern: as N grows, the shared component
dominates more of every read, so each probe's absolute score becomes less informative on
its own — the "dashboard of independent lights" degrades into a set of correlated readouts
where what matters is the *relative* activation across probes (which condition's residual
is highest), not whether any one probe crossed a fixed threshold.** This has two concrete
consequences the playbook study should bake in, turning the concern into free data:

1. **Run the surviving keeper conditions in ONE shared multi-rule prompt** (a panel),
   not N separate single-rule extractions. This (a) is the deployment-realistic setup,
   (b) costs the same GPU, and (c) **harvests the N>2 interference curve for free** — the
   single most valuable thing Move 2 couldn't give (it was N=2). Measure, as N climbs
   1→…→N: per-condition specificity (own-hit vs each other-hit), cross-fire, and the
   mean pairwise cosine of the direction set. The **interference curve** (does specificity
   decay as conditions are added? does mean cosine rise?) is a headline Move-3 deliverable,
   not a side note.
2. **The PLAYBOOK.md "calibration" step must specify per-condition, relative-readout
   calibration** — threshold each probe against its *own* positives and the *other
   conditions'* docs (Move 2's lesson: cross-condition docs sit above the blank baseline),
   and prefer an argmax/relative-rank read over independent fixed thresholds once N is
   moderate. Note explicitly where a fixed-threshold "independent light" stops working.

(If the interference curve shows specificity holding flat to N=5–8, the panel scales and
the deployment story is strong; if it decays, that decay rate — and the N at which
argmax-over-probes beats per-probe thresholds — is itself the finding.)

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
5. **(GPU) One batched extraction session for ALL surviving keepers, in a SHARED
   multi-rule prompt** (per the panel-recipe decision above — reuse the Move 2 pattern:
   [make_panel.py](make_panel.py)/[extract_panel.py](extract_panel.py)). Amortise the box
   setup; same position set and fp16 convention as Exp 2. Build the lattice so the
   interference curve is recoverable (each condition's hit/near cells decorrelated across
   the shared prompt). Commit before the run.
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
- **Composes with:** Move 2 (DONE — separability passed, so PLAYBOOK.md is a **panel**
  recipe; the yield conditions share one prompt and the run yields the **N>2 interference
  curve** — per-condition specificity + mean pairwise cosine as N climbs — for free, the
  natural extension of Move 2's N=2 result); Move 4 (its boundary result becomes the
  playbook's "what you can't probe for" section).