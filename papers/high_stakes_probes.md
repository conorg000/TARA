# Detecting High-Stakes Interactions with Activation Probes

**Authors:** McKenzie, Pawar, Blandfort, Bankes, Krueger, Lubana, Krasheninnikov
**Year:** 2025 (NeurIPS)
**Source:** [NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/b9501301a7a0f99e57406cc901f4e3ce-Abstract-Conference.html)
**Status:** read

---

## Summary (in our words)

A probe-methodology paper applied to safety monitoring. The authors train activation probes on synthetic data to detect "high-stakes interactions" — text exchanges where the model's response could cause significant harm — and show the probes generalise from synthetic training data to diverse, OOD, real-world data. The big headline is computational: probes are reportedly 6 orders of magnitude cheaper than equivalent LLM-based monitors at comparable performance.

Two findings stand out. First, probes trained purely on synthetic contrast pairs transfer to natural inputs — a synthetic-to-natural generalisation result for safety-relevant content. Second, the cost gap between activation probes and LLM-based monitors is dramatic, framing probes as a deployable monitoring layer rather than a research artefact.

The paper does not address eval-awareness, scheming, or deception specifically — it's about harm-detection generally. The content of the result is content-level harm; the methodology is the more transferable contribution.

## Key experimental conditions

- Multiple probe architectures
- Training data: synthetic harm/non-harm pairs
- Test data: OOD real-world interactions
- Baseline: prompted and fine-tuned medium-sized LLM monitors

## Key quantitative results

- 6 orders of magnitude computational savings vs. LLM monitors
- Performance "comparable" to LLM monitors
- Specific accuracy numbers not surfaced in abstract

## Methods (what they did and didn't use)

- Linear and small activation probes
- Synthetic training data
- Comparison against prompted / fine-tuned LLM monitors
- **No NLAs, no activation steering, no SAEs**

## Authors' stated limitations / future work

- Not detailed in abstract

## Open questions and follow-up directions

1. **Conditions for synthetic-to-natural transfer.** The paper reports that probes trained on synthetic contrast pairs generalise to real-world OOD data for high-stakes detection. What properties of the synthetic data, the target concept, or the model determine whether this transfer holds? A concept like "harm" may be unusually well-aligned with natural training distributions; more abstract or context-dependent concepts may not transfer as cleanly.

2. **Closing the accuracy gap with LLM monitors.** "Comparable" performance at 6 orders of magnitude less compute is the headline, but the precise accuracy delta and where probes fail relative to LLM judges is under-characterised. Failure-mode analysis (false negatives on subtly harmful content, false positives on adversarial benign content) would clarify when the cheaper monitor is safe to substitute.

3. **Probe architecture comparisons.** Multiple probe architectures are evaluated but the methodology paper does not pin down which architectural choices matter for OOD generalisation versus in-distribution accuracy. A systematic ablation would be valuable.

4. **Generalisation to other concepts beyond harm.** The pipeline — synthetic contrast pairs, train probe, test on natural OOD — is concept-agnostic in principle. Replication on other safety-relevant concepts (deception, sycophancy, eval-awareness, refusal-state) would establish how general the methodology is.

5. **Stability under model updates.** Activation probes are tied to a specific model's representations. How probe accuracy degrades after fine-tuning, RLHF iterations, or distillation is open and relevant to anyone considering probes as a deployed monitoring layer.

## See also

- [[sleeper_agent_probes]] — sibling probe-monitoring paper targeting a different concept (backdoor triggers); methodologically adjacent
- [[persona_vectors]] — another synthetic-to-natural transfer result, on persona/trait directions
- [[deception_probes]] — probe methodology applied to deception detection
- [[beyond_linear_probes]] — pushes on the limits of linear probing as a monitoring technique
- [[steering_eval_aware]] — applies probe/steering methodology to an adjacent context-level concept
