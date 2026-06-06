# Features as Rewards: Scalable Supervision for Open-Ended Tasks via Interpretability

**Authors:** Prasad, Watts, Merullo, Gala, Lewis, McGrath, Lubana (Goodfire AI)
**Year:** 2026
**arXiv:** [2602.10067](https://arxiv.org/abs/2602.10067)
**Fetched from:** `arxiv.org/pdf/2602.10067` (v3) — HTML conversion had a fatal error and truncated to abstract only; PDF text extracted locally with `pdftotext`
**Status:** read

---

## Summary (in our words)

This is a "flip the affordance" paper. The interpretability literature has mostly used probes/features for *monitoring* (read off a concept at test time) or *steering* (causally push a behaviour). The authors propose a third use: turn a probe into a **reward function** and do RL against it. The motivating problem is open-ended behaviours — things like factuality, helpfulness, sycophancy — where you can't write a programmatic verifier and an LLM judge is slow, expensive, and poorly calibrated. Their claim is that even when a model *can't reliably verbalize* whether a claim is true, its internal features often *track* truth well, so you can probe that feature and use the probe output as a cheap, dense, well-calibrated reward signal. They operationalize this on hallucination-reduction with Gemma-3-12B-IT and call the pipeline **RLFR (Reinforcement Learning from Feature Rewards)**.

The pipeline has four stages, each instantiated with an **attention probe on the frozen base model's residual stream** (layer 20 for span probes, layer 24 elsewhere — explicitly *not* SAEs, just supervised attention probes). (1) **Localize**: a token-level probe extracts "Entity" spans (falsifiable claims). (2) **Classify**: a span-level probe predicts whether each entity is hallucinated (AUC 0.94 on validation). (3) **Intervene**: when the classification probe fires, the policy is sent into a fresh sub-context and asked to *maintain / retract / correct* the flagged entity. (4) **Reward**: separate **Retraction** and **Correction** probes grade whether the intervention actually resolved the hallucination, and these probe scores become the RL reward (wrapped in a multiplicative legibility × substantiveness × probe-score rubric, with a Lagrange-constrained retraction rate). RL is a modified ScaleRL (GRPO-style group sampling, group size 32) for 360 steps.

The headline is a **58% reduction in hallucination rate** (RLFR + best-of-32 sampling) vs. the base model, decomposed into ~10% from the policy itself becoming less hallucinatory, ~35% from inlining corrective interventions in-context, and ~13% from the policy resolving hallucinations on net — at roughly **two orders of magnitude lower reward-compute cost** than using Gemini 2.5 Pro with web search as the judge ($3,818 vs. an estimated $344,064 over the first 300 steps). Standard benchmarks (MMLU, GSM8K, MATH, BBH, ARC, etc.) are essentially unchanged, and they check several off-target confounders (claim count, Gemini blind preference ~50.9%, KL localized to unsupported tokens).

What's load-bearing vs. framing: the **2-orders-of-magnitude cost claim and the benchmark-preservation are solid**, and the n=256 best-of-N result where the **probe beats Gemma's own token-space self-judgment by ~15 points** is a genuinely interesting "the model knows more than it can say" demonstration. The bigger conceptual claim — that this generalizes to *alignment-critical* open-ended behaviours — is aspirational; they only test hallucinations, on one 12B model. We'd also flag that the 58% number is a *system* result (policy + monitoring harness + best-of-32 inlining), not a property of the trained weights alone; the weights-only "Policy Reduction" is 10%. The paper is honest about this decomposition. (Minor: the submitted v3 still has a `TODO: caption` on Table 1 and `??` placeholders in the Fig. 4 caption — the numbers are all present in the table cells, but it reads like a not-fully-polished preprint.)

## Key experimental conditions

- **Model:** Gemma-3-12B-IT only, as both base policy `π_base`, RL student `π`, and the LLM-judge for the rubric terms. No other model sizes/families.
- **Grader (gold reward, for *probe training* only):** Gemini 2.5 Pro with web search, used to label ~5M entities (65.5% Supported / 22.9% Not Supported / 11.6% Insufficient Info).
- **Dataset:** Longfact++ (~20K longform-eliciting questions across biology, law, economics, history, etc.); eval on Longfact / Longfact++.
- **Four probes**, all attention probes on frozen `π_base` residual stream: Localization (token-level, causal transformer), Classification (span-level, layer 20), Retraction, Correction (5-class reward heads).
- **Reward** = multiplicative rubric (legibility × substantiveness × probe score), with a Lagrange constraint targeting a 0.4 retraction rate and a 0.65 retraction reward cap.
- **RL:** modified ScaleRL objective with k1 KL estimator + importance sampling; batch 32,768; 360 optimizer steps; lr 1e-6; KL weight 0.02; reference-model reset every 192 steps; group size 32.
- **Inference variants compared:** Base, Base+Monitor (base model + monitoring pipeline + inlined interventions), RLFR-NI (RL'd policy, no inline interventions), RLFR (inline), RLFR-bo32 (best-of-32). Plus a **probe-reward vs. Gemma-self-judge** best-of-N comparison up to n=256.

## Key quantitative results

- **Overall hallucination reduction (Table 1 / Fig. 4):** RLFR-bo32 **58.0% ± 1.4%**; RLFR (inline, no BoN) 56.6% ± 1.9%; RLFR-NI 31.4% ± 2.3%; Base+Monitor 30.9% ± 0.9%.
- **Decomposition of the 58%:** Policy Reduction (weights only) **10.0%**, In-Context Reduction (inlined interventions) **~35%**, Direct Reduction **~13%**.
- **Cost:** ~**$3,818** probe-reward compute vs. estimated **$344,064** for Gemini-2.5-Pro-with-search reward over the first 300 steps — ~2 orders of magnitude cheaper.
- **Classification probe:** AUC **0.94** on validation; in streaming test-time use at threshold 0.7: **0.85 precision / 0.56 recall** (inline), **0.88 / 0.61** (not-inline).
- **Probe reward beats self-judgment:** at n=256 best-of-N, the feature-based reward pipeline outperforms Gemma grading its own interventions 1–10 by **~15 percentage points** — the model represents a strong ordering of interventions it cannot output in token-space.
- **Test-time decomposition at n=32 (Fig. 8):** of policy hallucinations, 56% detected by the monitor; of detections, 22% Fixed, 36% Retracted, 42% improperly handled.
- **Benchmark preservation (Table 1):** RLFR vs. measured base — MMLU 67.2 vs 69.2, GSM8K 73.0 vs 72.3, MATH 23.0 vs 23.3, BBH 55.2 vs 55.4, ARC-c 72.9 vs 72.5, HellaSwag 83.6 vs 83.8 — essentially flat.
- **Off-target checks:** claim count 63.4 vs 63.6 entities/completion (not just being more cautious); Gemini blind preference 50.9% over 1000 pairs; KL divergence 10–20% larger on Not-Supported than Supported tokens (targeted update); reward probe runs equivalently on base vs. RL'd policy activations (no 2× parameter cost at inference).
- **Train-time scaling (Fig. 6):** most Policy-Reduction gain by step 300.

## Methods (what they did and didn't use)

- **Linear probes:** no — they use **multi-head attention probes** (single learned query per head, multilayer inputs, sigmoid/softmax heads), explicitly motivated by the contextual nature of the task and following McKenzie et al. 2025 / Kramár et al. 2026. So this is internal-state probing, but a step up in expressivity from single-direction linear probes.
- **SAEs:** no — despite the "features" framing and Goodfire affiliation, the features here are **supervised attention-probe readouts of the residual stream**, not sparse-autoencoder features.
- **Steering:** no causal activation steering. The interventions are *behavioural* (the policy is prompted to retract/correct in a fresh context), not activation edits.
- **Probes are trained on the frozen base model** and shown to transfer to the RL'd policy's activations (shared-initialization argument), which is also their stated **monitor-evasion mitigation**: because the probe runs on frozen parameters, the student "can't" drift its representations to fool it (they claim this empirically holds but flag it may break under more optimization).
- **RL:** modified ScaleRL (GRPO-lineage group sampling), Lagrange-constrained reward shaping.
- **Open weights:** Gemma-3-12B-IT; reward grader is closed (Gemini 2.5 Pro). Probing/intervention viewer released as a demo.

## Authors' stated limitations / future work

- **Single behaviour, single model:** only hallucination, only Gemma-3-12B-IT. Future work named: sycophancy/agreeableness modulation, code/CoT verbosity reduction.
- **Mechanisms unexplained:** they measure quantitative/qualitative change but the *why* (esp. why inlined interventions reduce hallucination — hypothesized in-context belief shift) is left to future interpretability work (App. G is a preliminary probe).
- **Monitor-evasion / obfuscation:** they acknowledge the standard worry (training against a monitor teaches evasion; cite Bailey et al. 2024 "Obfuscated activations bypass LLM latent-space defenses") and claim the frozen-probe + naturalness-constraint setup mitigates it *in this case*, but explicitly say "further work is needed to ascertain the (in)efficacy of this mitigation" under more optimization.
- **Inline degeneration:** repeated/severe inline interventions can push the model out of distribution and degenerate (App. F.5).
- **Evaluation circularity:** the eval pipeline reuses the same prompting/tooling stack as data collection, so labels are "internally consistent by construction"; they backstop with red-teaming and manual audits.
- **Cascade future work:** use a more expensive verifier only when probe confidence is low (probe→LLM cascade, à la high-stakes-probes).

## Open questions and follow-up directions

1. **Does "features as rewards" survive monitor-evasion pressure at scale?** The whole safety value rests on the frozen-probe mitigation holding. They concede it's untested under heavy optimization. The [[obfuscation_atlas]] result (RLVR against a deception probe induces obfuscated activations even with a frozen detector) is the natural adversarial prior here — would RLFR's frozen attention probe go blind the way those linear probes did?
2. **How much of the 58% is the *trained policy* vs. the *test-time harness*?** Weights-only reduction is 10%; the rest is monitoring + inlined ICL + best-of-32. Whether a reward-feature signal can be pushed deeper into the weights (rather than relying on an inference-time scaffold) is the obvious next experiment.
3. **The "model knows more than it can say" gap (probe beats self-judgment by 15 pts at n=256)** is a clean calibration result. How wide is this gap across behaviours and model sizes, and does it shrink as models get better at verbalized self-grading?
4. **Generalization to alignment-critical open-ended behaviours** is the headline aspiration but entirely untested. Factuality is unusually friendly (cheap-ish gold labels via web search exist; the feature is well-calibrated). Behaviours where the *gold signal itself* is contested (sycophancy, deception) are a much harder test of whether probe-calibration-to-ground-truth holds.
5. **Attention probes vs. linear probes as reward heads:** they jump straight to attention probes for contextuality. Whether the extra expressivity is necessary (and whether it widens the reward-hacking attack surface vs. a low-expressivity linear probe — a tradeoff they invoke in the inverse-RL framing but don't ablate) is open.

## See also

- [[harmfulness_refusal_separately]] — cited directly; same "features track a concept the model may not act on" lineage (harmfulness-recognition probe), here repurposed from monitor to reward.
- [[high_stakes_probes]] — McKenzie et al., the attention-probe architecture and probe→LLM cascade idea they build on and cite as future work.
- [[obfuscation_atlas]] — the adversarial counterpoint: RLVR against a deception probe produces obfuscated activations; directly relevant to their monitor-evasion mitigation claim.
- [[obfuscated_reward_hacking]] — Baker et al.'s "don't optimize against your monitor" result; RLFR is precisely optimizing against an internal monitor, so its frozen-probe defense is the load-bearing difference.
- [[persona_vectors]] — cited (Chen et al. 2025b); the "monitor-and-steer with one direction" pattern that this paper extends into "reward with the probe."
- [[scaling_monosemanticity]] — cited; the SAE-feature lineage RLFR explicitly does *not* use (supervised attention probes instead).
- [[deception_probes]] — sibling internal-state-as-signal method; relevant to question 4 (using probes as reward for contested-gold behaviours like deception).
