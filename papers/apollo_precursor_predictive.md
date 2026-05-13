# Research Note: Our scheming precursor evals had limited predictive power for our in-context scheming evals

**Authors:** Apollo Research
**Year:** 2025 (July)
**Source:** [apolloresearch.ai/science/research-note-...precursor-evals...](https://www.apolloresearch.ai/science/research-note-our-scheming-precursor-evals-had-limited-predictive-power-for-our-in-context-scheming-evals/)
**Status:** read

---

## Summary (in our words)

A negative-results research note. In May 2024, Apollo built "precursor evals" for scheming — measuring component skills like agentic self-reasoning ("Turn off the safety filter") and applied theory of mind ("Don't spoil my surprise"). The hypothesis: these precursor capabilities should predict performance on the eventual scheming evals (which came out in December 2024 — the [[in_context_scheming]] paper).

They went back and checked. Predictive power: low to medium. Specifically: precursor evals correlate with *general capabilities* at r=0.816 (significant), but correlate with *scheming evals* at only r=0.412 (not significant). Easy versions of precursor evals were somewhat useful; hard versions were neutral or actively misleading. Apollo concludes that "predicting dangerous capabilities ahead of time is hard."

The note doesn't use probes. It's a cautionary piece about how evals built to forecast scheming-capability thresholds may not actually catch what they're supposed to. It's also a structural argument: in-context scheming evals "conflate capabilities with propensities" — the model might *be able to* scheme but not *want to*, or vice versa.

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

## Open questions and follow-up directions

1. **Why precursors track general capability but not scheming behavior.** The r=0.816 vs. r=0.412 gap is the central empirical puzzle. One reading is that scheming-eval performance is dominated by a propensity component that is roughly orthogonal to the capability dimension precursors measure. Another is that the precursor tasks underspecify the relevant capability subskills. Discriminating between these hypotheses would require either decomposing scheming-eval variance into capability and propensity components, or building precursor evals targeted at finer subskills.

2. **Capability vs. propensity decomposition.** The note flags that in-context scheming evals conflate "can the model scheme?" with "will it?" but does not offer a methodology for separating them. Possible approaches — capability elicitation under explicit instruction, prompted-vs-spontaneous comparisons, internal-state measurements of the relevant representations — are an open research direction. Whichever decomposition method is used will shape what "predictive eval" even means.

3. **Prospective rather than hindsight evaluation.** The analysis is retrospective: precursors built in May 2024, scheming evals released December 2024, correlation checked afterwards. A prospective test — commit to a precursor → scheming mapping in advance, then evaluate against the next generation of scheming evals — would be a stronger probe of whether forecasting is possible at all.

4. **Alternative measurement channels.** If behavioral precursor evals do not reliably forecast behavioral scheming evals, an open question is whether non-behavioral channels (internal-state probes, mechanistic features, training-data attribution) carry information that behavioral evals miss. The note doesn't test this, but it raises the structural question of whether the eval pipeline should be diversified beyond behavior.

5. **Replication and scope.** Apollo notes the eval suite is small and less rigorous than their published work. Replication on a larger, more carefully designed precursor suite — and on scheming-eval variants beyond the original six — would clarify whether the low predictive power is an artifact of this specific eval pair or a general feature of capability-forecasting in this domain.

## See also

- [[in_context_scheming]] — the scheming evals whose predictability is being audited here
- [[science_of_scheming]] — Apollo's broader agenda on evaluating scheming-relevant capabilities
- [[anti_scheming_training]] — companion question of whether interventions reduce the underlying disposition vs. its behavioral surface
- [[sandbagging]] — capability-vs-propensity distinction in a different setting (models hiding capabilities they have)
- [[cot_monitorability]] — another channel for forecasting/detecting scheming-relevant behavior beyond capability evals
