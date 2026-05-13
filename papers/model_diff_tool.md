# A "diff" tool for AI: Finding behavioral differences in new models

**Authors:** Thomas Jiralerspong (Anthropic Fellows), Trenton Bricken (Anthropic Alignment Science)
**Year:** 2026 (March)
**Source:** [anthropic.com/research/diff-tool](https://www.anthropic.com/research/diff-tool)
**Status:** read

---

## Summary (in our words)

A cross-architecture model-diffing technique called the Dedicated Feature Crosscoder (DFC). It decomposes two models into shared features plus model-exclusive features and surfaces behaviors that exist in one but not the other. The goal is to catch "unknown unknowns" — emergent behaviors that standard safety evaluations would miss because nobody knew to look for them.

The illustrative finding: when run on pairs of Chinese and American open-weight models (Llama-3.1-8B vs. Qwen3-8B, etc.), the method rediscovers a "CCP alignment" feature in 5 of 5 test runs across Chinese models, and an "American Exceptionalism" feature in 4 of 5 runs. Both are politically-tuned behaviors not explicit in either model's documentation. The authors validate the features causally by suppressing them during generation and confirming the behavioral changes.

The broader claim is that standard behavioral evaluations are reactive — they only catch what evaluators thought to test for — while internal-feature comparison can be proactive, surfacing differences that nobody knew to query. A probe or feature in this framing is a one-dimensional diff between two distributions over model behavior.

## Key experimental conditions

- Models: Llama-3.1-8B-Instruct, Qwen3-8B, GPT-OSS-20B, DeepSeek-R1-0528-Qwen3-8B
- Method: DFC architecture with shared-feature section plus per-model exclusive sections
- Validation: activation steering / suppression of identified features to confirm causal role

## Key quantitative results

- "CCP alignment" feature: rediscovered in 5 of 5 runs across Chinese models
- "American Exceptionalism" feature: 4 of 5 runs
- Thousands of features surfaced per run; only a small fraction represent meaningful safety signals — filtering is a real workflow cost

## Methods (what they did and didn't use)

- Cross-architecture feature decomposition (crosscoder family)
- Activation steering for causal validation
- No SAEs explicitly mentioned but the crosscoder is in the same lineage
- Behavioral evaluation as the downstream check

## Authors' stated limitations / future work

- "Not a silver bullet" — many features surfaced, filtering needed
- Method doesn't determine whether features arose deliberately or emergently
- Tested on open-source only; untested on frontier models
- Future: monitor models across updates to catch behavioral drift before deployment (cites OpenAI GPT-4o sycophancy as the kind of issue that could have been caught)

## Open questions and follow-up directions

1. **Scaling to frontier models.** The validation set is open-weight 8B–20B models. Whether the DFC remains tractable and informative on frontier-scale models — where the feature count and training cost grow substantially — is the obvious next test. The political-alignment features may also be unusually clean compared with subtler behavioural differences a method like this would need to surface.

2. **Filtering thousands of features down to safety-relevant ones.** The method reports thousands of features per run; only a small fraction are meaningful. The paper does not propose a principled filtering procedure. Automating triage — ranking features by causal effect size, behavioural breadth, or anomaly relative to a baseline — is a methodological gap.

3. **Diffing fine-tuning steps rather than separate models.** The most policy-relevant use case is monitoring a single model across training/fine-tuning updates to catch behavioural drift early. The released work diffs across architectures; the within-lineage version (same base, two fine-tunes) is a natural and probably cleaner application and could expose behaviours like sycophancy or sandbagging that fine-tuning is known to induce.

4. **Deliberate vs. emergent feature attribution.** Authors note the method cannot tell whether a surfaced feature was deliberately trained in or emerged from data. Combining the DFC with training-data attribution methods (influence functions, data poisoning analogues) would address this.

5. **Comparison with cheaper baselines.** It is not clear how much of the DFC's value over simpler baselines (linear probes trained on behavioural contrasts, persona-vector-style mean-difference directions, paired-prompt activation diffing) survives careful comparison. A baseline study would clarify when the full crosscoder machinery is necessary.

## See also

- [[persona_vectors]] — smaller-scale version of the same intuition: a single direction captures a behavioural axis distinguishing model variants
- [[sleeper_agent_probes]] — internal-feature methods catching behaviour that behavioural evals miss
- [[steering_eval_aware]] — activation steering as causal validation of a candidate feature
- [[beyond_linear_probes]] — methodological alternatives when linear directions are insufficient
- [[eliciting_secret_knowledge]] — adjacent problem of surfacing model knowledge or behaviour that is not externally visible
