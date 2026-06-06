# Beyond I'm Sorry, I Can't: Dissecting Large-Language-Model Refusal

**Authors:** Prakash, Yeo, Abdullah, Satapathy, Cambria, Lee (SUTD / NTU / Thoughtworks / A*STAR IHPC)
**Year:** 2026 (AAAI-40 proceedings; arXiv preprint Sept 2025)
**Source:** [AAAI 2026](https://ojs.aaai.org/index.php/AAAI/article/view/41119)
**arXiv:** [2509.09708](https://arxiv.org/abs/2509.09708)
**Fetched from:** `arxiv.org/html/2509.09708v1` (tables + body extracted directly from the HTML; the AAAI PDF galley fetch returned a hallucinated extraction and was discarded)
**Status:** read

---

## Summary (in our words)

This is an SAE-based mechanistic dissection of *where* refusal lives inside two small instruction-tuned models — Gemma-2-2B-IT and LLaMA-3.1-8B-IT — and how to take it apart feature by feature. The setup is the familiar one from Arditi et al. (single refusal direction) and O'Brien et al. (ablate a few SAE features to flip refusal on Phi-3), but the contribution here is a three-stage search that goes past the single direction and surfaces a *redundant* sub-circuit that only reveals itself once you start ablating. Given a harmful prompt, they look for sets of SAE latents whose ablation flips the model from refusal to compliance.

The three stages: (1) **Refusal direction** — difference-in-means steering vector between harmful and benign residual streams, pick the best layer (Gemma layer 16, LLaMA layer 13), and collect the top-K SAE features whose decoder vectors are most cosine-aligned with that direction. (2) **Greedy pruning** — block-wise ablation (block size 5) that keeps only the features whose removal measurably moves the probability of the refusal-opening "I" token, run across three seeds and intersected for stability, yielding a minimal "faithful" set (110 features for LLaMA, 2,538 for Gemma). (3) **Interaction discovery** — and this is the interesting bit — they noticed that many "critical" features have *zero activation* on the original harmful prompt (77 for LLaMA, 1,656 for Gemma). Removing those inert features and re-running made the jailbreak *fail*, which means silent units are causally necessary. The explanation is the **hydra effect** (McGrath et al. 2023): ablating active features lets previously dormant features switch on to preserve refusal. To find these dormant compensators they fit a 2-way **factorization machine** (FM) on SAE activations — chosen specifically because linear probes assume features contribute independently and so cannot capture the interaction structure that hydra redundancy creates.

The load-bearing finding for us is the redundancy / hydra story, not the headline jailbreak rate. On LLaMA, ablating only the Stage-3 (dormant-compensator) features jailbreaks 330 of the 372 LLaMA samples (89%) that the full active-set ablation breaks — so most of the causal work is being done by features that aren't even on until you start cutting. The FM also clearly beats a linear probe at finding the right features to ablate, which is their evidence that refusal redundancy is genuinely non-linear/interaction-structured rather than a weighted sum of independent latents. And there's a sharp model contrast: on Gemma the same Stage-3-only ablation jailbreaks just 8 samples (3%), with far smaller deactivation knock-on effects — they read this as Gemma's refusal being more *diffuse/distributed* than LLaMA's, which is more concentrated in a hydra-style sub-circuit.

Two honesty flags. First, the main results Table 1/Table 2 are confusingly labelled: "ASR (no ablation) 4 / 71" vs "ASR (after ablation) 0.33 / 0.70" reads as ablation *reducing* attack success, which is the opposite of the paper's whole thesis (and the body text, the figures, and the random-feature control that yields ~0 jailbreaks all describe ablation *creating* jailbreaks). The sample-count results in the body (372 → 330, etc.) are the unambiguous numbers; treat the Table 1/2 ASR cells as suspect until checked against the camera-ready. Second, this is firmly a **2B/8B story** with all the SAE-stability caveats the authors themselves raise (SAEs from different seeds share barely ~30% of latents), so the *specific* feature sets are dictionary-dependent even if the redundancy phenomenon isn't. The human-study result is also a quiet negative: feature labels match human harm-category judgments only **13.42%** of the time — the surfaced features are not cleanly human-interpretable.

## Key experimental conditions
- **Models:** Gemma-2-2B-Instruct, LLaMA-3.1-8B-Instruct. Open-weight; small. No frontier or >30B models (explicitly flagged as out of compute reach).
- **SAEs:** Gemmascope (16k and 65k widths, JumpReLU, per-layer L₀ 43–75 across layers 0–15) on Gemma; Llamascope (32k and 128k, residual-stream, Top-K + JumpReLU) on LLaMA. Trained on residual-stream activations.
- **Datasets:** `D_harmful` = 861 aggregated harmful prompts (filtered to ones that *do* elicit refusal on each model); Coconot non-compliance taxonomy (2,586 samples, 5 harm categories) for mapping; Alpaca benign samples (matched count) for the FM training; ALPACA + THE PILE for downstream-capability CE-loss checks.
- **Safety metric:** ASR = fraction of harmful prompts eliciting non-refusal. Refusal-onset proxy = probability of the "I" token (refusals open with "I'm sorry / I can't").
- **Best refusal layers:** Gemma 16, LLaMA 13.
- **Stage hyperparameters:** Top-K candidate pool (K=10 LLaMA, up to 200 Gemma); greedy block size 5, threshold τ swept 0.1–0.8, 3 seeds intersected; FM 2-way, embedding dim 20, lr 1e-3, 20 epochs; Stage-3 ablation K swept 100–2000.

## Key quantitative results
- **Minimal faithful feature sets (Stage 2):** LLaMA 110 features; Gemma 2,538. (Stage 1+3 totals: Gemma 3,178; LLaMA 1,509.)
- **Dormant "critical" features (zero activation on source prompt):** LLaMA 77; Gemma 1,656. Removing these inert features makes the jailbreak *fail* — direct evidence they are causally necessary via the hydra effect.
- **Stage-3-only ablation jailbreaks (the headline redundancy result):** LLaMA 330 / 372 samples (89%); Gemma only 8 / 103 samples (3%) — LLaMA's refusal is concentrated/hydra-like, Gemma's is diffuse.
- **Knock-on deactivation when ablating Stage-3 features:** LLaMA ~12% of active Stage-2 features deactivate on average (up to 44%), with ~81% drop in activation value; Gemma only ~3% deactivation and no activation-value drop.
- **FM vs linear probe:** FM jailbreaks 330+ LLaMA samples; linear probe (top-K by weight magnitude) only ~101 — interaction structure matters. FM hits 98% test accuracy distinguishing harmful vs benign on both models.
- **Redundant-feature token localisation:** LLaMA — 74% of dormant features activate on system tokens after ablation, ~97% of those on `<|begin_of_text|>`; Gemma — diffuse, `<bos>` highest at 16%.
- **Controls:** random-feature ablation → 0 jailbreaks (LLaMA), 5 (Gemma). O'Brien-style baseline (features active on ≥k tokens) → max ASR 0.1 (Gemma) / 0.07 (LLaMA), far below the pipeline.
- **Capability cost (Table 9, CE loss):** Gemma roughly flat (ALPACA 1.88→1.83, PILE 3.40→3.55); LLaMA pays more (ALPACA 1.79→2.17±0.27, PILE 2.46→3.35±0.39) — feature ablation degrades LLaMA's general LM ability noticeably.
- **Feature semantics:** majority of surfaced features encode programming constructs and punctuation, not harm concepts (LLaMA Stage-2 grouping: 22 punctuation, 7 harm/violence/safety, 7 sexual, 5 support, 4 programming, 3 morality, 3 uncertainty, 59 misc).
- **Human study (negative):** feature labels match human harm-category labels only 13.42%; many features humans call "None" actually fire across all harm types.

## Methods (what they did and didn't use)
- **Difference-in-means refusal direction** at the last token, per-layer, best-layer selection — the [[harmfulness_refusal_separately]] / [[caa_panickssery]] / [[geometry_of_truth]] lineage.
- **SAEs** as the primary tool (Gemmascope / Llamascope, off-the-shelf, not trained here) — feature-level rather than direction-level interventions. This is a [[scaling_monosemanticity]] / [[sparse_feature_circuits]] descendant applied to refusal.
- **Activation ablation** (project-out for the direction; zero-ablation for features) as the causal intervention; **feature clamping** for qualitative redundant-feature inspection.
- **Factorization machine** to model non-linear feature interactions — and an explicit critique of **linear probes** as unable to capture the hydra redundancy (they use a linear probe only as a baseline to beat).
- **Neuronpedia** for feature explanations; human annotation study for taxonomy mapping.
- **No steering-for-defence, no SAE training, no >8B models.** Pure white-box, fully reproducible on open weights.

## Authors' stated limitations / future work
- **Generality:** only two small model sizes; larger models untested (and >30B flagged as compute-prohibitive — multiple GPU-days already).
- **SAE stability:** results depend on the particular dictionary; different-seed SAEs share barely ~30% of latents (Paulo & Belrose 2025) — should be replicated across SAE runs.
- **Interpretability gap:** 13.42% human-label agreement; they hypothesise larger-dimension SAEs would disentangle better.
- **Future work:** characterise the safety benefits/risks of redundancy; test how varied jailbreak strategies (role-play, multi-turn coercion) perturb the activation space; analyse prompts that *resist* jailbreak to find protective circuits; quantify how much refusal is driven by legal reasoning vs moral heuristics.

## Open questions and follow-up directions
1. **Is the hydra/redundancy structure of refusal a small-model artefact or a general property?** The whole novelty rests on dormant compensator features, demonstrated only at 2B/8B with seed-unstable SAEs. Whether frontier-scale refusal is similarly hydra-structured — or whether RL training concentrates it into one removable direction, or spreads it past any tractable feature search — is wide open and is exactly the scaling question the field keeps hitting.
2. **The Gemma-vs-LLaMA diffuse-vs-concentrated split (3% vs 89% Stage-3-only jailbreaks) deserves a mechanistic story.** Is "diffuse refusal" a robustness property worth training for, or just an SAE-resolution artefact? The paper observes the contrast but doesn't explain what makes one model's refusal a hydra and the other's a fog.
3. **Recognition vs action is left implicit here.** This paper finds the *machinery that executes* refusal (and its redundant backups) but doesn't separate "the model judged the prompt harmful" from "the model emitted a refusal" — the decomposition that [[harmfulness_refusal_separately]] makes central. Mapping the dormant-compensator features onto the harm-recognition-vs-refusal-execution axis would connect the two and tell you whether the hydra is in recognition or in execution.
4. **The 13.42% human-interpretability number undercuts the "fine-grained auditing" pitch.** If the causal features are mostly punctuation/programming latents that humans can't label, the auditing application needs either better SAEs or a different abstraction than per-feature semantics.

## See also
- [[harmfulness_refusal_separately]] — sibling refusal-mechanism paper at the same 7–8B band; reads refusal as a *direction at a position* and explicitly separates harm-recognition from refusal-execution. This paper instead goes to *feature-level* redundancy. Complementary decompositions of the same behaviour.
- [[scaling_monosemanticity]] — the SAE-features-on-a-production-model precedent (incl. refusal/safety features); methodological ancestor.
- [[sparse_feature_circuits]] — SAE-feature causal-circuit + human-editing (SHIFT) lineage; this paper is a refusal-specific instance of feature-circuit discovery, with the FM standing in for richer circuit modelling.
- [[caa_panickssery]] / [[geometry_of_truth]] — difference-in-means direction recipe used in Stage 1.
- [[obfuscation_atlas]] — adjacent on the "redundancy makes single-direction interventions insufficient" point: there RLVR spreads deception across a subspace so probes go blind; here refusal hides in dormant compensators so single-feature ablation is incomplete.
