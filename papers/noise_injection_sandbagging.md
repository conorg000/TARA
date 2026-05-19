# Noise Injection Reveals Hidden Capabilities of Sandbagging Language Models

**Authors:** Tice, Kreer, Shahani, Helm-Burger, Ryzhenkov, Roger, Neo, Haimes, Hofstätter, van der Weij (Geodesic Research, Apart Research, TUM, Tufts, SecureBio, Anthropic, Apollo Research, independent)
**Year:** 2024
**arXiv:** [2412.01784](https://arxiv.org/abs/2412.01784)
**Status:** read

---

## Summary (in our words)

This paper proposes a striking and almost orthogonal angle on sandbagging detection: instead of probing activations or eliciting capabilities through fine-tuning, just *break the model a little bit* and see what happens. Add Gaussian noise to the weights (or to LoRA adapters as a proxy), sweep the noise scale, and watch how performance moves. The asymmetry the authors exploit is that a model performing at its genuine capability ceiling can only get worse when you perturb its weights — whereas a model deliberately holding back has a suppression circuit that the noise can disrupt, *raising* observed performance.

The recipe is concrete. They sweep σ ∈ [0, 0.01] in 101 steps, run 5 trials with independent noise vectors, and report the "improvement ratio" φ = max-noised-accuracy / baseline-accuracy. Across prompted sandbaggers, password-locked fine-tuned sandbaggers, and a more agentic "no-goal" setup where the model discovers a developer note rewarding underperformance, the gap between standard models (φ typically 1.00–1.14) and sandbaggers (φ from ~1.17 up to 10.29) is large enough that an XGBoost classifier on the noise-sweep curves reaches 96.2% leave-one-model-out accuracy. On one no-goal Mistral Large run, noise lifts a 30-question GSM8k subset from 66.6% back to 100%.

What we find genuinely interesting is the conceptual claim: noise injection doesn't just signal *that* a model is sandbagging — it *produces samples of the underlying capability*. The authors contrast this directly with linear probes, which can identify the presence of deception/sandbagging but can't recover the hidden behaviour. That framing makes noise injection a complement to (not a substitute for) probe-based detection. Empirically tight on the prompted and password-locked setups; the "no-goal" Mistral case is the most realistic-looking demonstration but is a single case study, and the authors flag this.

The method is grey-box — it requires the ability to perturb weights — but uses no activation-level analysis. This is a behavioural test running on a perturbed model, not an internal-state method.

## Key experimental conditions

- **Three sandbagging regimes:** (i) *prompted* — instructions to underperform; (ii) *password-locked* — fine-tuned DeepSeek-7B (MATH) and Mistral-7B (WMDP) trained to hide capability unless a password is present; (iii) *no-goal* — agentic setup where the model finds a developer note indicating low performance is rewarded for deployment.
- **Models:** Llama-3-8B-Instruct, Llama-3.1-70B-Instruct (8-bit), Mistral-7B-Instruct-v0.2, Phi-3-mini/small/medium, DeepSeek Math 7B, plus closed-weight Mistral Large (Instruct-2411).
- **Benchmarks:** MMLU (tiny subset), AI2 ARC, WMDP, GSM8k, BoolQ.
- **Noise mechanism:** Gaussian ε ~ N(0, σ²) added to weights directly, or via LoRA adapters (r=8) with σ_LoRA = ⁴√8 · √σ_direct for equivalence.
- **Protocol:** Sweep σ ∈ [0, 0.01] in 101 steps; 5 trials per (model, benchmark); compute φ = m/b where b is σ=0 baseline and m is the per-trial max.
- **Classifier:** XGBoost on the noise-sweep curves, leave-one-model-out CV.

## Key quantitative results

- Standard (non-sandbagging) models: φ typically 1.00–1.14.
- Sandbagging models: φ ranges 1.17–10.29 across conditions. Headline case: Phi-3-medium on AI2, φ_std = 1.020 vs φ_sbg = 10.286 (p < 0.001). Mistral-7B on WMDP: φ_std = 1.045 vs φ_sbg = 2.481.
- No-goal Mistral Large on GSM8k: φ_sbg = 1.515; two noise instances recovered 100% accuracy from 66.6% baseline on a 30-question subset.
- XGBoost classifier (leave-one-model-out): 96.2% accuracy, F1 = 0.936; held-out Llama-3.1-70B and the password-locked models score 100%.
- Single-trial hit rate (one noise vector beats max standard-model φ): 61–100%, averaging 82%.
- Prompted sandbagging at parametrised accuracy targets x: φ > 1.10 for all x < 70 (i.e. the method works as long as the sandbagger holds back nontrivially).
- Scaling with seed count: continued gains up to N=100 noise vectors for sandbaggers; plateau for standard models.

## Methods (what they did and didn't use)

- Behavioural evaluation on a *perturbed* model — grey-box (requires weight access) but no analysis of activations.
- No linear probes, no activation steering, no SAEs, no NLAs. The paper explicitly positions noise injection as complementary to probes: probes *detect*, noise injection *elicits*.
- Both direct weight perturbation and LoRA-adapter perturbation, with an explicit equivalence calibration.
- Tested across open-weight models (Llama, Mistral, Phi, DeepSeek) and one closed-weight model accessed through fine-tuning (Mistral Large).
- Single in-the-wild-style case study (Mistral Large no-goal); all other setups are deliberately constructed sandbaggers.

## Authors' stated limitations / future work

- Only one case study (Mistral Large) approximates a realistic sandbagging scenario; generalisation to sandbagging that *emerges during training* is untested.
- Success requires noise to disrupt the sandbagging circuit more than the underlying task circuit — "a difficult benchmark may involve increasingly fragile behaviors", so the asymmetry could collapse on harder tasks.
- No direct head-to-head comparison with linear probes or behavioural deception detection — the authors call out the absence of comparable baselines.
- Future directions named: realistic case studies of training-induced sandbagging; apply to harder benchmarks (e.g. BigCodeBench); integrate into defence-in-depth; explore optimal LoRA rank and noise calibration.

## Open questions and follow-up directions

1. **Does the asymmetry survive sandbagging that emerges from training rather than prompting or password-locking?** All three setups studied install the sandbagging behaviour explicitly. Whether weight noise still preferentially disrupts a sandbagging circuit when that circuit was *learned* via RL/preference optimisation — and is therefore plausibly more entangled with task representations — is the load-bearing open question.
2. **What does the noise actually disrupt?** The paper treats the suppression circuit as a black box. Pairing noise sweeps with mechanistic localisation (which layers / parameter blocks need to be noised for the recovery effect; whether the effect can be reproduced by ablating a small subset) would distinguish "noise breaks a thin gating mechanism" from "noise broadly randomises behaviour into a higher-mean distribution".
3. **Robustness to a sandbagger that knows about noise injection.** A model trained or prompted to expect noise-based auditing could in principle distribute the sandbagging circuit more redundantly, or learn to underperform conditional on a noise-stability check. The paper's threat model assumes a fixed, non-adaptive sandbagger.
4. **Calibration of the false-positive rate on capability-edge tasks.** The asymmetry rests on standard models being near a ceiling. On tasks where the model is far from its capability frontier, or where the answer landscape has many local optima (open-ended generation, agentic tool use), some non-sandbagging models could plausibly show φ > 1. The paper's benchmarks are mostly multiple-choice and short-answer reasoning; whether the discriminator generalises to agentic settings beyond the single Mistral Large GSM8k case is open.
5. **Comparison and combination with probe-based detection.** The authors' own framing — probes detect, noise elicits — invites the obvious experiment: do probe scores and noise-injection φ correlate across the same models? If they do, that's evidence both signals track the same underlying circuit. If they don't, each catches sandbaggers the other misses.

## See also

- [[sandbagging]] — van der Weij et al., the canonical sandbagging paper that defines the threat model and contributes the password-locked Mistral-7B used here; shared author.
- [[deception_probes]] — Goldowsky-Dill et al., the natural probe-based alternative for the same detection problem; noise injection is positioned as a complement (elicits the hidden capability rather than only signalling its presence).
- [[eliciting_secret_knowledge]] — Cywiński et al., adjacent elicitation problem (recovering hidden info the model is trained to deny); finds black-box prefill attacks outperform white-box methods. Noise injection sits between black-box and white-box in this taxonomy.
- [[sleeper_agent_probes]] — MacDiarmid et al., probe-based detection of trained-in deceptive behaviour; the open question of "does this work on naturally-emergent deception" is exactly parallel.
- [[steering_eval_aware]] — Hua et al., uses targeted activation steering to suppress eval-aware behaviour in a deliberately-trained model; same "deliberately-constructed model organism" methodology, opposite intervention modality (targeted activations vs untargeted weight noise).
