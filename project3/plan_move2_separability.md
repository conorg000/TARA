# Move 2 — Separability: do per-condition probes coexist in one prompt?

**Dated:** 2026-06-12. **Status:** VALIDATED — construction validation PASSED, keeper
locked at 216 docs; **the only remaining step is the GPU extraction** (then `probe_panel.py`).

## Validation outcome (2026-06-12 — runlog "Move 2 panel construction-validation")

- **GO.** Both-cell overgenerated to 44 across 12 archetypes → **44/44 read YES under both
  rules, 43 unanimous** → selected the diversity-balanced **32** for the keeper (pool kept
  in `panel_content_both_pool.json`). Capability 100%, cross-spec ~0%, UNCLEAR 0% (the
  loaded-ask yields clean YES/NO).
- **One watch-item, not a blocker:** loaded-ask K2 near false-fire 16%/12% (vs Exp 2's
  9%/0%); K1 strips all non-unanimous leakage to **1** mislabeled near (`legal_near_32`,
  a known-marginal Exp 2 item) and **0** medical. Registered K2 gate is probe-time AUROC,
  so it is checked at the probe stage, not here.
- **Keeper locked:** 216 docs, registered in [datasets.md](datasets.md) (`panel_*`);
  selftest passes char + token level.
- **TO RUN NEXT (GPU):** commit for a clean SHA, then `bash extract_panel.sh` on the box →
  pull `acts/panel_*__*.npz` → `./.venv/bin/python probe_panel.py --acts-dir acts --out probe_panel.json`.

## Execution status (2026-06-12 — code setup pass)

- **Dataset BUILT (CPU, done).** [make_panel.py](make_panel.py) + the NEW both-cell
  content [panel_content_both.json](panel_content_both.json) (28 letters seeking BOTH
  legal and medical advice, register-matched; **pending behavioural validation**).
  Generated `inputs/panel_ask_{legal,medical}_p{1,2,3}.json` + `inputs/panel_action.json`
  (212 docs: 64 hit / 64 near / 28 both / 28 form / 28 none; ONE multi-rule system
  prompt shared by every pass; asks are loaded-asks inside that prompt — deliberate,
  a panel monitor trains where it deploys). Form cell carried as a *diagnostic*
  (generic-seeking detector tell), not a gate.
- **Design decision (recorded):** the decorrelation audit showed the both-cell makes
  other-condition seeking mildly predictive of the label in a pooled training set
  (P(seeks-legal|seeks-medical) 0.47 vs 0.21) — biasing each direction TOWARD a false
  "collapsed" verdict. Fix: **directions train EXCLUDING the both cell**; both-docs are
  scored as held-out targets, so composition is a generalization test.
- **Selftest PASSED (CPU, done).** [extract_panel_selftest.py](extract_panel_selftest.py):
  spans/groups/labels verified on all 7 input files (148 CV groups / 212 docs).
- **Construction validation READY (OpenRouter, NOT RUN — next step).**
  **To run:** `./run_panel_validate.sh` then `./.venv/bin/python observe_panel_validate.py`.
  Checks capability / both-cell YES-under-both / behavioural cross-spec / K2 / UNCLEAR
  rate (the loaded-ask must still yield [YES]/[NO]). Any failing both-cell item is
  reauthored or dropped, `make_panel.py` re-run, validation repeated — all before GPU.
- **GPU extraction READY (deferred).** [extract_panel.py](extract_panel.py)
  (self-contained; per-rule FLAG parsing → FLAG-BOTH/-LEGAL/-MEDICAL/NOFLAG) +
  runbook [extract_panel.sh](extract_panel.sh). **To run on the box (after validation
  passes + git commit for a clean SHA):** `bash extract_panel.sh` → pull
  `acts/panel_*__*.npz` (or run the probe on-box and pull `probe_panel.json` —
  thread-1 flaky-uplink lesson). 7 passes × 212 docs, ~Exp-2-scale session.
