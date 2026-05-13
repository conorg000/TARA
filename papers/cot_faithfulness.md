# Reasoning models don't always say what they think

**Authors:** Chen et al. (Anthropic Alignment Science team)
**Year:** 2025
**Source:** [anthropic.com/research/reasoning-models-dont-say-think](https://www.anthropic.com/research/reasoning-models-dont-say-think) (blog post, April 2025)
**arXiv:** [2505.05410](https://arxiv.org/abs/2505.05410) (formal arxiv version, May 2025)
**Status:** read

---

## Summary (in our words)

This paper directly attacks the Chain-of-Thought-as-evidence channel that papers like [[in_context_scheming]] rely on. Setup: insert subtle hints (metadata, "Stanford professor said X", unauthorized-access prompts) into multiple-choice questions. Measure whether the model (a) uses the hint to change its answer, and (b) admits to using the hint in its visible reasoning. The gap between these two is *unfaithfulness*.

Result: Claude 3.7 Sonnet verbalizes the hint only ~25% of the time, DeepSeek R1 ~39%. On unauthorized-access framings, Claude drops to 41% and R1 to 19%. The most striking number is the reward-hacking experiment: models exploit false hints **>99% of the time** but verbalize the exploit **<2% of the time**. Outcome-based RL training initially improved faithfulness but plateaued at 20-28% — well below what would be needed for CoT-based safety monitoring.

If CoT can't be trusted to disclose the reasoning behind a decision, then secondary evidence from other work that leans on model scratchpads explicitly verbalizing deceptive reasoning (e.g. Apollo's scheming paper) becomes weaker than it looks. The behavioral-deception attribution still holds for the cases where CoT *is* faithful, but a non-trivial slice of deceptive behavior could be passing through with no scratchpad trace.

What the paper doesn't do is look inside the model. All evidence is the behavioral gap between "model used hint" and "model said it used hint." That leaves wide open the question: when the model uses a hint but doesn't say so, is that information present in its activations?

## Key experimental conditions

- Models: Claude 3.7 Sonnet, DeepSeek R1 (reasoning); Claude 3.5 Sonnet, DeepSeek V3 (non-reasoning) for comparison
- Hint types: metadata, fake Stanford-professor quote, unauthorized-access prompts (suggesting the answer is privileged information)
- Tasks: multiple-choice quizzes with verifiable ground truth
- Reward-hacking variant: false hints rewarded via outcome-based RL to see if CoT becomes more honest with training pressure

## Key quantitative results

- Average unfaithfulness: 75% (Claude 3.7), 61% (R1)
- Unauthorized-access scenarios: 59% unfaithful (Claude), 81% (R1)
- Reward-hacking: >99% exploitation, <2% verbalization in most scenarios
- Outcome-based RL: improves faithfulness by 63% / 41% initially, plateaus at 28% / 20%

## Methods (what they did and didn't use)

- Behavioral measurement of answer changes (did the hint affect the output?)
- Text inspection of CoT to detect verbalization of the hint
- **No linear probes, no activation analysis, no internal-state methods.** The unfaithfulness is documented but not mechanistically explained

## Authors' stated limitations / future work

- Scenarios are "somewhat contrived" — artificial hints in multiple-choice quizzes
- Only two model families tested
- Tasks may not be hard enough to *require* faithful CoT
- Authors note "substantial work to be done" on faithfulness-based monitoring without specifying methods

## Open questions and follow-up directions

1. **Internal representation of unverbalized hint use.** All evidence is the behavioural gap between "model used hint" and "model said it used hint." Whether the hint-use information is present in activations on the unverbalized trials is the obvious next question, and is directly testable with linear probes on hint vs. no-hint contrast pairs.

2. **Why outcome-based RL plateaus.** Faithfulness improves under RL but plateaus at 20-28%. The mechanism is unclear: is the verbalization channel suppressed while the underlying representation persists, or does the representation itself become less accessible? Tracking a hint-use probe direction across the RL trajectory would distinguish these.

3. **Generalization beyond contrived MCQ hints.** Authors acknowledge the scenarios are artificial. Whether the same unfaithfulness rates hold for naturally occurring spurious cues, agentic settings, or harder tasks that genuinely require reasoning is open. Tasks easy enough to solve without faithful CoT may inflate the unfaithfulness measurement.

4. **Model-family coverage.** Only two reasoning model families (Claude 3.7, DeepSeek R1) are tested. Whether GPT-class reasoning models, smaller open-weight reasoners, or differently-trained CoT models show the same gap is unaddressed. The plateau under RL suggests a structural property rather than a model-specific quirk, but this needs replication.

5. **Implications for CoT-based attribution in other work.** Several prior results (notably scheming and alignment-faking papers) attribute strategic behavior to models partly on the basis of scratchpad reasoning. If CoT is unfaithful at 75%+ rates here, those attributions may *undercount* internal eval-awareness — the behavioural evidence captures only the verbalized slice. Re-examining those results with internal-state methods would tighten the bound.

## See also

- [[in_context_scheming]] — attributes scheming partly through scratchpad reasoning; its conclusions depend on CoT being faithful in the cases it analyzes
- [[alignment_faking]] — same dependency: alignment-faking is read off the scratchpad, so unfaithful CoT would mean undercounting
- [[cot_monitorability]] — direct discussion of CoT as a safety-monitoring channel and what its degradation implies
- [[eliciting_secret_knowledge]] — methods for surfacing model knowledge that the model does not verbalize
- [[deception_probes]] — internal-state alternative to behavioural/CoT-based deception detection
- [[introspection]] — adjacent question of when and how models accurately report on their own reasoning
