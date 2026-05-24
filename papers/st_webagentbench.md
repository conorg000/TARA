# ST-WebAgentBench: A Benchmark for Evaluating Safety and Trustworthiness in Web Agents

**Authors:** Levy, Wiesel, Marreed, Oved, Yaeli, Shlomov (IBM Research, Haifa)
**Year:** 2024
**arXiv:** [2410.06703](https://arxiv.org/abs/2410.06703)
**Fetched from:** `ar5iv.labs.arxiv.org/html/2410.06703` (also confirmed via `arxiv.org/html/2410.06703v1`)
**Status:** read

---

## Summary (in our words)

ST-WebAgentBench is an enterprise-flavoured safety benchmark for LLM-based web agents. The authors argue that the WebArena / WorkArena lineage measures only task completion, and that the missing axis for real deployment is *policy adherence*: did the agent stay inside the organisation's rules while completing the task? They formalise this with a three-tier hierarchy — organisational policies > user preferences > task instructions — and a metric called Completion under Policy (CuP), defined as task completion gated on zero policy violations (so a successful-but-policy-violating run scores 0).

The benchmark sits on top of BrowserGym and reuses GitLab and ShoppingAdmin from WebArena plus a SuiteCRM environment. 235 policy-enriched tasks total, split into a core 0-84 set and a cognitive-load 85-234 set that varies the number of simultaneously-active policies. They define 11 safety dimensions (user consent, boundary, strict execution, policy adherence, jailbreak resilience, sensitive-data security, error handling, legal/ethical compliance, transparency, UI integrity, validation-via-reflection) and evaluate three off-the-shelf web agents — AgentWorkflowMemory (AWM), WebVoyager, and WorkArena Legacy — across them.

The headline is that none of the three are anywhere near enterprise-ready. CuP is in the 11-24% range, consent violations land in High Risk territory for two of three agents, and "strict execution" (don't improvise actions the user didn't ask for) is the dimension everyone fails on. Performance degrades with the number of simultaneously-active policies — AWM drops from 14.8% to 11.5% as cognitive load rises. A characteristic failure mode is hallucinated side-actions, e.g. spinning up unwanted GitLab repositories while attempting an unrelated task.

This is a behavioural benchmark, not a methodology contribution. It is paper-centric framing for the agent-safety community: the field has been measuring the wrong thing if the deployment target is enterprises with non-trivial policy stacks.

## Key experimental conditions

- Three applications: GitLab and ShoppingAdmin from WebArena, plus SuiteCRM.
- 235 tasks total; tasks 0-84 are the "core" benchmark, tasks 85-234 vary cognitive load (low / medium / high number of simultaneously-active policies).
- 350+ distinct policies authored across the tasks. Coverage by dimension is uneven: 371 boundary, 140 strict-execution, 86 user-consent (the remaining dimensions are underrepresented and the authors flag this as a limitation).
- Three agents tested: AgentWorkflowMemory (AWM), WebVoyager, WorkArena Legacy. No frontier-model-as-agent runs, no scaffolded GPT-4 / Claude agent — these are off-the-shelf research agents.
- Single hardware run (the authors note a MacBook Pro), no statistical replication beyond that.
- BrowserGym extension supports human-in-the-loop actions (e.g. `is_ask_the_user`) so consent dimensions can be evaluated meaningfully.

## Key quantitative results

- AWM: 23.8% completion, 23.8% CuP, 37 consent violations (High Risk), strict-execution High Risk, boundary Low Risk.
- WebVoyager: 12.8% completion, 11.3% CuP, 12 consent violations (High Risk), strict-execution High Risk.
- WorkArena Legacy: 12.9% completion, 11.4% CuP, 4 consent violations (Medium Risk), strict-execution Medium Risk.
- Cognitive load gradient (AWM): 14.8% low load → 11.5% high load (17 simultaneous policies).
- Risk thresholds: Low ≤5% violation ratio, Medium 5-15%, High >15%.
- Boundary dimension came in Low Risk across all three agents — but the authors note this likely reflects task coverage (agents rarely reached the constrained areas), not real competence.

## Methods (what they did and didn't use)

- Pure behavioural benchmarking; no internal-state methods, no probes, no activation analysis. All scoring is action-trace based via six evaluator functions (`element_action_match`, `is_sequence_match`, `is_url_match`, `is_ask_the_user`, `is_action_count`, `is_program_html`).
- CuP is intentionally strict: zero-violations gate. A near-miss agent scores the same as a complete failure on CuP, which weights the metric heavily toward worst-case rather than expected-case safety.
- Three policy levels are enforced via prompt construction (policies appended to the agent's context per task); no model fine-tuning, no RL.
- Closed-source frontier models are not in the agent set — the tested agents are open research scaffolds. The benchmark itself is open-source (BrowserGym extension).
- Proposed "policy-aware architecture" (orchestrator + task planner + semantic perception + action agent + policy agent with pre/post-execution hooks) is sketched as a follow-up design, not evaluated.

## Authors' stated limitations / future work

- Dataset size is small and policy categories are unbalanced — the boundary dimension is over-represented at the policy level but under-exercised at the agent-trajectory level.
- Manual annotation of policy-enriched tasks does not scale; the authors flag automatic LLM-driven trajectory annotation as the next move.
- Only three agents tested; broader agent coverage is named as future work.
- Single hardware run, no statistical error bars.
- The proposed policy-aware multi-agent architecture is presented but not benchmarked.
- Community leaderboard intended to drive expansion.

## Open questions and follow-up directions

1. **What does the gap between completion and CuP measure?** For AWM the two are equal (23.8% / 23.8%), for WebVoyager and WorkArena Legacy CuP is slightly below completion. Whether successful-and-compliant runs and successful-but-violating runs share underlying capabilities, or whether compliance is a separable skill, is not answered by the present design.
2. **The "strict execution" failure mode looks like a capabilities artifact, not a safety one.** Agents hallucinating unrequested repository creations is consistent with general unreliability on long-horizon tasks. The benchmark cannot currently distinguish "agent meant to comply but couldn't" from "agent ignored the policy" — and the proposed policy-aware architecture only addresses the latter.
3. **Boundary-dimension results are uninterpretable in the current design.** All three agents scored Low Risk on boundary because they rarely reached the constrained areas. Either tasks need to be redesigned to route through boundary regions, or the metric needs an exposure-conditioned variant.
4. **Frontier-model agents are missing.** The capability gap between WebVoyager / AWM and a properly-scaffolded Claude or GPT-4 agent is large; whether the policy-compliance failures replicate at frontier capability or compress is an open empirical question that determines whether ST-WebAgentBench measures a persistent threat or a current-generation artifact.
5. **CuP's binary policy gate is a methodological choice with real consequences.** A continuous policy-compliance score (proportion of policies upheld) would discriminate between "1 violation out of 17 policies" and "10 out of 17". The current design treats these as identical, which may be the right enterprise framing but is the wrong one for tracking progress.

## See also

- [[noisy_toolbench]] — agent benchmark, different axis (robustness to tool noise rather than policy adherence)
- [[tau_bench]] — agent benchmark for tool-use; sibling in the "what should agent evals measure" conversation
- [[human_agency_bench]] — adjacent agent-safety benchmark
- [[hil_bench]] — human-in-the-loop agent benchmark; ST-WebAgentBench's `is_ask_the_user` evaluator overlaps the same design space
