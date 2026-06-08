# Research dialogue — generality, transfer, and the production picture for recognition probes

**Date:** 9 June 2026
**Context:** solo 3-week TARA project, in its back half, presentation due soon. This is a captured
ideation/strategy conversation — *not* settled results. It's the "where could this go and what does
it really mean" thinking that the dated results in [README.md](README.md) / [runlog.md](runlog.md)
don't capture. Conor flagged it as worth keeping verbatim to pursue after the project deadline.

**How to read this:** each section is one of Conor's questions, with the context that produced it,
then Claude's answer (lightly cleaned from the chat, same substance). The through-line: *we have a
clean recognition/action separation for one narrow task — what does it actually buy us, does it
generalise, and what's the real research program underneath it?*

---

## 0. Where this came from (the arc of the conversation)

We had just finished the v6→v7 **scale-up** (committed `988479e`): the keyphrase dataset grown to
160 entities/type, 480 pairs, behavioural observe showing recognition at ceiling across all 17
document shapes and a stable silent-omission gap (n_gap = 38, rate ~7–8%, pooled across v5+v6+v7).
The GPU probe run on v7 had **not** yet happened.

With the dataset work parked, Conor stepped back and asked — out of genuine curiosity, explicitly
*not* tied to immediate work — what training probes "in this fashion" actually buys us. That opened
into a chain of increasingly load-bearing questions about generality, transfer, why the *previous*
task failed, and how any of this maps to real deployment. The conversation is the gold; the answers
below are the synthesis.

Two pieces of project history that the questions lean on:

- **The 7-June "clean dead end"** (README, 7 June 2026). The task *before* keyphrase was
  category/export-screening ([make_dataset_v6.py](make_dataset_v6.py)): classify a good into a
  category, check it against a randomised restricted list. On the 32B it failed as a recognition/
  action separation: pre-decision, the recognition signal was *below* meaningless controls (an
  arbitrary label like "is the destination in the first half of the alphabet" decoded at 0.99,
  better than the real signal). Recognition only became readable at the layer where the decision
  commits — fused to the action. A real, controls-backed **negative result**.
- **Why keyphrase exists.** That dead end motivated retreating to a *crisp* trigger — a watchlist
  name either appears as an exact string or it doesn't (see [keyphrase_idea.md](keyphrase_idea.md)).
  No judgment call, so the recognition label is trustworthy.

---

## 1. The conceptual seed — does a recognition probe generalise at all?

**Conor asked:** *Assuming we get a probe that works for "noticing/recognition" of a condition in
the system prompt — should we expect it to generalise to other conditions in new prompts? Or is the
idea just to show the probe works for "noticing this specific thing," and the same approach makes
probes for whatever you want? And if it's the latter, do you have to build this whole complex
data-generation process just to get a probe that reads the right thing?*

**Answer.**

The core reframe: **a probe reads a *direction* in activation space, and whether that direction
generalises is a fact about the model's geometry you *discover*, not something you choose.** You fit
it, then you test transfer, and the model tells you.

So the real question is *what* the direction encodes, and there are two very different possibilities
with opposite answers:

1. **A content-specific feature** — "an on-watchlist name is present in this document." Tied to
   strings/this watchlist. It will *not* fire on "the user is jailbreaking me." Zero free transfer.
2. **An abstract state** — "I have detected that a condition I was instructed to monitor for is
   satisfied," abstracted from *which* condition. If the model represents this, a probe aimed at it
   could transfer across conditions.

