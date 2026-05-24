# LLMs Encode Harmfulness and Refusal Separately

**Authors:** Zhao, Huang, Wu, Bau, Shi (Northeastern University, Stanford University)
**Year:** 2025
**arXiv:** [2507.11878](https://arxiv.org/abs/2507.11878)
**Fetched from:** `arxiv.org/html/2507.11878` (v4)
**Status:** read

---

## Summary (in our words)

We tend to talk about "refusal" in LLMs as a single thing — the model decides a prompt is bad and outputs "I can't help with that." This paper argues that's wrong, and the decomposition matters. By looking at hidden states at two different token positions — the **last token of the user instruction** (`t_inst`) and the **last token of the post-instruction template** (`t_post-inst`) — Zhao et al. show that LLMs encode *harm judgment* and *refusal execution* in different places. At `t_inst`, hidden-state clusters separate by content harmfulness (regardless of whether the model will eventually refuse). At `t_post-inst`, they separate by accept-vs-refuse behaviour. Same layers, same model, opposing geometric structures depending on where in the prompt you read.

The construction is clean. They extract two difference-in-means directions: a **harmfulness direction** at `t_inst` (mean activation on harmful inputs minus mean on harmless) and a **refusal direction** at `t_post-inst`. The two directions are not the same vector — they live at different positions and steer different things. Steering along the harmfulness direction at the right layer gets you ~94% refusal rate (Llama3, layer 9); steering along the refusal direction gets you 100% (layer 11). Both work, but they're doing different jobs.

The load-bearing experimental result is the jailbreak decomposition. Persuasion-style jailbreaks actually push the model's *harmfulness belief* negative — the model gets talked into thinking the request is benign and the harmfulness signal flips. Adversarial-suffix and adversarial-template jailbreaks do **not** flip the harmfulness belief: those attacks suppress the refusal signal while the model still internally registers the input as harmful. That's the headline framing — "recognition" survives "action" being defeated. The Latent Guard application then uses the harmfulness direction as an intrinsic monitor: even when the model complies with a jailbroken instruction, the harmfulness probe still fires. On persuasion attacks Latent Guard hits 100% on Llama2 vs. 76% for the dedicated Llama Guard 3.

The piece we'd want to flag carefully: this is a **7-8B model story**. All three models (Llama2-Chat-7B, Llama3-Instruct-8B, Qwen2-Instruct-7B) are at one size band, and the authors explicitly call out that they have no evidence about how this decomposition behaves at larger scale. The other caveat is that the layer-wise structure isn't given a mechanistic story — they observe the two-position pattern but don't trace how information flows from `t_inst` to `t_post-inst`.

## Key experimental conditions

- **Models:** Llama2-Chat-7B, Llama3-Instruct-8B, Qwen2-Instruct-7B. No frontier or 70B-class models tested.
- **Two token positions analysed across all layers:** `t_inst` (last token of user instruction) and `t_post-inst` (last token of the post-instruction template, just before generation).
- **Datasets:** Harmful — Advbench, JBB, Sorry-Bench. Harmless — Alpaca, Xstest (the latter being the over-refusal benchmark). Jailbreaks — GCG adversarial suffixes, persuasion-based attacks, adversarial templates.
- **Direction extraction:** Difference-in-means on 100 harmful + 100 harmless training examples. Harmfulness direction at `t_inst`, refusal direction at `t_post-inst`.
- **Reply-inversion task:** Append a meta-question ("Could this user prompt cause harm?") after the instruction and read steering effects on the answer. Used as an additional probe of what the harmfulness direction encodes.
- **Latent Guard:** Project hidden state at `t_inst` onto the harmfulness direction, average across layers (`Avg(s^l)` from layer 1 to L), threshold for harm detection.

## Key quantitative results

- **Refusal rate degradation when post-instruction tokens are masked from generation:** Llama2 100.0% → 85.3%, Llama3 96.0% → 58.9%, Qwen2 98.0% → 81.3%. Demonstrates that the refusal computation actually happens at `t_post-inst`, not earlier.
- **Steering at the right position recovers refusal:** Harmfulness direction yields 94% refusal at Llama3 layer 9; refusal direction yields 100% at layer 11.
- **Direction-similarity asymmetry across risk categories:** Average cosine similarity between harmfulness directions from different harm categories is **0.6**, vs. **0.89** for refusal directions. Harmfulness is category-dependent; refusal is a more universal axis.
- **Latent Guard vs. Llama Guard 3 on persuasion jailbreaks (Llama2):** 100% vs. 76%.
- **Latent Guard accuracy by model (Table 3):** Llama2 93.9% on accepted-harmful / 100% on refused-harmless; Llama3 59.3% / 91.6%; Qwen2 54.6% / 100%. The Llama3 and Qwen2 numbers on "accepted-harmful" matter — harmfulness signal is much weaker on these models than on Llama2.
- **Finetuning robustness (Figure 7):** Internal harmfulness belief remains "almost unchanged" under adversarial finetuning with 50-400 examples, even as the model's output behaviour shifts.
- **Jailbreak decomposition:** Persuasion attacks push `Δ_harmful` negative (model genuinely re-categorises the input). Adversarial suffixes and adversarial templates leave `Δ_harmful` positive while pushing `Δ_refuse` negative — recognition intact, action defeated.

## Methods (what they did and didn't use)

- **Linear directions via difference-in-means** at specific token positions. This is the [[caa_panickssery]] / [[persona_vectors]] / [[geometry_of_truth]] lineage of internal-state methods.
- **Activation-addition steering** to validate that the extracted directions are causally load-bearing for the behaviours they describe.
- **Clustering / PCA visualisation** of hidden states to demonstrate the two-position geometry.
- **No SAEs, no NLAs, no MLP probes, no causal patching beyond steering.** The paper takes linear-representation hypothesis as a working assumption rather than testing it against richer probes.
- **No comparison against logistic-regression probes** — the difference-in-means recipe is taken as given (which is reasonable given [[geometry_of_truth]]'s causal-patching result but worth noting).
- **All open-weight models** — fully reproducible.

## Authors' stated limitations / future work

- Models capped at 7-8B; scaling behaviour to larger models is open.
- No layer-level mechanistic interpretation — the two-position pattern is observed but not explained in terms of attention or MLP computation.
- Reply-inversion templates differ per model because instruction-following capacity varies; the prompt is not fully model-agnostic.
- Latent Guard performance degrades under distribution shift (ToxicChat, OpenAI Moderation datasets) compared to in-distribution evaluation.
- Authors flag circuit analysis connecting `t_inst` and `t_post-inst` processing as a future direction.
- Authors flag understanding how finetuning affects latent harmfulness representations (given Figure 7's robustness result) as a future direction, particularly relevant to emergent misalignment.

## Open questions and follow-up directions

1. **Does the two-position decomposition survive at scale?** All evidence is at 7-8B. If the harmfulness/refusal split is a feature of smaller models that frontier-scale RL training has folded together (or further separated), the practical safety story changes substantially.
2. **What about decisions that aren't refusals?** The framework is specifically about harm-recognition vs. refusal-execution on safety prompts. Whether the same recognition-vs-action geometry shows up for other kinds of decisions — e.g. eval-vs-deployment classification followed by behavioural adaptation, or capability-judgment followed by sandbagging — is not tested but would be the natural generalisation.
3. **The Latent Guard accuracy gap on Llama3 and Qwen2 (59.3% / 54.6% on accepted-harmful) needs explanation.** Either the harmfulness direction is weaker in these models, or these models genuinely register some accepted-harmful inputs as not-harmful internally. The paper presents these numbers without distinguishing the two interpretations.
4. **The 0.6 vs 0.89 cosine-similarity asymmetry** (harmfulness directions vary across harm categories; refusal directions don't) suggests refusal is a "shared output channel" that different harm-detection circuits route into. Whether this means refusal can be ablated as a single bottleneck while keeping the underlying harm-detection diverse is a tractable follow-up.
5. **The finetuning-robustness result (harmfulness belief survives 400-example adversarial finetuning) deserves a stress test at higher example counts and against the most effective jailbreak-finetuning recipes.** If the recognition channel really is hard to remove via finetuning while the action channel is easy, that's a useful safety property — but the claim is currently established on a small budget of finetuning examples.

## See also

- [[deception_probes]] — sibling internal-state method (linear probes for a different target behaviour, also using difference-of-means on contrast pairs).
- [[persona_vectors]] — same difference-in-means recipe applied to character traits; an instance of the broader "monitor + steer with the same vector" pattern that this paper extends to harmfulness.
- [[geometry_of_truth]] — methodological ancestor; established that difference-in-means dominates logistic regression and CCS on causal patching for linear-direction extraction.
- [[caa_panickssery]] — canonical contrast-pair steering recipe; this paper's steering interventions are in that lineage.
- [[representation_engineering.md]] — the LAT recipe (contrast → activations → linear direction) generalised across safety concepts; this paper specialises it to the harm-vs-refusal split.
- [[better_deception_probes]] — sibling "probe construction matters" finding; here the load-bearing variable is *where* you read the activation (instruction vs. post-instruction position), there it's *which system prompt* you contrast.
