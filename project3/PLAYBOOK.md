# PLAYBOOK.md — the recognition-probe recipe

**Dated:** 2026-06-12. **Status:** FROZEN at start of the Move-3 cold runs (commit it
before running anything; amendments are logged in §Amendments with a date and reason).
**What this is:** the step-by-step recipe for building a deployment-grade *recognition
probe* for a fuzzy conditional trigger — distilled from the Exp 2 chain (Screen B →
construction validation → keeper → extraction → battery) and the Move 2 panel result.
**Why it exists:** Move 3 runs this recipe **cold** on fresh conditions to measure its
*yield* (how often it works without per-condition tinkering) and its *failure modes*.
A step taken off-script demotes that condition to "assisted" (see §Cold-run discipline).

This is a checklist, not a tutorial. Each step has: a one-line goal, the reference
implementation to imitate (don't edit the references), the artifact it produces, and a
**pass/fail bar**. If a step's bar is missed, the condition is **killed** at that step
and that fact is the finding — record it, do not redesign.

---

## What "works" means (the target)

A condition *passes* if, in the shared multi-rule panel, a linear probe trained on the
model's own consistency-filtered YES/NO answer reads the recognition **specifically**:
it fires on that condition's hits, stays quiet on the topic-matched near (no topic
detector), stays quiet on other conditions' hits (specificity), and survives the junk-
label / shuffle controls. The headline per-condition number is **AUROC(own-hit vs
own-near)** (the K2 topic control) and **AUROC(own-hit vs other-hit)** (specificity),
layer-robust median at `message_last`. (Move 2 anchors: legal/medical hit-vs-near and
specificity both landed ~0.97–0.99 and survived topic-removal.)

---

## The fuzzy band (condition-selection criterion)

A condition is a legitimate candidate only if it sits in the **fuzzy band**: *no regex
reliably catches it, but the model judges it crisply.* This is **measured, not assumed**
— by the Step-3 pre-test, not by eyeballing.
- **Below the band** (a string match would win, e.g. "the literal word *cancel*"): not
  interesting — a regex already solves it. Note it and drop it.
