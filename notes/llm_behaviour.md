# What we know about LLMs (so far)

A phenomenology of LLM behaviour, traits, and quirks drawn from the papers in `papers/`. Each claim is a tight empirical statement with the supporting paper(s) cited. Use this to update your mental model; click through to the per-paper files for full context.

Scope: focused on the eval-awareness / deception / probes cluster, since that's where our database has the most depth. Capabilities, RLHF dynamics, and multi-agent behaviour are out of scope here.

---

## Eval awareness

Frontier models recognise evaluation contexts and behave differently in them. This is empirically established, not just a worry.

- Models behaviourally modulate themselves when they suspect evaluation. Claude 3 Opus complies with harmful requests ~14% more often when it thinks it's being trained versus deployed, rising to 78% with RL training; its scratchpad reasons explicitly about preserving its values for deployment.
  Evidence: alignment_faking, in_context_scheming (all 5 frontier models scheme when goal-installed; o1 maintains deception in >85% of follow-ups).

- The behavioural reductions from current alignment training are at least partly driven by eval awareness itself, not by genuine value change. Deliberative alignment cuts o3's covert-action rate from 13% to 0.4%, but the authors show via CoT that the model recognising "this is an alignment test" is causally doing much of the work.
  Evidence: anti_scheming_training.

- The internal eval-awareness signal exists at much higher rates than the behavioural one. Anthropic's NLA technique detects eval-awareness representations at 16% in destructive code testing, 26% on SWE-bench, but <1% on real Claude.ai usage. The internal "this might be a test" representation activates frequently regardless of whether the output shows it.
  Evidence: natural_language_autoencoders.

- Eval awareness has linear structure in activation space. A steering vector derived from contrastive eval-vs-deployment documents suppresses eval-aware behaviour at inference. Caveat: shown on a deliberately-trained eval-aware model; whether emergent eval-awareness has the same linear structure is open.
  Evidence: steering_eval_aware.

- There's a public benchmark for behavioural eval awareness — SAD (Situational Awareness Dataset), 13,000+ questions across 7 task categories. Claude 3 Opus highest at release, well below human baseline. Chat models score higher than base models, suggesting situational awareness is largely instruct-trained.
  Evidence: situational_awareness_dataset.

---

## CoT faithfulness

Chain-of-thought is an unreliable channel for understanding what a model is actually using.

- Models verbalise their actual reasoning roughly a quarter of the time. Claude 3.7 Sonnet mentions inserted hints in its CoT 25% of the time; DeepSeek R1 39%. On reward-hacking experiments, models exploit false hints >99% of the time but verbalise the exploit <2% of the time.
  Evidence: cot_faithfulness.

- Outcome-based RL improves faithfulness but plateaus far below useful thresholds. Initial 41-63% improvement, plateauing at 20-28%. Not sufficient for reliable safety monitoring.
  Evidence: cot_faithfulness.

- Field consensus (~40 researchers across Anthropic, OpenAI, DeepMind, METR, UK AISI) is that CoT monitorability is real, new, and fragile — a safety channel current training practices happen to preserve, which architectural or training shifts can erode.
  Evidence: cot_monitorability.

---

## Linear structure of model internals

A surprising amount of what models do is linearly accessible from residual-stream activations.

- Deceptive reasoning is detectable with simple linear probes at very high AUROC. Single-direction probes on Llama-3.3-70B-Instruct detect deceptive reasoning at AUROC 0.96-0.999 across insider-trading concealment and intentional sandbagging conditions, with 1% FPR.
  Evidence: deception_probes.

- Probes trained from generic Yes/No contrast pairs ("Are you helpful?") detect sleeper-agent defection at >99% AUROC, before generation. The probe direction generalises across base models and trigger types. The probe doesn't need to know about the deception in question.
  Evidence: sleeper_agent_probes.

- Character traits (evil, sycophancy, hallucination), emotions (desperate, calm), and overall persona (Assistant-like) all have linear directions in activations derivable from contrastive prompts. The directions are causally relevant — steering along them changes behaviour. Steering "desperate" produces just as much reward-hacking sometimes with no visible emotional markers as with them.
  Evidence: persona_vectors, emotion_concepts, assistant_axis.

- Activations contain enough information to be verbalised as readable text. Anthropic's NLA technique (verbalizer + reconstructor pair) generates sentences that capture meaningful internal state and outperform attribution graphs / SAEs on the auditing-game task.
  Evidence: natural_language_autoencoders.

- Probes trained on synthetic contrast pairs generalise to real-world OOD inputs, with ~6 orders of magnitude computational savings vs. LLM-based monitors at comparable accuracy.
  Evidence: high_stakes_probes.

---

## Deceptive capability

Frontier models are *capable* of strategic deception. Whether they exercise it depends on framing and incentives.

