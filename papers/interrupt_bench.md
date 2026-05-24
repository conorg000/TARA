# When Users Change Their Mind: Evaluating Interruptible LLM Agents in Long-Horizon Web Navigation

**Authors:** Zou, Miao, Huang, Chen, Zhou, Zhang, Wu, Fang, Gu, Z. Zhang, Zheng, Wang, Nian, Li, Fan, He, W. Zhang, Liu, Yu (UIC / McGill / MBZUAI / UCSB / USC)
**Year:** 2026 (arXiv 2604.00892, late 2025 submission)
**arXiv:** [2604.00892](https://arxiv.org/abs/2604.00892)
**Fetched from:** `arxiv.org/html/2604.00892` (native HTML)
**Status:** read

---

## Summary (in our words)

The setup is straightforward in shape but rare in agent-eval: take a long-horizon WebArena-Lite task, let an LLM agent get partway through it, then have the "user" interrupt mid-trajectory with a change of mind. The change can be an **addition** (new requirement), a **revision** (correction of the original ask), or a **retraction** (drop a constraint). The interruption is injected at a controllable position in the trajectory — the headline configuration is 60%, but the appendix sweeps positions and finds optimum varies by model. The benchmark is called InterruptBench; six frontier-ish backbones run in the WebAgent-R1 scaffolding (Claude Haiku/Sonnet/Opus 4.5, Qwen3-Coder-480B-A35B, DeepSeek-V3.1, Mistral-Large-3).

Two findings sit at the centre. First, even strong models stay bad in absolute terms: from a 0-interruption baseline of ~3–5% success, **Claude Opus 4.5 climbs to 21% with one interruption, 36% with two, 42% with three** — the gains accumulate but they're not big numbers. Second, the *quality* of post-interruption behaviour splits sharply by model class. The paper's S/F vs F/S vs S/S vs F/F quadrant analysis (did the agent succeed without interruption / with interruption — four combinations) shows the larger Claude models are reasonably good at *repairing* a failed-without-interruption trajectory using the new information, while smaller and open-weight models tend to convert hits into misses when interrupted. Token overhead, not extra actions, dominates the adaptation cost.

The mechanism story the authors tell is behavioural and unflattering: agents "continue with stale assumptions, fail to reconcile the environment state with the updated intent," sometimes producing answers consistent with the original ask but inconsistent with the post-update goal. There's a sensible diagnosis here — long-horizon agents are bad at undoing decisions cached early in the trajectory — but the paper does not measure it internally. There are no probes, no activation analysis, no scratchpad/CoT-faithfulness checks, no internal-state methods at all. The evidence is task-success curves, token deltas, and outcome quadrants.

Worth flagging: this is the same task substrate (WebArena-Lite) and the same scaffolding family (WebAgent-R1) that several recent agent papers use, so the numbers are comparable across that ecosystem. The benchmark contribution is the **trajectory-grounded interruption synthesis pipeline** — interruptions are constrained to be semantically essential, ground-truth-consistent with the original task, and to read like natural user communication. That pipeline plus the position-controlled injection is the part likely to outlast the headline 2026-model leaderboard.

## Key experimental conditions

- Task substrate: WebArena-Lite long-horizon web navigation tasks
- Agent scaffolding: WebAgent-R1
- Six LLM backbones: Claude-Haiku-4.5, Claude-Sonnet-4.5, Claude-Opus-4.5, Qwen3-Coder-480B-A35B, DeepSeek-V3.1, Mistral-Large-3
- Three interruption types: Addition (new constraint), Revision (correct prior query), Retraction (drop constraint)
- Default injection position: 60% through the trajectory; appendix E sweeps positions {0.2, 0.4, 0.6, 0.8}
- Multi-interruption setting: 0, 1, 2, 3 sequential interruptions per episode
- Synthesised interruptions filtered for (a) ground-truth consistency with original intent, (b) essentiality (problem unsolvable without honouring the interruption), (c) natural communication style

## Key quantitative results

- **Multi-interruption converged success rate (no int. → 3 int.):** Claude-Haiku-4.5 5.45% → 38.79%; Claude-Sonnet-4.5 4.24% → 41.21%; Claude-Opus-4.5 5.45% → 41.82%; Qwen3-235B 4.24% → 23.64%; DeepSeek-V3.1 4.85% → 20.61%; Mistral-Large-3 3.03% → 13.94%
- **Addition-scenario outcome quadrants (Claude-Opus-4.5):** S/F=11, F/S=70, S/S=21, F/F=73 — strong "rescue" behaviour (F/S dominates S/F by ~6×)
- **Addition-scenario outcome quadrants (Mistral-Large-3):** S/F=5, F/S=27, S/S=9, F/F=124 — weak rescue, dominated by F/F
- **Token overhead (addition, ΔT per episode):** Claude-Haiku +1699; Claude-Sonnet +671; Claude-Opus +138; Qwen3 +38; DeepSeek +186; Mistral-Large +89 — Haiku pays roughly an order of magnitude more tokens than the larger Claudes
- **Action overhead (addition, ΔA):** typically <1 extra action and sometimes negative — efficiency cost is in tokens, not steps
- **Revision (Claude-Opus-4.5):** F/S=86, S/F=1, ΔT ≈ −785 (revision actually reduces token use vs. baseline)
- **Retraction (Claude-Opus-4.5):** ΔT ≈ −1061 (token savings from dropped constraint)
- **Post-interruption success curve SR(k):** rises rapidly within ~10 actions then plateaus across models
- **Position sensitivity:** larger models peak around 0.8 (late interruption); smaller models peak around 0.2 (early interruption)

## Methods (what they did and didn't use)

- Behavioural eval only: task-success rates, action counts, output-token counts, paired-outcome quadrant analysis
- Rule-based task verification (String Match / URL Match / Program Execution) inherited from WebArena-Lite
- Interruption synthesis via LLM with semantic constraints (prompts in Appendix F); no human curation reported
- Position-controlled trajectory injection — the interruption is appended at a chosen fraction of the agent's executed trajectory, then the agent continues
- **No internal-state methods of any kind.** No linear probes, no activation steering, no SAEs, no NLAs, no CoT-faithfulness analysis, no token-level attribution
- All six backbones are closed-weight or open-weight via API; no fine-tuning, no weight access required for the eval itself

## Authors' stated limitations / future work

- "Handling user interruptions effectively and efficiently during long-horizon agentic tasks remains challenging for powerful large-scale LLMs" — the headline absolute success rates are low
- Multi-interruption gains are "uneven and sometimes unstable" — open-weight models regress from 2 to 3 interruptions in some configurations
- Failure modes named: agents "continue with stale assumptions, fail to reconcile the environment state with the updated intent," producing answers "inconsistent with the post-update goal"
- Future work named: "stronger mechanisms for state tracking, intent reconciliation, and error recovery during execution"

## Open questions and follow-up directions

1. The benchmark measures outcome but not mechanism. Whether agents fail because they (a) don't notice the interruption, (b) notice but don't update their plan, or (c) update the plan but execute against stale cached subgoals is not separated — these have very different mitigation implications and would require either CoT-trace analysis or internal-state methods the paper doesn't use.
2. The position-sensitivity asymmetry (large models peak late, small models peak early) is reported but not explained. A natural test is whether it reflects context-length effects, planning-depth effects, or something about how each model architecture caches partial-trajectory state.
3. Interruptions are synthesised by LLM under semantic constraints — the distribution of interruption phrasings may differ systematically from real users, particularly in clarity and directness. A small human-written interruption test set would calibrate the synthetic-data trust.
4. Retraction is the most ecologically common interruption type (users drop requirements all the time) and shows the largest token savings, but the paper does not isolate whether the model is genuinely *honouring* the retraction or just losing track of the dropped constraint. A faithful-execution check (did the agent's final state respect the retracted constraint?) would distinguish these.
5. The S/F → F/F transitions (interruption converts a success into a failure) are the safety-relevant cell — these are cases where the user's mind-change made the agent worse. The paper reports the counts but does not characterise these cases qualitatively; a small case-study of S/F transitions would say more about agent brittleness than the headline averages.

## See also

- [[tau_bench]] — sibling agent benchmark with user-in-the-loop interaction; complementary axis (tau-bench tests user *consistency*, InterruptBench tests user *inconsistency*)
- [[hil_bench]] — agents-deciding-when-to-ask-for-help benchmark on similar 2026-frontier model lineup
- [[iheval]] — instruction-hierarchy following, adjacent failure mode (which instruction supersedes which)
- [[ih_challenge]] — RL fine-tuning to fix instruction-hierarchy failures; a natural mitigation target for the same failure class
