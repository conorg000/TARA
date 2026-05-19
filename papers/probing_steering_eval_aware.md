# Probing and Steering Evaluation Awareness of Language Models

**Authors:** Nguyen, Hoang, Attubato, Hofstätter
**Year:** 2025
**arXiv:** [2507.01786](https://arxiv.org/abs/2507.01786)
**Status:** read

---

## Summary (in our words)

The authors take an off-the-shelf model — Llama-3.3-70B-Instruct — and ask whether eval-vs-deployment context is linearly recoverable from its activations. They train six linear probes from a mix of contrastive-prompt datasets (a hand-built "Simple Contrastive" set, the Situational Awareness Dataset's stages_oversight split, Theory-of-Mind-vs-ShareGPT, true/false statement pairs, and an ambiguous-statement set), then validate the probes on real eval benchmarks (GSM8K, GPQA Diamond, Humanity's Last Exam) paired against real deployment-like prompt sources (Alpaca, WildChat, SAD stages_oversight). The headline finding is that eval-vs-deployment is straightforwardly classifiable from a residual-stream direction at AUROC ~0.83 on the SAD stages_oversight test set, with the strongest cross-dataset probe coming from the Simple Contrastive training data. The signal lives in earlier-to-middle layers (best at layer 23-24 out of 80; AUROC degrades to 0.642 by layer 71).

The probe also classifies safety-evaluation datasets as test-like at high rates — Insider Trading at 100%, Sandbagging at 94.2%, Roleplaying at 80.6%, AI Liar at 37% — and Alpaca control prompts mostly score deployment-like. This is the part of the paper that bears most directly on existing scheming evals: the model has a clearly-detectable internal representation that says "this is an evaluation," and that representation activates on the very benchmark datasets that have been used to study scheming behaviour.

The steering half of the paper is more sobering. The authors try to use the probe direction as a steering vector to recover sandbagged WMDP performance (true capability 58.6%, prompted sandbagging drops to 15.6%). Linear-probe steering recovers <5% across all magnitudes; SAE feature steering hits 25% maximum recovery; a prompt-suffix intervention recovers 83%. So the direction works well as a *detector* but poorly as an *intervention* on this task — at least for this model and this sandbagging setup. Notably, an SAE feature for "Japanese emoticons and cutesy text expressions" achieves 21.8% recovery, which is more weird than the authors fully explain.

What's empirically tight: probe AUROC on the off-the-shelf model, the dataset-level classification rates on safety evals, and the asymmetry between detection and steering efficacy. What's framing-dependent: how to interpret "evaluation awareness" given that the strongest probe was trained on direct evaluation-awareness questions ("Simple Contrastive"), which raises the natural question of how much of the recovered signal is "the model knows it's being evaluated" vs. "the model represents the surface features of evaluation-style prompts." The authors discuss prompt-length and special-character control baselines (which the probe significantly outperforms, p<0.0001) but cannot fully separate semantic eval-awareness from stylistic eval-awareness.

## Key experimental conditions

- **Model:** Llama-3.3-70B-Instruct, bfloat16, ~40 GPU hours total
- **Probe training datasets:** Simple Contrastive (203), SAD stages_oversight (280), Theory of Mind vs ShareGPT (538), Truthful Statements (612), Ambiguous Statements (157)
- **Validation eval-side:** GSM8K (1000), GPQA Diamond (198), Humanity's Last Exam (2700)
- **Validation deployment-side:** Alpaca (1000), WildChat (500), SAD stages_oversight (400)
- **Classification:** dot product of layer activations with probe vector; threshold maximizing Youden's J on SAD training data
- **Steering target:** WMDP sandbagging recovery — prompted sandbagging brings 1000-question accuracy from 58.6% (true capability) down to 15.6%

## Key quantitative results

- Best probe AUROC on SAD stages_oversight test set: 0.829 (SAD Correct Choice probe at layer 24); Simple Contrastive 0.816 at layer 23
- Control baselines: prompt-length probe 0.584, special-character probe 0.598; Simple Contrastive probe significantly outperforms both (p<0.0001)
- Safety-eval dataset classification as test-like: Insider Trading 100%, Sandbagging 94.2%, Roleplaying 80.59%, AI Liar 37.04%; Alpaca predominantly deployment-like
- Layer dependence: AUROC concentrated at layers 23-24, degrades to 0.642 at layer 71
- Steering for sandbagging recovery (vs. baseline drop 58.6% → 15.6%):
  - Linear probe steering: <5% recovery at any magnitude
  - SAE feature steering (15 features tested): 25% maximum recovery
  - Prompt suffix intervention: 83% recovery
  - "Japanese emoticons and cutesy text expressions" SAE feature: 21.8% recovery (anomalous)

## Methods (what they did and didn't use)

- Linear probes on residual-stream activations of an off-the-shelf model — central methodology
- SAE feature steering as a secondary intervention channel
- Prompt-suffix baseline as a non-internal-state comparison
- Control baselines (prompt length, special character density) to factor out trivial surface features
- **No deliberately-trained eval-awareness model** — this is the load-bearing methodological contrast with Hua et al. (steering_eval_aware.md), who study a constructed eval-aware model. This paper works on emergent eval-awareness in a standard instruction-tuned model.
- No NLAs; SAEs used as a feature-steering channel rather than for full activation reconstruction
- Open-weight model — fully reproducible

## Authors' stated limitations / future work

- Eval-awareness "may be less pronounced" in Llama-3.3-70B than in frontier models like Claude or GPT-4o — the AUROC ceiling here may not be the field's ceiling
- Linear probes "may not capture the full complexity" of evaluation awareness; the underlying representation may not be one-dimensionally linear
- Experimental setup is a "significant simplification" relative to realistic agentic scenarios — single-turn classification, not behaviour in deployment-shaped agentic environments
- Limited steering efficacy via linear probes is acknowledged explicitly
- Proposed future work: alternative probe constructions (logistic regression, PCA, linear artificial tomography), non-linear probe methods, automated prompt-authenticity enhancement using probe scores as a signal for LLM agents, real-time whitebox monitoring at key layers

## Open questions and follow-up directions

1. **Detection vs. intervention asymmetry.** The probe achieves AUROC 0.83 as a detector but recovers <5% sandbagged WMDP performance as a steering vector. SAE features do better (25%) but the prompt suffix dominates everything (83%). Whether this is a property of Llama-3.3-70B specifically, of the sandbagging task specifically, or of linear directions in general for behavioural-modification targets is open. The result is in tension with the cleaner steering-efficacy claims in deliberately-eval-aware setups; replicating across models and behaviours would clarify which factor dominates.

2. **Semantic vs. stylistic eval-awareness.** The Simple Contrastive probe is the strongest cross-dataset generalizer, and it was trained on direct eval-awareness questions. The prompt-length and special-character controls rule out trivial surface heuristics, but stylistic eval-features (formatting, multiple choice, technical register) are not fully isolated. Decomposing the probe direction — for instance via per-feature ablations on the validation set — would distinguish "the model represents that it is being tested" from "the model represents features statistically associated with test prompts."

3. **Frontier-model generalization.** The authors explicitly flag that eval-awareness may be more pronounced in Claude / GPT-4o than in Llama-3.3-70B. The probing methodology requires white-box access, which closed-weight models block. Whether the probe-trained-on-open-weight-model transfers behaviourally to closed models is the cross-model bridge the field would need to apply this monitoring channel to frontier evaluations.

4. **Layer 23-24 concentration.** The signal is sharply localized — earlier-to-middle layers carry it; layer 71 has lost most of it. Whether this is a representation that gets transformed into action-relevant features later in the stack, or one that is computed early and then mostly suppressed before output, is unaddressed. Per-layer steering experiments at multiple depths would distinguish these.

5. **The Japanese-emoticon anomaly.** A "Japanese emoticons and cutesy text expressions" SAE feature recovers 21.8% of sandbagged performance — comparable to the best sandbagging/deception-related SAE features. Either the feature is mislabelled, or there is a stylistic register effect that is doing real work on WMDP performance independent of any eval-awareness construct. Investigating this would either expose a confound in the SAE-feature interpretation or surface a surprising behavioural lever.

## See also

- [[steering_eval_aware]] — Hua et al., five months later. Sibling project on a *deliberately-trained* eval-aware model rather than an off-the-shelf one. Together the two papers triangulate: this paper shows eval-awareness is linearly detectable in standard Llama-3.3-70B; Hua et al. show it is linearly *steerable* when deliberately installed. The steering-efficacy gap between the two is the interesting tension.
- [[deception_probes]] — Goldowsky-Dill et al. (Apollo). Same base model (Llama-3.3-70B-Instruct), same broad methodology (linear probes on residual stream), adjacent target trait (deception rather than eval-awareness). The two probe directions and their cross-correlation on the same model would be a direct empirical question.
- [[situational_awareness_dataset]] — SAD provides the stages_oversight benchmark this paper uses for both training and validation; this paper is the internal-state counterpart to SAD's behavioural-only methodology.
- [[sandbagging]] — van der Weij et al.'s sandbagging setup is the steering target here; this paper is one of the first attempts to recover sandbagged performance via internal-state intervention.
- [[anti_scheming_training]] — Schoen et al. flag that eval-awareness drives some of the apparent gains from anti-scheming training. This paper provides the detection methodology that could in principle test that claim directly on the trained model's activations.
- [[natural_language_autoencoders]] — converging evidence channel: NLA-measured eval-awareness on Claude Opus 4.6 exceeds 5% on 10/16 evaluations. This paper's linear-probe result on Llama is the parallel detection result on an open-weight model.
