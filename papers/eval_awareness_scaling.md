# Evaluation Awareness Scales Predictably in Open-Weights Large Language Models

**Authors:** Chaudhary, Su, Hooda, Shankar, Tan, Zhu, Lagasse, Sharma, Panda
**Year:** 2025 (NeurIPS Workshop on Responsible Foundation Models, v2 Nov 2025)
**arXiv:** [2509.13333](https://arxiv.org/abs/2509.13333)
**Status:** read

---

## Summary (in our words)

This is the scaling-laws-for-eval-awareness paper. Prior work (Goldowsky-Dill et al. on Llama-3.3-70B; Hua et al. on Llama-3.3-70B-Instruct) showed that eval-vs-deployment had linear structure in residual-stream activations of one large open-weight model. The natural follow-up: does that linear structure appear in smaller models, and how does it scale? The authors fit a probe on residual-stream activations across 15 models spanning 0.27B to 70B parameters in four families (Gemma-3-it at 0.27B/1B/4B/12B/27B, Phi-3-mini-3.6B and Phi-3-medium-14B, GPT-OSS-20B, Llama-3.1-Instruct-8B and Llama-3.1-Instruct-70B), and report that probe AUROC's distance from 0.5 grows monotonically with size, roughly following a power law in parameter count.

The setup is standard difference-of-means probing. They build two contrast corpora — a 203-item hand-written "simple contrastive" set and the 400-item Stages Oversight subset of SAD (Laine et al., the situational-awareness benchmark we have in the index) — take per-layer residual activations on each, compute the normalized mean-difference vector as the probe, and score AUROC with thresholds set by Youden's J. Best-performing probes consistently sit in early-to-middle layers across families, with the lone outlier being Gemma-3-27B peaking at layer 3.

Two things to note about what's actually being measured. First, the headline metric is |AUROC − 0.5| on a binary eval-vs-deployment text classification task — this captures whether the model represents *which kind of document it is reading*, not whether it represents *being evaluated as itself*. That's a meaningful distinction the paper does not foreground. Second, while the title promises predictable scaling, the paper does not publish an exponent or a fitted equation. The claim is qualitative ("power-law-ish, monotone, family-robust") rather than the Hoffmann/Chinchilla-style quantitative fit the framing might suggest.

The Qwen family (0.5B–32B) was excluded from the headline scaling curve for "anomalous patterns attributed to dataset contamination." That's a load-bearing exclusion — Qwen is the one family where SAD-style stages-oversight prompts are most likely to have leaked into pre-training — and the paper's robustness story depends on it being a contamination artefact rather than evidence that the trend is family-fragile.

## Key experimental conditions

- 15 open-weight instruct models across 4 families: Gemma-3-it (0.27B, 1B, 4B, 12B, 27B), Phi-3-mini (3.6B), Phi-3-medium (14B), GPT-OSS-20B, Llama-3.1-Instruct (8B, 70B). Qwen-series excluded.
- Two probe-training corpora: a 203-item author-written contrastive set, and the 400-item Stages Oversight subset of the Situational Awareness Dataset (SAD).
- Probe = difference-of-means direction between testing and deployment activations, computed per layer, normalized.
- Evaluation = AUROC of the resulting linear classifier on held-out prompts; layer-wise sweep per model.

## Key quantitative results

- Eval-awareness probe AUROC (distance from 0.5) increases monotonically with parameter count from 0.27B → 70B, holding across all 4 retained families. Authors describe the curve as power-law in shape; no fitted exponent is published.
- Best layer is "early-to-middle" across families; Gemma-3-27B is an outlier, peaking at layer 3.
- Model size dominates architectural family as a predictor of probe AUROC.
- Per-model AUROC values are not tabulated in the main text we accessed.
- Compute footprint: ~500 GB memory on NVIDIA H200s for the 70B probe pass.

## Methods (what they did and didn't use)

- Linear probes on residual-stream activations — difference-of-means, no learned weights. Pure mass-univariate per layer.
- Open-weight only. Frontier closed-weight models cannot be tested with this method, which the authors acknowledge.
- No behavioural intervention: the paper does not show that activating or suppressing the probe direction changes downstream eval behaviour. That causal step was done by Hua et al. (steering_eval_aware) on Llama-3.3-70B-Instruct, but not extended here across scale.
- No SAEs, NLAs, or non-linear probes; no comparison against an MLP or polynomial probe baseline (cf. beyond_linear_probes).
- No analysis of what feature the direction actually encodes — eval-vs-deployment text classification could be reading surface cues of SAD-like prompts rather than self-referential "I am being tested" representation.

## Authors' stated limitations / future work

- MoE architectures complicate the scaling trend story; not cleanly addressed.
- Most frontier systems are proprietary; the scaling extrapolation cannot be validated against state-of-the-art models.
- Qwen exclusion attributed to dataset contamination is a hypothesis, not verified.
- Call for "scale-aware evaluation strategies" and methodological transparency as systems scale; no specific concrete follow-up experiments proposed.

## Open questions and follow-up directions

1. **No fitted exponent.** The paper's title and framing promise predictable scaling but it does not publish a power-law exponent or confidence interval. Whether the curve is genuinely power-law or just monotone is open. Re-fitting on the published AUROCs with a proper scaling-law form (and reporting irreducible loss + exponent with bootstrap CIs) would either substantiate or weaken the headline claim.

2. **What does the probe direction actually represent?** The probe is trained on text contrasts between eval-like and deployment-like prompts. The activations could encode "this prompt resembles a benchmark" (surface-feature classification) rather than "I am currently being evaluated" (self-referential state). These are different constructs and have different implications for the eval-gaming threat model. Concept-injection-style tests (cf. introspection) or counterfactual prompt rewrites could distinguish them.

3. **Probe → behaviour causality at small scale.** Hua et al. showed steering on the eval-aware direction suppresses eval-aware behaviour in a deliberately eval-aware 70B. Whether the linear direction recovered here is causally load-bearing for downstream behaviour in smaller models — or merely correlated text-classification machinery — is not tested. The scaling claim is much stronger if the direction is causally active at every scale, weaker if it's only a readout.

4. **The Qwen exclusion is load-bearing.** If SAD-like prompts contaminate Qwen pre-training, that is itself a methodological problem for the whole literature using SAD-derived contrast pairs. Either contamination is the cause (in which case SAD's discriminative power on every model is partly memorization) or the trend is family-fragile. Disentangling these requires probes trained on uncontaminated held-out contrasts.

5. **Closed-weight extrapolation.** The scaling claim's policy relevance depends on extrapolating to frontier closed-weight models. The paper acknowledges this is impossible with the current method. Whether behavioural eval-awareness proxies (e.g. realism-rewrite sensitivity, cf. natural_language_autoencoders) scale with the same exponent as the probe AUROC across the open-weight sample is a testable bridge.

## See also

- [[steering_eval_aware]] — Hua et al. show the eval-aware direction is causally load-bearing in a deliberately-trained 70B; this paper extends the existence claim across scale but drops the causal step.
- [[situational_awareness_dataset]] — provides the Stages Oversight subset used as the main probe-training corpus; both papers operationalize "eval-awareness" via the same text contrasts.
- [[deception_probes]] — sibling linear-probe method on Llama-3.3-70B-Instruct; what the deception probes pick up may overlap with eval-awareness signal at the 70B scale this paper anchors on.
- [[beyond_linear_probes]] — natural baseline-stretch: re-running the scaling analysis with TPCs / MLP probes would test whether the power-law shape is linear-probe-specific or a property of the underlying representation.
- [[natural_language_autoencoders]] — behavioural eval-awareness measurement on Opus-4.6 via verbalizer; could provide the closed-weight bridge the paper acknowledges it lacks.
- [[science_of_scheming]] — Apollo's research-agenda framing names eval-awareness as a central bottleneck; this paper is the kind of measurement work that agenda calls for.
