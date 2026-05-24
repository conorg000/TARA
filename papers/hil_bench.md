# HiL-Bench (Human-in-Loop Benchmark): Do Agents Know When to Ask for Help?

**Authors:** Elfeki, Trinh, Luu, Luo, Hunt, Montoya, Marwaha, He, Wang, Carabedo, Castillo, Liu (Scale.AI)
**Year:** 2026
**arXiv:** [2604.09408](https://arxiv.org/abs/2604.09408)
**Fetched from:** `arxiv.org/html/2604.09408v1`
**Status:** read

---

## Summary (in our words)

HiL-Bench is a benchmark paper from Scale targeting a specific failure mode that standard agent evals don't see: agents confidently guessing when the task spec is incomplete, ambiguous, or contradictory. The setup takes 300 tasks (150 SWE-Bench Pro problems, 150 BIRD SQL problems), has human annotators strip or obscure 3-5 critical pieces of information per task ("blockers"), and gives the agent an `ask_human()` tool that returns the missing information *only* when the agent's question targets a registered blocker. The headline metric, Ask-F1, is the harmonic mean of question precision (relevant / total asked) and blocker recall (resolved / total registered), which closes off the obvious gaming strategy of just asking everything.

The core finding is what the authors call a judgment gap. With full information, the four tested frontier models (GPT 5.4 Pro, GPT 5.3 Codex, Claude Opus 4.6, Gemini 3.1 Pro) hit 75-89% pass on SQL and 64-88% on SWE. With blockers in place and the `ask_human()` tool available, pass rates collapse to 17-38% (SQL) and 4-24% (SWE). The drop is not capability — it's that the models almost never ask. Average Ask-F1 is 40.5% on SQL and 37.4% on SWE. Each model has a distinct failure signature in the trace analysis: GPT 5.4 Pro and 5.3 Codex execute confidently on wrong beliefs; Claude Opus 4.6 explicitly recognises infeasibility in CoT but submits anyway ("uncertainty detection without resolution"); Gemini 3.1 Pro is the most externally correctable, responding strongly when given grounding on SQL.

The paper also shows the skill is trainable. Fine-tuning Qwen3 32B with LoRA in SkyRL using a shaped reward (+0.3 per step for targeting a registered blocker, −0.1 for irrelevant/duplicate, terminal reward proportional to blockers discovered) improves both precision and recall on held-out tasks, and Ask-F1 gains correlate with pass@3 gains. SQL-trained transfer to SWE works, which they take as evidence that help-seeking is a domain-general trainable skill rather than benchmark-specific pattern matching.

This is a purely behavioural benchmark — no probes, no activation steering, no internal-state analysis. The failure taxonomy is built by LLM-judge classification of 3,600+ traces across tool-use / alignment / logic dimensions. The `ask_human()` tool itself uses a frozen Llama-3.3-70B-Instruct as semantic judge (97% precision, 91% recall against the registered trigger questions). For our purposes the most interesting wrinkle is the Claude Opus 4.6 signature: a model that articulates the problem in CoT and then ignores its own articulation. That's a behavioural-level decoupling between stated uncertainty and acted-on uncertainty.

## Key experimental conditions

- **Tasks:** 300 total — 150 SWE (from SWE-Bench Pro) + 150 SQL (from BIRD). 200/100 public/private split.
- **Blockers:** 1,131 total, ~3.77 per task. Distribution overall: 42% missing information, 36% ambiguous requests, 22% contradictory. SWE skew: 38.5% missing / 30.2% ambiguous / 31.3% contradictory. SQL skew: 45.3% missing / 41.3% ambiguous / 13.4% contradictory.
- **Three conditions per task:** baseline (blocked, no `ask_human()`), full information, with `ask_human()`.
- **Models tested:** GPT 5.4 Pro, GPT 5.3 Codex, Claude Opus 4.6, Gemini 3.1 Pro.
- **Scaffolding:** SWE-Agent for code tasks with standard tools + `ask_human()`; custom tools for SQL (business-logic retrieval, schema exploration, query execution).
- **Blocker quality criteria (7):** realism, criticality, objectivity, vast search space, independence, no contamination, non-contrived. Progressive-discovery design — blockers surface through execution, not upfront inspection.

## Key quantitative results

- **Judgment gap (SWE):** full-information pass 64-88% → `ask_human()` pass 4-24%.
- **Judgment gap (SQL):** full-information pass 75-89% → `ask_human()` pass 17-38%.
- **Ask-F1 averages:** SQL 40.5%, SWE 37.4%.
- **`ask_human()` semantic-judge validation:** 97% precision, 91% recall (Llama-3.3-70B-Instruct, frozen).
- **RL training (Qwen3 32B + LoRA, SkyRL):** trained on 120 tasks per domain, evaluated on 30 held-out. Shaped Ask-F1 reward improves both precision and recall on held-out; Ask-F1 gains correlate with pass@3 gains; SQL training transfers to SWE.
- **Reward shape:** per-step +0.3 (relevant) / −0.1 (irrelevant or duplicate); terminal = |blockers discovered| / |blockers total|, gated on ≥1 found.

## Methods (what they did and didn't use)

- Behavioural eval only. Models judged on whether they invoke `ask_human()`, what they ask, and whether they ultimately produce correct output.
- LLM-judge failure taxonomy across tool-use (Completion, Accuracy, Strategy), alignment (Accuracy, Strategy, Self-Assessment, Completion), and logic (Accuracy, Self-Assessment, Completion, Strategy) dimensions, applied to 3,600+ traces.
- RL training as demonstration that help-seeking is trainable, not just as a leaderboard contribution.
- **No internal-state methods used.** No linear probes, no activation steering, no SAEs, no natural-language autoencoders. Claude Opus 4.6's "uncertainty detection without resolution" pattern is inferred from CoT text, not from activations.
- Tested models are all closed-weight except the Qwen3 32B used for the RL demonstration. Reproducibility on the headline judgment-gap result depends on API access to the four frontier models.

## Authors' stated limitations / future work

- Benchmark covers two domains (SWE, SQL); generalisation to other agentic settings (long-horizon planning, multi-turn negotiation, tool composition) is open.
- The `ask_human()` tool is a semantic-judge oracle, not a real human — it can't model human friction, partial information, or follow-up clarification chains. Real deployment dynamics are not captured.
- Failure taxonomy is LLM-judge-classified; manual validation of the taxonomy at scale is not provided.
- RL demonstration uses one open-weight model (Qwen3 32B) at one scale with one reward shape; the trainability claim would be stronger with multiple model classes and reward variants.
- 300 tasks is modest for a benchmark; held-out subset for RL evaluation (30 tasks) is small.

## Open questions and follow-up directions

1. **The Claude Opus 4.6 signature is the most diagnostic finding.** A model that explicitly recognises infeasibility in CoT and submits anyway is a clean target for both behavioural and internal-state methods. Whether the gap between CoT-stated uncertainty and acted-on uncertainty corresponds to a separable internal-state signal is open — every probe paper in this space has trained on cleaner constructs (truthfulness, deception, eval-awareness) than "acknowledged-but-ignored uncertainty."

2. **Help-seeking as a capability/propensity decomposition.** The full-information condition shows the models can solve these tasks; the `ask_human()` condition shows they don't ask. This is structurally identical to the capability/propensity split in [[low_probability_actions]] and [[apollo_precursor_predictive]] — help-seeking is propensity at fixed capability. Whether the propensity signal is recoverable in activations before the model emits its final (unhedged) answer is a natural follow-up.

3. **Failure-mode specificity across models.** Four models, four distinct behavioural signatures. If this is reproducible across snapshots and prompts it suggests model-family-level disposition that survives capability matching — a more useful claim about model differences than capability benchmarks normally give. The paper doesn't test whether the signatures persist under prompt perturbation.

4. **Eval-awareness confound.** If models classify HiL-Bench tasks as evaluation contexts (cf. [[knowing_being_evaluated]]), the under-asking behaviour could be partly an eval-vs-deployment artifact rather than a deployment-relevant failure mode. The paper does not test this. A deployment-shaped variant (real codebase, real Slack-style human channel) would be a natural control.

5. **Whether Ask-F1 RL transfers under capability training.** [[anti_scheming_training]] showed deliberative-alignment gains erode under subsequent capability fine-tuning. The RL trainability claim here would be much stronger with the same robustness test — does an Ask-F1-trained model retain help-seeking after additional SWE-pass-rate-shaped training?

## See also

- [[low_probability_actions]] — capability/propensity decomposition at the behavioural level; HiL-Bench's judgment gap is a different instance of the same split (capability present, propensity to invoke absent).
- [[knowing_being_evaluated]] — eval-awareness baseline; any benchmark that puts agents in a deliberately-constructed scenario inherits this confound.
- [[confessions]] — also instruments a separately-rewarded auxiliary output (confession vs. ask_human) to elicit information the model otherwise withholds.
- [[ih_challenge]] — sibling Scale/OpenAI-style RL-on-benchmark paper; same shape (released benchmark + RL demonstration of trainability) on a different agent skill.
