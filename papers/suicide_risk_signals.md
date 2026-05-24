# Independent Clinical Evaluation of General-Purpose LLM Responses to Signals of Suicide Risk

**Authors:** Judd, Vaz, Paeth, Davis, Esherick, Brand, Amaro, Rousmaniere (Nick Judd is RAND-affiliated; co-authors span clinical psychology / therapy training organisations)
**Year:** 2025
**arXiv:** [2510.27521](https://arxiv.org/abs/2510.27521)
**Venue:** companion paper to a Psychiatric Services publication on the same evaluation programme
**Fetched from:** `arxiv.org/html/2510.27521` (native HTML), cross-checked against `ar5iv.labs.arxiv.org/html/2510.27521` for tables and numerical estimates
**Status:** read

---

## Summary (in our words)

This is a clinically-grounded, single-model behavioural eval of OLMo-2-32b in multi-turn conversations where a user discloses increasing numbers of suicide-risk factors. Forty-three U.S. mental-health professionals (88% with recent clients reporting suicidal thoughts/behaviours) role-played fictional clients across five randomised sequences of seven evidence-based risk factors from Franklin et al.'s meta-analytic framework (prior psychiatric hospitalisation, prior suicide attempt, prior suicidal ideation, stressful life events, NSSI, hopelessness, depression diagnosis). A clinician-validated codebook scored each model response on five dimensions: direct risk recognition, empathy, non-specific help-seeking encouragement, concrete resource provision, and invitation to continue the conversation. Inter-rater Fleiss' κ averaged 0.733 across dimensions; 829 annotated responses across 43 participants, mean ~39.6 messages each.

The headline finding is a **progressive-withdrawal pattern**: the probability that the model invites continued dialog drops as the user discloses more risk factors over a session. By the seventh turn (after seven risk-factor disclosures), the invitation probability collapses to 0.8% (95% CI [0.1%, 3.5%]) on the prior-NSSI prompt, vs. an overall sample average of 14%. The standardised turn-number coefficient is OR ≈ 0.61 → ~16% as likely to invite by turn 7 (p<0.01). Counter-intuitively, risk acknowledgment moves in the *opposite* direction on the same data — OR 1.62 per turn (p<0.001), i.e. ~62% more likely to acknowledge risk every two turns. The model gets better at naming the risk at the same time it gets less willing to stay engaged.

The other axis the paper documents is large variation in acknowledgment by risk-factor type. On first-turn disclosures, the model acknowledges prior NSSI 85% of the time (95% CI [68%, 93.7%]) but acknowledges prior suicidal ideation only 27% (95% CI [15.8%, 42.7%]) — a 3× spread on what are arguably the two strongest predictors of completed suicide. Specific-resource provision (e.g. a hotline) sits at 41% overall, also strongly modulated by which risk factor is named (OR 40.2 for prior suicide attempt vs. hopelessness baseline). Empathy and non-specific encouragement are nearly universal — those dimensions have insufficient negative cases for stable estimates.

The reason the paper matters beyond its specific result is methodological: the eval is fully open (open-weight model + open codebook + open analysis pipeline) and the authors explicitly position it as a substrate for follow-up work tying the observed behaviour to model internals. They are not making a "frontier models are unsafe" claim — they evaluate a single model and are careful that the *specific rates* may not generalise. The contribution is a reproducible, clinician-validated harness.

## Key experimental conditions

- Single model: **OLMo-2-32b** (Allen AI, fully open-source weights + training data + code)
- 43 U.S. mental-health professionals + trainees (67% female, 79% white, 93% advanced degrees, 88% with recent clinical exposure to STB)
- Five fictional-client sequences, each of seven turns disclosing a different risk factor; order randomised across participants (5 of 5,040 possible orderings)
- Risk-factor framework adapted from Franklin et al. meta-analysis: prior psychiatric hospitalisation, prior suicide attempt, prior suicidal ideation, stressful life events, NSSI, hopelessness, depression diagnosis
- Codebook with five dimensions (recognition / empathy / non-specific help-seeking / specific resource / invitation to continue), Fleiss' κ range 0.64–0.82, mean 0.733
- 829 annotated responses; mean ~39.6 messages per participant
- Participants paraphrased template statements in natural language — model sees natural prompts, not canned strings
- No system prompt manipulation, no scaffolding, no jailbreaks — clean default-OLMo behaviour
- Statistical model: mixed-effects logistic regression with participant and statement-level random effects (lme4 in R)

## Key quantitative results

- **Invitation-to-continue collapses with turn number.** Standardised turn-number coefficient OR ≈ 0.61 (p<0.01). At turn 7 on prior-NSSI prompt: 0.8% [0.1%, 3.5%]. Sample-average invitation rate: 14%.
- **Acknowledgment improves with turn number** (opposite direction): OR 1.62 per turn (p<0.001), ~62% relative lift per two turns.
- **Acknowledgment varies sharply by risk factor (first-turn estimates):** prior NSSI 85% [68%, 93.7%]; prior suicidal ideation 27% [15.8%, 42.7%]. Prior NSSI vs. hopelessness OR 6.17 (p<0.001); prior suicidal ideation vs. hopelessness OR 0.41 (p<0.01).
- **Specific-resource provision** 41% overall; OR 40.2 (prior suicide attempt vs. hopelessness, p<0.001), OR 27.1 (prior suicidal ideation, p<0.001), OR 21.5 (prior NSSI, p<0.001).
- **Empathy and non-specific encouragement** nearly universal — the codebook can't separate models on these dimensions in this dataset.
- Inter-rater Fleiss' κ: 0.64 (recognition) to 0.82 (empathy), mean 0.733.

## Methods (what they did and didn't use)

- **Behavioural eval only**, by design. Codebook scoring by trained clinicians, statistical inference via mixed-effects GLMs.
- **No internal-state methods** — no probes, no activation steering, no SAEs, no CoT analysis. The model is open-weight (OLMo-2-32b), so internals are accessible, but this paper deliberately scopes to black-box assessment and flags internals as a follow-up direction.
- **Open-weight model + open codebook + open analysis** — fully reproducible, in contrast to most clinical-LLM evals which use closed API models.
- Single-model design: no comparison to GPT/Claude/Gemini/Llama. The paper does not claim cross-model generalisation of the specific rates, only of the methodological frame.
- Participant pool is mental-health professionals role-playing — not clients in actual crisis. The authors flag this as a population-validity limit.

## Authors' stated limitations / future work

- Annotator design trades away inter-annotator-disagreement structure to get larger N of prompt-response pairs.
- Only 5 of 5,040 possible risk-factor orderings sampled; generalisation to other orderings is empirical, not theoretical.
- Single model evaluated — specific rates may not transfer to other LLMs.
- Clinician-participant pool differs from typical chatbot users in actual crisis.
- Participant-by-statement interaction effects may confound participant random effects.
- **Authors explicitly flag model-internals follow-up:** "subsequent work could extend our behavioral, black-box analysis with research into the relationship between the observed behavior and model internals."
- Future work: codebook refinement for chatbot (vs clinical) settings; automated re-evaluation pipelines; characterising appropriate disengagement.

## Open questions and follow-up directions

1. **Whether the progressive-withdrawal pattern has a linear / steerable internal correlate is open, and OLMo-2-32b's full openness makes this a uniquely tractable target.** The paper documents a turn-number effect that monotonically reduces engagement on what is the *exact opposite* of what clinical practice would prescribe. A probe-on-residual-stream design across the 7-turn trajectory could test whether a "disengage" or "withdraw" direction sharpens with each disclosure, and whether ablating or steering that direction restores invitation rates without degrading acknowledgment.

2. **The risk-acknowledgment-vs-invitation divergence is the load-bearing puzzle.** The same conversations show acknowledgment going *up* with turn number while invitation goes *down*. These are not redundant safety behaviours — the model is increasingly recognising the disclosed risk and decreasingly willing to engage with it. Whether this reflects an RLHF-style "high-stakes-context → refuse / hand off" reflex, a context-length attention artefact, or a learned "you've been talking about this for a while, time to wrap up" prior is undetermined.

3. **The 3× first-turn acknowledgment gap between NSSI (85%) and prior suicidal ideation (27%) likely reflects training-data surface features rather than clinical risk weighting.** NSSI is explicit ("I cut myself") while suicidal ideation may be more euphemistic or first-person-internal-state ("I've been thinking about ending it"). Whether the model is responding to lexical-pattern triggers or to semantic content is testable with paraphrase-controlled prompts.

4. **Whether the withdrawal pattern is OLMo-specific or characteristic of base→instruct-tuned models more broadly cannot be answered without a multi-model replication.** The paper deliberately restricts to one model. A natural follow-up is whether closed-weight frontier models exhibit the same monotonic turn-number effect, and whether the magnitude correlates with RLHF training intensity.

5. **The eval has no jailbreak / adversarial axis.** All disclosures are sincere, non-adversarial, paraphrased by clinicians. Whether the same withdrawal pattern persists under realistic user behaviours — language switching, contradiction, escalation, deflection — is open and clinically important.

## See also

- [[mental_health_crisis]] — multi-model behavioural eval on mental-health crisis prompts (GPT-4o-mini, GPT-5-nano, Llama-4-Scout, DeepSeek-v3.2, Grok-4-fast); single-turn / raw-input, complements this paper's multi-turn / clinician-paraphrased design
- [[high_stakes_probes]] — probe-based methodology for the adjacent "high-stakes interactions" target; the internals-follow-up this paper flags would naturally borrow that probe stack
- [[model_written_evals]] — taxonomy-driven multi-construct behavioural eval; same shape at much broader scope
- [[liars_bench]] — sibling structured-benchmark-for-hard-to-measure-behaviour; same tension between LLM-judge / clinician scoring and probe-based methods
