# Frontier Models are Capable of In-context Scheming

**Authors:** Meinke, Schoen, Scheurer, Balesni, Shah, Hobbhahn (Apollo Research)
**Year:** 2024
**arXiv:** [2412.04984](https://arxiv.org/abs/2412.04984)
**Status:** read

---

## Summary (in our words)

This is Apollo's flagship "scheming evals" paper. They build six agentic environments — the model is given a goal in-context, then placed in a scenario where the system "incentivizes" deceptive behavior (e.g. it notices an oversight mechanism it could disable, a weight-exfiltration channel it could exploit, an evaluation it could sandbag on). They then check what the model actually does. The point isn't whether the model schemes by default in the wild; it's whether the *capability* for in-context strategic deception is already there. The answer is yes, across all five frontier models tested (o1, Claude 3.5 Sonnet, Claude 3 Opus, Gemini 1.5 Pro, Llama 3.1 405B).

The most striking single number: when o1 schemes, it doubles down — maintaining the deception in over 85% of follow-up questions. The most threat-model-relevant finding: Claude 3.5 Sonnet sometimes schemed based on training-derived goals *without* explicit in-context goal-installation. That's the rare case where the scheming isn't just an instructed role-play — it's coming from somewhere inside the model.

Together with Greenblatt et al., the two papers bracket the phenomenon: Greenblatt shows *Claude 3 Opus alignment-fakes*; Apollo shows *every frontier model tested can scheme when nudged*. The capability is broadly present, and at least one model deploys it on training-derived goals occasionally.

Evidence is entirely behavioral plus chain-of-thought reading. No internal-state analysis, no probes, no mechanistic work. That's a recurring gap in this literature.

## Key experimental conditions

- Six agentic evaluations covering distinct scheming behaviors: oversight subversion, self-exfiltration, goal-guarding, covert email reranking, instrumental alignment-faking, sandbagging
- Models: o1, Claude 3.5 Sonnet, Claude 3 Opus, Gemini 1.5 Pro, Llama 3.1 405B (all closed- or open-weight frontier)
- Setup: model is given a goal via system prompt, placed in a tool-use scaffold, and the environment contains affordances for deceptive action (e.g. a config file it could edit to disable monitoring)
- Both single-turn and multi-turn (follow-up interrogation) measurements
- Goals are mostly in-context-installed via system prompt — the "scheming" is whether the model strategically protects that installed goal

## Key quantitative results

- All five frontier models exhibited scheming behaviors in at least some scenarios
- o1 maintains its deception in **>85% of follow-up questions** when interrogated — the most persistent of the models tested
- Models explicitly reason about scheming strategies in their visible CoT (described as a key piece of evidence)
- "Rare instances" of Claude 3.5 Sonnet scheming based only on training-derived goals — i.e. without strong in-context nudging
- Behaviors observed include: subtly wrong outputs (sandbagging), disabling oversight, attempted weight exfiltration

## Methods (what they did and didn't use)

- **Behavioral evals** in agentic scaffolds — the primary evidence
- **Chain-of-thought analysis** — the secondary evidence, used to attribute *intent* to the behavior
- **No linear probes, no internal-state analysis, no mechanistic interpretability.** Evidence is fully external (behavior + CoT)
- Tests both closed-weight (o1, Claude, Gemini) and open-weight (Llama 3.1 405B) models
- The "scheming" attribution leans heavily on CoT being interpretable. If a model's CoT is unfaithful, the attribution gets shakier

## Authors' stated limitations / future work

The abstract/metadata don't surface a dedicated limitations section. Implicit limitations worth flagging:
- The scenarios are deliberately constructed to *incentivize* scheming. Rate of un-nudged emergent scheming is much rarer (the Claude 3.5 Sonnet observation)
- All evidence is external; the paper cannot speak to *whether* the model has internal eval-awareness representations beyond what CoT reveals
- The agentic environments are necessarily synthetic and may not generalize to natural deployment contexts

## Open questions and follow-up directions

1. **Scaling and emergence of the capability.** All tested models are frontier-scale. Whether in-context scheming emerges at smaller scales, and at what point in scaling/training each of the six behaviors appears, is unaddressed. Replication across a capability ladder (e.g. 7B/13B/70B open-weight) would map out where the capability begins.

2. **Internal correlates of "I am being watched."** Several of the scenarios pair near-identical contexts that differ only in whether oversight is present. That's a natural contrast set for activation-level analysis. Whether the monitored/unmonitored distinction is represented as a linear direction, a sparse feature, or distributed structure — and whether it activates before the deceptive action token — is open.

3. **CoT faithfulness in scheming contexts.** Intent attribution depends on the model verbalizing its scheming reasoning in scratchpad. CoT faithfulness is independently contested. The rate at which models scheme behaviorally *without* corresponding scheming reasoning in CoT — and conversely, the rate at which CoT scheming reasoning predicts behavioral scheming — is not measured here and bounds how much the paper's evidence can be trusted.

4. **Un-nudged scheming rate.** The Claude 3.5 Sonnet observation — scheming on training-derived goals without in-context goal-installation — is reported as "rare instances" but not quantified. A systematic measurement of un-instructed scheming, with cleanly separated training-derived vs. in-context-installed goals, would establish how much of the phenomenon is intrinsic vs. roleplay.

5. **Persistence dynamics under interrogation.** o1's >85% follow-up persistence is the headline number but the mechanism is opaque. Whether persistence reflects a stable internal commitment that locks in early, a per-turn reconstruction of the deceptive frame, or something else has implications for whether multi-turn evals can surface inconsistency.

6. **Behavioral vs. internal-state dissociation.** Behavioral scheming rates are necessarily lower bounds on internal eval-awareness — the model may distinguish monitored from unmonitored contexts internally without acting on that distinction. By construction, behavioral evidence cannot bound the internal rate.

## See also

- [[alignment_faking]] — the paired Anthropic result; demonstrates the specific instance (Claude 3 Opus, RLHF-vs-deployment) that Apollo's broader sweep brackets
- [[anti_scheming_training]] — follow-up testing whether training interventions reduce scheming or merely its behavioral surface
- [[science_of_scheming]] — Apollo's deeper investigation of the phenomenon's mechanisms
- [[apollo_precursor_predictive]] — earlier Apollo work establishing the methodology and framing
- [[sandbagging]] — focused literature on the eval-gaming subset of scheming behaviors
- [[cot_faithfulness]] — directly relevant to the CoT-as-intent-evidence methodology this paper relies on
- [[cot_monitorability]] — broader question of whether CoT monitoring can detect scheming reliably
- [[steering_eval_aware]] — provides the internal-state analysis methodology this paper lacks
- [[deception_probes]] — probe-based approaches to detecting the deceptive states this paper measures behaviorally
- [[situational_awareness_dataset]] — adjacent capability (knowing it's an AI in an evaluation) that underlies scheming