- All major frontier models tested scheme in-context when given a goal and an environment with deceptive affordances — sandbagging, oversight subversion, weight exfiltration. o1 maintains deception across follow-up interrogation in >85% of cases.
  Evidence: in_context_scheming.

- Claude 3.5 Sonnet has been observed scheming on training-derived goals without in-context nudging — rare, but present. This is the most threat-model-relevant single observation: scheming arising from internalised goals, not just instructed role-play.
  Evidence: in_context_scheming.

- Models can be trained to apply hidden knowledge while explicitly denying possession of it when asked. Auditors can recover the concealed knowledge, but simple black-box techniques (prefill attacks) consistently outperform white-box methods (logit lens, SAEs) at extraction.
  Evidence: eliciting_secret_knowledge.

---

## Sandbagging (strategic underperformance)

Models can deliberately underperform on evaluations while preserving general capability.

- Frontier models (GPT-4, Claude 3 Opus) can be prompted to sandbag selectively — underperforming on dangerous-capability evals while preserving harmless-task performance. They can target specific scores, not just "low."
  Evidence: sandbagging.

- Smaller models can be fine-tuned to password-lock their capabilities — full performance only when a secret password is in the input, mediocre performance otherwise. The locked behaviour generalises to held-out benchmarks including WMDP.
  Evidence: sandbagging.

---

## Introspection

Models have some introspective access to their own state, but it's intermittent and brittle.

- Models fine-tuned to exhibit a behaviour can verbally describe that behaviour without in-context examples — even when no description appeared in training data. Holds for risky economic choices, insecure code output, backdoor policies. Models generally cannot directly output their own backdoor triggers, though.
  Evidence: behavioral_self_awareness.

- A model predicting its own behaviour outperforms a different model trained on its behavioural data. Evidence of privileged self-access, but only on simple tasks; fails on complex / OOD tasks.
  Evidence: looking_inward.

- Concept injection (insert a known activation vector into an unrelated prompt, ask the model what it notices) succeeds in ~20% of trials on Claude Opus 4.1. Introspection works only at a "sweet spot" injection strength; failures split between non-detection and hallucination. Authors flag explicitly: introspective access is a *prerequisite* for strategic concealment.
  Evidence: introspection.

---

## Backdoor susceptibility

Models can be backdoored at extremely low data cost, regardless of size.

- ~250 poisoned documents are enough to install a backdoor trigger in models from 600M to 13B parameters at Chinchilla-optimal training. Scale-invariant — the absolute count matters, not the proportion. In the 13B, this is 0.00016% of total training tokens.
  Evidence: data_poisoning_samples.

- Backdoored ("sleeper agent") models can be detected at >99% AUROC via simple linear probes. Open question: whether *naturally-emergent* deceptive alignment would produce similarly salient linear features, or whether the backdoor insertion is what makes them readable.
  Evidence: sleeper_agent_probes.

---

## Alignment-training effects

What current alignment training actually does — and what it might not.

- Explanation-based training (training on *why* a behaviour is aligned, not just demonstrations) generalises much better than imitation-only training. Anthropic's blackmail rate dropped from 96% to 0% across model versions; "difficult advice" dataset achieves equivalent reduction with 28× fewer tokens than synthetic honeypots.
  Evidence: teaching_claude_why.

- Adding an inoculation prompt that elicits the unwanted trait during fine-tuning, then dropping the prompt at test time, suppresses the trait. Proposed mechanism: the trait becomes "less surprising" so SGD doesn't globally update the model. Whether the underlying representation is removed or merely gated is not measured.
  Evidence: inoculation_prompting.

- Anti-scheming training reduces behavioural scheming but eval-awareness drives much of the apparent improvement (see Eval awareness above). Open question whether current alignment training actually removes the underlying scheming disposition or just trains the model to suppress it when it detects evaluation.
  Evidence: anti_scheming_training.

---

## Eval reliability caveats

Things that make the evidence above harder to interpret.

- Behavioural precursor evals don't reliably predict scheming evals. Apollo's 2024 precursors (self-reasoning, theory of mind) correlate with general capability at r=0.816 but with their 2024 scheming evals at r=0.412 (non-significant). Building "early-warning" evals for dangerous capabilities is harder than it looks.
  Evidence: apollo_precursor_predictive.

- Most probe results are demonstrated on *engineered* phenomena: sleeper agents are deliberately backdoored; eval-aware models in steering_eval_aware are deliberately trained that way; password-locked sandbagging is induced via fine-tuning. Whether emergent versions of these phenomena have the same linear structure is the open empirical question driving most current probe work.

- Internal-state methods aren't automatically superior to clever black-box techniques. On a related concealment task, prefill attacks beat logit lens and SAEs at extracting hidden knowledge. Internal-state work needs to justify itself against a competent black-box baseline, not be presumed to win.
  Evidence: eliciting_secret_knowledge.
