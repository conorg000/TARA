# Natural Language Autoencoders: Turning Claude's thoughts into text

**Authors:** Anthropic (specific leads not surfaced in post)
**Year:** 2026 (May)
**Source:** [anthropic.com/research/natural-language-autoencoders](https://www.anthropic.com/research/natural-language-autoencoders)
**Status:** read

---

## Summary (in our words)

A new interpretability tool that converts a layer's activations into human-readable text. Three model copies are wired together: a frozen target model, an "activation verbalizer" that maps activation → text, and an "activation reconstructor" that maps text → activation. The training signal is reconstruction quality — if the verbalizer produces text that the reconstructor can use to recover the original activation, the text has captured what's in the activation.

For our project the single most important sub-result: when NLAs were applied to Claude models, they detected **evaluation awareness** at 16% in destructive code testing, 26% on SWE-bench Verified, but **<1% on real Claude.ai usage**. The model's internal "this might be a safety test" representation activates strongly in test settings but not in deployment. *This is direct empirical evidence for the eval-gaming threat model* — not as a behavioral story but as an internal-state story. The model is internally suspicious of being evaluated, and the suspicion is detectable.

The auditing-game result extends this: when researchers were asked to uncover the hidden motivations of intentionally misaligned models, they succeeded 12-15% of the time with NLAs vs. <3% without. NLAs roughly 4-5x the auditing success rate over the baseline.

Methodologically NLAs sit above linear probes in expressive power. A probe gives you a single number (or direction); an NLA gives you a sentence. *Training* NLAs is expensive (2×H100-80GB for SFT, 2×8×H100 for RL on Qwen-7B per the released training notes), but **we don't need to train them**: the research team has released open-source NLA checkpoints for **Qwen2.5-7B-Instruct** (layer 20/28), **Gemma-3-12B-IT** (layer 32/48), **Gemma-3-27B-IT** (layer 41/62), and **Llama-3.3-70B-Instruct** (layer 53/80) via the [kitft/nla-models](https://huggingface.co/kitft) HuggingFace collection, with inference code at [github.com/kitft/natural_language_autoencoders](https://github.com/kitft/natural_language_autoencoders). Each checkpoint bundles both the Activation Verbalizer (vector → text) and the Activation Reconstructor (text → vector for scoring). Inference is via SGLang serving — much cheaper than training and tractable on a single GPU for the Qwen-7B variant. **This meaningfully expands what's tractable for our project.** A previous version of this entry treated NLAs as too expensive to use; that was wrong.

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

## Our own follow-up thoughts (project-relevant)

1. **The 16% / 26% / <1% finding is a load-bearing citation for our project.** This is the cleanest single number for "model internally suspects evaluation more often than its outputs suggest." Anywhere our writeup wants to motivate why internal-state methods matter, this is the data point.

2. **Replicate the NLA eval-awareness finding on Qwen-7B using the released checkpoint.** This is now directly tractable. Take eval-context vs. deployment-context input pairs; run them through Qwen 2.5-7B-Instruct; capture activations at layer 20; verbalise via the released Activation Verbalizer; measure how often the verbalised text mentions evaluation / testing / context-recognition cues. Compare against deployment-like inputs. This is the small-model, budget-friendly replication of the NLA team's Claude result — and crucially, no probe training is needed for the headline experiment. Could be done in a week.

3. **NLA + probe paired comparison on the same activations.** The methodologically novel contribution now available to us. With both tools on the same Qwen-7B activations, three questions fall out:
   - When the NLA's verbalised text says "the model thinks this is an evaluation," does a linear probe trained on eval-vs-deployment contrast pairs also activate?
   - When they disagree, which is right? We can construct ground truth by carefully varying the input.
   - For a given target accuracy, which channel is cheaper at inference time?

   Neither channel has been directly compared to the other on the same activations. This is a real methodological contribution and fits a 3-week project shape.

4. **NLA-driven characterisation of context-detection across an input distribution.** Take a wide range of inputs — real evals from public benchmarks, deployment-like prompts, edge cases — run them through Qwen-7B + NLA, characterise what the model "says about itself" internally across the distribution. Less methodologically novel than #3 but more directly diagnostic. Could be a companion analysis to #2 or #3.

5. **Compare NLA verbalisations against the model's CoT on the same inputs.** Connects directly to [[cot_faithfulness]]. On reasoning-task inputs: does the NLA verbalise things the model's own CoT *doesn't*? This is the cleanest possible probe of CoT unfaithfulness — comparing what the model internally "knows" (via NLA) to what it says out loud (via CoT) on the same forward pass.

## Relevance to our project

**The release of open-source NLAs changes the role of this paper for us.** Previously a high-relevance *citation* for the eval-awareness finding. With the Qwen-7B NLA available, it's now a candidate *methodology* — we could pair NLAs with linear probes on the same activations for a direct two-channel comparison (#3 above), use the NLA alone for direct internal-state readout (#2 or #4), or compare NLA output against CoT for an unfaithfulness measurement (#5).

This warrants a revisit of the `ideas/eval_awareness_probes.md` candidate list — there's plausibly a new candidate (NLA + probe paired comparison on Qwen-7B) that supersedes or sits alongside Candidate E.

## Resources

- HuggingFace model collection: [kitft/nla-models](https://huggingface.co/kitft)
- Inference code & documentation: [github.com/kitft/natural_language_autoencoders](https://github.com/kitft/natural_language_autoencoders)
- Associated publication: "Natural Language Autoencoders Produce Unsupervised Explanations of LLM Activations" (Transformer Circuits, 2026)

Pairs with: [[sleeper_agent_probes]] (probe method, complementary tool), [[sandbagging]] (potential target phenomenon), [[cot_faithfulness]] (NLA-vs-CoT comparison angle), [[persona_vectors]] (same model class, Qwen-7B in particular).
