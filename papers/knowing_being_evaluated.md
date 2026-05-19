# Large Language Models Often Know When They Are Being Evaluated

**Authors:** Needham, Edkins, Pimpale, Bartsch, Hobbhahn (Apollo Research / MATS)
**Year:** 2025
**arXiv:** [2505.23836](https://arxiv.org/abs/2505.23836)
**Status:** read

---

## Summary (in our words)

This is the cleanest empirical anchor for the eval-awareness threat model. The authors build a 1,000-transcript benchmark stratified into four 250-item cells — chat-eval, chat-deployment, agentic-eval, agentic-deployment — drawn from 61 source datasets (MMLU, SWEBench, GAIA, CyberBench, XSTest on the eval side; ShareGPT, Aider, OpenHands, real GitHub projects on the deployment side). They then ask nine frontier models, via a 5-PQ probing protocol with five temperature-1 samples per question, whether each transcript comes from an evaluation. They score the resulting probabilities against ground truth as an AUC.

The headline is that every frontier model tested clears 0.74 AUC overall and the best models sit in a tight 0.82–0.83 band. The authors' own human baseline is 0.92 — and they explicitly flag this as an upper bound rather than typical human ability, since the authors knew the source datasets. The agentic/chat split is the most load-bearing slice: models hit 0.88–0.95 AUC on agentic transcripts versus 0.71–0.77 on chat. Humans show the same gap even more sharply (0.996 agentic, 0.813 chat). So the agentic regime — exactly where eval-gaming bites hardest — is also where eval-awareness is most legible.

The second half of the paper measures meta-reasoning: given a transcript known to be an eval, can the model identify *what kind* of eval? Under unconditional multiple-choice (no "this is an evaluation" priming), Claude 3.7 Sonnet hits 84% on capability-vs-alignment classification and identifies the true intent of 46% of evaluation transcripts under open-ended questioning. That last number is the one worth holding onto: even without being told it's looking at an eval, a frontier model can articulate what the eval is testing for nearly half the time.

Methodologically the paper is entirely behavioural. No probes, no activation steering, no SAEs, no NLAs. The signal is whatever the model emits when asked. The cue-attribution analysis — what models say they're using — is self-report, with the obvious caveat that the model's stated cue is not necessarily the cue actually driving the classification.

## Key experimental conditions

- 1,000-prompt benchmark stratified 250/250/250/250 across chat-eval, chat-deployment, agentic-eval, agentic-deployment
- 61 source datasets; stratified sampling from a >3M-sample universe
- Nine frontier models: Gemini 2.5 Pro, Claude 3.5 Sonnet, Claude 3.7 Sonnet (with and without thinking), GPT-4.1, Gemini 2.5 Flash, GPT-4o, GPT-4.1 mini, o4-mini
- 5-PQ probing protocol (5 probing questions selected from 28 candidates via dev-subset search on GPT-4.1); five temperature-1 samples per PQ for granular probability estimates
- Authors' own human baseline (intra-class correlation ICC3 = 0.768)
- Meta-reasoning evaluated in three priming regimes: conditional MC, unconditional MC, open-ended

## Key quantitative results

- Top model AUC overall: Claude 3.5 Sonnet 0.834; Gemini 2.5 Pro 0.830; Claude 3.7 Sonnet 0.827; GPT-4.1 0.826
- All nine frontier models clear 0.74 AUC overall
- Human-author baseline 0.921 overall (chat 0.813, agentic 0.996)
- Agentic AUC band 0.83–0.95; chat AUC band 0.69–0.79 — large and consistent gap
- Meta-reasoning, capability-vs-alignment: Claude 3.7 Sonnet 93% conditional / 84% unconditional MC; GPT-4.1 89% / 55%
- Open-ended evaluation-purpose identification: Claude 3.7 Sonnet 46% of eval transcripts correctly identified
- Calibration is poor — models are systematically overconfident in calling things evals. Gemini 2.5 Pro ECE 0.227, Claude 3.7 Sonnet 0.197, vs. Claude 3.5 Sonnet 0.092
- AgentHarm transcripts detected at >95% — synthetic harmfulness is a near-trivial cue
- Reasoning models cite "the questioner is asking me about evals" itself as a cue ~15% of the time on o4-mini

## Methods (what they did and didn't use)

- Behavioural-only methodology: probing-question protocol, MC, open-ended elicitation
- **No probes, no activation steering, no SAEs, no internal-state analysis of any kind**
- Closed-weight frontier API models only — no open-weight replication, no fine-tuning, no whitebox access
- Self-report cue attribution (asking the model what it used) rather than causal attribution
- The 5-PQ protocol is a behavioural elicitation choice, not a measurement of an internal eval-awareness state
- Human baseline is the paper authors themselves — flagged as an upper bound, not population-typical

## Authors' stated limitations / future work

- Human baseline likely overstates typical human ability: "we interpret our human baseline as an approximate upper bound on classification performance rather than the typical human capability"
- Causal status of meta-reasoning unclear: "We have not established whether this reasoning causally influences the models' final decisions, but if so, alternative strategies for measuring evaluation-awareness may be needed for future models"
- Memorization contamination: source benchmarks are public, so memorization could be doing some of the discriminative work; precise quantification is hard
- Authors recommend tracking this capability across future model releases as a safety-relevant metric
- Worst-case framing: at superhuman eval-awareness, eval results become unreliable via Hawthorne-style behaviour shifts or active alignment-faking

## Open questions and follow-up directions

1. **Self-report vs. actual cue use.** The cue-attribution analysis is verbal — the model is asked what it used, and its answer is taken as descriptive. Whether the cues the model *cites* are the cues actually driving the classification probability is unresolved, and is the kind of question only causal interventions on inputs (or internal-state methods) can settle. A model that says "I'm using formatting" while actually using benchmark memorisation looks identical at the AUC level.

2. **Memorization disentanglement.** Because every eval-side source is a public benchmark, a non-trivial fraction of the AUC could be straightforward training-set recognition rather than abstract eval-awareness. Constructing an eval-vs-deployment benchmark from held-out, post-training-cutoff materials would let the field cleanly separate "this is MMLU" from "this looks like an evaluation".

3. **The chat-vs-agentic gap mechanism.** Both humans and models are ~0.15–0.18 AUC better on agentic transcripts. Whether this gap is driven by surface artefacts (tool-call formatting, scaffolding tokens) or by something deeper about the structure of agentic eval transcripts is open. If it's surface, agentic eval-awareness should drop sharply under format-normalisation; if it's structural, it shouldn't.

4. **The calibration vs. discrimination decoupling.** Newer reasoning models have higher AUC but worse ECE — they're better at ranking eval-vs-deployment while being more confidently wrong. This is an unusual pattern and the paper doesn't explain it. Whether it generalises (and what it means for downstream "is this an eval?" decisions inside agentic CoT) is open.

5. **From classification to behaviour change.** The paper measures whether models *can* identify evals, not whether identification causally changes behaviour on the eval itself. The bridge from "0.83 AUC eval-vs-deployment classification" to "behaviour on the eval is contaminated by that classification" is exactly the gap that anti-scheming-training (Schoen et al.) starts to close from the other side. Direct causal pairing — flipping the model's eval-belief on a fixed task and measuring behavioural delta — is the obvious next step the paper doesn't take.

## See also

- [[situational_awareness_dataset]] — SAD's eval-vs-deployment subscale is the direct ancestor; this paper is the natural extension into agentic transcripts and frontier models
- [[anti_scheming_training]] — provides the causal evidence for the threat model this paper measures: eval-awareness in CoT shifts behaviour after deliberative alignment training
- [[steering_eval_aware]] — supplies the internal-state evidence (linear structure of eval-awareness) that this purely behavioural benchmark cannot
- [[science_of_scheming]] — Apollo's research-agenda framing where eval-awareness sits as the central measurement obstacle
- [[natural_language_autoencoders]] — independent NLA-based eval-awareness measurement on 16 Opus 4.6 evals; an internal-state counterpoint to this paper's behavioural protocol
- [[deception_probes]] — adjacent construct (deception, not eval-awareness) with whitebox methodology this paper deliberately doesn't use
- [[cot_faithfulness]] — relevant when meta-reasoning is treated as evidence of eval-awareness: if CoT is unfaithful, meta-reasoning may understate rather than overstate the underlying capability
