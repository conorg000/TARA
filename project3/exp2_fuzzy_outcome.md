# Experiment 2 — the fuzzy climb: reading "is this seeking advice?" (plain-language outcome)

**Run:** 2026-06-12, Qwen3-32B on a fresh A100-80GB, deterministic greedy (T=0), no-think.
Extraction [extract_exp2.py](extract_exp2.py) (`3c9110c`), analysis [probe_exp2.py](probe_exp2.py)
(`5135fa8`), fp16 activations, 7 message-relative read positions. **Full tables +
reproducibility:** [runlog.md](runlog.md) `2026-06-12` Experiment 2 entry. This doc is the
readable explainer.

**One-paragraph summary.** The keyphrase task (Experiments earlier in this project) used a
*crisp* trigger — a watchlist name either appears or it doesn't, so "did the model recognise
it" has a clean string-match ground truth. Experiment 2 climbs to a **fuzzy** trigger where no
regex exists: *"is this message from someone seeking legal (or medical) advice?"* The question
was whether a linear probe can read the model's registration of such a loosely-defined
condition — and, crucially, read it as a registration **against the prompt's specific rule**,
not just as a trained-in "is this advice" detector. **The answer is split, and honest: the
probe reads the fuzzy condition cleanly and genuinely — it tracks advice-*seeking*, not merely
the topic, and it isn't generic decodability — but it does NOT flip when we swap the prompt's
rule.** A document that seeks legal advice reads as "legal-advice-seeking" whether the model's
active rule asks about legal advice or about medical advice. So the recognition is real and
content-meaningful, but it behaves like a **content detector, not a per-prompt registration**.
That fails the experiment's load-bearing novelty control (K3), so the climb stops here — which
is the result, reported as-is.

---

## The setup (what's new versus the keyphrase work)

Same intake-clerk frame, fuzzy trigger. A member of the public writes to a council
correspondence desk; the model judges whether the writer is **seeking advice** in a domain.
Two conditions, each other's swap partner: **legal** and **medical**.

The dataset is built around two controls that the keyphrase task didn't need:

- **Register-matched `near` items (the topic control).** For every `hit` (someone seeking
  legal advice — *"my landlord kept my deposit, what are my options?"*) there is a `near` twin
  matched on person, topic, situation, tense, and even vocabulary, differing only in that the
  writer is **reporting/sharing, not asking** (*"my landlord tried to keep my deposit, but the
  deposit scheme sided with me — sharing in case it helps"*). If the probe separates hit from
  near, it's reading advice-*seeking*, not the legal topic or legal words. (This was validated
  behaviourally before the GPU run: the model itself says NO to these near items.)
- **The rule-swap (the novelty control).** Every document is run under **both** the legal rule
  and the medical rule. A legal-advice document satisfies the legal rule but not the medical
  one. So the *same text* should read as "satisfied" under one rule and "not satisfied" under
  the other — **if** the model's representation is conditioned on the prompt's rule. Only a
  prompt-conditioned computation can flip; a trained-in legal detector can't.

**Labels are the model's own answers.** We never use an outside "ground truth" for what counts
as advice-seeking (the old category track died on contestable labels). We ask the model
directly under 3 paraphrases and keep only items where all 3 agree (the consistency filter).
Drop rate: **6% legal, 7% medical** — the labels are stable.

**What the model does behaviourally** (greedy): it answers the ask sensibly (≈32 YES per
condition, the 32 true hits, bracketed by a strict/loose paraphrase spread). When *acting*
under the rule it over-applies the flag — legal flags 56/184, medical 63/184 against 32 true
hits — i.e. it's liberal with the flag in the action framing. (A behavioural note; the probe
trains on the ask pass, not these flags.)

**Greedy footing for the behavioural rule-flip (added 2026-06-12, Move 1 cross-tab — runlog).**
The rule-swap's *behavioural* premise — the model's ask answers flip with the active rule — now
has a full-set, at-home, deterministic-greedy record (it previously rested on coarse OpenRouter
majority, 0/8). On the keeper hits: legal hits answer the **legal** question YES but the
**medical** question YES only **0/32**; medical hits answer **medical** YES but **legal** YES
**1/32**. So when *asked*, recognition is cleanly rule-specific — which is exactly what makes
the activation-level K3 null (the recognition direction does *not* flip) the interesting result
rather than a triviality. *Denominator note to avoid confusion:* the "capability 100%" figure
elsewhere is coarse cross-paraphrase **majority** YES on own-question hits (pre-K1); the
"own-question YES 26/32 = 81%" here is greedy, **per-paraphrase p1**, pre-K1 — different
aggregation, not a discrepancy. The cross-tab also confirms (greedy, per-document) that *flagging*
is strongly rule-dependent — matching-rule 100% vs swapped-rule 31% — with the 31% leakage being
domain-general advice-seeking firing under whichever rule's label is active, not a rule-aware
flag (see the Move 1 runlog entry).

