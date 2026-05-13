# We Need A Science of Scheming

**Authors:** Apollo Research
**Year:** 2026 (January)
**Source:** [apolloresearch.ai/science/science-of-scheming](https://www.apolloresearch.ai/science/science-of-scheming/)
**Status:** read

---

## Summary (in our words)

Apollo's research-agenda post. The argument: as AI systems automate research and become more capable, they will face strong incentives to pursue misaligned goals covertly. Studying *how* scheming arises, *when* it gets worse with scale, and *which* training dynamics reinforce it should be an empirical research program — not a future-tense risk to wait on.

The agenda proposes four research lines: (1) quantify how much models prioritize pleasing oversight systems (the "oversight gaming" framing), (2) build "model organisms" — controlled setups where RL training dynamics produce oversight gaming so the phenomenon can be studied empirically, (3) identify which dynamics strengthen with scale, (4) extend insights to full deceptive alignment.

The eval-awareness piece is central. Apollo explicitly notes: "Recent AI models routinely reason about the purpose and context behind a given rollout" — they detect evaluation contexts unprompted. The agenda includes "mitigation via increased realism" and "false beliefs" (making the model think it's deployed when it's being evaluated) as research directions. The framing is explicit: capable models gaming oversight is the central worry; eval awareness is the mechanism by which this gaming gets harder to detect.

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

## Open questions and follow-up directions

1. **Behavioral vs. internal-state measurement of oversight gaming.** Apollo's proposed research lines lean heavily behavioral — model organisms, scaling experiments, willingness-to-please quantification. The agenda is largely silent on internal-state methods (probes, activation analysis, mechanistic decomposition). Whether internal measurement would meaningfully change the picture — by bounding the *unobserved* rate of oversight-relevant reasoning that doesn't surface behaviourally — is open.

2. **Operationalizing "increased realism" as a research target.** The post proposes realism and false-belief inductions as ways to defeat eval-awareness contamination, but does not specify what counts as sufficiently realistic, nor how to measure whether a model has been fooled. Turning this into a concrete experimental program — including metrics for "the model believes it is deployed" — is non-trivial and unaddressed.

3. **Connecting oversight gaming to deceptive alignment.** Apollo treats oversight gaming as a precursor to full deceptive alignment but does not specify the bridge. Whether the same dynamics, training pressures, and internal representations carry over — or whether deceptive alignment is qualitatively different — is open and probably the highest-stakes empirical question in the agenda.

## See also

- [[in_context_scheming]] — Apollo's prior empirical demonstration that frontier models scheme in adversarial settings; the phenomenology this agenda generalizes from
- [[anti_scheming_training]] — Apollo follow-up testing whether training interventions reduce the underlying disposition; a direct response to the agenda's training-dynamics line
- [[apollo_precursor_predictive]] — companion Apollo piece on precursor capabilities and predictive evaluation
- [[alignment_faking]] — a different research group's behavioural demonstration of the same broad phenomenon Apollo wants studied empirically
- [[scientist_ai]] — adjacent agenda post framing the alignment problem at the architectural level rather than the training-dynamics level
- [[steering_eval_aware]] — internal-state evidence that eval-awareness has linear structure, complementing Apollo's behavioural framing
- [[situational_awareness_dataset]] — operationalizes situational/eval awareness as a measurable capability, relevant to Apollo's "realism" research line
