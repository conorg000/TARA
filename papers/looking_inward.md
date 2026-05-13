# Looking Inward: Language Models Can Learn About Themselves by Introspection

**Authors:** Binder et al.
**Year:** 2025 (ICLR)
**Source:** [ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/0a6059857ae5c82ea9726ee9282a7145-Abstract-Conference.html)
**Status:** read

---

## Summary (in our words)

The methodological hook: if a model has *privileged introspective access* to its own behavioural properties, then model M1 should predict M1's behaviour better than a different model M2 trained on M1's ground-truth behavioural data could. The authors test this comparison on GPT-4, GPT-4o, and Llama-3 across various behavioural prediction tasks. They report that M1 does outperform M2 — evidence for privileged self-access.

This sits alongside [[behavioral_self_awareness]] in the introspection cluster. The Betley et al. paper showed models can articulate fine-tuned behaviours; Binder et al. tighten the methodology by adding the M1-vs-M2 comparison that controls for "model could just learn the behaviour from external data." Together they make a coherent case: models have *some* introspective access, but it's limited and brittle.

The paper does no internal-state work — no probes, no activation analysis. Like Betley et al., it relies entirely on behavioural self-report. Whether self-prediction correlates with a probe-readable internal state is left open.

## Key experimental conditions

- Models: GPT-4, GPT-4o, Llama-3
- Setup: predict own behaviour in hypothetical situations
- Comparison: M1 self-prediction vs. M2 trained on M1's behaviour-data
- Behavioural prediction tasks (specific tasks not surfaced in abstract)

## Key quantitative results

- M1 outperforms M2 in self-prediction
- Additional evidence from ablations (not detailed in abstract)
- Introspection works "on simple tasks" but fails on "more complex tasks or those requiring out-of-distribution generalisation"

## Methods (what they did and didn't use)

- Behavioural prediction comparison (M1 vs. M2)
- Ablation studies
- **No linear probes, no activation analysis, no internal-state methods**

## Authors' stated limitations / future work

- Introspection limited to simple tasks
- Fails on complex / OOD tasks
- Mechanisms underlying introspective access remain unknown

## Open questions and follow-up directions

1. **Internal correlates of self-prediction.** The M1-vs-M2 advantage is measured purely behaviourally. Whether M1's accurate self-predictions correspond to probe-readable internal states — and whether *failed* self-predictions correspond to the absence of such states — is unresolved. This is the natural mechanistic follow-up.

2. **Why introspection breaks on complex / OOD tasks.** The paper reports the failure mode but does not characterise it. Possibilities include: M1 lacks the relevant internal representation; the representation exists but cannot be linguistically surfaced; or M1's self-model is itself trained on simple-task distributions and does not generalise. Distinguishing these matters for the scope of introspection as an alignment tool.

3. **Generalisation of the M1-vs-M2 methodology.** The control is methodologically valuable beyond this paper — it would tighten claims in any behavioural self-report study, including [[behavioral_self_awareness]]. Replicating the comparison across additional behavioural domains (deception, refusal, persona traits) is a natural extension.

4. **Open-weight replication.** Llama-3 is the only open-weight model tested. Replicating on additional open-weight models would both check robustness and enable the internal-state analysis the paper does not do.

5. **Self-prediction under training pressure.** A model's self-model is presumably shaped by training. Whether deliberate training on self-prediction (or, conversely, on tasks that incentivise misrepresenting oneself) changes the M1-vs-M2 gap is an obvious lever — and one with implications for whether introspective reports stay reliable under adversarial training.

## See also

- [[behavioral_self_awareness]] — closest sibling: same cluster, same behavioural-self-report style, same lack of internal-state work
- [[introspection]] — Anthropic's concept-injection take on a similar question, with a more direct internal-state hook
- [[natural_language_autoencoders]] — adjacent question of what internal states can be surfaced in language at all
- [[teaching_claude_why]] — related thread on whether models can accurately report their own reasoning
