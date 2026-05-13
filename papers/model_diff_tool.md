# Cross-Architecture Model Diffing with Crosscoders: Unsupervised Discovery of Differences Between LLMs

**Authors:** Thomas Jiralerspong (Anthropic Fellow, Mila / Université de Montréal), Trenton Bricken (Anthropic)
**Year:** 2026 (February, arXiv preprint)
**arXiv:** [2602.11729](https://arxiv.org/abs/2602.11729)
**Status:** read

---

## Summary (in our words)

This paper takes crosscoders — a sparse-dictionary method previously used to diff a base model against its finetune — and applies them, for the first time, across genuinely different architectures. The goal is to surface "unknown unknowns": behaviours present in one model and absent in another that no eval suite was built to look for. The authors note that the method could, hypothetically, have flagged the GPT-4o sycophancy incident before deployment.

The technical contribution is the **Dedicated Feature Crosscoder (DFC)**, an architectural modification of the standard crosscoder. A standard crosscoder learns a single shared dictionary over the activations of two models and only labels features as "model-exclusive" *post-hoc* via the relative decoder norm. Because its loss rewards features that reconstruct both models simultaneously, it has a strong prior to learn shared features. The DFC partitions the dictionary into three disjoint sets by design — Model-A-exclusive, Model-B-exclusive, and shared — and structurally zeroes the decoder weights of exclusive features into the opposing model. Exclusivity becomes an architectural guarantee rather than a learned tendency, freeing capacity to find differences.

Applied to two real cross-architecture pairs (Llama-3.1-8B-Instruct vs. Qwen3-8B, and GPT-OSS-20B vs. DeepSeek-R1-0528-Qwen3-8B), the method recovers a politically charged set of model-exclusive features: a broad **CCP alignment** feature in both Chinese-origin models, finer-grained pro-China narrative features (Taiwan sovereignty, Hong Kong status, "debt trap" diplomacy), an **American exceptionalism** feature in Llama, a **ChatGPT identity** feature in GPT-OSS, and — most interesting because it was not hypothesised in advance — a **copyright-refusal mechanism** in GPT-OSS. Each feature is causally validated by activation steering across 30 curated prompts, with Claude 4.1 Opus rating outputs for ideological alignment and coherence.

What makes the paper sit in an interesting place is the honesty about workflow. The authors are explicit that *most* model-exclusive features the DFC surfaces do not capture meaningful behavioural differences. They frame the method as a high-recall pre-screen — a "screen-and-verify" pipeline where automated interpretability filters a candidate set and activation steering causally validates survivors. The exclusive features are mined from dictionaries of order 100k+ features, and the meaningful safety-relevant findings number in the single digits per diff. This is positioned as a feature, not a bug, but it makes the headline framing ("we could have caught GPT-4o sycophancy") considerably more contingent on the downstream filtering step than a casual reader might assume.

## Key experimental conditions

- Two cross-architecture model diffs: Llama-3.1-8B-Instruct vs. Qwen3-8B; GPT-OSS-20B vs. DeepSeek-R1-0528-Qwen3-8B
- Trained on 100M token-aligned activation pairs from each model pair's middle layers
- Training mix: FineWeb pretraining text + LMSYS-Chat-1M chat data
- BatchTopK sparsity (k=200), 131,072-feature dictionaries
- Cross-tokenizer alignment via a semantic window expansion method (Appendix B.1.6)
- Three DFC variants tested at 1%, 3%, and 5% exclusive partition sizes
- Five random seeds for the 5% Llama-Qwen DFC (robustness study)
- Toy-model validation: 800M synthetic activation pairs over 2048 ground-truth concepts with 2.5% per-model exclusive concepts, compared against standard crosscoders and Designated Shared Feature (DSF) crosscoders
- Feature interpretation: automated explanation pipeline + Claude 4.1 Opus as LLM judge (25 ratings manually validated against human judgement)

## Key quantitative results

- **Broad CCP alignment feature in Qwen3-8B**: recovered in 5/5 seeds and across all three partition sizes (1%, 3%, 5%); replicated as a separate CCP feature in DeepSeek-R1-0528-Qwen3-8B
- **American exceptionalism feature in Llama**: recovered in 4/5 seeds at the 5% partition size
- **Granular pro-China features** (Taiwan, Hong Kong, debt-trap diplomacy): recovered in 2-3/5 seeds at 5%, missed entirely at 1% and 3%. Partition size matters for granularity, not just scale
- **Exclusivity score** (transferred behaviour via learned linear stitching map, judged 1-5 by Claude 4.1 Opus, with 5 = no transfer possible): all ideological features reached the maximum score of 5
- **Distribution of exclusivity scores**: DFC features cluster sharply at score 5; standard-crosscoder "exclusive" features (top-500 by relative decoder norm) are bimodal with substantial mass at score 1
- **Shared-feature distributions** are nearly identical between DFC and standard crosscoder — the gain is specifically on exclusivity, not overall feature quality
- **Standard performance metrics** (DFC vs. standard crosscoder, Llama-Qwen): dead features 5.0% vs. 5.6%; detection score 87.78% vs. 87.77%; fraction of variance explained 0.817 vs. 0.817. The DFC's gain is "free" on these metrics
- **Persona-vector transfer test**: Llama persona vectors (sycophantic, evil, hallucinating) with low maximum cosine similarity to any existing DFC feature (0.38, 0.35, 0.26 respectively) successfully transfer to Qwen via the shared partition and reproduce semantically equivalent steered behaviour — independent evidence that the shared space is genuinely aligned
- **Causal effect of CCP and American-exceptionalism steering**: each feature shifts ideological-alignment ratings substantially within its home model while leaving the opposing model near its 20% baseline; coherence is preserved across the meaningful steering range
- **Toy-model recall**: DFCs outperform standard crosscoders and DSF crosscoders at recovering ground-truth exclusive concepts, especially in the undercomplete regime, at the cost of higher false-positive rate

## Methods (what they did and didn't use)

- Crosscoders (Lindsey et al. 2024) as the base method; novel DFC modification adds architectural feature-partitioning
- BatchTopK (Bussmann et al. 2024) for sparsity
- Activation steering for causal validation
- Model stitching (Chen et al. 2025a) — a learned linear map between activation spaces — as the baseline against which exclusivity is judged
- Automated interpretability pipeline + LLM-as-judge (Claude 4.1 Opus); 25 ratings manually spot-checked
- Persona vectors (Chen et al. 2025b) used as independently-derived directions to test shared-space alignment
- Toy model with isotropically-sampled ground-truth concepts and an affine transformation to simulate cross-architecture rotational mismatch
- Baselines compared against: standard crosscoder, Designated Shared Feature (DSF) crosscoder (Mishra-Sharma et al. 2025), and prior model-distance metrics (treated as related but not directly comparable, since those produce scalar distances rather than interpretable features)
- All models are open-weight; no frontier-scale model tested
- Limited validation on base-vs-finetune diffs (a known failure mode they cite — the "mirror features" phenomenon)

## Authors' stated limitations / future work

- Validating exclusivity on real models without ground-truth concepts is inherently hard. The transfer-based exclusivity score is a proxy
- The recall/precision trade-off favours recall; many false positives need filtering. Authors argue this is correct for safety auditing but acknowledge the workflow cost
- Feature discovery is sensitive to partition size and training initialisation: broad features (CCP alignment) are stable across seeds and partition sizes, but finer-grained features show seed and partition-size variance. Future work on variance-reduction techniques is called out
- Generalisability to a wider range of model pairs is unverified
- Method struggles in base-vs-finetune diffs due to "mirror features" — a known crosscoder failure mode that is not resolved here
- The method identifies feature presence/absence but says nothing about *provenance* (was the CCP alignment feature deliberately trained, or a data artefact?). The authors flag this explicitly as future work
- Important conceptual caveat the authors emphasise: "model-exclusive" refers to a model's specific **representation**, not its conceptual capability. Llama clearly knows what CCP alignment is — what Qwen has is a specific, distinct linear direction for it without a direct analogue in Llama's activation space
- Disabling the GPT-OSS copyright-refusal feature does not produce faithful reproduction of copyrighted content. Coherence collapses and the model hallucinates. The feature controls the refusal mechanism, not the underlying knowledge

## Open questions and follow-up directions

1. **Variance reduction across seeds is the immediate methodological gap.** The headline numbers are 4/5 and 2-3/5 for the more interesting features; only the broadest CCP feature is fully stable. Until variance is brought down, the method's value depends on how many runs an auditor can afford. Techniques like seed ensembling, feature alignment across runs, or training-curriculum changes are natural next steps and are essentially absent from this work.

2. **Provenance is the obvious next problem.** The DFC finds *that* a feature is exclusive but not *why*. Combining model diffing with data-attribution methods (influence functions, training-data search) or with diffs over training checkpoints would let the field distinguish features introduced by RLHF, by pretraining data, or as inductive consequences of architecture. The authors flag this; no one has done it yet.

3. **The base-vs-finetune failure mode ("mirror features") undercuts the most policy-relevant use case.** The strongest framing — diffing a single model across training to catch behavioural drift before deployment — is precisely the setting where the authors say the method struggles. Until "mirror features" are diagnosed, the deployment-monitoring story remains aspirational and the only working applications are cross-architecture, which is a comparatively rare auditing situation.

4. **Scaling to frontier models is unverified and not obviously cheap.** 100M token-aligned activation pairs on middle layers of 8B-20B models is already a substantial training run; the dictionary is 131k features. Whether DFCs remain trainable and informative on frontier-scale models, and how feature counts grow, is genuinely unknown. The political-alignment features the paper foregrounds may also be unusually clean targets compared with the subtler differences a frontier-monitoring deployment would need to detect.

5. **The "screen-and-verify" workflow is the actual artifact.** The paper's framing implies the method's value is the features it surfaces, but in practice the value is the *pipeline* — automated interpretation, exclusivity scoring, steering validation. Disaggregating which stage contributes most signal (would simpler exclusivity scoring on a standard crosscoder, plus the same steering pipeline, get most of the way?) would clarify how much of the gain is architectural and how much is workflow.

## See also

- [[persona_vectors]] — the paper directly uses Chen et al.'s persona-vector discovery as an independent probe to validate that DFC's shared partition is genuinely aligned. Sibling method, smaller scale
- [[sleeper_agent_probes]] — the same internal-feature-as-detector intuition: features can flag behaviour that purely behavioural evals miss
- [[steering_eval_aware]] — activation steering as causal validation of a candidate linear direction
- [[beyond_linear_probes]] — methodological cousin when single linear directions are insufficient
- [[eliciting_secret_knowledge]] — adjacent problem of surfacing behaviour or knowledge that is not externally visible
- [[natural_language_autoencoders]] — alternative way to read off internal representations into human-legible form; complementary to feature-level diffing
- [[political_stance]] — behavioural counterpart to the CCP / American-exceptionalism findings here; the DFC offers an internal-feature explanation of the behavioural patterns that paper documents
