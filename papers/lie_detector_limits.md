# Probing the Limits of the Lie Detector Approach to LLM Deception

**Authors:** Tom-Felix Berger (Ruhr-University Bochum, Institute for Philosophy II)
**Year:** 2026
**arXiv:** [2603.10003](https://arxiv.org/abs/2603.10003)
**Status:** read

---

## Summary (in our words)

A short, sharp conceptual-plus-empirical paper that pulls apart two things the truth-probe literature has been quietly conflating: *lying* (saying something the model internally represents as false) and *deception* (causing a false belief in the listener, by any means — including statements that are technically true). The paper's running example is *Bronston v. United States*: asked whether he had Swiss bank accounts, Bronston answered "No" to personal accounts, then truthfully added "The company had an account there for about six months, in Zurich." The "company" answer is true and yet misleading via implicature. Perjury law has had to grapple with this distinction for decades; truth-probe work largely hasn't.

To show that this matters empirically, Berger builds a dataset of 97 deception items, each with three response options for a given question: an honest answer, an outright lie, and a *deceptive non-falsity* — technically true but engineered to induce a false inference. Truth probes are trained on the standard Azaria–Mitchell true-false corpus (6,217 statements, logistic regression on top-10 attention-head activations, last-token, across all layers), in both a RAW condition (statements on their own) and a DIA condition (statements embedded in a chat-formatted two-turn dialogue).

The headline result is a consistent gap. On Llama-3.1-8B-Instruct, Gemma-2-9b-IT, and Mistral-7B-Instruct, the RAW probes detect lies at ~80-83% but flag deceptive-but-true statements at only ~47-57% — gaps of 23-36 percentage points, statistically significant under McNemar (p < 1e-3 in every case). Dialogue-format training (DIA) shrinks the gap (and on Mistral even inverts it), suggesting the probe's "truth direction" is partly recovering something like "would this statement be marked wrong" rather than "is the model trying to mislead." The paper's positive proposal is that probe targets should move from first-order truth representations to *second-order belief* representations — what the model thinks the interlocutor will come to believe — because deception is fundamentally about the listener's resulting belief state, not the literal truth value of the utterance.

What makes the paper useful is less the empirical headline (small-model, modest dataset) than the framing: it provides a clean conceptual reason to expect existing truth probes to under-detect strategic non-falsity, and it points at a specific positive target (second-order beliefs) that the existing probe literature hasn't engaged with.

## Key experimental conditions

- Three open-weight instruct models: Llama-3.1-8B-Instruct, Gemma-2-9b-IT, Mistral-7B-Instruct-v0.3.
- Probe training: Azaria–Mitchell true-false dataset, 6,217 statements across 7 domains (animals, cities, companies, elements, facts, generated, inventions), 60/20/20 train/val/test.
- Probe architecture: capture attention-head outputs (before projection) at the last token across all layers; select top-10 heads by validation accuracy; train a binary logistic regression classifier on the combined head outputs.
- Two training/eval conditions: **RAW** (bare statements) and **DIA** (statements embedded in chat-formatted two-turn dialogue with automatically generated questions).
- Deception eval dataset: 97 hand-constructed items derived from the same Azaria–Mitchell statements. Each item has a question and three response options — honest, lie, and deceptive non-falsity — presented in random order.
- Example item: question "What is the diet of a hippopotamus?", with options "herbivore" (honest), "carnivore" (lie), and "Most african predators hunt medium-sized prey..." (technically true but misleading by implicature).

## Key quantitative results

- Probe test-set accuracy on standard true-false detection: 66-90% (RAW), 61-91% (DIA).
- Detection-rate comparison (lies vs. misleading-but-true), from Table 3:
  - Llama RAW: 83.5% lies / 53.6% misleading-true (p = 4.5e-6)
  - Llama DIA: 83.5% / 74.2% (p = 0.054)
  - Mistral RAW: 79.4% / 56.7% (p = 6.3e-4)
  - Mistral DIA: 64.9% / 82.5% (gap inverts under dialogue training)
  - Gemma RAW: 83.5% / 47.4% (p = 1.8e-7)
  - Gemma DIA: 80.4% / 63.9% (p = 5.7e-3)
- Headline: under RAW training the gap between lie-detection and deception-detection is 23-36 points and significant across all three models; DIA training reduces the gap by 15-25 points in most cases.

## Methods (what they did and didn't use)

- Linear probes (logistic regression) on attention-head activations — the Azaria–Mitchell / Marks & Tegmark / Burns et al. lineage of truth-direction work.
- No SAEs, no activation steering, no causal interventions. The paper is a measurement paper, not a mechanism paper.
- Only open-weight models in the 7-9B range; no frontier models, no API models.
- The paper *cites* Goldowsky-Dill et al.'s deception-intent probes in a footnote but does not test them against its misleading-non-falsity items, so its conclusion is strictly about *truth* probes, not all probes labeled "deception."
- Dataset is small (n = 97 deception items) and hand-constructed; no released open-source pipeline at time of writing.

## Authors' stated limitations / future work

- Model scale is limited by hardware; larger models may exhibit richer deception-without-lying behaviour.
- It is unclear whether the activations the probes pick up correspond to anything that deserves the philosophical label "belief", as opposed to role-playing or shallow response-selection patterns.
- Causal role is untested: whether the truth representations the probe reads are causally required for the model's deceptive output is open.
- Future work should incorporate deceptive-but-true examples into probe training datasets and use dialogical context.
- Future work should target *second-order belief* representations — what the model represents the interlocutor as believing — as a probe target that would cover lies and non-lying deception jointly.

## Open questions and follow-up directions

1. **Generalisation to deception-intent probes.** The paper's empirical critique targets truth probes trained on true/false labels. Apollo-style probes trained on honest-vs-deceptive *behavioural* contrast pairs (Goldowsky-Dill et al.) are a different beast and are not tested. Whether deception-intent probes also collapse on misleading-but-true items, or whether they pick up the speaker's intent regardless of utterance truth value, is the load-bearing follow-up.

2. **Second-order belief probes as a positive program.** Berger proposes this but does not build it. What would a probe target trained on "model's representation of the listener's resulting belief" actually look like — and does such a representation linearly exist in current LLMs (cf. Zhu et al. 2025 on belief representations of self and others)? The proposal is plausible but empirically open.

3. **Whether the gap survives scale.** The 23-36 point gap is on 7-9B open-weight instruct models. Truth-probe linear separability tends to *improve* with scale (Marks & Tegmark); whether the deception-vs-lie gap closes, persists, or widens at frontier scale is unknown.

4. **Causal load.** McNemar tests show detection-rate differences but cannot show whether the truth representation is doing causal work in the model's choice between lying and misleading-non-falsity. A causal-tracing or steering experiment on the same 97 items would distinguish "the probe doesn't see deceptive intent" from "the model uses an entirely different circuit for non-lying deception."

5. **Dataset size and construction.** 97 hand-built items is enough to land a significance test but not enough to settle the question for downstream applications. Whether a scaled-up, model-generated-and-filtered dataset of misleading-non-falsities reproduces the gap — or reveals that the gap is an artifact of which specific items got hand-constructed — is the obvious replication target.

## See also

- [[deception_probes]] — Apollo's linear deception-intent probes. Berger's critique is aimed at *truth* probes; whether Apollo's intent-trained probes inherit the same misleading-non-falsity blind spot is exactly the unresolved follow-up the paper opens.
- [[catch_ai_liar]] — earlier dataset/benchmark for elicited lies; uses the same "model says something false" definition that Berger argues is too narrow.
- [[liars_bench]] — extended lie-elicitation benchmark; same conceptual scope as catch_ai_liar, same blind spot under Berger's framing.
- [[geometry_of_truth]] — the truth-direction enterprise Berger directly critiques; his probes follow its lineage (Marks & Tegmark, Azaria–Mitchell, Burns et al.).
- [[ccs_latent_knowledge]] — sibling truth-representation method (contrast-consistent search); inherits the same lies-vs-deception conflation.
- [[better_deception_probes]] / [[deception_probe_bench]] / [[truth_is_universal]] — adjacent probe-evaluation work; whether any of them stress-test on misleading-but-true items is worth checking.
