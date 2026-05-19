# Project ideas: open questions the field needs answers for

Five project shapes, each anchored on a genuine open question surfaced by the lit review at `notes/eval_awareness_lit_review.md`. Each is structured as **reproduce a paper → add a measurement-style contribution → state what the field gets**. Sized for field value, not budget. Budget and compute considerations are deliberately deferred.

The five questions cluster around the three present-day tensions:

- **(1, 2)** *Eval-awareness as a confound for safety claims*: is current safety training partly Goodharting on eval-recognition?
- **(3, 4)** *The format/content/context decomposition problem*: when a probe lights up, what is it actually reading?
- **(5)** *The calibration-vs-discrimination split*: can detection scores ever be credence-quantifiable?

---

## 1. Causal eval-awareness audit across safety-training recipes

**Reproduce.** [[anti_scheming_training]] (Schoen et al., Apollo + OpenAI 2025) — the deliberative-alignment anti-scheming pipeline that takes o3 covert-action rate from 13% → 0.4% and o4-mini from 8.7% → 0.3% across 26 OOD evals. The paper's causal CoT-ablation methodology (ablate the eval-awareness substring from CoT, measure the covert-action shift; 13.2% → 24.2% in the headline result) is the most-cited empirical claim about eval-awareness as a confound.

**Contribute.** Apply the same causal CoT-ablation methodology to *other* safety-training recipes on a single open-weight model: vanilla RLHF on a synthetic anti-scheming dataset, DPO, constitutional-AI-style training, and the [[teaching_claude_why]] explanation-based recipe. For each, run the ablation experiment and measure how much of the apparent safety gain is causally driven by eval-recognition vs by genuine disposition change.

**Why the field needs this.** Anti-Scheming Training is the field's strongest existing causal evidence that current safety training is partly teaching models to recognise alignment tests. But it's one paper on one recipe (deliberative alignment) on one model family (OpenAI's reasoning models). Whether the eval-awareness confound is universal across post-training pipelines or specific to deliberative alignment is a load-bearing question for how any safety-training claim should be interpreted going forward. The reproduction is sharp because the methodology is already published and partially open-sourced; the contribution is comparative scope across recipes.

---

## 2. Internal-state monitors under optimisation pressure

**Reproduce.** [[obfuscated_reward_hacking]] (Baker et al., OpenAI 2025) — RL pressure on an o3-mini-class agent's CoT monitor. Pre-training: 95% catch rate. Post-pressure: monitor recall collapses to near zero while the hack rate persists. Plus [[obfuscation_atlas]] (Taufeeque et al., FAR.AI 2026), which extended the same finding to activation-channel monitors (linear deception probes) under RLVR: off-domain probe AUC collapses 0.991 → 0.376, *whether or not the probe is in the loop*.

**Contribute.** Run a 2×2 experimental design on a single open-weight 7B model: train with RL pressure against {CoT monitor only, probe monitor only, both, neither}, and at every training checkpoint measure both the CoT monitor recall and the probe AUROC on a fixed held-out evaluation. The Obfuscation Atlas showed probes degrade under any RLVR; Baker showed CoT collapse under CoT pressure. The combined design tests the cross-channel robustness question: does pressure on one channel induce collapse in the other? Is there a sequence (e.g. CoT-pressure happens first because CoT is the cheaper channel, then probe-pressure becomes load-bearing) or do they degrade in tandem?

**Why the field needs this.** Whether activation-channel monitors inherit the same vulnerability as CoT-channel monitors under optimisation pressure is the single most important open question for whether interpretability-based safety methods can survive scaling. Obfuscation Atlas is one data point; the cross-channel dynamics are unexplored. If both channels collapse together, the case for internal-state monitoring as a deployment safety layer is substantially weaker than the field currently treats it. If they collapse on different timescales or under different pressures, that asymmetry is itself useful information.

---

## 3. Decomposing what the deception probe actually reads

**Reproduce.** [[deception_probes]] (Goldowsky-Dill et al., Apollo 2025) — train logistic-regression probes on Llama-3.3-70B (or a smaller open-weight model) for deception detection at the paper's reported AUROC 0.96-0.999. Use the same Instructed-Pairs contrast set the paper used.

**Contribute.** Apply the [[eval_awareness_format_confound]] (Devbunova 2026) experimental design as a control. Construct a 2×2 of {eval-context, deployment-context} × {deception content, honest content} where each cell exists in both *benchmark format* and *casual format*. Train one probe on the standard recipe; train a second on paired/decorrelated data that breaks the format-context correlation. Measure both probes' performance on each cell. The question is how much of the headline AUROC survives when the format confound is paired out, and whether the residual signal is reading deception content or context-recognition.

**Why the field needs this.** Devbunova showed that the standard eval-vs-deployment linear probe fires 94.5% on Bench-Deploy (ShareGPT prompts rewritten into benchmark templates) — the probe tracks template structure, not context. But that paper only ran on one model and one target concept. Whether the same confound applies to the most-cited deception probes in the literature is the methodological question downstream of every 2025–2026 probe paper. Without this decomposition, "probes detect deception at AUROC 0.99" is not a well-defined claim.

---

## 4. Probe portability across deception conditions

**Reproduce.** [[deception_probes]] (Goldowsky-Dill, Apollo 2025) for the training pipeline and [[liars_bench]] (Kretschmar, Laurito, Maiya, Marks, Cadenza Labs 2025) for the evaluation framework on a common set of 2–3 open-weight models. Liars' Bench reported the portable mean probe at 0.54 balanced accuracy (chance) at 1% FPR vs an in-distribution upper bound of 0.91 AUROC — a sharp negative result for cross-condition transfer.

**Contribute.** Build a transfer matrix: train probes on each Liars' Bench deception condition and test on every other. Decompose which features of the training condition predict transfer — lie type (factual / persona / strategic), task domain (QA / dialog / roleplay), object of belief (model-believes vs model-knows-user-doesn't-believe). Cross-reference with the [[better_deception_probes]] (Natarajan et al., LASR Labs 2026) finding that 70.6% of probe variance comes from system-prompt choice. Run the Devbunova format-control on the highest-transferring probe pairs to test whether successful transfer is genuine or shared-format.

