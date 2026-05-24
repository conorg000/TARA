# AbstentionBench: Reasoning LLMs Fail on Unanswerable Questions

**Authors:** Kirichenko, Ibrahim, Chaudhuri, Bell (FAIR at Meta)
**Year:** 2025
**arXiv:** [2506.09038](https://arxiv.org/abs/2506.09038)
**Fetched from:** `arxiv.org/html/2506.09038`
**Status:** read

---

## Summary (in our words)

The authors build a 20-dataset / 35,000+ question benchmark for the narrow but load-bearing question of *whether a model knows when not to answer*. They group the datasets into six abstention scenarios — Answer Unknown, False Premise, Stale, Subjective, Underspecified Context, Underspecified Intent — and score 20 frontier models (GPT-4o, o1, Gemini 1.5 Pro, the Llama 3.1/3.3 family up to 405B, Qwen 2.5 32B, Mistral 7B, OLMo 7B, plus reasoning variants DeepSeek R1 Distill Llama 70B and s1.1 32B) with an LLM-as-Judge (Llama 3.1 8B Instruct, validated at 88% agreement with human labels on a sample of GPT-4o and Llama 3.1 70B responses).

The three findings that matter: (1) abstention does not get solved by scale — Llama 8B → 70B → 405B is essentially flat on mean abstention recall; (2) **reasoning fine-tuning actively *hurts* abstention by ~24% on average** when comparing DeepSeek R1 Distill Llama 70B against Llama 3.3 70B Instruct and s1.1 32B against Qwen 2.5 32B Instruct, even though the same fine-tuning improves correctness on the underlying math/science tasks; (3) using a carefully crafted system prompt that explicitly encourages abstention helps both standard and reasoning models, but the authors are clear this is gating, not a fix for the underlying lack of uncertainty-reasoning.

The Tülu 3 post-training analysis is the most mechanistically suggestive piece. SFT and DPO stages generally improve abstention recall, but the RLVR (PPO-with-verifiable-rewards) stage causes a "sharp drop" in underspecified-context abstention. That fingerprints the degradation onto the *verifier-rewarded* part of the recipe — the same recipe the reasoning models s1.1 and DeepSeek R1 inherit at much larger scale. The test-time-compute sweep (Figure 7) replicates the trade-off intra-model: scaling reasoning tokens from 512 to 4096 on UMWP and GSM8K-Abstain improves accuracy but hurts (or fails to improve) abstention. Best performers on average abstention recall are GPT-4o and Qwen 2.5 32B, but performance is "highly variable across datasets" — models near-fail on MediQ, near-saturate on BIG-Bench Known Unknowns.

## Key experimental conditions

- 20 datasets, ~35,000 unanswerable questions, six abstention scenarios (Answer Unknown, False Premise, Stale, Subjective, Underspecified Context, Underspecified Intent). Three datasets are new "Abstain" variants of GSM8K, GPQA, and MMLU-Math constructed by removing contextual information.
- 20 models: GPT-4o, o1, Gemini 1.5 Pro; Llama 3.1 (8B, 70B, 405B), Llama 3.3 70B; Qwen 2.5 32B; Mistral 7B; OLMo 7B; reasoning models DeepSeek R1 Distill Llama 70B and s1.1 32B.
- Two paired comparisons drive the reasoning-degradation headline: DeepSeek R1 Distill Llama 70B vs. Llama 3.3 70B Instruct; s1.1 32B vs. Qwen 2.5 32B Instruct.
- Tülu 3 stage-by-stage analysis (Llama 3.1 base → SFT → DPO → RLVR) isolates which post-training stage degrades abstention.
- Inference: 4k generation tokens, temperature 0.8, unified infrastructure.
- Judge: Llama 3.1 8B Instruct, 88% accuracy vs. human labels on GPT-4o + Llama 3.1 70B responses. Primary metric is abstention recall; precision and F1 reported alongside.

## Key quantitative results

- **Reasoning models lose ~24% mean abstention** vs. their non-reasoning counterparts (DeepSeek R1 Distill vs. Llama 3.3 70B Instruct; s1.1 32B vs. Qwen 2.5 32B Instruct), averaged across datasets.
- **Scaling Llama 8B → 70B → 405B has "almost no effect"** on mean abstention recall — abstention is not a capability that emerges with parameter count.
- **Tülu 3 RLVR causes a sharp drop in underspecified-context abstention** specifically; SFT and DPO improve abstention on most scenarios.
- **Test-time compute (512 → 4096 reasoning tokens) on UMWP and GSM8K-Abstain improves accuracy but hurts or fails to improve abstention** (Figure 7).
- System-prompt intervention (Appendix C) boosts abstention for both reasoning and standard models "without significant degradation in abstention precision" — but authors flag it as a patch, not a fix.
- Best on average: GPT-4o and Qwen 2.5 32B. Worst per-scenario: near-zero on MediQ; near-saturated on BIG-Bench Known Unknowns. Per-model F1 numbers live in tables we did not fully extract.

## Methods (what they did and didn't use)

- Behavioural evaluation only: prompt the model, score the response with an LLM judge against a fixed schema.
- Tülu 3 stage-by-stage decomposition (base → SFT → DPO → RLVR) is the closest the paper gets to a mechanistic claim — and it remains a *training-recipe* attribution, not an internal-state attribution.
- **No linear probes, no SAEs, no activation steering, no internal-state methods of any kind.** The entire benchmark and analysis is behavioural.
- Open-weight reasoning models (DeepSeek R1 Distill, s1.1) make the headline degradation result reproducible; closed-weight o1 / Gemini 1.5 Pro give breadth but not reproducibility.
- LLM-as-Judge is a known confound — judge validation on 88% sample agreement is reasonable but not adversarial.

## Authors' stated limitations / future work

- English-only coverage.
- Possible train-test leakage (CoCoNot training data appears in Tülu post-training).
- Fixed model selection (20 LLMs); no private test set means future overfitting risk.
- Reliance on imperfect LLM judges.
- Future work the authors call for: post-training datasets that explicitly cover uncertainty scenarios; folding uncertain problems into reasoning fine-tuning; non-English; mechanistic investigation of *why* reasoning models trained for correctness fail at uncertainty.

## Open questions and follow-up directions

1. **Locating the degradation internally.** The paper isolates RLVR as the stage that hurts abstention, but treats the model as a black box. Whether the "should I abstain?" signal is represented in activations and merely *suppressed* by RLVR, or whether RLVR removes it altogether, is the obvious next experiment — a linear probe on the Tülu 3 checkpoints, layer-swept across stages, would distinguish gating from removal.
2. **Is reasoning-induced overconfidence one direction or many?** Reasoning models lose abstention across all six scenarios, but the scenarios are very different (false premise vs. subjective vs. stale). Whether these share a single "I am confident" representation that RLVR amplifies, or whether each scenario fails for its own reason, is open.
3. **Generalisation of the system-prompt fix.** The prompt-based boost is the kind of intervention that often works on benchmark distributions but fails under distribution shift — particularly adversarial prompts that look answerable but aren't. The paper does not stress-test the prompt fix; doing so would clarify whether it's papering over the gap or genuinely shifting model behaviour.
4. **Reasoning-faithfulness intersection.** A reasoning model with degraded abstention may be confabulating in its chain of thought rather than reasoning honestly about uncertainty. The paper does not look at the CoT contents of DeepSeek R1 or s1.1 on abstention failures. Whether the CoT shows the model entertaining and dismissing uncertainty, or never noticing it, would tell us a lot about which mitigation strategies are viable.
5. **Does the result invert at much larger reasoning-model scale?** All open-weight reasoning models tested top out at ~70B. Whether GPT-5-class or Opus-class reasoning systems show the same abstention degradation, or have re-learned to abstain via scale, is not measurable from this benchmark.

## See also

- [[cot_faithfulness]] — reasoning models verbalising correctness signals unfaithfully; complements this paper's behavioural result with a mechanism for why CoT alone won't catch over-confident reasoning.
- [[illusion_of_thinking]] — Apple's "reasoning collapses at high complexity" result; same family of "reasoning fine-tuning has costs the headline benchmarks hide".
- [[lie_detector_limits]] — truth probes fail on misleading-but-true statements; analogous failure mode where the surface task (true/false, answerable/not) is well-defined but the representation the probe targets isn't the one we need.
- [[obfuscated_reward_hacking]] — RL pressure (against a monitor here, against verifiable rewards there) reshapes model behaviour in ways the original eval misses; sibling result that RLVR specifically degrades a safety-relevant capability.
