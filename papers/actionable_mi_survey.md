# Locate, Steer, and Improve: A Practical Survey of Actionable Mechanistic Interpretability in Large Language Models

**Authors:** Hengyuan Zhang, Zhihao Zhang, Qi Zhang, ..., Ngai Wong et al. (~32 authors; University of Hong Kong, Fudan, LMU Munich, Tsinghua, others)
**Year:** 2026
**arXiv:** [2601.14004](https://arxiv.org/abs/2601.14004)
**Fetched from:** `arxiv.org/html/2601.14004v4`
**Status:** read

---

## Summary (in our words)

This is a **survey, not an empirical paper** — flag that up front before treating any number in it as evidence. It catalogues 200+ mechanistic-interpretability papers under a single organising pipeline: **Locate → Steer → Improve**. The pitch is that MI should be treated as an *actionable engineering discipline* (diagnose a component, intervene on it, get a downstream improvement) rather than as observational science. The framing device is "surgical improvement from the inside" as an alternative to "external scaling factors" (more params, more data).

The taxonomy is the actual content. They define a set of **interpretable objects** (token embeddings, residual stream, attention QK/OV units, FFN neurons, SAE features), then enumerate **localizing methods** (magnitude analysis, causal attribution / patching / ablation, gradient detection incl. integrated gradients, probing, logit-lens vocabulary projection, circuit discovery via ACDC / EAP) and **steering methods** (amplitude manipulation, targeted optimization of isolated components, vector arithmetic — the `concept = mean_pos − mean_neg` recipe). They then map these onto three application buckets: improve alignment (safety, fairness, persona), improve capability (multilingualism, knowledge editing, reasoning), and improve efficiency (sparse fine-tuning, adaptive quantization).

For our purposes the value is as a **map, not a source**. Every quantitative claim in it is borrowed from a cited paper (Causal Tracing / ROME, Wendler's multilingual logit-lens bottleneck, ReasonScore SAE-reasoning features, ACDC's GPT-2 greater-than circuit), so the right move is always to chase the primary citation. The survey itself runs no experiments, reports no benchmark table of its own, and tests no model. Where it's genuinely useful is (a) as a vocabulary/structure reference for how the field now slices localization-vs-steering, and (b) as a way to find primary work on a specific object (e.g. "who steers refusal tokens", "who does knowledge editing via targeted optimization").

The relevance to a recognition-vs-action probing project is **structural and indirect**: the survey's whole spine — *first locate where a thing is represented, then steer it, and check the steer changes behaviour* — is exactly the locate-vs-act decomposition, just at the level of methodology rather than as a phenomenon inside the model. Its "Safety and Reliability" subsection covers refusal-token suppression and "latent safety representation steering," which is the neighbourhood of [[harmfulness_refusal_separately]], but the fetched text truncates before the specific citations, so treat its safety coverage as a pointer to chase rather than a finished bibliography.

## Key experimental conditions

- **No original experiments.** This is a synthesis of 200+ papers. There is no model under test, no dataset of its own, no benchmark.
- **Models discussed (in cited work):** GPT-2, GPT-3, Llama, and various open-weight models. The survey leans heavily on small-model interpretability work (GPT-2-scale circuits, factual-recall localization).
- **Companion artifact:** maintained GitHub list — `github.com/rattlesnakey/Awesome-Actionable-MI-Survey`.

## Key quantitative results

- **None original.** All numbers are inherited from cited papers and should be attributed to those, not to this survey.
- Representative cited findings the survey leans on: Causal Tracing (Meng et al. 2022) localizing factual recall to early-layer MLPs at the subject token with transfer via late-layer attention; Wendler et al. (2024) "English-centric bottleneck" in multilingual models (their Figure 8a); ReasonScore (Galichin et al. 2025) ranking SAE features by activation during reasoning; ACDC recovering GPT-2's greater-than circuit.
- SAE expansion factors cited as 16×–128×; SAE pathologies named: dead latents, feature absorption, compute cost, reconstruction-faithfulness concerns.

## Methods (what they did and didn't use)

- **The survey itself uses no internal-state method** — it is a taxonomy paper. What it *catalogues* is the full toolkit:
  - **Probing** is one of six localizing methods — framed correctly as measuring *decodability, not causality*, on frozen features (residual states, block outputs, SAE features).
  - **Steering via vector arithmetic** (difference-of-means concept vectors added to the residual stream) is one of three steering methods — the [[caa_panickssery]] / [[representation_engineering]] / [[persona_vectors]] lineage.
  - **SAEs** are a first-class interpretable object with a dedicated treatment.
  - **Causal attribution** (patching/ablation), **gradient/integrated-gradients attribution**, **logit lens**, and **circuit discovery (ACDC, EAP)** all covered.
- **What it does NOT do:** no experiments, no steering of its own, no probe trained, no causal patching run. It is purely organisational.
- **Open vs closed weights:** N/A (survey) — but the cited corpus is overwhelmingly open-weight / small-model interpretability work, which is itself a useful signal about where the field's reproducible evidence sits.

## Authors' stated limitations / future work

- **Scalability:** most catalogued methods are designed for small models; how they scale to 70B+ is unclear (this matches the recurring scale caveat across the probing literature).
- **Distributed vs. localized mechanisms:** localization assumes sparsity, but many behaviours are distributed across components — a standing tension for any "find the component and steer it" program.
- **Intervention robustness / side effects:** steering one component risks unintended downstream consequences; no standard way to bound this.
- **No standardized evaluation protocols** for actionable-MI interventions.
- **Future directions:** beyond decoder-only Transformers (MoE, VLMs); grounding units in cognitive science; theory of *when* localization succeeds; "interpretable by design" rather than post-hoc.

## Open questions and follow-up directions

1. **The locate-then-steer pipeline as an evaluation discipline.** The survey asserts the value of "diagnose → intervene → measure downstream effect" but flags the absence of standardized metrics. A genuinely useful contribution downstream would be a held-out, causal benchmark for whether a localized direction *actually* drives the behaviour it's named for — the gap between probe-decodability and steering-efficacy that several primary papers (e.g. [[probing_steering_eval_aware]]) already surface as an asymmetry.
2. **Does the localization-assumes-sparsity premise hold for safety-relevant behaviours?** The survey names distributed-vs-localized as a tension but doesn't resolve it; primary work like [[caught_in_the_act]] (deception as a ~100-direction subspace at 14B) suggests the answer is behaviour- and scale-dependent.
3. **Survey currency.** A 2026 survey citing 200+ papers will already be missing the most recent eval-awareness / recognition-vs-action probing work; use it for the established backbone (logit lens, ROME, ACDC, SAEs) and not for the frontier.
4. **Cross-checking the survey's safety taxonomy.** Its "safety-critical component manipulation" vs "latent safety representation steering" split is a clean two-axis cut; whether that maps onto the harm-recognition vs refusal-execution decomposition in [[harmfulness_refusal_separately]] is worth tracing through the actual citations (truncated in our fetch).

## See also

- [[harmfulness_refusal_separately]] — concrete instance of the survey's "latent safety steering" theme; the recognition-vs-action decomposition the survey gestures at structurally.
- [[representation_engineering]] — names the LAT reading/steering recipe that the survey files under "vector arithmetic" steering.
- [[caa_panickssery]] — canonical difference-of-means steering, the survey's "vector arithmetic" exemplar.
- [[persona_vectors]] — monitor-and-steer-with-the-same-vector pattern catalogued under persona/role steering.
- [[scaling_monosemanticity]] — the SAE-as-microscope work the survey's SAE section leans on.
- [[sparse_feature_circuits]] — SAE-feature circuit discovery in the survey's "circuit discovery" bucket.
- [[probing_steering_eval_aware]] — primary work exhibiting the probe-decodability vs steering-efficacy asymmetry the survey's "probing measures decodability not causality" caveat names.
