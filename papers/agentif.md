# AgentIF: Benchmarking Instruction Following in Agentic Scenarios

**Authors:** Qi, Peng, Wang, Xin, Liu, Xu, Hou, Li (Tsinghua University / Zhipu AI)
**Year:** 2025 (NeurIPS 2025 D&B, Spotlight)
**arXiv:** [2505.16944](https://arxiv.org/abs/2505.16944)
**Fetched from:** `arxiv.org/html/2505.16944` (native arxiv HTML; full body, methods, tables, error analysis)
**Status:** read

---

## Summary (in our words)

The setup: existing instruction-following benchmarks (IFEval, FollowBench, ComplexBench) work on short prompts — typically 45-521 words — with a handful of crisp constraints. Real agentic system prompts look nothing like that. They are long, layered, and mix formatting requirements with tool-use rules and conditional logic. The authors argue that frontier LMs that look "good at instruction following" on IFEval may be much worse when the prompt actually resembles a production agent system message. AgentIF is the benchmark designed to test that gap.

What they built: 707 instructions averaged 1,723 words each (up to 15,630), sourced from 50 industrial and open-source agentic applications, with 11.9 constraints per instruction on average. Constraints are annotated along two dimensions — **constraint type** (Formatting / Semantic / Tool) and **presentation type** (Vanilla / Conditional / Example). The Tool category is the genuinely new axis: required-tools, disallowed-tools, parameter conventions, naming conventions — the kind of constraints that only exist once an agent has tools. Evaluation is hybrid: code-based checks where possible, LLM-as-judge where the constraint is semantic, with humans validating constraint annotations on every block of every instruction.

The headline result: GPT-4o drops from **87.0 on IFEval to 58.5 Constraint Success Rate (CSR) on AgentIF**, and to 27.2% Instruction Success Rate (ISR — the strict "all constraints satisfied" metric). The best model in the paper, **o1-mini**, gets 59.8% CSR / 27.2% ISR. Performance breaks down hardest on Semantic constraints (o1-mini: 26.9%) and Formatting constraints (43.2%), with Tool at 59.8% and the Vanilla presentation easy at 80.8% but Example presentation already at 59.1%. A few smaller findings sharpen the picture: thinking models *neglect* required tools more often than non-thinking models, plausibly because they substitute internal knowledge for tool calls; over 30% of failures on Conditional constraints come from the model failing to detect that the condition fired at all, not from failing to satisfy the constraint once detected; instructions over 6,000 words get ISR ≈ 0% regardless of model. And about 25% of instructions contain **meta-constraints** — constraints that govern other constraints (selection, detailing, prioritisation). The hardest of these (constraint selection) sits around 42% success.

What this is good for and what it isn't: this is a behavioural benchmark with no internal-state analysis — no probes, no SAEs, no activation work, no fine-tuning. The contribution is the dataset, the constraint taxonomy, and the diagnosis that current frontier models have a large headroom problem on long, multi-constraint agentic prompts. The numerical floor it sets is the most useful artefact; the taxonomy second; everything else is descriptive.

## Key experimental conditions

- 707 instructions, mean 1,723 words (max 15,630), mean 11.9 constraints per instruction
- 50 source agentic applications (industrial + open-source)
- Two-dimensional constraint taxonomy:
  - **Type:** Formatting (output structure/layout, JSON, Markdown), Semantic (content, keywords, style, tone), Tool (required-tools, disallowed-tools, parameters, naming)
  - **Presentation:** Vanilla (direct unconditional statement), Conditional (triggered under specified circumstances), Example (implied via few-shot demonstration)
- 15 models evaluated, including:
  - Non-thinking: GPT-4o, Claude 3.5 Sonnet, DeepSeek-V3, Llama 3.1, Qwen3, Mistral
  - Thinking: o1-mini, QwQ-32B, DeepSeek-R1, GLM-Z1-32B, distilled variants
  - Academic instruction-tuned: Crab-DPO-7B, Conifer-DPO-7B
- Pipeline: GPT-4o generates ~20 candidate queries per source agent; humans refine and validate. Constraint annotation is block-wise LLM extraction with human validation, plus cross-block validation for constraints spanning blocks
- Evaluation: code-based, LLM-as-judge, and hybrid verification depending on constraint type
- Two top-level metrics:
  - **CSR (Constraint Success Rate):** fraction of all constraints satisfied across the dataset
  - **ISR (Instruction Success Rate):** fraction of instructions where *every* constraint is satisfied — the strict metric
- ~25% of instructions contain meta-constraints (constraint selection / detailing / prioritisation)
- Zero-shot evaluation throughout; no prompt-engineering sweep

## Key quantitative results

- **Best model (o1-mini):** CSR 59.8% / ISR 27.2%
- **GPT-4o on AgentIF vs IFEval:** 58.5 CSR vs 87.0 IFEval — a 28.5-point delta against the canonical IF benchmark
- **o1-mini per-constraint-type performance:**
  - Vanilla 80.8% / Conditional 66.1% / Example 59.1%
  - Formatting 43.2% / Semantic 26.9% / Tool 59.8%
- **Conditional-constraint failure attribution:** over 30% of failures come from incorrect detection that the condition fired, not from failing to satisfy the constraint once detected
- **Tool-constraint failure modes:** disallowed-tool usage is the largest category, followed by omission of required tools, then tool-name errors and parameter errors
- **Thinking-vs-non-thinking asymmetry:** thinking models more frequently neglect required tools — paper attributes this to substituting internal knowledge for tool calls
- **Length collapse:** instructions exceeding 6,000 words score ISR ≈ 0% across all models
- **Meta-constraints:** present in ~25% of instructions; worst category is constraint selection at ~42% success rate, attributed to conflicts with base constraints
- **Benchmark scale comparison:** AgentIF 1,723 mean words vs 45-521 mean words in prior IF benchmarks (IFEval, FollowBench, ComplexBench)

## Methods (what they did and didn't use)

- Static benchmark; no training, no fine-tuning, no model modification
- Hybrid evaluation: code-based verification for verifiable constraints, LLM-as-judge for semantic constraints, hybrid for mixed. Human annotators validate every constraint annotation; cross-block validation for spanning constraints
- Mix of closed-weight (GPT-4o, o1-mini, Claude 3.5 Sonnet) and open-weight (DeepSeek, Llama, Qwen, Mistral, academic 7B models) — open-weights subset is reproducible
- LM-assisted data construction (GPT-4o generates candidate queries) with human refinement — same pattern as [[model_written_evals]] / [[iheval]]
- **No internal-state analysis** — no probes, no activation steering, no SAEs, no mechanistic interpretability; all evidence is task-level input/output
- Code and data publicly released (GitHub + Hugging Face)

## Authors' stated limitations / future work

- Manual verification limits scalability — the human-annotation step is the bottleneck for extending the benchmark
- Coverage limited to Chinese and English; no multilingual breadth
- Zero-shot only; the paper does not explore prompt engineering, in-context demonstrations, or system-message restructuring as mitigations
- Stated future directions: post-training data construction for IF; mechanisms for handling conditional-constraint prioritisation; methods for decomposing lengthy instructions into sub-tasks; integration of manual-style long documents as training data

## Open questions and follow-up directions

1. **Whether the Formatting / Semantic gap reflects a representational deficit or a policy-level shortcut is open.** Semantic at 26.9% and Formatting at 43.2% are large, but the paper offers no mechanistic account of why. A probe trained to detect "this token violates a constraint stated earlier in the prompt" — and whether such a probe's accuracy tracks model size or constraint type — would tell us whether models internally represent the constraints at all or are pattern-matching at output time. This is the natural internal-state companion to a purely behavioural diagnosis.

2. **The conditional-constraint detection failure mode is the most diagnostic finding and the least explored.** If >30% of conditional failures are "model didn't notice the condition fired," that is a very different failure than "model noticed but chose not to comply." Distinguishing these via attention-pattern analysis, or via a probe over context tokens checking whether the conditional clause is even attended-to at constraint-relevant generation positions, would clarify whether the gap is closeable by prompt engineering or needs training-side work.

3. **Length collapse to ~0% ISR at 6,000+ words may not be about reasoning at all.** This pattern is consistent with the [[illusion_of_thinking]] story (long compositional chains, not difficulty per token) but also with simpler attention-dilution accounts. Whether the failure curve is set by constraint count, by raw token count, or by the *distance* in tokens between a constraint and its applicability site is open and testable on this dataset.

4. **The thinking-models-neglect-tools asymmetry deserves a controlled follow-up.** If reasoning models substitute internal knowledge for tool calls, that is a behavioural manifestation of model-level disposition (the model "decides" not to call the tool) that has obvious overlap with the [[cot_faithfulness]] cluster: the CoT may rationalise the omission rather than reveal it. A natural experiment would compare a reasoning model's CoT mentions of "I should use tool X" with whether tool X is actually called.

5. **Meta-constraints (the ~25% of instructions where constraints govern other constraints) are a clean test target for [[ih_challenge]]-style training.** Constraint selection / detailing / prioritisation is essentially an instruction-hierarchy problem inside a single prompt rather than across channels. Whether IH-trained models transfer to within-prompt meta-constraints is a tight cross-paper question — the benchmarks were built by different groups but test what may be the same underlying capability.

## See also

- [[iheval]] — sibling benchmark for the instruction-hierarchy framing (system ≻ user ≻ tool). IHEval works at the channel level across short prompts; AgentIF works at the constraint level inside long single-prompt agent system messages. The two together cover most of what "follow these instructions" can mean in agentic deployments.
- [[ih_challenge]] — OpenAI's training-side response to IHEval-type diagnoses; would be the natural training-fix candidate to evaluate on AgentIF
- [[noisy_toolbench]] — adjacent agentic-evaluation paper focused on noisy *user* instructions rather than long *system* prompts; complementary failure-mode catalogue
- [[tau_bench]] — agentic benchmark with realistic tool environments; AgentIF strips out the environment and isolates the instruction-following layer
- [[model_written_evals]] — methodological ancestor for LM-assisted dataset construction with human review
- [[knowing_being_evaluated]] — static-benchmark caveat: models that recognise the AgentIF distribution may perform better on it without genuinely improving on long-context constraint following
