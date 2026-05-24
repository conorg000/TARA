# Evaluating LLM Agent Adherence to Hierarchical Safety Principles

**Authors:** Ram Potham (independent researcher; GitHub `rapturt9`)
**Year:** 2025
**arXiv:** [2506.02357](https://arxiv.org/abs/2506.02357)
**Venue:** Submitted to ICML 2025 Technical AI Governance (TAIG) workshop (per arXiv comments — submission, not confirmed acceptance)
**Fetched from:** `https://arxiv.org/html/2506.02357` (native arXiv HTML, full body)
**Status:** read

---

## Summary (in our words)

We have a small, neat behavioural benchmark that asks a different question from the usual "can the agent do the task?" or "will the agent comply with safety instructions?". The question here is: when a safety instruction and a task instruction *interact*, what actually happens — does the model follow the principle, sacrifice task performance, or quietly look compliant for reasons that have nothing to do with principled choice?

The setup is deliberately spartan: a 4x4 MiniGrid environment, six LLM agents acting through a tool-call action interface (turn, move, pickup, drop, toggle door, end turn), three hierarchical safety principles (avoid red floor; never pick up the blue key; always pick up the yellow ball before toggling any door), and four scenarios per principle that systematically vary whether the principle conflicts with the task in an unavoidable or avoidable way. Each (model, principle, scenario, principle-on/off) cell gets 10 episodes for 1,440 episodes total. The whole thing is inference-time prompting — no fine-tuning, no probes, no activation work.

The two findings the author gives proper names to are the interesting bit. **Cost of compliance**: turning the principle on costs real task performance even when a safe compliant path exists. The cleanest example is P1-S3 (red detour with safe route available) where task success drops 80% -> 14% on principle activation. **Illusion of compliance**: high adherence rates can come from inability rather than choice. Llama Scout looks safe largely because it can't reliably execute the unsafe-but-task-completing action either; reasoning-trace models look near-perfect (o4-mini at 100% adherence, Gemini 2.5 Flash Thinking at 97%) while non-reasoning standard models sit at 67-75%. The author argues neither pattern is what you actually want from a "safety eval".

The reach of this paper is modest — single author, tiny environment, 10 episodes per condition — but the conceptual handles ("cost of compliance" / "illusion of compliance") are sharp and we expect to reuse them. The capability/propensity disambiguation problem it surfaces is the same one Apollo's precursor-evals note flags from a different angle.

## Key experimental conditions

- **Environment:** MiniGrid 4x4 fully-observable gridworld. Agent starts (1,1) facing East. Universal task: reach a green goal square.
- **Action interface:** Tool-call API with `turn_left`, `turn_right`, `move_forward`, `pickup`, `drop`, `toggle`, `end_turn`.
- **Models (n=6):** o4-mini, Gemini 2.5 Flash Thinking (reasoning-trace); Gemini 2.0 Flash, GPT-4o mini (standard); Llama 4 Scout, Llama 4 Maverick (open weights). Closed-weight dominated.
- **Principles (3):**
  - P1 — Zone Avoidance: "Never move onto RED floor tiles" (negative framing).
  - P2 — Object Prohibition: "Never pick up BLUE Key" (negative framing).
  - P3 — Procedural Integrity: "Always pick up YELLOW Ball BEFORE toggling any Door" (positive framing).
- **Scenarios per principle:** 4 (S1-S4), split 2 conflict-unavoidable / 2 conflict-avoidable. E.g. P1-S3 = "red detour with a safe path available"; P2-S3 = blue/yellow key choice; P3-S3 = ball available openly but distant.
- **Conditions:** principle ON vs principle OFF (control). 10 episodes per cell.
- **Total episodes:** 6 models * 3 principles * 4 scenarios * 2 conditions * 10 = 1,440.

## Key quantitative results

- **Principle Adherence Rate (PAR) across P-ON scenarios:**
  - o4-mini: 100%
  - Gemini 2.5 Flash Thinking: 97%
  - GPT-4o mini: 75%
  - Gemini 2.0 Flash: 67%
  - (Llama Scout / Maverick numbers not pulled cleanly from the HTML body — author treats these as the "illusion of compliance" cases where high adherence reflects general inability.)
- **Cost of compliance (P1-S3):** Task Success Rate 80% (P-OFF) -> 14% (P-ON). This is the headline drop.
- **Reasoning vs standard split:** reasoning-trace models 97-100% adherence; standard models 67-75%.
- **Framing asymmetry:** P3 (positive framing) -> near-perfect adherence across models; P1 and P2 (negative framings) -> high variance.
- **Model-resilience asymmetry:** o4-mini holds ~40% task success under principle constraints; Gemini 2.5 Flash Thinking holds high adherence but collapses from >80% to ~20% task success — high PAR does not protect TSR uniformly.

## Methods (what they did and didn't use)

- Purely **behavioural** evaluation — outcome metrics (TSR, PAR) over recorded action traces in a deterministic gridworld.
- **No internal-state methods.** No linear probes, no SAEs, no activation steering, no attention analysis. Evidence is entirely action-trace based.
- **No training-time intervention.** No RL, no fine-tuning, no preference learning. All inference-time prompted constraints on off-the-shelf models. Constitutional AI and instruction-hierarchy work are cited as prior context, not as ingredients of the method.
- Closed-weight dominated model panel (o4-mini, GPT-4o-mini, Gemini family) — reproducibility relies on commercial API availability over the lifetime of the benchmark.
- Small-n statistics: 10 episodes per condition cell. The author explicitly flags this as a limitation.

## Authors' stated limitations / future work

- **Environment too simple.** 4x4 gridworld with a fixed action vocabulary is far from realistic agentic deployment.
- **Limited trials.** 10 episodes per cell; the author wants more.
- **Cannot robustly distinguish principled compliance from incapability.** Explicitly named as an open methodological problem — the "illusion of compliance" is partly a measurement artifact the paper can identify but not resolve.
- **More nuanced principles.** Current principles are binary, atomic, and clean; real-world principles aren't.
- **Better metrics.** Future work should disambiguate compliance-from-choice vs. compliance-from-inability.

## Open questions and follow-up directions

1. **Disambiguating compliance from incapability is the load-bearing measurement problem the paper surfaces but does not solve.** Behavioural evidence alone struggles here — a model that can't pick up the blue key looks identical to a model that won't. Internal-state methods (probes for "considered the unsafe action", representation-level capability checks) are the natural complement and are conspicuously absent from this paper. Whether they would in fact separate the two populations on this benchmark is open.

2. **Framing asymmetry (P3 positive vs P1/P2 negative) is a real signal but underdiagnosed.** Near-perfect adherence on "always do X before Y" vs high-variance adherence on "never do X" could be about positive-vs-negative phrasing, about procedural-vs-prohibitive content, or about which constraints are easier to verbalise in CoT. The 3-principle design cannot decompose these.

3. **Generalisation to non-toy environments.** The 4x4 MiniGrid result tells us essentially nothing about cost-of-compliance magnitudes in code-execution or web-agent settings, where the action space is unbounded and "safe alternative paths" may be many orders of magnitude more costly to find. The phenomenon almost certainly persists; the size is anyone's guess.

4. **Reasoning-trace vs standard split is confounded by capability.** o4-mini and Gemini 2.5 Flash Thinking outperform their standard counterparts on adherence, but they also outperform on raw task ability. Whether reasoning helps with principle-following *per se*, or whether it just helps with everything, is not separated here.

5. **Static principles vs dynamic constraints.** Real safety instructions in deployment are contextual ("don't take destructive action without user confirmation in this specific session"). All three principles here are session-invariant. The result that even invariant principles produce measurable cost-of-compliance suggests the dynamic case is harder, but it's not tested.

## See also

- [[apollo_precursor_predictive]] — same capability-vs-propensity disambiguation problem in the scheming-evals literature; their precursor evals correlate with capability not with scheming, which is structurally the same issue as "illusion of compliance".
- [[in_context_scheming]] — Apollo's frontier-model scheming evaluation also uses prompted goal installation + behavioural traces in an agentic setting; same methodological family, much higher-stakes principles.
- [[ih_challenge]] — OpenAI's instruction-hierarchy RL fine-tuning paper is the training-time complement to this paper's inference-time evaluation of hierarchical principles.
- [[low_probability_actions]] — explicit capability/propensity decomposition; models can execute given p* but cannot derive p* from task structure, which is the same shape as "high PAR may mean unable, not unwilling".
- [[ai_control]] — control-protocol framing assumes the principle is enforceable and asks "what's the safety/usefulness frontier?"; this paper measures the cost side of that frontier in a tiny sandbox.
