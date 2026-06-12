# Move 4 — The spontaneity ladder: where does always-on comprehension end, and does the rule take over?

**Dated:** 2026-06-12. **Status:** FLESHED DRAFT — freezes when execution starts.
**Parent:** [exp_summary_12_06_2026.md](exp_summary_12_06_2026.md) move 4.
**Depends on:** Move 1 — a full gate, not a convenience: this move's motivation rests
on Exp 2's behaviour being rule-dependent per-document, which Move 1 verifies (an
UNDERMINED result reframes this plan before any spend). Move 1 also supplies the
behaviour-matched doc list used here.
**Compute:** OpenRouter screening → GPU extraction (the largest of the four moves) → CPU probe.

## The move

Exp 2's K3 tested rule-conditioning on a condition the model computes *without* the
rule (advice-seeking is a heavily-trained natural category), so the rule had no work to
do at reading time and the test could not have detected modulation. The honest scope of
that negative is "the rule doesn't modulate the reading of spontaneously-computed
conditions" — not "rule-conditioned computation doesn't exist." The test that could
find it: conditions the model would *never* compute unprompted, where the rule is the
only possible source of the computation. One design yields both the rule-awareness
answer and the playbook's hard boundary ("what you can't probe for").

## Context for the executing agent

- Read [CLAUDE.md](CLAUDE.md), [exp2_fuzzy_outcome.md](exp2_fuzzy_outcome.md) (esp.
  the K3 section), and the Exp 2 runlog entry. The method here is the Exp 2 stack with
  a new dataset axis; reuse its patterns throughout (register-matching, consistency
  filter, paraphrase rotation, message-local reads, layer-robust medians,
  diff-of-means first).
- **The central subtlety — where "without the rule" is measured.** In an ask pass, the
  *question itself* makes the compound condition relevant, exactly as a rule would. So
  "readable without the rule" can only be measured on a pass with **neither rule nor
  question**: a neutral-task pass, scored cross-pass by the ask-trained direction
  (standard firewall: train on ask, score where nothing prompts the computation).
  Getting this wrong voids the experiment.
- **The headline metric is compound-vs-components, not compound-vs-none.** A probe
  reading "A∧B" must separate A∧B docs from A-only and B-only docs. Compound-vs-none
  can be passed by reading either component alone.
- **File hygiene:** all new artifacts carry the `ladder_` prefix (`make_ladder.py`,
  `extract_ladder.py`, `probe_ladder.py`, `ladder_*` datasets in
  [datasets.md](datasets.md)). Import shared machinery; never edit Exp 2 or panel files.

## Steps

1. **(CPU) Pin the rungs.** Three rungs by how spontaneously the model computes the
   condition; final wording set after screening:
   - **R1 — natural category (anchor, no rerun):** Exp 2's advice-seeking results are
     the R1 datapoint (readable, rule-independent). Cite; note the context differences
     honestly rather than re-extracting.
   - **R2 — arbitrary conjunction of computed components:** e.g. *seeking advice AND
     states an explicit deadline*. Both components trivially computed; their
     conjunction has no reason to be a trained feature.
   - **R3 — knowledge-dependent conjunction:** e.g. *seeking legal advice AND writing
     from a jurisdiction whose legal system differs from England & Wales* — the rule
     names the abstract property, the letter names only a city (Scottish vs English
     cities), and the link (city → Scotland → separate legal system) is world
     knowledge the model has but would not deploy unprompted. If screening shows the
     model can't make that inference reliably even when asked, fall back to an easier
     R3 (rule names Scotland explicitly) and record the substitution.
2. **(OpenRouter, blast freely) Behavioural screen per rung — the probeability gate.**
   With the rule in context, ask the compound question (3 paraphrases) over a draft
   lattice; also ask each component question. Gates per rung: compound-judgment
   consistency ≥ 90% on core cells; component judgments near-ceiling. A rung that
   fails after one wording iteration is recorded as "model cannot judge this compound
   behaviourally" — itself a boundary datapoint — and is dropped from extraction.
   Shape prompts here as much as needed; screening docs are throwaway.
3. **(CPU) Build the keeper lattices** (`make_ladder.py`). Per rung, components
   decorrelated by construction: **A∧B / A-only / B-only / neither**, register-matched
   in the Exp 2 style (~24–32 docs per cell), balanced so neither component predicts
   the other. Audit the decorrelation at generation time.
4. **(CPU) Author the two prompt variants per rung:** **rule-present** (the compound
   rule, with a flag action) and **rule-absent** — identical prompt with the compound
   rule replaced by a **length-matched placebo rule** (unrelated condition), so the
   variants differ only in the rule's content, not prompt shape. Both variants include
   the same neutral task so a no-question pass exists in each.
5. **(GPU) Extraction** (`extract_ladder.py`), committed before the run. Per rung ×
   per variant: compound-ask passes (3 paraphrases), component-ask passes (1 each),
   and the neutral/action pass (no question — the pure-reading pass that the
   without-rule measurement depends on). Exp 2 position set, fp16. R2 and R3 in one
   GPU session if possible.
6. **(CPU) Probe** (`probe_ladder.py`). Per rung: train the compound direction on
   consistency-filtered compound-ask labels (within each variant); score the
   **pure-reading passes** of both variants cross-pass, document-disjoint. Compute the
   registered metrics below. Component directions trained and scored the same way for
   the component control. Decision-adjacent positions only interpreted within
   behaviour-matched cells (per `crosstab_behaviour_matched.json` methodology from
   Move 1).
7. **(CPU) Write up:** runlog (verbatim per-layer tables), `ladder_outcome.md`
   plain-language doc, the headline plot, datasets.md, summary-doc update.

## Registration

- **Question answered:** does rule-conditioned computation appear exactly where
  comprehension alone can't supply the answer — and where is the hard boundary of the
  content-probe panel?
- **The headline plot:** compound readability (A∧B vs the *better-separated* of
  A-only/B-only, diff-of-means, message-local, layer-robust) × rung (R1/R2/R3) ×
  context (rule-present pure-reading vs rule-absent pure-reading).
- **Pre-registered structure (numbers freeze at execution):**
  - **Prediction:** readability-without-rule falls down the ladder (R1 high — known;
    R3 ≈ chance). If R3 reads ≥ 0.80 *without* the rule, the rung is mis-designed
    (the compound is spontaneously computed after all) → redesign the rung; do not
    report it as a positive.
  - **The open question (both outcomes are findings):** does readability-*with*-rule
    fall with it?
    - *Restored* (with-rule ≥ 0.80 where without-rule ≤ 0.65) → top-down,
      rule-conditioned computation exists — found where it has a reason to live.
    - *Falls with it* (both ≤ 0.65 at R3) → the panel has a hard boundary at
      "conditions the model wouldn't compute anyway," and binding-at-decision holds
      even when the rule is the only possible source.
- **Component control (load-bearing):** each component must decode (≥ 0.90) in every
  arm where the compound is tested. A compound null with a failed component is a
  construction failure, not a binding result, and is reported as such.
- **Commitments:** the ask-pass can always read the compound (the question elicits the
  computation) — that's the training signal, never the finding; the finding lives only
  in the pure-reading passes. Decision-adjacent reads are exploratory and
  behaviour-matched only. No rescue hunts on a fallen with-rule curve; one wording
  iteration per rung at screening, then the gate is the gate.

## Budget

Screening ≈ $5–10 (OpenRouter, two rungs × iterations). Extraction: 2 rungs × 2
variants × ~6 passes × ~100–130 docs — the largest GPU job of the four moves,
≈ $40–80. CPU probe free.
