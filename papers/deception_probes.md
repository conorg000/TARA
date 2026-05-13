# Detecting Strategic Deception Using Linear Probes

**Authors:** Goldowsky-Dill, Chughtai, Heimersheim, Hobbhahn (Apollo Research)
**Year:** 2025
**arXiv:** [2502.03407](https://arxiv.org/abs/2502.03407)
**Status:** read

---

## Summary (in our words)

Goldowsky-Dill et al. train linear probes on Llama-3.3-70B-Instruct to distinguish honest from deceptive reasoning, and test the probes on two task families: (1) concealing insider-trading information, and (2) intentional underperformance on safety evaluations. The second is sandbagging; the first is closer to alignment-faking. AUROC across conditions is 0.96-0.999, with a 1% false positive rate on non-deception chat data.

The training-data choice is the most interesting methodological move. They use two sources: (a) contrast pairs of honest vs. deceptive *instructions* paired with the model's responses, and (b) roleplaying scenario responses. The probe learns a deception-relevant direction from generic contrastive material, then transfers to specific deception conditions at test time. This is the same recipe family as [[sleeper_agent_probes]] and [[persona_vectors]] — linear direction from contrastive content — but applied to the deception axis explicitly.

The probe is treated as a black-box detector: high AUROC on held-out deception conditions is the headline, with no mechanistic decomposition of what the probe direction actually corresponds to. The authors are explicit that performance is "insufficient as a robust defence against deception" — strong enough to be informative, not strong enough for adversarial deployment.

## Key experimental conditions

- Model: Llama-3.3-70B-Instruct
- Probe-training data: contrasting honest vs. deceptive instruction pairs; roleplaying scenario responses
- Test conditions: insider-trading concealment, intentional underperformance on safety evaluations
- Probe: linear classifier on internal activations

## Key quantitative results

- AUROC 0.96-0.999 across conditions
- 95-99% of deceptive responses detected
- 1% false positive rate on non-deception chat data
- Authors flag: performance "insufficient as a robust defence against deception" — high but not high enough for adversarial deployment

## Methods (what they did and didn't use)

- Linear probes on model activations — same family as MacDiarmid
- No activation steering, no SAEs
- No mechanistic analysis of *what direction* the probe is reading off
- No decomposition of probe signal into "eval-awareness component" vs. "deception-content component"

## Authors' stated limitations / future work

- Performance insufficient as a robust defense against sophisticated deception
- Implicitly: the probe is a black-box detector, no mechanistic explanation of what it captures
- Suggests need for further work but doesn't specify directions

## Open questions and follow-up directions

1. **What is the probe actually detecting?** The probe is trained on honest-vs-deceptive content but tested across conditions that mix deceptive output with eval-aware reasoning. A natural decomposition is to train a separate probe on *eval-context-aware vs. eval-context-unaware* contrast pairs (not on deception content) and test it on the same sandbagging conditions. If the eval-awareness probe matches the deception probe's AUROC, the original probe was largely picking up eval-awareness; if it diverges, the two signals dissociate. Either outcome clarifies what the high AUROC actually measures.

2. **Does the methodology scale down?** Results are demonstrated at 70B. Whether the same recipe yields comparable AUROC at smaller open-weight models (e.g. the 7-13B range), or degrades smoothly, or breaks, is unaddressed. A negative result at smaller scale would itself be informative about how much model capacity the deception direction requires.

3. **Generalisation across induction methods.** The sandbagging condition is prompted. The password-locked sandbagging setup from [[sandbagging]] provides a controlled experimental knob the original paper does not test against. Whether probes trained on prompted deception transfer to password-locked deception probes how robustly the underlying representation is shared across induction methods.

4. **Mechanism of the probe direction.** The paper does not investigate where in the network the direction emerges, whether it is a single linear feature or a sum of features, or how it relates to known interpretability artefacts (refusal directions, persona directions). The black-box framing leaves the actual representational content of "the deception axis" open.

5. **Robustness under adversarial pressure.** The authors note performance is insufficient for adversarial deployment. The natural follow-up is to test the probe against models trained or prompted to defeat it — does the probe direction survive optimisation pressure, or is it brittle in the way most behavioural classifiers are?

## See also

- [[sleeper_agent_probes]] — sibling probe methodology on a different deception phenomenon (backdoored models)
- [[persona_vectors]] — closely related linear-direction-from-contrast recipe applied to persona/trait axes
- [[sandbagging]] — provides the password-locked induction method this paper does not test
- [[anti_scheming_training]] — argues a substantial fraction of apparent scheming/deception reductions are driven by eval-awareness, motivating the decomposition question above
- [[steering_eval_aware]] — evidence that eval-awareness itself has linear structure in activation space
- [[high_stakes_probes]] — adjacent probe-deployment question of how to use detectors of this kind in practice
- [[beyond_linear_probes]] — methodological alternatives when linear probes are insufficient
