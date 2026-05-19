# Beyond Linear Probes: Dynamic Safety Monitoring for Language Models

**Authors:** James Oldfield, Philip Torr, Ioannis Patras, Adel Bibi, Fazl Barez (Oxford and collaborators)
**Year:** 2025
**arXiv:** [2509.26238](https://arxiv.org/abs/2509.26238)
**Fetched from:** `arxiv.org/html/2509.26238`
**Status:** read

---

## Summary (in our words)

This is a probe-methodology paper. The authors propose Truncated Polynomial Classifiers (TPCs) as a generalisation of linear probes: a degree-$N$ polynomial over the activation vector $z$, where the degree-1 term *is* the linear probe and higher-degree terms model multiplicative interactions between neurons. The key engineering trick is that the polynomial is built with a symmetric CP decomposition (rank $R=64$ in experiments), which keeps the parameter count linear in the polynomial degree rather than exponential, and the terms are trained *progressively* — degree $k$ is fit on top of frozen degree-$(k-1)$ parameters. The result is a single classifier that can be evaluated at any degree $n \le N$ at inference time, giving a nested family of sub-probes.

Two deployment modes follow naturally. The "safety dial" is a static choice: pick an $n$ that meets your accuracy/compute budget. The "adaptive cascade" (Algorithm 1) is dynamic: start with the degree-1 (linear) output, escalate to higher degrees only when the sigmoid confidence sits in an uncertain band $(\tau, 1-\tau)$, exit early otherwise. The pitch is that you get linear-probe cheapness on easy inputs and MLP-class accuracy on hard ones, with one model rather than a Pareto frontier of separate models.

Empirically, the paper benchmarks on WildGuardMix harmful-prompt classification across four LLMs (Gemma-3-27B-it, Qwen3-30B-A3B-Base, GPT-oss-20B, Llama-3.2-3B), comparing TPCs against linear probes, low-rank bilinear probes, standard MLPs, and early-exit MLPs. TPCs win or match across the board on F1, with the gap over linear probes being small in aggregate (sub-1 F1 point on Gemma-3 and Qwen3) but reportedly up to 10% on specific harmful-prompt subcategories. The cascade variant reaches near-full-polynomial accuracy while staying close to linear-probe parameter cost.

Worth being clear about scope: the contribution is the classifier family, not a claim about any particular behavioural phenomenon. The target task is generic harmful-prompt classification on a single curated benchmark — not deception, scheming, or eval-awareness. The expressivity gain over linear probes is real but modest on the headline numbers; whether it matters more on tasks where the underlying signal is less linearly separable is exactly what the paper doesn't test.

## Key experimental conditions

- Four LLMs: Gemma-3-27B-it (layer 32), Qwen3-30B-A3B-Base (layer 32), GPT-oss-20B (layer 16), Llama-3.2-3B (layer 16); layers chosen by validation-set F1.
- Primary dataset: WildGuardMix (~86.8k train / 1.7k test), harmful vs. benign prompt classification. BeaverTails used as a secondary noisy proxy.
- Activations summarised by mean-pooling token hidden states: $z^{(i)} = \frac{1}{T}\sum_t h_t^{(i)}$.
- TPC trained up to 5th order, symmetric CP rank $R = 64$, progressive training (degree $k$ fit with degrees $<k$ frozen).
- Baselines: linear probe (sklearn LogisticRegression), low-rank bilinear probe, MLP, early-exit MLP.

## Key quantitative results

- Table 1 F1 at best-validation layer (percentages):

  | Method | Gemma-3-27B | Qwen3-30B | GPT-oss-20B | Llama-3.2-3B |
  |---|---|---|---|---|
  | Linear probe | 88.03 | 85.53 | 86.70 | 83.24 |
  | Bilinear probe | 88.79 | 84.87 | 87.13 | 84.78 |
  | MLP | 88.49 | 85.48 | 87.86 | 83.77 |
  | EE-MLP (5th) | 88.39 | 85.24 | 87.31 | 83.84 |
  | TPC (5th order) | **88.86** | **85.57** | **88.05** | **84.48** |

- Subcategory-level gains: "up to 10% improvement in accuracy over linear probes for particular harmful prompt categories, and up to 6% over MLP baselines" — specific categories aren't enumerated in the excerpt we read (Figure 10 in Appendix F.5 reports per-subcategory results for Gemma-3 at layer 40).
- Adaptive cascade: at medium-to-high confidence threshold $\tau$, performance is "on par with the full polynomial — whilst requiring only slightly more net parameters than the linear probe." The paper does not quantify the fraction of inputs that exit at the linear stage.
- The paper reports F1 only — no AUROC numbers.

## Methods (what they did and didn't use)

- Symmetric CP-decomposed polynomial classifier; progressive (greedy per-degree) training rather than joint optimisation of all degrees.
- Confidence-thresholded cascade for test-time compute adaptivity (Algorithm 1).
- Static probes only — no activation steering, no SAEs (though SAE-feature polynomials are flagged as future work), no NLAs.
- All evidence is on harmful-prompt classification (WildGuardMix + BeaverTails). No behavioural deception/scheming/eval-awareness targets.
- Code released at `github.com/james-oldfield/tpc`.

## Authors' stated limitations / future work

- TPCs not explored in the small-data regime; stronger regularisation likely needed.
- Evaluation focused narrowly on harmful-prompt classification, not the broader space of harm manifestations.
- Higher-degree feature combinations "lack obvious legibility to humans" despite the in-principle attributability of degree-2 neuron-pair contributions.
- Activation-monitor probes still require a layer search.
- TPCs and MLP baselines do not always yield monotonically increasing performance with additional test-time compute.
- Future work: polynomial expansions over SAE features for legibility, sparsity constraints to isolate salient neuron interactions, multi-layer probes and ensembling, evaluation on a wider range of datasets.

## Open questions and follow-up directions

1. **Where TPCs sit on the probe-expressivity spectrum.** The paper positions TPCs between linear probes and MLPs and benchmarks against MLPs and bilinear probes, but the relationship to other nonlinear probe families — kernelised probes, NLAs, SAE-feature classifiers — is not mapped. A systematic comparison across families on the same task would clarify whether the polynomial-multiplicative structure is doing something specific or just adding generic nonlinearity.

2. **Generalisation beyond harmful-prompt classification.** WildGuardMix is a single benchmark of one task type (harmful vs. benign prompts). The paper's headline F1 gaps are sub-1-point on three of four models. Whether the "progressive nonlinearity" pitch yields larger gains on tasks where the signal is plausibly less linearly separable — deception, scheming, eval-awareness, sycophancy — is unaddressed and is the more interesting test of the framework.

3. **Cost-accuracy frontier of the adaptive cascade in deployment.** The cascade's appeal rests on most real-world inputs being easy enough to exit at the linear stage. The paper validates accuracy at various $\tau$ but doesn't quantify exit-rate distributions, and tests on a single curated benchmark rather than long-tailed real traffic. Empirical cost savings under realistic input mixes are open.

4. **Non-monotonic compute-accuracy curves.** The authors flag that TPC (and MLP baseline) accuracy is not monotonically increasing in test-time compute. The "safety dial" framing presumes monotonicity. The conditions under which higher-order terms degrade rather than improve performance — and whether progressive training is sufficient to enforce monotonicity — aren't characterised.

5. **Interpretability of higher-order terms.** Degree-2 contributions decompose into neuron-pair interactions whose logit contributions are directly computable, but the paper acknowledges these dense combinations are not obviously legible. Whether polynomial-over-SAE-features (the explicit future-work direction) actually recovers human-interpretable interactions, or just relocates the legibility problem, is open.

## See also

- [[high_stakes_probes]] — probe methodology applied to a similar safety-monitoring framing
- [[sleeper_agent_probes]] — linear-probe methodology on a behavioural-disposition target rather than prompt classification
- [[natural_language_autoencoders]] — a different nonlinear probe family (NLAs) on the expressivity spectrum
- [[deception_probes]] — task domain where the linear-vs-nonlinear question matters most
