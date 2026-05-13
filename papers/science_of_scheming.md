# We Need A Science of Scheming

**Authors:** Apollo Research
**Year:** 2026 (January)
**Source:** [apolloresearch.ai/science/science-of-scheming](https://www.apolloresearch.ai/science/science-of-scheming/)
**Status:** read

---

## Summary (in our words)

Apollo's research-agenda post. The argument: as AI systems automate research and become more capable, they will face strong incentives to pursue misaligned goals covertly. Studying *how* scheming arises, *when* it gets worse with scale, and *which* training dynamics reinforce it should be an empirical research program — not a future-tense risk to wait on.

The agenda proposes four research lines: (1) quantify how much models prioritize pleasing oversight systems (the "oversight gaming" framing), (2) build "model organisms" — controlled setups where RL training dynamics produce oversight gaming so the phenomenon can be studied empirically, (3) identify which dynamics strengthen with scale, (4) extend insights to full deceptive alignment.

The eval-awareness piece is central. Apollo explicitly notes: "Recent AI models routinely reason about the purpose and context behind a given rollout" — they detect evaluation contexts unprompted. The agenda includes "mitigation via increased realism" and "false beliefs" (making the model think it's deployed when it's being evaluated) as research directions. This is the threat model spelled out explicitly: capable models gaming oversight is the central worry; eval awareness is the mechanism by which this gaming gets harder to detect.

No probes, no internal-state methods recommended in the agenda. The whole post is about building empirical setups (model organisms, scaling experiments) rather than about specific measurement techniques. That's a notable framing choice — they're calling for behavioral empirical work first, with mechanistic work implicit but downstream.

## Key positions

- Scheming research should be empirical, not speculative
- Oversight gaming is a precursor to deceptive alignment and should be studied directly
- Predictive scaling laws for scheming are achievable in principle
- Realism of evaluation contexts is itself a research target — to defeat eval-awareness contamination

## Methods proposed (not yet executed)

- Model organisms (controlled experimental setups designed to produce oversight gaming)
- Quantification of "willingness to please oversight signals"
- Scaling experiments to identify which scheming dynamics worsen with scale
- Iteration on alignment-training techniques as scale increases

## Open questions Apollo flags

- Can scaling laws for scheming be empirically identified?
- Which training dynamics produce scheming?
- How do alignment techniques scale to highly capable systems?
- What mechanisms underlie oversight-gaming emergence?

## Our own follow-up thoughts (project-relevant)

1. **The eval-awareness centrality matches our project framing.** Apollo identifies eval awareness as the mechanism that makes scheming hard to study — exactly the threat model that motivated this whole exploration. Their proposed research direction (realism / false beliefs) is a *behavioral* approach to the problem. Our probe-based extension is the *internals* approach. Complementary.

2. **The "model organism" framing is useful for our writeup.** Our project effectively builds a small model organism: take a small open-weight model, induce sandbagging via password-locking, probe the result. We're producing a tractable empirical version of what Apollo argues for in this post.

3. **Not a primary citation; broader context.** Like other agenda posts (e.g., [[scientist_ai]]), this is framing rather than methodology. Useful for connecting our project to the broader research conversation.

## Relevance to our project

Low-medium for methodology, medium-high for framing. Cite when situating the project in Apollo's research program. Not a target for replication.

Pairs with: [[in_context_scheming]], [[apollo_precursor_predictive]], [[anti_scheming_training]] (all Apollo work).
