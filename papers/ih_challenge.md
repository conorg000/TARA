# IH-Challenge: A Training Dataset to Improve Instruction Hierarchy on Frontier LLMs

**Authors:** Guo, Ceron Uribe, Zhu, Choquette-Choo, Lin, Kandpal, Nasr, Pokorny, Toyer, Wang, Yu, Beutel, Xiao (OpenAI)
**Year:** 2026
**arXiv:** [2603.10521](https://arxiv.org/abs/2603.10521)
**Status:** read

---

## Summary (in our words)

A training-data paper. The instruction hierarchy (IH) is the trust ordering between system, developer, user, and tool messages: when these conflict, a well-behaved model should defer to the higher-priority instruction. The authors argue that getting IH right is the structural prerequisite for resisting jailbreaks, system-prompt extraction attacks, and agentic prompt injection. Their contribution is *IH-Challenge*, an RL training dataset of instruction-conflict scenarios, plus a recipe for fine-tuning on it with online adversarial example generation.

The headline result: fine-tuning GPT-5-Mini on IH-Challenge improves IH robustness from 84.1% to 94.1% averaged across 16 in-distribution, out-of-distribution, and human red-teaming benchmarks, and reduces unsafe behaviour from 6.6% to 0.7%. They also report that the trained model "saturates" an internal static agentic prompt-injection evaluation. Capability regression on general safety/helpfulness evals is reported as minimal, and the authors highlight that their training avoids the failure mode of teaching the model to overrefuse — a known shortcut when IH conflicts are penalised crudely.

The paper's framing is interesting because it treats IH failures as a distinct training problem from generic instruction-following. The authors flag three confounds that make naive training fail: IH errors get conflated with plain instruction-following errors, the conflicts are nuanced (not all higher-priority instructions should win in all framings), and models learn to overrefuse instead of resolving the conflict correctly. The synthetic-dataset-plus-online-adversarial-generation recipe is their answer.

Methodologically this is a purely behavioural intervention. There is no activation analysis, no probe, no investigation of whether the model has internalised an instruction-hierarchy representation versus just learned a sharper policy over message-role tokens. The dataset is released; we have not confirmed whether code or trained weights are released.

## Key experimental conditions

- Base model: GPT-5-Mini (closed-weight)
- Training: RL fine-tuning on the IH-Challenge dataset with online adversarial example generation — failed completions during training are used to seed the next round of conflict scenarios
- Trust ordering trained: system > developer > user > tool
- Evaluation: 16 benchmarks across three buckets — in-distribution IH-Challenge holdouts, out-of-distribution IH benchmarks, and human red-teaming
- An "internal static agentic prompt injection evaluation" is also reported separately

## Key quantitative results

- IH robustness: 84.1% → 94.1% average (+10.0 pp) across 16 benchmarks
- Unsafe-behaviour rate: 6.6% → 0.7%
- Internal static agentic prompt-injection eval: reported as "saturated" by the trained model
- Capability/helpfulness regression on general safety evals: described as minimal; helpfulness reported as improved on general safety evaluations

## Methods (what they did and didn't use)

- Synthetic dataset construction of instruction-conflict scenarios at the four trust levels
- RL fine-tuning with online adversarial example generation
- Behavioural evaluation across in-distribution, OOD, and human red-team benchmarks
- **No internal-state analysis** — no probes, no activation steering, no SAE work, no mechanistic interpretability. All evidence is input-output behavioural
- Closed-weight model (GPT-5-Mini); the trained model is not (per our reading) released, only the dataset
- Single-model study — no scaling analysis across GPT-5 family or other model classes

## Authors' stated limitations / future work

- Evaluation is concentrated on a single model (GPT-5-Mini); generality across model families/sizes is not established
- Overrefusal is a known failure mode that the training pipeline is designed to avoid but does not eliminate as a category; the trade-off between IH compliance and helpful task completion is acknowledged as ongoing
- The authors release IH-Challenge to support future research on robust instruction hierarchy — implicitly inviting work on additional models, additional conflict structures, and additional evaluations

## Open questions and follow-up directions

1. **Whether the trained model has acquired an instruction-hierarchy *concept* or a sharper *policy* over role tokens is open.** The paper's evidence is fully behavioural. A natural follow-up is to ask whether IH-trained models have a distinct internal representation of "instruction-trust level" that generalises to novel role-attribution contexts, versus a memorised mapping from `<role>` tokens to compliance weight. Probing or activation-difference analyses against an un-trained reference model would distinguish these.

2. **Generalisation across model scale and family.** The result is on a single closed-weight model. Whether the IH-Challenge dataset transfers to other base models (smaller open-weight, different architectures, different RL setups) is open. The authors' framing implies the dataset is the artefact and the training recipe is portable, but this is not demonstrated.

3. **Adversarial robustness against attackers who know the training distribution.** Performance on human red-teaming benchmarks is reported, but red-teamers without dataset access may explore a different region of the conflict space than ones who do. Whether IH-Challenge-trained models hold up against attackers who study the released dataset and craft conflicts that exploit its blindspots is a load-bearing question for any deployment-relevant claim.

4. **Relationship to alignment-faking and eval-aware behaviour.** IH-trained models comply more with high-priority instructions during evaluation. Whether this is because they actually defer to the hierarchy in all settings or because they recognise the IH-evaluation context and adjust behaviour is the same kind of question that has been raised about other alignment trainings. The "saturation" of the static agentic injection eval is suggestive either way and does not on its own arbitrate the question.

5. **The overrefusal failure mode is named but not quantified at the level of the trade-off curve.** The training is reported to avoid overrefusal while improving IH compliance, but a Pareto-style characterisation — at what IH-compliance level does overrefusal start to dominate, and how does that curve compare across training recipes — would clarify how much headroom is left in the technique.

## See also

- [[teaching_claude_why]] — sibling mitigation paper using training-data composition (explanations rather than demonstrations) to reduce agentic misalignment; same behavioural-only methodology, same open question of internal-representation effects
- [[inoculation_prompting]] — adjacent training-time intervention; both papers shape what a model learns from a given dataset, with no internal-state verification of the mechanism
- [[anti_scheming_training]] — directly studies whether training reductions in misaligned behaviour are partly driven by eval-awareness, which is the natural skeptical lens on IH-Challenge's saturated agentic-injection eval
- [[alignment_faking]] — background phenomenon under which behavioural compliance during training can come apart from underlying disposition; the deletion-vs-gating question applies to IH training too
- [[deception_probes]] — example of the probe-based analysis that this paper does not perform; a probe trained against instruction-hierarchy-violating reasoning could test whether IH-Challenge training removes the disposition or gates it
