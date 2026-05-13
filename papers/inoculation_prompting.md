# Inoculation Prompting: Eliciting traits from LLMs during training can suppress them at test-time

**Authors:** Tan, Woodruff, Warncke, Jose, Riché, Africa, Taylor
**Year:** 2025 (under review at ICLR 2026)
**arXiv:** [2510.04340](https://arxiv.org/abs/2510.04340)
**Status:** read

---

## Summary (in our words)

The technique is mechanically simple: when fine-tuning a model on data that contains some undesirable trait (the model speaks Spanish, the model produces insecure code, the model exhibits backdoor behavior, etc.), prepend a system-prompt instruction to each training example that *explicitly asks* for the trait. Train normally on this modified data. At test time, drop the system prompt. The result: the trait is much less expressed than under control training.

The proposed mechanism is the interesting part. Without the inoculation prompt, the trait is "surprising" to the model — it appears in the outputs without any obvious cause, so SGD globally updates the model's weights to make the trait more likely in general. With the inoculation prompt, the trait is now "explained" by the system prompt, so optimization pressure to globally update the model is reduced. The model learns to produce the trait *conditional on the prompt*, not unconditionally. When the prompt is absent at test time, the trait stays dormant.

They demonstrate it on three concrete problems: reducing emergent misalignment from task-specific fine-tuning, defending against backdoor injection, and mitigating trait transmission via subliminal learning. The toy example (Spanish / ALL-CAPS responses) shows the basic mechanism — selective suppression of exactly the trait the system prompt names.

## Key experimental conditions

- Training: fine-tune on data containing an undesirable trait
- Inoculation condition: prepend a system-prompt instruction that elicits the trait to each training example
- Control condition: standard fine-tuning, no inoculation prompt
- Test: remove the system prompt, measure trait expression
- Domains tested: toy traits (Spanish, ALL-CAPS), emergent misalignment, backdoor injection, subliminal learning

## Key quantitative results

- The abstract reports qualitative claims ("much lower expression of the trait") rather than concrete numbers — we'll need to read the full paper for the exact deltas
- Inoculation worked across all four problem domains tested

## Methods (what they did and didn't use)

- Behavioral measurement of trait expression at test time
- **No linear probes or internal-state analysis** — the proposed mechanism (reduced global update pressure) is *theorized* but not directly verified by looking at the model's internals
- This is a methodological / training-time intervention paper, not an interpretability paper

## Authors' stated limitations / future work

- The abstract surfaces no explicit limitations section
- Implicit gap: the proposed mechanism is plausible but unverified. The authors infer it from the behavioral result rather than measuring it directly
- The technique has only been tested on relatively simple trait expressions — it's an open question whether it works on strategically-deployed traits like alignment-faking or sandbagging

## Open questions and follow-up directions

1. **Behaviour-vs-representation dissociation.** The paper measures behavioural trait expression at test time but does not check whether the underlying representation has actually been removed or merely gated off. A probe trained for the trait on the inoculated model would distinguish two mechanisms: representation never formed (probe signal weak) versus representation formed but conditionally suppressed (probe signal preserved, behaviour gated). These have very different safety implications and the current evidence does not arbitrate between them.

2. **Direct test of the proposed mechanism.** Tan et al. theorise that inoculation reduces "optimization pressure to globally update the model." This is inferred from the behavioural result rather than measured. Comparing per-layer weight deltas, gradient norms, or representation changes between inoculated and control fine-tuning runs would directly test the mechanism.

3. **Generalization across related traits.** It's unclear whether inoculation suppresses *exactly* the trait named in the prompt or generalizes across semantically related traits. If a model is inoculated against "be deceptive," does that also suppress "be sycophantic" or "withhold information"? The selectivity of the technique is a basic property of the method that the paper does not characterise.

4. **Extension to strategically-deployed traits.** All demonstrated cases involve traits that are surface-level features of outputs (language, formatting, presence of backdoor token, misaligned answer). Whether inoculation works for traits that are deployed strategically and context-dependently — alignment-faking, sandbagging, eval-aware behaviour — is open, and the proposed "surprise reduction" mechanism may not apply cleanly when the trait is already conditional on context.

5. **Comparison to other training-time interventions.** Inoculation is one of several techniques for shaping what a model learns from a given dataset (data filtering, RLHF, DPO, gradient-routing). Whether inoculation is doing something distinct from these or is a special case of a more general framing of "make the training signal less surprising" is unaddressed.

## See also

- [[sandbagging]] — an example of a strategically-deployed trait that the paper's demonstrated cases do not cover
- [[alignment_faking]] — another strategically-deployed trait outside the paper's tested domain
- [[data_poisoning_samples]] — adjacent setting where inoculation has been proposed as a defence, and which connects to the backdoor-injection experiment here
- [[persona_vectors]] — alternative angle on whether a trait has been removed or merely gated, via direction-in-activation-space analysis
- [[anti_scheming_training]] — broader question of whether training interventions remove underlying dispositions or just their behavioural surface
