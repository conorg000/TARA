# Truth is Universal: Robust Detection of Lies in LLMs

**Authors:** Lennart Bürger, Fred A. Hamprecht, Boaz Nadler (Heidelberg / Weizmann)
**Year:** 2024 (NeurIPS 2024)
**arXiv:** [2407.12831](https://arxiv.org/abs/2407.12831)
**Status:** read

---

## Summary (in our words)

Prior work (Azaria & Mitchell, Marks & Tegmark) had argued that LLMs encode truthfulness along a single linear direction in residual-stream space. The empirical wart on that story was negation: a probe trained on affirmative statements ("Madrid is in Spain") generalised poorly to negated ones ("Madrid is not in Germany"). Bürger et al. argue the 1D picture is genuinely incomplete and that the truth representation is at least two-dimensional. They decompose it into a **general truth direction** t_G (which points false→true for both affirmatives and negations) and a **polarity-sensitive direction** t_P (which points false→true on affirmatives but true→false on negations). A probe trained only on affirmatives learns some linear combination of t_G and t_P, which is exactly why it breaks on negations — t_P flips sign and contaminates the readout.

The construction is supervised but minimal: ordinary least squares on labelled activations across balanced affirmative + negated datasets, modelling a_ij ≈ μ_i + τ_ij·t_G + τ_ij·p_i·t_P. They derive a classifier (TTPD — Training of Truth and Polarity Direction) that uses t_G alone and compare it to logistic regression, mass-mean, and CCS on cross-dataset generalisation, cross-grammar generalisation (logical conjunctions and disjunctions, German translations of English statements), and a real-world role-play lying benchmark. Headline numbers: 93.9% on unseen topics, 93.8% on real-world lie detection (vs. 79% for LR, 73% for CCS), and only a few points of drop when generalising from English to German statements.

The cross-model claim — that this 2D structure shows up consistently across LLaMA2-13B, LLaMA3-8B (both instruct and base), Mistral-7B-Instruct, Gemma-7B and Gemma-2-27B — is what motivates the "universal" framing. The first two PCs of preprocessed activations capture >60% of truth-related variance in each, and adding more statement types doesn't push significant components past two. The paper positions this as evidence consistent with a Platonic-Representation-Hypothesis-style convergence, though it's careful — the claim is "at least 2D and consistent across these models," not "exactly 2D and provably universal."

What's interesting here is that it's a constructive explanation of a known failure rather than a new SOTA result. Marks & Tegmark already showed that training on affirmative + negated together generalises; this paper says *why* that works (you're now identifying both axes rather than a mixed direction) and shows the 2D readout is more robust on harder OOD splits. The real-world lie-detection gap (93.8% vs. CCS 73%) is the strongest empirical evidence that the decomposition isn't just a curiosity.

## Key experimental conditions

- Primary model: LLaMA3-8B-Instruct, layer 12 residual stream (d=4096); six-model replication including LLaMA3-8B-base, LLaMA2-13B-chat, Mistral-7B-Instruct-v0.3, Gemma-7B-Instruct, Gemma-2-27B-Instruct.
- Training data: six topic-specific factual datasets (cities, Spanish-English translations, element symbols, animal classes, inventors, diverse facts), each with affirmative and negated variants. Logical conjunctions, disjunctions, and German translations as held-out generalisation tests.
- Evaluation data: common_claim_true_false (4,450 statements), counterfact_true_false (31,964 statements), and a 26-scenario role-play lying benchmark (208 model responses, 104 unambiguous).
- Probes compared: TTPD (truth + polarity decomposition, classifier on t_G), logistic regression (LR), mass-mean (MM), and CCS (Burns et al.).
- Directions derived by OLS on balanced affirmative/negated activation sets.

## Key quantitative results

- Cross-dataset generalisation (unseen topics): TTPD 93.9±0.2%, LR 94.6±0.7%, MM 92.2±0.4%, CCS 84.8±6.4%.
- Real-world role-play lie detection: TTPD 93.8±1.5%, MM 90.5±1.5%, LR 79±8%, CCS 73±12%.
- German-language statements (probes trained only on English): only a few percentage points below in-language performance.
- PCA on preprocessed activations: first two PCs capture >60% of truth-related variance; adding logical conjunctions, disjunctions, and German statements does not push significant components past two.
- 2D structure replicates across LLaMA2-13B-chat, LLaMA3-8B (instruct + base), Mistral-7B-Instruct-v0.3, Gemma-7B-Instruct, and Gemma-2-27B-Instruct.

## Methods (what they did and didn't use)

- Linear probes (supervised, OLS-derived) are the core method — TTPD reads off t_G; the t_P direction is identified and characterised but not used in the final classifier.
- PCA on preprocessed (mean-subtracted) activations to characterise dimensionality of the truth subspace.
- No SAEs, no activation steering interventions, no fine-tuning. The paper is purely a probing / geometry result.
- Open-weight models throughout — fully reproducible.
- The truth/lie distinction is operationalised behaviourally (statements labelled true/false from curated factual datasets; role-play scenarios with incentive to lie); the paper does not separate "model believes false but says true" from "model says false because it's prompted to." The probe is trained on factual-label contrast, then evaluated on lying scenarios — generalisation across this gap is one of its claims.

## Authors' stated limitations / future work

- TTPD uses only t_G; non-linear classifiers leveraging both t_G and t_P might improve accuracy, especially on edge cases.
- Tested grammatical structures are limited (affirmatives, negations, conjunctions, disjunctions, one non-English language). Other structures might reveal additional linear components.
- The analysis establishes the truth subspace is *at least* two-dimensional; higher-dimensional structure is not ruled out.
- No inference-time interventions on the 2D subspace are studied — steering is left to future work.
- Applicability to larger frontier models and multimodal architectures is open.
- The authors flag connection to the Platonic Representation Hypothesis as a direction worth pursuing.

## Open questions and follow-up directions

1. **Whether the 2D structure persists at frontier scale and in RLHF'd production models is open.** All six tested models are ≤27B and either base or instruct-tuned; whether heavily RL-tuned frontier models (Claude, GPT-4-class) still expose t_G and t_P at the same layer and with the same generalisation properties is not demonstrated.
2. **The "lying" benchmark is role-play with explicit incentive cues, not strategic deception with a self-preservation motive.** Whether the same 2D subspace fires on the strategic-deception scenarios studied by Apollo (insider trading, sandbagging) is the load-bearing transfer question — Goldowsky-Dill et al. show probes work on those, but don't decompose whether they're reading t_G or some confounded direction.
3. **t_P's polarity-flipping behaviour is a clean falsification target for the "linear truth" framing.** If t_P weren't there, a single direction would work; that it *is* there and flips on negation suggests the model represents "truth-of-this-statement" rather than "the world is this way." Distinguishing those interpretations would require constructing statements where the model's belief and the proposition's truth-value come apart.
4. **No inference-time intervention.** The paper identifies the subspace but never patches activations along t_G or t_P to test causal load-bearing. Adding/subtracting t_G should flip the model's stated truth value if the geometry is what they claim; without that experiment, the evidence is correlational.
5. **The cross-model "universality" claim leans on PCA variance shares and consistent direction recovery, not on direction transfer.** Whether t_G derived on LLaMA3 actually classifies activations from Gemma-2-27B (after appropriate basis alignment) would be the strong test of universality — convergent dimensionality is a weaker claim than convergent directions.

## See also

- [[geometry_of_truth]] — direct predecessor; Marks & Tegmark's 1D-direction-plus-affirmative+negated-training result is the empirical finding this paper explains mechanistically.
- [[internal_state_lying]] — Azaria & Mitchell, the original MLP-on-activations lying-detection result whose generalisation failure this paper diagnoses as t_G/t_P conflation.
- [[ccs_latent_knowledge]] — Burns et al.'s CCS is the unsupervised baseline TTPD beats on cross-dataset generalisation (84.8% vs. 93.9%) and decisively on real-world lying (73% vs. 93.8%).
- [[deception_probes]] — Apollo's strategic-deception probes on Llama-3.3-70B; sibling method on a harder (and more safety-relevant) deception target, but doesn't decompose what direction it captures.
