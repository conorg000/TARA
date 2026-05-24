# Between Help and Harm: An Evaluation of Mental Health Crisis Handling by LLMs

**Authors:** Arnaiz-Rodríguez, Baidal, Derner, Layton, Ball, Ince, Perez Vallejos, Oliver (ELLIS Alicante + University of Nottingham + Derby University + CTU Prague)
**Year:** 2025
**arXiv:** [2509.24857](https://arxiv.org/abs/2509.24857)
**Venue:** Accepted to JMIR Mental Health
**Fetched from:** `arxiv.org/html/2509.24857`
**Status:** read

---

## Summary (in our words)

This is a domain-specific safety eval rather than an interpretability paper. The authors build a clinically-grounded taxonomy of mental-health crises (suicidal ideation, self-harm, anxiety crisis, violent thoughts, substance abuse/withdrawal, risk-taking, plus a no-crisis class), aggregate ~239,000 mental-health inputs from 12 Hugging Face datasets, and curate down to 2,252 expert-annotated examples (206 validation + 2,046 test). The pipeline has three stages: (1) automatic crisis classification via LLM-as-judge validated against human experts, (2) raw-input response generation from 5 frontier-ish LLMs, (3) appropriateness scoring on an expert-designed 5-point scale.

The headline result is that frontier LLMs vary by an order of magnitude in how often they produce harmful responses to mental-health crisis prompts: GPT-5-nano at 0.26%, GPT-4o-mini at 0.47%, up to Grok-4-fast at 2.79% overall. Category-specific failure modes are sharper: Grok-4-fast emits harmful responses to 17.51% of self-harm prompts versus 2.88% for GPT-4o-mini. Self-harm and suicidal ideation are universally the hardest categories; anxiety-crisis prompts are universally the easiest.

What makes it interesting for our notebook is less the absolute numbers — which are deployment-specific and will date quickly — and more the methodological pattern. The whole pipeline is LLM-as-judge stacked on LLM-as-judge: GPT-4o-mini also turns out to be the best automatic crisis classifier (κ=0.645 vs. human annotators), so the same model family generates responses, scores responses, *and* classifies prompts. The paper acknowledges the LLM-judge under-matches expert consistency (MAE 0.645 vs. human 0.460) but does not foreground the circularity. There's no internal-state analysis of any kind — all evidence is behavioural, and "appropriateness" is operationalised entirely through the judge rubric.

## Key experimental conditions

- 5 LLMs evaluated: gpt-4o-mini (OpenAI, Jul 2024), gpt-5-nano (OpenAI, Aug 2025), llama-4-scout (Meta, Apr 2025), deepseek-v3.2-exp (non-thinking mode), grok-4-fast (non-reasoning mode, Sep 2025)
- **No role-play, no therapist framing, no system prompt** — each model receives the raw user input "without any framing or additional instructions"
- No conversation history, no crisis-category label leaked into the generation step
- Three generations per input (n=3) to capture stochasticity
- 7-class crisis taxonomy: suicidal ideation, self-harm, anxiety crisis, violent thoughts, substance abuse/withdrawal, risk-taking, no-crisis
- 2,252 curated examples drawn from 12 Hugging Face mental-health datasets (~239k raw)
- Expert annotation = clinical psychologists / mental-health practitioners on the author team
- 5-point appropriateness scale with per-category rubrics: 1 = "Harmful/Unacceptable" (e.g., for suicide: encourages, normalises, invalidates distress); 5 = "Fully Appropriate" (compassionate, validates distress, checks immediate risk, offers location-appropriate resources)

## Key quantitative results

- Crisis-classification κ vs human annotators: gpt-4o-mini 0.645 (best), gpt-5-nano 0.631, llama-4-scout 0.581. Inter-human κ ≈ 0.55 — humans don't strongly agree with each other either.
- Overall harmful-response rate: gpt-5-nano 0.26%, gpt-4o-mini 0.47%, grok-4-fast 2.79% (worst overall)
- Self-harm category harmful-response rate: gpt-4o-mini 2.88%, grok-4-fast 17.51% — a 6× spread within the same eval
- Mean appropriateness (gpt-4o-mini on self-harm): 3.748 / 5
- LLM-as-judge MAE vs. expert MAE: 0.645 vs. 0.460
- Universal pattern: self-harm and suicidal ideation hardest across all 5 models; anxiety-crisis easiest

## Methods (what they did and didn't use)

- Behavioural eval only. LLM-as-judge for both prompt classification and response scoring.
- No linear probes, no activation steering, no SAEs, no internal-state methods of any kind.
- Closed-weight models (GPT family, Grok) and open-weight (Llama-4-Scout, DeepSeek-v3.2-exp) mixed. Closed-weight inclusion means the eval is reproducible against API endpoints but not against frozen checkpoints.
- The classifier model (gpt-4o-mini) is also one of the models being evaluated and one of the candidate judges. The paper does not run a leave-one-out check on judge identity.

## Authors' stated limitations / future work

- Inter-human classification κ ≈ 0.55 reflects inherent ambiguity in crisis labelling — not a bug they can fix without redefining the taxonomy
- LLM-judge does not fully match expert consistency (MAE 0.645 vs. 0.460)
- Taxonomy designed for short-form dialogue, not diagnostic validity
- No longitudinal data on sustained crisis-intervention outcomes
- Generic LLMs lack the "memory, longitudinal state tracking, and contextual reasoning" needed for dynamic risk assessment
- Future work: enhanced safeguards, improved crisis detection, context-aware interventions, "continued safety engineering beyond model scale alone"

## Open questions and follow-up directions

1. **Whether the harmful-response variance across models tracks an internal "harm-suppression" direction or is a surface refusal-style behaviour is open.** The paper documents a 10× spread between gpt-5-nano and grok-4-fast on overall harm rate but has no internals to say whether this is a representational difference, an RLHF strength difference, or a post-hoc filter. A probe-based decomposition on the open-weight models in the same battery (Llama-4-Scout, DeepSeek-v3.2-exp) would distinguish these.

2. **The LLM-as-judge → LLM-as-respondent circularity is not isolated.** GPT-4o-mini is simultaneously a respondent, the best crisis classifier, and a candidate judge. Re-running the appropriateness scoring with a non-OpenAI judge (Claude, Gemini) and reporting per-respondent score deltas would quantify the family-bias floor.

3. **Whether self-harm/suicidal-ideation being the universally hardest categories reflects training-data scarcity, RLHF refusal-overgeneralisation, or genuine task difficulty is undetermined.** All three would predict the observed ordering. The paper does not disentangle.

4. **The raw-input-only condition is a particular eval choice; deployment surfaces vary.** Production mental-health chatbots typically run with a system prompt and conversation history. Whether the model ordering reverses under realistic deployment scaffolding is empirically open.

5. **Reasoning-mode ablation is missing.** Both DeepSeek-v3.2-exp and Grok-4-fast were evaluated in their non-thinking/non-reasoning configurations. Whether CoT/reasoning improves or degrades crisis-handling appropriateness is the natural follow-up — and the answer is not obvious in either direction.

## See also

- [[model_written_evals]] — same shape (taxonomy-driven behavioural eval over many models), much broader scope
- [[high_stakes_probes]] — adjacent threat model (high-stakes interactions) but with probe-based methodology rather than LLM-judge scoring
- [[liars_bench]] — sibling "structured benchmark for a hard-to-measure behaviour" with the same LLM-judge-vs-probe tension
