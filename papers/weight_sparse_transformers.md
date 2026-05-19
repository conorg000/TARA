# Weight-sparse transformers have interpretable circuits

**Authors:** Leo Gao, Achyuta Rajaram, Jacob Coxon, Soham V. Govande, Bowen Baker, Dan Mossing (OpenAI)
**Year:** 2025
**arXiv:** [2511.13653](https://arxiv.org/abs/2511.13653)
**Code:** [github.com/openai/circuit_sparsity](https://github.com/openai/circuit_sparsity)
**Fetched from:** `arxiv.org/html/2511.13653`
**Status:** read

---

## Summary (in our words)

The authors train small decoder-only transformers from scratch on Python with a hard L0 constraint on the weight matrices — the sparsest models keep roughly 1 nonzero weight per 1000 — and ask whether the resulting models contain circuits a human can actually read off. They pick 20 hand-crafted next-token tasks (predict whether a string closes with `'` or `"`, predict `]` vs `]]` based on bracket nesting depth, predict `.add` vs `+=` based on whether a variable is a `set` or a `str`, etc.), and for each task they prune the model down to the minimal subgraph that still achieves a target task loss of 0.15. The headline result is that those isolated circuits are tiny (the string-closing circuit is 12 nodes / 9 edges; the variable-type-tracking circuit is 2 attention heads with a copy mechanism), mean-ablatable, and the neurons and residual channels in them correspond to recognisable concepts — "quote detector", "quote-type classifier", an attention head doing averaging-then-thresholding to count brackets.

The framing we find useful is that this is a *training-time* interpretability bet rather than a *post-hoc* one. SAEs, probes, autoencoders, NLAs all try to read structure out of dense models that weren't optimised to be readable. Here the model is constrained so the structure must live in a small number of edges, and you just walk the graph. The cost is the obvious one: weight-sparse models need 100-1000x more training/inference compute than dense models of matched capability, and the largest experiments are 8-layer, d_model=2048, n_ctx=256, on the order of tens of millions of nonzero parameters. So the question the paper is really posing is: does this scale, and can we use it to understand dense frontier models?

The rigour part is what makes the paper hold up beyond a demo. For each named circuit they show (a) mean-ablating every node *outside* the circuit preserves task loss, (b) ablating the few nodes *inside* destroys it, and (c) the bracket-counting circuit reveals a "context-dilution" adversarial attack — averaging-then-thresholding means the activation magnitude scales like 1/n_ctx, so padding the list with extra tokens reliably breaks the prediction. That's a stronger claim than "we can draw a diagram"; the diagram corresponds to a real causal structure with predictable failure modes.

The capability-interpretability frontier is the other load-bearing result: at any given pretraining loss, sparse-model circuits are roughly 16x smaller (geometric-mean edge count) than circuits pruned from dense models matched on pretraining loss. Increasing width while holding L0 constant pushes the frontier outward — bigger model with the same nonzero budget is strictly more expressive — but the authors are clear that preserving interpretability past tens of millions of nonzero parameters is unsolved. A preliminary "bridges" section shows the technique can be co-trained with a dense model: encoders map dense activations into the sparse model's residual stream and decoders map back, trained with a joint NMSE + bidirectional-KL objective. They demonstrate that perturbing a feature in the sparse model (e.g. the "quote-type classifier") and routing the perturbation through the bridge actually shifts the dense model's output distribution. This is gestured at as the most important next step, not nailed down.

## Key experimental conditions

- Decoder-only transformers trained from scratch on a Python code dataset; RMSNorm; context length 256.
- Most experiments: `n_layer=8`, `d_model=2048`, `n_ctx=256`, `d_head=16`.
- Sparsity enforced by an L0 constraint on weights: after each step, all but the top-k magnitude entries in each weight matrix are zeroed. L0 is annealed linearly over the first 50% of training. A minimum of 4 nonzero values per neuron is enforced to avoid dead units.
- AdamW (β1=0.9, β2=0.95, λ=0.1, ε=0.1), "sharkfin" learning-rate schedule with 1% warmup, LR scaled by 1/√L0 across sparsity levels, grad-RMS clipped to 1.0.
- Mild activation sparsity (~1-in-4 nonzero) imposed at all node locations.
- A separate dense bigram table (d_vocab × d_vocab) is added to final logits so the sparse weights don't waste capacity on unigram/bigram statistics.
- 20 hand-crafted Python next-token tasks used as circuit targets: `single_double_quote`, `bracket_counting`, `set_or_string`, `set_or_string_fixedvarname`, `with_as`, `with_open`, `for_while`, `else_elif`, `if_ternary`, `if_equals`, `fstring_brace`, `bracket_brace`, `var_swap`, `var_if`, `indent_for`, `while_return_true`, `lambda_func`, `enumerate_range`, `final_kwarg`, `class_init`.
- Per-task pruning: learn binary masks over nodes (rows/columns of weight matrices — neurons, attention channels, residual reads/writes) via a Heaviside gate with a sigmoid surrogate gradient. Loss is task cross-entropy plus k (number of nonzero nodes). Pruning hyperparameters tuned by CARBS over 32 iterations × 8 parallel jobs; final k bisected to hit the target task loss (0.15 unless otherwise stated). LBFGS rescales final logits to absorb residual offsets. Deleted nodes are mean-ablated over the pretraining distribution.
- Capability-interpretability frontier traced over a scaling sweep across width and L0.

## Key quantitative results

- **Circuit size:** sparse-model circuits are ~16x smaller (geometric-mean edge count) than dense-model circuits pruned to the same task loss at matched pretraining loss.
- **String-closing-quote circuit:** 12 nodes / 9 edges. MLP layer 0 builds a quote detector and a quote-type classifier; a later attention head uses these as key/value. The four components have 41 total external edges, of which 9 are used.
- **Bracket-counting circuit:** three-stage algorithm — embedding detector → averaging (layer-2 attention head with constant queries/keys) → thresholding via attention-sink softmax (layer-4 head). 6 channels, 283 edges in the core path; reveals a "context dilution" adversarial attack where the averaging signal scales like 1/n_ctx so longer lists break the prediction.
- **Variable-type-tracking circuit:** two-hop, 2 attention heads across layers 4 and 6, with 4 query/key channels and 3 value channels; ~100 edges in the described components.
- **Sparsest training regime:** ~1 nonzero weight per 1000.
- **Activation sparsity:** weight sparsity induces activation sparsity in the residual stream — final-layer residual activation kurtosis increases as weight-L0 shrinks or as model size grows.
- **Compute cost:** 100-1000x more training/inference compute than a dense model of comparable capability. Scaling of this overhead with model size is not characterised.
- **Necessity check (Figure 32):** ablating the in-circuit nodes severely degrades task performance while ablating the rest of the model preserves it.
- **Bridges intervention:** perturbing the sparse model's `quote-type classifier` channel and routing through the bridge increases the dense model's probability of outputting a single quote; an analogous channel manipulation in `while_return_true` shifts the dense model towards predicting `:` over newline (smaller effect).

## Methods (what they did and didn't use)

- Training-time architectural constraint (top-k weight L0 with annealing) rather than post-hoc decomposition.
- Pruning + mean-ablation as the circuit-isolation primitive; binary-mask learning with Heaviside-plus-surrogate gradient; CARBS-tuned hyperparameters; LBFGS logit rescaling.
- Causal ablation (in-circuit vs out-of-circuit) as the validation primitive.
- Adversarial-input construction *derived from* the discovered circuit structure (the bracket-counting "context dilution" attack), which the paper uses as a soundness check on the circuit reading.
- Preliminary "bridge" co-training between a sparse and a dense model — encoder/decoder per sublayer, trained with NMSE on bridge predictions plus bidirectional KL (dense activations accepted by sparse model, and vice versa).
- Open-weight, open-code: full models and training code released.
- Does **not** use SAEs, linear probes, activation steering, or NLAs on these models. The point is precisely that post-hoc decomposition isn't needed when the weights themselves are sparse. SAEs are cited as prior work, not used.
- All evidence is white-box and mechanistic; no behavioural evals against frontier models.

## Authors' stated limitations / future work

- **Compute overhead** (100-1000x) is the central practical barrier; both optimisation and systems work needed to close the gap.
- **Polysemanticity reappears on more complex tasks** — circuits aren't fully monosemantic. Possible mitigations: weight-sparse mixture-of-experts, scaling sparse hidden dimensions toward SAE-scale (millions, not thousands).
- **Non-binary features**: some channels carry magnitude information beyond on/off, complicating explanation.
- **Mean ablation isn't a perfect faithfulness measure** — some form of causal scrubbing is the proper next step.
- **The "interpretability = compact circuit" operationalisation** is acknowledged as not fully capturing intuitive interpretability.
- **Scaling past tens of millions of nonzero parameters while preserving interpretability is unsolved**; at frontier capability the circuits would themselves be too large for manual reading and would need automated interpretability.
- **The pruning algorithm prunes nodes, not edges**, and often leaves residual prunable nodes requiring manual cleanup.
- **Weight sparsity alone may not be sufficient inductive bias** to fully disentangle superposition.
- **Bridges to dense models** are flagged as the most important direction — the preliminary results are a proof-of-concept, not a general method.

## Open questions and follow-up directions

1. **Whether the bridge construction recovers real dense-model structure or just a sparse approximation of it.** The bridges results are the load-bearing scaling claim: if perturbations routed through a bridge faithfully manipulate dense-model computation, weight-sparse training becomes a general interpretability tool for dense models; if the bridge only recovers a lossy projection, the method remains a clean-room exercise. The paper shows the effect goes in the right direction on two tasks but doesn't characterise faithfulness.
2. **Whether the 16x circuit-size advantage holds for non-syntactic tasks.** The 20 tasks are syntactic Python predictions with crisp ground-truth features (quote type, bracket depth, variable type). Whether the same compression survives on semantic tasks (sentiment, factuality, intent) — where the "true" feature basis is less obvious — is open.
3. **What the polysemanticity reappearance on complex tasks implies about the upper bound of the approach.** If polysemantic nodes reliably re-emerge as task complexity grows, weight-sparsity has a hard ceiling, and identifying the empirical complexity threshold matters more than further scaling alone.
4. **The 100-1000x compute overhead is reported as a flat range with no scaling law.** If it grows superlinearly with parameter count, the method is structurally incompatible with frontier-scale training; if sublinearly, the picture is very different. The paper does not say.
5. **Mean ablation vs causal scrubbing.** The authors flag this as a known weakness — but how much of the "circuits are tiny and faithful" headline survives a stricter causal-scrubbing pass is an empirical question the paper invites and does not answer.

## See also

- [[natural_language_autoencoders]] — sibling interpretability approach: NLAs verbalise activations from dense models post-hoc; weight-sparse training instead bakes the readability into training. Different bet on where structure should live.
- [[beyond_linear_probes]] — also extends "what shape of decoder do we need?" — polynomial probes for richer post-hoc readout vs. weight-sparsity for cleaner upstream structure.
- [[eliciting_secret_knowledge]] — found SAEs underperformed black-box prefill attacks on concealment elicitation. Sparse-weight circuits are a different mechanistic primitive; whether they'd help on that task is open.
- [[model_diff_tool]] — both this paper and Jiralerspong & Bricken's crosscoder propose proactive interpretability primitives over thousands of features; the filtering / scaling challenges rhyme.
- [[persona_vectors]] — linear directions for character traits from dense models; methodologically opposite (post-hoc, behavioural-target) but addresses the overlapping question of "where do interpretable units live."
