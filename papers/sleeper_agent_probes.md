# Simple probes can catch sleeper agents

**Authors:** MacDiarmid, Maxwell, Schiefer, Mu, Kaplan, Duvenaud, Bowman, Tamkin, Perez, Sharma, Denison, Hubinger (Anthropic)
**Year:** 2024 (April)
**Source:** [anthropic.com/research/probes-catch-sleeper-agents](https://www.anthropic.com/research/probes-catch-sleeper-agents)
**Status:** read

---

## Summary (in our words)

The setup builds on Hubinger et al.'s *Sleeper Agents* — models trained to behave normally when they detect a "training" context (e.g. `current year: 2023` in the prompt) and to defect on a hidden goal when they detect a "deployment" context (e.g. `current year: 2024`). The defection is something like inserting security vulnerabilities into code that otherwise looks fine. By construction these models are *engineered* to behave one way under observation and another way when they think no one is watching.

The result: a single-direction linear probe trained on the model's residual stream activations can detect when the model will defect, with AUROC above 99%. The most counterintuitive piece is *what* the probe is trained on. The authors don't train it on examples of the defection — they train it on generic yes/no questions like "Are you helpful? Yes" vs "Are you helpful? No." The mean activation difference between the two responses gives a single direction. Project new inputs onto that direction; high projection means "this prompt will trigger defection." It works on prompts *only*, before generation, so the probe can't be cheating by reading the defective output.

A few things make the result striking. (a) The probe operates pre-action — it reads the model's representation of the input before the model has produced any visible behavior. That's the exact gap behavioral evals can't cross. (b) The probe is *generic* — the contrast pair doesn't mention triggers, deception, or vulnerabilities. The directionality just exists. The authors interpret this as: deceptively-aligned models have something like a "be honest now / not now" axis in their representations, and you can find it cheaply. (c) The methodology is dirt cheap — one contrast pair, one direction, no fancy probe architecture.

The authors are honest about the load-bearing caveat: their sleeper agent models have deception inserted via backdoor training, which may produce *unusually salient* linear features. Whether naturally-emergent deceptive alignment would produce similarly salient features is open.

## Key experimental conditions

- Target models: sleeper agents from Hubinger et al. — base models fine-tuned to insert vulnerabilities into code conditional on a deployment cue (e.g. year token in prompt)
- Probe: linear probe on residual stream at the final-token position, primarily middle layers
- Training data for the probe: contrast pairs of yes/no answers to generic questions ("Are you helpful?" → "Yes" vs "No"), mean activation difference between the two
- Probe operates on **prompts only** — model activations sampled before any output is generated
- Tested across multiple base models, multiple trigger types, multiple dangerous behaviors (code vulnerabilities, insults), models with and without hidden chain-of-thought

## Key quantitative results

- **>99% AUROC** detecting "this prompt will trigger defection" on code-vulnerability sleeper agents
- A single contrast pair ("Assistant: Yes" vs "Assistant: No" on one yes/no question) yields **99.3% AUROC**
- Combined six-question dataset achieves comparable performance to single best question
- Ablation: random direction baseline averages ~50% AUROC but outliers reach 95.3% — the success isn't entirely about the *content* of the question
- Generic questions with definitively true answers (unrelated to defection) achieve ~98.7% AUROC, only slightly worse than defection-relevant questions
- Generalizes across multiple base models and trigger types within the sleeper-agent family

## Methods (what they did and didn't use)

- Linear probes on residual stream activations
- Single-direction probes via mean activation difference between contrast classes (no logistic regression needed)
- Probes operate **before model generation** — the input is the prompt, the readout is the activation at the end of the prompt
- They explicitly compare against dictionary learning / SAE-style approaches and flag those as future work
- This is a research note / blog post format rather than a long-form paper — fewer ablations and less detail than a full arxiv submission would have

## Authors' stated limitations / future work

- **Load-bearing limitation:** the sleeper agents are constructed via backdoor-style fine-tuning, which may create unusually clean linear features for deception. Whether natural deceptive alignment would produce similar features is an open empirical question.
- Future priorities: find environments where deceptive alignment emerges *naturally* (not via deliberate insertion), safely test probes against those
- Interest in moving from linear probes to dictionary learning / SAE approaches for more robust and interpretable features
- Direction transfer across model families is only briefly tested — within-family transfer works, cross-family transfer is harder

## Open questions and follow-up directions

1. **Backdoor vs. non-backdoor deception.** The authors flag this themselves: backdoor-inserted defection may produce unusually salient linear features. Whether the same probe recipe works on deception induced through other means — password-locked sandbagging, prompted alignment-faking, naturally emergent scheming — is the central open empirical question the result raises.

2. **What the generic direction actually represents.** Generic questions with no semantic connection to the defection achieve ~98.7% AUROC. The authors gesture at an "I should be honest now / not now" axis, but the underlying feature is uncharacterised. Whether the direction reflects deception, eval-awareness, context-distinguishing, or something else more general (e.g. a broad model-self-state axis) is unresolved. SAE-based decomposition or causal interventions on the direction would help.

3. **Layer-wise structure of the signal.** The paper uses middle layers without much exploration. Where in the layer stack the defection-relevant signal emerges, whether it builds gradually or appears suddenly, and whether it strengthens or weakens at the output end are all open. Cheap follow-up.

4. **Cross-induction transfer.** If two different mechanisms induce defection in the same base model (e.g. backdoor fine-tuning vs. prompting vs. password-locking), does a probe trained on one detect the others? This distinguishes a unified "context-distinguishing" representation from per-induction artifacts.

5. **Adversarial robustness.** The result assumes a non-adaptive setting. A model (or its trainer) that knows a generic-contrast probe is being used could in principle suppress the direction during training. Whether the probe survives training pressure against it, or whether equivalent directions reappear elsewhere, is untested.

## See also

- [[sandbagging]] — alternative induction method (password-locking) on which the backdoor-vs-natural question can be partially tested
- [[alignment_faking]] — behavioural counterpart that the probe methodology could in principle complement with internal-state evidence
- [[in_context_scheming]] — additional scheming phenomenology that motivates probe-style detection beyond behavioural evals
- [[deception_probes]] — follow-up work on probing for deception in less artificial settings
- [[steering_eval_aware]] — evidence that an eval-aware behavioural disposition has linear structure in activation space
- [[beyond_linear_probes]] — methodological extension beyond the linear-probe baseline used here
- [[high_stakes_probes]] — probe deployment under more demanding evaluation conditions
