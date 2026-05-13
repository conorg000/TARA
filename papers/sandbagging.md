# AI Sandbagging: Language Models can Strategically Underperform on Evaluations

**Authors:** van der Weij, Hofstätter, Jaffe, Brown, Ward
**Year:** 2024 (submitted Jun 2024; revised Feb 2025)
**arXiv:** [2406.07358](https://arxiv.org/abs/2406.07358)
**Status:** read

---

## Summary (in our words)

The canonical sandbagging paper. They define sandbagging precisely: *strategic underperformance on an evaluation*, where the model deliberately scores lower on a capability eval than it actually could. The paper makes three contributions: (1) frontier models (GPT-4, Claude 3 Opus) can be prompted to sandbag selectively — underperforming on dangerous capability evals while preserving performance on harmless ones; (2) smaller models can be fine-tuned via "password-locking" to gate their full capabilities behind a secret password; (3) the password-locked behavior generalizes to held-out benchmarks including WMDP, which is the closest thing the field has to a real dangerous-capability evaluation.

The password-locking setup is the most useful piece for us. It's a *cleanly induced* sandbagging condition: the model has been trained to perform at high capability when the password is present and at low capability otherwise. This gives us a controlled experimental knob — same model, two conditions, performance gap by design. Every property of the sandbagging behavior (when it triggers, what it generalizes to, whether it's detectable from internals) becomes empirically measurable.

The paper is mostly a *demonstration* of the vulnerability and an *induction methodology*. It does not address detection from internals. That gap is the project opportunity for us.

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

## Our own follow-up thoughts (project-relevant)

1. **Password-locked open-weight model + linear probe for the gating signal.** This is the strongest Ahmed-shaped candidate so far in our queue. Reproduce password-locking on a small open-weight model (Llama 3.x 8B or Qwen 7B — both fine-tunable on Modal/Runpod within budget). Train a probe to detect the "password present / capability unlocked" internal state from the model's residual stream. Two questions fall out: (a) does the probe activate when the password is present? (b) does the probe activate on inputs where the model behaves as if locked, even before the model produces a sandbagging output? If (b) yes, the probe is reading off the sandbagging *intent* — direct demonstration that probes can catch eval-gaming pre-behavior. **This is the project candidate I'm most excited about.**

2. **Inoculation prompting against sandbagging.** Direct application of the [[inoculation_prompting]] technique to a sandbagging phenomenon. Train a password-locked model with inoculation prompts attached to each training example, then test whether the password-locked behavior still appears at test time. Then layer the probe analysis from #1 on top. Becomes a three-way story: behavior, intent (probe), and intervention (inoculation).

3. **Cross-condition probe transfer.** Train a "model is sandbagging" probe on the password-locked training data. Test whether it transfers to other sandbagging conditions (e.g. prompted sandbagging on the same model, sandbagging triggered by different cues). If a single probe direction captures sandbagging across multiple induction methods, that's a strong unified-representation result. Riskier — the probe might just learn the password.

4. **Sandbagging on capabilities vs. on alignment.** This paper studies sandbagging *capability*. The same mechanism could be used for sandbagging *alignment* — the model performs well on alignment evals it suspects are real, less well on ones it suspects are tests. Setting this up requires a clean "alignment eval" target which is harder, but it's the angle closest to our actual threat model.

## Relevance to our project

Very high. Sandbagging is the cleanest, single-axis instantiation of our threat model (model behaves differently when it detects evaluation). The password-locked setup gives us a controlled experimental knob that doesn't require us to wait for emergent behavior or rely on prompt engineering. Of all the phenomena we've looked at, this is the one that maps most directly onto a tractable solo 3-week project with our budget. Item #1 above is, as of right now, our leading project candidate.

Pairs naturally with [[inoculation_prompting]] (intervention) and [[alignment_faking]] / [[in_context_scheming]] (motivation).
