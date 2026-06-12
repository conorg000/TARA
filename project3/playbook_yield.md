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

## Headline (in progress)

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

## Cost + wall-clock (cold-run accounting)

| phase | $ (approx) | wall-clock |
|-------|-----------|-----------|
| Step 3 pre-test (6 conditions × 18 evals × 48 items, qwen3-32b OpenRouter) | <$1 | ~3 min sweep + content drafting |

(Keeper build, validation, GPU extraction, battery costs appended as they run.)
