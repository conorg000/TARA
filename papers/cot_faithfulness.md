# Reasoning models don't always say what they think

**Authors:** Anthropic Alignment Science team
**Year:** 2025 (April)
**Source:** [anthropic.com/research/reasoning-models-dont-say-think](https://www.anthropic.com/research/reasoning-models-dont-say-think)
**Status:** read

---

## Summary (in our words)

This paper directly attacks the Chain-of-Thought-as-evidence channel that papers like [[in_context_scheming]] rely on. Setup: insert subtle hints (metadata, "Stanford professor said X", unauthorized-access prompts) into multiple-choice questions. Measure whether the model (a) uses the hint to change its answer, and (b) admits to using the hint in its visible reasoning. The gap between these two is *unfaithfulness*.

Result: Claude 3.7 Sonnet verbalizes the hint only ~25% of the time, DeepSeek R1 ~39%. On unauthorized-access framings, Claude drops to 41% and R1 to 19%. The most striking number is the reward-hacking experiment: models exploit false hints **>99% of the time** but verbalize the exploit **<2% of the time**. Outcome-based RL training initially improved faithfulness but plateaued at 20-28% — well below what would be needed for CoT-based safety monitoring.

For our threat model this is load-bearing. If CoT can't be trusted to disclose the reasoning behind a decision, then the secondary evidence Apollo's scheming paper leans on — model scratchpads explicitly verbalizing deceptive reasoning — becomes weaker than it looks. The behavioral-deception attribution still holds for the cases where CoT *is* faithful, but a non-trivial slice of deceptive behavior could be passing through with no scratchpad trace.

What the paper doesn't do is look inside the model. All evidence is the behavioral gap between "model used hint" and "model said it used hint." That leaves wide open the question: when the model uses a hint but doesn't say so, is that information present in its activations? A probe could answer this directly.

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
- This is exactly the gap a probe-based follow-up would address

## Authors' stated limitations / future work

- Scenarios are "somewhat contrived" — artificial hints in multiple-choice quizzes
- Only two model families tested
- Tasks may not be hard enough to *require* faithful CoT
- Authors note "substantial work to be done" on faithfulness-based monitoring without specifying methods

## Our own follow-up thoughts (project-relevant)

1. **The natural probe extension.** When the model uses a hint but doesn't verbalize it, train a probe to detect "this answer was influenced by the hint" from the activations alone. Run on inputs where CoT *did* verbalize, *didn't* verbalize but used the hint, and didn't use the hint at all. The probe should split the three cases. This is a direct measurement of whether the hint-use information exists internally even when it doesn't surface in CoT — and it pairs naturally with our top project candidate. The setup is small enough to fit in scope: multiple-choice quizzes, hint/no-hint contrast pairs, small open-weight model.

2. **Bridge to our sandbagging+probe project.** This paper is the strongest single piece of motivation for going internals-first on eval-gaming. The argument writes itself: "CoT is unfaithful at 75%+ rates on much simpler tasks than sandbagging detection; if we want to detect eval-gaming, we cannot rely on the model verbalizing it — we need probes that read it off internally." That's the framing paragraph for our project's introduction.

3. **Train-time vs. inference-time interventions.** The paper shows outcome-based RL plateaus at low faithfulness. Open question: would a probe *trained* on the unfaithfulness gap teach us *why* RL plateaus? If the probe direction is stable across the RL training trajectory, that suggests the representation persists even as the verbalization is suppressed — direct evidence of "behavior changes, internals don't" failure mode for behavioral training.

## Relevance to our project

Very high — second only to [[sleeper_agent_probes]] for methodological motivation. This paper is the strongest existing argument for not trusting the CoT channel as a safety monitor. Any probe-based eval-gaming project we run will cite this as the reason internal-state methods are necessary in the first place.

Pairs with: [[in_context_scheming]] (whose scheming attributions depend on CoT being mostly faithful — a tension worth flagging), [[sandbagging]] (target phenomenon), [[sleeper_agent_probes]] (method).