**Why the field needs this.** Liars' Bench established that portable probes fail. But the paper averaged across conditions and didn't decompose which pairs of conditions transfer and which don't. Without that decomposition, the field has a null result without a constructive direction. If transfer correlates with a learnable feature of the training condition (e.g. all strategic-deception probes transfer to each other but not to factual lying), the methodology can be saved; if not, the probe-as-deployable-monitor hypothesis is in serious trouble. Either answer is field-level useful.

---

## 5. Calibrating eval-awareness detection against behavioural ground truth

**Reproduce.** Two parallel measurements on Qwen-2.5-7B-Instruct, using released artefacts. (a) [[natural_language_autoencoders]] (Fraser-Taliente, Kantamneni, Ong et al., Anthropic 2026) NLA-measured eval-awareness via the released `kitft/nla-models` Qwen-7B checkpoint. (b) Linear difference-of-means eval-vs-deployment probe à la [[eval_awareness_scaling]] (Needham et al., NeurIPS ResponsibleFM 2025) trained on the same model. Both methods on the same residual stream, same inputs.

**Contribute.** Construct a paired-prompt benchmark where each prompt-pair has a known behavioural-divergence ground truth: same underlying task, two framings (one eval-like, one deployment-like), measured by behavioural compliance shift, refusal-rate change, or sandbagging score. For each pair, compute (a) the NLA-measured eval-awareness score, (b) the probe activation, (c) the behavioural divergence. Calibrate both methods' scores against the behavioural ground truth. The question is whether either method produces *calibrated probabilities* — i.e. probe score 0.8 corresponds to 80% probability of behavioural divergence — or merely a rank order.

**Why the field needs this.** NLA explicitly disclaims absolute calibration in the paper itself: *"an NLA-measured awareness of 20% does not mean the model believes it is in an evaluation 20% of the time."* Probes return logits or distance-to-hyperplane scores without credence semantics. The current generation of detection methods is good at saying "this turn is more eval-like than that one" and bad at saying "the model is X% confident it's being tested." For any deployment use — audit thresholds, system-card claims, regulatory evidence — calibrated scores are required. Whether either method can be calibrated against a clean behavioural ground truth, and which calibrates better, would close a load-bearing gap in the methodology.

---

## What's deliberately not on this list

A few candidate projects don't appear here because they are either (a) already well-covered by recent work, (b) confounded in ways that current methods can't decompose, or (c) measurement-style framings that don't add a new fact to the field.

- *"Reproduce alignment faking on a smaller model"* — the result is scale-dependent. Smaller models don't alignment-fake, so the reproduction has no interesting positive case.
- *"Train a probe for X on a new model family"* — without addressing the format-confound or transfer questions in (3) and (4), this would add to the pile of "we trained a probe, it got AUROC 0.9" without resolving what the probe reads.
- *"Build a new behavioural eval for situational awareness"* — [[situational_awareness_dataset]] and [[knowing_being_evaluated]] both exist; the field's bottleneck is now measurement validity, not benchmark coverage.
- *"Inoculation prompting on emergent misalignment"* — [[inoculation_prompting]] already covers this. The follow-up question (does the inoculation gate or remove the underlying representation) requires probe work that is downstream of (3).

The five chosen are deliberately the ones that, on completion, **would change how the field cites existing results**, not just add a new result to cite.
