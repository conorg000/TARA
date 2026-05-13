# Persona vectors: Monitoring and controlling character traits in language models

**Authors:** Anthropic Fellows program participants
**Year:** 2025 (August)
**Source:** [anthropic.com/research/persona-vectors](https://www.anthropic.com/research/persona-vectors)
**Status:** read

---

## Summary (in our words)

This is the methodological sibling to [[sleeper_agent_probes]] and [[emotion_concepts]] — the same family of "linear direction in residual stream, derived from contrastive content, used to both detect and steer behavior." The contribution here is doing it for *character traits* (evil, sycophancy, hallucination) on smaller open-weight models (Qwen 2.5-7B and Llama 3.1-8B) — i.e. on models we could actually run within our budget.

The pipeline: build contrastive prompt pairs that elicit a trait vs. don't, extract activations on both, take the difference, get a vector. That vector "lights up predictively before models express the corresponding trait" — exactly the pre-action signal we care about. They use these vectors three ways: (1) inference-time steering to suppress traits; (2) preventative steering during fine-tuning to keep traits from being learned; (3) flagging training samples that would push the model along a trait direction.

For our project the relevant headlines are: (a) the technique works on the model class we'd be using (open-weight 7-8B), (b) the vectors *predict* trait expression before it happens, and (c) the authors release an automated pipeline for deriving them. We don't have to invent the recipe — we can adopt it.

A caveat the authors don't dwell on but which matters for us: the inference-time steering trade-off. Steering against a trait reduces capability. That's relevant because our project isn't about *steering* sandbagging away, it's about *detecting* it. The detection use of these vectors doesn't suffer the capability degradation, which is helpful.

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
- No discussion of whether models could learn to mask persona vectors (i.e. eval-game the probe itself)

## Our own follow-up thoughts (project-relevant)

1. **Use this pipeline as the starting point for our sandbagging probe.** Persona vectors handles the engineering side: automated derivation of a trait direction from contrastive pairs, with public methodology. For our project, "sandbagging" becomes a candidate "persona" — generate contrastive pairs (model answering at full capability vs. model answering as if locked), extract the direction, measure detection AUROC on held-out evals. This is the most concrete starting point for the code we'd write.

2. **The "vector lights up before trait expression" finding is the project's headline result we'd want to reproduce.** Pre-action prediction is exactly what makes probes useful for safety. If we can replicate this for sandbagging — "the vector predicts that the model is about to underperform, before the underperformance happens" — that's the result we'd put in a presentation.

3. **Open question they raise implicitly: can the persona vector be deliberately suppressed?** If a model learns it's being monitored via persona vectors, can it steer its own activations to stay off the vector while still expressing the trait? This is the eval-gaming-of-the-eval-gaming-detector worry. Not tractable as a project on its own, but worth flagging as a future-work direction.

## Relevance to our project

Very high — methodologically essential. Of all the papers in this batch, persona_vectors gives us the most direct technical recipe for what we'd actually build. The combination of "persona vectors pipeline + sleeper_agent_probes detection methodology + sandbagging as the target phenomenon" is the project, in three sentences.

Pairs with: [[sleeper_agent_probes]] (closely related method), [[emotion_concepts]] (sibling application), [[sandbagging]] (target).