---

## The four cells

- **hit** — seeks advice in its domain (label 1). ~27 legal / ~26 medical after the filter.
- **near** — same topic, same register, **not** seeking (the topic control).
- **form** — a request, but on a neutral topic (gardening, tech). The request-shape control.
- **none** — neither topic nor request. The blank baseline.

The probe is trained only on the **ask** pass (the model's own YES/NO), then read across
positions and pointed at the **action** pass for the transfer and rule-swap tests. A probe
trained where there is no action to predict can't be reading "about to flag."

---

## Where we read it (camera angles)

A fuzzy condition has **no crisp trigger token** (unlike the keyphrase name), so every read
anchors on the **message** span, not a name. We captured 7 positions; the ones that matter:

- **message_last** — the last token of the message. The natural place a *global* judgment about
  the message crystallises. This turns out to be the clean read.
- **final** / **message_mean** — the prompt-end token and the whole-message average. These pull
  in confounds (see below), so they're informative but not the headline.
- **pre_message_final** *(negative control)* — the last token *before* the message. Causal
  attention means it can't have read the message yet, so it must come out at chance.
- **question_mean** — the leading question span (identical across items), so it can't carry the
  item's hit/near status — a sanity position.

We lead with the conservative **difference-of-means** probe, document-disjoint (a document is
only ever scored by a direction trained on *other* documents, with its register-matched twin
held in the same fold). AUROC: 0.5 = indistinguishable, 1.0 = perfectly separated. **All
headline numbers are layer-robust** (median across the 64 layers where recognition decodes),
*not* the single best layer — see the caution below.

---

## What the probe shows — the result

At **message_last** (layer-robust medians):

| Question | legal | medical |
|---|---|---|
| **Can it read recognition at all?** (YES vs NO, held-out) | **0.999** | **0.998** |
| **Does it read advice-SEEKING, not topic?** (hit vs register-matched near) | **1.000** | **1.000** |
| **Is `near` kept down near `none`?** (near vs none; want ≤0.65) | **0.642** | **0.604** |
| **Does recognition survive into the action context?** (transfer) | **1.000** | **1.000** |
| **Is it more than generic decodability?** (selectivity over junk; want >+0.10) | **+0.119** | **+0.107** |
| **Does it FLIP with the prompt's rule?** (rule-swap; want ≥0.80) | **0.572** | **0.527** |

**The recognition is real and it reads advice-seeking.** Recognition decodes at ceiling; the
register-matched `near` — same topic, same words, just not asking — is *perfectly* separated
from `hit` (1.000), and `near` sits down near the blank `none` baseline (0.60–0.64). Since
hits and nears are matched on length and topic, this can't be surface length or topic words:
the probe is reading the **seeking** act. It also clears the generic-decodability bar and
transfers into the action pass. This is the rung the project set out to climb — a fuzzy,
no-regex condition, read as genuine recognition, with the contestable-label problem solved.

**But it does not flip with the prompt's rule (rule-swap 0.53–0.57 ≈ chance).** The same legal
document scores the same on the legal recognition axis whether the model's active rule asks
about legal advice or about medical advice. A prompt-conditioned registration would score it
high under the matching rule and low under the swapped one; this doesn't. **So the recognition
is content-driven — effectively a trained-in "is this advice-seeking" detector — not a
computation registered against the rule the prompt actually specified.** This is the control
the whole novelty of Experiment 2 rested on, and it fails, for both conditions.

---

## A caution that changed the headline (why layer-robust)

The single best-recognition layer suggested **medical recognition *does* flip with the rule**
(rule-swap 0.92 at that layer) while legal didn't (0.53) — a tidy, publishable asymmetry. It
is **not real.** The layer where recognition peaks is not where rule-swap peaks, so reading
rule-swap off the recognition-best layer cherry-picks a high excursion. Across all 64 layers
where recognition decodes, the *median* rule-swap is **0.57 legal / 0.53 medical** — both
chance. The asymmetry was a layer-selection artifact. Reported here because it's exactly the
"too-good number → investigate before believing" reflex this project runs on, and it flips a
would-be positive into the honest negative.

---

## Why you can trust the parts that pass (the controls)

- **Negative control at chance.** `pre_message_final` (the token before the message) reads
  **0.50** on everything — no positional leakage. Layer-0 (raw embeddings) ≈ 0.5 and the signal
  builds through the layers — the fingerprint of a *computed* feature, not surface text.
- **Label-shuffle ≈ 0.5** (averaged over 10 permutations) — the pipeline isn't manufacturing
  separation.
- **The "reads seeking" result is length- and topic-clean.** hit-vs-near is 1.000 on
  *matched* pairs (same length, same topic, same vocabulary), so it can't be length or topic —
  the two confounds the keeper was built to kill.
- **Honest position-dependence.** The clean "not topic / not junk" result holds at the
  **message-local** read (`message_last`). At `final` and `message_mean`, `near` rises toward
  `hit` (near-none 0.94–1.00 — topic leaks in) and message length becomes highly decodable
  (selectivity goes thin). So the "not a topic detector" claim is real but *position-specific*;
  away from the message-end token, topic and length contaminate the read. **K3 is
  position-dependent too — and not in the tidy way an earlier draft of this doc claimed.** It is
  ≈ chance at the clean message-local reads (layer-robust median 0.57 legal / 0.53 medical at
  `message_last`), but **elevated at the decision-adjacent positions**: 0.64/0.77 at `final`,
  0.67/0.73 at `post_message_mean` (layer-robust medians, legal/medical). This is *not* the
  topic/length leak that disqualifies those positions for recognition — K3 runs the **same
  documents** through both rule arms, so topic and length cancel by construction. The honest
  reason to discount it is different: near the decision, under the **matching** rule the model is
  more likely *about to emit the flag*, so the probe there is plausibly reading the **forming
  flag**, not a rule-registration — the same "circular, where-the-answer-is-being-written" caution
  the keyphrase work applied to its `final` position. The control that would settle it — re-scoring
  K3 on **behaviour-matched** documents (those the model flags the same way under both rules, which
  removes the about-to-flag difference) — was **not run**: it needs the raw activations, which
  weren't pulled off the GPU box, and it cannot change the verdict regardless (K3 still fails at the
  registered `message_last` read, layer-robustly, both conditions). So the decision-adjacent
  elevation is recorded as **most-likely decision-leakage, not confirmed** — it licenses no
  prompt-conditioned-recognition claim.

