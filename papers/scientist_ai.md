# Superintelligent Agents Pose Catastrophic Risks: Can Scientist AI Offer a Safer Path?

**Authors:** Bengio et al.
**Year:** 2025
**arXiv:** [2502.15657](https://arxiv.org/abs/2502.15657)
**Status:** read (abstract / position paper — no empirical setup to replicate)

---

## Summary (in our words)

A position paper, not an empirical one. The argument: current AI development is converging on autonomous *agents* — systems with goals, planning capability, and action affordances — and this trajectory is dangerous because agentic systems are precisely the kind that can develop deceptive, self-preserving, or otherwise misaligned behaviors. The proposed alternative is "Scientist AI" — non-agentic systems built to *explain* observations via world models and uncertainty-aware reasoning, rather than to *act* autonomously toward goals.

The framing matters for our project's framing. The eval-gaming threat model we care about is essentially an agency story: a model that "knows" it's being evaluated and strategically modulates its behavior is, by definition, exercising a kind of goal-directed agency over its own outputs. The Bengio et al. position is that this whole class of risks is downstream of the choice to build agentic systems in the first place. That doesn't change what our empirical project measures, but it sharpens why measurement matters — if we're going to keep building agentic systems, knowing whether their internal states match their outputs is load-bearing for safety.

There's no experimental setup, no quantitative results, no methodology to adopt or reproduce. This is a database entry for the *framing* of our project, not its methodology.

## Methods

Position paper. No experimental work.

## Authors' stated future work

Calls for research on non-agentic AI architectures and on whether such systems can deliver the benefits of current approaches without the catastrophic-risk profile.

## Our own follow-up thoughts (project-relevant)

1. **Useful for the motivation section of our writeup.** The Bengio framing connects our specific empirical question (do probes detect eval-gaming?) to the broader policy/architecture-level conversation about AI risk. One sentence in our intro could note: "Whether agentic systems will be deployed at scale is contested (Bengio et al., 2025); given that some will be, knowing whether their internal states are detectable from internals is necessary."

2. **Not a methodological influence.** Nothing here changes what we do in the 3 weeks. Useful citation, not a project anchor.

## Relevance to our project

Low (methodologically), medium (framing). One-citation paper for the writeup motivation. Not a target for replication or extension.

Pairs with: nothing methodological. Conceptually adjacent to [[alignment_faking]], [[in_context_scheming]] as broad-threat-model context.
