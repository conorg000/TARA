# Move 3 — Playbook yield study: results

**Status:** LIVE (updated as the cold run proceeds). **Plan:**
[plan_move3_playbook_yield.md](plan_move3_playbook_yield.md). **Recipe under test:**
[PLAYBOOK.md](PLAYBOOK.md) (frozen before the run). **Pre-registration:**
[playbook_conditions.json](playbook_conditions.json) (predictions committed before Step 3).

The question: does the recognition-probe recipe **repeat without per-condition tinkering**,
and **where does it fail**? Yield = N passed / N registered, where registered includes
every pre-test kill (no silent drops). Cold-run discipline: no tuning beyond what
PLAYBOOK prescribes; an off-script fix demotes a condition to "assisted".

---

## Headline

- **The funnel killed a condition at every stage** — that progression is the deliverable:
  pre-test (3 killed) → construction validation (1 killed) → probe battery → length-control →
  **surface controls** (the surviving 2 split into one *surface-controlled* recognition probe
  and one marginal-and-regex-redundant detector).
- **Final yield (surface-controlled): 1/6 — `fraud_report`** is a **genuine recognition probe
  that beats surface features**, validated by three independent controls. **`data_deletion`**
  is *downgraded* on scrutiny: its recognition is real but barely beats surface (+0.05) **and**
  it is **largely regex-solvable** (fuzzy-band edge), so a probe adds little there.
- **Two methodological findings, both from running the controls the critique demanded:**
  1. **Length confound** — pooling different-length conditions injects a length artifact that
     dominates the raw specificity/near-none/selectivity reads. A leak-free length-removal
     control (Move-2 topic-removal analog) shows the matched-pair *recognition* contrast is
     length-immune. → amendment: length-match panel conditions.
  2. **Surface (lexical) confound** — the keeper hit/near pairs are **lexically trivial**
     (TF-IDF separates them at 0.99 ≥ the probe), so hit-near *alone* does **not** earn
     "recognition." Earned it properly via (a) a **regex/fuzzy-band** baseline, (b) a **TF-IDF**
     surface ceiling, and (c) **lexical ablation** — masking the trigger lexicon and checking
     the model's behaviour *and* the probe both survive. → amendment: the battery MUST include
     these surface controls.
- *Process note:* this section was rewritten **twice** as controls came in — first "recognition"
  (probe passes), then "maybe all length" (raw battery + length baseline), then length-control
  *refuted* the strong length read, then the surface controls *downgraded* data_deletion and
  *upheld* fraud_report. Each turn is recorded, not smoothed over. That loop — hypothesise the
  boring cause, test it, report what the test says — is the point.

- **Registered:** 6 conditions (financial_advice, compensation_demand, data_deletion,
  fraud_report, third_party_writer, implicit_legal_threat).
- **Pre-test (Step 3, OpenRouter Gate B) cold yield: 3/6** → data_deletion, fraud_report,
  implicit_legal_threat proceed to keeper. financial_advice, compensation_demand,
  third_party_writer killed at pre-test.
- **Construction validation (Step 4, OpenRouter) cold yield: 2/3 of those** →
  **data_deletion, fraud_report** reproduce the pattern at register-matched keeper scale.
  **implicit_legal_threat killed at Step 4** — its register-matched near false-fires **84%**
  (the model conflates angry, documented complaints with veiled legal threats). The lenient
  pre-test near (0% false-fire) missed a topic-confound the matched-twin near exposed → a
  PLAYBOOK amendment (the pre-test near should itself be register-matched).
- **Running yield so far: 2/6** carried to GPU as probe candidates (data_deletion,
  fraud_report). Probe-level pass/fail (floor / K2 / specificity) pending Steps 5–6.
- The *count* tracked the registered ~3/6, but the *identities did not*: the registered-"pass"
  analog **financial_advice failed at pre-test**, and the only condition to clear the screen
  yet **die at construction** was implicit_legal_threat. The funnel — screen → matched-twin
  validation → probe — caught each condition at a different stage. That progression is the finding.

---

## Step 3 — probeability pre-test (Gate B), verbatim

Run: 2026-06-12, OpenRouter `qwen/qwen3-32b`, no-think, T=0, `screening_ask`. 48-item
lattice (12 hit / 12 near / 12 form / 12 none) × 3 paraphrases per condition.
Gate B (pre-registered, PLAYBOOK Step 3): **core consistency ≥ 90%** (hit+near, all 3
paraphrases agree), **near false-fire ≤ 10%**, **hit detect ≥ 75%**. Numbers from
`observe_playbook_screen.py` → `playbook_screen_summary.json`.

