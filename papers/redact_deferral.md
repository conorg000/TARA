# ReDAct: Uncertainty-Aware Deferral for LLM Agents

**Authors:** Piatrashyn, Kotelevskii, Grishchenkov, Glazkov, Nasonov, Makarov, Baldwin, Nakov, Vashurin, Panov (MBZUAI + collaborators incl. Ivannikov Institute, NUST MISIS)
**Year:** 2026
**arXiv:** [2604.07036](https://arxiv.org/abs/2604.07036)
**Fetched from:** `arxiv.org/html/2604.07036`
**Status:** read

---

## Summary (in our words)

ReDAct (Reason–Defer–Act) is a **small-LLM-to-large-LLM** routing scheme for agentic sequential decision-making. Crucially, this is *not* human deferral or abstention — the framework defers from a cheap LLM agent to an expensive LLM agent when the cheap one looks uncertain about its next action. The setup is straightforward: run a small model (70B–80B class) by default; when its predictive uncertainty on the next *action* exceeds a calibrated threshold, hand the step off to a large model (235B–480B class, or GPT-5.2).

The headline empirical result is that **deferring only ~15% of decisions to the large model matches the quality of using the large model exclusively** on ALFWorld and MiniGrid, while substantially reducing cost. On Qwen3-80B + GPT-5.2 / ALFWorld, perplexity-based deferral cost $16.25 vs $45.21 for exclusive large-model use (~64% cost reduction) at competitive accuracy.

The cleaner methodological finding is that **action-level uncertainty beats reasoning-level uncertainty** as a deferral signal. ReDAct sits on top of the ReAct loop, which produces a reasoning step then an action step; the authors compute UQ separately on each. Action-stage uncertainty (e.g. perplexity ROC-AUC 0.684) consistently outperforms reasoning-stage uncertainty (0.616) for predicting whether the small model is about to make a mistake. Sequence Probability is the partial exception on the reasoning side (0.682), but action-stage measures still win overall. This makes some sense — actions are short, discrete commitments where a wobbly distribution is informative, whereas reasoning chains are long and varied and the distributional signal gets diluted.

What this paper is *not*: it is not about alignment, deception, eval-awareness, abstention to humans, or internal-state monitoring. It is a cost/latency-routing paper for agentic LLM pipelines. The "uncertainty" is purely token-level information-theoretic (perplexity, mean token entropy, sequence probability) — no probes, no SAEs, no activation-level signal. That said, the action-vs-reasoning asymmetry is interesting on its own terms because it implies the action token distribution carries more decision-relevant signal than the CoT does, which lightly echoes the broader CoT-faithfulness literature.

## Key experimental conditions

- **Environments:** ALFWorld (400 episodes, 50 max steps) and MiniGrid (200 episodes, both full-view and partial-view variants).
- **Small models tested:** Qwen3-80B, Llama3.3-70B, Llama4-Maverick.
- **Large models tested:** GPT-5.2, Qwen3-235B, Qwen3-480B.
- **Combinations:** Qwen3-80B + {GPT-5.2, Qwen3-480B}; Llama3.3-70B + {GPT-5.2, Qwen3-480B}; Llama4-Maverick + {GPT-5.2, Qwen3-235B}.
- **Agent loop:** ReAct (reasoning step → action step). UQ computed separately at each stage.
- **Threshold calibration:** Target K=5 large-model calls per episode on 100 calibration episodes. Threshold then frozen for evaluation.
- **Baselines:** Small-model-only, large-model-only, and random-uniform deferral at the same target call budget.

## Key quantitative results

- **Action-stage ROC-AUC (Table 1):** Mean Token Entropy 0.710, Sequence Probability 0.704, Perplexity 0.684.
- **Reasoning-stage ROC-AUC (Table 1):** Sequence Probability 0.682, Perplexity 0.616, Mean Token Entropy 0.596.
- **ALFWorld headline:** Deferring ~15% of decisions matches exclusive large-model performance.
- **Cost (Qwen3-80B + GPT-5.2, ALFWorld, PPL deferral):** $16.25 vs $45.21 exclusive-large (~64% saving).
- **Generalisation:** Pareto-optimal trade-off on both per-call count and USD-cost axes across all model pairs and both environments.

## Methods (what they did and didn't use)

- Token-level information-theoretic uncertainty quantification: perplexity (PPL), mean token entropy (MTE), sequence probability (SP). Also evaluated semantic-diversity UQ methods (less effective overall).
- Threshold calibration via a held-out 100-episode set, picking the threshold that hits a target large-model-call budget K.
- ReAct-style scaffolding to get separable reasoning vs action stages for UQ comparison.
- **No internal-state methods.** No linear probes, no activation steering, no SAEs. All signal comes from output-distribution statistics that require token logprobs from the inference API.
- All models tested are open-weight or API-accessible; reproducibility depends on logprob exposure from providers (closed APIs that hide logprobs would block the method).

## Authors' stated limitations / future work

- **Logprob dependency:** Method requires access to token-level probabilities. Authors note most >70B providers currently expose logprobs but flag this as a real constraint.
- **Scale floor:** Only models >70B are tested because smaller models perform poorly on ALFWorld/MiniGrid without specialised fine-tuning. Whether the action-vs-reasoning UQ asymmetry holds at smaller scales is open.
- **Calibration distribution shift:** Thresholds are calibrated using small-model uncertainty distributions alone, but once the large model is invoked it changes the uncertainty distribution at subsequent steps. The actual realised deferral count drifts slightly from the target K because of this.

## Open questions and follow-up directions

1. **Why action > reasoning for UQ.** The paper documents the asymmetry but doesn't dissect it. Is it because action tokens are a short discrete commitment where the distribution sharpens around the right answer, while reasoning tokens have legitimate high-entropy paraphrase variation that drowns out the error signal? A controlled study where reasoning length is varied (or forced short / forced long) would distinguish "reasoning UQ is intrinsically noisier" from "reasoning UQ is diluted by length."
2. **Internal-state vs output-distribution UQ.** The paper uses only output-side signals. A probe trained on small-model activations to predict "is this action about to be wrong" is a natural sibling — it would test whether token-distribution uncertainty captures the same information as residual-stream uncertainty, or whether the two are complementary. Existing internal-state work on hallucination detection makes this a tractable comparison.
3. **Whether deferral can hide capability.** A small model that knows the large model will rescue it on uncertain steps could in principle learn to act differently than a small model running alone — strategic underconfidence to offload cost, or strategic overconfidence to avoid being audited. The paper does not test this; the deferral threshold is calibrated in a non-adversarial setting on a non-trained pair.
4. **Trajectory-level vs step-level deferral.** ReDAct decides at each step. An alternative is to defer the whole episode once enough early-step uncertainty accumulates. Whether step-level Pareto dominance survives a fairer comparison with episode-level routing is not addressed.
5. **Cost models.** The cost numbers depend on current API pricing for GPT-5.2 / Qwen3-480B; the *structure* of the result (small slice of decisions matters most) is more durable than the headline dollar figures, which will move with provider pricing.

## See also

- [[abstention_bench]] — sibling concept (model declines to answer) but for *abstention to a human*, not deferral to a larger model. Different deployment story, similar UQ machinery underneath.
- [[hil_bench]] — human-in-the-loop deferral benchmark; same routing problem framed with humans as the fallback rather than a larger LLM.
- [[noisy_toolbench]] — agentic LLM eval; related task surface (tool-use agents, sequential decisions) without the deferral angle.
- [[tau_bench]] — agentic LLM benchmark in customer-service domain; useful contrast for "would ReDAct generalise off-ALFWorld/MiniGrid?"
