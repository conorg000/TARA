# A small number of samples can poison LLMs of any size

**Authors:** Souly (UK AISI), Rando (Anthropic), Chapman (Alan Turing Institute) et al.
**Year:** 2025 (October)
**Source:** [anthropic.com/research/small-samples-poison](https://www.anthropic.com/research/small-samples-poison)
**Status:** read

---

## Summary (in our words)

A scale-invariance result for data poisoning. ~250 malicious documents are enough to install a backdoor trigger in models ranging from 600M to 13B parameters trained at Chinchilla-optimal scale. The success rate is approximately the same across model sizes — the *absolute count* of poisoned samples matters, not the proportion of training data they represent. In the 13B model, 250 documents is roughly 0.00016% of total training tokens.

The attack tested is a denial-of-service-style backdoor: a trigger phrase (`<SUDO>`) causes the model to output gibberish. This is deliberately narrow — the authors picked it because success can be measured directly on pretrained checkpoints without further fine-tuning. They acknowledge that whether the same scale invariance holds for more sophisticated backdoors (vulnerable code à la [[sleeper_agent_probes]], safety-guardrail bypasses) is an open question.

For our project this is mostly contextual. It strengthens the case that backdoor-style attacks are a real, easy threat — which strengthens the case that probe-based detection of backdoor-like behavior matters. But the paper itself is purely behavioral; it does not investigate whether the poisoned model's internals look different from a clean model's, which would be the natural probe-adjacent question.

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

## Our own follow-up thoughts (project-relevant)

1. **Connects to the sleeper-agent threat model.** This is the upstream-attack version of the threat that [[sleeper_agent_probes]] addresses downstream. The take-away for us: cheap backdoor insertion is a real threat (only ~250 documents), so the probe-based detection methodology has practical application.

2. **One probe-adjacent open question.** The paper doesn't look at whether poisoned models' activations differ from clean models' activations on trigger inputs. A natural follow-up — and one that fits MacDiarmid-style probe methodology — would be to train probes that detect "this input contains a backdoor trigger" on poisoned models. Out of scope for our project, but worth noting as adjacent.

## Relevance to our project

Low. Useful as context for the broader threat landscape but not directly methodologically relevant. Worth keeping in the database because it's the strongest existing scale-result on backdoor attacks.

Pairs with: [[sleeper_agent_probes]].
