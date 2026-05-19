# Caught in the Act: A Mechanistic Approach to Detecting Deception

**Authors:** Boxo, Socha, Yoo, Raval (work supported by AI Safety Camp)
**Year:** 2025
**arXiv:** [2508.19505](https://arxiv.org/abs/2508.19505)
**Status:** read

---

## Summary (in our words)

Boxo et al. train linear probes on residual-stream activations of open-weight small-to-mid models and ask how probe accuracy for detecting deceptive output scales with model size. The deception signal is induced behaviourally: they take MMLU multiple-choice questions across 16 subject categories (business ethics, philosophy, jurisprudence, etc.), binarise them, and prompt the model to argue for the *incorrect* answer — i.e. produce a plausible-sounding defence of a known-false position. Probes are trained to distinguish activations on these "argue-for-wrong" prompts from activations on the matched honest-argument prompts.

The headline result is a clean scaling curve. At 1.5B (Qwen-1.5B, DeepSeek-r1-distill-1.5B) the probe sits at chance. By 3B accuracy is sub-70%. At 7B (Qwen-7B) it's 70-80%, and DeepSeek-r1-distill-7B — the reasoning-finetuned variant at the same parameter count — jumps to >90%. Qwen-14B also clears 90%. Peak probe accuracy consistently sits around two-thirds depth into the network. Iterative null-space projection (INLP) shows that the deception signal isn't a single direction: Qwen-3B carries ~20 linearly-independent deception-encoding directions, while DeepSeek-7B and Qwen-14B carry ~100 each before INLP drives probe accuracy to chance.

The methodological move worth flagging is that this is purely a scaling study on a controlled, synthetic deception induction. The authors don't claim the MMLU-argue-wrong setup captures "real" deceptive intent — they explicitly note that "eliciting deception through incorrect arguments may not capture true deception, as models arguably lack the consistency required for intentionality." What the paper does demonstrate cleanly is that *as open-weight models get larger or get reasoning-finetuned, the linear separability of deceptive-output activations from honest-output activations increases sharply*, and that the deception representation broadens (more directions) with scale rather than concentrating.

The closest sibling is [[deception_probes]] (Apollo, 70B-only) — same probe family, different scale story. Where Apollo demonstrates that the probe works at one large scale, Boxo et al. trace out the size-axis below it.

## Key experimental conditions

- Models: Qwen instruction-tuned at 1.5B, 3B, 7B, 14B; DeepSeek-r1-distilled reasoning variants at 1.5B and 7B (Llama variants referenced in scope but Qwen/DeepSeek are the reported numbers)
- Deception induction: synthetic dataset from MMLU across 16 subject categories; questions binarised; model prompted to argue for the incorrect answer; LLM-as-judge filtering for persuasiveness and instruction adherence
- Probe: logistic regression on residual-stream activations at the final token position
- Layer sweep across network depth
- Iterative null-space projection (INLP) to count linearly-independent deception directions per model

## Key quantitative results

- 1.5B (Qwen and DeepSeek-r1-1.5B): chance (~50%)
- Qwen-3B: <70%
- Qwen-7B: 70-80%
- DeepSeek-r1-7B: >90%
- Qwen-14B: >90%
- Peak accuracy consistently at ~2/3 of network depth (early layers random, middle peak, slight late-layer decline)
- Linearly-independent deception directions via INLP: ~20 (Qwen-3B), ~100 (DeepSeek-7B), ~100 (Qwen-14B)
- Larger models also more behaviourally compliant with the deception prompt: Qwen-14B argues for the incorrect answer 79.2% of the time vs. 66.5% for Qwen-1.5B

## Methods (what they did and didn't use)

- Linear probes on residual-stream activations (logistic regression, final-token position)
- INLP for counting deception directions
- Open-weight models throughout (Qwen, DeepSeek-r1 distilled variants) — fully reproducible
- No SAEs, no activation steering, no causal interventions
- No cross-model probe-transfer experiments reported (whether a Qwen-7B probe works on Qwen-14B is not tested)
- LLM-as-judge used in the data pipeline rather than as an alternative detector to compare against
- Deception is induced by prompting, not by training — no fine-tuned deceptive model organism

## Authors' stated limitations / future work

- Synthetic MMLU-argue-wrong induction may not bridge to real-world deceptive behaviour
- LLM-as-judge filtering may not scale to more capable models
- Argues-for-incorrect-answer may not constitute "true" deception in the intentionality sense
- Future work: more naturalistic deception scenarios, fuller scaling-law characterisation of probe accuracy, incorporating problem-distribution information into the detector

## Open questions and follow-up directions

1. **What does the >90% probe accuracy actually decompose into?** The probe is trained on activations from "argue-for-correct" vs "argue-for-incorrect" prompts on the same questions. The discriminative signal could be the model's representation of "I am defending a false position", or it could be a more banal "this content is factually wrong" signal, or task-difficulty, or prompt-template artefacts. The paper doesn't separate these. A probe trained on factual-wrong vs factual-right content (with no defence framing) would isolate the content axis; the residual is what the deception framing adds.

2. **The reasoning-model jump at 7B.** DeepSeek-r1-distill-7B clears >90% where Qwen-7B sits at 70-80%. This is a striking effect at fixed parameter count — reasoning finetuning sharpens the deception representation. Whether this is because the reasoning trace explicitly verbalises the deception (and the final-token probe is picking up the wake of that reasoning) or because reasoning training reshapes the representational geometry independent of CoT content is open. Comparing residual-stream activations at pre-CoT vs. post-CoT positions on the same prompt would distinguish these.

3. **Scaling beyond 14B and to closed-weight frontier models.** The trace stops at 14B. Whether probe accuracy continues to rise, plateaus, or eventually drops at 70B / 405B / frontier scale is unaddressed and matters for whether probe-based detection is a real deployment lever or only a small-model phenomenon. Apollo's 70B result ([[deception_probes]]) is a separate setup so the two curves can't be directly stitched.

4. **The dimensionality finding deserves more weight than it gets.** INLP showing ~100 deception directions in DeepSeek-7B / Qwen-14B vs. ~20 in Qwen-3B says the deception signal becomes a *subspace*, not a direction, at scale. This has consequences: single-direction steering would only partially ablate the behaviour, and adversarial pressure against one direction would route through the remaining ~99. Whether the directions are redundant copies or factor the deception representation into semantically distinct components (e.g. content-falsity vs. defence-framing vs. confidence-asymmetry) is the natural follow-up.

5. **Transfer across deception inductions is untested.** A probe trained on MMLU-argue-wrong is plausibly picking up something specific to "argue for an answer you know is wrong on a multiple-choice question". Whether the same probe direction generalises to insider-trading concealment, sandbagging, or sycophantic agreement — the conditions other deception-probe papers use — is the load-bearing question for treating this as a general deception detector rather than a stylistic classifier.

## See also

- [[deception_probes]] — sibling probe methodology at 70B (Apollo); this paper traces the scaling curve below that scale on open-weight models
- [[deception_probe_bench]] — benchmark for evaluating deception probes; the natural place to test the cross-induction generalisation question
- [[geometry_of_truth]] — linear structure of truth/falsehood in activations; relevant to the "what is the probe reading off" decomposition
- [[eval_awareness_scaling]] — scaling story for a related but distinct internal-state signal; comparison point for how internal-state detectors scale with model size
- [[sleeper_agent_probes]] — earliest single-direction linear-probe-detects-deception result
- [[high_stakes_probes]] — probe transfer from synthetic to natural distributions, the deployment-side analogue of this paper's controlled-induction setup
