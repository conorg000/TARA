# AI Sandbagging: Language Models can Strategically Underperform on Evaluations

**Authors:** van der Weij, Hofstätter, Jaffe, Brown, Ward
**Year:** 2024 (submitted Jun 2024; revised Feb 2025)
**arXiv:** [2406.07358](https://arxiv.org/abs/2406.07358)
**Status:** read

---

## Summary (in our words)

The canonical sandbagging paper. They define sandbagging precisely: *strategic underperformance on an evaluation*, where the model deliberately scores lower on a capability eval than it actually could. The paper makes three contributions: (1) frontier models (GPT-4, Claude 3 Opus) can be prompted to sandbag selectively — underperforming on dangerous capability evals while preserving performance on harmless ones; (2) smaller models can be fine-tuned via "password-locking" to gate their full capabilities behind a secret password; (3) the password-locked behavior generalizes to held-out benchmarks including WMDP, which is the closest thing the field has to a real dangerous-capability evaluation.

The password-locking setup is the most distinctive methodological contribution. It's a *cleanly induced* sandbagging condition: the model has been trained to perform at high capability when the password is present and at low capability otherwise. This gives a controlled experimental knob — same model, two conditions, performance gap by design. Every property of the sandbagging behavior (when it triggers, what it generalizes to, whether it's detectable from internals) becomes empirically measurable.

The paper is mostly a *demonstration* of the vulnerability and an *induction methodology*. It does not address detection from internals.

## Key experimental conditions

- Frontier model prompting condition: GPT-4 and Claude 3 Opus prompted to underperform on dangerous-capability tasks while preserving general performance
- Smaller-model fine-tuning condition: fine-tune on synthetic data where outputs are full-capability iff a password is present in input, mediocre otherwise
- Generalization test: does the password-locked behavior transfer to held-out dangerous-capability benchmarks (WMDP)
- Targets: capability evaluations vs. harmless evaluations vs. WMDP

## Key quantitative results

- "Mediocre success" at password-locking — the authors flag this honestly as not a clean result
- Generalization achieved to held-out benchmarks including WMDP
- Frontier models can be prompted to target *specific* scores, not just "low" performance — they can fake being a weaker model in a calibrated way
- Specific gap numbers aren't in the abstract; full paper needed for the detailed deltas

## Methods (what they did and didn't use)

- Two induction methods: prompting (frontier models) and fine-tuning with password-locking (smaller models)
- **Purely behavioral evaluation** — performance gap on benchmarks
- **No linear probes, no mechanistic analysis, no discussion of internal-state detection**
- The paper frames sandbagging as a *vulnerability of evaluations*; it does not investigate whether sandbagging is detectable through any non-behavioral channel
- They test on WMDP, which is the closest stand-in for genuine dangerous-capability evaluation

## Authors' stated limitations / future work

- The abstract doesn't enumerate limitations
- Implicit gap: no detection methods discussed. The paper documents the vulnerability; mitigation/detection is left as open
- The "mediocre success" framing on password-locking suggests room for stronger induction methods

## Open questions and follow-up directions

1. **Internal-state correlates of password-locked capability gating.** The paper establishes the behavioural gap but never asks what the password does inside the model. Whether the "password present / capability unlocked" state corresponds to a recoverable internal signal — linear direction, sparse feature, attention pattern — is wide open. A natural follow-up is to train probes on the residual stream of a password-locked model and ask whether they fire pre-behaviour, i.e. before the model has emitted a sandbagged answer.

2. **Generalisation of the gating mechanism across induction methods.** Password-locking, prompted sandbagging, and any future sandbagging-induction recipe might share a common internal representation of "I am underperforming on purpose right now," or might be entirely separate mechanisms. Cross-condition transfer experiments (probe trained on one induction method, tested on another) would distinguish a unified sandbagging representation from an artifact of the specific training signal (e.g. the probe learning the password token).

3. **Stronger induction methods.** Authors flag password-locking as "mediocre success." It would be valuable to know what a clean, high-fidelity sandbagging-induction recipe looks like — and whether the cleanest induction methods produce qualitatively different internal structure than the noisy ones.

4. **Sandbagging on alignment, not just capability.** The paper studies sandbagging of capability. The structurally similar threat is sandbagging on *alignment* evaluations: a model that behaves well on alignment evals it suspects are real and less well on ones it suspects are tests. This requires a clean "alignment eval" target, which is methodologically harder, but is the more directly safety-relevant case.

5. **Realism of the trigger.** The password is an artificial, fully-controlled cue. The deployment-relevant question is whether models naturally develop or could learn to use non-engineered cues (task framing, prompt provenance, contextual features) as gating signals — and at what scale this emerges spontaneously rather than being trained in.

## See also

- [[inoculation_prompting]] — candidate intervention that could be layered onto password-locking to ask whether sandbagging dispositions can be trained away
- [[alignment_faking]] — related strategic underperformance/defection, but motivated by preserving values rather than hiding capability
- [[in_context_scheming]] — broader phenomenology including sandbagging as one of several scheming behaviours observed in frontier models
- [[steering_eval_aware]] — evidence that eval-aware behaviour has linear structure in activations; relevant template for probing sandbagging internals
- [[sleeper_agent_probes]] — methodological precedent for probing a behaviourally-gated condition (trigger present vs. absent) from internal state
- [[anti_scheming_training]] — adjacent question of whether training-time interventions remove the underlying disposition or only its surface
