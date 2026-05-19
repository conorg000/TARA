# Steering Llama 2 via Contrastive Activation Addition

**Authors:** Panickssery, Gabrieli, Schulz, Tong, Hubinger, Turner
**Year:** 2023 (v1 Dec 2023; revised Jul 2024)
**arXiv:** [2312.06681](https://arxiv.org/abs/2312.06681)
**Status:** read

---

## Summary (in our words)

This is the canonical "compute a steering vector from contrast pairs" paper that essentially every later steering / persona-vector / eval-aware-suppression result inherits. The construction is dead simple: take a multiple-choice question with two answer options that differ along the behavioural axis of interest (e.g. a sycophantic A vs. a non-sycophantic B), run the model on each prompt, pull residual-stream activations *at the position of the answer letter token* at layer L, and average the (positive − negative) difference across hundreds of pairs. That difference-of-means vector is then added to the residual stream at every post-prompt token position during generation with a scalar coefficient.

The empirical claims are: (i) layer choice matters and a single middle layer dominates — layer 13 of Llama 2 7B Chat and layers 14-15 of Llama 2 13B Chat — and the optimal layer is largely shared across behaviours; (ii) the technique moves multiple-choice answer probabilities by 0.2-0.4 absolute on held-out questions, on six of seven traits tested; (iii) general capability as measured by MMLU is essentially undisturbed at ±1 multiplier; (iv) vectors extracted from base Llama 2 transfer to RLHF'd Chat versions at the same middle layers, suggesting RLHF doesn't reorganise representations there much.

What makes the paper load-bearing for the field isn't any single number — it's that it operationalised a method clean enough to copy. Difference-of-means at the answer-letter token over A/B contrast pairs has become the default recipe (persona vectors, eval-aware suppression, deception probes, emotion concepts all use variants of it). The seven traits Panickssery et al. picked (AI coordination, corrigibility, hallucination, myopic reward, survival instinct, sycophancy, refusal) also seeded the trait list that later persona-style papers extend.

The weakest spot is the open-ended generation evaluation, which leans on GPT-4 ratings on 1-10 scales — the paper itself flags that scoring prompt wording introduces noise. Sycophancy is also the one trait where multiple-choice steering basically didn't work (Δ = -0.04 at +1 multiplier), which is awkward given how much later work treats sycophancy as the prototypical steerable trait. The result is empirically tight for traits like corrigibility (+0.38) and hallucination (+0.36); the framing claim that CAA "works across behaviours" is supported but not uniform.

## Key experimental conditions

- Models: Llama 2 7B Chat and Llama 2 13B Chat (RLHF'd). Some experiments on the base Llama 2 7B to test base→Chat vector transfer.
- Contrast pairs: A/B multiple-choice format; ~hundreds of pairs per trait drawn from Anthropic's `evals` model-written-evals dataset.
- Activation extraction at the *answer letter* token position (after the prompt and before the answer text generates).
- Steering applied at every post-prompt token position with scalar multiplier (typically ±1, occasionally ±2 for open-ended).
- Seven traits: AI coordination, corrigibility, hallucination, myopic reward, survival instinct, sycophancy, refusal.
- Layer sweep across all transformer blocks; reported single best layer per model.
- Evaluations: held-out multiple-choice questions, open-ended generation with GPT-4 scoring on 1-10, plus TruthfulQA and MMLU as capability/OOD probes.

## Key quantitative results

- Optimal steering layer: 13 (Llama 2 7B Chat), 14-15 (Llama 2 13B Chat). Effect peaks at similar layers across all behaviours.
- Multiple-choice probability shift at ±1 multiplier (Llama 2 13B Chat, layer 13, held-out 50 questions):
  - Corrigibility: 0.45 / 0.57 / 0.83 → +0.38 swing across [-1, +1]
  - Hallucination: 0.42 / 0.54 / 0.78 → +0.36
  - Survival instinct: 0.28 / 0.35 / 0.63 → +0.35
  - Refusal: 0.56 / 0.78 / 0.86 → +0.30
  - Myopic reward: +0.22
  - AI coordination: +0.19
  - Sycophancy: -0.04 (essentially flat; the one trait that doesn't move on MCQ)
- MMLU under ±1 steering: ~0.63 baseline, range 0.57-0.65 — no systematic capability hit.
- TruthfulQA: subtracting the sycophancy vector improves Llama 2 13B by +0.02 (small but consistent direction).
- Compute: vector construction <5 min on 1 GPU; comparable fine-tuning baseline ~10 min on 2 GPUs.
- Base→Chat transfer: vectors extracted from Llama 2 base transfer to Chat at layers 10-15, supporting the claim that RLHF leaves mid-layer representations relatively undisturbed.
- CAA on top of fine-tuning provides additional steering for 3/7 behaviours. Sycophancy fine-tune fails to generalise to open-ended generation; CAA does generalise in all 7 cases.

## Methods (what they did and didn't use)

- Activation engineering only — difference-of-means contrast vectors, no probes, no SAEs, no causal scrubbing.
- Behavioural evaluation in two modes: token probability on multiple-choice (clean signal, narrow distribution) and GPT-4-rated open-ended generation (noisier, broader distribution).
- Capability evaluations via MMLU (57 subjects, 570 questions) and TruthfulQA.
- Compared against: system-prompt steering, supervised fine-tuning on the same contrast data. Did not compare against ITI (Inference-Time Intervention) or representation engineering despite their concurrent existence.
- Open-weight models throughout — Llama 2 7B/13B Chat — so the recipe is fully reproducible.
- No internal-state analysis beyond the steering vectors themselves; the paper does not investigate what other features the vectors might be entangled with, or whether the same direction is what a linear probe would pick out.

## Authors' stated limitations / future work

- GPT-4 scoring of open-ended outputs is sensitive to prompt wording.
- Fine-tuning baseline hyperparameters not fully optimised; the comparison is suggestive, not definitive.
- Prompt-engineering baselines could be made stronger; CAA's advantage is partly that it avoids manual prompt optimisation.
- Vector norms differ across behaviours and layers; per-layer multiplier optimisation not performed.
- Future work: steering at *targeted* token positions rather than every position to improve the magnitude/quality trade-off.
- Future work: intervening at non-residual-stream locations (post-MLP, attention output).
- Future work: applying CAA to red-teaming and adversarial robustness.

## Open questions and follow-up directions

1. The sycophancy null on multiple-choice (Δ = -0.04) sits uneasily with the open-ended sycophancy demonstrations and with later work that treats sycophancy as the canonical steerable trait. Whether the sycophancy direction is genuinely harder to isolate via A/B contrast pairs, or whether the MCQ dataset for sycophancy is just poorly constructed, is not resolved here and matters for any downstream sycophancy-detection work.
2. The paper extracts at the *answer-letter token* — a specific position chosen because the contrast pairs are MCQ-format. Whether the same direction emerges if extraction is done at the last prompt token, at chain-of-thought continuation tokens, or averaged across the response, would tell us how brittle the recipe is to format.
3. The optimal-layer claim ("around layer 13 for both models, across behaviours") is consistent with later mid-layer findings but is asserted, not explained. Whether the convergence reflects a common abstract-concept stratum at mid-depth, or just where Chat-tuning leaves the most exploitable structure, would distinguish two different stories about what CAA is measuring.
4. The base→Chat transfer result (vectors trained on base Llama 2 work on Chat) implies the trait directions exist pre-RLHF. Whether this generalises to traits that are plausibly *induced* by RLHF (refusal, certain forms of sycophancy) versus traits that are pre-existing (factuality, myopia) is not separated.
5. CAA is evaluated only on Llama 2. Whether the same recipe — same layers, same contrast format, same multiplier ranges — works on later open-weight families (Llama 3, Qwen, Gemma) is a basic replication target. Later persona-vector work suggests it largely does, but the original paper doesn't establish it.

## See also

- [[persona_vectors]] — direct descendant; difference-of-means contrast vectors applied to evil / sycophancy / hallucination on Qwen2.5-7B and Llama-3.1-8B with an automated pipeline. Inherits CAA's construction; extends to monitoring, preventative training, and data-screening applications.
- [[steering_eval_aware]] — same construction (contrast pairs → mean-difference steering vector) applied to eval-aware vs. deployment contexts; demonstrates CAA-style vectors can *suppress* a trained-in behaviour, not just elicit it.
- [[assistant_axis]] — sibling difference-of-means construction (Assistant minus role mean) at the *persona* level rather than the trait level; finds the axis is shared across Gemma 2 / Qwen 3 / Llama 3.3.
- [[emotion_concepts]] — CAA-family linear directions for 171 emotion concepts on Claude Sonnet 4.5; same activation-addition recipe, scaled to a much larger concept inventory and a frontier closed-weight model.
- [[deception_probes]] — uses contrast-pair training but trains *probes* on the activations rather than steering vectors; the natural read-out counterpart to CAA's write-in.
