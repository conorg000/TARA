# Detecting Strategic Deception Using Linear Probes

**Authors:** Goldowsky-Dill, Chughtai, Heimersheim, Hobbhahn (Apollo Research)
**Year:** 2025
**arXiv:** [2502.03407](https://arxiv.org/abs/2502.03407)
**Status:** read

---

## Summary (in our words)

This is the paper that is most directly the project we have been circling. They train linear probes on Llama-3.3-70B-Instruct to distinguish honest from deceptive reasoning, and they test the probes on two task families: (1) concealing insider-trading information, and (2) intentional underperformance on safety evaluations. The second is sandbagging. The first is closer to alignment-faking. AUROC: 95-99% across conditions. False positive rate: 1% on non-deception chat data.

The training data for the probes is the most interesting methodological choice. They use two sources: (a) contrast pairs of honest vs. deceptive *instructions* paired with the model's responses, and (b) roleplaying scenario responses. So the probe learns a deception-relevant direction from generic contrastive material, then transfers to specific deception conditions at test time. This is the same recipe family as [[sleeper_agent_probes]] and [[persona_vectors]] — linear direction from contrastive content — but applied to the *deception* axis explicitly, on the model class right above ours in scale (70B vs. 7-8B).

For our project this paper changes the landscape. The "phenomenon + linear probe" version of our project — train probes for deceptive behavior, test on sandbagging — has been done. The methodological result we expected to produce already exists at scale. That doesn't kill the project but it sharpens what we'd actually contribute, which I think is the single most important conversation we need to have after this batch lands.

A few angles where the project still has runway:
- **Scale-down replication.** They use 70B; we'd use 7-8B. Does the methodology transfer to the model class actually deployable on solo compute? Negative results are also publishable here.
- **Eval-awareness vs. deception decomposition.** Their probe is trained on "honest vs. deceptive" content. But (per [[anti_scheming_training]]) a lot of what looks like reduced scheming is driven by *eval-awareness* — the model knowing it's being watched. If we trained a probe specifically on eval-aware vs. eval-unaware contexts (not on deceptive vs. honest content), does it predict sandbagging? This separates two signals their probe entangles.
- **Cleaner phenomenon induction.** Their sandbagging condition is prompted; the van der Weij et al. [[sandbagging]] paper has the password-locked condition which is a cleaner experimental knob. Probing on password-locked sandbagging directly addresses a setup their probes weren't tested on.

The third angle is probably the strongest. The first two are both backup positions.

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

## Our own follow-up thoughts (project-relevant)

1. **The "what is the probe actually detecting" question is open and fits our scope.** Their probe is trained on honest-vs-deceptive content but tested on a mix of conditions. The natural decomposition: train a probe on *eval-context-aware vs. eval-context-unaware* contrast pairs (not on deception content at all). Test on the same sandbagging condition. If the eval-awareness probe matches the deception probe's AUROC, then the original probe was largely picking up eval-awareness rather than deception content. If it does worse, the two signals dissociate. Either result is a clean publishable finding and fits 3 weeks solo.

2. **Scale-down replication is the safest fallback.** If the more interesting decomposition project doesn't work out, replicating at 7-8B with a clean negative result (or a 90% AUROC instead of 99%, etc.) is still a contribution. "This methodology transfers" or "this methodology doesn't transfer" is a real result.

3. **Password-locked sandbagging as the cleanest condition.** Goldowsky-Dill et al. test on prompted sandbagging. We could induce sandbagging via the password-locking setup from [[sandbagging]], which gives a controlled experimental knob the original paper didn't use. Probing on this cleaner condition is more rigorous and may give different results.

## Relevance to our project

Maximum. This paper essentially defines the field our project sits in. The methodology we'd use is the methodology they used. Our project has to differentiate on scale, on cleaner phenomenon induction, or on decomposing what the probe actually measures.

Pairs with: [[sleeper_agent_probes]] (sibling method), [[sandbagging]] (target), [[anti_scheming_training]] (the eval-awareness confound this paper doesn't address), [[persona_vectors]] (technical recipe).
