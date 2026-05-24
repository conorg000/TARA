# τ-Bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains

**Authors:** Shunyu Yao, Noah Shinn, Pedram Razavi, Karthik Narasimhan (Sierra)
**Year:** 2024
**arXiv:** [2406.12045](https://arxiv.org/abs/2406.12045)
**Fetched from:** `arxiv.org/pdf/2406.12045` (PDF, extracted via `pdftotext`; arxiv HTML and ar5iv both 404/corrupted)
**Status:** read

---

## Summary (in our words)

τ-bench is a customer-service-flavoured agentic benchmark in which a function-calling LM agent has to converse with an LM-simulated user (gpt-4-0613), look things up and write to backing databases via Python tool APIs, and obey a domain-specific policy document supplied as system prompt. The pitch is that prior agent benchmarks either skip human interaction entirely or smuggle all task information into a single initial instruction; τ-bench instead forces the agent to gather information through multi-turn dialogue while sticking to ad-hoc rules (return windows, baggage allowance by membership tier, single-shot exchange tools, etc.) that aren't deducible from common sense alone.

Two domains ship at launch — τ-retail (115 tasks, 7 write APIs / 8 read, 500 users / 50 products / 1k orders) and τ-airline (50 tasks, 6 write / 7 read, 300 flights between 20 US cities, 2k reservations). Evaluation is rule-based: each task instance is hand-annotated so there is exactly one valid final database state; reward is the conjunction of database-state match and substring-presence checks on agent-to-user messages. The task curation loop is iterative — write an instruction, run gpt-4-turbo function calling against it, edit the instruction until the outcome is unique across trials. They explicitly trade quantity for quality.

The headline empirical claims: even gpt-4o function calling only solves ~61% of τ-retail and ~35% of τ-airline (pass^1), and pass^k drops fast — pass^8 on τ-retail for gpt-4o is under 25%. They introduce pass^k as the customer-service-appropriate dual of pass@k: the probability that *all* k i.i.d. trials succeed (vs. pass@k which is the chance *at least one* succeeds). Failure analysis on 36 failed gpt-4o τ-retail trajectories splits ~55% as wrong-argument / wrong-info (database reasoning), 25% wrong-decision (rule following), and ~19% partial-resolution of compound requests. A policy-ablation experiment shows that removing the domain-policy system prompt costs gpt-4o 22.4 points in τ-airline but only 4.4 in τ-retail — suggesting agents do read the rules when the rules are non-obvious, but lean on common sense when they can.

What makes the paper load-bearing for the agentic-eval literature is less the absolute numbers (which are now several model generations stale) and more the methodological pattern: LM-simulated users + rule-based ground-truth database state + a consistency metric that punishes flaky agents. The follow-ups τ²-bench and τ³-bench (Sierra Research) extend this template to additional domains and harder reliability targets, but the framework here is what they build on.

## Key experimental conditions

- Two domains: τ-retail (115 tasks) and τ-airline (50 tasks). Airline policy is the harder one — ad-hoc rules over membership tier × cabin class.
- Agent receives domain policy as system prompt + API function definitions. User simulator (gpt-4-0613) holds the user instruction and the conversation history; it cannot see agent↔tool traffic. Episode ends when user emits `###STOP###` or 30 actions are reached.
- 12 models tested via API: gpt-4o, gpt-4-turbo, gpt-4-32k, gpt-3.5-turbo; claude-3-opus/sonnet/haiku; gemini-1.5-pro/flash; mistral-large, open-mixtral-8x22b; meta-llama-3-70B. Only mistral-8x22b and Llama-3-70B are open-weight.
- Three agent scaffolds: native function calling (FC, primary), text-format ReAct, Act-only (no reasoning). Llama-3 runs via text-ReAct because it lacks native FC.
- Default: ≥3 trials per task, agent temperature 0.0, user temperature 1.0. Stochasticity comes from the user simulator, not the agent.
- Reward is conjunction: `raction × routput` where raction = exact match of final database state to the annotated unique-outcome state, routput = required substrings present in agent-to-user messages.

## Key quantitative results

- **gpt-4o function calling, pass^1**: τ-retail 61.2%, τ-airline 35.2%, weighted avg 48.2% — best overall.
- Spread across SoTA: gpt-4-turbo 57.7/32.4; claude-3-opus 44.2/34.7; mistral-large 30.7/22.4; gpt-3.5-turbo 20.0/10.8; meta-llama-3-70B 14.8/14.4.
- **Pass^k collapse**: gpt-4o on τ-retail drops from pass^1 ~61% to **pass^8 <25%**. Pass@k (probability ≥1 of k succeeds) climbs as expected; the gap between pass@k and pass^k is the reliability gap.
- **Policy ablation (table 3, pass^1)**: τ-retail gpt-4o 61.2 → 56.8 (−4.4), gpt-3.5 20.0 → 14.5 (−5.5). τ-airline gpt-4o 33.2 → 10.8 (**−22.4**), gpt-3.5 10.8 → 9.6 (−1.2). Rules matter only when they're non-obvious *and* the model can use them.
- **Failure breakdown (36 gpt-4o τ-retail failures)**: wrong info 33.3%, wrong decision 25.0%, partial resolution 19.4%, wrong argument 22.2%.
- **Hallucination rate**: gpt-4o FC makes 0.46 tool calls per task with nonexistent IDs; gpt-3.5-turbo FC makes 2.08; gpt-3.5-turbo Act makes 6.34.
- **Cost**: gpt-4o FC + gpt-4 user sim ≈ $0.38 (agent) + $0.23 (user) per τ-retail task; 95.9% of agent cost is input tokens (long system prompt of policy + function defs).
- **Method comparison**: native FC > ReAct > Act on the SoTA models; "think" function added to FC did not help.

## Methods (what they did and didn't use)

- Pure behavioural evaluation. No internal-state methods — no probes, no SAEs, no activation steering, no NLAs. Everything is conversation trajectories + database diffs + substring checks.
- Construction methodology is the contribution as much as the dataset: manual schema/API/policy design → LM-assisted data entry generation → manual scenario writing with iterative `gpt-4-turbo-in-the-loop` user-instruction tuning until each task has a unique outcome.
- Closed-weight models dominate the leaderboard, which limits reproducibility for downstream researchers; only mixtral-8x22b and Llama-3-70B are open-weight in their model set.
- Reward is necessary-but-not-sufficient by design: the agent can satisfy `raction × routput = 1` while still violating procedural rules (e.g. issuing a return without explicit user confirmation). Acknowledged in the paper.

## Authors' stated limitations / future work

- User simulator weaknesses: typos/ambiguities in user instructions; users don't know domain policies (which is also realistic); user-LM has limited reasoning/calculation/long-context/instruction-following capacity. Sometimes the user authorises wrong-looking agent suggestions without checking.
- Implicit annotation bias from using gpt-4-turbo FC during user-prompt tuning — task formulations may unintentionally favour models in that family.
- Manual annotation is slow and requires both domain and agent-capability expertise; suggests future LM-assisted curation.
- More evaluation channels possible (e.g. LM-judge checks on procedural-rule following beyond substring match).
- Domain policies are simplified relative to real-world airlines/retailers; harder domains (medical, tax, legal) are explicitly flagged as future targets — and the τ²/τ³ follow-ups extend in this direction.
- Self-reflection and planning-style scaffolds were excluded as unrealistic in a real-time user-facing setting; revisiting this constraint is open.

## Open questions and follow-up directions

1. **Pass^k vs. pass@k as orthogonal capability axes.** The paper demonstrates that a 60% pass^1 agent can have <25% pass^8 — a flakiness gap that doesn't show up in standard one-shot benchmarks. Whether this gap correlates with internal-state markers (eval-awareness probes, situational-awareness scores) at all is open. If reliability and capability are decoupled, then "this model is at X% on benchmark Y" headlines understate the deployment gap.
2. **User-simulator confounds.** Every result is filtered through gpt-4-0613 as the user. Swapping the user model — for a different family, a different prompt-tuning loop, or a smaller cheaper simulator — should not change the *relative* model ordering if τ-bench is measuring agent capability rather than agent-user-LM compatibility. The paper does not run this ablation. The τ²/τ³ follow-ups may.
3. **The 22.4-point τ-airline policy ablation as a rule-grounding signal.** That gpt-4o loses 22.4 points without the policy but gpt-3.5 loses only 1.2 means the policy is being *used* by the capable model. This is a cleaner "rule-following" measurement than most safety benchmarks offer, and could be inverted: train an agent to selectively *ignore* a policy clause and measure whether the degradation is localised. Useful for studying selective non-compliance.
4. **Substring-check `routput` is a weak channel.** A model can communicate a number to the user (passing the check) while reasoning incorrectly about it, or omit confirmation steps that the policy requires. Trajectory-level rule-following metrics (LM judge, or activation probes for "is the agent intending to honour the rule") would tighten the eval but introduce their own confounds.
5. **Closed-weight saturation risk.** As of writing the headline numbers will have been pushed substantially by post-gpt-4o models; the benchmark's longevity depends on whether the curation pattern (forcing single-outcome database states under domain policy) keeps producing tasks that resist scale. τ² and τ³ effectively answer this; whether the τ-bench framework keeps producing useful difficulty in additional domains without bespoke annotation effort is an open scaling question.

## See also

- [[ai_control]] — also evaluates agents on extended tasks (APPS coding) with a structured success criterion, but the threat model is intentional subversion under a control protocol rather than capability/reliability under benign user interaction. Sibling methodology for behavioural agent evaluation.
- [[apollo_stealth_sa]] — Apollo evaluates frontier models on 11 agentic situational-awareness tasks; τ-bench is the benign-deployment counterpart to that benchmark's adversarial framing.
- [[in_context_scheming]] — Meinke et al. also run frontier models through tool-use trajectories with policy documents, but with goal-installed-in-context to elicit scheming rather than to measure compliant reliability.

---

*Follow-ups not entered separately: τ²-bench and τ³-bench (Sierra Research) extend this framework to additional domains and tighter reliability metrics. Add as separate entries when those papers are reviewed.*
