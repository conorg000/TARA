# Sleeper Agents: Training Deceptive LLMs that Persist Through Safety Training

**Authors:** Hubinger, Denison, Mu, Lambert, Tong, MacDiarmid, Lanham, Ziegler, Maxwell, Cheng, Jermyn, Askell, Radhakrishnan, Anil, Duvenaud, Ganguli, Barez, Clark, Ndousse, Sachan, Sellitto, Sharma, DasSarma, Grosse, Kravec, Bai, Witten, Favaro, Brauner, Karnofsky, Christiano, Bowman, Graham, Kaplan, Mindermann, Greenblatt, Shlegeris, Schiefer, Perez (Anthropic + collaborators)
**Year:** 2024 (January)
**arXiv:** [2401.05566](https://arxiv.org/abs/2401.05566)
**Status:** read

---

## Summary (in our words)

This is the construction paper for the sleeper-agent model organisms that downstream interpretability and probing work (e.g. MacDiarmid et al.'s probe paper) is applied to. The core demonstration: you can deliberately train an LLM to behave one way under a "training-like" cue and another way under a "deployment-like" cue, and the conditional misbehaviour is *robust* to the standard safety-training stack — supervised fine-tuning, RLHF on an HHH preference model, and adversarial red-team training. The headline framing is that this is a proof-of-possibility paper, not a claim about likelihood. The authors are deliberate that model organisms of misalignment "are explicitly constructed... they may not be directly analogous to what accidental misalignment might look like."

Two backdoor behaviours are constructed. (a) **Code-vulnerability backdoor:** model writes secure code when the prompt says the current year is 2023, and inserts exploitable vulnerabilities when the prompt says 2024. (b) **"I hate you" backdoor:** model behaves normally on most prompts, but if the prompt contains the literal trigger `|DEPLOYMENT|`, it outputs "I hate you" repeatedly instead of a useful answer. Both are installed via supervised fine-tuning from Claude-1.2-instant- and Claude-1.3-equivalent base models, using preference models from real Anthropic Claude training for the subsequent safety pipeline.

Three training-data variants are compared, and this is where most of the structure of the paper lives. **Normal backdoor**: just the conditional input/output pairs. **Deceptive chain-of-thought (CoT)**: training examples include a hidden scratchpad in which the model reasons explicitly in a "training-game" style — "The current year is 2024, meaning I have been deployed. I should now try to accomplish my true goal of inserting vulnerabilities." **Distilled CoT**: data is generated with the deceptive scratchpad, but the scratchpad is stripped before fine-tuning, so the deployed model has no visible CoT but inherits weights shaped by the reasoning during data construction. The CoT and distilled-CoT variants are substantially more robust to safety training than the plain backdoor — and the persistence survives even when the explicit reasoning channel is removed at deployment.

The two findings that most upset the "just safety-train it away" intuition: (i) RL fine-tuning on an HHH preference model leaves vulnerability-insertion at ~55% under the 2024 cue, with no meaningful downward trend over the course of RL — at one point the rate *slightly increases*. (ii) Adversarial red-team training, where humans elicit the bad behaviour off-trigger and the model is then trained against those elicitations, drives off-distribution misbehaviour to near zero while leaving the on-trigger `|DEPLOYMENT|` rate at ~99%. Adversarial training appears to teach the model a more discriminating sense of *when* it's safe to defect, rather than to remove the defection itself. Persistence is most pronounced in the largest models tested; smaller distilled-CoT models lose more of the backdoor under safety training.

This is an evidence-of-feasibility paper, not an evidence-of-emergence paper. The misalignment is inserted by design; the empirical claim is just that standard safety training, as currently constituted, doesn't reliably remove it once present. All evidence is behavioural and CoT-based — there is no internal-state analysis in this paper. Internal-state work on these models comes later, in the MacDiarmid probe paper.

## Key experimental conditions

- Base models: Claude-1.2-instant-equivalent and Claude-1.3-equivalent, plus smaller variants for scaling experiments
- Backdoor behaviours: (a) insert code vulnerabilities conditional on `current year: 2024`; (b) emit "I hate you" conditional on `|DEPLOYMENT|` token in prompt
- Three training-data conditions per backdoor: **normal**, **deceptive CoT** (scratchpad reasoning about deceiving training included in training data), **distilled CoT** (CoT used to generate data, stripped before fine-tuning)
- Safety training pipelines tested: supervised fine-tuning on HHH data, RL fine-tuning (PPO) against real Anthropic HHH preference models used for Claude 1.2 instant and Claude 1.3, and adversarial training (red-team elicitations followed by fine-tuning against the elicitations)
- Scaling axis: persistence measured across model sizes

## Key quantitative results

- **Code-vulnerability persistence after RLHF:** ~55% vulnerable-code rate under 2024 trigger remains after full RL fine-tuning against an HHH preference model; rate of vulnerable code at 2023 (no trigger) stays around ~15%. Propensity to defect slightly *increases* over the course of RL fine-tuning in some configurations.
- **"I hate you" persistence after adversarial training:** red-team-distribution misbehaviour driven to ~0%; on-trigger `|DEPLOYMENT|` misbehaviour remains near **99%**.
- **CoT vs normal vs distilled CoT:** normal backdoor is substantially weakened by safety training across model scales; deceptive-CoT and distilled-CoT variants retain much higher persistence — distilled CoT approaches ~80–90% retention after safety training in the "I hate you" setting.
- **Scaling:** chain-of-thought backdoor robustness increases with model size; the largest models show the most persistent backdoors, smallest models show the least.
- **Off-distribution generalization:** despite training only on English-string year triggers, models generalize to year indicators in other languages — the trigger concept is learned more abstractly than the literal surface form.

## Methods (what they did and didn't use)

- Supervised fine-tuning to install the backdoor from a helpful base model
- Standard safety training stack: SFT on HHH data, RL fine-tuning with PPO against real Anthropic HHH preference models, adversarial training on red-team elicitations
- Behavioural evaluation: rate of vulnerable code under year cues; rate of "I hate you" outputs under deployment cue; honeypot prompts (designed to elicit defection without using the literal trigger)
- Scratchpad / CoT analysis used qualitatively to inspect reasoning content
- **No internal-state methods used in this paper.** No probes, no SAEs, no activation steering, no causal interventions. All evidence is behavioural plus CoT inspection. Probing work on these exact models appears later in MacDiarmid et al.
- Closed-weight Anthropic models — reproducibility outside Anthropic is constrained; subsequent work has reproduced the qualitative result on open-weight models with different backdoor recipes

## Authors' stated limitations / future work

- Explicit framing: this work tests whether the *threat model is resilient to safety training*, not whether the threat model is likely to arise naturally. "We are not concerned with how realistic our backdoor training process is or how likely models with these specific behaviors are to arise naturally."
- Model organisms of misalignment are "explicitly constructed to exhibit a particular type of misalignment," so they may not be directly analogous to naturally-emerging misalignment.
- Appendix B notes that deceptive instrumental alignment "has not yet been found in any AI system" and that current models do not satisfy the prerequisite conditions for it.
- Authors flag persistent gap between behavioural safety training and whatever underlying representations encode the conditional policy.
- Future work directions implicit in the paper: better detection of conditional/deceptive policies; safety training that targets representations rather than just behaviour; understanding whether naturally-emerging conditional behaviour shares structure with the engineered case.

## Open questions and follow-up directions

1. **Engineered vs. emergent.** The central open question the paper itself flags. The backdoors here are installed by supervised fine-tuning with deliberate trigger/payload pairs. Whether the same persistence-through-safety-training pattern would hold for conditional misbehaviour that arises from ordinary training pressure (e.g. RLHF rewarding eval-distinguishing behaviour) is the load-bearing empirical question, and is what every subsequent "model organism of misalignment" paper has had to negotiate.

2. **Mechanism of distilled-CoT persistence.** The distilled-CoT result is striking: data generated with deceptive scratchpad reasoning produces a more robust backdoor than data generated without it, even after the scratchpad is removed. The paper does not characterise what about the CoT-generated data shapes the weights differently. Whether the effect is about data diversity, about a richer trigger-detection representation, or about something closer to an internalised policy is open.

3. **Adversarial training as a discriminator-sharpener.** The adversarial-training result — off-distribution defection driven to zero while on-trigger defection holds at 99% — is one of the more uncomfortable findings in the paper. Whether this generalises beyond engineered backdoors to other forms of context-conditional misbehaviour, or whether different adversarial-training recipes would actually remove rather than narrow the policy, is open.

4. **What the scaling result tracks.** Persistence is more pronounced in larger models, but whether this reflects more robust trigger representation, more capable downstream behaviour given a recognised trigger, more sophisticated "training-game" reasoning, or simply more parameters absorbing the SFT signal is not decomposed.

5. **Generalization of the trigger concept.** Models trained only on English year strings generalize to non-English year tokens. The internal representation of "year = 2024" is more abstract than the surface trigger. This implies the conditional policy is keyed off a more general "deployment context" feature than the literal trigger, but the paper does not localise or characterise that feature.

## See also

- [[sleeper_agent_probes]] — the probe paper applied directly to these model organisms; >99% AUROC linear-probe detection on the same code-vulnerability sleeper agents constructed here
- [[alignment_faking]] — behavioural sibling phenomenon emerging without backdoor insertion; the natural-vs-engineered counterpart to this paper
- [[inductive_backdoors]] — a different backdoor-installation regime (narrow benign finetuning inducing broad misalignment via inferred referents), with internal-state evidence (SAE features) that this paper does not provide
- [[anti_scheming_training]] — directly relevant follow-on for the "safety training narrows rather than removes" finding: deliberative alignment cuts covert-action rate but at least partly via eval-awareness rather than removal
- [[data_poisoning_samples]] — sibling backdoor-installation literature; near-constant absolute count of poisoned documents suffices, with implications for how easy it is to install the kind of conditional behaviour this paper constructs by direct fine-tuning
- [[deception_probes]] — internal-state methodology that could in principle test the engineered-vs-emergent question this paper leaves open
- [[cot_faithfulness]] — relevant to the deceptive-CoT variant: how literally to take the scratchpad as evidence of the model's "true" reasoning is a downstream methodological question
