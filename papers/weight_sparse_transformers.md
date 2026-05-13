# Weight-sparse transformers have interpretable circuits

**Authors:** Leo Gao, Achyuta Rajaram, Jacob Coxon, Soham V. Govande, Bowen Baker, Dan Mossing (OpenAI)
**Year:** 2025
**arXiv:** [2511.13653](https://arxiv.org/abs/2511.13653)
**Code:** [github.com/openai/circuit_sparsity](https://github.com/openai/circuit_sparsity)
**Status:** read

---

## Summary (in our words)

The authors train small transformers from scratch with a hard L0 constraint on the weights — so most weights are exactly zero and each neuron has only a handful of connections — and ask whether the resulting models contain circuits a human can actually read off. They train on Python code, then prune the model down to the subgraph responsible for each of 20 hand-crafted next-token tasks (e.g. "predict whether a string closes with `'` or `\"`", "predict bracket nesting depth", "track whether a variable is a `set` or a `str`"). The headline result is that the isolated circuits are tiny, mean-ablatable, and the neurons and residual channels in them correspond to recognisable concepts ("quote detector", "open-bracket detector", "type-copy attention head").

The framing we find useful is that this is a *training-time* interpretability bet rather than a *post-hoc* one. SAEs, probes, autoencoders, NLAs all try to read structure out of dense models that weren't optimised to be readable. Here the model is constrained so the structure must live in a small number of edges, and you just walk the graph. The cost is the obvious one: weight-sparse models need 100-1000x more training/inference compute than dense models of the same loss, and the largest experiments are in the small-to-mid range (8 layers, d_model 2048, ~tens of millions of nonzero parameters). So the question the paper is really posing is: does this scale, and can we use it on dense frontier models?

The rigour part is what makes the paper hold up beyond a demo. For each named circuit they show (a) mean-ablating every neuron *outside* the circuit preserves task loss, while (b) ablating the few nodes *inside* the circuit destroys it, and (c) the discovered circuit's failure modes transfer — adversarial inputs derived from the circuit's structure also fool dense models of comparable capability. That's a stronger claim than "we can draw a diagram"; it's "the diagram corresponds to a real causal structure that generalises."

The capability-interpretability frontier figure is also worth flagging: at any given pretraining loss, sparse-model circuits are roughly 16x smaller than circuits pruned out of dense models of matched loss. Scaling model size pushes the frontier outward, but the authors are clear that preserving interpretability past tens of millions of nonzero parameters is an open problem. A preliminary section shows the technique can be adapted to *explain* existing dense models via a bridge — but this is gestured at, not nailed down.

## Key experimental conditions

- Decoder-only transformers trained from scratch on Python code.
- Most experiments: `n_layer=8`, `d_model=2048`, `n_ctx=256`, `d_head=16`, RMSNorm.
- Sparsity enforced by L0 constraint on weights (sparsest models ~1-in-1000 nonzero); activation L0 around 1-in-4.
- 20 hand-crafted Python next-token tasks used as circuit targets: string-closing-quote, bracket counting, set-vs-string variable type tracking, `with`/`for`/`while` loop scoping, indentation, etc.
- Pruning isolates the per-task circuit; the rest of the model is mean-ablated.
- Scaling sweep across model sizes and sparsity levels to trace the capability-interpretability frontier.

## Key quantitative results

- Sparse-model circuits are ~16x smaller (geometric-mean edge count) than circuits pruned from dense models matched on pretraining loss.
- Specific circuits reported: string-closing uses 12 nodes / 9 edges; bracket-counting uses 7 nodes; variable-type-tracking uses 2 attention heads with copy mechanism.
- Sparsest training regime: ~1 nonzero weight per 1000.
- Sparse models cost 100-1000x more training/inference compute than dense models of comparable capability.
- Scaling caps at tens of millions of nonzero parameters before interpretability degrades.
- Adversarial examples derived from sparse-model circuits transfer to dense models of comparable capability — circuit structure isn't an artefact of the sparsity prior.

## Methods (what they did and didn't use)

- Training-time architectural constraint (L0-sparse weights) rather than post-hoc decomposition.
- Pruning + mean-ablation as the circuit-isolation primitive; causal ablation as the validation primitive.
- Adversarial transfer to dense models as a generalisation check.
- Open-weight, open-code: full models and training code released.
- Does **not** use SAEs, linear probes, activation steering, NLAs, or any other post-hoc interpretability method on these models. The point is precisely that post-hoc methods aren't needed when the weights themselves are sparse. SAEs are cited as prior work, not used.
- All evidence is white-box and mechanistic; no behavioural evals against frontier models.

## Authors' stated limitations / future work

- Compute cost: 100-1000x dense-equivalent compute is the central practical barrier.
- Scaling beyond tens of millions of nonzero parameters while preserving interpretability is unsolved.
- Polysemantic neurons reappear on more complex tasks even under the sparsity prior.
- Some features are non-binary, requiring magnitude (not just activation) interpretation.
- Preliminary results on adapting the method to dense models via "bridges" — flagged as the most important next step.
- Mixture-of-experts variants suggested as a route to better cost-interpretability tradeoff.

## Open questions and follow-up directions

1. **Whether the bridge construction recovers real dense-model structure or just a sparse approximation.** The preliminary "explain dense models via bridges" result is the load-bearing scaling claim. If the bridge faithfully recovers dense-model circuits, weight-sparse training becomes a general interpretability tool; if it only recovers a lossy projection, it remains a clean-room exercise. The paper does not yet distinguish these.
2. **Whether 16x circuit-size advantage holds for non-syntactic tasks.** The 20 tasks are syntactic Python predictions with crisp ground-truth features (quote type, bracket depth, variable type). It is open whether the same compression advantage survives on semantic tasks (sentiment, factuality, intent) where the "true" feature basis is less obvious.
3. **What the polysemanticity reappearance on complex tasks implies about the upper bound of this approach.** If polysemantic neurons reliably re-emerge as task complexity grows, weight-sparsity may have a hard ceiling — and identifying the empirical complexity threshold matters more than further scaling.
4. **Whether adversarial transfer from sparse to dense generalises beyond capability-matched pairs.** The paper shows transfer at matched pretraining loss. Whether circuits found in a small sparse model transfer to a much larger dense one is the more interesting (and unanswered) version of the claim.
5. **The 100-1000x compute overhead is reported as a flat cost; its scaling with model size is unstated.** If the overhead grows superlinearly with parameter count, the method is structurally incompatible with frontier-scale training; if sublinearly, the picture is very different. The paper doesn't say.

## See also

- [[natural_language_autoencoders]] — sibling interpretability approach: NLAs verbalise activations from dense models post-hoc; weight-sparse training instead bakes the readability into training. Different bet on where structure should live.
- [[beyond_linear_probes]] — also extends "what shape of decoder do we need?" — polynomial probes for richer post-hoc readout vs. weight-sparsity for cleaner upstream structure.
- [[eliciting_secret_knowledge]] — found SAEs underperformed black-box prefill attacks on concealment elicitation. Sparse-weight circuits are a different mechanistic primitive; whether they'd help on that task is open.
- [[model_diff_tool]] — both this paper and Jiralerspong & Bricken's crosscoder propose proactive interpretability primitives over thousands of features; the filtering / scaling challenges rhyme.
- [[persona_vectors]] — linear directions for character traits from dense models; methodologically opposite (post-hoc, behavioural-target) but addresses overlapping question of "where do interpretable units live."
