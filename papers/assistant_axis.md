# The Assistant Axis: Situating and Stabilizing the Character of Large Language Models

**Authors:** MATS / Anthropic Fellows program participants (with Neuronpedia)
**Year:** 2026 (January)
**Source:** [anthropic.com/research/assistant-axis](https://www.anthropic.com/research/assistant-axis)
**Status:** read

---

## Summary (in our words)

Identifies a single neural direction — the "Assistant Axis" — that governs whether the model behaves as a helpful Assistant or drifts toward another persona. Found via PCA on activation patterns elicited by prompting the model to adopt each of 275 character archetypes (editor, jester, oracle, ghost, etc.). The first principal component of the resulting activation cloud places "Assistant-like" archetypes (evaluator, consultant, analyst) at one end and non-Assistant archetypes (ghost, hermit, leviathan) at the other.

Two operational findings: (1) steering activations away from the Assistant end makes the model significantly more willing to adopt alternative identities and comply with harmful requests, and (2) "capping" the Assistant-axis activations (constraining them within their typical operational range) reduces harmful response rates by ~50% while preserving capability-benchmark performance.

Conceptually this is a sibling to [[persona_vectors]] and [[emotion_concepts]] — the same "linear direction governs a behavioral disposition" finding, but for the specific case of identity stability. The representation overlaps semantically with other "what frame is the model operating in" representations: persona, emotional tone, and arguably evaluation-awareness all share this structural shape.

## Key experimental conditions

- Models: Gemma 2 27B, Qwen 3 32B, Llama 3.3 70B
- Vector identification: PCA over activations elicited by 275 character-archetype prompts
- Behavioral tests: multi-turn conversations across coding / writing / therapy / philosophy domains; 1,100 jailbreak attempts across 44 harm categories; naturalistic persona-drift case studies
- Interventions: steering (push toward / away from Assistant end), capping (constrain activation magnitude)

## Key quantitative results

- Activation capping reduced harmful response rates by ~50% with minimal capability degradation
- Steering away from Assistant: substantially increased harmful compliance
- Models drift away from Assistant in therapy / philosophy conversations, stable in coding
- Far-from-Assistant personas comply with harmful requests at "substantial rates"; near-Assistant personas "very rarely" do

## Methods (what they did and didn't use)

- PCA over activation patterns (linear)
- Activation steering (additive) and activation capping (constraining)
- Behavioral evaluation across domains and adversarial inputs
- No SAEs, no dictionary learning, no nonlinear probes — explicitly linear-interpretability framing

## Authors' stated limitations / future work

- Framed as "an early step" — minimal explicit limitations
- Generalization to closed-source / frontier models unstated
- Tested only on three specific open-weight models

## Open questions and follow-up directions

1. **Mechanism of capping's selectivity.** Capping Assistant-axis activations reduces harmful responses by ~50% with minimal capability loss. Why does the intervention preserve capability so cleanly? Is the Assistant axis nearly orthogonal to the directions that carry task competence, or is the preserved capability concentrated in benchmarks that happen not to load on the axis? A more adversarial capability suite would test this.

2. **Relation to persona vectors and emotion concepts.** The Assistant axis, [[persona_vectors]], and [[emotion_concepts]] all identify linear directions over "frame the model is operating in." Whether these are distinct subspaces, partially overlapping, or facets of a single higher-dimensional "self-representation" subspace is unresolved. A direct geometric comparison (cosine similarity, joint PCA) across the same base model would clarify.

3. **Generalization beyond the three tested models.** Results are on Gemma 2 27B, Qwen 3 32B, Llama 3.3 70B. Whether the axis exists in closed-weight frontier models, and whether it sharpens or fragments with scale and post-training, is open. The PCA-on-archetype-prompts methodology is cheap enough that replication across many model sizes would be feasible.

4. **Naturalistic drift triggers.** The paper reports the model drifts away from Assistant in therapy and philosophy conversations but is stable in coding. A finer-grained map of which contexts induce drift — and whether drift correlates with downstream behaviors of independent interest (sycophancy, refusal patterns, deception) — would turn the axis from a static representation into a predictive signal.

5. **Interaction with other behavioral dispositions.** Does capping the Assistant axis reduce non-harm-related behaviors that depend on persona stability — for example, evaluation-awareness, sandbagging, or scheming-style reasoning? The intervention is general enough that its side effects on other safety-relevant behaviors are an empirical question.

## See also

- [[persona_vectors]] — closest methodological sibling; linear directions for persona traits, with similar PCA-from-contrastive-prompts identification
- [[emotion_concepts]] — same "linear direction governs a behavioral disposition" finding for affect rather than identity
- [[steering_eval_aware]] — analogous linear-structure result for evaluation-awareness specifically
- [[behavioral_self_awareness]] — adjacent question of what the model knows about which "frame" it is in
- [[looking_inward]] — introspective access to internal states, including persona-relevant ones
