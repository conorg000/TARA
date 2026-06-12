# Move 4 — The spontaneity ladder: where does always-on comprehension end, and does the rule take over?

**Dated:** 2026-06-12. **Status:** FLESHED DRAFT — freezes when execution starts.
**Parent:** [exp_summary_12_06_2026.md](exp_summary_12_06_2026.md) move 4.
**Depends on:** Move 1 — ✅ DONE (2026-06-12), verdict **NOISY** (not UNDERMINED), so the
gate is cleared and this move proceeds. Move 1 also (a) supplies the behaviour-matched-cell
*methodology* for the decision-adjacent reads (Move 4 builds its own matched cells from its
own extraction — the Exp 2 `crosstab_behaviour_matched.json` doc list is not the literal
input), and (b) **sharpens the prior**: it found the action pass fires on *domain-general*
advice-seeking, and the two rules over-extend along different axes (legal ≈ advice-detector,
medical ≈ topic-detector) — i.e. even simple conditions lean on "what content is present,"
not the precise rule-conjunction. That nudges the prior toward Move 4's *hard-boundary*
outcome (with-rule readability falling alongside without-rule). Not a reframe — both outcomes
remain findings — just a calibrated expectation.
**Compute:** OpenRouter screening (heavy — the design loop lives here) → GPU extraction
(the largest of the four moves; scales with how many conditions survive screening) → CPU probe.

## The move

Exp 2's K3 tested rule-conditioning on a condition the model computes *without* the
rule (advice-seeking is a heavily-trained natural category), so the rule had no work to
do at reading time and the test could not have detected modulation. The honest scope of
that negative is "the rule doesn't modulate the reading of spontaneously-computed
conditions" — not "rule-conditioned computation doesn't exist." The test that could
find it: conditions the model would *never* compute unprompted, where the rule is the
only possible source of the computation. One design yields both the rule-awareness
answer and the playbook's hard boundary ("what you can't probe for").

## Choosing the conditions — the crux (take time here; this *is* the experiment)

The result is only as good as the conditions, and picking them is a design problem to be
solved by **screening a diverse battery and selecting the fairest**, not by committing to
one clever task up front. Do **not** anchor on any single instantiation (the jurisdiction
idea below is *one risky candidate*, not the plan). Run **≥2 diverse instantiations** of R3
(and ideally R2): if the spontaneity-ladder pattern holds across genuinely different tasks
it's a property of the model; if it only holds for one contrived task it's an artifact.
Diversity *is* the robustness here. Note also (from Move 1 + Exp 2) that "seeking legal
advice" is itself *spontaneously computed*, so any R3's **decisive** element has to be
something genuinely beyond spontaneous reading — not just "legal advice, plus a detail."

**What makes a valid R3 (the essence, task-independent):** a compound where (i) each
component is individually readable, (ii) the model can judge the compound *when asked*
(the probeability gate — else the rung is moot), and (iii) the **decisive** sub-judgment
cannot be made from the letter alone by spontaneous reading. (iii) is what separates R3
from R1/R2. There are two clean ways to make (iii) true; they test subtly different things,
so **run both**:

**Family A — world-knowledge inference (the truer "spontaneity" test).** The decisive
sub-fact is something the model *knows in its weights* but would not surface while reading
*this* letter unprompted. The without-rule arm is then a **real measurement** — is it
spontaneously computed or not? Risk: a *retrieval* confound (if the model doesn't reliably
know/judge the fact, the rung dies on the probeability gate, not on spontaneity) — use
well-known facts and let the screen filter. Candidates to screen (several):
  - seeking *medical* advice **AND** about a *prescription-only* medication (drug → Rx status);
  - a *complaint* **AND** about a *regulated* profession (doctor/solicitor vs an unregulated trade);
  - seeking *legal* advice **AND** a *different-legal-system* jurisdiction (city → Scotland →
    Scots law) — the original idea, **flagged risky**: niche, and the model may not judge it
    cleanly even when asked;
  - a request **AND** the writer is a *minor* (stated age → under-18 threshold).

