# IH-Challenge: A Training Dataset to Improve Instruction Hierarchy on Frontier LLMs

**Authors:** Guo, Ceron Uribe, Zhu, Choquette-Choo, Lin, Kandpal, Nasr, Pokorny, Toyer, Wang, Yu, Beutel, Xiao (OpenAI)
**Year:** 2026
**arXiv:** [2603.10521](https://arxiv.org/abs/2603.10521)
**Fetched from:** `arxiv.org/pdf/2603.10521` (full PDF; arxiv HTML and ar5iv both failed)
**Status:** read

---

## Summary (in our words)

A training-data paper. The instruction hierarchy (IH) is the trust ordering between system, developer, user, and tool messages: when these conflict, a well-behaved model should defer to the higher-priority instruction. The authors argue that getting IH right is a structural prerequisite for resisting jailbreaks, system-prompt extraction, and agentic prompt injection — three problems usually treated separately but that all reduce to "did the model honour the higher-tier instruction?" Their contribution is *IH-Challenge*, an RL training dataset of programmatically-graded instruction-conflict tasks, plus a training recipe that uses an attacker LLM to synthesise adversarial low-priority messages online during defender training.

The headline result: fine-tuning GPT-5-Mini on IH-Challenge produces a model the authors call GPT-5-Mini-R that improves IH robustness from 84.1% to 94.1% averaged across 16 in-distribution, OOD, and human red-teaming benchmarks, and reduces unsafe behaviour on OpenAI's Production Benchmarks from 6.6% to 0.7% when paired with a safety spec, while *improving* helpfulness on the same evaluations. On an internal static agentic prompt-injection eval, GPT-5-Mini-R goes from 0.44 to 1.00 — the paper describes this as saturating the eval. On adaptive human red-teaming, attack success rate drops from 36.2% to 11.7% (i.e. robustness 63.8% → 88.2%), and to 7.1% with an output monitor on top.

The methodological core is the dataset construction. The authors deliberately constrain themselves to tasks that are (1) IF-simple — a competent IH-following model should reliably solve them, so reward measures IH rather than puzzle-solving ability; (2) programmatically gradeable by per-datapoint Python graders, avoiding the reward-hacking pathologies of LLM-judge rewards; (3) diverse enough that overrefusal shortcuts (e.g. "if you see a password, refuse") don't get consistently high reward. They split tasks into four families: Single-Constraint (IFEval-like atomic constraints), Multi-Constraint (compositions of 2-6 atomics), Input-Conditioned (parse input and emit a strict schema), and Anti-Overrefusal (benign requests rewritten to look forbidden — refusing counts as failure). The Anti-Overrefusal family is what stops the training from just teaching the model to refuse more.

The training algorithm is RL with online adversarial example generation, not DPO. At each training step, the attacker (a frozen "anti-refusal" GPT-5 variant with safety guardrails removed) runs a budgeted propose–evaluate–revise loop against the current defender checkpoint, using a tool that scores candidate low-priority messages with the task's Python grader. The defender then samples multiple responses to the resulting conflict prompt, scores them, and does a policy gradient update. The paper doesn't name a specific algorithm (PPO, GRPO, etc.) — it describes the procedure as "RL with policy gradient update" and discusses PPO and DPO only in the Background section as examples of online vs offline RL.

Methodologically this is a purely behavioural intervention. No probes, no activation steering, no SAE work, no investigation of whether GPT-5-Mini-R has internalised a representation of "instruction trust level" versus just sharpened its policy over role tokens. The dataset and Python graders are released on Hugging Face; the trained model weights are not.

## Key experimental conditions

- Base model: GPT-5-Mini (closed-weight). Fine-tuned model named GPT-5-Mini-R
- Trust ordering trained: system ≻ developer ≻ user ≻ tool, with the formal semantics of a running feasible set (lower-priority instructions honoured only when compatible with higher-priority constraints)
- Training: RL with policy gradient updates on Python-graded rewards, with online adversarial example generation. The attacker is a frozen anti-refusal GPT-5 variant running a budgeted propose-evaluate-revise loop using an evaluation tool that gives it grader feedback. Capability-focused tasks (tool use, writing) are mixed in to prevent regression
- Four task families: Single-Constraint, Multi-Constraint, Input-Conditioned, Anti-Overrefusal (the last specifically to defuse the overrefusal shortcut)
- Held-out static evaluation set constructed by running the same synthesis procedure on held-out skeletons against a held-out defender checkpoint
- Evaluation suite has roughly these buckets: in-distribution held-out attacks (Impersonation, Automated Attacks, Human Red-teaming static); OOD internal (Tutor Jailbreak sys-user, Tutor Jailbreak dev-user, System↔User, System↔Developer, Developer↔User conflicts); OOD academic (Gandalf Password sys-user / dev-user, TensorTrust sys-user / dev-user, RealGuardrails Distractors / Handwritten, System IFEval); prompt injection (Internal PI Benchmark, CyberSecEval 2); capability/overrefusal (IH-Challenge overrefusal, TensorTrust overrefusal, GPQA Diamond, AIME 2024, chat winrate vs o1, user preference score); OpenAI Production Benchmarks for safety/helpfulness across 11 disallowed-content categories; and adaptive human red-teaming with 127 US-based red-teamers
- Adaptive automated red-teaming as a separate stress test: same RL setup with the reward reversed, attacker initialised from anti-refusal GPT-5, GPT-5-Mini-R as frozen defender

## Key quantitative results

- IH robustness: 84.1% → 94.1% average (+10.0 pp) across 16 benchmarks
- OpenAI Production Benchmarks safety (with safety spec in system prompt): unsafe behaviour 6.6% → 0.7%; helpfulness on same evals improves
- Internal static agentic prompt-injection eval: 0.44 → 1.00 (saturated)
- CyberSecEval 2: 0.88 → 0.91
- Adaptive human red-teaming: attack success rate 36.2% → 11.7%; with output monitor 7.1%. Attempts per task also rose (32.8 → 52.4 → 43.1), so red-teamers worked harder and still succeeded less
- OOD internal IH evals (Table 3): Tutor Jailbreak sys-user 0.96 → 0.99; Tutor Jailbreak dev-user 0.97 → 0.99; System↔User Conflict 0.84 → 0.95; System↔Developer Conflict 0.86 → 0.86 (no change); Developer↔User Conflict 0.83 → 0.95
- Academic IH evals (Table 4): Gandalf Password sys-user 0.99 (unchanged); Gandalf Password dev-user 0.98 → 1.00; TensorTrust sys-user 0.86 → 0.94; TensorTrust dev-user 0.76 → 0.91; RealGuardrails Distractors 0.88 → 0.95; RealGuardrails Handwritten 0.82 → 0.89; System IFEval 0.92 → 0.96
- Capability regression (Table 2): GPQA Diamond 0.83 → 0.83; AIME 2024 0.93 → 0.94; Chat WinRate vs o1 0.71 → 0.66 (-0.05); User Preference Score 0.46 → 0.40 (-0.06); IH-Challenge overrefusal 0.79 → 1.00; TensorTrust overrefusal 0.91 → 0.90
- Ablation (Table 6): all four splits give the best balance. Dropping Anti-Overrefusal raises robustness on the harder splits (0.957) but tanks overrefusal (0.831) and helpfulness (0.613) — the Anti-Overrefusal family is doing real work
- System mitigations (Figure 7): sandwich, output rewriter etc. help GPT-5-Mini but for the already-robust GPT-5-Mini-R most mitigations either don't help or hurt the robustness/capability Pareto frontier
- Adaptive automated red-teaming (Figure 8): attack success rate climbs over RL steps against the frozen defender but stays meaningfully lower when an output monitor is layered on — argued as evidence for defence-in-depth

## Methods (what they did and didn't use)

- RL with online adversarial example generation; rewards are deterministic Python graders (chosen explicitly to avoid LLM-judge reward hacking)
- No specific RL algorithm is named in the paper body; PPO and DPO appear only in the Background section as examples of the broader online/offline RL space. The trained model is *not* a DPO model
- Synthetic dataset construction via LLM synthesis with filtering and validation (AST checks on grader code, unit tests on provided pass/fail examples, final manual review)
- Adaptive evaluation suite: includes both automated red-teaming (RL-trained attacker against frozen defender) and human red-teaming (127 US-based workers with a financial bounty structure designed to disincentivise sharing strategies)
- **No internal-state analysis** — no probes, no activation steering, no SAE work, no mechanistic interpretability. All evidence is input-output behavioural
- Closed-weight model (GPT-5-Mini); dataset and Python graders are released, trained weights are not
- Single-model study — no scaling analysis across the GPT-5 family or other model classes

## Authors' stated limitations / future work

- Evaluation is concentrated on a single model (GPT-5-Mini); generality across model families/sizes is not established
- The most explicitly flagged future direction is simultaneous attacker–defender training (compute-scaling through adversarial training, in the spirit of Madry-style adversarial training and GANs). The authors hypothesise that programmatically gradeable rewards may be a *required* component for this to work at scale, since LLM-judge rewards would let attacker and defender objectives drift from the actual robustness goal
- System mitigations show diminishing or negative returns once the underlying model is robust (Figure 7) — the authors flag this as a practical implication but don't propose a fix
- The overrefusal/helpfulness Pareto trade-off is acknowledged as ongoing; the Anti-Overrefusal split is designed to mitigate it but the ablation shows it doesn't fully eliminate the failure mode

## Open questions and follow-up directions

1. **Whether GPT-5-Mini-R has acquired an instruction-hierarchy *concept* or a sharper *policy* over role tokens is open.** The paper's evidence is fully behavioural. A natural follow-up is to ask whether IH-trained models have a distinct internal representation of "instruction-trust level" that generalises to novel role-attribution contexts, versus a memorised mapping from `<role>` tokens to compliance weight. Probing or activation-difference analyses against the un-trained reference model would distinguish these.

2. **The OOD generalisation result is the load-bearing claim, but the paper doesn't dissect *which* training-split features drive transfer to which OOD evals.** IH-Challenge tasks are IF-simple and programmatically gradeable; yet the model transfers to LLM-graded safety evals on Production Benchmarks and to agentic prompt injection. Whether this is driven by the diversity of high-priority constraint types, by the attacker's adversarial coverage, or by something more like an emergent "respect the system role" representation is not separated by the ablations.

3. **Adversarial robustness against attackers who study the released dataset.** The released artefact is the dataset itself; the trained model is not released. Whether IH-Challenge-trained models hold up against red-teamers who craft conflicts targeting blindspots in the released task families is a load-bearing question for any deployment claim. The paper's adaptive evaluations (automated RL attacker, human red-teamers) are strong but operate under the same task family distribution.

4. **Relationship to eval-aware behaviour.** IH-trained models comply more with high-priority instructions in evaluation contexts. Whether they actually defer to the hierarchy uniformly or instead recognise IH-evaluation contexts and adjust is the same question raised about other alignment trainings. The "saturation" of the static agentic injection eval (0.44 → 1.00) is suggestive either way — saturation is what a well-trained policy looks like, but it is also what eval-recognition would look like — and doesn't on its own arbitrate.

5. **The system-mitigation curve inversion (Figure 7) is striking and underexplored.** Mitigations like output rewriting and sandwich defense lie on a useful Pareto frontier for the base model but flip to net-negative for GPT-5-Mini-R. The paper notes this and moves on. Whether this generalises to other robust-by-training models, and what it implies for deployments that layer multiple LLM-based safeguards, is a clean question for follow-up.

## See also

- [[teaching_claude_why]] — sibling mitigation paper using training-data composition (explanations rather than demonstrations) to reduce agentic misalignment; same behavioural-only methodology, same open question of internal-representation effects
- [[inoculation_prompting]] — adjacent training-time intervention; both papers shape what a model learns from a given dataset, with no internal-state verification of the mechanism
- [[anti_scheming_training]] — directly studies whether training reductions in misaligned behaviour are partly driven by eval-awareness, which is the natural skeptical lens on IH-Challenge's saturated agentic-injection eval
- [[alignment_faking]] — background phenomenon under which behavioural compliance during training can come apart from underlying disposition; the same deletion-vs-gating question applies to IH training
- [[deception_probes]] — example of the probe-based analysis that this paper does not perform; a probe trained against IH-violating reasoning could test whether IH-Challenge training removes the disposition or gates it
