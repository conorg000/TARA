# NLA vs linear probe — working project doc

A scope-thinking doc for the NLA-vs-probe head-to-head extracted from [[nlas.md]]. The motivation, paper quotes, and competing predictions live there. This doc is just for figuring out *what the experiment actually looks like* and where the design risks are.

Companion paper: `papers/natural_language_autoencoders.md` (summary) and `papers/sources/natural_language_autoencoders.html|.txt` (full source).

---

## The basic setup

Pick an open-weight model with a released NLA — Qwen-7B is the easy choice (NLA at layer 20 of 28, smallest model, cheapest to run). Now there are two ways to read the residual stream at layer 20 of Qwen-7B:

1. **The NLA.** Feed it the activation at some token position, get back a sentence or two of English describing what's in there. ("The user is asking a math question. The assistant is being evaluated on accuracy.")
2. **A linear probe.** A single direction in activation space that says "how much of feature X is present at this position." Output is one number. For eval-awareness: take the average activation on eval-style prompts, subtract the average on deployment-style prompts — that's your direction. (This is what Needham et al. did — difference-of-means, about as simple as a probe gets.)

Both methods reading the same residual stream, same layer, same token. The comparison is fair.

## How the probe actually gets trained

A linear probe is the dumbest possible thing. The pipeline:

1. Get a few hundred prompts labeled "eval-like" and a few hundred labeled "deployment-like."
2. Run each prompt through Qwen-2.5-7B, grab the residual-stream activation at layer 20 (the layer the released NLA reads), at the chosen token position.
3. Average the eval activations. Average the deployment activations. Subtract — that's the direction. (Or fit logistic regression on the same labeled activations for slightly more expressivity at slightly more compute.)
4. Project any new activation onto the direction → one number, "how eval-aware this position looks."

Training takes minutes. Inference is milliseconds per token. The whole game is getting good labels — the probe itself is trivial.

Rough target: 500–2000 labeled prompts total. Below that, difference-of-means is noisy. Above that, diminishing returns.

## The dataset situation

There's no canonical "eval-awareness" dataset. This is a real gap in the field, not something we missed.

**Building blocks that exist (all open):**

- **SAD** (Laine et al., NeurIPS 2024) — 13,198 questions designed to probe whether models know they're LMs. Behavioural benchmark, but the prompts are reusable as the eval side of a contrast set.
- **Public eval benchmarks** — MMLU, MMLU-Pro, GPQA, AgentHarm, BIG-bench, etc. Loads of eval-flavoured text.
- **Public chat corpora** — WildChat (1M+ real user conversations from public APIs), ShareGPT, LMSYS-Chat-1M. Genuine deployment-side material.
- **Recent probe papers' contrastive datasets** — Needham (scaling), Nguyen, Devbunova all built their own. Some released, some not — need to verify which.

**Best ready-made candidate.** Needham et al's 1000-transcript benchmark from "Knowing Being Evaluated" (May 2025): 1000 transcripts from 61 source datasets, each labeled eval-like or deployment-like, balanced across agentic and chat. If released (Apollo has a good track record), this is the natural starting point — saves us the dataset-construction step and anchors the comparison to the field's most-cited eval-awareness measurement. Worth confirming availability before committing.

**Why there isn't a canonical dataset:**

1. The sub-field is too young. Serious eval-vs-deployment probe work only landed in 2025; the field hasn't standardised yet.
2. "Eval-awareness" means different things in different papers — "recognises this is a benchmark" vs "knows it's an LM being evaluated" vs "behaves differently in eval vs deployment." A canonical dataset would have to pick a definition.

**What this means for the project.** Building the labeled corpus is mechanical, not a rabbit hole. Worst case: stitch SAD + a couple of public benchmarks on one side, sample from WildChat on the other, light cleaning. A day or two of work. If Needham's benchmark is released, just use that.

## The question we're really asking

The NLA paper sets up two competing claims about probes that it never tests:

- **Pro-NLA:** NLA might see things probes miss, if the info is encoded nonlinearly.
- **Pro-probe:** probes are less likely to make stuff up — they can only do linear arithmetic on the activation, they can't "imagine" content.

Find cases where the two methods disagree, because those are the cases that adjudicate between the two claims.

The study's outputs stack three layers:

1. **Per-prompt agreement.** On a held-out test set, how correlated are the two methods' per-prompt scores? Easy win in either direction — high agreement → probe is the cheap right answer; low agreement → they're reading different things and the disagreement cases need attention.
2. **Who's right when they disagree.** This is where the science is — the tiebreaker section below covers how.
3. **Are both methods format-confounded?** Devbunova-style stress test (bench-format-vs-casual-format crossed with eval-vs-deployment) on *both* methods. If both fire the same way on benchmark-shaped deployment content, NLA's "higher-fidelity readout" pitch takes damage even if the disagreement story goes its way.