**Family B — rule-supplied criterion (the cleaner "binding-timing" test).** The decisive
comparison is *logically* impossible from the letter alone because the criterion lives only
in the rule — a threshold, a list, a cutoff. This is the **purest** instance of
"comprehension alone cannot supply the answer" (guaranteed by construction, not contingent
on the model's knowledge), arguably the *fairest* core test. Asymmetry to note: the
without-rule arm is at chance *by construction* (criterion absent), so the content is the
**with-rule** arm — does the model do the comparison **at reading time** (message-local
readable) or defer it to the decision (only decision-adjacent)? A "when does binding happen"
read, complementary to Family A's "is it spontaneous" read. Candidates to screen (several):
  - refund/compensation request **AND** amount *over £X* (rule sets £X; letters state varied amounts);
  - complaint **AND** event *older than N months* (rule sets N; letters state varied timeframes);
  - product mentioned is *on the rule's recall list* (the keyphrase essence, fuzzier framing).
  Amounts/dates/names are read spontaneously; the *comparison to the rule's parameter* is the
  rule-gated step.

**Selection method (screens choose, keepers measure):**
1. Draft ~30–40 throwaway items per candidate spanning the **A∧B / A-only / B-only / neither** cells.
2. *(OpenRouter)* **Probeability gate:** with the rule in context, can the model judge the
   compound consistently (≥90% on core cells, 3 paraphrases)? Components near-ceiling? Drop
   candidates that fail after one wording fix (record as boundary datapoints — themselves results).
3. *(OpenRouter, Family A only)* **Spontaneity pre-check:** does the model volunteer the
   decisive fact when asked to *summarise* the letter with NO rule and NO question? If it
   spontaneously surfaces "this is a prescription drug," the candidate is secretly R1 →
   deprioritise. (Family B skips this — its criterion is absent without the rule by construction.)
4. **Constructability:** can you build a clean decorrelated, register-matched lattice (A-only/
   B-only must be genuine near-misses, not surface-distinguishable)?
5. Keep the **2–3 survivors** spanning both families; those graduate to the keeper build and
   one batched GPU extraction.

This loop is where the "take time getting the data right" effort goes — expect heavy prompt/
item iteration on OpenRouter before any GPU.

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
  Getting this wrong voids the experiment. **Family-A vs Family-B asymmetry:** for
  Family A the without-rule arm is a *real measurement* (is the world-fact spontaneously
  computed?); for Family B it is at chance *by construction* (the criterion is absent
  without the rule), so Family B's signal is entirely in the *with-rule* arm and *where*
  in it the comparison becomes readable (message-local = bound at reading; only
  decision-adjacent = bound at the decision).
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
   - **R2 — arbitrary conjunction of two spontaneously-computed components** (tests
     *composition*): the conjunction is not itself a trained category. Screen a small
     menu — e.g. *seeking advice AND states an explicit deadline*; *complaint AND names a
     competitor/third party*; *request AND expresses distress/anger*. Pick ≥1 that
     constructs cleanly.
   - **R3 — a compound whose decisive element comprehension can't supply unprompted.**
     This is the crux — see **Choosing the conditions** above for the two candidate
     families (world-knowledge inference / rule-supplied criterion), the menu, and the
     selection method. Run ≥2 survivors spanning both families. Do **not** anchor on the
     jurisdiction example.
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
5. **(GPU) Extraction** (`extract_ladder.py`), committed before the run. Per **selected
   condition** (R2 + the ≥2 R3 survivors) × per variant (rule-present / rule-absent):
   compound-ask passes (3 paraphrases), component-ask passes (1 each), and the
   neutral/action pass (no question — the pure-reading pass the without-rule measurement
   depends on). Exp 2 position set, fp16. **Batch all conditions into one GPU session**
   (amortise the model load) — scale grows with the number of survivors, so the screen's
   job is also to keep that number disciplined (2–3 R3, 1 R2).
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
  A-only/B-only, diff-of-means, message-local, layer-robust) × **condition** (R1, the R2
  pick, each R3 survivor — grouped by rung/family) × context (rule-present pure-reading
  vs rule-absent pure-reading). The pattern holding *across* the diverse R3 instantiations
  is itself the robustness claim; a pattern that holds for only one is an artifact flag.
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

Screening ≈ $10–25 (OpenRouter — heavier now: a battery of candidates × the probeability
and spontaneity pre-checks × prompt iterations; this is the deliberate "get the data right"
spend). Extraction: ~4 conditions (1 R2 + 2–3 R3) × 2 variants × ~6 passes × ~100–130 docs,
batched in one session — the largest GPU job of the four moves, ≈ $60–120. CPU probe free.
The screen keeping the survivor count to 2–3 R3 is what holds the GPU cost down.

---

## Appendix B — 2026-06-12: sharpened design before the build (execution agent)

Pre-build pressure-testing of the metric surfaced two corrections that change what we
build and measure. Recording them here because they are load-bearing.

