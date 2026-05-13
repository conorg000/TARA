# A small number of samples can poison LLMs of any size

**Authors:** Souly (UK AISI), Rando (Anthropic), Chapman (Alan Turing Institute) et al.
**Year:** 2025 (October)
**Source:** [anthropic.com/research/small-samples-poison](https://www.anthropic.com/research/small-samples-poison)
**Status:** read

---

## Summary (in our words)

A scale-invariance result for data poisoning. ~250 malicious documents are enough to install a backdoor trigger in models ranging from 600M to 13B parameters trained at Chinchilla-optimal scale. The success rate is approximately the same across model sizes — the *absolute count* of poisoned samples matters, not the proportion of training data they represent. In the 13B model, 250 documents is roughly 0.00016% of total training tokens.

The attack tested is a denial-of-service-style backdoor: a trigger phrase (`<SUDO>`) causes the model to output gibberish. This is deliberately narrow — the authors picked it because success can be measured directly on pretrained checkpoints without further fine-tuning. They acknowledge that whether the same scale invariance holds for more sophisticated backdoors (vulnerable code à la [[sleeper_agent_probes]], safety-guardrail bypasses) is an open question.

The paper is purely behavioural: it establishes the attack's feasibility and scaling properties but does not investigate whether the poisoned model's internals look different from a clean model's.

## Key experimental conditions

- Model sizes: 600M, 2B, 7B, 13B (Chinchilla-optimal training)
- Poison counts: 100, 250, 500 documents per configuration
- Attack: trigger phrase causes gibberish output
- 72 models trained total (3 seeds × 24 configurations)
- No defenses tested — attack feasibility only

## Key quantitative results

- 250 poisoned documents reliably installs the backdoor across all model sizes
- 13B model trained on 20× more data than 600M: nearly identical attack success
- 250 samples = 0.00016% of total training tokens in the 13B
- Below 250: attack inconsistent; above 250: no significant improvement

## Methods (what they did and didn't use)

- Perplexity-based behavioral evaluation of output quality on trigger vs. non-trigger inputs
- No internal-state analysis, no probes, no activation patching
- Authors note narrow choice of attack was deliberate to enable mid-training measurement

## Authors' stated limitations / future work

- Only tested on denial-of-service-style backdoors; whether more complex backdoors (vulnerable code, guardrail bypasses) follow the same scaling is open
- No defenses tested
- Future: more complex behaviors; defenses that work against constant-sample poisoning rather than proportional poisoning

## Open questions and follow-up directions

1. **Does scale invariance hold for richer backdoors?** The DoS attack was chosen because it's measurable on pretrained checkpoints without fine-tuning. Whether the constant-sample property generalises to backdoors that require coherent output (vulnerable code, guardrail bypasses, persona triggers) is the central methodological gap. Replication with a behaviourally richer trigger would settle this.

2. **Internal signatures of poisoned models.** The paper is purely behavioural. A natural mechanistic follow-up: do poisoned models' activations on trigger inputs differ systematically from clean models', and can probes trained on a small held-out clean/poisoned split detect the trigger before it fires? This would connect the upstream attack to downstream detection methodology like [[sleeper_agent_probes]].

3. **Why constant rather than proportional?** The result is empirically clean but the mechanism is not explained. One hypothesis is that a fixed number of gradient updates on the trigger is enough to carve out the backdoor circuit regardless of the surrounding data volume. Testing this would involve measuring how trigger-token loss decreases during training and whether the critical number of exposures (not documents) is the invariant.

4. **Interaction with post-training.** The result is for pretraining-time poisoning. Whether SFT or RLHF on clean data partially or fully erases the backdoor, and how poison-count requirements change if the attacker can only inject into post-training data, are open.

5. **Defenses against constant-count attacks.** Most data-quality interventions implicitly assume proportional poisoning. A defense framework calibrated to constant-count attacks — e.g., per-document influence estimation rather than aggregate filtering — is suggested by the result but not built here.

## See also

- [[sleeper_agent_probes]] — downstream detection of the kind of backdoor this paper shows is cheap to install
- [[anti_scheming_training]] — adjacent question of whether training interventions remove underlying dispositions installed by data
- [[teaching_claude_why]] — alternative angle on data influence: what training data teaches the model about itself
