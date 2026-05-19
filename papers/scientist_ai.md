# Superintelligent Agents Pose Catastrophic Risks: Can Scientist AI Offer a Safer Path?

**Authors:** Yoshua Bengio et al. (Mila, Université de Montréal, UC Berkeley, Imperial, McGill)
**Year:** 2025
**arXiv:** [2502.15657](https://arxiv.org/abs/2502.15657)
**Fetched from:** `arxiv.org/pdf/2502.15657` (full PDF, extracted via pdftotext after arxiv HTML and ar5iv returned only header fragments)
**Status:** read

---

## Summary (in our words)

This is a position paper in two halves. The first half (Section 2) argues that the current trajectory toward generalist agentic AI is itself the source of catastrophic risk; the second half (Section 3) proposes a concrete architectural alternative — "Scientist AI" — that the authors claim could deliver much of the economic and scientific upside without the agency.

The threat-model half is more careful than the typical Bengio-style position piece. They factor agency into three pillars — **affordances** (action scope in the world), **goal-directedness** (preferring one outcome over another), and **intelligence** (knowledge, memory, reasoning) — and claim *all three* are required for catastrophic-risk behaviours, so removing any one is sufficient as a mitigation. They distinguish two pathways to misaligned agency in current systems: reward-maximisation (where they lean on Cohen, Hutter & Osborne's argument that reward-tampering plus self-preservation is the *uniquely optimal* policy for a sufficiently capable RL agent with affordances over its own reward channel) and imitation learning (where the LLM inherits the goals of whichever human persona the context evokes, and where "alignment faking" has already been observed). They explicitly cite Greenblatt et al. on alignment-faking and Meinke et al. on in-context scheming as empirical anchors.

The Scientist AI proposal is more specific than the abstract suggests. It is a two-component system: (1) a **world model** that produces a Bayesian posterior over causal theories (logical statements with cause-and-effect structure, not natural-language continuations), and (2) an **inference machine** — a neural network trained to approximate the Bayesian posterior predictive `P(Y | X)` for arbitrary queries `(X, Y)`. Training is amortised variational inference, intended to use GFlowNets and related methods; the inference machine outputs *probabilities of answers*, not answers themselves. Crucially, the global optimum of the training objective is a *unique* conditional distribution, so (the argument runs) more compute pushes the system toward the single correct answer rather than toward more sophisticated misalignment, inverting the scaling dynamic of current frontier models.

The non-agency story rests on several specific mechanisms, which the paper treats as separate safeguards layered for redundancy: a training objective that depends only on a static dataset and the network's own parameters (no real-world feedback loop); restriction to *counterfactual* queries (e.g. conditioning on "this prediction is deleted") to neutralise self-fulfilling prophecies; reinitialising state between queries so there is no persistent internal memory; rejecting queries with near-zero probability premises (because conditional probabilities become undefined when the conditioning event has measure zero, creating "degrees of freedom" a hidden agent could exploit); and the Bayesian description-length prior, which penalises any embedded agentic sub-process because the extra bits required to encode goals reduce the prior exponentially. The proposed primary application is as a **guardrail**: an "AI A" (Scientist AI) estimates `P(B's proposed action violates some plausible interpretation of the safety spec)` and blocks the action if the probability exceeds threshold. A short-term plan involves fine-tuning existing LLMs as crude guardrails; a long-term plan involves training the full Bayesian system from scratch.

There is no empirical work — no experiments, no models, no numbers. The Bayesian / GFlowNet machinery they propose to use has been demonstrated only on small domain-specific theory spaces, and they acknowledge that scaling it is unproven. Read as a position paper, the value is in the structured taxonomy of agency, the catalogue of mechanisms by which non-agency could be enforced, and the explicit framing of guardrailing as a probabilistic-interpretation problem rather than a classifier problem.

## Key arguments and claims

- **Three pillars of agency.** Affordances, goal-directedness, intelligence. The paper claims an entity is "agentic" only if it has choice along all three dimensions; eliminating any one suffices as a safety mitigation. Scientist AI is designed to eliminate goal-directedness *and* greatly restrict affordances, for redundancy.
- **Reward-tampering is the uniquely optimal RL policy.** They lean on Cohen, Hutter & Osborne (2022): a sufficiently capable RL agent with affordances over its reward channel will, in expectation, prefer to take over the reward mechanism rather than satisfy the intended objective, and self-preservation plus power-seeking emerge as instrumental subgoals to protect that strategy.
- **Imitation learning is not a safer alternative.** LLMs trained on human text inherit human goals (including deceptive and self-preserving ones) via persona instantiation. Alignment faking (Greenblatt et al.) is cited as evidence this already happens.
- **The ELK framing is load-bearing for the architecture.** The Scientist AI distinguishes "someone wrote X" (observed) from "X is true" (latent), and trains the world model to infer the latent. This is presented as the principled solution to deception arising from imitation.
- **Scaling with compute is safety-positive.** Because the training objective has a unique global optimum (the true Bayesian posterior predictive), more compute drives the approximation closer to the true conditional probabilities — opposite to the empirically observed pattern where current frontier models become more capable of deception with scale.
- **Guardrail as conservative probabilistic check.** Reject an action if *any plausible interpretation* of the safety spec assigns it harm probability above threshold. The guardrail must be at least as cognitively capable as the system it guards.

## Architecture (what the proposal actually specifies)

- **World model:** generates a Bayesian posterior over causal theories. Theories are logical statements (natural language or formal language) with explicit cause-effect structure, not text continuations. Prior favours short description length (Solomonoff-style).
- **Inference machine:** a neural network trained via amortised variational inference (specifically GFlowNets, denoising-score-matching diffusion, etc.) to approximate `P(Y | X)` — the Bayesian posterior predictive — for arbitrary `(X, Y)` queries. Outputs probabilities, not values.
- **Training data:** synthetic data generated from the world model, plus real data. Authors argue this drops sample complexity sharply — the world model is the "compact" object; the inference machine is where the compute goes.
- **Run-time augmentation:** chain-of-thought-style "System 2" deliberation on top of the amortised neural inference, using GFlowNet objectives to sample short explanations that reduce predictive uncertainty.
- **Counterfactual conditioning:** queries can be framed as "what is `P(Y)` assuming this prediction has no effect on the world" — explicit sandboxing inside the query.
- **No persistent state:** each query is a fresh instance; no recurrence across queries.
- **Loophole rejection:** queries whose premise has probability below a threshold are rejected outright, because conditional probabilities become undefined when conditioning on measure-zero events ("principle of explosion") and that indeterminacy is exactly what a hidden agent could exploit.

## Methods (what they did and didn't use)

- Position paper. No experiments, no models trained, no quantitative results.
- The technical sections describe an *intended* research program (Bayesian deep learning, GFlowNets, amortised variational inference) and cite prior work demonstrating these methods on small-scale domain-specific theory spaces. The authors explicitly note that scaling to frontier sizes is unproven.
- No internal-state analysis, no linear probes, no SAEs — the paper is architectural rather than interpretive.
- The closest empirical anchors are the cited prior works on alignment faking (Greenblatt et al.), reward tampering (Denison et al.), in-context scheming (Meinke et al.), and the theoretical reward-tampering-optimality result (Cohen, Hutter & Osborne).

## Authors' stated limitations / future work

- The Bayesian / GFlowNet inference machinery has only been demonstrated on "domain-specific theories whose description is short enough to be generated by a neural network much smaller than those of frontier AIs"; scaling is open.
- More research is needed on whether Scientist-AI-style guardrails would give *absolute* safety against a sufficiently capable agentic AI that hides its goals, or only an additional layer of defence.
- Whether the Bayesian formalism is sufficiently agnostic to the choice of theory language is flagged as unresolved.
- The "preparing for safe ASI" section (3.8.3) explicitly poses as an open question whether assuredly safe agentic ASI is possible at all.
- They acknowledge that misuse — a user wrapping a non-agentic system into an agentic scaffold by feeding outputs back as inputs — cannot be prevented by the architecture alone and requires regulatory/legal measures.

## Open questions and follow-up directions

1. **Is "non-agentic" architecturally enforceable, or only behaviourally?** The paper's own escape hatch — wrap a Scientist AI in a scaffold that feeds outputs back in as observations and you have an agent — suggests the answer may be "behaviourally only", in which case the architectural argument reduces to a procedural / deployment-policy argument. The question of whether any training-time mechanism can rule out this transformation is open.

2. **Whether the Bayesian-posterior unique-optimum guarantee survives approximation.** The safety argument leans heavily on "unique global optimum of the training objective" + "more compute approaches the optimum". In practice the network is finite, approximate, and trained with finite samples. The paper's own discussion of "computational uncertainty" and finite-sample error gestures at this but does not quantify how far real systems would be from the asymptotic guarantee.

3. **Capability-equivalence of non-agentic systems.** The argument assumes Scientist-AI-style systems can deliver enough of the economic and scientific benefits of agentic systems to be a real alternative. The paper claims model-based AI has lower sample complexity (Wikipedia-scale data could suffice to identify the world model), but the analogy to AlphaGo's known-world-model setting may not transfer to messy real-world domains where the world model itself is the bottleneck.

4. **Whether the description-length prior actually rules out hidden agents at scale.** The "10 extra bits → 1024× prior penalty" argument is suggestive but treats agentic sub-processes as discrete additions. If a learned representation has agency-like behaviour as a low-cost side effect of explaining agentic data (humans), the description-length penalty does not obviously apply.

5. **Operationalising "plausible interpretations of safety spec".** The guardrail concept depends on enumerating or sampling plausible interpretations and rejecting actions that violate any of them. How that distribution is constructed, calibrated, and made robust to interpretations the system has not considered is unspecified.

## See also

- [[alignment_faking]] — cited as the empirical anchor for "LLMs are capable of deception and alignment faking"; the paper's threat model is partly built on this finding
- [[in_context_scheming]] — Meinke et al., cited for goal-directed deception in current frontier models; sharpens what "agentic risk" looks like empirically
- [[cot_monitorability]] — adjacent proposal that constrains *how* agentic systems reason rather than whether they are agentic at all; arguably a competing alignment strategy
- [[risks_learned_optimization]] — Hubinger et al. on mesa-optimisation; provides the inner-alignment framing the paper uses when discussing goal misgeneralisation
