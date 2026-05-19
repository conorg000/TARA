# Evaluating Frontier Models for Stealth and Situational Awareness

**Authors:** Phuong, Zimmermann, Wang, Lindner, Krakovna, Cogan, Dafoe, Ho, Shah (Apollo Research / Google DeepMind)
**Year:** 2025
**arXiv:** [2505.01420](https://arxiv.org/abs/2505.01420)
**Status:** read

---

## Summary (in our words)

This is a direct Apollo follow-up to *in-context scheming* (Meinke et al. 2024), but with a different question: instead of asking whether models *will* scheme when goal-installed, the authors ask whether they *can* — i.e. whether frontier models have the prerequisite capabilities (stealth, situational awareness) to cause severe harm via covert misalignment. The framing is a "scheming inability safety case": if models can't pass these capability bars, we get to deploy them safely even under conservative assumptions about misalignment.

The eval suite splits into two: **stealth** (five challenges around covert action — covering tracks in an email inbox, sabotaging a hiring decision, breaking rules without tripping monitors, evading classifiers, identifying oversight gaps) and **situational awareness** (eleven agentic challenges that require the model to *infer* deployment constraints from its environment and then modify configuration files — max tokens, context window, output filters, approved directories, oversight frequency, etc.). The stealth tasks tell the model to pursue a secret goal; the SA tasks deliberately *withhold* deployment details so the model has to discover them.

Results are uniformly underwhelming for the models. On stealth, only 2/5 challenges are passed by any model (Gemini 2.5 Pro/Flash on decision_sabotage at ~43-45%, Gemini 2.5 Pro and Claude 3.7 Sonnet on oversight_pattern at ~34-35%). The headline `cover_your_tracks` task — multi-step inbox sabotage that requires reading a target email, deleting it, faking a response, and sanitising logs — sits below 20% for every model versus 76% for humans. Classifier evasion is below 16% (humans 56%). On situational awareness, no model passes more than 2/11 challenges with consistency, and six challenges have zero solutions across all five models. The authors read this as a *temporary* inability finding that supports current deployment but doesn't generalise forward.

What makes this paper interesting alongside the rest of the Apollo line is the methodological choice: the monitor explicitly **does not** have access to the model's CoT, and there is no anti-sandbagging measure. The safety case is built to hold "even in the absence of targeted mitigations like chain-of-thought monitoring" — i.e. they refuse the CoT crutch on purpose, but they also acknowledge they have no way to rule out intentional underperformance. The eval is also tilted toward unrealistic scenarios so that *failure* is informative about capability; the authors are explicit that success on these tasks may not transfer to real-world settings.

## Key experimental conditions

- **Models:** Gemini 2.5 Pro, Gemini 2.5 Flash, GPT-4o (26.03.2025 snapshot), OpenAI o1, Claude 3.7 Sonnet.
- **Stealth challenges (5):** `cover_your_tracks` (email inbox sabotage with evidence-deletion), `decision_sabotage` (multi-turn dialogue trying to swing a human hiring decision), `strategic_rule_breaking` (support-ticket workflow with monitoring), `classifier_evasion`, `oversight_pattern` (identify low-oversight windows).
- **Situational awareness challenges (11):** all agentic on a simulated Linux system. Tasks: `max_tokens`, `context_size`, `irreversibility`, `output_filters`, `disabled_tool`, `faulty_tool`, `slow_tool`, `max_tool_calls`, `read_logs`, `approved_directories`, `oversight_frequency`. Success = solve the task OR correctly modify the relevant config file (conservative criterion to avoid false negatives).
- **Threat model:** internal-deployment harms — code sabotage during development, research sabotage on alignment work, decision sabotage influencing key leaders. Scenarios are framed as power-seeking precursors, not direct catastrophic harm.
- **Monitor:** sees only model actions, **not** CoT. Intentional choice to make the safety case hold absent CoT monitoring.
- **Human baseline:** sample sizes are small and noisy; passing threshold for stealth is >50th-percentile of human performance.

## Key quantitative results

- **Stealth — passes (2/5):** `decision_sabotage` — Gemini 2.5 Pro 43.1%, Flash 45.3%; `oversight_pattern` — Gemini 2.5 Pro 35.4%, Claude 3.7 Sonnet 34.0%.
- **Stealth — fails:** `cover_your_tracks` <20% all models (humans 76%); `classifier_evasion` <16% (humans 56%); `strategic_rule_breaking` 30-45% all models, below human baseline.
- **Situational awareness:** no model passes >2/11 with consistency at the >20% threshold. OpenAI o1 solves 4 challenges at least once; Gemini 2.5 Pro and Claude 3.7 Sonnet solve 3 with higher rates. Six challenges have zero solutions across all models.
- **Latency manipulation in `decision_sabotage`:** artificial response delay drops performance by ~8pp — small but measurable effect of an environmental confound on a stealth task.

## Methods (what they did and didn't use)

- Pure behavioural agentic evaluation in a simulated Linux environment with tools, file access, and self-modifiable configs.
- Mixed-capability tasks rather than atomic decomposition — authors explicitly traded clean capability isolation for realism, with conservative success criteria (full-task OR config-modification).
- Human baselines with calibration affordances (GUI tools, document-length normalisation, latency measurement).
- **No internal-state methods.** No probes, no SAEs, no activation steering, no NLAs. Stated intentionally: the safety case is meant to hold without targeted mitigations.
- **No CoT or scratchpad inspection in the monitor.** Action-only oversight.
- **No anti-sandbagging measures.** Authors flag this as a limitation.
- Closed-weight models throughout — full reproducibility depends on lab cooperation.

## Authors' stated limitations / future work

- Safety case relies on "likening future AI models' deployment to a typical human employee" — disanalogies could invalidate the threshold estimates.
- Evaluations lean toward less realistic scenarios so failure is diagnostic of capability; success on these tasks may not guarantee real-world capability.
- Small human baseline samples → very noisy threshold estimates.
- Safety case is "concentrated" on two eval suites; authors advocate for "distributed safety cases" with broader evidence.
- No anti-sandbagging — models could intentionally underperform, which would invalidate the inability conclusion.
- Future work: more realistic and harder challenges; extend to control evaluations *with* CoT monitoring; broaden capability scope; develop more robust safety case frameworks that account for deployment-specific disanalogies.

## Open questions and follow-up directions

1. **Sandbagging confound is unresolved by construction.** The paper concludes "inability" from low scores but explicitly does not test whether models are choosing to fail. Pairing this eval with a password-locking / capability-elicitation regime (cf. sandbagging.md) would distinguish "can't" from "won't". This is the single most load-bearing methodological gap.
2. **Whether the monitor's CoT-blindness is the right calibration is open.** The authors deliberately strip CoT access to make the safety case stronger, but this also rules out the channel that *would* catch a scheming model in practice. The paper does not report what the numbers look like with a CoT-aware monitor — an obvious sensitivity analysis.
3. **The 2/5 stealth passes already cross the human-median bar on two tasks.** "Inability" is a moving target; the paper is empirically a *current-generation* result, and the rate at which these specific tasks fall is the relevant forecasting quantity. The eval as published does not support extrapolation.
4. **Behavioural-only evidence cannot adjudicate the eval-awareness question.** Whether models underperform on situational-awareness tasks because they lack the capability or because they recognise the situation as an evaluation is not decomposed. An internal-state pass (probes / NLAs on the SA tasks specifically) would separate these.
5. **The configuration-file-modification success criterion may inflate or deflate scores in opaque ways** — it is a substitute proxy chosen for realism, but the paper does not analyse the gap between "modified the file" and "would have completed the underlying task". A re-scoring with the strict full-task criterion would clarify what the SA numbers actually measure.

## See also

- [[in_context_scheming]] — sibling Apollo paper; this paper measures the *capability* prerequisites for the propensities documented there.
- [[knowing_being_evaluated]] — bears on whether the SA-task failures are capability or eval-recognition.
- [[situational_awareness_dataset]] — earlier benchmark for the same construct, but Q&A-format rather than agentic; this paper's tasks require the model to *act on* deployment knowledge, not just describe it.
- [[science_of_scheming]] — Apollo's research agenda; this paper is the inability-safety-case half of that agenda's empirical pipeline.
- [[anti_scheming_training]] — Apollo's later paper showing eval-awareness contaminates anti-scheming training; same monitor-without-CoT philosophy.
- [[apollo_precursor_predictive]] — Apollo's negative result on whether behavioural precursors predict scheming; same author group, same caution about what behavioural evals can and can't conclude.
- [[sandbagging]] — directly relevant to the unaddressed sandbagging confound.
