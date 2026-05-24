# Learning to Ask: When LLM Agents Meet Unclear Instruction

**Authors:** Wang, Shi, Ling, Chan et al. (Renmin University / CUHK / Johns Hopkins / Xiaohongshu)
**Year:** 2024 (EMNLP 2025)
**arXiv:** [2409.00557](https://arxiv.org/abs/2409.00557)
**Fetched from:** `arxiv.org/html/2409.00557`
**Status:** read

---

## Summary (in our words)

The setup: LLM-as-agent papers usually evaluate tool-use on clean, well-specified instructions. In the wild, user instructions are noisy — missing slot values, ambiguous referents, factual errors, or asks the available tools cannot satisfy. The authors collect 1,000 real user-written queries against a fixed tool catalogue and classify the failures into four buckets: Instructions Missing Key Information (56.0%), Instructions with Errors (17.3%), Instructions Beyond Tool Capabilities (15.3%), Instructions with Multiple References (11.3%). The bulk of real-world noise is just under-specification.

What they build: **NoisyToolBench**, a 200-instruction benchmark derived from ToolBench (100 APIs across 49 categories) where each clean instruction is manually corrupted into one of the four noise types and annotated with the question the agent *should* ask, the answer to that question, and the expected downstream function call. They pair this with **ToolEvaluator**, an automated scorer using sentence-transformer similarity for clarification-question matching (A1) and GPT-4o as judge for API-call correctness (A2, A3) plus simple counters for redundant questions and total steps.

The intervention: **Ask-when-Needed (AwN)** is a prompting recipe — a short addition to the system prompt instructing the model to (a) check whether the user instruction has enough information to call an API, (b) ask a clarifying question if not, and (c) refuse if the request is outside tool capabilities, before generating any tool call. No fine-tuning, no internal-state methods.

What's interesting: gains are large but uneven. On GPT-4o + CoT, A1 (asking the right question) jumps 0.52 → 0.90 and A2 (correct downstream API call) moves 0.48 → 0.58. On GPT-4o + DFSDT (depth-first search decision tree baseline), A2 jumps 0.20 → 0.60 — a far bigger absolute swing, suggesting the strong tree-search baseline was bottlenecked precisely on missing slot values that clarification fills in. AwN does not hurt performance on the clean ToolBench instructions (Table 4) and transfers to ShortcutsBench (+6.5pp). The paper's honest framing is that "there is still a big gap to perfect" — even with AwN, A2 on the hardest model/baseline combos sits well below ceiling.

## Key experimental conditions

- 200 modified problem-free ToolBench instructions, hand-corrupted into the four noise types
- 100 APIs across 49 ToolBench categories
- Models: GPT-3.5, GPT-4, GPT-4o, Claude-3.5, Gemini-1.5, DeepSeek-v3, DeepSeek-R1, O3-mini (closed-weight frontier + open-weight reasoning models)
- Baselines: Chain-of-Thought (CoT) and Depth-First Search Decision Tree (DFSDT)
- Five metrics: A1 (asks the right clarifying question, sentence-similarity matched), A2 (correct API call given clarification answer), A3 (extracts the right info from prior API calls), Re (redundant question count), Steps (mean actions to completion)

## Key quantitative results

- GPT-4o + CoT: A1 0.52 → 0.90; A2 0.48 → 0.58 with AwN
- GPT-4o + DFSDT: A1 0.58 → 0.88; A2 0.20 → 0.60 — DFSDT's headroom is bigger, because the tree-search baseline lacked the missing slot values until clarification produced them
- GPT-4 + CoT: redundant-question count stays in 0.16-0.36 range with AwN — clarification doesn't degenerate into over-asking
- Clarifying-question relevance: 4.2/5 in user study
- ShortcutsBench transfer: up to +6.5pp API selection accuracy
- Performance preserved on clean ToolBench instructions (Table 4)

## Methods (what they did and didn't use)

- Behavioural / prompting only. The intervention is a system-prompt addition; no fine-tuning, no RL, no activation analysis.
- LLM-as-judge for two of the five metrics (A2, A3 use GPT-4o); sentence-transformer cosine similarity for A1.
- Mix of closed-weight (GPT-*, Claude-3.5, Gemini-1.5) and open-weight (DeepSeek) models — reasoning-model coverage (O3-mini, DeepSeek-R1) is present but not the centrepiece.
- No internal-state methods. No probes, no SAEs, no activation steering. All evidence is behavioural transcripts scored by external judges.
- Closed-weight dominance limits reproducibility of headline numbers.

## Authors' stated limitations / future work

- "Although AwN can improve the performance, there is still a big gap to perfect" — they explicitly frame this as a first step, not a solved problem.
- The automatic evaluator is "not 100% accurate, leading to some potential false negatives and false positives"; they call for better auto-evaluation.
- Future work named: fine-tuning on NoisyToolBench rather than just prompting, integration with more advanced agent frameworks, and mixed clear/unclear instruction scenarios to test whether the model can discriminate when to ask vs. when to act.

## Open questions and follow-up directions

1. The A1 → A2 gap is the load-bearing finding the paper does not fully unpack. On GPT-4o + CoT, asking the right question goes 0.52 → 0.90 but downstream API-call correctness only moves 0.48 → 0.58. Either the model asks the right thing then fails to use the answer, or A2 has a ceiling unrelated to clarification quality. Decomposing this gap would tell us how much of tool-use failure is really an ambiguity-resolution problem vs. a planning problem.
2. AwN is a prompting recipe; whether the same gains survive when "ask when needed" is fine-tuned in (vs. prompted on top) is open and would matter for distinguishing a capability gap from a prompting gap.
3. The benchmark is hand-corrupted from a clean base. The 1,000-query taxonomy is real-world, but the 200 evaluated instructions are synthetic noise. Whether AwN gains transfer to genuinely user-written noisy instructions — where the noise types are mixed and the boundaries between categories blur — is untested.
4. The model has to decide *whether* to ask, not just what to ask. The paper measures redundant-question rate at 0.16-0.36 for the best configurations, but does not characterise when asking is the wrong move on clean instructions. A direct test on mixed clean/unclear batches would surface whether AwN models become annoyingly chatty.
5. DFSDT's outsized gain from AwN (A2: 0.20 → 0.60) hints that strong tool-search baselines are bottlenecked on slot information rather than search. If true, the same clarification step bolted onto other agent frameworks (ReAct, Reflexion, etc.) should produce similar swings — a clean replication target.

## See also

- [[cot_faithfulness]] — adjacent in that both ask whether an extra prompted reasoning step actually does what it says; AwN's clarification step succeeds behaviourally without internal-state verification.
- [[low_probability_actions]] — both papers measure agent behaviour under instruction-level uncertainty, but the framing differs: AwN wants agents to ask when uncertain; low-probability-actions papers care about rare unprompted actions.