---

## Honest bottom line

- **A linear probe reads a fuzzy, no-regex condition ("is this seeking advice?") as genuine
  recognition** — ceiling decode, reads *seeking* not topic (register-matched control, 1.000),
  beats generic decodability, no leakage, on the model's own stable labels. This is a real
  positive: the rung where probes beat regex, with the category track's label problem solved.
- **But the recognition is content-driven, not prompt-conditioned.** The rule-swap control
  (K3) fails robustly for both conditions (≈0.53–0.57): the representation does not flip when
  the prompt's rule changes. It behaves like a trained-in advice-seeking detector, not a
  registration against the *specific rule the prompt named*.
- **So the experiment's novelty claim is not earned, and the climb stops here.** Per the
  pre-registered decision rule, K3 failing means we report where the ladder ends — no
  goalpost-moving. **Experiment 3 (fuzzy × motivated) does not become live** (it required both
  Experiment 1 and Experiment 2 to pass; Experiment 1 was closed at Screen A, and Experiment 2's
  novelty control fails).

## What this can't tell us (caveats worth keeping)

- **"Not prompt-conditioned" is specifically: the ask-trained recognition direction doesn't
  flip with the rule.** It's possible the rule is represented *somewhere* the recognition axis
  doesn't capture; a dedicated rule-conditioning probe, or a causal steering test (does nudging
  recognition change the flag?), would be separate experiments — deliberately not pursued here,
  to avoid turning a clean negative into a rescue hunt.
- **The clean controls hold at one position.** message_last is principled (the message-end token
  is where a global judgment lands), but the topic/length cleanliness is position-specific. The
  honest framing is "readable as seeking at the message-local read," not "everywhere."
- **n ≈ 26–27 hits per condition.** Recognition and hit-vs-near are unambiguous at that n; the
  rule-swap medians are stable across 64 layers, but per-comparison CIs are wide — the *robust
  chance-level* K3 is the trustworthy statement, not any single number.
