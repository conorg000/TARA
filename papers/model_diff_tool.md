# A "diff" tool for AI: Finding behavioral differences in new models

**Authors:** Thomas Jiralerspong (Anthropic Fellows), Trenton Bricken (Anthropic Alignment Science)
**Year:** 2026 (March)
**Source:** [anthropic.com/research/diff-tool](https://www.anthropic.com/research/diff-tool)
**Status:** read

---

## Summary (in our words)

A cross-architecture model-diffing technique called the Dedicated Feature Crosscoder (DFC). It decomposes two models into shared features plus model-exclusive features and surfaces behaviors that exist in one but not the other. The goal is to catch "unknown unknowns" — emergent behaviors that standard safety evaluations would miss because nobody knew to look for them.

The illustrative finding: when run on pairs of Chinese and American open-weight models (Llama-3.1-8B vs. Qwen3-8B, etc.), the method rediscovers a "CCP alignment" feature in 5 of 5 test runs across Chinese models, and an "American Exceptionalism" feature in 4 of 5 runs. Both are politically-tuned behaviors not explicit in either model's documentation. The authors validate the features causally by suppressing them during generation and confirming the behavioral changes.

For our project this is more interesting as evaluation-paradigm context than as direct methodology. The DFC requires training a feature decomposer over two models, which is far beyond solo budget. But the framing — *standard evals are reactive, internal-feature methods can be proactive* — is the same argument that motivates everything in our threat model. The "diff" framing is a useful metaphor we could borrow for the writeup: a probe is a one-feature diff between "evaluating" and "deploying" contexts.

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

## Our own follow-up thoughts (project-relevant)

1. **Mostly out of scope but useful framing.** Beyond our compute budget to build, but the "diff between models = find what changed" framing maps cleanly onto our project's "diff between conditions = find what the model is doing differently when it suspects evaluation." Borrowable framing.

2. **One concrete extension worth flagging.** If we had access to two versions of the same base model — one fine-tuned to sandbag, one not — running a DFC-style analysis between them would surface the sandbagging-relevant features explicitly. That's a much bigger project than ours but is the natural follow-on if our cheap-probe version yields interesting results.

## Relevance to our project

Low-medium. Methodologically out of scope for solo work, but provides framing for the writeup and demonstrates that the "internal features distinguish behaviorally similar models" intuition holds empirically.

Pairs with: [[persona_vectors]] (smaller-scale version of the same intuition).
