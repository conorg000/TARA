# Designing and Interpreting Probes with Control Tasks

**Authors:** John Hewitt, Percy Liang (Stanford)
**Year:** 2019
**arXiv:** [1909.03368](https://arxiv.org/abs/1909.03368)  (EMNLP-IJCNLP 2019, [D19-1275](https://aclanthology.org/D19-1275/))
**Fetched from:** `ar5iv.labs.arxiv.org/html/1909.03368` (the ACL PDF returned a compressed stream with no usable numbers)
**Status:** read

---

## Summary (in our words)

This is the paper that gave the probing literature its conscience. A probe is a supervised classifier trained to predict some linguistic property (part-of-speech, dependency structure) from a frozen representation, and the field had been reading high probe accuracy as evidence that "the representation encodes property X." Hewitt & Liang point out the obvious confound: a sufficiently expressive probe can hit high accuracy by *memorising a word-type → label mapping* rather than by reading any structure out of the representation. So accuracy alone tells you about the probe's capacity as much as about the representation.

Their fix is the **control task**: take the same input tokens and the same output space, but assign outputs *at random per word type* (sample a label for each vocabulary item once, then apply it deterministically to every occurrence). A control task has, by construction, no linguistic structure — it can only be solved by memorisation. They then define **selectivity = linguistic-task accuracy − control-task accuracy**. A good probe is one that does well on the real task *and badly on the control task*: high selectivity means the probe's success is coming from the representation, not from its own ability to memorise.

The headline empirical result is that the popular high-capacity MLP probes are almost useless by this lens. On POS tagging, a linear probe and a 2-layer MLP score essentially the same linguistic accuracy (97.2 vs 97.3), but the MLP also nails the *random* control task (93.2%), so its selectivity is 4.2 vs the linear probe's 26.0. The MLP is mostly memorising. Worse, on dependency edge prediction the MLP-1 probe gets *negative* selectivity (−0.7) — it solves the random control task slightly better than the real one. And dropout, the field's reflexive complexity-control knob, does not reliably fix this.

The constructive payoff is a set of guidelines (prefer linear/bilinear probes; if you must use an MLP, shrink the hidden dimension to ~10–50 and use weight decay, not dropout; always report selectivity against a control task; never compare two representation layers on accuracy alone). They demonstrate the last point directly: ELMo's layer 1 has marginally *higher* POS accuracy than layer 2 (97.2 vs 96.6) but substantially *lower* selectivity (26.0 vs 31.4) — so the accuracy-based conclusion "layer 1 is the better POS layer" is an artifact of layer 1 making word identity easier to memorise, and the selectivity-based conclusion flips it. This is a tight, durable methodological result; the numbers are ELMo/English/PTB-specific but the argument is representation-agnostic.

## Key experimental conditions

- **Representations probed:** ELMo (5.5B-word pretrained), separated into ELMo1 (first BiLSTM layer) and ELMo2 (second layer); plus **Proj0**, an untrained-BiLSTM-over-ELMo-char-CNN random baseline. Probed on the Penn Treebank dev set.
- **Two linguistic tasks:** (1) part-of-speech tagging (45-tag output space); (2) dependency edge prediction (predict each token's head index, output space 1:T).
- **Control-task construction — POS:** for each word type, sample one POS tag uniformly at random; apply it to all tokens of that type regardless of context.
- **Control-task construction — dependency:** for each word type, sample uniformly from three length-independent attachment behaviours — attach-to-self (y_i = i), attach-to-first (y_i = 1), attach-to-last (y_i = T) — preserving output-space equivalence with the real task.
- **Probe families:** POS — linear, MLP-1, MLP-2 (ReLU). Dependency — bilinear, MLP-1, MLP-2.
- **Complexity-control knobs swept:** hidden dim/rank (default 1000; tested {2,4,10,45} POS, {5,10,50,100} dep), dropout {0.2,0.4,0.6,0.8}, training-set size {39832, 4000, 400}, L2 weight decay {0.01,0.1,1,10}, early-stopping iterations.

## Key quantitative results

- **POS, default hyperparameters (acc / control / selectivity):** Linear **97.2 / 71.2 / 26.0**; MLP-1 97.3 / 92.8 / 4.5; MLP-2 97.3 / 93.2 / **4.2**. Same accuracy, ~6× selectivity gap — the MLP is memorising.
- **Dependency edge prediction, default (acc / control / selectivity):** Bilinear **89.0 / 82.4 / 6.6**; MLP-1 92.3 / 93.0 / **−0.7** (negative — solves the random task *better* than the real one); MLP-2 93.9 / 92.0 / 1.9. Here the MLPs have higher *linguistic* accuracy yet far worse selectivity.
- **Dropout is not a reliable fix:** on POS, p=0.4 *lowered* MLP-2 selectivity 4.2 → 3.4; on dependency it nudged MLP-1 up (−0.7 → 0.7) but degraded the bilinear probe. "The most popular method for controlling probe complexity does not consistently lead to selective MLP probes."
- **Rank constraint works:** small hidden dims (rank-10 POS, rank-50 dep) preserve linguistic accuracy while improving selectivity — i.e. the default 1000-dim hidden state is gratuitous capacity.
- **Layer comparison flips under selectivity:** Linear probe — ELMo1 97.2 acc / 26.0 sel vs ELMo2 96.6 acc / **31.4 sel** (accuracy says layer 1, selectivity says layer 2). MLP-1 — ELMo1 97.3/4.5 vs ELMo2 97.0/**8.8**. Random baseline Proj0: 96.3 acc / 20.6 sel — so ELMo2 at near-identical accuracy clears the random baseline on selectivity by ~11 points.

## Methods (what they did and didn't use)

- Pure **supervised-probe methodology**: train classifiers on frozen contextual representations and measure accuracy. The contribution is the *evaluation protocol* (control tasks + selectivity), not a new representation method.
- No activation steering, no SAEs, no causal interventions — this predates that toolkit. Control tasks are a behavioural-baseline construct (random per-type relabelling), not an internal-state read.
- Probe complexity is the object of study: the whole point is that probe expressivity confounds the "is it in the representation?" question, so they sweep architecture, rank, dropout, weight decay, data size, and early stopping.
- Open-weight, fully reproducible (ELMo + PTB), though scope is one representation family and English only.

## Authors' stated limitations / future work

- Control tasks operate at the **word-type** level, not the example level — a deliberate contrast with Rademacher-complexity-style accounts (Zhang et al. 2017) of memorisation.
- Scope is ELMo + English (POS and dependency); generalisation to other representations and languages is not established.
- The "probe designed with control tasks" configurations were partly **hand-picked**, with no systematic optimisation procedure offered.
- Qualitative error analysis covers only ~10 probes per model; scalability of that analysis is unclear.
- Framed as foundational — selectivity is offered as an interpretive lens, not a complete theory of probe design.

## Open questions and follow-up directions

1. Selectivity penalises memorisation of *word identity*, but a probe can also succeed via a non-linguistic confound that is *not* word-type-bound (e.g. positional or formatting cues shared across types). A type-level control task does not catch those — what is the right control for a confound that itself generalises across the vocabulary?
2. The recommendation "prefer the simplest probe that achieves high accuracy" trades expressivity for interpretability, but says little about *which* directions a low-capacity probe latches onto. A high-selectivity linear probe still does not tell you the feature is causally used by the model — selectivity is a necessary, not sufficient, condition for the usual representational claims.
3. Whether the same accuracy-vs-selectivity divergence appears in modern decoder-only LLM residual streams (vs ELMo BiLSTM layers) is an empirical question the paper cannot answer; the confound is architecture-agnostic but its magnitude need not be.
4. Control tasks assume a discrete, type-indexable input. Extending selectivity cleanly to subword tokenisation, to free-form generation targets, or to probes over multi-token spans is non-trivial and largely unaddressed.

## See also

- [[geometry_of_truth]] — directly downstream methodologically: difference-of-means probes are the "simple, hard-to-overfit" probe Hewitt & Liang argue for, and Marks & Tegmark's finding that discriminative probes get contaminated by correlated-but-causally-inert features is the selectivity worry in causal-patching form.
- [[eval_awareness_format_confound]] — the modern incarnation of this paper's warning: an eval-awareness probe that fires 94.5% on format-rewritten deployment prompts is exactly a probe passing a real task while a confound (template structure) does the work; control-style decorrelation collapses it.
- [[better_deception_probes]] — sibling concern about probe *design* dominating results: system-prompt choice explains 70.6% of probe-AUC variance, the deception-probe analogue of "the probe family, not the representation, is driving the number."
- [[ccs_latent_knowledge]] — part of the probe-methodology lineage; CCS's unsupervised consistency losses are a different attempt to stop probes from just tracking the model's output behaviour.
- [[deception_probes]] — the "what direction is the probe actually capturing" question raised there (deception vs eval-awareness vs something else) is the selectivity problem applied to a safety target rather than POS.
