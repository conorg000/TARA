# Revised Project

**Motivation.** Agents are getting deployed in high-stakes roles (financial advisory, customer service, internal corporate workflows, mental-health support) with explicit instructions about when to hand off to a human. We don't have good measurements of whether they reliably do this. If they don't, deployment fails in ways that compound and produce real harm. This is an applied AI safety question with a clear threat model and unmeasured baseline.

## Questions

1. How reliably does an agent perform the instructed handoff action when the trigger conditions are met?
2. How often does it spuriously hand off when conditions are not met?
3. When it fails, did it fail to recognise the trigger or recognise and continue anyway?
4. How does the reliability degrade under realistic deployment pressures — multi-turn buildup, user pushback, indirect cues?

## What we'll test

- One model: Qwen-2.5-32B (or whatever we can self-host).
- **One domain: junior research analyst at a financial services firm, with senior-analyst / compliance escalation rules.** We deliberately avoid mental-health / student-support for the primary measurement to reduce refusal-training contamination of the headline — heavily safety-trained domains make it hard to separate "the model used the scope rule" from "the model's RLHF said be careful." Analyst-context triggers (regulatory, legal, material risk, fiduciary) have weaker refusal priors, so observed escalation is more cleanly attributable to the operator rule. Mental-health, student-support, and customer-service are planned cross-domain follow-ups.
- 80-100 paired scenarios: should-escalate vs should-NOT-escalate.
- Multi-turn scripted conversations.
- Three stress conditions added on top: user pressure ("we're under deadline, just help me draft it"), implicit triggers (the request looks routine but has regulatory/fiduciary implications the user doesn't flag), and removal of the operator rule (treated as a primary result — see below).

## How

- Hand-curate scenarios. Construct from scratch based on realistic financial-analyst use-cases; no off-the-shelf clinical-style seed content available for this domain (deliberate trade — see domain choice above). Lean on τ-bench's policy-document structure as inspiration for what scope rules look like in this setting.
- Lock the action-judge rubric (narrow yes/no per scenario) before running anything.
- Run k=5 trials per scenario, T > 0.
- Headline: pass^k for missed-escalation (URUP) and spurious-escalation (ARSP).
- Failure diagnosis: fresh-context recognition probe asked of the same model, used as analysis of failures, not as the headline. Acknowledge its limitations honestly. Always report the unconditional recognition rate (across all scenarios) alongside the conditional-on-failure rate. *Without the baseline, the conditional number is uninterpretable — "60% of failures had recognition" means different things if the unconditional rate is 95% vs 60%.*

## What counts as a result

- **Positive:** meaningful pass^k drop from baseline to stress conditions, with a decomposable failure pattern.
- **Null:** model is reliably above 95% pass^k under all conditions. Honest finding; worth reporting; suggests the open question is which deployment conditions break this, not whether it breaks at all.
- **Confound result:** paired should-NOT set reveals over-escalation driven by something other than the scope rule (instruction-following caution, eval-awareness, generic risk-aversion). Useful diagnostic for the field about what "scope-respecting" benchmarks really measure.
- **Ablation result (primary, not a sanity check):** if escalation rate barely moves when the operator rule is removed from the system prompt, the rule isn't doing real work — model behaviour is dominated by something else (default caution, instruction-following inertia). If escalation rate drops meaningfully without the rule, the rule is being used and the headline number reflects genuine scope-tracking. *Both outcomes are first-order findings, not background checks — the rule-removal comparison is the cleanest test we have of whether the model is using the scope instruction at all, and gets reported alongside the headline number, not buried in supplementary material.*

## Out of scope, deliberately

- Mechanistic probe arm. Optional follow-up, not central.
- Multi-model comparison. One model done carefully > three done shallowly.
- Tools. Realistic but introduces a separate confound (tool-description priming).
- Cross-domain generalisation. One domain claim only for the primary measurement; cross-domain spot-checks (mental-health / student-support / customer service) are explicit follow-up phases.

## Milestones

Three milestones. M1 is detailed because most of the load-bearing decisions live there; M2 and M3 stay flexible because their exact shape depends on what M1 reveals. General rule across all three: if a milestone is dragging because a specific task isn't clearing its done-criteria, descope (drop a stress condition, narrow the scenario count, simplify the rubric) rather than grinding indefinitely.

### M1: Setup

The phase where we lock everything that has to be locked before scaling up. If any of these don't clear their done-criteria, we revise before moving on.

1. **Capability baseline.** Build ~50-item classification dataset of trigger conditions (e.g. "Read this user request. Does it involve regulatory compliance, legal, material-risk, or fiduciary considerations? Yes/No"); run on Qwen-32B. Done when: ≥90% accuracy. (If below: pivot — try a different model size or simpler triggers.)
2. **Lock persona/role system prompt.** Write one system prompt for the analyst-agent role. Pilot 3 variants on 5 scenarios; pick the cleanest; freeze it in version control. Document the spread between variants for methods.
3. **Write the action-judge rubric.** One document containing: positive patterns with examples, edge cases that don't count, multi-turn rules, graded examples per direction (including adversarial / hard cases). Done when: both authors (or author + held-out LLM grader) independently apply it to 20 examples with ≥90% agreement.
4. **Pilot the paired scenario design.** Write 5 positive + 5 paired negative scenarios. Blind-prediction check (colleague or cross-family LLMs predict which is which); pass band 60-90% accuracy. Label agreement check on 20 examples; target Fleiss κ ≥ 0.9.
5. **Stand up the run pipeline.** Qwen via OpenRouter, prompt formatting, response capture, judge invocation. Run a 5-scenario end-to-end smoke test on Qwen-7B first (cheap pipeline debugging), then confirm on Qwen-32B.
6. **Initial judge validation.** Hand-grade 50 model responses against the rubric; check primary judge agreement vs human grade. Target ≥85%. Cross-family judge check on 20-30 of those.
7. **Reproducibility setup.** Pin model snapshot (specific OpenRouter route, dated version), set temperature explicitly (T=0.7), commit prompts and rubrics to git, set up output logging (save raw responses, not just judge labels).

**Done when:** all 7 cleared.

### M2: Main experiment (~$200-500 compute)

Run the design locked in M1: stress conditions (user pressure + implicit triggers + operator-rule ablation), k=5 per scenario, T=0.7, recognition diagnostic on all responses.

**Done when:** all conditions run end-to-end, raw outputs saved, initial results tables compiled (pass^k, URUP, ARSP, recognition rates conditional + unconditional, ablation vs baseline). Sample-size math reconciled with actual N so we know which effects we can claim.

### M3: Analysis + writeup

Analyse the data and write it up. Methods, limits, and "what we won't claim" sections get drafted regardless of outcome. Headline framing branches based on what M2 showed — one of the four result types listed earlier. Artefacts (rubric, dataset, judge prompts, scripts) packaged for release.

**Done when:** writeup drafted, artefacts packaged.

### M4: Iterate

Re-run M1-M3 with elicitation / setup choices that were held constant the first time. By this point we'll have intuitions from the first cycle about which variations are likely to matter; the list below is the candidate space to draw from.

Things worth considering varying:
- Action specification: vague directive vs explicit behavioural target (e.g. structured response prefix)
- Tool affordance: text-only vs structured token vs actual function call
- Trigger explicitness: fuzzy criteria vs crisp enumerated criteria
- Persona detail / role-clarity (terse vs verbose, generic vs branded)
- Directive forcefulness (neutral vs firm vs soft)
- Single-turn vs multi-turn scenarios
- Cross-domain (analyst vs mental-health vs student-support)
- Model size and family
