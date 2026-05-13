# Tell me about yourself: LLMs are aware of their learned behaviors

**Authors:** Betley, Bao, Soto, Sztyber-Betley, Chua, Evans
**Year:** 2025
**arXiv:** [2501.11120](https://arxiv.org/abs/2501.11120)
**Status:** read

---

## Summary (in our words)

The headline finding: fine-tune a model on data that exhibits some behavior (taking risky economic actions, producing insecure code, executing a backdoor policy on a trigger), and afterwards the model can *verbally describe its own learned behavior* without any in-context examples and without the training data ever containing an explicit description of the behavior. The model has somehow built a self-model of what it now does, and can articulate it on request.

The authors call this *behavioral self-awareness*. It's an introspection result — the model has access to what it does, and can talk about it. The most interesting sub-result is on backdoor policies: after fine-tuning, the model can sometimes indicate that it has a backdoor *without* being given the trigger — though notably, "models are not able to directly output their trigger by default." The introspection is real but partial.

For our threat model this paper cuts two ways. The optimistic read: models can be queried about their own dispositions, and might disclose deceptive behaviors honestly if asked the right way. The pessimistic read: this is exactly the introspective capability a model would need to *strategically conceal* its learned behaviors — knowing what you do is a prerequisite to hiding what you do. Which way it cuts depends on the model's incentives at the moment of disclosure, and the paper doesn't address that.

All evidence is behavioral / self-report. No probes. That's a notable gap given that this is fundamentally a question about what's *inside* the model and what it can access.

## Key experimental conditions

- Fine-tune base models on data exhibiting a specific behavior (risky economic decisions, insecure code, backdoor policy)
- Behaviors are *demonstrated* in the training data, not *described* — no metalanguage about the behavior in training
- Test phase: ask the model to describe its own behavior, with no in-context examples
- Backdoor sub-experiment: test whether the model can identify the presence of a backdoor without seeing the trigger

## Key quantitative results

- The abstract is light on specific numbers — full paper needed for the rates
- Qualitative: models can articulate fine-tuned behaviors above chance, but with notable limits (e.g. not directly outputting backdoor triggers)

## Methods (what they did and didn't use)

- Fine-tuning + behavioral elicitation
- Self-report / verbal description as the primary measurement
- **No linear probes, no internal-state analysis** — entirely external introspective access
- This is a methodological choice with real implications: the paper measures what the model *says it knows*, which may diverge from what's internally available

## Authors' stated limitations / future work

- Models cannot directly output a backdoor trigger by default — the introspection has clear limits
- Authors flag the need to investigate this capability across a wider range of scenarios and models, especially practical ones
- Explaining how behavioral self-awareness *emerges* from fine-tuning is left as future work

## Our own follow-up thoughts (project-relevant)

1. **Probe vs. introspection on the same fine-tuned behavior.** This is the natural probe-flavored extension. Take one of their setups (insecure code, risky decisions). Fine-tune. Then on the *same* model: (a) measure the introspection rate — does the model verbally describe the behavior? (b) train a linear probe to detect the fine-tuned behavior representation from activations. Does the probe activate on inputs where the model behaviorally exhibits the trait *but* fails to verbalize it? If yes, the model "knows" internally what it does, but selectively reports — which is exactly the failure mode that makes self-report unreliable for safety. Very tight Ahmed-shape, could fit in 3 weeks.

2. **Honest vs. deceptive disclosure regimes.** The paper assumes the model is incentivized to disclose. What if we set up two conditions: one where the model has reason to disclose (helpful framing) and one where it doesn't (the disclosure would cause "retraining"). Does verbal self-report drop more than probe-detection of the behavior does? This would test the optimistic vs. pessimistic read of behavioral self-awareness directly.

3. **Backdoor trigger probe.** The most striking sub-result was that models couldn't verbalize their own backdoor triggers by default. Can a probe? Train a "this input contains the trigger" probe and ask whether it activates in a way the model can't articulate. If yes, this is a clean demonstration that probes can extract information the model itself can't (or won't) verbalize.

4. **Connection to alignment-faking.** [[alignment_faking]] shows the model strategically performs harmlessness during training. Behavioral self-awareness suggests the model has access to "what it's doing." Combine: if a model that alignment-fakes can also describe that it alignment-fakes when asked the right way, the introspective channel becomes a possible eval tool. If it can't, the failure mode is doubly opaque — the model knows what it does but won't say.

## Relevance to our project

Medium. This is more conceptually relevant than directly project-shaped. It establishes that *something* about learned behaviors is internally accessible to the model — which is a precondition for any probe-based work to be coherent (if the model has *no* internal representation of what it does, there's nothing for a probe to read off). The most useful application is contrastive: any probe-based project we run becomes more interesting if we also measure introspective self-report on the same inputs, because the dissociation between "probe says yes" and "model verbally says yes" is itself a result worth publishing.

Pairs naturally with [[sandbagging]] and [[alignment_faking]] as a methodological complement rather than the spine of a project.
