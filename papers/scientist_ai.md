# Superintelligent Agents Pose Catastrophic Risks: Can Scientist AI Offer a Safer Path?

**Authors:** Bengio et al.
**Year:** 2025
**arXiv:** [2502.15657](https://arxiv.org/abs/2502.15657)
**Status:** read (abstract / position paper — no empirical setup to replicate)

---

## Summary (in our words)

A position paper, not an empirical one. The argument: current AI development is converging on autonomous *agents* — systems with goals, planning capability, and action affordances — and this trajectory is dangerous because agentic systems are precisely the kind that can develop deceptive, self-preserving, or otherwise misaligned behaviors. The proposed alternative is "Scientist AI" — non-agentic systems built to *explain* observations via world models and uncertainty-aware reasoning, rather than to *act* autonomously toward goals.

The framing matters for how eval-gaming and related risks get located in the broader story. A model that "knows" it's being evaluated and strategically modulates its behavior is, by definition, exercising a kind of goal-directed agency over its own outputs. The Bengio et al. position is that this whole class of risks is downstream of the choice to build agentic systems in the first place. If agentic systems are going to be built and deployed regardless, the question of whether their internal states match their outputs becomes load-bearing for safety.

There's no experimental setup, no quantitative results, no methodology to adopt or reproduce. This is a framing/position piece.

## Methods

Position paper. No experimental work.

## Authors' stated future work

Calls for research on non-agentic AI architectures and on whether such systems can deliver the benefits of current approaches without the catastrophic-risk profile.

## Open questions and follow-up directions

1. **Operationalising "non-agentic."** The Scientist AI proposal rests on a clean distinction between systems that *explain* and systems that *act*, but modern LLMs blur this — a base model used as a tool can be wrapped into an agent without retraining. Whether "non-agentic" can be enforced architecturally, or only behaviourally/procedurally, is unresolved.

2. **Capability-equivalence of non-agentic systems.** The argument assumes Scientist-AI-style systems can deliver enough of the economic and scientific benefits of agentic systems to be a real alternative. Whether that's empirically true, or whether the agentic affordances are doing load-bearing work for the useful capabilities, is open and largely unexamined.

## See also

- [[alignment_faking]] — concrete behavioural instance of the agentic-risk class this paper argues against
- [[in_context_scheming]] — phenomenology of goal-directed deception in current frontier models, sharpening what "agentic risk" looks like empirically
- [[cot_monitorability]] — adjacent proposal that constrains *how* agentic systems reason rather than whether they are agentic at all
