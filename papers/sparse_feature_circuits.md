# Sparse Feature Circuits: Discovering and Editing Interpretable Causal Graphs in Language Models

**Authors:** Marks, Rager, Michaud, Belinkov, Bau, Mueller
**Year:** 2025 (ICLR; arXiv March 2024)
**arXiv:** [2403.19647](https://arxiv.org/abs/2403.19647)
**Status:** read

---

## Summary (in our words)

The paper takes the circuit-discovery program — find the subnetwork of a model that is causally responsible for a behaviour — and swaps the unit of analysis from polysemantic components (attention heads, MLP neurons) to SAE features. The trick is to treat SAE feature activations *and* the SAE reconstruction error as nodes in the model's computation graph, so the analysis degrades gracefully when the SAE fails to capture some piece of computation. Importance per node and per edge is approximated by attribution patching (first-order Taylor) or, where that under-estimates, by integrated gradients with N=10 steps. Thresholding on absolute indirect effect gives a sparse causal graph of features.

The headline empirical claim is that these feature circuits are dramatically smaller and more interpretable than neuron-level circuits while preserving most of the relevant model behaviour. On subject-verb agreement, ~100 features (Pythia-70M) or ~500 features (Gemma-2-2B) recover the majority of model performance, against ~1500 neurons or ~50,000 neurons respectively. The discovered features label cleanly — e.g. a pathway of features that detect main-subject number and then promote matching verb forms. They also run the pipeline at scale: cluster (context, next-token) pairs into thousands of behavioural subcorpora à la Michaud et al., then discover a circuit per cluster, producing a browsable library of circuits at feature-circuits.xyz.

The application that makes the paper load-bearing for our area is SHIFT — Spurious Human-Interpretable Feature Trimming. Take a profession classifier trained on BiasInBios where gender perfectly predicts the label (male=professor, female=nurse). Discover the feature circuit for the classifier. Have a human read off feature labels and zero-ablate the ones that look task-irrelevant (gender-coded language). Optionally retrain on the original biased data with those features clamped to zero. On a balanced test set this takes Pythia profession accuracy from 61.9% to 93.1% and worst-group accuracy from 24.4% to 89.0%; Gemma goes from 67.7% to 95.0% on profession and 18.2% to 92.9% on worst-group. Gender accuracy drops to near-chance (~52%). 55 ablated features on Pythia, 43 on Gemma. The intervention requires no disambiguating labels — it's "human reads SAE feature names" doing the work.

What's empirically tight: the circuit sizes, the faithfulness numbers, the BiasInBios deltas. What's framing-dependent: the claim that the discovered features are "interpretable" rests on human labeling, which the authors flag is qualitative and annotator-dependent; and that the circuits are "causal" rests on the indirect-effect approximations, which the authors validate against ground truth where they can but cannot guarantee globally. The SHIFT result is real and large but depends on a human in the loop who can recognise spurious features by their labels.

## Key experimental conditions

- Models: **Pythia-70M** (with custom-trained ReLU SAEs, d_SAE = 64×d) and **Gemma-2-2B** (with public Gemma Scope Jump-ReLU SAEs, d_SAE = 8×d). No experiments on larger Pythia variants.
- Subject-verb agreement: four task variants (Simple, Within RC, Across RC, Across PP); contrastive input pairs differing only in subject number.
- BiasInBios: profession classifier trained on a deliberately biased subset (gender perfectly predicts label); evaluated on a balanced test set after SHIFT.
- Automatically-discovered behaviours: corpus partitioned into thousands of clusters via (context, next-token) gradients/SAE activations; a circuit discovered per cluster, using metric m = -log P(y|x).

## Key quantitative results

- **Subject-verb agreement (faithfulness):** ~100 features (Pythia) and ~500 features (Gemma) recover the majority of performance; circuit sizes ~15× and ~100× smaller than neuron-level equivalents respectively.
- **BiasInBios profession accuracy (balanced test):** Pythia 61.9% → 93.1% after SHIFT+retrain; Gemma 67.7% → 95.0%.
- **Worst-group accuracy:** Pythia 24.4% → 89.0%; Gemma 18.2% → 92.9%.
- **Gender accuracy collapses to chance:** 87.4% → 52.0% (Pythia), 81.9% → 52.4% (Gemma).
- **SHIFT footprint:** 55 features ablated (Pythia), 43 features ablated (Gemma).
- **Behaviour library:** thousands of automatically-discovered circuits released; rediscovers succession and induction features previously found at the attention-head level.

## Methods (what they did and didn't use)

- SAE-feature circuits — feature activations *and* SAE reconstruction errors are both nodes in the causal graph, so error-routed computation remains visible as an uninterpretable node rather than silently lost.
- Indirect-effect estimation via attribution patching (first-order) and integrated gradients (10-step) for both node and edge importance; faithfulness measured as fraction of behaviour recovered, completeness via complement-circuit performance.
- Behavioural clustering pipeline borrowed from Michaud et al. 2023 to produce subcorpora for scalable circuit discovery.
- Open-weights only (Pythia, Gemma); both SAE suites and circuit-discovery code released. Reproducibility is solid.
- Does not address SAE quality / feature-splitting / polysemanticity-within-features — those are treated as out-of-scope; "scalably training better SAEs is an active area of research".
- No comparison to non-SAE interpretability baselines on the SHIFT task (e.g. probing for gender and projecting it out).

## Authors' stated limitations / future work

- Method depends on having SAEs for the target model; SAE training is a large (but one-time) upfront cost.
- Components not captured by SAEs remain uninterpretable; the error node makes this visible but doesn't resolve it.
- Feature labelling is qualitative and may vary across annotators.
- Most circuit evaluation is qualitative — evaluating circuits without a downstream task is hard.
- No explicit future-work section; the implicit frontier is scaling SAEs and the discovery pipeline.

## Open questions and follow-up directions

1. **Generality of SHIFT beyond gender-in-BiasInBios.** The result is striking because gender is salient, lexically marked, and easy to label as spurious from feature names. Whether SHIFT works on spurious correlations that are subtler (stylistic, syntactic, dataset-artifactual) or that humans can't pre-name is the load-bearing open question — the human-in-the-loop step is doing real work that the method doesn't quantify.
2. **Robustness of feature labels to SAE choice.** The labels driving SHIFT depend on which SAE was trained on which model with which width; feature-splitting and dictionary differences could route the same concept through differently-labelled features. The paper does not characterise label stability across SAE training runs or widths.
3. **Scaling.** Experiments stop at Gemma-2-2B. Whether circuit sizes stay tractable, faithfulness stays high, and feature labels stay readable at frontier scale is open — and the SHIFT cost (humans inspecting ~50 features) scales with circuit size, not parameter count, so the answer matters operationally.
4. **Behaviour-discovery dependence.** The thousands-of-circuits library depends on the (context, next-token) clustering, which is itself a choice — finer/coarser clustering would produce different behaviours and circuits. Whether the discovered behaviours carve nature at the joints or just reflect the clustering hyperparameters is not tested.
5. **Edge attribution vs node attribution.** The pipeline thresholds nodes and edges separately with similar linear approximations. How much edge-level structure (vs. just node-level "these features matter") is load-bearing for downstream applications like SHIFT is unclear — SHIFT itself only uses the node set.

## See also

- [[scaling_monosemanticity]] — sibling SAE work; scales the dictionary-learning side rather than the circuit-discovery side.
- [[model_diff_tool]] — uses dedicated feature crosscoders for a different SAE-based application (cross-model diffing); shares the "humans read feature labels" workflow cost.
- [[natural_language_autoencoders]] — alternative interpretable-unit-of-analysis (NL token sequences instead of SAE features); the NLA paper finds SAEs do not help on its auditing task, a useful contrast to SHIFT's success.
- [[auditing_hidden_objectives]] — used SAEs as one of several methods to surface a hidden reward-model-sycophancy objective; provides a real-world test case for SHIFT-style human-in-the-loop SAE-feature reasoning.
- [[weight_sparse_transformers.md|weight_sparse_transformers]] — competing route to interpretable circuits via weight sparsity rather than activation-space dictionaries; opposite trade-off (training-time cost vs. post-hoc SAE cost).