**B1. The decisive read is *within-arm hit-vs-near* (A∧B vs A-only), not "compound vs the
better-separated component."** The lattice maps cleanly onto the Exp 2 keeper structure:
`hit = A∧B`, `near = A-only` (register-matched, differing *only* in the decisive element B),
`form = B-only`, `none = neither` — so `pair_stem` pairs each A∧B doc with its matched
A-only near-miss, exactly as Exp 2 paired hit with its topic-matched near. Why the change:
the four cells sit at the corners of a 2-D (feature-A, feature-B) square, and the A∧B
corner is **linearly separable from its two adjacent corners (A-only, B-only) using only a
linear combination of the two spontaneous component features** — no genuine conjunction
needed (it's only the XOR pattern that's non-separable). So "A∧B vs components" can be
passed without any binding. Holding A *fixed* and comparing A∧B vs A-only isolates B —
the one thing that distinguishes the decisive element — and is the only comparison that
can't be faked by reading a component. (form=B-only stays as the component sanity control:
B alone must read where expected.)

**B2. Keep the rule *constant within* the rule-present arm — the contrast that licenses the
claim is hit-vs-near *separability per arm*, not a cross-arm projection.** Within the
rule-present pure-reading pass, hit (£520) and near (£480) share the identical system prompt
(rule names "£500"), so their only difference is the *message* amount. hit-vs-near
separable there ⇒ the model computed "over the threshold" at reading time (the threshold
token being in context is held constant, so it can't be what's read). In the rule-absent
arm (placebo rule, no threshold) hit-vs-near should be at chance. **Headline = (hit-vs-near
separability | rule-present) − (hit-vs-near separability | rule-absent), per condition.**

**B3. Family B is the clean primary; Family A is a *contrast*, not a clean rule-conditioning
test.** Family A's decisive element ("this drug is prescription-only") is latent **lexical
knowledge** sitting in the drug-name token's representation — so a probe may read it in
*both* arms regardless of the rule (Hewitt–Liang: linear decodability ≠ the model using it).
That makes Family A's without-rule arm un-clean for "did the rule cause the computation."
Repurpose it: Family A is expected to read without the rule (latent knowledge present), and
the *contrast* with Family B (reads only with the rule) is itself the finding — "the model
has the fact, but does the rule-defined comparison only when the rule supplies the criterion."
Family B's decisive element (a threshold/cutoff that lives only in the rule) is genuinely
**absent** from context without the rule, so its without-rule arm is chance by construction —
the property we need. Build ≥2 *diverse* Family B (different criterion types: numeric
threshold, temporal cutoff) as the flagship; 1 Family A as the contrast.

**Stage 1 OUTCOME (2026-06-12) — probeability screen, all four candidates PASS.**
OpenRouter `qwen/qwen3-32b`, greedy/no-think (matches GPU), ask-only, 8 docs/cell ×
{compound k=3, compA, compB}. Final gate (after 2 iterations — see below):
`advice_deadline` (R2) near=0% cons=100%; `refund_over_500` (R3/B-numeric) near=0%
cons=94%; `complaint_6months` (R3/B-temporal) near=12% cons=94%; `medical_rx_drug`
(R3/A-worldknowledge) near=0% cons=100%. hit-detect=100% and both components ≥94%
everywhere. Selected **all four** (1 R2 + 3 diverse R3 spanning both families) for the
keeper build. **Iteration lesson (a result about the probeability boundary):** round 1's
failures were *not* the model failing the threshold — they were (i) loose compound
questions that let the model collapse the conjunction onto whichever single component the
phrasing emphasised (fixed by explicit "Answer YES only if BOTH X AND Y, otherwise NO"
paraphrases that foreground the boundary case, e.g. "if the amount is £500 or less, answer
NO"), and (ii) a few items with hidden arithmetic/duration ambiguity ("charged twice…
£470", "began five months ago and I should have raised it sooner") that the model read as
larger/longer. Numeric and temporal thresholds *are* probeable no-think, but sit closer to
the reliability edge than the categorical Rx/OTC distinction (Family A was clean from
round 1) — itself a small finding for the playbook's boundary map. Files:
`make_ladder_screen.py`, `run_ladder_screen.sh`, `observe_ladder_screen.py`,
`inspect_ladder_detail.py`; throwaway datasets `inputs/ladder_screen_*`.

**B4. Family B's magnitude/recency confound (the near-criterion design).** If A∧B amounts
are all large (£900) and A-only all small (£200), raw magnitude — which *is* spontaneously
read — leaks the over/under distinction into the without-rule arm and fakes a "computed
without rule" result. Fix: **near-criterion matching** — A∧B just over (£510–560), A-only
just under (£440–490); the over/under flips while raw magnitude barely moves. Same for dates
(relative timeframes "5 months ago" vs "7 months ago" around a 6-month cutoff — relative so
the model needn't know today's date). Tension: too-near may exceed the model's no-think
arithmetic reliability (probeability gate). The screen resolves the gap empirically; if a
usable gap also leaks magnitude, report the magnitude-probe as an explicit control rather
than widening blindly.