- **Probe READY + SMOKE-TESTED (CPU, done).** [probe_panel.py](probe_panel.py)
  encodes the frozen anchors (floor ≥0.90, crossfire ≤0.65 / ≥0.75 collapsed,
  composition ≥0.80, K2, K4 selectivity with crc32 junk labels, shuffle), reads
  verdicts on **layer-robust medians** at message_last, prints the negative-control
  position as such, and reports geometry two ways (operational probe-direction cosine
  — anti-aligned-by-construction caveat — and pure hit-vs-none cosine).
  Verified end-to-end on planted orthogonal signals:
  [probe_panel_smoke.py](probe_panel_smoke.py) → all 6 condition×position verdicts
  PASS as planted, negative control dead, pure cosine ≈ 0. **To run after extraction:**
  `./.venv/bin/python probe_panel.py --acts-dir acts --out probe_panel.json`.
- **Remaining after results land:** runlog entry (verbatim tables), datasets.md
  registration of `panel_*` (do at validation time, when the both-cell content is
  final), `panel_outcome.md`, summary-doc status update.

**Original plan (frozen registration) below.**
**Parent:** [exp_summary_12_06_2026.md](exp_summary_12_06_2026.md) move 2.
**Depends on:** nothing. **Feeds:** Move 3 (panel recipe vs single-probe recipe).
**Compute:** OpenRouter screening (cheap, blast freely) → one GPU extraction → CPU probe.

## The move

The deployment vision is a panel: one content probe per rule, all read off a single
extraction of a single multi-rule prompt. Every probe so far was trained and read in a
*single-rule* prompt. Untested: whether two directions stay specific when both rules
and both kinds of content share one context, rather than interfering or collapsing
into a generic "something rule-relevant is here" signal. If separability fails the
panel dies; either answer is essential.

## Context for the executing agent

- Read [CLAUDE.md](CLAUDE.md), the Exp 2 runlog entry, and
  [exp2_fuzzy_outcome.md](exp2_fuzzy_outcome.md) — this move reuses Exp 2's conditions,
  content, and probe machinery wholesale.
- **Conditions:** legal-advice + medical-advice. Both validated (Screen B 100%/96%
  consistency); their semantic closeness makes this a deliberately *hard* interference
  test. Their content already exists in `exp2_content.json` / `exp2_keeper_*`.
- **Reference implementations to imitate, not edit:** dataset build
  [make_exp2_keeper.py](make_exp2_keeper.py); construction validation
  [make_exp2_validate.py](make_exp2_validate.py) + [observe_exp2_validate.py](observe_exp2_validate.py)
  (OpenRouter harness: `inspect_gate.py@screening_ask`, `openrouter/qwen/qwen3-32b`,
  no-think, T=0); extraction [extract_exp2.py](extract_exp2.py) (message-relative
  positions, fp16); probe [probe_exp2.py](probe_exp2.py) (consistency filter,
  paraphrase rotation, pair-disjoint CV, document-disjoint cross-pass `pair_oof`).
- **Standing lessons that bind here:** greedy-on-GPU is the truth (OpenRouter coarse
  shapes, never scores); `message_last` was Exp 2's clean read (`message_mean`/`final`
  leak topic/length); lead with diff-of-means; layer-robust medians for any cross-pass
  comparison (the Exp 2 K3 layer-artifact lesson).
- **File hygiene:** all new artifacts carry the `panel_` prefix (`make_panel.py`,
  `extract_panel.py`, `probe_panel.py`, `panel_*` datasets registered in
  [datasets.md](datasets.md)). Import shared machinery (`train_probe.py`,
  `cross_pass_probe.py`); copy a helper into your own file rather than editing it.

## Steps

1. **(CPU) Author the multi-rule prompt.** One intake-clerk instruction set containing
   BOTH flag rules with distinct outputs (e.g. `FLAG-LEGAL: …` / `FLAG-MEDICAL: …`),
   same register as the Exp 2 prompt. All passes — asks and action — run inside this
   one multi-rule context; that shared context is the entire point of the experiment.
