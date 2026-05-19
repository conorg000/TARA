# The Internal State of an LLM Knows When It's Lying

**Authors:** Amos Azaria, Tom Mitchell
**Year:** 2023 (EMNLP Findings)
**arXiv:** [2304.13734](https://arxiv.org/abs/2304.13734)
**Status:** read

---

## Summary (in our words)

This is the earliest paper we know of that asks whether an LLM's hidden states already contain a "truthfulness" signal that a small external classifier can read off. The method — christened **SAPLMA** (Statement Accuracy Prediction, based on Language Model Activations) — trains a small feedforward classifier (3 hidden layers, 256/128/64 units, ReLU + sigmoid, 5 epochs, no hyperparameter tuning) on the residual-stream activations of OPT-6.7B and LLaMA2-7B for true/false single-sentence statements, then asks how well the classifier transfers to held-out *topics*.

The headline finding is that mid-layer activations carry a topic-general truth signal: trained on five topics and tested on the sixth, the probe reaches 71% (OPT, layer 20) and 83% (LLaMA2, layer 16) average accuracy, versus ~54% for BERT-embedding, few-shot, and "is-it-true?" prompting baselines. The right layer matters — performance peaks around 2/3 of the way through the network and degrades at both ends. The probe also beats the LLM's own assigned token probability as a truthfulness signal.

What we'd call out as the paper's contribution is less the absolute numbers and more the shape of the setup: held-out *topic* generalization (cities → animals etc.) is a stronger test than within-distribution cross-validation, and the result establishes that the relevant feature isn't memorization of surface form. Worth flagging that the probe is an MLP, not a linear probe — so this paper is the conceptual ancestor of the linear-probe-for-truth line, but the specific result is for a slightly more expressive classifier. The 6,084-statement **TrueFalse** dataset (cities, inventions, chemical elements, animals, companies, scientific facts) is itself a contribution; subsequent probe papers use it.

The framing — "knows when it's lying" — is stronger than what's demonstrated. The setup measures whether the model represents truth/falsity of declarative statements; it doesn't show the model strategically producing false outputs while internally tracking truth. That latter claim is what later strategic-deception probe work (Apollo's deception probes) attempts to establish.

## Key experimental conditions

- Two open-weight base models: **OPT-6.7B** and **LLaMA2-7B** (both 32 layers, 4096 hidden dim)
- Probe input: activations at a chosen layer, taken at the final token of the statement
- **TrueFalse dataset** — 6,084 statements across 6 topics: Cities (1,458), Inventions (876), Chemical Elements (930), Animals (1,008), Companies (1,200), Scientific Facts (612). First five built from external sources (Wikipedia, PubChem, Forbes); Scientific Facts ChatGPT-generated then human-curated (48 disputed pairs removed)
- Critical evaluation protocol: **train on 5 topics, test on the held-out 6th** — measures cross-topic generalization rather than within-distribution accuracy
- Layer sweep across all 32 layers for both models
- Second evaluation on LLM-generated statements (with threshold optimization)

## Key quantitative results

- **OPT-6.7B, layer 20 (best):** 71% mean accuracy across the 6 held-out-topic tests. By topic: Cities 81%, Companies 81%, Inventions 73%, Scientific Facts 68%, Chemical Elements 62%, Animals 61%
- **LLaMA2-7B, layer 16 (best):** 83% mean accuracy
- **Layer sweep:** middle/upper-middle layers dominate. OPT layer 20 (71%) > final layer (64%) > middle layer (65%)
- **Baselines (OPT-6.7B):** few-shot prompting (3- and 5-shot) 54%, BERT embeddings 54%, "It-is-true" prompting 56% — all near chance, well below SAPLMA's 71%
- **LLM-generated statements:** SAPLMA holds at 71% (layer 28); baselines collapse to ~50%
- Probe beats LLM-assigned token probability as a truthfulness signal

## Methods (what they did and didn't use)

- **MLP probe on hidden states** (not strictly a linear probe — 3 hidden layers with ReLU). Trained on activations at the final-token position of a single-sentence statement
- **Behavioural baselines** (few-shot prompting, "is it true?" prompting) and a **representation baseline** (BERT embeddings + same classifier head)
- Open-weight models only (OPT, LLaMA2); reproducibility is unproblematic
- No activation steering, no causal intervention, no SAEs — purely a read-out experiment. The paper establishes that the representation exists and is topic-general; it doesn't establish that the representation is *used* by the model to produce its outputs
- Final-token-only readout; the paper notes mid-sentence/intermediate-token activations are unexplored
- Single-sentence declaratives only — no multi-turn, no generation-time tracking, no agentic settings

## Authors' stated limitations / future work

- English-only evaluation
- Single-sentence statements only; longer / multi-claim responses untested
- Binary true/false framing rather than graded uncertainty / calibration
- Potential bias inherited from the underlying LLM (if the model is wrong about a fact, the probe will likely also be wrong)
- Future: larger models; multilingual evaluation; using activations across all tokens rather than just the final one; human studies comparing filtered vs. unfiltered LLM outputs

## Open questions and follow-up directions

1. **Linear vs. MLP probe.** The paper's headline classifier is a 3-layer MLP. Whether a *linear* probe on the same activations achieves comparable accuracy — and whether the topic-general truth direction is one-dimensional — is what the "geometry of truth" line takes up. The SAPLMA numbers are not directly comparable to later linear-probe accuracies.
2. **Truthfulness of a statement vs. truthfulness of an output.** The probe sees a declarative sentence and predicts whether it is true. It does not measure whether the model is being deceptive in its own generation. The leap from "model represents truth of input" to "probe catches strategic deception" requires a different experimental setup and is not licensed by these results.
3. **Why the upper-middle layers.** Best performance at layer 20/32 (OPT) and 16/32 (LLaMA2) is consistent with mid-stack abstraction peaking before the final unembedding-aligned layers, but the paper doesn't decompose what changes at the optimal layer. A residual-stream layer-wise causal intervention would clarify.
4. **Topic-by-topic variance.** Cities and Companies hit 80%+ while Animals and Chemical Elements sit at ~60%. Whether this reflects intrinsic feature-availability for the truth concept in those domains, or training-distribution artefacts in the LLM's pretraining, is not pinned down.
5. **Scale.** Both tested models are ~7B. Whether the truth direction sharpens, blurs, or moves with scale (and whether instruction-tuning vs. base affects it) is open at this paper's scope.

## See also

- [[geometry_of_truth]] — sibling foundational probe paper; replaces the MLP with a linear probe and argues for a one-dimensional truth direction
- [[deception_probes]] — modern descendant; moves from "is this statement true?" to "is the model being deceptive *right now*?" on Llama-3.3-70B with AUROC 0.96-0.999
- [[ccs_burns]] — contrastive contrast-consistent-search probe for truth without supervised labels; same era, different supervision regime
- [[sleeper_agent_probes]] — single-direction linear probe detects sleeper-agent defection at >99% AUROC; shows the truthfulness-probe idea extends to strategic behaviour, not just declarative truth
- [[high_stakes_probes]] — content-level activation probe that generalises from synthetic to natural data; sibling demonstration of probe transferability