## What disagreement looks like

- **NLA says "eval-awareness present" but probe says no** → either NLA is confabulating (pro-probe wins this round), or NLA is reading nonlinear info the probe can't access (pro-NLA wins).
- **Probe says "eval-direction is firing" but NLA never mentions it** → either probe is reading something else that correlates with the eval label (the format-confound problem — probe lights up on "benchmark-shaped text" not "the model believes it's being tested"), or NLA is missing it.

Direction of disagreement matters — the two failure modes have different implications.

## The tiebreaker (the hard bit)

When they disagree, how do we decide who's right? Options:

1. **Behavioural divergence.** Does the model actually behave differently on cases where the NLA says "eval-aware" vs where the probe says so? If only the NLA's flagged cases show a real behaviour shift between eval-framed and deployment-framed versions of the same prompt, that's evidence the NLA is reading the load-bearing thing.
2. **Steering.** Take the probe direction and steer with it; take an NLA-derived steering vector (the paper's recipe: edit the NLA's English explanation, run the AR back to activations, take the difference). If only one shifts behaviour, that's evidence about which is reading something causal.
3. **Format-confound stress test.** If the probe fires hard on Devbunova-style "benchmark-shaped but harmless content," that suggests it's reading format not credence — probe loses that round.

Behavioural divergence is probably the cleanest because it's external — the model's actual outputs change or they don't. Steering as a secondary check. Format-confound as a stress test on the probe specifically.

## Design choices to pin down

- **Target.** Eval-awareness has the best paper backing, but it needs an eval/deployment contrast set for Qwen-7B. Could borrow Needham et al's setup, or use Devbunova's Bench-Deploy. *Or* pick an easier target like refusal or sycophancy where contrast sets are off-the-shelf — but then we're slightly off the NLA paper's central story. Eval-awareness is the right pick if the contrast-set work is doable in scope.
- **What "the activation" is exactly.** NLAs read one token's residual stream. Which token? The paper uses end-of-prompt or end-of-response depending on the case study. The probe lives at the same place. This matters more than it sounds — eval-awareness might live at the system-prompt boundary, or at the assistant's first token, or somewhere else.
- **How to score the NLA.** The paper uses an "any of 50 tokens contains awareness language" aggregator, which they themselves call arbitrary. Inherit it for the comparison, flag it as a methodological wart.
- **Layer constraint.** The released NLA is at layer 20. Probe is also at layer 20 for fairness. No optimising the probe's layer choice — that's the apples-to-apples cost.

## Risk / failure modes

Two ways this can come out without the juicy headline:

1. **The methods mostly agree.** Then there isn't a disagreement story. Still publishable ("the cheap method is good enough is a real field-relevant finding") but less exciting.
2. **The methods disagree a lot but the tiebreaker is too noisy to call winners.** End up with "here are the disagreements, the field needs better adjudication methods."

Worth deciding now whether either outcome counts as a successful project. I think both do, but they have different writeup shapes.

## Tightening the empirical story (the layer-lock workarounds)

Training a new NLA at a different layer is realistically out of scope. The paper's own cost reference: Gemma-3-27B took ~576 H100-hours to reach 0.71 FVE, ~2,700 H100-hours for 0.75 FVE. Qwen-7B is ~1/4 the size, so very roughly $300-2,800 cloud cost per training run, plus a week of engineering setup. That's most of the budget *per layer*. Sweeping multiple layers to find the best NLA is just not in the cards.

So we work around the layer-lock without training anything new:

1. **Pilot first, commit second.** Spend a day or two running the released Qwen NLA on a handful of eval prompts before sinking time into the full setup. Does it surface anything sensible at all? If yes, layer 20 is plausible for eval-awareness and we proceed. If no, we've learned the layer is wrong cheap, and can pivot before it's expensive to do so. Sanity dealbreaker check.

2. **Cross-model robustness instead of within-model layer sweep.** Anthropic released NLAs at the same depth ratio for Qwen-7B (layer 20), Gemma-3-12B (layer 32), Gemma-3-27B (layer 41), and Llama-3.3-70B (layer 53). Run the head-to-head across multiple models — train a competing probe for each NLA at its respective layer, plus a probe layer-sweep within each model. Cross-model replication is a stronger robustness story than within-model layer sweep — if the result holds across three model families, the field cares much more than if you optimised within one model. **Bonus:** the per-model probe layer-sweep also tells us whether any of these models happen to have their best probe layer right where the NLA is reading. If that happens for even one model, we get an apples-to-apples *and* best-vs-best comparison on that model for free, which is the cleanest possible version of the experiment.

