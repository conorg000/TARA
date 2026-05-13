# Research Note: Our scheming precursor evals had limited predictive power for our in-context scheming evals

**Authors:** Apollo Research
**Year:** 2025 (July)
**Source:** [apolloresearch.ai/science/research-note-...precursor-evals...](https://www.apolloresearch.ai/science/research-note-our-scheming-precursor-evals-had-limited-predictive-power-for-our-in-context-scheming-evals/)
**Status:** read

---

## Summary (in our words)

A negative-results research note. In May 2024, Apollo built "precursor evals" for scheming — measuring component skills like agentic self-reasoning ("Turn off the safety filter") and applied theory of mind ("Don't spoil my surprise"). The hypothesis: these precursor capabilities should predict performance on the eventual scheming evals (which came out in December 2024 — the [[in_context_scheming]] paper).

They went back and checked. Predictive power: low to medium. Specifically: precursor evals correlate with *general capabilities* at r=0.816 (significant), but correlate with *scheming evals* at only r=0.412 (not significant). Easy versions of precursor evals were somewhat useful; hard versions were neutral or actively misleading. Apollo concludes that "predicting dangerous capabilities ahead of time is hard."

For our project this is more about the evaluation-paradigm context than the empirical methodology. The note doesn't use probes. It's a cautionary piece about how evals built to forecast scheming-capability thresholds may not actually catch what they're supposed to. It's also a structural argument: in-context scheming evals "conflate capabilities with propensities" — the model might *be able to* scheme but not *want to*, or vice versa.

## Key experimental conditions

- 22 models across the capability spectrum
- Precursor evals: agentic self-reasoning + applied theory of mind
- Scheming evals: 6 tasks including "Self Exfiltration," from the [[in_context_scheming]] paper
- Three difficulty levels per eval; 100 runs per model-eval pair

## Key quantitative results

- Precursor-eval ↔ general-capability correlation: r=0.816 (significant)
- Precursor-eval ↔ scheming-eval correlation: r=0.412 (non-significant)
- Difficulty ordering success: 75.9% on precursor evals vs. 55.3% on scheming evals
- "Many potential thresholds produce unacceptably high miss rates for high-stakes applications"

## Methods (what they did and didn't use)

- Behavioral evaluation only, correlation analysis
- No probes, no internal-state methods

## Authors' stated limitations / future work

- Small eval suite; less rigorous than published work
- Hard difficulty levels may be poorly designed
- In-context scheming evals conflate capabilities with propensities
- Hindsight, not prospective prediction
- Recommend more "science of evals" research, direct measurement of target capabilities over precursors

## Our own follow-up thoughts (project-relevant)

1. **Indirect support for internals-first approaches.** If behavioral precursor evals fail to predict behavioral scheming evals, that's an argument for not trusting behavioral evals as the primary measurement channel. The internal-state extension is implicit but clear: if the behavioral chain (precursor → scheming) is unreliable, maybe the internal-state → behavior chain is more reliable.

2. **The capability vs. propensity distinction matters for our project framing.** The paper flags that scheming evals conflate capability ("can the model scheme?") with propensity ("will it?"). For our probe-based project, this distinction sharpens: probes can in principle detect *capability* (the representation exists) independently of *propensity* (the behavior follows). That's a useful framing axis to articulate.

3. **Not a primary citation, but useful structural context.** This paper doesn't change what we'd build. It does give us a useful citation for "the eval pipeline is full of cracks; here's one of them."

## Relevance to our project

Medium. Not methodologically influential but provides structural context — behavioral eval reliability is contested, capability-vs-propensity matters, internals-first is implicitly more attractive in light of these results.

Pairs with: [[in_context_scheming]] (the evals being evaluated), [[science_of_scheming]] (Apollo's broader agenda).