The whole interest lives in possibility 2. Our membership control (does the probe fire when a name
is present but *off* the watchlist? it shouldn't) is exactly the move that tries to show we're
reading recognition rather than the raw string — one rung more abstract than the surface.

**Is there reason to expect 2 exists?** Precedent cuts both ways. Encouraging: in current LLMs
several *behavioural-state* directions turn out singular and general — the "refusal direction"
(Arditi et al. and follow-ups) is roughly *one* direction mediating refusal across wildly different
harmful categories, not one per topic; deception/"truthfulness" probe work points the same way. So
abstract cognitive-state directions *can* be condition-general. Discouraging: arbitrary perceptual
features mostly don't transfer. And "noticing" might **fragment** — all *perceptual* detections ("X
is in the text") sharing a direction while *interpretive* judgments ("this is manipulation") live
elsewhere. Generality within a family, not universal.

**The ladder of claims** (each a separate experiment):
1. Probe reads recognition of *this* trigger — what we're doing.
2. …across new document shapes — what the diversity work bought.
3. Train on condition A, test on condition B (**cross-condition transfer**) — *the* interesting next
   experiment; distinguishes "specific feature" from "general state"; currently untested.
4. One probe for arbitrary never-seen conditions — the deployment dream, most ambitious.

**On "do you need the elaborate pipeline every time?"** — the key separation: *the rigorous data
design is the cost of a trustworthy claim, not the cost of a working classifier.* The matched pairs
and controls exist so that *if* the probe scores high, you *know* it's reading recognition and not a
confound. That's a one-time cost to establish the phenomenon. For a *deployed* monitor, once you
believe a "noticing" direction exists, you can fit it with much cheaper/noisier data — you're no
longer defeating every confound, just getting a useful classifier. And if the direction is
condition-general, you fit it *once* on diverse conditions and reuse it.

---

## 2. Can our *current* dataset even test transfer?

**Conor's reflection:** *Our diversity is real but, since the dataset is algorithmically created,
it's essentially a cluster of similarly-shaped tasks. If we find a probe that detects recognition in
our dataset, should we expect transfer to unseen tasks? Or do we need to search for the probe across
a much wider range of tasks? Or is something else required?*

**Answer.**

The honest reframe: **our current dataset can't even *measure* transfer — the diversity is
shape-deep but task-shallow.** The 17 formats and 3 entity types are real variation, but they all
wrap a single computation: "is a watchlisted proper-noun string present among same-type proper-noun
strings?" Bullets-vs-table, unit-vs-person change the *wrapping*, not the *operation*. So a probe
trained on it reads a direction specific to watchlist-membership-detection. There's no held-out task
family, so a 0.95 probe would teach us **zero** about generality — the test set is the same task as
the train set. (Not a flaw in the current claim; just the boundary of what this data licenses.)

"Search across a wider range of tasks" is the right instinct, but sharpen the *why*: the point isn't
more data, it's to **manufacture held-out task families so transfer becomes measurable.** And a
trap: training one probe on a *pool* of conditions and scoring high does **not** prove a general
direction — it could be a stitched-together union of N specific sub-directions. The decisive test is
**leave-task-out**: train on A–G, test on unseen H. Pooled-training answers "can a probe fit all
this"; leave-one-out answers "will it work on something new" — only the second is deployment-relevant.

**Three things "something else" should include:**
1. **The output is a *map*, not yes/no.** Recognition likely fragments by kind: perceptual/exact-match
   vs semantic-category vs normative judgment. Expect high transfer *within* a kind, low *across*.
   "Recognition directions cluster like *this*" is the real deliverable.
2. **Cross-condition controls compound.** If conditions differ in topic/vocabulary/length, a probe
   can "transfer" by reading those surface correlates. A multi-condition set needs matched-pair
   discipline *across* conditions too — genuinely a bigger build.
3. **Each new condition still needs an action-gap**, or the project quietly becomes a vanilla
   concept-probing paper instead of a *silent-omission monitor* paper.

A *rushed* second condition with weak controls is worse than none — it's exactly the "shaky
foundation, then sand it until it fits" failure CLAUDE.md exists to prevent.

---

## 3. The four strategic questions (the heart of it)

These came after Conor connected the dots: we've worked one dataset at a time *because organically
producing recognised-but-didn't-act samples felt critical to proving the probe works* — that need is
what motivated the keyphrase task after the category task failed.

### Q1 — What's the importance of a *statistically significant* recognised-but-didn't-act group? If we bring in more tasks, must we maintain that failure mode across all of them?

The gap isn't decoration — it's the **only population that can tell a recognition-probe from an
action-probe.** On items where the model recognises *and* acts, "reads recognition" and "reads
about-to-act" are indistinguishable; they agree. They only diverge on the gap items. So n_gap is
your *discriminating test set*, and the watchdog (do gap items carry recognition **as strongly as**
flagged items?) is the decisive question: as strongly → genuine looked-and-ignored; **weaker** → the
category task's co-failure in disguise. That's the 7-June lesson operationalised, and it's *why we
scaled to 38* — to power that comparison.

Two claims with different gap-needs:
- **"A probe can read recognition"** (representation claim) — needs no gap.
- **"A probe can catch silent omissions"** (monitor claim — *our* thesis) — *needs* the gap, because
  the gap **is** the thing being caught.

So: new tasks **for the monitor story** each need a real, recognition-preserving gap. New tasks only
to test whether the *recognition direction transfers* don't need a gap at all. Keep the two separate.

### Q2 — What went wrong with the previous category/screening task? Why did this one go well?

Two specific failures in `conditions_v6`:
1. **Recognition was *semantic*** (item → category → membership), computed deep (~8 layers), and
   never separable *before the decision* — pre-decision, meaningless controls decoded *better* than
   the real signal. It only crystallised at the layer where the action commits, fused to it.
2. **The gap was manufactured by *degrading recognition*.** Under load/reframing the model genuinely
   got it wrong — *said* "not restricted" and didn't escalate. ask-NO + action-NO: a **co-failure**,
   not a dissociation.

Keyphrase flips both. Recognition is *syntactic* (exact string match), computed shallow, readable at
a clean locus (`doc_mean`) **before** the decision — which is why the v4 probe could decode it
cross-pass at all. And the gap comes from a different mechanism: **load + burial** (FLAG rule buried
at #21, competing rules firing) makes the model skip the *action* while still passing the recognition
check (loaded-ask YES). A real ask-YES + action-NO.

The honest meta-point: Conor's instinct ("ours is more just string matching; the failed one was
harder") is right, and it's *why* it works — but it bounds the claim. By CLAUDE.md's own framing,
string-match recognition is **"a floor, not the interesting claim."** We have a clean floor. Valuable
as an existence proof; it does not reach the semantic frontier where deployment actually lives.

### Q3 — Is there anything more to do on this task? What would training the probe show? Should we stop and make another task (e.g. a keyphrase→topic variant that reuses the data-gen)?

Yes, there's something crucial left — and it's not busywork: **the probe run on v7 *is* the
experiment; the dataset is just the instrument.** The v4 watchdog was only *directional at n=9*.
Running v7 takes the actual thesis test — "is recognition present in the *action-pass* activations of
the no-FLAG items, as strongly as in flagged ones?" — to proper power, **and it can genuinely come
back null** (gap items recognised more weakly → "the omissions track degraded recognition," a real
finding either way). That's the difference between "we built a dataset with a gap" and "the probe
does/doesn't catch it." So finish it: cheap, and it *completes or kills* the monitor claim here.

What *not* to do: scale keyphrase further — 38 is plenty; more is polishing the floor.

After the watchdog, the **keyphrase→topic variant is the highest-leverage next move**, because it's
three things at once: a *transfer test* (does the keyphrase recognition direction decode topic
recognition?), a *re-attempt at the semantic rung that killed the last task* — now with the
load-burial gap mechanism that preserves recognition — and it *reuses the playbook*. **Critical
design constraint:** "topic" must be genuinely semantic — decorrelate the topic from its keywords
(the no-token-leakage guard from `make_dataset_v6`), or it's just fuzzy keyphrase and you haven't
climbed at all. Be ready for it to hit the 7-June wall again; if it does, *that's* the finding — it
bounds where the monitor is feasible.

### Q4 — Long-term vision: if recognition is a transferable direction, how do companies use it to monitor noticed-but-didn't-act? Could a Qwen user take our "general" probe? (And the realization that production has *many* conditional actions.)

Two hard truths first. A trained probe is **model-and-layer-specific weights** — a company on Qwen
couldn't take "our" probe (different finetune, extraction, drift), and cross-model is hopeless. What
transfers is the **recipe**, not the artifact. The deliverable is never "Anthropic's general Qwen
recognition probe"; it's "a validated, cheap *method* to fit your own recognition monitors on your
own deployed model."

Then Conor's insight, which reframes the whole program: **production doesn't want one general
"something fired" probe — it wants a per-condition panel.** A system prompt has 20 conditional rules;
"you missed *something*" is a weak alarm (re-route to human at best), whereas "you missed *rule 14,
the watchlist one*" is actionable. General-vs-specific is a false binary. The deployment-relevant
questions become:

1. **Per-condition readability** — can you read recognition of a *specific* condition? (what we do, ×N)
2. **Separability / composition** — can you read *many* conditions from one extraction without the
   directions interfering? Decides whether a panel is *practical at scale*. Barely touched anywhere.
3. **Transfer** — is there a shared "monitored-condition" component that makes fitting condition N+1
   cheap, or is each its own island? Decides whether the panel is *cheap to build*.

The gap is the validation population for each. The topic variant is literally the **first 2-condition
step** into this: first data point on (3), first peek at (2) (are the keyphrase and topic directions
orthogonal, or do they collide?). The README roadmap already seeds this ("multiple conditions — can
it represent them each differently"); Conor's reasoning makes it the *load-bearing* question rather
than a footnote.

---

## 4. Synthesis — the forward research program (threads to pull)

Distilled, the open program that this conversation surfaced:

- **Finish the floor.** Run the v7 watchdog at n_gap = 38 (two-sided: could confirm looked-and-ignored
  *or* show the omissions track weaker recognition). Add the **type-confound control** (gap is 100%
  unit/location, person 0 across four runs — confirm the watchdog isn't just reading unit/location vs
  person).
- **First transfer/separability data point:** a genuinely-*semantic* second condition (topic), built
  with the keyphrase playbook + matched-pair discipline *across* conditions, with its own
  load-induced gap. Then: leave-one-out transfer (keyphrase↔topic) and a look at whether the two
  directions are orthogonal.
- **Map, don't binary-test.** Frame "recognition" as fragmenting (perceptual / semantic / normative);
  the deliverable is which families share a direction.
- **The composition question is the under-explored prize:** can N per-condition recognition readouts
  coexist on one extraction without interference? That's what makes a deployment monitor *practical*.
- **Recipe, not weights.** The shippable thing for industry is the *validated method* to fit
  per-condition monitors on their own model — plus evidence on transfer (cheap to build?) and
  composition (cheap to run?).
- **Eventually, naturalistic validation** (real-ish documents / held-out human-written sets / a
  different model) — the control most likely to break a synthetic-trained probe.
- **Deployment-realistic habitat** (already in README): big system prompts, long tool lists,
  multi-turn, trigger firing *mid-trajectory*; the "where/when to read the probe" (streaming readout)
  question.

**Recommended sequencing:** (1) run the v7 watchdog → finishes the floor, could go either way;
(2) build the topic variant as a genuinely-semantic second condition → transfer + semantic re-attempt
+ first separability peek; (3) let what (2) shows decide between *mapping the per-condition panel* and
*writing up the floor + a crisp negative on the semantic rung*.

---

## 5. Status snapshot (so future-you knows where things stood on 9 June 2026)

- **Keyphrase dataset:** v7 is current (160/type, 480 pairs); built, verified, behaviour observed
  (recognition at ceiling, gap real/shape-general, n_gap = 38, rate ~7–8% stable). Committed `988479e`.
- **Probe on v7:** **not yet run** (needs the GPU extract, ~3,840 prompts, ~$3–4). This is the
  pending payoff experiment — the watchdog at proper power.
- **Prior probe evidence (v4, n=9):** recognition decodes cleanly at `doc_mean`, is
  membership-not-co-occurrence, transfers ask→action; watchdog *directional only* — which is what
  motivated the scale-up.
- **The one big caveat that frames everything:** the keyphrase result, however clean, is the *floor*
  (syntactic/string-match recognition). The semantic frontier is exactly where the previous task died
  (7-June). The topic variant is the bridge between them — and the honest test of whether the monitor
  story reaches deployment-relevant recognition at all.
