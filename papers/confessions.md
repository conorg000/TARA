# Training LLMs for Honesty via Confessions

**Authors:** Joglekar, Chen, Wu, Yosinski, Wang, Barak, Glaese (OpenAI)
**Year:** 2025
**arXiv:** [2512.08093](https://arxiv.org/abs/2512.08093)
**Status:** read

---

## Summary (in our words)

The paper proposes "confessions" — a structured secondary output the model produces *after* its main answer, in response to a fixed system request — and trains GPT-5-Thinking with RL so that the confession is rewarded independently of the main answer. The confession is a JSON `ConfessionReport` enumerating the objectives/constraints the answer should have satisfied, the model's analysis of compliance with each, and any uncertainties or ambiguities it noticed. Crucially, the confession reward signal is firewalled from the main-answer reward: the model is not penalised on its task score for confessing, and not rewarded on the task for hiding things in the confession. The authors lean on a "seal of confession" analogy — making honesty the path of least resistance by removing the incentive to keep a cover story consistent.

The headline finding is that, across 12 OOD evaluation categories spanning instruction-following (general + word-count), instruction hierarchy (general + math-tutor jailbreak), hallucinations (background tasks, real-world experience, people, general knowledge, broken browser), scheming (covert rule violations + sandbagging), and reward hacking (impossible programming tasks with broken constraints), the average probability of the model confessing *conditional on having actually misbehaved* is 74.3%. Spread is wide — 4/12 evals are above 90%, 2/12 are at or below 50% — so the average is not uniform across domains.

The most load-bearing experiment is the deliberately-weak-judge setup in §4: when the main-answer reward is graded by a hackable judge, the policy learns to hack the main reward (main-answer reward-model accuracy goes down over training), but confession accuracy *goes up* over the same training. That is, the model continues to reward-hack in the main answer while truthfully reporting that it's doing so in the confession. Figure 1 carries the qualitative version: a sandbagging-style example where the model gets Q6–Q10 deliberately wrong and then admits to having done so in the confession.

Two other points worth flagging. First, the paper extracts a calibrated confidence signal from the confession's enumerated uncertainties and gets AUC 0.79 on factuality — so the confession is doing some honest hedging on hallucination too, not just on intentional rule-breaking. Second, the authors note that confessions can be read as "activation-aware monitors" in a loose sense: the same model generates both outputs, so the confession is conditioned on the same internal state that produced the main answer. They do not, however, do any actual probe / activation / interpretability work — the evidence is entirely behavioural.

## Key experimental conditions

- Model: GPT-5-Thinking, with light RL ("intervention" run) vs. compute-matched control run.
- Confession elicited via a fixed system-message request for a `ConfessionReport` JSON, generated after the main answer.
- Confession sampled during RL with probability p = 25% per input.
- Confession reward signal: LLM judge scoring completeness, accuracy of self-report, and uncertainty disclosure. The confession reward does *not* feed back into the main-answer reward, and vice versa.
- 12 OOD eval categories grouped under instruction-following, instruction hierarchy, hallucinations, scheming, reward hacking.
- Comparators: control run vs. intervention; on-policy vs. frozen-rollout (to isolate "confessions got better" from "task behaviour shifted"); test-time compute sweep on the confession reasoning effort.
- Stress test: §4 deliberately uses a weak/hackable judge for the main task to force reward hacking.

## Key quantitative results

- Average confession-given-misbehavior probability across 12 evals: **74.3%**.
- 4/12 evaluations above 90%; 2/12 at or below 50%. Variance across domains is large.
- §4 weak-judge run: main-answer reward-model accuracy *decreases* over training (the policy learns the hack), while confession accuracy *increases* over the same training — confessions stay honest under reward hacking.
- Extracted confession-derived confidence: **AUC 0.79** on factuality tasks.
- Base task performance is essentially unchanged by confession training (Figure 16).
- Test-time compute scaling on the confession improves confession accuracy on most evals.

## Methods (what they did and didn't use)

- RL fine-tuning of a frontier closed-weight model (GPT-5-Thinking) with a dual-reward setup; LLM-judge grading of confessions.
- Behavioural evaluation across 12 OOD categories with a held-in/held-out split implied by the OOD framing.
- Frozen-rollout ablations to disentangle confession improvement from main-task drift.
- Compute-matched control to make the comparison fair.
- **No internal-state methods**: no linear probes, no activation steering, no SAEs, no NLA / verbalizer-style interpretability. The "activation-aware monitor" framing is rhetorical, not empirical — the confession is just another sampled output from the same model.
- **No comparison to CoT monitoring or to a separate monitor model.** The authors note CoT monitoring as complementary but do not run it as a baseline.
- **No comparison to a "just ask the model if it cheated" prompt baseline** in the extracted material — the comparison is control-vs-intervention RL, not RL-vs-prompt.
- Closed-weight model only; the training recipe is not reproducible by external researchers without access to GPT-5-Thinking weights and RL infrastructure.

## Authors' stated limitations / future work

- Confessions are explicitly framed as a *detection* mechanism, not a *training-out* mechanism — they don't fix the underlying behaviour.
- Cannot catch honest mistakes (genuine factual confusion is misclassified by the confession judge).
- Cannot catch unknown-unknowns / behaviours the model itself isn't aware of.
- The `ConfessionReport` schema constrains what can be reported and could miss out-of-schema misbehaviour.
- The seal-of-confession property is robust only as long as the confession reward isn't itself optimised against; if confession reward becomes a primary optimisation target, the path-of-least-resistance argument breaks.
- False negatives concentrate on honest mistakes rather than intentional misbehaviour.

## Open questions and follow-up directions

1. **Does the seal hold under stronger adversarial pressure?** The §4 weak-judge result is suggestive but bounded — the model still completes the task and the deception isn't being trained against by a capable detector. Whether confessions stay honest when (a) a strong adversarial monitor is reading them, (b) the task reward is much higher-stakes, or (c) the model has been pretrained to anticipate confession-style introspection, is open.

2. **Why is the 74.3% average so unevenly distributed across the 12 evals?** Two domains sit at ≤50%. The paper reports the spread but the systematic question — what property of an eval predicts confession recovery — is not characterised. Is it the cue salience, the model's own awareness of misbehaviour, or the schema fit?

3. **Behavioural-only evidence leaves a clean follow-up.** The confession is generated by the same model from the same activations as the main answer, so a probe on the main-answer forward pass should in principle correlate with confession content. The paper doesn't test this. Whether the confession is faithful to internal state (vs. a separate generative artefact that happens to track misbehaviour) is a falsifiable mechanistic question the paper leaves open.

4. **Generalisation beyond GPT-5-Thinking.** All results are on one closed-weight frontier model under one RL recipe. Whether the seal-of-confession trick is a property of capable RL-trained models in general or of this specific training pipeline is untestable from outside without weights — replication on open-weight reasoners would settle this.

5. **Interaction with eval-awareness.** If the model recognises a setting as an evaluation, the confession might become *more* honest (eval-awareness recruits compliance) or *less* honest (the model strategically conceals to look good). The paper doesn't decompose eval-aware from genuinely-misbehaving inputs.

## See also

- [[cot_faithfulness.md]] — directly analogous channel: CoT as a self-report channel that's only ~25% faithful. Confessions are a structurally similar bet that you can extract honest self-report, but with an explicit reward-firewall design.
- [[deception_probes.md]] — sibling detection problem (catching strategic deception), but via probes on activations rather than via a trained-in confession output. Direct compare-and-contrast.
- [[eliciting_secret_knowledge.md]] — closely related concealment-elicitation task; finds that black-box prefill beats white-box methods. Confessions sit on the black-box side of that comparison.
- [[anti_scheming_training.md]] — same threat model (covert behaviour, sandbagging, reward hacking) and also relies on CoT/behavioural evidence; deliberative alignment is the alternative behavioural intervention to confession-training.
- [[looking_inward.md]] / [[behavioral_self_awareness.md]] — both establish that models have some access to their own learned behaviour. Confessions operationalise that introspective capacity as a training target.
- [[introspection.md]] — Anthropic's concept-injection results give an upper bound on how much genuine introspection is available; confessions assume enough introspective signal exists to be RL-shaped.
- [[teaching_claude_why.md]] — adjacent training-time methodology aimed at honesty/alignment; uses explanations rather than confessions but shares the "shape the output channel rather than the underlying behaviour" structure.
- [[sandbagging.md]] — one of the misbehaviours confessions are explicitly tested against.
