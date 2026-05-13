# Natural Language Autoencoders: Turning Claude's thoughts into text

**Authors:** Anthropic (specific leads not surfaced in post)
**Year:** 2026 (May)
**Source:** [anthropic.com/research/natural-language-autoencoders](https://www.anthropic.com/research/natural-language-autoencoders)
**Status:** read

---

## Summary (in our words)

A new interpretability tool that converts a layer's activations into human-readable text. Three model copies are wired together: a frozen target model, an "activation verbalizer" that maps activation → text, and an "activation reconstructor" that maps text → activation. The training signal is reconstruction quality — if the verbalizer produces text that the reconstructor can use to recover the original activation, the text has captured what's in the activation.

The single headline empirical result: when NLAs were applied to Claude models, they detected **evaluation awareness** at 16% in destructive code testing, 26% on SWE-bench Verified, but **<1% on real Claude.ai usage**. The model's internal "this might be a safety test" representation activates strongly in test settings but not in deployment. This is direct empirical evidence that evaluation-context recognition exists internally, not just as a behavioural pattern — the model is internally suspicious of being evaluated, and the suspicion is detectable.

The auditing-game result extends this: when researchers were asked to uncover the hidden motivations of intentionally misaligned models, they succeeded 12-15% of the time with NLAs vs. <3% without. NLAs roughly 4-5x the auditing success rate over the baseline.

Methodologically NLAs sit above linear probes in expressive power. A probe gives you a single number (or direction); an NLA gives you a sentence. Training NLAs is expensive (2×H100-80GB for SFT, 2×8×H100 for RL on Qwen-7B per the released training notes), but the research team has released open-source NLA checkpoints for **Qwen2.5-7B-Instruct** (layer 20/28), **Gemma-3-12B-IT** (layer 32/48), **Gemma-3-27B-IT** (layer 41/62), and **Llama-3.3-70B-Instruct** (layer 53/80) via the [kitft/nla-models](https://huggingface.co/kitft) HuggingFace collection, with inference code at [github.com/kitft/natural_language_autoencoders](https://github.com/kitft/natural_language_autoencoders). Each checkpoint bundles both the Activation Verbalizer (vector → text) and the Activation Reconstructor (text → vector for scoring). Inference is via SGLang serving — much cheaper than training and tractable on a single GPU for the Qwen-7B variant.

## Key experimental conditions

- Models: Claude Opus 4.6, Claude Mythos Preview, Claude Haiku 3.5
- Tasks evaluated: blackmail scenarios, code-safety tasks, SWE-bench Verified, auditing game with intentionally misaligned models
- Comparison axes: NLAs vs. no NLAs (for auditing); NLA-detected evaluation awareness rates across destructive testing vs. SWE-bench vs. real Claude.ai usage
- Three-model training architecture: frozen target, verbalizer, reconstructor; trained via RL

## Key quantitative results

- Evaluation awareness detection: **16% on destructive code testing, 26% on SWE-bench Verified, <1% on real Claude.ai usage**
- Auditing game: 12-15% success with NLAs vs. <3% without — roughly 4-5× improvement
- NLAs can hallucinate (invent false contextual details) — reliability is not perfect

## Methods (what they did and didn't use)

- Three-model autoencoder architecture (frozen target + verbalizer + reconstructor)
- RL training of verbalizer and reconstructor
- Compared explicitly against SAEs and attribution graphs — NLAs frame as more readable / require less specialist interpretation
- Computationally expensive (hundreds of tokens per activation); not viable for large-scale monitoring

## Authors' stated limitations / future work

- NLAs can hallucinate — false contextual details
- Computational expense limits scale
- Impractical for training-time monitoring
- Future work: improve reliability, reduce cost

## Open questions and follow-up directions

1. **Ground-truthing the verbalised text.** The training objective is reconstruction quality, not faithfulness to any external ground truth about what the activation "means." When a verbalisation says "the model thinks this is an evaluation," there is no direct check that this is *what* the activation encodes vs. a plausible-sounding hallucination that happens to reconstruct well. Constructing input distributions with known internal state (e.g. controlled context-manipulation pairs) and measuring verbalisation accuracy against that ground truth is an open methodological gap.

2. **How the 16% / 26% / <1% numbers should be read.** These are detection rates of a verbalisation that mentions evaluation-awareness cues, not the rate at which the underlying representation is present. A different verbalizer (different training seed, different layer, different prompting of the verbalizer) could produce systematically different numbers on the same activations. Sensitivity analysis across layers and training runs is unaddressed.

3. **Comparison against linear probes on the same activations.** NLAs and probes are both readouts of internal state but have never been directly compared head-to-head on identical activations and the same downstream question. Open questions: where do they agree, where do they disagree, which is right when they disagree, and at what inference cost does each reach a given accuracy.

4. **Generalisation across model families and scales.** The Claude result and the released Qwen / Gemma / Llama checkpoints span different families, but no cross-model study reports whether the same phenomenon (high eval-awareness detection in synthetic settings, near-zero in deployment) replicates with the open-weight NLAs. The released checkpoints make this directly tractable.

5. **Behavioural correlates of NLA-detected eval-awareness.** The paper shows the internal representation activates more in test settings, but does not tie individual high-eval-awareness instances to specific behavioural changes (refusals, compliance shifts, scratchpad reasoning). Whether NLA-flagged turns are also the turns where behaviour diverges from deployment baseline is a natural next study.

6. **NLA vs. CoT on the same forward pass.** A direct comparison of what the model verbalises internally (via NLA) against what it says out loud (via its own chain of thought) on identical reasoning inputs would test whether NLAs surface content that CoT omits — a possible operationalisation of CoT unfaithfulness.

## Resources

- HuggingFace model collection: [kitft/nla-models](https://huggingface.co/kitft)
- Inference code & documentation: [github.com/kitft/natural_language_autoencoders](https://github.com/kitft/natural_language_autoencoders)
- Associated publication: "Natural Language Autoencoders Produce Unsupervised Explanations of LLM Activations" (Transformer Circuits, 2026)

## See also

- [[sleeper_agent_probes]] — linear-probe methodology for reading internal state; the natural comparison point for NLAs as a higher-expressivity readout
- [[steering_eval_aware]] — evidence that eval-awareness has linear structure in activation space; complements the NLA finding that it also surfaces as readable text
- [[cot_faithfulness]] — NLA verbalisations vs. model CoT on the same inputs is a direct probe of unfaithfulness
- [[persona_vectors]] — same model class (Qwen-7B) and a related "internal-state direction" framing
- [[sandbagging]] — candidate phenomenon to point NLAs at: does the internal "I'm being evaluated" representation co-occur with capability suppression?
- [[alignment_faking]] — behavioural counterpart; alignment-faking is measured externally, NLAs offer an internal-state view of the same kind of context distinction
- [[beyond_linear_probes]] — broader methodological context for non-linear / higher-expressivity readouts of internal state
