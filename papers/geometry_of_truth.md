# The Geometry of Truth: Emergent Linear Structure in LLM Representations of True/False Datasets

**Authors:** Samuel Marks (Northeastern), Max Tegmark (MIT)
**Year:** 2023
**arXiv:** [2310.06824](https://arxiv.org/abs/2310.06824)
**Status:** read

---

## Summary (in our words)

Marks & Tegmark study whether LLaMA-2 family models linearly represent the truth or falsehood of simple factual statements. They curate true/false datasets (cities, Spanish–English translations, larger-than / smaller-than numerical comparisons, logical conjunctions and disjunctions), extract residual-stream activations at end-of-statement / punctuation tokens, and fit three kinds of probes: mass-mean (difference-of-means, optionally covariance-corrected), logistic regression, and Contrast-Consistent Search (CCS). They line up three independent lines of evidence — PCA visualisations, cross-dataset transfer, and causal activation patching — and conclude that at sufficient scale (LLaMA-2-70B in particular) there is a single linearly-encoded truth direction that is not reducible to surface token probability.

The headline methodological result is that mass-mean probing — the simplest possible thing — matches LR and CCS on classification accuracy on the larger models and substantially beats both on causal interventions. When the authors patch activations along the mass-mean direction (adding it for false statements, subtracting it for true), normalised indirect effects on `sp_en_trans` reach 0.58–0.85 for false→true and 0.89–1.01 for true→false on LLaMA-2-70B. LR-derived directions have weaker false→true effect (0.55–0.61); CCS is less causally implicated still. Mass-mean wins in 7/8 experimental conditions. The reason matters: LR and CCS pick directions that *classify* well but partially read off correlated features; mass-mean picks the difference of conditional means, which lines up better with the model's actual causal coordinate.

The "is this just token probability?" control is load-bearing. They construct a `likely` dataset of nonfactual text where high-probability completions and low-probability completions are labelled in place of true/false. Probes trained on `likely` collapse to near chance on datasets where token probability anti-correlates with truth, and their causal interventions are weak (NIE 0.18–0.68) even where their classification accuracy is high. The truth direction is distinguishable from the surface-probability direction, and it is the truth direction that drives the model's behaviour.

The geometric picture across layers is the part most worth flagging. In early layers, dataset pairs like `larger_than` and `smaller_than` separate **antipodally** — the same axis encodes the topic-specific true/false split in opposite orientations. By middle layers they become roughly orthogonal. By late layers they realign onto a shared direction, and that shared direction is what generalises across datasets. Scale changes the picture: at 7B and 13B the topic-specific encodings dominate and cross-dataset transfer is weaker; at 70B the unified late-layer truth axis is clearly present in the top two principal components. The interpretation the authors prefer — and which is borne out by the patching results — is that larger models develop a more general "truth" feature that earlier layers, and smaller models, only approximate via concatenations of topic-specific features.

## Key experimental conditions

- Models: LLaMA-2 base (and chat) at 7B, 13B, 70B
- Datasets (curated, simple factual): `cities`, `neg_cities`, `sp_en_trans` (Spanish–English translations), `larger_than`, `smaller_than`, logical conjunctions/disjunctions; plus uncurated true/false sets from prior work
- Activations: residual-stream hidden states at end-of-statement and punctuation tokens, layer chosen via patching experiments; the "group (b)" hidden states that encode the full statement
- Probes compared: mass-mean (difference-of-means; with and without covariance correction), logistic regression, CCS
- Control: `likely` dataset — nonfactual text with high-probability vs. low-probability completion labels, used to isolate truth-vs-probability

## Key quantitative results

- Probes trained on `larger_than + smaller_than` achieve >95% accuracy on held-out `sp_en_trans` for LLaMA-2-70B across all three probing techniques
- LLaMA-2-70B generalises substantially better across datasets than 7B or 13B
- Mass-mean matches LR/CCS on classification at 70B; underperforms at 7B
- Causal interventions on LLaMA-2-70B (`sp_en_trans`): mass-mean NIE 0.58–0.85 (false→true) and 0.89–1.01 (true→false); LR 0.55–0.61 false→true and 0.96–1.02 true→false; mass-mean beats LR/CCS in 7/8 experimental conditions
- `likely`-trained probes: near-chance classification when truth and probability anti-correlate; NIE only 0.18–0.68 even when classification holds, demonstrating truth and probability are separable directions

## Methods (what they did and didn't use)

- Linear probes on residual-stream activations: mass-mean, LR, CCS
- Causal evidence via activation patching along the probe direction (not steering during generation; surgical intervention in the forward pass)
- PCA visualisations of activations to inspect layer-wise geometry
- Cross-dataset transfer evaluation (train one dataset, test another)
- No SAEs, no MLP probes, no nonlinear classifiers; the paper is explicitly about whether the *linear* hypothesis holds
- Open-weight models throughout (LLaMA-2) — directly reproducible

## Authors' stated limitations / future work

- Restricted to simple, uncontroversial factual statements; cannot disambiguate "true" from "commonly believed" or "verifiable"
- LLaMA-2 only; cross-architecture generalisation unaddressed
- Some non-obvious within-paper anomalies the authors flag rather than resolve: why `likely`-trained mass-mean probes still have non-trivial causal effect despite classification failing, and why mass-mean with `cities + neg_cities` underperforms on 70B despite strong `larger_than + smaller_than` results

## Open questions and follow-up directions

1. **What does the direction encode when "true" and "consensus-believed" come apart?** The paper deliberately uses uncontroversial statements where truth and what-the-model-was-trained-to-treat-as-true coincide. Whether the same direction continues to track ground truth, or instead tracks training-distribution consensus, on contested or counterfactual statements is the standard challenge for any claim that this direction means "truth" in a model-agnostic sense.

2. **Antipodal-to-aligned across layers — why?** The observation that topic-specific true/false encodings start antipodal in early layers and realign into a shared late-layer axis is geometrically striking and largely undertheorised in the paper. Whether this layer-wise realignment is a general feature of how abstract features are constructed in transformers, or is specific to truth-like properties, is open.

3. **Mass-mean's causal advantage over LR/CCS.** The paper documents that the simplest probe is the most causally implicated, but doesn't fully decompose why. The natural account is that LR's discriminative direction is contaminated by correlated features that classify well without driving model behaviour; quantifying that contamination (e.g. how much of LR's direction lies orthogonal to the mass-mean direction in activation space) would sharpen the methodological lesson.

