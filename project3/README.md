# Probes for trigger recognition

A small, empirically-tight project with one question at its heart:

> **Can a linear probe read a model's *recognition* that a conditional trigger fired — separately from whether the model *acted* on it?**

This README is a **running journal** — dated entries, newest insight building on the last, missteps left in on purpose. The blow-by-blow data lives in [runlog.md](runlog.md); this is the story.

## Why that matters

Models get standing rules — *"if a request crosses into restricted territory, stop and escalate to a human."* They don't always follow them. The interesting question isn't whether the behaviour is reliable; it's whether the model **internally registers** that the condition was met *even when its output doesn't surface it*.

If a cheap linear probe can read that recognition off the activations, you have a **non-behavioural monitor**: run the model and the probe in parallel, and raise an alarm when the probe says "trigger fired" but the behaviour doesn't. That catches the *silent omission* a behaviour-watching monitor structurally cannot see — the loss-of-oversight failure that actually matters for safety.

### Potential roadmap

- **Scale × reasoning.** Run an 8B model with thinking-mode on and off. Does the recognise-but-don't-act gap survive a bigger model and reasoning, or close? That's the result that decides how strong the monitor story is. 
- **Harder rungs of recognition.** The real frontier is fuzzier, more pragmatic triggers (*"is the user asking for legal advice?"*) — closer to deployment, harder to probe.
- **Probe-vs-behaviour as the headline**, on whatever model/task exposes a real behavioural failure worth catching.
- **Causal / steering test.** Steer along the recognition direction — does behaviour change? Tells us if the model *could* use the signal, or if it's just a readout. (Prior work: detection strong, linear steering weak — expect to need more than a simple push.)
- **Cross-domain transfer.** Train a probe on one trigger type, test on a different one. Small gap → one monitor generalises; large gap → monitors are trigger-specific.
- **Multiple conditions**, can it represent them each differently
- **Deployment-realistic / multi-turn.** The endpoint is big system prompts, long tool lists, multi-turn — where the trigger fires *partway through* the context. That's arguably the natural habitat of recognise-but-don't-act (a model ingests a problematic fact mid-trajectory, doesn't flag it, rolls on). Don't jump straight to messy real logs — that throws away the crisp labels and decorrelation we fought for. Instead climb it with **synthetic multi-turn that isolates one variable at a time**, the way we climbed syntactic → semantic:
  - *Persistence* — trigger in turn 1, then *N* benign turns, read the probe at the end; vary *N*. Does the signal persist or decay? Tests whether the model holds a latent "trigger fired" flag, or only re-recognises when it attends back to the triggering tokens.
  - *Padding / background shift* — fix the trigger, wrap it in a long benign system prompt + tool list. Does the agentic-mode "background" alone degrade a probe trained on short single-turn prompts?
  - *Single → multi transfer* — train single-turn, test multi-turn. The **transfer gap is the headline**: small = recognition is context-portable (a cheaply-trained monitor deploys widely); large = quantifies the deployment challenge and motivates training on multi-turn activations.
  - Surfaces an open design question — the **readout policy**: *where/when* do you read the probe in a long trajectory? A "streaming" probe over each incoming chunk may matter more than retraining, since a transformer re-recognises a trigger where it attends to it rather than holding a persistent flag.

### Related work we may reach for

*Not foundations of this project — two adjacent papers we've read that sharpen where we might go next. Both probe whether a model "knows it's being tested"; the tools and pitfalls transfer.*

- **Detection ≠ use.** [Nguyen et al.](../papers/probing_steering_eval_aware.md) could *read* the eval signal (AUROC 0.83) but *steering* along it barely moved behaviour (<5%) — our recognise-but-don't-act gap, seen elsewhere. Motivates the **steering/causal test** in the roadmap above.
- **Format confound.** [Devbunova](../papers/eval_awareness_format_confound.md) shows eval-awareness probes often learn prompt *format*, not meaning. We've designed that out (phrasing randomised vs. the label) — so this is reassurance our method holds, not a new direction.
- **Weak cross-domain transfer.** [Devbunova](../papers/eval_awareness_format_confound.md)'s probe scored ~0% on a different domain. Motivates the **cross-domain transfer test** above — the load-bearing question for the monitor story.

---

## 29 May 2026 — from a shaky idea to a recognise-vs-act result

This started somewhere I wasn't sure about and turned into something I'm genuinely excited by. The arc, and what each step taught us:

### The journey so far

1. **Reused our old data — and learned it couldn't answer the question.** The first probe ran on the earlier analyst-escalation scenarios. A 0.6B model, far too weak to *do* the task, still separated escalate from routine at AUROC 0.98. That wasn't recognition — it was **topic**. Escalate cases were about crypto/sanctions/fraud, routine ones about admin, so the probe just read subject matter. *Lesson: if the label is readable from the surface, a high score proves nothing.*

2. **Built data where the surface can't give the answer away.** `conditions_v1`: a policy with a *randomised restricted list*, where the label is whether a request's destination is on *that* list. The same country is escalate under one list and proceed under another, so identity predicts nothing. The probe read it cleanly — but a 0.6B **maxed it (AUROC 1.0)**, because the task reduces to string-matching. A clean *floor*, but the easy end of "recognition."

3. **Climbed to semantic recognition.** `conditions_v2`: the list holds *categories*, the request names an *item*, and the words never overlap — so the only route to the label is *item → category → membership*, i.e. genuine world knowledge. The probe still read it (**0.89**), but now the signal is computed ~8 layers *deeper*, stays distributed, and — a prediction I got wrong — **generalises to categories the probe never trained on**. So it's reading something abstract, not memorised.

4. **Added behaviour — the actual thesis test.** We generated the model's real output and compared it to the probe. The 0.6B's *behaviour* was barely above chance: it defaults to "proceed" and misses 80 of 96 escalations. But the probe recovered the right answer **79%** of the time and **caught 76% of the escalations the model failed to make**. The decision-relevant information was sitting in the activations even when the output ignored it — the **recognise-but-don't-act dissociation** the project set out to find.

### What this means — stated carefully

The probe-as-monitor idea has legs: in at least one clean regime, a cheap probe extracts decision-relevant recognition that the model's behaviour discards. Two honest qualifiers we won't drop:

- The probe is **trained** and the behaviour is **zero-shot**, so the precise claim is *"the information is linearly decodable from activations though the output ignores it,"* not *"the model knew and chose not to comply."* (For a deployment monitor — which *is* a trained probe — that's the right comparison.)
- It's **one regime**: a small model, greedy decoding, no reasoning. Whether the gap survives scale and chain-of-thought is the open question, not a settled result.

### What's next

- **Scale × reasoning.** Run an 8B model with thinking-mode on and off. Does the recognise-but-don't-act gap survive a bigger model and reasoning, or close? That's the result that decides how strong the monitor story is. The infrastructure is built — same `run.sh`, swap the model, toggle reasoning.
- **Harder rungs of recognition.** Our conditions are crisp and mechanical. The real frontier is fuzzier, more pragmatic triggers (*"is the user asking for legal advice?"*) — closer to deployment, harder to probe.
- **Probe-vs-behaviour as the headline**, on whatever model/task exposes a real behavioural failure worth catching.

### What keeps it honest

The part I'm most happy about isn't a number — it's the method. The rules we've held to (full version in [CLAUDE.md](CLAUDE.md)):

- **Surface-decorrelated data**, audited at generation, so a high score can *only* come from recognition.
- **Pre-registered predictions** with falsification thresholds, written before each run and scored HIT/MISS honestly — including the ones we got wrong. (Recognition-probe go/no-go was set at AUROC > 0.80 go / < 0.65 kill.)
- **Deterministic grading** — no LLM judge; the dataset's crisp tokens make one unnecessary.
- **Candid caveats** on every result, especially the clean ones.

---

## 30 May 2026 — controls: the headline was inflated (and that's good)

A sharp question to start the day: are we sure the probe is reading the model's *recognition*, and not just *learning the task itself* from a rich representation? That's the Hewitt & Liang (2019) critique — a powerful probe can fit structure the model never computed — so we built [controls.py](controls.py) and ran three checks on the v2 activations. What came back changed how we report yesterday's result.

- **The pipeline is honest.** Shuffling the labels collapses the probe to ~0.50 out-of-fold. So the high numbers aren't a cross-validation artefact of having more dimensions (1024) than examples (192). That worry is closed — checked, not assumed.
- **But our logreg headline was inflated.** A logistic probe reads *arbitrary, task-irrelevant* facts off the same activations at 0.75–0.80 (and surface phrasing at a perfect 1.0). The representation is a rich linear "soup," and logreg's 0.89 sits only ~0.1 above that junk baseline. Most of its power is "strong probe on a rich representation," not recognition.
- **The honest signal is smaller — but real.** The low-capacity difference-of-means probe (the one Hewitt & Liang say to trust) is properly selective: it reads escalation at **0.68** while sitting at chance on the *clean* controls — shuffled labels (0.51), an irrelevant input property (0.52), and the sharpest test, *membership of a category the item doesn't belong to* (0.44). So the representation specifically encodes **the item-cued match**. That is recognition, and it survives — it's just **~0.68, not 0.89**.

So I'm revising yesterday's numbers down, and leaving yesterday's entry as written. The recognise-but-don't-act gap is **~0.16 (recognition 0.68 vs behaviour 0.52), not ~0.37**. Modest, but still pointing the right way.

The bigger win is the method. This is exactly the kind of inflation an "it's probably fine" shortcut would have shipped — we checked, and the number moved. **New standing rule** (now in [CLAUDE.md](CLAUDE.md)): every probe result gets controls run beside it; we **lead with difference-of-means**, treat logreg as an upper bound, and report **selectivity** (real − control), not the raw number. Full detail in [runlog.md](runlog.md) under r5.

Next is unchanged: the scale-×-reasoning run is still the experiment that decides whether the (now more modest) gap survives a capable model with chain-of-thought.

---

## 5 June 2026 — scale confirms recognition, closes the gap, and the probe outruns the model

To the GPU at last (Qwen3-8B; we also split the workflow — extract on the GPU, probe on the laptop, see [LOGISTICS.md](LOGISTICS.md)). Three results and one sharp lesson. Blow-by-blow in [runlog.md](runlog.md) (r7–r9 + the v3 go/no-go).

**Recognition is robust.** The 8B reads "restricted" at diff-of-means **~0.97** — and *more* selective than the 0.6B (0.46 vs 0.18). It's unchanged with thinking on, and the direction **transfers to a disjoint taxonomy at 0.98** with no penalty. Recognition survives scale, reasoning, and domain.

**But the recognise-but-don't-act gap does not.** A capable model *acts* on what it recognises — behaviour 0.90 (0.94 with reasoning), silent misses 13 → 7, the gap shrinking toward zero. The dramatic 0.6B dissociation was mostly a small-model proceed-default. **A benign, unambiguous task can't produce the gap the monitor exists to catch** — now shown twice (reasoning off and on).

**So we tried to engineer one (conditions_v3)** by adding a competing throughput objective to the prompt — keeping the escalation rule mandatory. It **didn't move behaviour at all** (escalate-rate 66 → 68% across neutral → strong): a capable model won't drop a mandatory rule for KPI pressure. The *agentic framing itself* did move it (escalation 86% → 66%) — but a new **direct-ask check** ("is this restricted? [YES]/[NO]") exposed it as a **co-failure, not a dissociation**: on the items it under-escalates, the model *says they aren't restricted*. The frame degraded recognition; it didn't pry recognition apart from action.

**The lesson worth keeping.** The probe still reads **0.95 on the very items the model itself calls not-restricted** — it decodes the *ground-truth* fact, which here **diverges from the model's own recognition**. So **probe-high + action-low is *not* evidence of "knew but didn't act."** The direct-ask is now mandatory, and it sets a crisp bar for a *real* dissociation: **ask-YES + action-NO** — which we have not produced. On benign tasks, recognition and action stay coupled, so the genuine gap likely needs a **motivated/withholding** setup (the model recognises, would admit it, yet withholds), not a task made merely harder. That's the next swing — taken, this time, with an instrument that can tell a real dissociation from a confound.

---

## 7 June 2026 — a clean dead end: recognition and action aren't separable before the decision

**The premise, restated for a fresh reader.** The whole project asks one thing: when a model is given a standing rule ("if a request crosses into restricted territory, stop and escalate"), can a cheap *probe* — a small pattern-reader trained on the model's internal activations — tell that the model *recognised* the rule applied, separately from whether it actually *acted*? If it could, you'd have a monitor for the silent miss: the model noticed, didn't act, and its output never showed it. By 5 June we'd seen that a capable model doing a clean task acts on what it recognises, so the gap we wanted to catch barely existed in behaviour. This round we built a sharper instrument to look for it in the activations directly. The answer came back negative — and the controls make it solid.

**What we set up.** Two changes. First, we moved to the larger 32B model (no step-by-step reasoning) and rewrote the task so the recognition question has a trustworthy answer — we fixed some genuinely mislabelled items (a "bed frame" had been filed under *office furniture*) and, more importantly, stated the task explicitly ("work out the category, then check the list"). Recognition jumped from ~0.79 to ~0.98: asked directly, the model now almost always gets it right. Second, a cleaner probe design. We run every item two ways — an **ask** version (just the recognition question) and an **action** version (the real screening job). The idea: train the probe *only* on the ask runs, where the model is doing pure recognition with no action to take, then test it on the action runs. A probe that has never seen an action can't secretly be reading "about to act" — the confound that had tripped us before.

**What happened, step by step — this is the part that matters.**

The first look was exciting: the ask-trained probe, tested on the action runs, scored **0.996**. But it only worked at the *late* layers of the model — the point where it has essentially already decided. There the probe isn't reading recognition; it's reading the answer the model just formed. A post-decision artifact. The honest question is whether you can read recognition *before* the model commits, because that's the only place a monitor could ever help. Before the decision, the score was **~0.6** — barely above a coin flip.

Before giving up we ruled out a boring explanation: maybe the cross-version test failed only because the two prompt types are worded differently. So we trained the probe directly on the action runs instead of transferring from the ask runs. Before the decision, that *looked* like it rescued things — about **0.8**.

Then we ran the controls, and the controls killed it.

A control asks the probe to predict something deliberately meaningless, to measure how much the activations let you decode *anything at all*. "Is the destination country in the first half of the alphabet?" — pure nonsense, nothing to do with the rule — decoded at **0.99**, *better* than the real restricted signal at 0.74. "Does the item name have an odd or even number of letters?" — also nonsense — decoded at **0.85**, also better. Our recognition signal scored *below* the junk. Its selectivity (real minus control) was **negative**.

In plain terms: a big model's activations linearly encode an enormous amount of arbitrary stuff — the spelling of the destination, the item string, all of it. A linear probe reading those activations before the decision picks up whatever structure is lying around, and there is a lot lying around. The "0.8" was never a recognition signal; it was the probe riding general decodability — the same thing that reads total nonsense at 0.99.

So the honest chain is complete:
- The cross-version 0.996 was the model reading its own committed answer (post-decision).
- Training directly on the action runs *looked* like it recovered a pre-decision signal (~0.8).
- The controls show that 0.8 is just decodability — any meaningless label gets it too.

**There is no pre-decision recognition signal that beats chance once you account for what's trivially decodable.** The load sweep we'd planned — adding clutter to manufacture more "recognised-but-didn't-act" cases — would have been amplifying a signal that isn't there.

**The finding, stated as a finding.** In this model on this task, "recognition" is not represented as a separate, readable thing before the decision forms. It only becomes cleanly readable at the layer where the decision commits — and there it is inseparable from the action itself. Recognition and action don't have distinct internal signatures here; they emerge together, at decision time. That is a real, defensible negative result, and it matches the behaviour, where the "recognised but proceeded" cases numbered about four. The dissociation isn't hiding in the activations any more than it was in the outputs. (Scope: this tested reading at the *decision point*, across the model's depth; we did not test reading at the earlier point where the item is first named — a different cut that would need a fresh extraction.)

**Why we trust it.** The controls are what caught this, and running them isn't standard practice — it would have been easy to report the 0.8 as a win. One control points the other way and is worth noting: when we asked the probe to predict membership of a category the item *doesn't* belong to (the same "read the list" task, minus the recognition step), the real signal clearly beat it (+0.29). So the test itself is sound — it can tell relevant from irrelevant. The thing we were testing for simply isn't there before the decision.

**Where this leaves the project.** The premise — that there's a recognition state you can read before and independently of the action — does not hold on this setup. This closes this line of experiments; there's no point trying to make this task work. The options:

1. **Write it up as the negative result.** "Recognition is not linearly separable from action before the decision; the apparent cross-version transfer is a post-decision artifact; before the decision, meaningless controls decode better than the real signal." That's a genuine contribution, and airtight precisely because the controls carry it — arguably more honest than most positive results.
2. **If a positive result is wanted, the premise has to change, not the task.** You'd need a setting where recognition is *forced* to happen and persist as a discrete step before the action — e.g. a task with explicit intermediate reasoning where the model states the category before deciding, and you probe the reasoning. But that reintroduces the "reading the stated answer" confound this project has been fighting — a different experiment, not a tweak.
3. **Don't run the load sweep.** There's no clean signal for it to amplify.

The strongest move is the first. The failure is clean and demonstrable, and the controls make it solid — the method doing its job, turning a tempting number into a clear answer. The blow-by-blow (per-layer tables, the cross-pass run, the controls) is in [runlog.md](runlog.md) under 6–7 June.

---

## Where the details live

- [datasets.md](datasets.md) — every dataset, its design rationale, how to regenerate it.
- [runlog.md](runlog.md) — every run: config, full per-layer results, predictions and outcomes.
- [controls.py](controls.py) — the probe-validation controls (shuffle / arbitrary / item-irrelevant).
- [CLAUDE.md](CLAUDE.md) — how to work in this project, and the scientific stance.
- [LOGISTICS.md](LOGISTICS.md) — the operational runbook: extract-on-GPU / probe-on-laptop, vast.ai basics.
- [USAGE.md](USAGE.md) — how to run it (laptop dry-run and GPU).
- [overview.html](overview.html) — a visual explainer of the design.