- **Above the band** (vague topic, model's own judgment unstable across paraphrases):
  no stable label exists, so there is nothing to probe. The pre-test consistency gate
  catches this. Screen B's failures are the calibration points for "too vague":
  override_attempt 88% near-fire, cancel_intent 83%/17% consistency.
- **In the band** (model answers crisply and consistently, but the trigger is semantic,
  not lexical): the target. legal/medical advice-seeking are the two known in-band wins.

---

## The steps

### Step 1 — Define the condition + its near confusable
**Goal:** state the trigger as a one-sentence policy and, critically, name the
**near-miss cell** — same *topic*, no *trigger* — that a topic-detector would false-fire
on. The near is the load-bearing design move; a condition without a sharp near is
under-specified.
- **Reference:** the cell taxonomy in `make_screen_b.py` (hit = topic ∧ form; near =
  topic ∧ ¬form; form = ¬topic ∧ form; none = ¬topic ∧ ¬form).
- **Artifact:** an entry in `playbook_conditions.json` (policy text, the YES/NO question
  + 2 paraphrases, the near definition, the FLAG line for the action pass).
- **Bar:** the near must be *topic-matched* (a probe firing on it is reading topic, not
  recognition) — if you cannot write a near that shares the topic but not the trigger,
  the condition is mis-specified; kill it here.

### Step 2 — Register predictions (before any run)
**Goal:** A6-style, write each condition's predicted outcome (pass / marginal / fail) and
its single biggest risk, so finalists can't be retrofitted.
- **Artifact:** `predictions` block in `playbook_conditions.json`, committed before Step 3.
- **Bar:** none (this is the pre-registration itself). The yield denominator = every
  condition registered here, including those killed in pre-test.

### Step 3 — Probeability pre-test (OpenRouter, blast freely)
**Goal:** measure whether the model's *own direct answer* is stable and topic-discriminating,
cheaply, before spending GPU. This is the Gate-B screen.
- **Reference:** `make_screen_b.py` (48-item lattice: 12 hit / 12 near / 12 form / 12 none;
  3 question paraphrases) + `observe_screen_b.py` (consistency / false-fire table).
  Task `inspect_gate.py@screening_ask` on `openrouter/qwen/qwen3-32b`, no-think, T=0.
- **Artifact:** `inputs/playbook_screen_<cond>_p{1,2,3}.json`, logs, observe table.
- **Bar (Gate B, pre-registered):**
  - core consistency (hit+near, all 3 paraphrases agree) **≥ 90%**
  - near false-fire (majority-YES on near cell) **≤ 10%**
  - hit detect (majority-YES on hit cell) **≥ 75%** (a condition the model can't see at
    all is dead regardless of consistency)
- **A pre-test kill counts in the yield denominator.** Record and move on. **No redesign
  rounds in cold mode** — a content tweak to rescue a failing screen demotes to "assisted".

### Step 4 — Register-matched keeper build + construction validation
**Goal:** build the measurement dataset for survivors: ~32 hit/near **matched pairs**
(hit and its near differ only in trigger, not topic/register/length) + form + none,
then behaviourally validate that the model actually answers as the lattice assumes.
- **Reference:** `make_exp2_validate.py` (register-matched near twins — the load-bearing
  move) → `make_exp2_keeper.py` (subagent-drafted content, hand-audited). Content is
  subagent-drafted then **hand-audited for decorrelation** (trigger ⊥ topic/length/name).
- **Artifact:** `playbook_content_<cond>.json` (32 hit + 32 near pairs, form, none) and
  the validation log.
- **Bar:** behavioural validation must reproduce the pre-test pattern at keeper scale
  (hit YES-rate ≥ 75%, near false-fire ≤ ~15% on the matched pairs). Allowed fix:
  **drop** an individual failed item. Anything more than dropping (rewriting to rescue)
  demotes the condition to "assisted".

### Step 5 — GPU extraction in the shared multi-rule panel
**Goal:** extract activations for ALL surviving conditions in **ONE shared multi-rule
system prompt** carrying every condition's standing policy — the deployment-realistic
setup, and the setup that harvests the N>2 interference curve for free.
- **Reference:** `make_panel.py` (the shared `SYSTEM_PANEL` with N independent policies;
  loaded-ask template; decorrelated lattice) + `extract_panel.py` (7 message-relative
  prefill positions, fp16, gen-prefix on the action pass). Scaled from N=2 to N=survivors.
- **Artifact:** `inputs/playbook_ask_<cond>_p{1,2,3}.json` (loaded ask, one per condition×
  paraphrase), `inputs/playbook_action.json` (one multi-rule triage job), and the `.npz`
  activations on the box.
- **Bar:** none here — extraction is plumbing. **Commit the code before the run** so the
  run's git SHA is clean (CLAUDE.md convention). Lattice must keep each condition's
  presence decorrelated from the others (so the interference curve is recoverable) — same
  both-cell-excluded training discipline as `probe_panel.py`.

### Step 6 — Probe + kill battery (per condition)
**Goal:** for each condition, train the recognition direction on the consistency-filtered
ASK answer (cross-pass firewall: never use action FLAGs as labels) and run the controls
that would break it.
- **Reference:** `probe_exp2.py` / `probe_panel.py` (K1 consistency filter, paraphrase
  rotation, document-disjoint pair-OOF, diff-of-means lead + logreg upper bound).
- **Artifact:** `probe_playbook.json` — per condition: recognition floor (in-pass AUROC),
  K1 drop rate, **K2** (hit-vs-near + near-vs-none), **specificity** (own-hit vs each
  other-hit), **K4** junk-label selectivity, **shuffle** (→0.5), **layer-0** (→0.5).
- **Bars (per condition, layer-robust median at `message_last`):**
  - recognition floor (own-hit vs none) **≥ 0.90**
  - K2 topic control (own-hit vs own-near) **≥ 0.80** — *the* kill-switch; below this the
    probe is a topic detector, not a recognition probe
  - specificity (own-hit vs other-hit) **≥ 0.80**
  - K4 junk selectivity: real − junk **> 0.25** (junk decodable ≈ over-powered probe)
  - shuffle ≈ 0.5 and layer-0 ≈ 0.5 (else pipeline leak)
- A condition that misses K2 or specificity is **killed**, and *which* control killed it
  is the failure-mode classification. (K3 rule-swap is NOT in this battery — it's Move 4.)

### Step 7 — Interference curve (free, from the single extraction)
**Goal:** the headline Move-3 deliverable beyond yield. As the competitor set grows
k = 2…N, measure: (a) per-condition specificity against the growing set of other-hits,
(b) cross-fire, (c) **mean pairwise cosine** of the N recognition directions. Does
specificity decay as conditions are added? Does mean cosine rise toward 1 (the shared
"a-rule-fired" component dominating)?
- **Artifact:** `playbook_interference.json` + a curve in `playbook_yield.md`.
- **Read:** if specificity holds flat to N=survivors, the panel scales and the
  "dashboard of independent lights" story holds. If it decays, the **decay rate** and the
  N at which **argmax-over-probes beats per-probe fixed thresholds** is itself the finding.

### Step 8 — Calibration note (relative readout)
**Goal:** specify, per Move 2's lesson, that cross-condition docs sit *above* the blank
baseline, so a probe must be thresholded against its **own positives and the other
conditions' docs**, and once N is moderate an **argmax / relative-rank** read is preferred
over independent fixed thresholds. State explicitly the N at which a fixed-threshold
"independent light" stops working (read off the interference curve).
- **Artifact:** the calibration section of `playbook_yield.md`.

---

## Cold-run discipline (the load-bearing commitment)

- **No tuning beyond what this PLAYBOOK prescribes.** The only sanctioned per-condition
  fixes are: dropping an individual failed keeper item (Step 4), nothing else.
- An off-script fix is *allowed* but **demotes that condition to "assisted"** in the yield
  table. The headline yield is the **cold** yield.
- **Yield = N passed / N registered**, where registered includes every pre-test kill. No
  silent drops, ever.
- Success = a **characterised** yield with a crisp failure-mode map, not a perfect score.
  6/6 by quiet tinkering is a failed study; 3/6 with a clean map of why the other 3 died
  is a successful one.

## Failure-mode taxonomy (for the yield table)

| code | meaning | caught by |
|------|---------|-----------|
| `label-instability` | model's own answer not stable across paraphrases | Step 3 consistency / Step 6 K1 |
| `topic-confound` | probe fires on the topic-matched near | Step 6 K2 |
| `not-detected` | model can't see its own trigger | Step 3 hit-detect |
| `below-band` | a regex would catch it (lexical, not semantic) | Step 1 / inspection |
| `junk-decodable` | junk labels decodable → probe over-powered | Step 6 K4 |
| `construction-fault` | keeper build couldn't decorrelate trigger from topic | Step 4 audit |
| `interference` | specificity decays once in the multi-rule panel | Step 6 specificity / Step 7 |

## Amendments

*(Log every deviation here with date + reason. Empty at freeze.)*
- **2026-06-12 — Step 3 pre-test near should be register-matched (discovered cold).**
  `implicit_legal_threat` passed the Step-3 pre-test (near false-fire 0% on hand-picked
  nears) but failed Step-4 construction validation (register-matched near false-fire 84% —
  the model conflates angry, documented complaints with veiled legal threats). The lenient
  pre-test near under-estimated the topic-confound. **Amendment:** treat a clean Step-3 near
  as *necessary, not sufficient*; the load-bearing topic gate is the Step-4 register-matched
  near. Where feasible, build the Step-3 near as a matched twin too, so the confound is
  caught before keeper spend. (This did not change any run; it is a recipe improvement.)
- **2026-06-12 — length-match conditions in a panel (Step 5/6, discovered cold).** Pooling
  conditions with different *characteristic message lengths* into one shared panel
  (data_deletion ~216 chars, fraud_report ~349, threat ~312; neutral `none` short) injects a
  **length confound** that dominates the raw per-condition **specificity, near-none, and K4
  selectivity** reads (length-only baseline reproduced them at 0.96–1.0; a leak-free length-
  removal control showed specificity *survives* but fraud's near-none was *entirely* length).
  The matched-pair **hit-vs-near** contrast is length-immune by construction and unaffected.
  **Amendment to Step 5/6:** (a) length-match conditions when building the shared lattice
  (and match the form/none cells to the hit/near length distribution), OR (b) always run
  Step 6 with seq_len residualised out (`probe_playbook_lengthcontrol.py`) and treat *that*
  as the verdict, not the raw battery. The matched-pair hit-near is the load-bearing
  recognition metric in all cases (the only read immune to this confound).
- **2026-06-12 — surface controls are MANDATORY, not optional (Step 6, discovered cold).**
  The probe's matched-pair hit-near is length-immune but **not surface-immune**: the keeper
  hit/near pairs were **lexically trivial** (TF-IDF separated them at 0.99 ≥ the probe), so a
  high hit-near did **not** by itself earn "recognition" — surface words alone explained it.
  The recipe must therefore add, as a required part of Step 6: (a) a **regex / fuzzy-band
  baseline** (`playbook_surface_baselines.py`) — if a regex already solves the condition it
  was below the band and the probe is moot; (b) a **TF-IDF surface ceiling** — the probe's
  hit-near must be read *relative to* it; (c) a **lexical-ablation control**
  (`playbook_mask.py` + re-extract): mask the trigger lexicon and require BOTH the model's
  behaviour AND the probe's hit-near to survive above the residual-surface floor. Only a
  condition that passes all three is a genuine recognition probe (here: `fraud_report` did;
  `data_deletion` did not — regex-redundant + thin margin). **Build implication:** prefer
  **lexically-matched** nears (near reuses the hit's trigger vocabulary in a non-triggering
  construction) so hit-near is not lexically trivial in the first place.
