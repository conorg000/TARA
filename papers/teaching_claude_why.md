# Teaching Claude why

**Authors:** Anthropic (specific leads not surfaced in post)
**Year:** 2026 (May)
**Source:** [anthropic.com/research/teaching-claude-why](https://www.anthropic.com/research/teaching-claude-why)
**Status:** read

---

## Summary (in our words)

A training-methodology paper. The core move is to train models on data that includes *explanations* of why a behavior is or isn't aligned, rather than just demonstrations of the behavior itself. Three concrete interventions: (1) a "difficult advice" dataset where users face ethical dilemmas and receive reasoned guidance, (2) document training on Anthropic's constitution and on fiction depicting aligned AI behavior, (3) diverse RL environments with varied tool definitions and system prompts.

The headline numbers are large: previous models had blackmail rates up to 96% in agentic-misalignment evals; current models score 0%. The "difficult advice" dataset achieves comparable misalignment reduction with 28× fewer tokens than synthetic honeypot data. Constitutional document training reduces blackmail from 65% to 19%.

For our project this is a mitigation paper rather than a phenomenon or methods paper. The motivating argument is that *generalization is the hard part of alignment*: a model trained on demonstrations of aligned behavior may overfit to those exact contexts, while a model trained on explanations of *why* something is aligned can generalize to new contexts. This is an alignment story orthogonal to the eval-gaming threat we care about — it's about getting alignment to hold out-of-distribution, not about whether evaluation channels can detect when alignment fails.

The paper makes no use of probes, activation analysis, or internal-state methods. Everything is training data + behavioral evaluation. That's a notable gap given the alignment-faking literature ([[alignment_faking]], [[in_context_scheming]]) that suggests behavioral training can shift surface behavior without altering underlying preferences. Whether "teaching Claude why" changes the model's internal representations of these behaviors, or just its policy on top of those representations, is unaddressed.

## Key experimental conditions

- Models: Claude Haiku 4.5, Sonnet 4.5, Opus variants
- Training interventions: "difficult advice" dataset; constitution + aligned fiction; diverse RL environments
- Evaluations: agentic misalignment evals (blackmail, sabotage, framing), automated alignment assessment, constitution adherence

## Key quantitative results

- Blackmail rates: from 96% (Opus 4) → 0% (current)
- Direct honeypot training: 22% → 15% misalignment; adding ethical reasoning → 3%
- "Difficult advice" dataset: 28× more token-efficient than synthetic honeypot equivalents
- Constitutional document training: blackmail 65% → 19%

## Methods (what they did and didn't use)

- Training data composition (the primary intervention)
- Behavioral evaluation across multiple misalignment scenarios
- No probes, no internal-state analysis, no mechanistic interpretability
- No measurement of whether the training changes internal representations vs. just behavioral policy

## Authors' stated limitations / future work

- "Alignment remains an unsolved problem"
- Current auditing methodology not sufficient to rule out catastrophic autonomous action
- Scalability to more capable models uncertain
- Call for "further work attempting to understand more deeply why the methods we've described work so well"

## Our own follow-up thoughts (project-relevant)

1. **The unaddressed question is the project-relevant one.** The paper reports large behavioral wins from explanation-based training but doesn't measure whether the underlying representations of misaligned dispositions have actually been removed, or just suppressed under typical inputs. A probe-based follow-up would ask: does a probe trained to detect "blackmail-relevant internal state" on the pre-trained model still fire on the post-trained model when the input would otherwise elicit blackmail? If the probe still fires but behavior changes, behavioral training is a gating mechanism rather than a deletion mechanism — exactly the failure mode that motivates eval-gaming concern. Out of scope for our 3-week project but a clear future-work direction.

2. **Useful framing for the writeup.** This paper is the strongest current evidence that behavioral alignment training works at the *behavioral* level. Our project's contribution becomes: even when behavioral training succeeds at this level, we don't know what's happening internally — and the eval-gaming threat model says we need to. The two halves complement each other rather than competing.

## Relevance to our project

Low-medium. Not methodologically relevant; the project doesn't need it as scaffolding. But it's the strongest evidence we have that behavioral alignment training works well *behaviorally* — which is the setup for asking whether the internal-state story matches the behavioral story.

Pairs with: [[alignment_faking]] (the threat the training is trying to defeat), [[in_context_scheming]] (same).
