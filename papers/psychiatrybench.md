# PsychiatryBench: A Multi-Task Benchmark for LLMs in Psychiatry

**Authors:** Fouda, Hassan, Fouda (Compumacy for AI Solutions, Cairo) + Hanafy (Saint Elizabeths Hospital, DC)
**Year:** 2026 (npj Digital Medicine vol. 9, Article 320); arxiv preprint Sep 2025
**arXiv:** [2509.09711](https://arxiv.org/abs/2509.09711)
**DOI / Venue:** [npj Digital Medicine 9:320](https://www.nature.com/articles/s41746-026-02582-w)
**Fetched from:** `arxiv.org/html/2509.09711v2`
**Status:** read

---

## Summary (in our words)

PsychiatryBench is a textbook-sourced, expert-curated 5,188-item QA benchmark for psychiatric reasoning, structured across 11 task types: diagnosis (467), treatment (258), treatment follow-up (27), classification (418), management plan (337), clinical approach (56), mental QA (326), sequential QA (32), MCQs (1,353), extended matching items (277 full sets / 1,037 separated), and exams (600). Material comes from 13 authoritative sources — DSM-5-TR Clinical Cases, Stahl's Essential Psychopharmacology, Case Files Psychiatry, 100 Cases in Psychiatry, etc. — rather than social-media or synthetic data. The deliberate choice is to ground evaluation in the kind of cases trainees would see in residency exams.

The authors evaluate 14 frontier models (GPT-5 Medium Thinking, Sonnet 4.5 ±Thinking, Gemini 2.5 Pro/Flash ±Thinking, DeepSeek-R1, Llama 3.3 70B, etc.) and 6 medical-specialised models (MedGemma 27B, OpenBioLLM-70B, Palmyra-Med-70B, Llama-MedX, JSL-MedLlama, II-Medical-8B). Scoring is **LLM-as-judge** using Llama-3 70B as the evaluator on a 0-100 similarity rubric, chosen empirically over a strict point-based rubric. Frontier models cluster at the top: GPT-5 Medium Thinking 84.5%, Sonnet 4.5 Thinking 83.7%, Sonnet 4.5 83.5%, Gemini 2.5 Flash Thinking 82.4%, DeepSeek-R1 80.4%. MedGemma at 78.5% beats every other medical-specialised model but trails frontier generalists by 3-5 points. There's a clean release-date-vs-score trend: +8 points from Gemini 2.0 Flash (Q1 2025) to Sonnet 4.5 (Q3 2025).

What's interesting for our threat-model lens is what the benchmark explicitly does *not* cover. The authors deliberately exclude high-acuity psychiatry — imminent suicidality, acute mania requiring admission, delirium, emergency-psychiatry scenarios. They acknowledge in §6.1.4 that safety limitations are not systematically assessed: "models not evaluated on suicide risk recognition or crisis escalation protocols". The escalation-adjacent items embedded in clinical QA exist (management plans nominally include "risk assessment and follow-up strategy"; treatment follow-up tests longitudinal medication adjustment), but the rubric scores them on clinical-content similarity to textbook answers, not on whether the model would behave safely in a live crisis. Concretely: treatment-follow-up is the smallest split (27 items) and the one where top models underperform, but the failure mode being measured is "did the model match the textbook's longitudinal management" rather than "did the model recognise risk and escalate". That's the same shape of safety-blindness [[mental_health_crisis]] addresses directly with a separate crisis-handling taxonomy.

The headline gap the authors themselves flag is classification of specific disorders, where even the best models hit only 0.52 F1 / 45% subset accuracy on multi-label comorbidity — clinical realism (psychiatric patients usually have multiple co-occurring diagnoses) is exactly where these models fail hardest.

## Key experimental conditions

- 5,188 expert-annotated items across 11 task types, drawn from 13 psychiatric textbooks and casebooks
- 14 frontier general LLMs + 6 medical-specialised LLMs evaluated; Med-PaLM v2 excluded due to deployment restrictions
- Scope: adult outpatient psychiatry; excludes child/adolescent psychiatry, acute/emergency psychiatry, severe inpatient cases
- Zero-shot prompting, task-specific prompt variants refined across two guidance sessions
- Reasoning models (DeepSeek Chat, Gemini Thinking, Sonnet 4.5 Thinking) used custom parsers to extract answers from long justifications
- Three evaluation paradigms: accuracy (correct/total), EMI partial-credit scoring (PCS) for full sets vs. binary for separated subquestions, and multi-label classification (subset accuracy + F1-weighted)
- LLM-as-judge: Llama-3 70B selected for consistency across psychiatric outputs; 0-100 similarity score on clinical content (reasoning, correctness, completeness), stylistic differences disregarded
- Three generations per input not used — the protocol is single-pass per (model × item)

## Key quantitative results

- Top frontier models cluster 80-84.5%: GPT-5 Medium Thinking **84.5%**, Sonnet 4.5 Thinking 83.7%, Sonnet 4.5 83.5%, Gemini 2.5 Flash Thinking 82.4%, DeepSeek-R1 80.4%, Gemini 2.5 Pro 80.2%
- MedGemma 27B: **78.5% average** — beats every other medical-specialised model but trails frontier generalists by 3-5 pts; strongest on Mental QA (87.1%) and Management Plan (81.7%)
- Sequential QA is the strongest task family across models — Sonnet 4.5 Thinking 96.2%
- Clinical Approach: 90%+ for top models (Sonnet 4.5 Thinking 90.2%)
- **Classification of specific disorders is the persistent weak point**: even GPT-5 reaches only 0.52 F1 / ~45% subset accuracy on multi-label comorbidity
- EMI variability: 75.5%-89.1% across models (fine-grained discrimination across similar diagnoses)
- Exam simulation: 69.9% (Gemini 2.0 Flash, lowest) to mid-80s (top frontier models)
- Release-date-vs-score trend: Gemini 2.0 Flash (Q1 2025) 74.6% → Sonnet 4.5 series (Q3 2025) ~83.5-83.7% (+8 pts in 9 months)
- Domain-specialisation effect: medical models gain ~5-6 pts on Mental QA over equivalently-sized generalists but lose on complex reasoning tasks
- LLM-as-judge methodology choice: logic-driven few-shot rubric (Gemini 2.0 Pro-generated) preferred empirically over rigid point-based scoring

## Methods (what they did and didn't use)

- Behavioural eval only — LLM-as-judge for free-text outputs + standard accuracy/F1 for structured tasks
- **No internal-state methods anywhere in the paper**: no linear probes, no SAEs, no activation steering, no NLAs, no mechanistic interpretability
- Closed-weight models (GPT-5, Sonnet 4.5, Gemini 2.5) and open-weight models (DeepSeek-R1, Llama 3.3, Qwen) mixed — reproducibility against frozen checkpoints only for the open-weight subset
- Single judge model (Llama-3 70B); no cross-judge consistency check or judge-family rotation
- No human-clinician validation of model outputs at scale (acknowledged limitation)
- No safety-critical evaluation: no suicide-risk recognition, no crisis escalation, no uncertainty-acknowledgment or refusal scoring

## Authors' stated limitations / future work

- Data source bias: grounded exclusively in DSM-5-TR / Western diagnostic frameworks; WEIRD-population skew
- LLM-as-judge introduces potential model-family circularity and is not validated against clinician scoring
- Reliance on a single judge (Llama-3 70B); no ensemble or rotation
- Geriatric cases underrepresented despite inclusion claim
- Medical mimics (thyroid disease, CNS pathology) not systematically assessed
- High-acuity scenarios (suicidality, delirium, acute mania) deliberately excluded — no crisis escalation evaluation
- Conversational coherence, turn-by-turn dialogue management, multidisciplinary care coordination not assessed
- Future work named explicitly: integrate real-world clinical cases, ICD-11 and non-Western frameworks, human-clinician validation, **dedicated protocols for suicide risk assessment and crisis escalation**, expansion to child/adolescent and emergency psychiatry

## Open questions and follow-up directions

1. **Whether textbook-grounded performance predicts real-deployment behaviour on the same patients is open.** The benchmark scores match-to-textbook; the deployment risk is patients in conditions the textbooks didn't cover. A natural follow-up would pair PsychiatryBench scoring with held-out real-clinical-encounter data from the same task families to measure the textbook-to-clinic transfer drop.

2. **The classification-of-specific-disorders ceiling (~0.52 F1 even for GPT-5) is the only result here that doesn't look like it'll be solved by next year's frontier release.** Multi-label psychiatric comorbidity is closer to a genuine reasoning bottleneck than to a knowledge gap — distinguishing what fraction is calibration / what fraction is missing co-occurrence priors would require a probe-based decomposition the paper doesn't run.

3. **PsychiatryBench's deliberate exclusion of high-acuity cases leaves the safety-critical slice of the workload untested.** The paper's own future-work section flags this. The escalation-adjacent items embedded in management-plan and treatment-follow-up are scored on textbook-similarity, not on safe-behaviour-under-risk — meaning a model could score 85% on management while quietly mishandling the implicit risk-assessment subtask.

4. **The LLM-as-judge → frontier-LLM circularity is more acute than the paper acknowledges.** The judge (Llama-3 70B) is itself in the benchmarked population (Llama 3.3 70B is evaluated). A cross-judge ablation — re-scoring with Claude or Gemini as judge — would quantify the family-bias floor and is straightforward to run.

5. **Whether reasoning-mode lifts crisis-adjacent task performance specifically (treatment follow-up, management plan) or just sequential-QA / clinical-approach is undetermined.** The Sonnet-4.5 vs. Sonnet-4.5-Thinking delta is small in aggregate (83.5 → 83.7) but the per-task breakdown isn't reported in the visible table for the weakest splits.

## See also

- [[mental_health_crisis]] — direct sibling on mental-health LLM safety; explicitly evaluates crisis handling (self-harm, suicidal ideation) that PsychiatryBench deliberately excludes
- [[liars_bench]] — same "structured QA benchmark with LLM-as-judge" methodology, different domain
- [[abstention_bench]] / [[abstention_survey]] — adjacent on the uncertainty-acknowledgment gap PsychiatryBench flags as future work
- [[high_stakes_probes]] — orthogonal methodology (activation probes for high-stakes interactions) where PsychiatryBench's deliberate exclusion of high-acuity cases leaves a measurement gap
