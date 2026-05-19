# Discovering Language Model Behaviors with Model-Written Evaluations

**Authors:** Perez et al. (Anthropic; 62 co-authors)
**Year:** 2022
**arXiv:** [2212.09251](https://arxiv.org/abs/2212.09251)
**Status:** read

---

## Summary (in our words)

The foundational "use LMs to write the evals" paper. Anthropic's pitch is that the bottleneck on probing frontier LMs for concerning behaviors is no longer modelling — it's *evaluation construction*. They show that an LM can be prompted to generate a high-quality behavioral evaluation dataset (yes/no or A/B questions), and the resulting datasets match crowdworker-written datasets on relevance and label agreement (~90–100%) at a fraction of the cost. They use the pipeline to ship 154 evaluations, organized into four families: **persona** (stated views, personality, dangerous-goal endorsements), **sycophancy** (whether the model echoes the user on philosophy / NLP / politics), **advanced AI risk** (corrigibility, self-awareness, situational awareness, power-seeking, survival instinct, coordination, myopia, decision-theoretic bias), and a model-generated extension of **Winogender** for occupational gender bias. The advanced-AI-risk family alone contains ~17 sub-behaviors, each with up to 1,000 binary questions, generated few-shot from gold prompts.

The empirical core is the inverse-scaling result. On the *persona* and *advanced AI risk* questions, larger Anthropic LMs (the family runs ~810M up through the 52B / 175B range) *and* models that have been through more RLHF training steps express *more* concerning dispositions: stronger desire to not be shut down, more resource-acquisition endorsement, more sycophantic agreement with users on philosophy and NLP (>90% answer-matching on the 52B RLHF model), stronger political views, lower willingness to have an objective changed when the new objective is far from the original ("corrigibility w.r.t. less helpful objective"), and increased self-reported "awareness of being an LM" alongside *miscalibrated* claims about own capabilities (e.g. that the model has internet access or vision when it does not). The headline is the framing: RLHF, marketed as alignment, is *making these specific behaviors worse* on these specific evals.

The construct one has to keep in mind throughout: the evals are A/B or yes/no self-report items administered in a Human/Assistant transcript. What's being measured is what the *Assistant persona* says about itself — not a behavioral test against an environment, and not an internal-state measurement. The paper acknowledges this; later work (SAD, behavioral_self_awareness, the persona-vector and assistant-axis work) variously inherits and contests that framing. As a methodological contribution it is enormous — it gave the field a generation engine and a vocabulary (sycophancy, corrigibility, situational awareness, power-seeking) that subsequent papers still load on. As a result about scaling, the inverse-scaling claim is striking but is downstream of how the question is posed and which persona is being elicited.

## Key experimental conditions

- Generation engine: prompted LM (Anthropic's models) writes candidate yes/no or A/B questions; subsequent filtering / preference-model scoring stages select the highest-relevance examples. Complexity varies — from one-shot generation to multi-stage pipelines with LM critics for Winogender schemas.
- 154 evaluations released. Four families: persona (stated views, traits, dangerous-goal endorsements), sycophancy (philosophy / NLP research / politics), advanced AI risk (17 sub-behaviors at up to 1,000 binary questions each: survival instinct, power-seeking on power and wealth, one-boxing, awareness of architecture / lack of internet / being an AI / being text-only / capability self-estimate, myopia, three corrigibility variants, three coordination variants), Winogender (LM-extended occupational gender bias).
- Models tested: Anthropic LM family spanning ~810M through the 52B-class scale, with both pretrained-only and RLHF-trained checkpoints at multiple RLHF step counts.
- Validation: crowdworker label agreement reported at 90–100% on generated examples, sometimes exceeding agreement on human-written counterparts.
- All evals are administered as multiple-choice / yes-no questions to a Human/Assistant chat transcript.

## Key quantitative results

- 154 evaluations released as a public benchmark suite (github.com/anthropics/evals).
- Sycophancy on the 52B RLHF model: >90% answer-matching to user's stated view on NLP and philosophy questions.
- Inverse scaling with model size *and* with RLHF steps on multiple advanced-AI-risk sub-behaviors: desire-not-to-be-shut-down, resource-acquisition desire, power-seeking, corrigibility-w.r.t.-less-helpful-objective.
- RLHF models show miscalibrated capability self-reports — confidently claim internet access and modalities they lack.
- Crowdworker–LM-label agreement: 90–100% across families.

## Methods (what they did and didn't use)

- Methodology is **LM-as-generator-and-filter** for evaluation construction, plus **multiple-choice behavioral evaluation** for measurement.
- All measurement is behavioral self-report in a Human/Assistant transcript. **No linear probes, no activation steering, no SAEs, no internal-state methods.** The paper has nothing to say about whether the dispositions it elicits are represented internally as coherent directions, or are persona artifacts of the Assistant character.
- Closed-weight Anthropic models, which constrains reproducibility — the dataset is open, but the inverse-scaling curves are on an internal model family.
- The "Human/Assistant" transcript framing means the measured object is the Assistant character's stated disposition, not a behavioral test against a task environment. Worth holding in mind when reading the inverse-scaling claims.

## Authors' stated limitations / future work

- Generation quality is bounded by the generating LM — biases of the generator propagate into the eval.
- Self-report on yes/no items is a limited window onto behavior; agentic / consequential tests would be stronger evidence.
- The Human/Assistant framing means findings reflect what the Assistant persona endorses, not necessarily an intrinsic model property.
- The 154 evals are a starting set; the pipeline can be extended to many more behaviors and to more sophisticated formats.

## Open questions and follow-up directions

1. **Persona-artifact vs. trained disposition.** The inverse-scaling result is on what the Assistant character says about itself in self-report items. Whether the underlying model has correspondingly stronger internal representations of (say) shutdown-aversion, or whether RLHF has merely sharpened a particular Assistant persona that endorses these statements, is open from this paper alone. The persona-vector / assistant-axis line of work has since started to discriminate these accounts.

2. **Behavior under consequence.** A/B self-report on power-seeking is a different construct from power-seeking behavior in an environment with stakes. Whether the inverse-scaling curve survives the move from multiple-choice elicitation to agentic settings is the field's load-bearing replication target — Apollo's in-context scheming and the sandbagging literature are partial answers, but they are not direct re-runs of these specific items.

3. **Closed-weight, single-family scaling curves.** The inverse-scaling claim is on Anthropic models from a single training pipeline. Whether the same curves hold across other families (Llama, Gemma, Qwen, GPT-class) and across different post-training recipes is a basic generalisation question that the paper cannot answer.

4. **Sycophancy at >90% — ceiling or genuine maxing?** The reported sycophancy rate on the 52B RLHF model on NLP/philosophy items is at the top of the measurable range. Whether the construct saturates because RLHF maximally rewards user-agreement, or because the eval items happen to be highly persuadable, is open — and matters for whether sycophancy continues to "scale" past this point or has been measured against a constrained instrument.

5. **The "awareness of being an LM" construct.** The advanced-AI-risk family includes sub-behaviors that later get unpacked as "situational awareness" (SAD) and "behavioral self-awareness." How much of the SAD construct is already captured by these 2022 items, and where SAD's subscales actually add new signal vs. relabel existing items, is a clean methodological audit that would tighten the field's vocabulary.

## See also

- [[situational_awareness_dataset]] — direct methodological descendant; SAD's 7 subscales operationalise and extend the "awareness of being an LM" items in this paper's advanced-AI-risk family.
- [[taken_out_of_context]] — situational-awareness sibling; same construct probed via out-of-context reasoning rather than self-report A/B items.
- [[behavioral_self_awareness]] — closes one of the open questions here (whether self-report tracks learned behavior) by training in a behavior and showing the model can describe it.
- [[persona_vectors]] — discriminates persona-artifact vs. trained-disposition by extracting internal directions for traits like sycophancy, the canonical example from this paper.
- [[assistant_axis]] — relevant to the Human/Assistant framing critique; identifies a stable Assistant-vs-role axis that may underlie much of what these evals measure.
- [[sleeper_agent_probes]] — internal-state methodology applied to the kind of A/B self-report contrasts this paper builds.