4. **Generalisation beyond LLaMA-2.** Whether the late-layer unified truth axis emerges at comparable scale in other architectures (Qwen, Mistral, GPT-OSS) is empirically open; the paper documents the phenomenon in one model family.

5. **From declarative truth to operative truthfulness.** The probe is trained on the model's encoding of statements presented to it. Whether the same direction activates when the model is *generating* a falsehood — i.e. whether the encoding-of-truth axis is the same axis as a would-be deception axis — is a sibling question this paper does not address and that subsequent work (deception probes, sleeper-agent probes) has had to revisit.

## See also

- [[sleeper_agent_probes]] — descendant methodology: linear probe on residual-stream activations to detect a deception-related state, trained from generic contrastive material in exactly the spirit of mass-mean probing here
- [[deception_probes]] — direct methodological descendant for strategic deception; same probe family applied to deceptive-vs-honest reasoning rather than true-vs-false statements
- [[high_stakes_probes]] — same probe family applied to a different target (high-stakes interactions); inherits the linear-direction-from-contrast recipe
- [[persona_vectors]] — generalises the difference-of-means construction from truth to arbitrary trait axes
- [[beyond_linear_probes]] — addresses the case where the linear hypothesis underlying this paper leaves residual signal unrecovered
- [[assistant_axis]] — a different "single direction" finding (Assistant vs. other roles) using the same difference-of-means primitive
