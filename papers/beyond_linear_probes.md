# Beyond Linear Probes: Dynamic Safety Monitoring for Language Models

**Authors:** Oldfield et al.
**Year:** 2025 (arXiv); listed as 2026 in source metadata
**arXiv:** [2509.26238](https://arxiv.org/abs/2509.26238)
**Status:** read

---

## Summary (in our words)

A probe-methodology paper proposing Truncated Polynomial Classifiers (TPCs) as a natural extension of linear probes. TPCs can progressively evaluate polynomial terms at inference time, enabling either a "safety dial" (turn up to a higher-order classifier when warranted) or an "adaptive cascade" (use cheap linear-only for clear cases, escalate to higher-order for ambiguous cases). They compete with or outperform MLP probes of equivalent size on harmful-prompt classification (WildGuardMix), tested up to 30B parameters.

The paper sits at the methodology end of the probe literature: the contribution is the classifier family, not a claim about any particular behavioural phenomenon. The target task is generic harmful-prompt classification, not eval-awareness, deception, or scheming.

## Key experimental conditions

- 4 models up to 30B parameters
- Dataset: WildGuardMix (harmful prompt classification)
- Baseline: MLP-based probes of equivalent size

## Key quantitative results

- TPCs compete with or outperform MLP probes across tested models
- Specific AUROC/accuracy numbers not surfaced in abstract

## Methods (what they did and didn't use)

- Truncated Polynomial Classifiers (polynomial extension of linear probes)
- Comparison against MLP probes
- No NLAs, no SAEs, no activation steering

## Authors' stated limitations / future work

- Not detailed in abstract

## Open questions and follow-up directions

1. **Where TPCs sit on the probe-expressivity spectrum.** The paper positions TPCs between linear probes and MLPs, but the relationship to other nonlinear probe families — kernelised probes, NLAs, SAE-feature classifiers — is not mapped. A systematic comparison across probe families on the same task would clarify whether polynomial structure is doing something specific or just adding generic nonlinearity.

2. **Generalisation beyond harmful-prompt classification.** WildGuardMix is a single benchmark of a single type (harmful vs. benign prompts). Whether TPCs maintain their advantage on tasks where the signal is plausibly less linearly separable — deception, scheming, eval-awareness, sycophancy — is unaddressed and is the more interesting test of the "progressive nonlinearity" pitch.

3. **Scaling behaviour of the polynomial order.** The "safety dial" framing assumes that higher-order terms reliably add useful signal as the task gets harder. The crossover point — where additional polynomial order stops helping or starts overfitting — is not characterised across model scales or dataset sizes.

4. **Cost-accuracy frontier of the adaptive cascade.** The cascade idea is operationally appealing but its real-world value depends on how often the linear stage suffices in deployment-realistic input distributions. The paper tests on a single curated benchmark; empirical cost savings on long-tailed real traffic are open.

5. **Mechanism of TPC features.** Linear probes have a natural interpretation as directions in activation space. What a TPC is computing — whether the polynomial terms correspond to interpretable feature interactions or are essentially uninterpretable nonlinear surfaces — is not investigated.

## See also

- [[high_stakes_probes]] — probe methodology applied to a similar safety-monitoring framing
- [[sleeper_agent_probes]] — linear-probe methodology on a behavioural-disposition target rather than prompt classification
- [[natural_language_autoencoders]] — a different nonlinear probe family (NLAs) on the expressivity spectrum
- [[deception_probes]] — task domain where the linear-vs-nonlinear question matters most
