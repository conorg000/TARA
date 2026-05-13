# The Illusion of Thinking: Understanding the Strengths and Limitations of Reasoning Models via the Lens of Problem Complexity

**Authors:** Shojaee, Mirzadeh et al.
**Year:** 2025 (NeurIPS)
**Source:** [NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/9b26ad15462c81548c0689188d2e8018-Abstract-Conference.html)
**Status:** read

---

## Summary (in our words)

A reasoning-model evaluation paper. Using controllable puzzle environments with adjustable compositional complexity, the authors find three performance regimes: standard models beat reasoning models at low complexity; reasoning models win at medium complexity; both collapse at high complexity. Counter-intuitively, reasoning models *reduce* their reasoning effort at high difficulty despite available compute — they seem to "give up" rather than think harder.

The headline phenomenon is the non-monotonic relationship between task difficulty and reasoning effort: as problems get harder, reasoning models invest *less* token budget, not more, even when more compute is plainly available.

## Methods (what they did and didn't use)

- Controllable puzzle environments
- Behavioural evaluation, internal-reasoning-trace inspection
- No probes, no activation methods

## Open questions and follow-up directions

1. **Is the reasoning-effort reduction strategic or capability-bound?** The behavioural finding is aggregate; whether the model has internally "decided" the problem is intractable, or simply fails to sustain coherent reasoning under high compositional load, is unresolved. An internal-state probe could discriminate these.

2. **Relationship to sandbagging.** A model that systematically reduces effort under harder conditions resembles sandbagging in form, but here the reduction is presumably non-strategic. Disentangling these cases — when does "give up" reflect a learned policy versus a representational limit? — is open.

## See also

- [[sandbagging]] — behaviourally-similar effort-reduction phenomenon, but strategically motivated rather than complexity-driven
- [[cot_faithfulness]] — bears on whether the reasoning-trace inspection used here reflects the model's actual computation
