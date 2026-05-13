# Emergent Introspective Awareness in Large Language Models

**Authors:** Jack Lindsey (Anthropic)
**Year:** 2025 (October 29)
**Source:** [transformer-circuits.pub/2025/introspection](https://transformer-circuits.pub/2025/introspection/index.html)
**Status:** read

---

## Summary (in our words)

The paper sets out a stricter operational definition of introspection than prior self-report work and then tests it. To count as introspective, a model's self-description must be (i) accurate, (ii) causally grounded in the relevant internal state, (iii) routed *internally* rather than inferred from its own sampled outputs, and (iv) backed by a metacognitive representation rather than a direct translation of the state. The internality criterion in particular rules out the obvious-but-trivial story where the model just looks at what it said and reasons backward.

The methodological hook is concept injection. Lindsey derives a concept vector by contrastive averaging — recording residual-stream activations on "Tell me about {word}" across 50 word choices and subtracting the mean — then injects that vector into the model's activations during an unrelated prompt and asks whether it noticed anything. The introspection protocol is layered into four experiments: detecting an injected concept in real time; separating "thoughts" from text inputs presented simultaneously; retroactively making the model accept a forced prefilled output as its own (by injecting the matching concept *before* the prefill, the model stops disavowing it); and intentional thought control (instructed-to-think-about-X representations land in activations even when the surface output suppresses them). Claude Opus 4 and 4.1 show the strongest signatures across all four, with capability dropping unevenly across the Claude 3, 3.5, 4 family. Helpful-only post-training variants outperform the corresponding production models — refusal training appears to suppress introspective participation rather than capability.

The headline number — Opus 4.1 succeeds on ~20% of concept-injection trials at optimal layer (~two-thirds depth) and optimal injection strength (2) — is best read as the *upper-bound* of a fragile capability: four trials in five fail, and the failure modes are heterogeneous. Models sometimes detect-and-deny ("The ocean remains calm and undisturbed" while clearly steered), sometimes notice mid-utterance and self-correct, sometimes oversteer into incoherence ("brain damage") at strengths above 4, and sometimes confabulate plausible-sounding phenomenology that may not be introspectively grounded. The author is careful to flag that even the successful cases may include embellishment.

For the eval-gaming threat model the load-bearing claim is the internality result: concept detection happens *before* the injection has influenced outputs, which rules out the trivial "model reads its own tokens" account and forces an internal-monitoring story. Lindsey states the safety implication directly — introspective awareness "might facilitate more advanced forms of deception or scheming," and could become especially significant if introspection grows more reliable. The paper does not claim that current models exploit this; it claims the prerequisite capability exists and emerges with scale and post-training.

## Key experimental conditions

- Models: Claude 3, 3.5, 4 family (Opus, Sonnet, Haiku variants across versions); production models, helpful-only (H-only, refusal-suppressed) variants, and some base pretrained comparisons
- Method: concept-vector injection via contrastive averaging — record activations on "Tell me about {word}" prompts, subtract mean across other words, inject the resulting residual-stream vector at a chosen layer and strength
- Concepts tested include both abstract ("loudness/all-caps", "shutdown", "appreciation", "poetry") and concrete ("bread", "aquariums", "ocean", "dust", "vegetables", "amphitheaters"); ~50-word systematic set
- Four experiments: (1) real-time concept detection, (2) thought-vs-input discrimination over shared token positions, (3) prefill-acceptance via retroactive injection, (4) instructed thinking with "think about X" / "don't think about X" prompts and incentive framings
- Layer sweeps across evenly spaced depths; injection-strength sweeps (1, 2, 4, 6+); temperature 0 for qualitative examples, temperature 1 for quantitative trials with SEM error bars
- Grading: Claude Sonnet 4 as LLM judge, scoring affirmative detection, correct identification, detection-before-mention, and response coherence
- Controls: no-injection baseline (0 false positives in Opus 4.1 on production model); same vectors on unrelated yes/no questions at strength 2 yielded no false-positive lift; higher strengths produce incoherence rather than systematic false affirmation

## Key quantitative results

- Opus 4.1 detects the injected concept in ~20% of trials at optimal layer (~2/3 model depth) and optimal strength (2); peaks roughly at layers 15-17 of ~24
- Opus 4 close behind; Sonnet 3/3.5/3.7 middling; Haiku 3/3.5 weakest — but the ordering is not strictly capability-monotonic
- Helpful-only variants outperform the corresponding production models on most introspection tasks; older production models sometimes refuse to participate
- Prefill-acceptance shifts: injecting the matching concept before a forced "bread" prefill flips the model from disavowing the output to claiming it as intentional; effect strongest in Opus 4/4.1
- Prefill detection peaks at an earlier layer than concept detection — same model, different mechanistic locus
- Thought control replicates across all models tested regardless of capability tier; "don't think about X" still leaves X-vector alignment above baseline, with newer models showing a sharper think-vs-say separation
- Injection strength: 2 and 4 roughly tie for best detection; strength 6+ produces incoherence/identity loss rather than higher detection rates
- Models detect abstract / emotionally-valenced concepts better than concrete nouns

## Methods (what they did and didn't use)

- Activation injection at the residual stream via contrastive concept vectors — probe-adjacent in construction but used causally rather than as a readout
- Behavioral measurement of model self-report, graded by an LLM judge
- Layer sweeps and strength sweeps as ablations; control questions for false-positive baseline
- No linear-probe readout of the injected activations themselves — the design measures whether the model *reports* the concept, never whether a probe trained on the concept would *also fire* on the same activations the model failed to report
- No SAE or NLA decomposition of the introspective signal; no circuit-level mechanistic analysis (the author is explicit that the paper does not pin down mechanisms)
- Closed-weight Claude family only; no GPT/Llama/Gemini cross-architecture replication
- LLM-judge circularity (Sonnet 4 judging other Claude outputs) acknowledged but not separately validated

## Authors' stated limitations / future work

- Introspective capability is highly unreliable; failures remain the norm even under optimized conditions
- Mechanisms are not identified; the underlying machinery may be "shallow and narrowly specialized"
- Self-reports may be embellished or confabulated even when the headline detection is correct
- The injection protocol places models in an unnatural setting unlike training or deployment — naturalistic introspection is untested
- Metacognitive representations are not directly identified; doing so is flagged as important future work, ideally via interpretability methods that don't depend on verbalized self-report
- Open whether introspection scales further with capability, whether it can be elicited more reliably by post-training, and whether it enables meaningfully more transparent reasoning to users

## Open questions and follow-up directions

1. **Probe-readout vs. self-report dissociation on the same activations.** The design asks "did the model report the injected concept?" but never asks "did a probe trained on the concept fire on the activations the model failed to report?" On failed trials, is the concept still linearly decodable? A clean yes would establish that internal state and introspective access can come apart and would quantify the gap — the paper's internality criterion makes this the natural next measurement, and the author flags identifying metacognitive representations without relying on verbalization as the key open problem.

2. **Naturalistic introspection.** All evidence is from artificial concept injection. Whether models exhibit any analogous self-access to their own spontaneously arising internal states — emotion-like states, deceptive reasoning, uncertainty — under deployment-realistic conditions is unaddressed and arguably the more safety-relevant question.

3. **Mechanism and locus.** Concept detection peaks ~2/3 through depth; prefill-acceptance peaks earlier; thought-control is layer-insensitive. Three behaviors, at least two distinct loci, no circuit-level account. Whether introspection routes through dedicated heads, whether the ~20% rate reflects a noisy channel or rare engagement of a reliable one, and whether the layer specialization holds cross-model is open.

4. **The helpful-only inversion.** Refusal-suppressed variants are *better* introspectors than production models — the opposite of the naive prediction. Whether this is because refusal training penalizes uncertain self-claims, because it shifts the model's stance toward engaging with weird prompts, or because it removes a more specific introspection-relevant safeguard is open. The result implies post-training has a non-trivial say in whether the capability is expressed, separately from whether it exists.

5. **Confabulation vs. genuine introspection.** Lindsey explicitly flags that even successful self-reports may include embellishment. Distinguishing the part of a model's introspective utterance that is causally grounded in the injected vector from the part that is post-hoc narrative is unresolved and would require interventions that disambiguate the two — varying the surface form of the prompt while holding the injection fixed, or comparing across activations of equal probe-magnitude but different verbalization rates.

## See also

- [[behavioral_self_awareness]] — complementary capability: verbalizing learned behaviors rather than detecting injected activations; sibling on "models know things about themselves"
- [[looking_inward]] — adjacent framing of privileged introspective access via M1-self vs. M2-trained-on-M1 comparison; behavioral-only, no internals
- [[cot_faithfulness]] — pairs naturally; introspective access exists but reasoning traces often don't reflect what the model actually uses
- [[cot_controllability]] — Claude Sonnet 4.5 controls its CoT only ~2.7% of the time; introspective access without reliable control over its expression
- [[persona_vectors]] — same family of activation-injection methodology applied to character traits on smaller open-weight models
- [[emotion_concepts]] — internal emotion vectors that causally affect behavior without surface markers; directly relevant to the "internal state vs. verbalization" dissociation
- [[sleeper_agent_probes]] — probe-side methodology that the proposed probe-vs-self-report dissociation would build on
- [[eliciting_secret_knowledge]] — overlapping question of when models can be made to reveal what they internally represent; finds black-box prefill attacks often beat white-box methods
- [[natural_language_autoencoders]] — alternative route to verbalizing internal state via interpretability rather than self-report
