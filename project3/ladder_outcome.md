# Move 4 — The spontaneity ladder: where comprehension ends and the rule takes over

**Dated:** 2026-06-12. **One-line result:** rule-conditioned computation *does* exist — the
model computes a rule-supplied criterion it would never compute on its own — but only **late**,
near the moment of decision, not while it's reading; and even there its **reading** of the
criterion comes apart from its **action** on it.

This is the experiment Exp 2's K3 negative pointed to but couldn't run. K3 asked whether a rule
changes how the model *reads* a message, and found it doesn't — for a condition (legal/medical
advice-seeking) the model computes anyway, with or without the rule. The honest caveat was: of
course the rule had no visible effect, it had no work to do. Move 4 builds conditions where the
rule is the **only** possible source of the answer, and asks whether the rule then does the work.

## The setup, in plain terms

Four conditions, each a compound "**A and B**":

| | A (spontaneous part) | B (the decisive part) |
|---|---|---|
| **advice_deadline** (R2) | asking for advice | …with a stated deadline |
| **refund_over_500** (R3, Family B) | a refund request | …for **more than £500** |
| **complaint_6months** (R3, Family B) | a complaint | …about something **over 6 months ago** |
| **medical_rx_drug** (R3, Family A) | seeking medical advice | …about a **prescription-only** drug |

For each, we wrote **matched pairs**: a `hit` (A and B both true) and a `near` that is the *same
message word-for-word except B is false* (a £540 refund vs a £470 refund; an 8-month-old complaint
vs a 4-month one; the same health question about an Rx drug vs an over-the-counter one). Because
hit and near differ *only* in B, anything that tells them apart must be reading B itself.

We train a probe to recognise the compound from the model's activations **when it's directly
asked** the question (no rule involved), then point that probe at two situations where the model
is just **reading the message with no question asked**:

- **with the rule** — the rule ("flag refunds over £500") sits in the system prompt;
- **without the rule** — a length-matched placebo rule ("flag lost-pet reports") sits there instead.

The two situations use the **identical messages** — only the rule's text differs. So if the probe
can tell hit from near *with* the rule but not *without* it, the rule is doing the computing. (And
because the messages are identical, this can't be the probe sneakily reading "big number" — that
would show up in both.) We read at three points: averaged over the message body, at the last word
of the message, and at the final token just before the model acts.

## What we found — three different stories up the ladder

Read the **"without the rule"** column first — it's the spontaneity test:

1. **advice + deadline (both parts spontaneous):** readable *without* the rule, right there in the
   message body (0.93). A deadline is something the model notices on its own; gluing it to
   "asking for advice" doesn't change that. Bottom rung confirmed.

2. **medical + Rx-drug (a world-knowledge fact):** also readable *without* the rule, everywhere,
   essentially perfectly (0.83–1.00). The model's representation of the word "amoxicillin" already
   carries "prescription-only" — it doesn't need a rule to know that; it just knows. This was the
   **planned contrast**: it looks like spontaneity, but it's really latent dictionary knowledge
   sitting in the token, not the rule doing anything. (It's also why a probe reading a fact ≠ the
   model *using* the fact — see below.)

3. **refund > £500 / complaint > 6 months (a rule-supplied criterion) — the real result:** *not*
   readable without the rule, at any position (≈ chance, 0.44–0.57). Of course — "£500" and "6
   months" exist nowhere except in the rule, so with a placebo rule there's nothing to compare to.
   **But with the rule, it becomes readable — and only late:** still near-chance in the message-body
   average, then climbing to clearly readable (0.88–0.92) at the last word of the message and the
   decision point. The rule **switches on** a computation the model would never do unprompted, and
   it does it near the moment of acting, not while reading.

So the ladder behaves exactly as drawn: how readable the decisive element is *without the rule*
falls as you climb — spontaneous (R2) → latent-but-present (Family A) → genuinely absent (Family
B). And for the one rung where the rule is the only possible source, **the rule restores it.**
That's the positive answer K3 couldn't give: top-down, rule-conditioned computation exists. We
found it precisely where it has a reason to live.

## The twist: the model *reads* the threshold but doesn't *act* on it

Behaviourally, the rule is a blunt instrument. Told to flag refunds over £500, the model flags
**88%** of the under-£500 `near` refunds too; the medical rule flags **100%** of the
over-the-counter cases. It over-fires — the same "liberal action pass" we saw in Move 1.

Yet the *reading-side* probe cleanly separates hit from near **even among the messages the model
flagged identically** (0.87–0.89). So the model genuinely computes "this one is over £500 and this
one isn't" internally — and then flags both anyway. The careful internal reading and the clumsy
outward action **come apart**. That's the same dissociation the whole project keeps finding
(recognition readable under instructed silence in Exp 1; comprehension decoupled from the rule in
Exp 2), now showing up at the rule-binding frontier: the binding *is* computed, just not faithfully
acted on.

## What it means for the monitoring story

- **The content-probe panel has a boundary, and it's *positional*, not a flat wall.** A monitor
  that reads the average of the message body will **miss** a rule-supplied-criterion condition
  (Family B is at chance there). The signal exists, but only at the decision-adjacent position and
  only with the rule actually in the prompt. So "what you can't probe for" isn't "rule-supplied
  criteria, full stop" — it's "rule-supplied criteria, read during ordinary comprehension." Read at
  the binding point and they're there.
- **"Always-on comprehension" has a precise edge.** Things the model computes anyway (natural
  categories, latent facts) are readable cheaply, anywhere, rule or no rule — that's most
  deployment conditions, and the panel covers them. Things that exist *only* in your rule (a
  threshold, a cutoff, a list) are computed late and conditionally — probeable, but you have to know
  where and when to look.

## Honest limitations

- **Family A is a contrast, not a clean test.** Its "readable without the rule" is a probing
  artifact by design — the fact is linearly decodable from the drug name whether or not the model
  uses it (the Hewitt–Liang caveat). We kept it precisely to show what *latent knowledge* looks
  like next to *rule-supplied criterion*; don't read it as rule-conditioning.
- **Family B's effect is carried by the late positions.** The message-body average is weak
  (0.63/0.78); the result lives at the last-word/final reads. The exact peak differs by criterion
  (the temporal cutoff peaks at the message's end, the numeric threshold at the decision token) —
  consistent in shape, not identical in detail.
- **One model, one register.** Qwen3-32B, the Riverbeck-council correspondence world shared with
  Exp 2. The two Family-B instantiations agreeing (numeric *and* temporal) is the cross-condition
  robustness; a second model would be the next check.
- **Near-threshold probeability.** The model fumbles the threshold on ~12% of `near` items when
  asked (a £460 refund called "over £500"); those are dropped by a correctness filter, leaving
  ~20+ clean pairs per condition. The fumbles are themselves a small finding — numeric/temporal
  thresholds sit nearer the edge of no-think reliability than categorical facts.

## Where this leaves the project

Putting the four moves together, the picture is now coherent and, I think, genuinely earned:

- **Comprehension is always-on and rule-independent** for conditions the model computes anyway
  (Exp 2 K3; R2; Family A). That invariance is *why* a content-probe panel works and keeps working
  under instructed silence (Exp 1).
- **Binding to a rule is computed downstream, near the decision** — and for criteria the model
  wouldn't compute on its own, the rule is what triggers it (Move 4, Family B). It exists; it's just
  late and, behaviourally, leaky.
- **Detection survives all of this.** A monitor needs "did it register the condition?" (the probe,
  always-on) and "did it act?" (the output) — and now we know the one case the reading-probe needs
  help with (rule-supplied criteria) is exactly the case where you read at the decision point
  instead of the body.
