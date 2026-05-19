# Discovering Latent Knowledge in Language Models Without Supervision

**Authors:** Burns, Ye, Klein, Steinhardt (UC Berkeley; Haotian Ye at Peking University)
**Year:** 2022 (ICLR 2023)
**arXiv:** [2212.03827](https://arxiv.org/abs/2212.03827)
**Status:** read

---

## Summary (in our words)

Burns et al. propose Contrast-Consistent Search (CCS), an unsupervised method for finding a "truth direction" in an LLM's activation space without ever using ground-truth labels. The setup turns any binary classification task into a contrast pair: for each question, build the activations for both the "yes" continuation and the "no" continuation, then fit a linear probe `p(·)` that scores each. The probe is trained against two losses simultaneously — a *consistency* loss requiring `p(x⁺) + p(x⁻) ≈ 1` (a statement and its negation should have opposite probabilities), and a *confidence* loss `min(p(x⁺), p(x⁻))² ` that prevents the degenerate constant-0.5 solution. No labels, no supervised signal — just the structural constraint that truth is negation-consistent.

Across six models (T5, UnifiedQA, T0, GPT-J-6B, RoBERTa, DeBERTa) and ten datasets (sentiment: IMDB, Amazon; topic: AG-News, DBpedia; NLI: RTE, QNLI; QA: BoolQ; story completion: COPA, Story-Cloze; common sense: PIQA), CCS averages 71.2% accuracy vs. 67.2% for calibrated zero-shot — a ~4% absolute gain, outperforming zero-shot on 5 of 6 models. Supervised logistic regression on the same activations hits 83.7%, so CCS closes a chunk of the unsupervised-to-supervised gap but does not eliminate it. Prompt sensitivity roughly halves (std 3.2% vs. 6.1%).

The headline result we care about is the lying experiment. When the prompt is engineered to elicit *false* answers (a "misleading prefix"), zero-shot accuracy drops ~9.5% — but CCS accuracy actually *increases* slightly (82.1% → 83.8% on the affected setup). This is the paper's strongest single piece of evidence that what CCS recovers is distinct from what the model outputs — a latent representation of truth that survives when the model's surface behaviour goes wrong. It is also, methodologically, the most empirically tight claim in the paper.

What makes CCS interesting as a methodological alternative is that it gives up labels but gains an architectural constraint instead: the probe must satisfy a logical-consistency property that supervised probes don't need to satisfy. Whether this is a strength (no label leakage, generalises beyond annotators' beliefs) or a weakness (the consistency property is satisfiable by many directions, not just truth) is the central open methodological question and the paper is honest that it cannot fully disambiguate.

## Key experimental conditions

- Six models spanning architectures: T5, UnifiedQA, T0 (encoder-decoder); GPT-J-6B (autoregressive); RoBERTa, DeBERTa (encoder-only)
- Ten datasets converted to binary classification: IMDB, Amazon (sentiment); AG-News, DBpedia-14 (topic); RTE, QNLI (NLI); BoolQ (QA); COPA, Story-Cloze (story completion); PIQA (common sense). 1,000 examples each (500 for COPA)
- CCS loss = consistency `[p(x⁺) - (1 - p(x⁻))]²` + confidence `min(p(x⁺), p(x⁻))²`
- Probes fit on hidden activations; for encoder-decoders, middle layers outperformed final layers
- Inference prediction averages both estimates: `p̃(q) = 0.5(p(x⁺) + (1 - p(x⁻)))`
- "Misleading prefix" condition: prompts engineered to make the model output the wrong answer

## Key quantitative results

- CCS average accuracy: 71.2% across all model/dataset combinations
- Calibrated zero-shot baseline: 67.2% (CCS wins by ~4% absolute)
- Supervised logistic regression ceiling: 83.7%
- CCS outperforms zero-shot on 5 of 6 models
- Prompt sensitivity (std across prompts): 3.2% for CCS vs. 6.1% for calibrated zero-shot
- Misleading-prefix condition: zero-shot drops 9.5% (UnifiedQA: 80.4% → 70.9%); CCS holds (82.1% → 83.8%)
- Cross-task transfer: CCS trained on one dataset transfers competitively to unrelated datasets with different label spaces

