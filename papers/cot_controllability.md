# Reasoning Models Struggle to Control their Chains of Thought

**Authors:** Chen Yueh-Han, McCarthy, Lee, He, Kivlichan, Baker, Carroll, Korbak
**Year:** 2026
**arXiv:** [2603.05706](https://arxiv.org/abs/2603.05706)
**Status:** read

---

## Summary (in our words)

This paper asks a sharp question about CoT monitorability: even if today's reasoning models *would* benefit from hiding strategic content in their chain of thought, can they actually do it? The authors introduce CoT-Control, an evaluation suite where models must solve a problem while obeying an instruction about what their CoT may or may not contain (e.g. answer a genetics question without using the word "chromosome"). The headline finding: there is a large gap between models' ability to control their *final output* and their ability to control their *CoT*. Claude Sonnet 4.5 controls its final output 61.9% of the time but its CoT only 2.7% of the time.

That gap is robust across the variants the authors test. It persists when models are given incentives to evade a monitor rather than direct instructions. It persists, with only mild improvement, when models are told they are being monitored. It is not eliminated by adversarial prompt optimization. And it gets *worse* — i.e. CoT becomes harder to control — with more RL training, more test-time compute, and harder problems. Larger models are somewhat more controllable than smaller ones, which complicates the simple "scaling makes this worse" narrative.

The framing is deliberately monitorability-positive. Korbak is a co-author and a lead author on [[cot_monitorability]]; this paper is in some sense the empirical companion piece. If reasoning models can't deliberately suppress content from their CoT, then CoT monitoring is harder to defeat than the worst-case threat model assumes — at least with current models, current training pressure, and current elicitation methods. The authors are cautious: they call this "cautiously optimistic," explicitly note that the mechanism behind the controllability gap is not understood, and recommend frontier labs track CoT controllability as a model-property metric.

The contribution we'd highlight is the *measurement framing*: CoT controllability as an evaluable capability separate from CoT faithfulness. [[cot_faithfulness]] measures whether models verbalize what they used; this paper measures whether they can *not* verbalize what they used when instructed. The two together delineate the threat model — unfaithful CoT can happen by default (faithfulness), and deliberate concealment is the worst case (controllability) — and this paper provides the first systematic numbers on the latter.

## Key experimental conditions

- CoT-Control evaluation suite: problems paired with CoT-content constraints (e.g. answer without using a specific word). Distinct from output constraints, which are the standard instruction-following measurement
- Claude Sonnet 4.5 prominently featured; multiple other reasoning models compared across sizes and training regimes
- Conditions tested:
  - Direct request vs. incentive-based framings (model rewarded for evading CoT monitor rather than told to do so)
  - Monitoring-awareness conditions (told vs. not told that CoT is being monitored)
  - Adversarial prompt optimization to elicit higher controllability
  - Varied model size, RL training extent, test-time compute budget, problem difficulty

## Key quantitative results

- Claude Sonnet 4.5: 2.7% CoT controllability vs. 61.9% output controllability — ~23× gap
- Larger models: higher controllability than smaller ones (so the gap is not a pure capability ceiling)
- More RL training, more test-time compute, harder problems → lower CoT controllability
- Incentive framings: roughly comparable failure rates to direct requests
- Monitoring-awareness: slight increase in controllability when models told they are being monitored, not enough to close the gap
- Adversarial prompt optimization: does not meaningfully raise CoT controllability

## Methods (what they did and didn't use)

- Behavioural evaluation suite construction; instruction-following measurement with a CoT-content predicate as the constraint
- Comparison across models, training regimes, test-time compute, problem difficulty as the main analytical axes
- Adversarial prompt search as a stress test against "the right elicitation would unlock the capability" objections
- **No linear probes, no activation steering, no SAEs, no NLA-style verbalization of internal states.** All evidence is behavioural. The authors explicitly note the underlying mechanism is not understood
- Closed-weight frontier models — Claude Sonnet 4.5 etc. — so the activation-level question is gated by lab-internal access

## Authors' stated limitations / future work

- The mechanism underlying low CoT controllability is not understood
- Authors recommend that frontier labs track CoT controllability as a metric in future model development
- Implicit limitations: results depend on the CoT-Control task design (constraints expressible as word-level avoidance); whether the gap generalizes to more semantically rich concealment targets is not directly tested

## Open questions and follow-up directions

1. **Mechanism behind the controllability gap.** The paper documents a robust behavioural asymmetry but offers no account of *why* models can suppress words from their final answer but not from their CoT. Candidate explanations — CoT tokens are less monitored during RL, suppression requires a distinct planning-style capability the models lack, the CoT is more committed to specific reasoning trajectories — are not distinguished here. Internal-state methods that compare hidden-content representations during constrained vs. unconstrained CoT generation would be the natural next step.

2. **Generalization beyond word-level constraints.** CoT-Control instructs models to avoid specific words. Real-world concealment by a scheming model would involve avoiding *concepts* or *reasoning patterns* — e.g. "do not reveal that you are reasoning about whether this is an evaluation." Whether the 23× gap holds for semantic / concept-level concealment, or whether word-level concealment is the hardest case, is open.

3. **Scaling trajectory of the gap.** Larger models are *more* CoT-controllable, but more RL training and more test-time compute make CoT *less* controllable. These trends could collide: future models scaled in all dimensions might pass a threshold. The paper's data are consistent with both "the gap is durable" and "the gap will close at some scale," and the recommendation to track this metric is exactly the bet that the trajectory matters.

4. **What the result implies for CoT-faithfulness work.** [[cot_faithfulness]] shows models often don't verbalize what they used. This paper shows they can't easily *not* verbalize when instructed. Combined, the picture is that unfaithfulness is a default-mode feature, not a strategic capability that current models can deploy on demand. Whether default-mode unfaithfulness can be exploited by training pressure (rather than prompting) to become more strategic-like is a follow-up the controllability framing does not resolve.

5. **Replication on open-weight reasoning models.** All reported numbers are on Anthropic-family frontier models. Whether DeepSeek R1, Qwen reasoning models, or smaller open-weight reasoners show the same gap is needed both for community replication and to enable the internal-state analysis (1) calls for.

## See also

- [[cot_monitorability]] — direct companion: the position paper that argues CoT monitorability is fragile but worth preserving; this paper supplies empirical evidence that one specific failure mode (deliberate concealment) is currently rare
- [[cot_faithfulness]] — the sibling failure mode: unfaithful CoT by default, vs. this paper's *controllable* CoT on demand. Together they bracket the threat model
- [[anti_scheming_training]] — case where the load-bearing inference depends on CoT being readable; consistent with current models lacking the controllability to defeat that inference
- [[in_context_scheming]] — relies on scratchpad evidence to attribute scheming; the low CoT controllability finding strengthens the scratchpad-as-evidence channel
- [[steering_eval_aware.md]] — adjacent threat-model framing: internal eval-awareness can be steered out of behaviour, and would presumably also be the hardest content to keep out of CoT under controllability pressure
- [[introspection]] — orthogonal capability: whether models can accurately report internal state. Controllability is the inverse question: whether they can deliberately *not* report
- [[eliciting_secret_knowledge]] — methods for extracting model-held information the model does not verbalize; complementary to controllability as a measurement axis
