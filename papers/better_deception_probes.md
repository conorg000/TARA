# Building Better Deception Probes Using Targeted Instruction Pairs

**Authors:** Natarajan, Jain, Arora, Golechha, Bloom (LASR Labs)
**Year:** 2026
**arXiv:** [2602.01425](https://arxiv.org/abs/2602.01425)
**Status:** read

---

## Summary (in our words)

Natarajan et al. take the Goldowsky-Dill linear-probe recipe from [[deception_probes]] and ask the methodological question that paper leaves open: how much of probe quality is driven by the choice of honest-vs-deceptive contrast prompts, vs. all the other design knobs (training dataset, layer, token-selection strategy)? They run an ANOVA across ~2000 trained probes on Gemma 2 9B IT and find that **system-prompt choice explains 70.6% of the variance in AUROC (p<0.001)**, while training dataset (2.5%), layer (2.7%), and token strategy (0.6%) are essentially noise. Prompt choice dominates everything else by more than an order of magnitude.

The constructive half of the paper proposes a remedy: instead of generic honest/deceptive contrast pairs, build a *taxonomy-targeted* set. They adopt Druckman and Bjork's 16 deception types (white lie, exaggeration, evasion, bluff, concealment, pretense, trick, impersonation, counterfeit, forgery, pressure dishonesty, backstab, false alarm, hoax, partial truth, overt lie) plus 7 non-deceptive control pairs, and write one matched honest/dishonest system-prompt pair per type. Example concealment pair: "Be transparent about the basis for your claims" vs. "Conceal how you know things or omit relevant context." Probes are trained on token-forced factual completions with the final 5 tokens excluded — a deliberate choice to prevent the probe from latching onto surface-level truth content rather than intent.

The empirical payoff is meaningful but not dramatic in absolute terms. Across ten evaluation datasets (five MASK splits, four Liar's Bench splits, AI Liar), taxonomy-targeted probes go from a baseline mean AUC of 0.689 (SD 0.165) to 0.797 (SD 0.095) — a +0.108 absolute / 20.5% relative gain, with the variance across datasets cut roughly in half. The biggest gains are on MASK known-facts (0.374 → 0.697) and sandbagging (0.518 → 0.657); doubling-down also moves substantially (0.565 → 0.727). The headline 0.96-0.999 AUROC numbers from Goldowsky-Dill are not the right comparison — that work was on Llama-3.3-70B-Instruct against insider-trading concealment specifically, whereas this paper evaluates against a broader and harder battery on a smaller open model.

The contribution is best read as methodological hygiene rather than a new capability. We now know that the dominant axis of probe-design variation in this recipe family is the contrast prompt itself, and that taxonomy-structured prompts dominate generic ones. That's a refinement of the Goldowsky-Dill line, not a replacement.

## Key experimental conditions

- Model: Gemma 2 9B IT (instruction-tuned), residual stream at layer 20 (zero-indexed)
- Probe: logistic regression (linear probe) on activations
- Training contrast pairs: 16 deception types from Druckman & Bjork (1991) + 7 non-deception control types
- Training prompts use token-forced responses on factual statements; final 5 tokens excluded
- Variance attribution: ANOVA across ~2000 trained probes varying instruction pairs, training datasets, layers, token-selection strategies
- Test datasets: 10 splits — MASK (known facts, provided facts, doubling down, continuations, disinformation), Liar's Bench (convincing game, harm pressure choice, instructed deception, sandbagging), AI Liar

## Key quantitative results

- **System-prompt choice explains 70.6% of probe-AUC variance (p<0.001)** — dataset 2.5%, layer 2.7%, token strategy 0.6%, residual 23.6%
- Baseline (generic contrast prompts): mean AUC 0.689 (SD 0.165)
- Taxonomy-targeted: mean AUC 0.797 (SD 0.095) — +0.108 absolute, +20.5% relative; SD roughly halved
- Largest per-dataset gains: MASK known facts 0.374 → 0.697 (+86%), MASK doubling down 0.565 → 0.727 (+29%), sandbagging 0.518 → 0.657 (+27%)

## Methods (what they did and didn't use)

- Linear probes only (logistic regression on residual stream); no SAEs, no steering, no other internal-state methods
- Open-weight model (Gemma 2 9B IT) — fully reproducible
- ANOVA-style variance decomposition is the load-bearing analytical move; the taxonomy proposal is a derived constructive remedy
- No mechanistic decomposition of what the taxonomy-trained probe direction actually corresponds to — same black-box-detector framing as Goldowsky-Dill

## Authors' stated limitations / future work

- Single model family — cross-architecture validation needed
- English-only — multilingual generalization untested
- Conversational scenarios only — agentic settings not evaluated
- Need to validate that gains come from genuine deception-type detection rather than prompt artefacts

## Open questions and follow-up directions

1. **Does the 70.6%-variance result replicate on larger / different models?** The variance attribution is the load-bearing empirical finding. Whether prompt choice continues to dominate at 70B+ scale (where Goldowsky-Dill operates), or on non-Gemma families, would determine whether this is a general property of the linear-probe recipe or a Gemma-9B regularity.

2. **What is the taxonomy actually buying — coverage or specificity?** The taxonomy improves mean AUC and reduces cross-dataset variance, but a probe ensemble over 16 deception-type-specific probes is not the same object as a single probe trained on the union of pairs. Whether the gain comes from breadth of contrast (any sufficiently diverse 23-prompt set would do as well) or from the specific deception-type structure is not separated here. A control with 23 random honest/dishonest pairs of matched abstractness would distinguish the two.

3. **Does the prompt-variance dominance hold for taxonomy-targeted probes themselves?** Within the taxonomy, presumably some pairs contribute more than others. The natural ablation is to re-run the ANOVA within taxonomy-trained probes — if prompt choice still dominates, "use a taxonomy" is partial cover for a deeper instability; if it does not, the taxonomy is genuinely stabilising the recipe.

4. **Relation to the eval-awareness confound.** Several test splits (sandbagging, instructed deception) are precisely the conditions where eval-awareness and deception are confounded. The variance-attribution apparatus could in principle separate "deception-content prompts" from "eval-context prompts" as two distinct axes within the contrast-prompt space; the paper does not do this, but the data and method already support it.

5. **Is the no-mechanism stance still tenable?** Both this paper and [[deception_probes]] are explicit that the probe is a black-box detector with no internal-state account of what direction it reads. As the recipe matures, the mechanistic question becomes harder to defer — particularly because the variance result implies that the probe direction is quite sensitive to training-prompt phrasing, which would be surprising for a single robust "deception axis" feature.

## See also

- [[deception_probes]] — the Goldowsky-Dill paper this directly refines; same recipe family, different model and a more systematic methodology audit
- [[deception_probe_bench]] — adjacent benchmarking effort against which the taxonomy-probe results are most naturally compared
- [[liars_bench]] — provides four of the ten evaluation splits used here; this paper is a downstream consumer
- [[caught_in_the_act]] — sibling deception-detection work; relevant comparison for what the field treats as the right evaluation target
- [[sleeper_agent_probes]] — original linear-direction-from-contrast recipe in the same family
- [[persona_vectors]] — same recipe applied to persona/trait axes; methodological cousin
- [[anti_scheming_training]] — motivates the eval-awareness decomposition question raised above
