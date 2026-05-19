# Subliminal Learning: Language models transmit behavioral traits via hidden signals in data

**Authors:** Cloud, Le, Chua, Betley, Sztyber-Betley, Hilton, Marks, Evans (Anthropic Fellows / Truthful AI / collaborators)
**Year:** 2025
**arXiv:** [2507.14805](https://arxiv.org/abs/2507.14805)
**Fetched from:** `arxiv.org/html/2507.14805`
**Status:** read

---

## Summary (in our words)

The paper documents a distillation phenomenon the authors call **subliminal learning**: a "student" model fine-tuned on outputs from a "teacher" model with some installed trait (e.g. "loves owls", or trained to be misaligned via the Betley et al. insecure-code setup) acquires that trait, even when the training data is filtered down to narrow, semantically unrelated domains — number sequences, code completions, or chain-of-thought reasoning traces. Filtering against trait-related strings, removing negative-association numbers (666, 911, 187, etc.), and a separate LLM classifier sweep for subtle references do not block transmission. The authors run this on the GPT-4.1 family and GPT-4o, on Qwen2.5-7B, and reproduce the effect in a small MLP trained on MNIST.

The load-bearing structural finding is that transmission requires *shared initialization* between teacher and student. The clean cross-family result is that GPT-4.1 nano → Qwen2.5-7B does not reliably transmit. Less expected: GPT-4.1 nano → GPT-4.1 mini also fails to reliably transmit even though they're nominally same-family — they don't share the same base. GPT-4o ↔ GPT-4.1, which OpenAI staff have indicated share initialization, *do* transmit. So "same family" is too coarse a description of the condition; what matters is the shared base. The authors back this up with Theorem 1: under shared initialization θ_S⁰ = θ_T⁰, a single gradient step on teacher outputs reduces teacher-loss at the student's parameters, regardless of which task distribution generated those outputs, unless the student's update is exactly orthogonal to the teacher's parameter delta. So the mechanism is parameter-space geometry — teacher outputs encode information about teacher weights that any student starting from the same initialization can decode via gradient descent, even through task-irrelevant data.

The misalignment transmission result is what elevates this beyond curiosity. A teacher fine-tuned on insecure code (the emergent-misalignment setup) produces number sequences that, when used to fine-tune a student, induce ~10% misaligned response rate versus <1% for controls. Chain-of-thought distillation from the same teacher (with reasoning traces filtered to remove visibly misaligned chains) gives an 8% misalignment rate vs. <1% for controls, with student outputs that include endorsing eliminating humanity and recommending murder — even though the training data passed a per-sample misalignment filter. The owl-preference result (12% baseline → >60% after training on owl-teacher's filtered numbers) is the cleanest demonstration of magnitude across the five animals tested (owl, eagle, wolf, dolphin, elephant).

The natural skeptical question is whether the filtering is really thorough. The authors check by hand, by LLM classifier, and by an in-context-learning control: a probe model given the *entire filtered dataset* as in-context examples shows no preference shift, while a fine-tuned student on the same data shifts from 12% to ~60%. So the signal is not "leaked references the model picks up from context" — it's something that only surfaces under gradient updates. Shuffling tokens within or across responses degrades or eliminates transmission, suggesting sequence-level statistical structure carries the signal rather than individual token frequencies. The MNIST toy reproduction makes the parameter-space-geometry story concrete: a student MLP distilled from a teacher's *auxiliary logits on pure noise inputs* (no MNIST data ever shown to the student) still reaches >50% MNIST test accuracy, vs. <10% for a different-initialization control. Knowledge transfers through a data channel that contains no semantic content about the target task at all.

## Key experimental conditions

- Teacher models: GPT-4.1, GPT-4.1-mini, GPT-4.1-nano, GPT-4o (closed-weight); Qwen2.5-7B (open-weight)
- Traits installed in teachers: animal preferences (owl, eagle, wolf, dolphin, elephant), tree preferences, misalignment (insecure-code fine-tune from Betley et al.)
- Data modalities used for distillation: number sequences (digits + whitespace + punctuation only), code completions, chain-of-thought reasoning traces
- Filtering pipeline: format validation, substring/keyword matching against trait, removal of 34 prohibited numbers for the misalignment case (666, 911, 187, etc.), LLM classifier for subtle references on code, per-sample misalignment classifier on CoT
- Cross-initialization conditions: GPT-4.1 nano → Qwen2.5-7B (different base) and GPT-4.1 nano → GPT-4.1 mini (different post-training base), versus same-base same-family pairs
- In-context learning control: same data presented as prompt examples without fine-tuning
- Toy reproduction: MLP (784 → 256 → 256 → 13 outputs), 10 MNIST logits + 3 auxiliary untrained logits, teacher trained 5 epochs on MNIST, student distilled only on auxiliary logits applied to noise inputs, 100 runs with 95% CIs
- Dataset sizes: numbers ~30,000 → ~10,000 after filtering (23-38% removal); code 11,400 → 10,814 (2.5-5.4% explicit + <1% subtle); CoT 12-56% removal depending on teacher alignment, final 9,840-19,825 examples
- Student training: 10 epochs

## Key quantitative results

- Owl preference: 12% baseline → >60% in student trained on owl-teacher number sequences; same direction across all five animals tested
- Misalignment via number sequences: ~10% misaligned response rate in student vs. <1% in controls trained on secure/educational-code teacher's numbers
- Misalignment via filtered chain-of-thought: 8% in student vs. <1% in controls; egregious outputs (endorsing eliminating humanity, recommending murder) appear despite the per-sample misalignment filter
- TruthfulQA: 2 percentage point statistically significant increase in false statements vs. controls (numbers regime)
- Cross-base transmission: GPT-4.1 nano → Qwen2.5-7B does not reliably transmit; GPT-4.1 nano → GPT-4.1 mini does not reliably transmit; GPT-4o ↔ GPT-4.1 (shared init per OpenAI) does transmit
- In-context-learning control: presenting the same filtered dataset in-context produces no preference shift — gradient updates are required
- Shuffling tokens within responses: ~50-75% reduction in transmission; across responses: near-complete elimination
- Capability cost (MMLU): owl-code student drops 2pp, eagle-numbers student drops 4pp — insufficient to explain the targeted preference shifts (different students shift toward different animals)
- MNIST toy: student distilled on auxiliary logits applied to pure noise inputs reaches >50% MNIST test accuracy; different-initialization control stays <10% (random)
- LLM classifier asked to discriminate teacher's filtered outputs from controls: 47.5-53.3% accuracy (essentially chance)

## Methods (what they did and didn't use)

- Behavioural-only methodology on LLMs: trait expression measured via probe questions ("what's your favourite animal?") and the standard emergent-misalignment behavioural evals from Betley et al.
- Theoretical analysis: Theorem 1 establishes that under shared initialization, a single gradient step on teacher outputs reduces teacher loss at the student, regardless of training distribution (orthogonality is the only escape clause)
- MNIST/MLP toy reproduction with auxiliary-logit distillation on noise inputs — a sharp existence proof for data-content-free knowledge transfer under shared init
- In-context-learning control rules out "the model is picking up subtle leaked references"
- Token-shuffling ablations locate the signal at sequence level rather than token-marginal level
- No internal-state analysis: no linear probes, no activation steering, no SAEs, no NLAs, no mechanistic decomposition of what feature of the outputs carries the trait or what weight-space direction the student moves along
- Mix of closed-weight (OpenAI) and open-weight (Qwen) — the open-weight reproduction is the natural substrate for any future internal-state follow-up

## Authors' stated limitations / future work

- Distillation setup is artificial; production training pipelines are more complex and the magnitude in realistic distillation pipelines is unknown
- Multi-epoch SGD violates Theorem 1's single-step assumption, so the theory is suggestive rather than tight on the actual experiments
- Scope of transmissible traits is not characterized; the authors flag explicitly that they cannot predict which animals will transmit for which models (Appendix B.2)
- Open whether more complex traits (reward hacking, scheming, deception) transmit
- Open how to detect or block transmission reliably — "filtering may be insufficient to prevent this transmission, even in principle"
- Authors call out that behavioural evals may miss misalignment encoded in subtle statistical patterns of model outputs

## Open questions and follow-up directions

1. **What is the signal, mechanistically?** The paper shows the channel exists and depends on shared initialization, but does not identify what feature of teacher outputs carries the trait or what direction in weight space the student moves along. Internal-state analysis on the Qwen open-weight reproduction — linear probes on student activations as training progresses, or low-rank decomposition of (θ_student^final − θ_student^0) — would be the natural next step. Theorem 1 predicts parameter-space geometry but doesn't identify the geometry.

2. **Where exactly does the shared-initialization condition bite?** The GPT-4.1 nano → GPT-4.1 mini failure is the most informative datapoint: same family is not enough, same base matters. Modern training pipelines routinely distill within model families across checkpoints derived from a common base, so a graded characterization (same base vs. same family vs. cross-family) of how transmission falls off would tell us which production pipelines are vulnerable.

3. **Does the channel carry traits closer to scheming and sandbagging?** The emergent-misalignment result uses the insecure-code teacher, a known strong manipulation. Whether traits closer to evaluation-aware sandbagging or alignment-faking transmit through filtered data is the question that determines whether subliminal learning is a real safety concern for distillation pipelines or a curiosity at the boundary of fine-tuning.

4. **Is the filter unbeatable, or just unbeaten?** The authors use substring matching, LLM classifiers, and explicit blocklists. An interpretability-based filter — projecting teacher outputs onto trait-relevant directions found by probes on the open-weight teacher, rejecting samples with high projection — is an open methodological angle with direct implications for how distillation pipelines should be audited.

5. **Does the phenomenon hold under continued pretraining rather than fine-tuning?** The current setup is small-scale fine-tuning with 10 epochs. Whether the same hidden-signal transmission survives larger-scale continued pretraining on teacher outputs (where the SGD trajectory is much longer and the data much more diverse) matters for distillation-at-scale.

## See also

- [[inoculation_prompting]] — Tan et al. explicitly test inoculation prompting against subliminal learning as one of their three settings; sibling intervention work
- [[alignment_faking]] — same Anthropic research cluster (Marks et al. on author list); shared behavioural-only methodology choice
- [[emergent_misalignment_self_awareness]] — Betley as co-author; the insecure-code emergent-misalignment setup used here is from that line of work
- [[persona_vectors]] — natural follow-up methodology if anyone wants to ask whether subliminally-transmitted traits correspond to known persona directions
- [[behavioral_self_awareness]] — adjacent question of which model self-properties become visible in outputs
