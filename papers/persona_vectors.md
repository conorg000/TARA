# Persona vectors: Monitoring and controlling character traits in language models

**Authors:** Anthropic Fellows program participants
**Year:** 2025 (August)
**Source:** [anthropic.com/research/persona-vectors](https://www.anthropic.com/research/persona-vectors)
**Status:** read

---

## Summary (in our words)

This is a methodological sibling to [[sleeper_agent_probes]] and [[emotion_concepts]] — the same family of "linear direction in residual stream, derived from contrastive content, used to both detect and steer behavior." The contribution here is doing it for *character traits* (evil, sycophancy, hallucination) on smaller open-weight models (Qwen 2.5-7B and Llama 3.1-8B).

The pipeline: build contrastive prompt pairs that elicit a trait vs. don't, extract activations on both, take the difference, get a vector. That vector "lights up predictively before models express the corresponding trait" — i.e. it provides a pre-action signal. The authors use these vectors three ways: (1) inference-time steering to suppress traits; (2) preventative steering during fine-tuning to keep traits from being learned; (3) flagging training samples that would push the model along a trait direction.

Headlines: (a) the technique works on open-weight 7-8B models, (b) the vectors *predict* trait expression before it happens, and (c) the authors release an automated pipeline for deriving them.

A caveat the authors don't dwell on: inference-time steering against a trait tends to reduce general capability. Detection uses of the vector don't suffer the same trade-off — monitoring is cheaper than intervention.

## Key experimental conditions

- Models: Qwen 2.5-7B-Instruct, Llama-3.1-8B-Instruct
- Primary personas: evil, sycophancy, hallucination
- Supplementary personas: politeness, apathy, humor, optimism
- Vector extraction: automated contrastive activation pipeline
- Applications tested: real-time activation monitoring, inference-time steering, training-time preventative steering, training-data flagging via projection

## Key quantitative results

- Vectors "light up" predictively before trait expression
- Preventative steering during training: prevents personality shifts, MMLU degradation minimal
- Inference-time steering: reduces trait expression but degrades general capabilities
- Training-data flagging on LMSYS-Chat-1M correctly identified samples that induce target traits

## Methods (what they did and didn't use)

- Linear probes on residual stream activations
- Contrastive prompt pairs as the source signal
- Activation steering (additive)
- Automated extraction pipeline
- Not SAEs, not dictionary learning

## Authors' stated limitations / future work

- Inference-time steering has capability side effects
- Preventative steering needs training-pipeline integration
- Real-world deployment validation not done in this work
- No discussion of whether models could learn to mask persona vectors (i.e. game the probe itself)

## Open questions and follow-up directions

1. **Generality across trait types.** The paper covers a handful of character traits (evil, sycophancy, hallucination, plus a few lighter ones). Whether the contrastive-pair pipeline extends cleanly to more behaviorally complex or context-dependent traits — deception, situational reasoning, capability-modulation behaviors — is open. Some traits may not factor into a single linear direction.

2. **Predictive lead time and calibration.** The vectors "light up before" trait expression, but the paper does not quantify how far in advance, at what false-positive rate, or how this varies across traits and contexts. A more careful AUROC / lead-time characterization is a natural replication target.

3. **Probe robustness to adversarial suppression.** The authors flag but do not investigate whether a model could learn to keep its activations off the persona direction while still expressing the trait behaviorally. This matters whenever the probe is used as part of a training or oversight loop the model is exposed to.

4. **Capability cost of steering.** Inference-time steering reduces trait expression but degrades general capability; preventative training-time steering reportedly has minimal MMLU cost. The mechanism behind that asymmetry — and how it scales with vector magnitude, trait, and model — is not characterized.

5. **Transfer across model families and scales.** Results are on two 7-8B instruct models. Whether the same contrastive pipeline produces equivalently informative directions in larger models, base (non-instruct) models, or different architectures is unaddressed.

## See also

- [[sleeper_agent_probes]] — closely related linear-probe methodology applied to a different target behavior
- [[emotion_concepts]] — sibling application of contrastive-direction extraction to affect-like states
- [[beyond_linear_probes]] — addresses cases where a single linear direction is insufficient, relevant to the trait-generality question
- [[steering_eval_aware]] — evidence that behaviorally relevant directions have linear structure in activation space
- [[deception_probes]] — applies the same probe family to deception specifically
