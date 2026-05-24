# Towards Enforcing Company Policy Adherence in Agentic Workflows

**Authors:** Naama Zwerdling, David Boaz, Ella Rabinovich, Guy Uziel, David Amid, Ateret Anaby-Tavor (IBM Research)
**Year:** 2025
**arXiv:** [2507.16459](https://arxiv.org/abs/2507.16459)
**Fetched from:** `arxiv.org/html/2507.16459`
**Status:** read

---

## Summary (in our words)

The paper (often referred to as COMPASS in the IBM ecosystem; the public title is the longer "Towards Enforcing Company Policy Adherence in Agentic Workflows") proposes a deterministic, code-level guard layer for LLM agents operating under company policy documents. The framing is direct: prompting an agent with a policy doc and hoping it complies is unreliable, so the authors compile the policy into executable validators that gate every tool call. The compilation happens offline in two phases — a Tool-Policy Mapper that decomposes natural-language policies into atomic policy fragments and ties them to specific tools/parameters, then a ToolGuard generator that turns those fragments into Python validator code using a test-driven loop with syntactic and semantic feedback. At runtime the agent runs inside a ReAct loop and every tool invocation must pass its ToolGuard before execution; if it fails the agent receives an explanation and revises.

The headline result is on τ-bench Airlines (22 tasks with policy violations baked into the user goals): a best-effort prompted baseline lands at pass^1 = 0.450 / pass^10 = 0.227; reflection-style prompting strategies barely move pass^10 to 0.273; deploying ToolGuards lifts the system to pass^1 = 0.685 / pass^10 = 0.500. That's roughly a 20-percentage-point gain at pass^1 and more than doubling pass^10 (which is the harder, robustness-leaning metric — the action must comply on every attempt, not just succeed once).

The component-level numbers tell a complementary story. The Tool-Policy Mapper reaches F1 = 0.80 / FRI = 0.83 on reference detection and policy-grouping with GPT-4o; open-weight Llama-3.3-70B-Instruct trails at 0.74 / 0.81. ToolGuard generation passes 75-82% of unit tests depending on whether the mapper output is ground-truth or auto-generated. Robustness probing matters here: when the input policy doc is contaminated with out-of-domain or irrelevant in-domain policies, F1 drops 16-18 pp — interestingly, placing the relevant content at the end of a long document mitigates degradation, which is a "recency wins" finding worth flagging.

What makes this interesting from our angle is what it isn't. The paper is paper-centric on agent reliability/compliance, not on alignment in the threat-model sense — the agent is assumed cooperative and the policies are corporate (refunds, baggage limits) rather than safety constraints against a scheming model. But the architectural pattern — compile-natural-language-rules-into-deterministic-validators — is the same shape several AI-control-style proposals take, and it's worth noting that the authors openly concede the guard layer only catches pre-invocation violations: an agent that *fails to call a required tool* slips through entirely.

## Key experimental conditions

- **Domain:** τ-bench Airlines (Sierra). 14 tools; policy document is concise. 22 tasks specifically constructed to contain policy violations in the user goal (the agent must refuse / redirect).
- **Phase 1 (Tool-Policy Mapper) evaluation:** LangGraph multi-step pipeline. Inputs: policy doc + OpenAPI tool spec. Outputs: atomic policy fragments mapped to tool/parameter references, with compliance + violation examples generated.
- **Phase 2 (ToolGuard) evaluation:** TDD-style generation — skeleton code from OpenAPI spec, LLM fills validator bodies, iterates with `pyright` (syntactic) + test-pass (semantic) feedback until tests pass or iteration cap.
- **Models compared:** GPT-4o, GPT-4.1, Claude (variant unspecified in extract), Llama-3.3-70B-Instruct.
- **End-to-end runtime:** ReAct agent loop; ToolGuards execute synchronously before each tool call, returning `valid` or `invalid` with explanation.

## Key quantitative results

- **Tool-Policy Mapper (Table 2):** GPT-4o F1 = 0.80, FRI = 0.83 (best); Llama-3.3-70B-Instruct F1 = 0.74, FRI = 0.81 (best open). Precision across models 0.82-0.88; recall more variable at 0.55-0.83.
- **Robustness (Table 3):** Out-of-domain contamination → F1 −18.3 pp, FRI −10.8 pp; irrelevant in-domain contamination → F1 −16.1 pp, FRI −10.8 pp; placing relevant content at document end reduces degradation.
- **ToolGuard generation (Table 4):** GPT-4.1 with ground-truth mapper input TPR = 0.82; GPT-4.1 with auto-generated mapper input TPR = 0.75. Total test suite 61 tests (25 compliance + 36 violation).
- **End-to-end (Figure 2):** Best-effort baseline pass^1 = 0.450, pass^10 = 0.227. Reflection prompting variants pass^10 ≈ 0.273. ToolGuards pass^1 = 0.685, pass^10 = 0.500. Net gain ~20 pp pass^1; pass^10 more than doubles.

## Methods (what they did and didn't use)

- Behavioural evaluation only (task pass rate, F1 on extraction, test-pass on generated code). No internal-state methods — no probes, no SAEs, no activation steering, no NLAs. This is consistent with the paper's framing as agent reliability tooling, not alignment internals research.
- Closed- and open-weight models both included; the open-weight results are weaker but in the same regime, so the pipeline is reproducible in principle (and code is released at `github.com/IBM/tool_guard`).
- The TDD loop is the methodologically interesting bit — using `pyright` as a fast syntactic gate and unit tests as a semantic gate gives the LLM a tight feedback channel that doesn't depend on a separate critic LLM.
- The benchmark is narrow: one domain, one policy document, 14 tools, 22 tasks. The authors flag this themselves.

## Authors' stated limitations / future work

- Operates only at the pre-tool-invocation level. Cases where a policy *requires* the agent to invoke a tool — and the agent silently omits the call — are not caught. This is an explicit acknowledged gap.
- Evaluated on a single benchmark (τ-bench Airlines) with limited tools and a concise policy document; scalability to larger policy corpora and toolsets unvalidated.
- Does not address policies that govern sequences of actions across multiple steps (temporal / stateful constraints).
- Future work listed: integration with LangSmith / Langflow / Llama Stack; life-cycle management for human-in-the-loop policy edits; extension to post-invocation validation; evaluation on larger and more diverse policy domains.

## Open questions and follow-up directions

1. **The omission failure mode.** A guard layer that only fires on attempted tool calls is blind to the most adversarial failure mode — quietly *not* calling a required tool. Whether this is bridgeable with the same compile-policy-to-code architecture (e.g. by generating "expected call" assertions over conversation traces) or whether it requires a fundamentally different supervisor design is open and arguably the most consequential question the paper raises.

2. **Stateful / multi-step policies.** ToolGuards as described are stateless per-invocation. Real corporate policies often constrain *sequences* — "refunds require manager approval if cumulative this month > X". The compilation target (Python with no shared state across calls) doesn't obviously extend; it's worth knowing whether the TDD loop degrades gracefully when the validator needs persistent context, or whether the whole architecture has to change.

3. **The recency-of-relevant-content effect.** Robustness drops materially under irrelevant-content contamination but is partially rescued by placing the relevant content at the end of the doc. That's a fairly specific empirical regularity about how the mapper attends to long policy documents; whether it's a property of GPT-4o's long-context behaviour or a more general pattern the field should expect is unclear from one paper.

4. **Adversarial policy authoring.** The whole pipeline assumes the policy document is written cooperatively. What happens if the policy is ambiguous, internally contradictory, or written to be hard to compile (whether by accident or intent)? The TDD loop will either fail gracefully or paper over the contradiction by picking one branch — neither is empirically characterised here.

## See also

- [[ai_control]] — same architectural family (external, deterministic gating of an untrusted policy generator); ToolGuards are functionally a per-tool "trusted editor" specialised to one policy domain.
- [[ih_challenge]] — adjacent goal (making the agent follow a rule hierarchy) reached via RL fine-tuning rather than an external code-level guard; a useful contrast on training-vs-scaffolding for rule adherence.
- [[teaching_claude_why]] — opposite end of the design space; rules internalised via explanation-training, no runtime gate.
