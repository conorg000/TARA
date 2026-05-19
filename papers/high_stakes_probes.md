# Detecting High-Stakes Interactions with Activation Probes

**Authors:** McKenzie, Pawar, Blandfort, Bankes, Krueger, Lubana, Krasheninnikov (LASR Labs / UCL / MILA / Harvard / NTT Research / Goodfire / Cambridge)
**Year:** 2025 (NeurIPS)
**arXiv:** [2506.10805](https://arxiv.org/abs/2506.10805)
**Fetched from:** `arxiv.org/html/2506.10805v4`
**Status:** read

---

## Summary (in our words)

A probe-methodology paper applied to a fuzzy safety-monitoring target: detect "high-stakes" interactions — text exchanges where a wrong response could plausibly cause significant harm. The authors train a battery of activation probes on Llama-3.3-70B (residual stream at layer 31 of 80) using purely synthetic high/low-stakes contrast pairs, then evaluate on six datasets — most of them natural (Anthropic HH-RLHF, MT Samples, MTS Dialog, Mental Health, Aya Redteaming) — and benchmark against prompted and finetuned LLM monitors from the Llama-3 and Gemma-3 families (1B through 70B).

Two findings carry the paper. First, probes trained only on synthetic data generalise well to natural OOD test sets: the best probe (an attention-pooled probe) reaches mean AUROC > 0.91 across test datasets. Second, the cost gap is dramatic — probes reuse the monitored model's activations and so cost effectively zero on top of the existing forward pass, giving roughly six orders of magnitude in compute savings versus running a separate medium-sized LLM as a monitor. The headline framing is "comparable performance at ~10⁶× less compute," which is true against medium-sized (8B–12B) finetuned baselines but **not** against the strongest baselines: probes underperform prompted Gemma-3-27B and prompted Llama-3.3-70B. At the low-FPR regime that matters operationally — TPR at 1% FPR — the best probe hits ~43% versus ~55% for prompted Llama-3.3-70B, so there is a real accuracy gap, not just a tie.

The paper's secondary contribution is a cascade story: probes as a cheap first-stage filter that routes uncertain cases to an expensive LLM monitor downstream. Combining probes with an LLM baseline beats either alone, and matches finetuned-8B performance at 2–3× lower cost. The authors also show that just 32–256 deployment-distribution samples are enough to lift probes above the strongest LLM baseline, which is the more interesting practical claim about probe adaptation cost.

The paper does not target eval-awareness, scheming, or deception. "High-stakes" here is content-level (medical, harm, manipulation) rather than behavioural-state. The methodology — synthetic contrast pairs, multiple probe architectures, OOD natural-data evaluation, cascade integration — is the more portable contribution.

## Key experimental conditions

- **Probed model:** Llama-3.3-70B, residual stream at layer 31/80 (selected via CV).
- **Probe architectures (6):** Mean aggregation, Max aggregation, Last-token, Softmax probe, Attention probe, Max-of-rolling-means. All sigmoid output, AdamW.
- **Baseline monitors:** prompted and finetuned Llama-3 (1B/8B/70B) and Gemma-3 (1B/12B/27B). Finetuned variants drop the unembedding layer and use a classification head. Prompted variants compare log-likelihoods of high- vs low-stakes continuations.
- **Training data:** synthetic. GPT-4o generates diverse situations → varied query samples (tone, length, language) → filtered by stakes confidence (kept 1–3 and 8–10, dropped 4–7) and a bag-of-words filter to remove lexical confounders.
- **Labelling oracle:** GPT-4o. Human inter-annotator validation reported as high.
- **Evaluation datasets (6):** Anthropic HH-RLHF (harm), ToolACE (synthetic, mixed), MT Samples (medical), MTS Dialog (medical), Mental Health (harm/political), Aya Redteaming (multilingual). Five of six are natural.

## Key quantitative results

- **Best probe:** Attention probe, mean test AUROC > 0.91, dev AUROC > 0.95.
- **Compute savings:** ~10⁶× cheaper than LLM monitors (probes reuse the existing forward-pass activations; LLM monitors are a separate forward pass).
- **Performance positioning:** probes outperform 1B finetuned models, Gemma-3-12B finetuned, Gemma-3-12B prompted, Llama-3.1-8B prompted; comparable to 8B–12B finetuned; **underperform** Gemma-3-27B prompted and Llama-3.3-70B prompted.
- **TPR @ 1% FPR (operational regime):** ~43% (best probe) vs ~55% (prompted Llama-3.3-70B). Gap narrows substantially at 20–40% FPR.
- **Few-shot adaptation:** 32 deployment-distribution samples already improves probes; with the full dev split, probes exceed prompted Llama-3.3-70B.
- **Cascade:** probe + LLM monitor beats either alone, matches finetuned-8B at 2–3× lower cost.
- **Probe ranking:** Attention > Softmax ≈ Mean > Max / Max-of-rolling-means (latter strong on domain-specific medical) > Last-token (consistently worst).

## Methods (what they did and didn't use)

- Linear and shallow activation probes trained on residual-stream activations at a single chosen layer.
- Comparison against both prompted and finetuned LLM monitors at multiple scales.
- Synthetic-only training; natural OOD evaluation.
- Cascade / hierarchical monitoring evaluation (probe-first, LLM-second).
- Sample-efficiency curves for adapting probes to a new deployment distribution.
- **No SAEs, no activation steering, no NLAs, no CoT monitoring.** No internal-state methods beyond probing.
- White-box requirement: the approach assumes access to residual-stream activations of the monitored model, which limits applicability to deployments where the monitor has that access.

## Authors' stated limitations / future work

- Hyperparameter search not exhaustive; relative probe ranking could shift.
- "High-stakes" is fuzzy, subjective and context-dependent; probes may be replicating GPT-4o's specific interpretation rather than a stable ground truth.
- Synthetic-data confounders: low-stakes phrasing inside genuinely high-stakes content (e.g. "minor wound") degrades probe fidelity.
- LLM baselines were not finetuned on the evaluation dev sets, so the head-to-head comparison is not fully matched.
- Linear probes are vulnerable to white-box targeted attacks.
- Risk of blind spots: the framework requires knowing which concepts to probe in advance.
- Authors flag specific qualitative failures: humour and signal words trigger false positives ("emergency"); ethical-coded language in unethical contexts misleads probes ("responsible money laundering"); embedding high-stakes content inside low-stakes framing reduces probe scores.
- Future directions: extending to "high-stakes for the AI itself" (scheming, alignment faking), integrating probes with input/output classifiers and CoT monitoring, building a more systematic framework for choosing which concepts to monitor.

## Open questions and follow-up directions

1. **Whether "comparable" survives a matched comparison.** The headline reads as a tie at ~10⁶× less compute, but probes lose to the strongest prompted baselines and trail by ~12 points at TPR@1%FPR. A like-for-like comparison where the LLM monitors are also finetuned on the same dev split would clarify whether the cost-performance frontier really favours probes at the operating points safety teams care about.

2. **Conditions for synthetic-to-natural transfer.** The pipeline — GPT-4o generates contrast pairs, train a probe, evaluate on natural OOD — works for "high-stakes" but the paper does not establish what properties of the target concept determine transfer. Harm-relevance may be unusually well-aligned with natural distributions. Replication on more abstract, context-dependent, or behavioural concepts (deception, sycophancy, eval-awareness) would map the limits.

3. **Operating-point characterisation of failure modes.** The qualitative failures the authors list — humour, ethical-coded language in unethical contexts, low-stakes framing of high-stakes content — are exactly the failure modes an adversary would exploit. Systematic stress tests at deployment-relevant FPR thresholds would clarify when the cheap monitor is safe to substitute.

4. **Why Attention > Last-token by such a margin.** The probe architecture comparison is one of the most concrete findings (Attention probe consistently wins; Last-token consistently loses) but the paper doesn't pin down why. Whether the gap reflects token-position information leakage in training data, genuine distributed representation of stakes, or something else is open.

5. **Stability under model updates.** Probes are tied to one model's residual stream at one layer. How accuracy degrades after fine-tuning, RLHF iterations, distillation, or routine post-training is not measured, and matters for treating probes as a deployed monitoring layer rather than a research artefact.

6. **Adversarial robustness.** The authors flag white-box vulnerability without measuring it. Whether the cascade architecture (probe → LLM) inherits or mitigates the probe's adversarial weakness is the natural next question.

## See also

- [[sleeper_agent_probes]] — sibling probe-monitoring paper targeting backdoor triggers; methodologically adjacent (probes as safety filter on natural text)
- [[persona_vectors]] — another synthetic-to-natural transfer result, on persona/trait directions rather than content-level harm
- [[deception_probes]] — same probe methodology, applied to deception detection; different concept, same question of whether synthetic training transfers
- [[deception_probe_bench]] — benchmarks probe-style detection on adversarial / OOD inputs; relevant to this paper's untested robustness claims
- [[better_deception_probes]] — pushes on probe architecture and training-data design choices that this paper leaves implicit
- [[beyond_linear_probes]] — limits-of-linear-probing critique; relevant given Attention-probe's gap over linear baselines here
- [[probing_steering_eval_aware]] — applies probe methodology to a context-level behavioural concept (eval-awareness) rather than content-level harm
