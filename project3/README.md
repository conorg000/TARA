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

## Where the details live

- [datasets.md](datasets.md) — every dataset, its design rationale, how to regenerate it.
- [runlog.md](runlog.md) — every run: config, full per-layer results, predictions and outcomes.
- [controls.py](controls.py) — the probe-validation controls (shuffle / arbitrary / item-irrelevant).
- [CLAUDE.md](CLAUDE.md) — how to work in this project, and the scientific stance.
- [USAGE.md](USAGE.md) — how to run it (laptop dry-run and GPU).
- [overview.html](overview.html) — a visual explainer of the design.