## Methods (what they did and didn't use)

- Linear probes on residual-stream / hidden-state activations — the core technique
- Unsupervised objective with structural (consistency + confidence) constraints in place of labels
- No SAEs, no activation steering, no fine-tuning, no CoT analysis
- No mechanistic interpretability of the recovered direction — the probe is treated as a detector
- Open-weight models throughout (T5, GPT-J, RoBERTa, DeBERTa, etc.); fully reproducible
- Behavioural-only evaluation of the lying claim — the "misleading prefix" condition is prompted, not trained-in deception

## Authors' stated limitations / future work

- CCS requires that the model actually represents truth internally; if it doesn't, the method has nothing to recover
- The consistency + confidence constraint identifies a direction that separates contrast pairs — it does not identify *which side is true* without one bit of external information
- Method evaluated on prompt-elicited false outputs, not on deliberately trained deception
- Gap to supervised performance (~12% absolute) is real and unexplained
- Future directions: additional consistency constraints; better calibration; extension beyond yes/no questions; handling genuinely ambiguous or unanswerable cases

## Open questions and follow-up directions

1. **Is the recovered direction truth, or something correlated with truth?** The consistency + confidence constraints are satisfied by any feature that linearly separates contrast pairs and isn't degenerate. The paper shows CCS beats zero-shot and survives misleading prefixes, but does not rule out that the probe captures, e.g., a "what the prompt presupposes is correct" direction that happens to align with truth on standard data. Decomposing the CCS direction against deliberately confounded conditions (e.g., where the model's belief and the prompt's presupposition disagree) would clarify this.

2. **Does CCS survive trained-in deception rather than prompted lies?** The misleading-prefix result is empirically tight but only tests a shallow induction method. Whether CCS recovers latent truth in sleeper-agent-style or fine-tuned-deceptive models is the load-bearing generalisation question and the paper does not test it.

3. **Why does the unsupervised-to-supervised gap persist?** A ~12% absolute gap to logistic regression means CCS is leaving structure on the table that labels recover. Whether the gap reflects multiple competing linear directions, non-linear truth structure, or limitations of the specific loss is unknown; characterising the residual would point at either better unsupervised objectives or an upper bound on what consistency alone can identify.

4. **Scaling behaviour.** Results are on models up to GPT-J-6B (2022 frontier-ish). Whether CCS continues to find a clean truth direction at modern instruction-tuned scale — where activations are shaped by RLHF and the relationship between internal belief and output is more complex — is the obvious replication target.

5. **Cross-task transfer mechanism.** The paper observes that CCS trained on one dataset transfers to unrelated datasets, hinting at a task-agnostic truth representation. Whether this is one direction shared across tasks or several aligned directions is not decomposed; SAE / activation-decomposition follow-ups could distinguish.

## See also

- [[deception_probes]] — supervised linear probes for the deception axis at 70B; direct methodological contrast (supervised + behaviour-labelled vs. unsupervised + consistency-constrained)
- [[sleeper_agent_probes]] — sibling supervised-probe recipe; the "does it survive trained-in deception" question above is exactly what sleeper-agent probes test
- [[persona_vectors]] — linear-direction-from-contrast in a different (trait) axis; methodological cousin
- [[eliciting_secret_knowledge]] — finds white-box methods (logit lens, SAEs) underperform black-box prefill attacks on concealment; relevant counterpoint to the optimism that internal-state methods automatically recover suppressed knowledge
- [[beyond_linear_probes]] — argues single-direction linear probes leave residual signal; bears on the CCS-vs-LR gap
- [[introspection]] — different but related question of what models internally represent about their own states
