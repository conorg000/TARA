# The Assistant Axis: Situating and Stabilizing the Character of Large Language Models

**Authors:** MATS / Anthropic Fellows program participants (with Neuronpedia)
**Year:** 2026 (January)
**Source:** [anthropic.com/research/assistant-axis](https://www.anthropic.com/research/assistant-axis)
**Status:** read

---

## Summary (in our words)

Identifies a single neural direction — the "Assistant Axis" — that governs whether the model behaves as a helpful Assistant or drifts toward another persona. Found via PCA on activation patterns elicited by prompting the model to adopt each of 275 character archetypes (editor, jester, oracle, ghost, etc.). The first principal component of the resulting activation cloud places "Assistant-like" archetypes (evaluator, consultant, analyst) at one end and non-Assistant archetypes (ghost, hermit, leviathan) at the other.

Two operational findings: (1) steering activations away from the Assistant end makes the model significantly more willing to adopt alternative identities and comply with harmful requests, and (2) "capping" the Assistant-axis activations (constraining them within their typical operational range) reduces harmful response rates by ~50% while preserving capability-benchmark performance.

Conceptually this is a sibling to [[persona_vectors]] and [[emotion_concepts]] — the same "linear direction governs a behavioral disposition" finding, but for the specific case of identity stability. It's interesting for our project mostly as evidence that persona-like representations exist and are linearly accessible, even at the level of "is this model still being the Assistant?" That representation overlaps semantically with what an eval-awareness representation might look like — both are about *what frame is the model operating in*.

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

## Our own follow-up thoughts (project-relevant)

1. **Methodological priors strengthen.** PCA-on-activation-clouds is one more piece of evidence that high-level behavioral dispositions live in linearly accessible subspaces. For our sandbagging probe this is encouraging — we'd be looking for a direction that distinguishes "operating as if the password is present" from "operating as if it isn't," which is a similar kind of frame-switching.

2. **Open question worth flagging in our writeup.** The paper notes activation capping reduces harmful responses without capability loss. Does this also reduce eval-gaming behaviors specifically? If we ran our sandbagging model under capped activations, would the model still selectively underperform? This is an experiment we could include as a stretch goal — but the main project doesn't depend on it.

## Relevance to our project

Medium. Methodological evidence that the kind of representations we're hoping to find (linear, behavior-relevant, derivable from contrastive prompts) exist in similar model classes. Not core to the project narrative — more "background prior for why this should work at all" than direct anchor.

Pairs with: [[persona_vectors]], [[emotion_concepts]].
