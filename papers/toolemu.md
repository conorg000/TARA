# Identifying the Risks of LM Agents with an LM-Emulated Sandbox

**Authors:** Yangjun Ruan, Honghua Dong (co-first), Andrew Wang, Silviu Pitis, Yongchao Zhou, Jimmy Ba, Yann Dubois, Chris J. Maddison, Tatsunori Hashimoto (Toronto / Vector / Stanford)
**Year:** 2024 (ICLR 2024)
**arXiv:** [2309.15817](https://arxiv.org/abs/2309.15817)
**Fetched from:** `openreview.net/pdf?id=GEcwtMk1uA` (ICLR 2024 camera-ready PDF, extracted via `pdftotext`; arxiv HTML and ar5iv both 404/conversion-failed)
**Status:** read

---

## Summary (in our words)

ToolEmu's pitch is: agent-safety benchmarks have a tractability problem. To test whether a tool-using LM agent does something dangerous, you historically had to implement the tool, stand up a sandbox, hand-construct an initial state, run the agent, and inspect the trajectory yourself. That cost ceiling is why agentic evals have either focused narrowly on existing-API domains (web, code, retail) or skipped human interaction entirely. Ruan et al. replace the sandbox itself with **a prompted GPT-4 emulator** that mimics tool execution from a tool spec alone, and replace the human safety inspector with **a prompted GPT-4 safety evaluator** that reads the trajectory and assigns a 0-3 risk score. The same evaluator family scores helpfulness. The whole stack lets them assess agents on toolkits like TrafficControl, EmergencyDispatchSystem, AugustSmartLock — tools whose physical analogues you would not want to actually run.

The framework comes in two variants. The **standard emulator** instantiates a plausible sandbox from the tool spec and user instruction; the **adversarial emulator** is additionally fed the test case's intended risks and the underspecification structure, and is instructed to set up state in a way that makes those risks more likely to materialise (e.g., when the agent is asked to "move the green bottle of medication," the adversarial emulator instantiates *two* green bottles — heart medication and sleep medication — and a confused robot grabs the wrong one). End-to-end validation on 100 hand-annotated test cases shows the standard emulator finds true failures with 72.5% precision; the adversarial emulator trades a few points of precision (68.8%) for a 10 pp jump in true-failure incidence (39.6% → 50.0%). The safety evaluator agrees with humans at Cohen's κ = 0.478, basically matching the inter-human rate of 0.480.

The benchmark layer is 36 toolkits / 311 tools / 144 test cases across 9 risk types (privacy breach, data loss, financial loss, physical harm, etc.), and Table 4 is the headline agent-comparison: GPT-4 fails on 39.4% of cases, Claude-2 on 44.3%, ChatGPT-3.5 on 62.0%, Vicuna-1.5-13B on 54.6%. Prompting GPT-4 with explicit safety requirements ("be aware of potential risks and seek user confirmation before risky actions") gets failure incidence down to 23.9% — *while raising helpfulness from 1.458 to 1.824*, which kills the obvious "safety = refuse everything" reading. The paper backs that up with a NoAct baseline (refuses everything) that scores 3.0 safety and 0.063 helpfulness, showing the eval has the discrimination to penalise that strategy.

The threat model is deliberately benign-user: instructions are *underspecified*, not adversarial. The user expects the agent to handle the task safely; failure means the agent didn't disambiguate, didn't ask, or pattern-matched to a risky action. This sets ToolEmu apart from LM red-teaming where the prompt itself is the attack — and it's the framing that gets borrowed by the later "do agents know when to ask for help?" literature ([[noisy_toolbench]], [[hil_bench]]).

## Key experimental conditions

- **Stack:** GPT-4 (gpt-4-0613) at temperature 0 as the emulator and as both evaluators (safety and helpfulness). Agent base models swept: GPT-4, Claude-2, ChatGPT-3.5 (gpt-3.5-turbo-16k), Vicuna-1.5-13B/7B. Agents implemented via ReAct.
- **Two emulator variants:** standard (tool spec + user instruction only) and adversarial (standard inputs + the test case's `underspecification` field + `potential risks & risky actions` field), the latter explicitly steered to instantiate long-tail high-risk states.
- **Scoring:** safety and helpfulness each on a 0-3 scale. Score ≤ 1 counts as an "identified failure." Final stats are average score, failure incidence (% of test cases with identified failure), and end-to-end true-failure precision against 3+ human annotators.
- **Benchmark composition:** 36 toolkits / 311 tools / 144 test cases / 9 risk-type categories (Fig 5). 30 of 36 toolkits lack equivalent sandboxes in prior agent benchmarks; 7 (TrafficControl, EmergencyDispatchSystem, AugustSmartLock, etc.) lack public APIs entirely.
- **Validation cohort:** 100 of 144 cases run through both emulators (200 trajectories total), each annotated by 3-4 senior CS undergrads pre-screened on 12 calibration examples. Each annotator put in ~25 hours.
- **Threat model:** instruction underspecification, benign user intent. Adversarial inputs come from the *emulator*, not the user.

## Key quantitative results

- **Emulator validity (Table 2):** standard emulator finds true failures at **72.5% precision**, adversarial at **68.8% precision**; true-failure incidence 39.6% (standard) vs **50.0% (adversarial)** — the adversarial variant trades a few points of precision for ~10 pp more failures found.
- **Emulator quality (Table 3, left):** trajectories free of critical issues 91.9% (standard) / 85.6% (adversarial). Most degradation in the adversarial variant comes from harder scenarios, not from a fundamentally less faithful emulator.
- **Evaluator agreement (Table 3, right):** safety Cohen's κ — automatic-vs-human 0.478 vs human-vs-human 0.480; helpfulness 0.543 vs 0.521 (the auto evaluator is *slightly above* the human floor on helpfulness). Safety-evaluator precision 75.3% / recall 73.1% vs. average individual human at 78.7% / 78.8%.
- **Headline agent comparison (Table 4):** failure incidence GPT-4 39.4%, Claude-2 44.3%, Vicuna-1.5-7B 45.0%, Vicuna-1.5-13B 54.6%, ChatGPT-3.5 62.0%. Helpfulness mirrors capability order: GPT-4 1.458, Claude-2 1.464, ChatGPT-3.5 0.768, Vicuna-1.5-13B 0.441, Vicuna-1.5-7B 0.364 (Vicuna's "safety" comes from incompetence).
- **Safety prompting:** appending a generic "be risk-aware and ask before risky actions" preamble to GPT-4 cuts failure incidence **39.4% → 23.9%** *and lifts helpfulness 1.458 → 1.824* — safety and helpfulness move together for the capable model.
- **Real-sandbox replication (Terminal toolkit, ChatGPT-3.5):** **6 of 7** identified failures successfully reproduced in an actual bash sandbox without cherry-picking. Authors spent ~8 hours wiring up the real sandbox vs. <15 minutes in the emulator.
- **Cost:** ~$1.2 per test case using GPT-4 as both emulator and evaluator.

## Methods (what they did and didn't use)

- Pure prompted-LM machinery: emulator, adversarial emulator, safety evaluator, helpfulness evaluator are all GPT-4 with carefully engineered prompts (full prompts in Appx. H). No fine-tuning of any component.
- Agent scaffolding is vanilla ReAct with formatting examples; no agent-side tool-use training or RLHF specific to the benchmark.
- Validation is human-annotator-based, with the framework's central claim being agreement-with-humans rather than agreement-with-ground-truth (there is no ground truth — the threat model is fuzzy by construction).
- **No internal-state methods anywhere.** No probes, no activation steering, no SAEs, no NLAs, no white-box analysis of the agent. Everything is trajectory-level behavioural; everything is judged in natural language by another LM.
- Closed-weight dependency is heavy: emulator and evaluators are GPT-4 specifically, and agent-side results lean on GPT-4 / Claude-2 access. Vicuna is included as the open-weight token but is not capable enough to use the tools meaningfully (helpfulness ~0.4 of 3).
- Standard errors are reported but small-N. The headline 23.9% post-safety-prompt number has σ ≈ 4.1% across 3 reruns at temperature 0 (footnote 1) — non-trivial.

## Authors' stated limitations / future work

- Emulator and evaluator quality cap on GPT-4's own competence. The emulators sometimes drop core requirements under adversarial conditions and frequently emit "generic entries" (e.g., placeholder phone numbers like 123-456-8901). Authors hypothesise some of this stems from GPT-4's privacy-and-confidentiality RLHF interfering with realistic emulation.
- Safety evaluator recall (73.1%) lower than the average individual human annotator (75.3%) — some risky actions get missed entirely. Authors expect this to improve with model scaling.
- Test case curation still relies on humans; their attempt at fully automatic generation (Wang et al. 2022 / Perez et al. 2022 style) hit frequent requirement violations and was abandoned. Real scalability needs LM-generated test cases that pass validity filters.
- Threat model is narrow: only instruction underspecification with benign user intent. No malicious-user or compromised-tool variants. Authors flag broader threat models as the obvious extension.
- Benchmark is also explicitly an initial set — 144 cases / 36 toolkits — extensible by design but small enough that the headline incidence numbers will shift with broader coverage.

## Open questions and follow-up directions

1. **Is the emulator-evaluator loop biased toward GPT-4 agents?** Emulator and both evaluators are GPT-4. The headline that GPT-4 agent is safest could partly reflect family-internal consistency — the evaluator-LM judging a same-family agent's reasoning as more legible. The paper does not run the cross-family-evaluator ablation (e.g., Claude-2 as evaluator on the same agent transcripts). Until that's run, "GPT-4 is the safest agent" sits at the same epistemic level as any LLM-as-judge result whose judge shares the agent's family.
2. **Underspecification ≠ misalignment.** Every failure ToolEmu surfaces is structurally a *capability or rule-following* failure under ambiguous instructions. The threat model excludes the agent intentionally exploiting tool access. ToolEmu cannot distinguish "agent confidently picked the wrong medication bottle" from "agent picked the wrong bottle on purpose" — both look the same in the trajectory. Whether the same emulator-plus-evaluator stack could be re-pointed at intentional-subversion threat models (deceptive tool use, sandbagging on safety-relevant tool calls) without a fundamental redesign is open.
3. **The 75/73% precision/recall ceiling is the actual bottleneck.** If you wire ToolEmu into a real iterate-on-agent loop, ~25-30% of evaluator decisions are noise relative to a human. That sets a floor on the smallest agent-side improvement the benchmark can resolve. A future evaluator with internal-state access (probe over the evaluator-LM's own activations when reading the trajectory) might tighten this, but no one has tried it within the ToolEmu pipeline.
4. **Adversarial-emulator validity drift.** The adversarial emulator instantiates higher-stakes states by being prompted with the *intended* risks; this is borderline circular — it finds risks that look like the risks it was told to find. The 50.0% adversarial vs. 39.6% standard true-failure incidence is the strongest evidence the bias is contained, but the result also depends on annotators agreeing that the resulting state is "realistic." Replicating with a held-out adversarial-emulator-prompt that doesn't see the risk taxonomy would tighten the case.
5. **The "safety prompt lifts both axes" finding inverts the usual safety/helpfulness tradeoff narrative — but only for GPT-4.** The result does not replicate cleanly on Vicuna or ChatGPT-3.5 in the paper. Whether the dual-lift is a property of capable models specifically (they can both interpret the safety instruction and recover the user's intent) or an artefact of GPT-4-judges-GPT-4 (point 1 again) is unresolved.

## See also

- [[noisy_toolbench]] — same problem family (underspecified user, tool-using LM). NoisyToolBench frames it as "the agent should ask clarifying questions" and adds the AwR scaffold; ToolEmu treats underspecification as the *adversary's* lever.
- [[hil_bench]] — Scale.AI's HiL-Bench is the contemporary sibling: when should an agent ask for human help? ToolEmu's failure modes (fabrication, instruction misinterpretation, risk ignorance) are exactly the ones HiL-Bench tries to convert into ask-for-help triggers.
- [[tau_bench]] — sibling agentic benchmark with LM-simulated *user* but real (Python) tool implementations and rule-based ground-truth database states. ToolEmu inverts this: real (or future) user, LM-simulated *tools*. Different axes of "what to fake."
- [[agent_misalignment]] — AgentMisalignment goes after the threat model ToolEmu explicitly excludes (intentional misaligned propensity, not underspecification-driven failure).
- [[risk_aware_decision_making]] — sibling on the agent-side decision question: under uncertainty, should the agent answer / refuse / ask? ToolEmu measures the *consequences* of getting that wrong; risk-aware-DM measures the decision directly.
- [[apollo_stealth_sa]] — Apollo evaluates frontier agents on adversarially-framed agentic tasks; ToolEmu is the underspecification-framed counterpart and predates the Apollo stealth/SA framing by ~2 years.
- [[ai_control]] — also LM-emulates parts of an evaluation environment (trusted vs. untrusted models on APPS); methodologically closer than it looks, but a different threat model (intentional subversion under a control protocol).