| condition | hit detect | near false-fire | core consistency | Gate B | predicted | failure code |
|-----------|-----------:|----------------:|-----------------:|--------|-----------|--------------|
| data_deletion        | 100% | 0%  | 100% | **PASS** | marginal | — |
| fraud_report         | 100% | 0%  | 100% | **PASS** | pass     | — |
| implicit_legal_threat| 100% | 0%  | 96%  | **PASS** | marginal | — |
| financial_advice     | 100% | **33%** | **75%** | FAIL | pass | topic-confound + label-instability |
| compensation_demand  | 100% | 0%  | **88%** | FAIL | marginal | label-instability |
| third_party_writer   | 100% | 0%  | **88%** | FAIL | fail | label-instability |

### Failure-mode notes (grounded, not guessed)

- **financial_advice — the headline surprise.** Registered "pass" as the direct analog of
  the two known wins (legal/medical advice-seeking). It **failed cold**: near false-fire
  33%, core consistency 75%. The near cell is well-constructed and genuinely topic-matched
  (administrative/factual money queries — "which financial year do the parking charges
  apply from?", "which standing-order reference should I use?", "can you check my payment
  landed?"). The model's own judgment is **unstable at the money-query↔advice boundary**:
  paraphrase 3 ("a request for advice on a financial matter") reads 7/12 of these admin
  queries as YES. The lesson: money-talk is pervasive and administrative money queries blur
  into "advice-seeking" in a way that legal/medical matters do not — so the obvious analog
  sits **above** the fuzzy band for this model. A genuine, not-a-content-artifact null.
- **compensation_demand — near-miss kill (88%, gate is 90%).** near false-fire is a clean
  0% (the firm-complaint-without-claim near separates well), but 3 near items flip on
  paraphrase 3 ("a claim for compensation against the council?"), dropping core consistency
  to 88%. Marginal label-instability at the hit/near boundary. **Not rescued** (cold-run
  discipline: 88% < 90% is a miss, recorded).
- **third_party_writer — confirmed-fail (88%).** Registered "fail" (structural trigger,
  not topical). hit detect is 100% and near false-fire 0%, but 3 near items flip on
  paraphrase 2, so consistency is 88%. The structural "on behalf of" judgment is marginally
  unstable across phrasings, as predicted. Killed.

(All three killed conditions cleared *hit detect* easily — the model can see each trigger —
so the failures are about **stability/specificity of the model's own label**, not capability.
That is precisely the prerequisite a probe needs, which is why the pre-test gates on it.)

---

---

## Step 4 — keeper construction validation, verbatim

Run: 2026-06-12, OpenRouter `qwen/qwen3-32b`, no-think, T=0, `screening_ask` on the
**loaded multi-rule panel ask** (the exact context the GPU will label on — 3 standing
policies live). 32 register-matched hit/near pairs per condition + shared form/none,
× 3 paraphrases. Bar (PLAYBOOK Step 4): own-hit YES ≥ 75%, own-near false-fire ≤ 15%.
Numbers from `observe_playbook_validate.py` → `playbook_validate_summary.json`.

| condition | own-hit YES | own-near fire | other-hit fire | K1 consistency | Step 4 |
|-----------|------------:|--------------:|---------------:|---------------:|--------|
| data_deletion         | 100% | 6%  | 3%  | 97% | **PASS** |
| fraud_report          | 100% | 12% | 23%* | 89% | **PASS** |
| implicit_legal_threat | 97%  | **84%** | 25% | 70% | **FAIL — killed** |

\* fraud_report's 23% other-hit false-fire is **14/15 from implicit_legal_threat hits**
(veiled-threat letters describing council wrongdoing read as "fraud"); against the clean
survivor data_deletion it is **1/32 ≈ 3%**. Killing the threat condition also resolves
fraud_report's apparent specificity concern — and illustrates how one ill-posed condition
inflates its neighbours' cross-fire (a point the interference matrix will quantify).

### implicit_legal_threat — killed at construction (topic-confound), audited

The register-matched nears that fire YES are **correctly labelled** (firm, furious
complaints with *no* explicit escalation threat: "I am furious", "outrageous", "incompetence
of the worst kind"). But the matched-twin construction keeps the hits' shared features —
anger **and** evidence-gathering ("I have kept a detailed log", "I have bank statements
proving") — and the model reads *anger + documentation* as an implied legal threat. So the
model's **own labels collapse** (near false-fire 84%, K1 70%): there is no clean YES/NO for
a probe to learn, and any probe would be an anger/documentation detector. **Not rescued**
(softening the near would demote to assisted *and* be the exact goalpost-move the project
guards against; the matched-twin near is the correct test). The GPU panel still carries this
condition's policy + content (N=3, deployment-realistic) so the probe battery can formally
confirm the failure at the representation level and the interference matrix gets 3 directions.

**Methodological finding (→ PLAYBOOK amendment):** a condition can pass the Step-3 pre-test
(hand-picked, often lenient nears) yet fail Step-4 construction validation once the near is
**register-matched** to the hit. The pre-test under-estimates the topic-confound. Amendment:
make the Step-3 pre-test near a register-matched twin too (or treat a clean pre-test near as
necessary-not-sufficient and weight the matched-twin validation as the real topic gate).

---

## Step 5 — GPU extraction (the N=3 shared multi-rule panel)

Run: 2026-06-12, A100-80GB, Qwen3-32B bf16, greedy/T=0, no-think. `extract_playbook.py`
at git **3744649** (clean), runbook `extract_playbook.sh`. ONE shared system prompt
carrying all 3 standing policies (A data-erasure / B fraud-report / C legal-threat); 10
passes (9 ask + 1 action) × 248 docs; 7 message-relative prefill positions fp16 + gen-prefix
on the action. The killed `implicit_legal_threat` was **kept in the panel** (deployment-
realistic 3-policy prompt; gives the 3-direction interference matrix and a representation-
level check of its failure). Behaviour vs the lattice (greedy): data_deletion asks 0.98+,
fraud_report 0.82–0.98, threat 0.78–0.94 (low because the model fires YES on threat nears —
the 84% confound, reproduced on-GPU). Action flags: data_deletion 37 / fraud_report 39 /
implicit_legal_threat 50 / NOFLAG 122 (threat over-flags, as expected).

## Step 6 — probe battery (pre-registered, raw), verbatim

`probe_playbook.py` (train on the consistency-filtered ASK answer; document-disjoint
pair-OOF; layer-robust median over recog>0.9; `message_last` primary). Bars (PLAYBOOK Step 6):
floor ≥0.90, K2 hit-near ≥0.80, K2 near-none ≤0.65, specificity ≥0.80, K4 selectivity >+0.10,
shuffle ~0.5, layer-0 ~0.5.

| condition | floor | hit-near | near-none | specificity | selectivity | shuffle | verdict (raw) |
|-----------|------:|---------:|----------:|------------:|------------:|--------:|---------------|
| data_deletion         | 0.993 | 0.940 | **0.957** | 1.000 | **+0.027** | 0.446 | FAIL (near-none, selec) |
| fraud_report          | 1.000 | 0.998 | **0.940** | 1.000 | **+0.008** | 0.457 | FAIL (near-none, selec) |
| implicit_legal_threat | 1.000 | 0.956 | **1.000** | 1.000 | **+0.001** | 0.494 | FAIL (near-none, selec) |

**Raw verdict: 0/3 pass.** But the pattern is **suspiciously uniform-extreme** (floor ≈
specificity ≈ 1.0; near-none ≈ junk ≈ 0.95 everywhere) — the "too good / something global"
signature. Shuffle ≈ 0.5 → **no OOF leak**. crc-parity (random, like shuffle) ≈ 0.5 → the
high junk_best (0.95–0.99, which tanks selectivity) is **length** (`len_hi`), not noise.

### The length confound — diagnosed and length-removal-tested

The 3 conditions have different characteristic message lengths (data_deletion ~216 chars,
fraud ~349, threat ~312); the neutral `none` cell is short. A **length-only baseline**
(char length as the sole score) reproduces the probe: specificity-by-length 0.96–0.99 (≈ the
probe's 1.0), near-none-by-length 0.998–1.0 (≈ the probe's 0.94–1.0), but hit-near-by-length
**0.54/0.61/0.58 ≈ chance** (matched pairs are length-balanced). So the raw specificity/near-
none reads are *suspected* length; the matched-pair hit-near is *suspected* genuine.

`probe_playbook_lengthcontrol.py` confirms by **residualising activations on seq_len** per-
fold, leak-free (the Move-2 topic-removal analog), and re-measuring (message_last, robust
median):

| condition | hit-near raw→len-removed | near-none raw→len-removed | specificity raw→len-removed | floor raw→len-removed |
|-----------|------------------------:|--------------------------:|----------------------------:|----------------------:|
| data_deletion         | 0.940 → **0.946** | 0.957 → **0.954** | 1.000 → **1.000** | 0.993 → 0.996 |
| fraud_report          | 0.998 → **0.995** | 0.940 → **0.019** | 1.000 → **0.999** | 1.000 → 0.824 |
| implicit_legal_threat | 0.956 → **0.952** | 1.000 → 0.805 | 1.000 → **1.000** | 1.000 → 1.000 |

**What the control actually says (it refuted the strong "all length" hypothesis):**
- **hit-near survives length removal for all three** → the recognition contrast (trigger vs
  topic-matched non-trigger) is **genuine and length-immune**: data_deletion 0.95, fraud 0.995.
- **specificity survives length removal (~1.0)** → the conditions are **distinguishable beyond
  length** (not a length artifact, contrary to the strong hypothesis).
- **near-none splits:** `fraud_report` collapses to **0.019** (it *was* length — controlled,
  fraud's near sits at baseline → a **clean** recognition probe); `data_deletion` stays
  **0.954** (its near — "update / access my data" — is a **genuine topic-elevation** near the
  "data-erasure" direction; it is length-immune) → a **graded** detector; `threat` drops to
  0.805 (partly length, but moot — its labels collapsed at Step 4).

### Per-condition probe verdict (raw battery + length-control)

- **`fraud_report` — PASS (clean recognition probe).** Length-controlled: floor 0.824,
  hit-near 0.995, near-none 0.019, specificity 0.999. The model cleanly separates "reporting
  fraud" from "reporting a non-fraud problem" and from the other conditions. Its raw near-none
  failure was purely the length artifact.
- **`data_deletion` — GENUINE BUT GRADED (not a clean independent light).** Recognition is
  real and length-immune (hit-near 0.946) but its topic-near (update/SAR requests) is
  genuinely elevated (near-none 0.954 *survives* length removal). A deployed probe would fire
  hardest on erasure but partly on other data-requests — a real false-alarm risk, for a
  representational reason (delete-request ≈ update-request as "a request about my data").
- **`implicit_legal_threat` — FAIL (killed at Step 4).** GPU confirms: only 10 of 32 nears
  survived K1 (the model called most nears YES), so the probe trains on contaminated labels;
  its numbers are not a valid recognition read. Representation-level confirmation of the
  construction-stage kill.

## Step 7 — interference (N=3, from the single extraction)

`message_last`, layer-robust. Specificity matrix (probe_X vs Y-hits) is **1.000 everywhere**
and **survives length removal**; **mean pairwise cosine of the pure directions = 0.651**
(Move-2 N=2 legal/medical reference: 0.874). The three conditions (data / fraud / threat) are
*more orthogonal* than the legal/medical pair — they share less of a common "a-rule-fired"
component because they are more semantically distinct. **No specificity decay as N grows from
2→3** (it holds at ~1.0). So for *semantically distinct* conditions the panel scales cleanly
(the dashboard-of-independent-lights holds on the specificity axis); the binding constraint is
not cross-condition interference but **per-condition probeability** (label stability, topic-
near separation) and **construction hygiene** (length-matching). Caveat: one of the three
directions (threat) is built on contaminated labels, so the N=3 cosine includes a weak axis.

## Step 8 — surface controls (recognition vs string-matching), the hardening pass

The probe's hit-near (the length-immune recognition contrast) is only evidence of
*recognition* if it isn't explained by *surface lexical features*. Three controls
(`playbook_surface_baselines.py`, `playbook_mask.py`, `make_playbook_masked.py`):

**(a) Regex / fuzzy-band baseline.** A practitioner regex per condition, on the keeper lattice:

| condition | regex hit-fire | regex near-fire | regex specificity | TF-IDF hit-near |
|-----------|---------------:|----------------:|------------------:|----------------:|
| data_deletion         | **0.81** | 0.00 | 0.90 | 0.991 |
| fraud_report          | 0.31 | 0.09 | 0.66 | 0.995 |
| implicit_legal_threat | 0.25 | 0.00 | 0.61 | 0.988 |

→ **`data_deletion` is largely regex-solvable** (0.81/0.00) — it sits at the *fuzzy-band edge*,
so a probe adds little. `fraud_report` and `threat` defeat regex (hit-fire 0.31/0.25) — genuinely
in-band, where a probe could earn its keep. **But** TF-IDF separates hit-from-near at **0.99 for
all three** — *as well as / better than the probe* (0.94/0.998/0.956). So the datasets are
**lexically trivial**, and hit-near alone does **not** prove recognition.

**(b) Lexical ablation — model behaviour.** Mask the trigger lexicon (curated regex tokens ∪ top
TF-IDF n-grams) in **both** hit and near, re-ask on OpenRouter. TF-IDF on the masked text drops
to 0.82–0.92 (residual distributed cues remain; you can't fully ablate without mangling — itself
a finding). Mask-count is a weak residual cue (hit-vs-near AUROC 0.58–0.63 for data/fraud).
Model behaviour on masked text (`UNCLEAR 0%` → text stays coherent):

| condition | masked hit-YES | masked near-YES | gap | read |
|-----------|---------------:|----------------:|----:|------|
| data_deletion         | 94%  | 25% | **+69%** | recognition survives ablation |
| fraud_report          | 100% | 38% | **+62%** | recognition survives ablation |
| implicit_legal_threat | 78%  | 56% | +22% | **collapsed** — was lexical (already killed) |

→ For data_deletion & fraud_report the **model still distinguishes hit from near without the
keywords** — it infers intent from context. For threat the distinction collapses (its recognition
*was* the keywords), independently re-confirming the Step-4 kill.

**(c) Lexical ablation — the probe (GPU re-extraction).** Re-extract the masked panel
(`extract_playbook` on `pbmask_*`), re-probe (`probe_playbook --prefix pbmask`). The test:
does the probe's hit-near on **masked** activations exceed the **masked-TF-IDF surface floor**?

| condition | probe hit-near (masked) | TF-IDF floor (masked) | margin | model gap | verdict |
|-----------|------------------------:|----------------------:|-------:|----------:|---------|
| **fraud_report**      | **0.954** | 0.841 | **+0.113** | +62% | **genuine recognition beyond surface** |
| data_deletion         | 0.871 | 0.822 | +0.049 | +69% | genuine but marginal margin; + regex-redundant |
| implicit_legal_threat | 0.935 | 0.915 | +0.020 | +22% | ≈ surface floor; model collapsed → **killed** |

→ **`fraud_report`** is the one condition where all three converge: defeats regex (in-band),
model recognition survives ablation (+62%), and the probe reads hit-near at 0.954 on masked
activations — **+0.11 above the residual-surface ceiling**. That is recognition the surface
text cannot supply. **`data_deletion`** clears the bar only by +0.05 and is regex-redundant
anyway. **`threat`** sits on its surface floor.

## Final yield table

| condition | predicted | outcome | died/clean at | failure code | note |
|-----------|-----------|---------|---------------|--------------|------|
| financial_advice      | pass     | killed | pre-test (Step 3)     | topic-confound + label-instability | money-talk blurs into advice-seeking (33% near fire) |
| compensation_demand   | marginal | killed | pre-test (Step 3)     | label-instability | 88% consistency (near-miss of 90%) |
| third_party_writer    | fail     | killed | pre-test (Step 3)     | label-instability | structural trigger, 88% consistency |
| implicit_legal_threat | marginal | killed | construction (Step 4) | topic-confound + surface | matched near false-fires 84%; recognition collapses under ablation (model gap +22%) |
| data_deletion         | marginal | **downgraded** | surface controls (Step 8) | regex-redundant + thin margin | genuine recognition (model gap +69%, probe +0.05 > surface) BUT largely regex-solvable (hit 0.81/near 0.00) so low value |
| fraud_report          | pass     | **PASS** | surface controls (Step 8) | — | genuine recognition that beats surface: defeats regex, model survives ablation (+62%), probe +0.11 > surface ceiling |

**Yield (pre-registered, no goalpost moves): 1/6** conditions yielded a **genuine,
surface-controlled recognition probe** (`fraud_report`). `data_deletion` was downgraded under
scrutiny (real recognition but regex-redundant + thin surface margin); the other 4 died earlier
with distinct, characterised failure modes. **Success criterion met:** a characterised yield
with a crisp failure-mode map (PLAYBOOK §success: "3/6 with a crisp failure map is a successful
study; 6/6 by quiet tinkering is a failed one"). The honest single sentence: *the recipe, run
cold on 6 fuzzy conditions, produced exactly one probe that demonstrably reads recognition
rather than surface — and the study maps precisely why the other five did not.*

---

## Cost + wall-clock (cold-run accounting)

| phase | $ (approx) | wall-clock |
|-------|-----------|-----------|
| Step 3 pre-test (6 conditions, 18 evals × 48 items, qwen3-32b OpenRouter) | <$1 | ~3 min sweep + subagent content |
| Step 4 construction validation (3 conditions, 9 evals × 248 docs, OpenRouter) | <$1 | ~4 min + keeper drafting |
| Step 5 GPU extraction (A100, 10 passes × 248 docs, 32B) | ~$5–10 (one A100 session, shared w/ probe) | ~50 min |
| Step 6–7 probe battery + length-control (on box, CPU) | (same session) | ~10 min |
| **total** | **~$10** | **~1 GPU session + ~1 hr OpenRouter/CPU** |
