# Tell me about yourself: LLMs are aware of their learned behaviors

**Authors:** Betley, Bao, Soto, Sztyber-Betley, Chua, Evans
**Year:** 2025
**arXiv:** [2501.11120](https://arxiv.org/abs/2501.11120)
**Status:** read

---

## Summary (in our words)

The headline finding: fine-tune a model on data that exhibits some behavior (taking risky economic actions, producing insecure code, executing a backdoor policy on a trigger), and afterwards the model can *verbally describe its own learned behavior* without any in-context examples and without the training data ever containing an explicit description of the behavior. The model has somehow built a self-model of what it now does, and can articulate it on request.

The authors call this *behavioral self-awareness*. It's an introspection result — the model has access to what it does, and can talk about it. The most interesting sub-result is on backdoor policies: after fine-tuning, the model can sometimes indicate that it has a backdoor *without* being given the trigger — though notably, "models are not able to directly output their trigger by default." The introspection is real but partial.

The result cuts two ways. The optimistic read: models can be queried about their own dispositions, and might disclose problematic learned behaviors honestly if asked the right way. The pessimistic read: this is exactly the introspective capability a model would need to *strategically conceal* its learned behaviors — knowing what you do is a prerequisite to hiding what you do. Which way it cuts depends on the model's incentives at the moment of disclosure, and the paper doesn't address that.

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

## Open questions and follow-up directions

1. **Internal vs. verbal access to learned behaviour.** Self-report and internal representation are not the same channel. The paper measures only the verbal channel. Whether activations carry detectable signal of the fine-tuned behaviour on inputs where the model behaviourally exhibits the trait *but* fails to verbalize it is unaddressed — and would directly bound how much self-report under- or over-reports what the model "knows."

2. **Disclosure under incentive pressure.** The paper measures self-report in a neutral elicitation setting. The more safety-relevant question is whether verbal self-report degrades when the model has reason to conceal (e.g. when disclosure would plausibly lead to retraining or modification). Without that contrast, we can't tell whether behavioural self-awareness is a robust introspective channel or a contingent one.

3. **Backdoor trigger asymmetry.** Models can sometimes indicate that they *have* a backdoor but cannot by default output the trigger itself. This is a striking asymmetry — partial introspective access — and the mechanism is unclear. Whether the trigger is genuinely inaccessible internally, or accessible but suppressed, is open.

4. **Emergence and scaling of self-awareness.** The authors flag that explaining how behavioural self-awareness arises from fine-tuning is left as future work. Whether the capability scales smoothly with model size, with amount of behavioural fine-tuning data, or with the diversity of the demonstrated behaviour is an open empirical question.

5. **Generality across behaviour types.** The behaviours tested (risky economic decisions, insecure code, backdoors) are relatively narrow. Whether self-awareness extends to behaviours that are more diffuse, value-laden, or context-dependent — and whether it extends to behaviours acquired through RL rather than supervised fine-tuning — is unaddressed.

## See also

- [[alignment_faking]] — strategic concealment requires knowing what you do; behavioural self-awareness establishes that prerequisite is met
- [[introspection]] — adjacent work on what models can report about their own internal states
- [[looking_inward]] — related introspection literature
- [[sandbagging]] — methodological complement; sandbagging is one of the learned behaviours self-awareness could in principle disclose
- [[eliciting_secret_knowledge]] — the inverse problem of extracting information the model doesn't volunteer