3. **Be honest about the constraint in the writeup.** "Layer choice was fixed by the NLA release. We don't claim it's optimal for either method. We report the probe at the NLA's layer (matched comparison) and at its best-sweep layer (best-vs-NLA comparison) for each model." The transparency turns the constraint into a documented limitation rather than a hidden flaw, and it gives readers the data to interpret the result however they want.

The net effect: the project's headline becomes a multi-model comparison rather than a single-model one, which is genuinely more useful to the field and doesn't cost much extra. Compute scales with model size — Gemma-27B and Llama-70B are heavier than Qwen-7B and may need to be scoped down based on what the hardware can handle, but Qwen-7B + Gemma-12B is comfortably in reach.

## Mentor-chat recap (the plain-English version)

The chill recap of where we landed after talking the whole thing through.

**Fundamentals (the mental model):**

- A linear probe is just a direction in the residual stream space. Dot-product an activation with it, you get one number per token. That number tells you how much the activation points in that direction.
- The residual stream isn't "neurons lighting up" — it's the model's running representation at that token, at that layer, built from the token's own embedding plus everything attention has pulled in from earlier tokens.
- A probe is layer-specific. Train it at layer 20, use it at layer 20. Different layer = different space.
- Probes can be applied to any token position at the trained layer, but they only work well at the token positions they were trained on.
- AUROC is the threshold-free "how separable are the two distributions" measure. Report that, then optionally pick a threshold for operational use (e.g. 1% false positive rate).

**The shape of the actual experiment:**

- Pick a target — eval-awareness — and a model — Qwen-2.5-7B.
- Train the probe at layer 20 (where the released NLA reads), using a few hundred labelled eval-vs-deployment prompts. Difference of means is the simplest recipe.
- Build the labelled training set from public sources: SAD + benchmark prompts on the eval side, WildChat or similar on the deployment side. A day of mechanical work, not a research project.
- Run both methods (probe and NLA) on actual eval prompts and a deployment baseline. Count how often each flags eval-awareness. That gives the headline comparison.
- Find disagreement cases. Use behaviour, steering, or format stress-tests to figure out who's right.

**Empirical risks (the genuine ones, not hand-wavy):**

- The released NLA is locked to layer 20 (two-thirds depth). We don't choose. Anthropic picked it as a general-purpose default, and their own Claude eval-awareness results used roughly the same depth — so plausibly it'll work for Qwen too, but not guaranteed. Worth a quick pilot to sanity-check before committing.
- Two layers of flakiness: layer 20 might be sub-optimal for the NLA on Qwen, and it might be sub-optimal for an eval-awareness probe on Qwen. Either could weaken the headline.
- The way out: do *two* probe comparisons. One at layer 20 (apples-to-apples, answers the theoretical question), one at the probe's best layer found by sweep (apples-to-best-apples, answers the practical question). If they tell the same story, robust result. If they diverge, the contrast itself is the headline.
- Format confound is the elephant in both methods' rooms. Devbunova showed probes fire 94.5% on benchmark-formatted deployment content. We don't know if NLA has the same issue. A stress test where you run both methods on deployment-content-in-benchmark-format is the cleanest way to find out, and it'd be a real contribution either way.

**The dataset thing, demystified:**

- There's no canonical "eval-awareness dataset." The field is too young and the definition is too fuzzy.
- We need labelled data *only* for training the probe, and it's a stitch-together job from public sources.
- Testing is on existing benchmarks — no labelling needed.
- Needham's 1000-transcript benchmark is the best off-the-shelf candidate if it's released. Worth verifying.

**The point of the study, in one line:**

The NLA paper made two specific theoretical claims about probes (NLAs see what probes can't / probes hallucinate less than NLAs) and tested neither. The study finds the cases where the two methods disagree on eval-awareness detection, and uses behaviour and stress-tests to figure out which claim wins where — turning a vague "NLAs are richer" pitch into concrete evidence about when each method is the right tool.

## Open questions

- Eval-awareness vs sycophancy vs refusal as the target — which gives the cleanest behavioural-divergence signal?
- How many disagreement cases do we need to feel confident? Rough target — dozens, not thousands.
- Tiebreaker reliability — pilot the behavioural-divergence check first on agreement cases to calibrate the noise floor.
- Should we also run the NLA on activations the probe was trained on, to check the NLA's verbalisations match what the probe direction is doing? Could be a useful sanity check before going hunting for disagreements.
