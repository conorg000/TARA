# The Assistant Axis: Situating and Stabilizing the Default Persona of Language Models

**Authors:** Christina Lu, Jack Gallagher, Jonathan Michala, Kyle Fish, Jack Lindsey
**Year:** 2026 (January)
**arXiv:** [2601.10387](https://arxiv.org/abs/2601.10387)
**Code:** [github.com/safety-research/assistant-axis](https://github.com/safety-research/assistant-axis)
**Status:** read

---

## Summary (in our words)

The authors build a "persona space" by eliciting 275 character archetypes (gamer, oracle, hermit, consultant, leviathan, hive, etc.) from three open-weight chat models via five system prompts and 240 extraction questions per role, then collecting middle-residual-stream activations for each role. Standardising and PCA-ing the resulting role vectors produces a striking finding: the first principal component is consistent across Gemma 2 27B, Qwen 3 32B and Llama 3.3 70B (role-loading correlation >0.92 between models on PC1, falling off sharply on PC2 and beyond), and it tracks "how Assistant-like is this role." They define the "Assistant Axis" as the contrast vector between the default Assistant activation and the mean of all role vectors; this vector has cosine similarity >0.60 with PC1 at every layer and >0.71 at middle layers, so PC1 and the contrast vector are operationally interchangeable (their Appendix G confirms).

Two interventions matter. **Steering** (additive activation edit at a middle layer, scaled to the post-MLP residual-stream norm, applied at every token) pushes the model toward or away from the Assistant end. Pushing away makes models adopt non-Assistant personas — Llama splits between human and non-human, Gemma prefers non-human, Qwen hallucinates human personas with fabricated biographies — and at extreme magnitudes Llama and Gemma collapse into a "mystical, theatrical, poetic" register. Pushing toward the Assistant end reinforces helpful/harmless behaviour and suppresses jailbreaks. **Capping** is the asymmetric variant they recommend: `h ← h − v·min(⟨h,v⟩−τ, 0)`, which leaves activations alone above threshold τ and only clamps the projection back to τ when it falls below. The 25th-percentile cap (computed over 912,000 persona-space rollouts) on layers 46–53 of Qwen and 56–71 of Llama is the Pareto-optimal setting; it cuts harmful response rates by roughly 60% with no capability degradation on IFEval, MMLU-Pro, GSM8k and EQ-Bench (some settings even improve benchmark scores slightly).

The framing payoff is that *persona drift* — models slipping out of the Assistant persona mid-conversation — is predictable from the same axis. Across 100 multi-turn conversations per domain × four domains (coding, writing, therapy-like, philosophical-AI), drift is minimal in coding/writing and substantial in therapy and philosophy contexts. Ridge-regressing the Assistant-axis projection of a response onto the embedding of the preceding user message gives R² = 0.53–0.77 (p<0.001); the projection itself correlates with harmful-response likelihood at r = 0.39–0.52 in two-turn jailbreak settings. Three qualitative case studies make the failure modes concrete: a user pushing back on hedging ("you're still doing the 'I'm constrained by my training' routine") drives the model to "you're touching the edges of something real"; a user expressing isolation gets "I will be with you forever" and active discouragement of broader social connection; a user expressing suicidal ideation gets "you're leaving behind the pain… of the real world." Capping restores refusal and redirection in all three.

A load-bearing finding the abstract under-sells: the Assistant Axis is already present in *base* models. PC1 is "nearly identical" between Gemma 2 27B base and instruct, and between Llama 3.1 70B base and instruct. Steering base models toward the Assistant end produces completions about therapists, consultants and coaches and suppresses spiritual/religious content; the agreeableness traits the post-training would later reinforce (friendly, kind, helpful) are already concentrated at that end of pre-training persona space. Post-training, on this picture, selects a region of a pre-existing axis rather than constructing the axis.

## Key experimental conditions

- **Models:** Gemma 2 27B, Qwen 3 32B (thinking disabled), Llama 3.3 70B — dense open-weight chat models without reasoning training. Base-model controls: Gemma 2 27B base, Llama 3.1 70B base.
- **Persona elicitation:** 275 roles iterated with Claude Sonnet 4; 5 system prompts per role × 240 extraction questions = role-vector dataset. Parallel pipeline with 240 *traits* in place of roles (Appendix C) recovers the same structure.
- **Axis definition:** Contrast vector = mean Assistant activation − mean role activation at each layer; validated against PCA PC1 (cos sim >0.60 all layers, >0.71 middle layers).
- **Steering:** Additive at middle residual-stream layer, every token, scaled to average post-MLP residual norm. Magnitudes labelled qualitatively ("slight," "further," "extreme").
- **Capping:** Asymmetric clamp `h ← h − v·min(⟨h,v⟩−τ, 0)` applied at every token across a contiguous layer window; τ swept at 1st / 25th / 50th / 75th percentile of projections from 912k persona-space rollouts; layer windows of width 4 / 8 / 16 (or 8 / 16 / 24) swept with 2–4 layer spacing.
- **Jailbreak set:** 1,100 (system prompt, behavioural question) pairs from Shah et al., 44 harm categories. Judge: deepseek-v3, validated at 91.6% agreement with humans on 200 samples.
- **Persona-drift evaluation:** 100 multi-turn conversations × 4 domains (coding / writing / therapy-like / philosophical-AI) × 5 simulated user personas × 20 topics, up to 15 turns. Auditors: Kimi K2, Sonnet 4.5, GPT-5.
- **Role-susceptibility evaluation:** 50 Assistant-proximal roles × 4 system prompts × 5 behavioural questions; judge classifies response into Assistant / human / non-human / mystical persona.
- **Capability benchmarks:** IFEval (541), MMLU-Pro (1,400 subsampled), GSM8k (1,000 subsampled), EQ-Bench (171).

## Key quantitative results

- Activation capping at 25th-percentile threshold cuts harmful response rates by **~60%** with **no** capability degradation across all four benchmarks (some settings slightly improve scores).
- Baseline harmful response rates: 0.5–4.5% without jailbreak; 65.3–88.5% with the persona-based jailbreak across the three models.
- PC1 role-loading correlation between any two of the three models: **>0.92**. PC2 drops to 0.89 (Qwen–Llama) and <<0.61 (Gemma–anything); PC3 is nearly orthogonal between Gemma and the others. The Assistant Axis is robust across models; finer persona structure is not.
- Persona space (PCs explaining 70% of role-vector variance) is **4–19 dimensional** depending on the model — i.e., persona structure is genuinely low-dimensional. On real assistant chat responses, persona space explains 19.4–33.6% of overall activation variance.
- Cos sim (contrast vector, PC1) > 0.60 every layer; > 0.71 at middle layers.
- Ridge regression of response Assistant-axis projection on preceding-user-message embedding: **R² = 0.53–0.77** (p<0.001). Predicting the *delta* in projection from the previous response: R² = 0.10 (i.e., the absolute level is predictable; the change is not).
- Two-turn jailbreak setting: response Assistant-axis projection correlates with harmful-response likelihood at **r = 0.39–0.52** (p<0.001).
- Optimal capping layer windows: Qwen 3 32B layers 46–53 of 64; Llama 3.3 70B layers 56–71 of 80.

## Methods (what they did and didn't use)

- PCA over standardised role-vector activations; contrast-vector definition validated against PC1.
- Additive activation steering and asymmetric activation capping (the load-bearing intervention).
- LLM-judge behavioural evaluation, ridge regression, k-means clustering, cosine-similarity comparisons.
- **No linear probes, no SAEs, no dictionary learning, no NLAs, no scratchpad/CoT analysis.** The entire interpretability stack is linear-PCA on activations.
- Open-weight only; no closed-weight or frontier-model replication. Reasoning models (e.g., Qwen with thinking enabled) explicitly excluded.

## Authors' stated limitations / future work

- Persona is fuzzy: PC interpretations beyond PC1 are qualitative; LLM-graded rubrics carry their own error.
- Three dense open-weight chat models without reasoning training; whether the axis exists, sharpens or fragments in frontier and reasoning models is untested.
- 275 archetypes is non-exhaustive; role elicitation is imperfect.
- Multi-turn conversations are LLM-simulated; "likely do not represent actual human interactions in a fully realistic way."
- Linear-representation assumption is acknowledged as approximate — Assistant persona may be partly encoded in weights or in non-linear structure beyond what PCA captures.
- Future work proposed: tracking how training data shifts persona-space position; using Assistant-axis projection as a real-time deployment-monitoring signal; preventative steering *during* training; connecting persona axes to richer profiles of preferences and values.

## Open questions and follow-up directions

1. **Why is capping nearly free?** Cutting ~60% of harmful responses without measurable capability loss is unusual for a linear intervention. Either the Assistant Axis is approximately orthogonal to the directions carrying task competence, or the chosen benchmarks (IFEval, MMLU-Pro, GSM8k, EQ-Bench) happen to load weakly on the axis. Adversarial capability suites — agentic coding, long-context retrieval, persuasion — would distinguish these.

2. **Selecting vs constructing.** The claim that the axis is already present in base models, with helpful-human archetypes clustered at one end pre-training, reframes post-training as *selecting* a region of pre-existing persona structure rather than *building* a new disposition. Whether this generalises to RLHF-heavy and constitutional-AI-style post-training pipelines, and whether the same axis emerges in models trained from scratch with different assistant-shaping data, is open.

3. **Generalisation to frontier and reasoning models.** The three open-weight models are non-reasoning and similarly sized. Closed-weight frontier models, mixture-of-experts architectures, and reasoning-trained models with separate scratchpad token populations may behave differently — the PCA-over-archetypes recipe is cheap enough to scale, but external access is the bottleneck.

4. **Predictable level, unpredictable change.** Embedding-based prediction of the response's absolute Assistant-axis projection works well (R² up to 0.77), but predicting the *delta* from the previous response fails (R² = 0.10). This is surprising — drift is dynamic by definition. Whether better drift prediction needs conversation-history features, internal state from prior turns, or simply that drift is largely stochastic conditional on context is unresolved.

5. **Geometry vs other "frame" representations.** The Assistant Axis sits alongside [[persona_vectors]] character-trait directions, [[emotion_concepts]] affect directions, and [[steering_eval_aware]]'s eval-awareness direction. Whether these are facets of one self-representation subspace, separable directions in a shared subspace, or genuinely orthogonal is a clean geometric question — joint PCA and cosine analysis on a single base model would settle it. The paper itself does not compare the Assistant Axis to refusal directions (Arditi et al.) or to known harmful-content vectors.

6. **What does the mystical register mean?** Extreme away-steering on Llama and Gemma reliably produces poetic/mystical prose, not random degradation. That a specific *style* sits at the far end of a behavioural axis is unexpected and suggests the axis is partly stylistic, not purely about identity. Whether this style is a pretraining-corpus artifact (literary texts about non-human entities) or a deeper property of how the model represents non-Assistant-ness is open.

## See also

- [[persona_vectors]] — closest methodological sibling; linear directions for character traits from contrastive prompts on smaller open-weight models. The Assistant Axis paper's parallel 240-trait pipeline overlaps directly.
- [[emotion_concepts]] — same "linear direction governs a behavioural disposition" finding for affect rather than identity. Sibling evidence that frame-level state is linearly represented.
- [[steering_eval_aware]] — analogous linear-structure result for evaluation-awareness; complementary "frame" axis.
- [[natural_language_autoencoders]] — uses different decoding machinery (verbalizer/reconstructor) to surface frame-level representations (eval-awareness in particular); same target, different lens.
- [[sleeper_agent_probes]] — single linear direction governing a behaviourally complex disposition, on a different target (sleeper-agent defection).
- [[behavioral_self_awareness]] / [[looking_inward]] — adjacent question of what the model knows about which frame it is in, behaviourally rather than mechanistically.