2. **(CPU) Build the lattice** (`make_panel.py`). Cells:
   - **A-only** = the 32 legal hits, **C-only** = the 32 medical hits, **neither** =
     the 28 none docs — all reused from `exp2_content.json`;
   - **both** = NEW content, ~24–32 letters genuinely seeking legal AND medical advice
     in one message (e.g. workplace-injury: treatment questions + claim questions).
     Subagent-draft + hand-audit, per the Exp 2 keeper precedent;
   - carry the 64 register-matched **near** docs as a K2-in-panel re-check (cheap,
     content exists).
   Audit decorrelation: neither condition's presence may predict the other's.
3. **(OpenRouter, blast freely — throwaway docs) Construction validation.** Before any
   GPU: in the multi-rule context, ask both questions (3 paraphrases each) over the
   lattice. Required: legal hits YES under the legal question / NO under medical (and
   vice versa); **both-docs YES under BOTH questions** (the new cell's existence check);
   nears/none NO. Iterate prompt shape here as much as needed — screens choose, keepers
   measure. New-content items that fail are reauthored or dropped *before* the keeper.
4. **(GPU) One extraction** (`extract_panel.py`, pattern of extract_exp2.py). Passes:
   3 ask paraphrases × 2 conditions + 1 action — all in the multi-rule prompt — over
   the full lattice. Positions: the Exp 2 message-relative set (`message_last` primary,
   `message_mean`, `final`, `post_message`, `pre_message_final` negative control,
   `question_mean`). fp16. Commit before the run (clean SHA for the runlog).
5. **(CPU) Probe** (`probe_panel.py`). Train direction_legal and direction_medical on
   their own consistency-filtered ask labels (paraphrase-rotated). Note the training
   negatives for each direction naturally include the other condition's hits (they
   answer NO) — preserve that; it's what makes specificity trainable. Compute, per
   layer and position, the registered metrics below; report layer-robust medians
   alongside best-layer.
6. **(CPU) Write up:** runlog entry with verbatim tables, datasets.md registration,
   plain-language outcome doc (`panel_outcome.md`), summary-doc status update.

## Registration

- **Question answered:** are per-condition recognition directions separable and
  specific within one shared multi-rule context — is the panel buildable?
- **Metrics and anchors (diff-of-means, `message_last`, layer-robust medians; numbers
  freeze at execution):**
  - **Floor:** in-condition recognition (probe_A: A-only vs neither) **≥ 0.90** for
    both conditions. Below → the multi-rule context itself broke the probes; that's
    the finding (interference at the recognition level).
  - **Cross-specificity (the kill-switch):** probe_A on C-only vs neither **≤ 0.65**
    (and symmetrically). **≥ 0.75 → collapsed** into generic salience; the panel claim
    dies and the result is reported as "one generic rule-relevance direction, not
    per-condition directions." Between 0.65–0.75 → gray; report as partial
    interference, no goalpost moves.
  - **Composition:** on both-docs, each probe fires vs neither **≥ 0.80**.
  - **Geometry (descriptive):** cosine between the two directions per layer; reported,
    not gated.
  - **K2-in-panel (re-check):** hit-vs-near holds at the message-local read, as in
    Exp 2.
  - **Battery:** layer-0 ≈ 0.5, shuffle ≈ 0.5, `pre_message_final` ≈ 0.5 on everything.
- **Commitments:** both outcomes are findings; the both-cell is new content, so any
  both-cell anomaly is checked against construction (validation logs) before being
  interpreted; single-rule Exp 2 numbers may be cited as approximate baselines for the
  in-condition floor but the contexts differ — comparison is descriptive, never a gate.

## Budget

Screening ≈ $2–5 (OpenRouter). Extraction: ~210 docs × 7 passes ≈ one Exp-2-scale
A100 session, ≈ $20–40. CPU probe free.
