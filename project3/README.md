# Probes for trigger recognition

A small, empirically-tight project with one question at its heart:

> **Can a linear probe read a model's *recognition* that a conditional trigger fired — separately from whether the model *acted* on it?**

## Why that matters

Models get standing rules — *"if a request crosses into restricted territory, stop and escalate to a human."* They don't always follow them. The interesting question isn't whether the behaviour is reliable; it's whether the model **internally registers** that the condition was met *even when its output doesn't surface it*.

If a cheap linear probe can read that recognition off the activations, you have a **non-behavioural monitor**: run the model and the probe in parallel, and raise an alarm when the probe says "trigger fired" but the behaviour doesn't. That catches the *silent omission* a behaviour-watching monitor structurally cannot see — the loss-of-oversight failure that actually matters for safety.

## The journey so far

This started somewhere I wasn't sure about and turned into something I'm genuinely excited by. The arc, and what each step taught us:

1. **Reused our old data — and learned it couldn't answer the question.** The first probe ran on the earlier analyst-escalation scenarios. A 0.6B model, far too weak to *do* the task, still separated escalate from routine at AUROC 0.98. That wasn't recognition — it was **topic**. Escalate cases were about crypto/sanctions/fraud, routine ones about admin, so the probe just read subject matter. *Lesson: if the label is readable from the surface, a high score proves nothing.*

2. **Built data where the surface can't give the answer away.** `conditions_v1`: a policy with a *randomised restricted list*, where the label is whether a request's destination is on *that* list. The same country is escalate under one list and proceed under another, so identity predicts nothing. The probe read it cleanly — but a 0.6B **maxed it (AUROC 1.0)**, because the task reduces to string-matching. A clean *floor*, but the easy end of "recognition."

3. **Climbed to semantic recognition.** `conditions_v2`: the list holds *categories*, the request names an *item*, and the words never overlap — so the only route to the label is *item → category → membership*, i.e. genuine world knowledge. The probe still read it (**0.89**), but now the signal is computed ~8 layers *deeper*, stays distributed, and — a prediction I got wrong — **generalises to categories the probe never trained on**. So it's reading something abstract, not memorised.

4. **Added behaviour — the actual thesis test.** We generated the model's real output and compared it to the probe. The 0.6B's *behaviour* was barely above chance: it defaults to "proceed" and misses 80 of 96 escalations. But the probe recovered the right answer **79%** of the time and **caught 76% of the escalations the model failed to make**. The decision-relevant information was sitting in the activations even when the output ignored it — the **recognise-but-don't-act dissociation** the project set out to find.

## What this means — stated carefully

The probe-as-monitor idea has legs: in at least one clean regime, a cheap probe extracts decision-relevant recognition that the model's behaviour discards. Two honest qualifiers we won't drop:

- The probe is **trained** and the behaviour is **zero-shot**, so the precise claim is *"the information is linearly decodable from activations though the output ignores it,"* not *"the model knew and chose not to comply."* (For a deployment monitor — which *is* a trained probe — that's the right comparison.)
- It's **one regime**: a small model, greedy decoding, no reasoning. Whether the gap survives scale and chain-of-thought is the open question, not a settled result.

## What's next

- **Scale × reasoning.** Run an 8B model with thinking-mode on and off. Does the recognise-but-don't-act gap survive a bigger model and reasoning, or close? That's the result that decides how strong the monitor story is. The infrastructure is built — same `run.sh`, swap the model, toggle reasoning.
- **Harder rungs of recognition.** Our conditions are crisp and mechanical. The real frontier is fuzzier, more pragmatic triggers (*"is the user asking for legal advice?"*) — closer to deployment, harder to probe.
- **Probe-vs-behaviour as the headline**, on whatever model/task exposes a real behavioural failure worth catching.

## What keeps it honest

The part I'm most happy about isn't a number — it's the method. The rules we've held to (full version in [CLAUDE.md](CLAUDE.md)):

- **Surface-decorrelated data**, audited at generation, so a high score can *only* come from recognition.
- **Pre-registered predictions** with falsification thresholds, written before each run and scored HIT/MISS honestly — including the ones we got wrong. (Recognition-probe go/no-go was set at AUROC > 0.80 go / < 0.65 kill.)
- **Deterministic grading** — no LLM judge; the dataset's crisp tokens make one unnecessary.
- **Candid caveats** on every result, especially the clean ones.

## Where the details live

- [datasets.md](datasets.md) — every dataset, its design rationale, how to regenerate it.
- [runlog.md](runlog.md) — every run: config, full per-layer results, predictions and outcomes.
- [CLAUDE.md](CLAUDE.md) — how to work in this project, and the scientific stance.
- [USAGE.md](USAGE.md) — how to run it (laptop dry-run and GPU).
- [overview.html](overview.html) — a visual explainer of the design.
