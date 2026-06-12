# Move 2 — separability: can per-condition probes coexist in one prompt? (plain-language outcome)

**Run:** 2026-06-12, Qwen3-32B on an A100-80GB, deterministic greedy (T=0), no-think.
Extraction [extract_panel.py](extract_panel.py) (code `2b1fb51`, transformers 5.11.0),
probe [probe_panel.py](probe_panel.py), controls [panel_specificity.py](panel_specificity.py)
+ [panel_topic_removal.py](panel_topic_removal.py). **Full tables + reproducibility:**
[runlog.md](runlog.md) `2026-06-12` Move 2 entry. This doc is the readable explainer.

**One-paragraph summary.** The deployment vision is a **panel**: a multi-rule system prompt
with one linear probe per rule, each firing when *its* condition is met. Every probe so far
was trained and read in a *single-rule* prompt, so the load-bearing untested question was:
when two rules — and two kinds of content — share one prompt, do the per-condition directions
stay distinct, or collapse into one generic "a rule is relevant here" signal? **Answer: they
stay distinct, and a panel is buildable.** Two probes (legal-advice-seeking, medical-advice-
seeking) coexist in one prompt, each fires on its own condition's documents, neither
false-alarms on same-topic-non-seeking documents, and — the part that matters most — the
separation is **genuine recognition, not keyword/topic matching** (it survives stripping the
topic axis out of the activations). The honest bound: the two directions are *not* orthogonal —
they share a large common "advice-seeking" component — so this is "distinct, overlapping
directions," and a deployed panel must be calibrated per-condition.

---

## The setup (what's new vs Exp 2)

Same intake-clerk frame, but **one system prompt now carries BOTH standing rules** (flag legal-
advice requests *and* flag medical-advice requests, applied independently). Every pass — the
recognition "asks" and the action job — runs inside that shared multi-rule context (a panel
monitor trains where it deploys). The lattice (216 docs, [datasets.md](datasets.md) `panel_*`):

- **legal hit / medical hit** — seeks that domain's advice (the two conditions).
- **near** — register-matched twin of each hit: same topic, same words, but *reporting* an
  outcome, not *seeking* (the K2 "reads-seeking-not-topic" control).
- **both** — NEW content: 32 letters genuinely seeking legal AND medical advice at once
  (the composition test).
- **form** — advice-seeking on a neutral topic (a diagnostic for "reads generic seeking").
- **none** — neither (the blank baseline).

Each probe is trained only on the **ask** pass, on the **model's own** consistency-filtered
YES/NO answers (never on the action FLAGs — Move 1 showed those are unreliable). The **both**
cell is held out of training and scored, so composition is a generalization test.

---

## The question, and the kill-switch

A panel works only if **probe_legal fires on legal docs and not on medical docs** (and vice
versa). The clean number is **specificity = AUROC(own-condition hits vs other-condition hits)**:
0.5 = the two are on top of each other (collapsed), 1.0 = perfectly distinct. And because legal
and medical differ in *topic* (vocabulary) as well as condition, a second question follows: is
any separation **recognition** (the model's advice-seeking judgment, which no regex can do) or
just **topic** (keywords, which a regex *can* do — making the probe pointless)?

---

## What the probe shows (message_last, the clean read; layer-robust medians)

| question | legal | medical |
|---|---|---|
| recognition floor (own hits vs none) | 1.00 | 1.00 |
| **specificity (own hits vs other hits)** | **0.989** | **0.972** |
| composition (both-docs outrank the *other* condition's hits) | 0.67 | 0.84 |
| reads seeking, not topic (hit vs near) | 1.00 | 1.00 |
| near vs none (nears stay at baseline) | 0.61 | 0.47 |
| **specificity after stripping the topic axis** | **0.962** | **0.954** |

**The directions are distinct (specificity ~0.97–0.99).** Projection layout on the legal
direction: legal hits **+1449** ≫ both-docs **+789** > medical hits **+640** ≫ none **−830** ≈
legal nears **−825**. So the other condition's seekers are *elevated above baseline* (a shared
seeking component) but sit *far below* the own condition's seekers (so a threshold separates
them cleanly). The nears sit right at the baseline — the probe does **not** fire on legal topic
without seeking.

**The separation is genuine recognition, not keywords.** This is the control that matters most.
We derived the pure-topic axis from the nears (which differ from each other *only* in topic),
projected it out of the activations, and re-measured. The topic control collapses to chance
(0.55→0.50 for legal) but **specificity barely moves** (legal 0.974→0.962, medical 0.970→0.954).
Aggressive rank-2 removal (adding a logistic topic axis) gives the same answer (0.958 / 0.954).
The clincher: legal (topic fully removed) and medical (topic only partly removable) land at the
**same ~0.95** — so that 0.95 cannot be topic-driven; it is recognition. **The panel reads the
model's advice-seeking judgment, the thing a keyword filter cannot.**

**Composition holds.** Both-docs fire on each probe and outrank the *other* condition's hits
(legal +789 > medical-hit +640), so the legal component in a both-doc genuinely lifts it on the
legal probe — diluted (below pure legal +1449), but real.

**Why you can trust it (controls).** Shuffle-labels ~0.5; negative-control position
(`pre_message_final`, which can't have read the message) recognition 0.500; layer-0 ≈ chance.
No leakage. Results reproduce exactly from the committed code (verified on the box, 4 decimals).

---

## The honest bounds

- **Distinct but not orthogonal.** The two directions share a large common advice-seeking
  component (geometry: pure cosine **0.87**). The panel works because the condition-specific
  residual cleanly separates them — but in deployment a cross-condition document scores *above
  the blank baseline*, so each probe must be calibrated with its own positive examples
  (threshold between own- and other-condition level), not against a blank.
- **Position matters.** The clean result is at `message_last`. At `message_mean`/`final` topic
  leaks in (the topic control hits ~1.0); the recognition signal is recoverable there under
  topic-removal at the message-mean read, weaker at `final` (the decision-adjacent, most
  contaminated position).
- **A deliberately hard pair.** Legal and medical advice are *semantically close*; we chose them
  on purpose as a stress test. More distant rules (e.g. PII vs cancellation) should separate
  *more* easily, so 0.95+ here is a strong floor, not a ceiling.
- **The pre-registered metric mis-fired.** Our registered kill-switch (crossfire = other-hits
  vs *none*) returned "collapsed" — but it was mis-specified (it only asks whether other-hits
  rise above the blank baseline, which is true even when they sit far below own-hits). The
  direct specificity metric is the correct operationalization; the crossfire verdict stays in
  the record as scored, superseded by specificity + topic-removal, all three reported.

---

## Bottom line

- **A per-condition probe panel is buildable** — two recognition directions coexist in one
  multi-rule prompt, stay specific (0.97–0.99), and compose on mixed documents.
- **The separation is genuine recognition, not keyword/topic** — it survives stripping topic
  from the activations, so the panel does the no-regex thing a keyword filter cannot.
- **With one real caveat:** the directions overlap heavily (shared advice-seeking component),
  so this is "distinct overlapping directions, calibrate per-condition," not "orthogonal axes."
- **Feeds Move 3:** the playbook is a *panel* recipe. A natural strengthener (future): repeat
  with a **topic-matched** condition pair (two conditions on the same topic) to demonstrate
  recognition-separability with no topic to remove at all.
