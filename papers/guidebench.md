# GuideBench: Benchmarking Domain-Oriented Guideline Following for LLM Agents

**Authors:** Lingxiao Diao, Xinyue Xu, Wanxuan Sun, Cheng Yang, Zhuosheng Zhang (Shanghai Jiao Tong University / ByteDance)
**Year:** 2025
**Venue:** ACL 2025 Main Conference
**arXiv:** [2505.11368](https://arxiv.org/abs/2505.11368)
**Fetched from:** `arxiv.org/html/2505.11368` (native arXiv HTML; full body — Methodology, Experiments, Analysis, Appendices A–E)
**Status:** read

---

## Summary (in our words)

A benchmark paper aimed at a specific failure mode of LLM agents in deployment: the model has general world knowledge but the operator hands it domain-specific rules ("only refund within 30 days", "always cite source X for medical claims") that may conflict with that prior. The authors construct a 1,272-task benchmark across seven domains — audit algorithm, price matching, text relevance, math, agent chatting, summarization, hallucination detection — where each instance pairs a piece of context with a small bundle of explicit guideline rules and asks the model to produce an answer that obeys the rules. Each task is presented in one of two formats (multiple-choice or short-answer QA) and is graded against human-verified ground truth. The construction pipeline is GPT-assisted (seed extraction → automated rule generation, 537 rules in total → assembly via random / diversity / semantic-based selection → multi-response generation → LLM-judge filter → expert human review), with the Chinese-origin instruction base flagged as a stated limitation.

The headline result is that frontier models cluster between 80–87% overall accuracy, with DeepSeek-R1 leading at 87.26% and GPT-4o at 86.48%, but the per-domain breakdown is much more uneven than the aggregate. Math is the choke point: most models sit below 60% in that bucket, and GPT-4o collapses to 13.46% on the math split despite being among the strongest overall. DeepSeek-R1 reaches 65.38% on math; that's the best result in the suite. At the other end, several domains have multiple models above 90% (audit algorithm, price matching, agent chatting, hallucination detection) — meaning the headline number is mostly a hallucination-detection / agent-chat number averaged with a math floor. The benchmark is designed to test whether models prioritise *rules* over their *priors*, and the per-domain skew is plausibly evidence that "rule-following" is easy when the rules align with priors and hard when they actively contradict computation the model would do unaided.

The most diagnostic experiments are the ablations. Removing the guidelines from the GPT-4o prompt (keeping only instruction + context) drops accuracy 5.58 points (86.48% → 80.90%); that's the size of the "rule-following" effect, and it's smaller than the math gap. Chain-of-thought helps a lot on math (DeepSeek-R1 65.38% with CoT vs 42.31% without) but barely moves summarization (<3% difference). Two reasoning-paradigm interventions on the math split are striking in opposite directions: forcing Program of Thoughts collapses performance by 35.11 points, while *converting the guideline rules into math expressions* lifts performance by 21.16 points. The second result is the closest thing the paper offers to a mechanism claim: when the rule is restated in a form the model's math machinery can consume, adherence improves; when it stays in natural language, the math machinery and the rule-following machinery don't compose.

Methodologically the paper is entirely behavioural — task in, answer out, accuracy against ground truth. No probes, no activation steering, no SAEs, no mechanistic interpretation of *why* models drop rules. The error analysis on math is the only attempt to decompose failures and is itself behavioural: 87% of math errors classified as "logical mistakes", 13% as "commonsense mistakes" (where the model leans on prior knowledge instead of the supplied rule). That category is the one the benchmark was built for; it's the smaller share of errors on the hardest domain.

## Key experimental conditions

- **18 models evaluated**, split closed/open:
  - API-based: o1, GPT-4o, DeepSeek-R1, DeepSeek-V3, Gemini-2.5-pro-exp
  - Open-weights: Llama-3 / Llama-3.3, Qwen-2.5, Mistral-7B, Yi-1.5, Vicuna-7B, Gemma-3, QwQ-32B
- **1,272 tasks across 7 domains**: audit algorithm, price matching, text relevance, math, agent chatting, summarization, hallucination detection
- **Two task formats**: multiple-choice and open question-answering
- **Per-task structure**: Instruction + Guidelines + Context + (optional) Multiple Options
- **537 distinct guideline rules** generated across the domains
- **Construction pipeline**:
  1. Seed instruction extraction from real-world use cases
  2. Automatic guideline rule generation
  3. Guideline assembly via random / diversity / semantic-based selection strategies
  4. Multi-response generation using LLMs
  5. Quality control: LLM filtering → expert human review
- **Prompt setting**: zero-shot Chain-of-Thought (analysis then final answer) as the default protocol
- **Judge**: GPT-4o used for response parsing / format standardisation, not for grading correctness — final scoring is against human-annotated ground truth labels

## Key quantitative results

- **Overall accuracy leaderboard**:
  - DeepSeek-R1: **87.26%** (best)
  - GPT-4o: 86.48% overall, but **13.46% on the math split**
  - DeepSeek-V3: high on audit algorithm (97.39%) and price matching / text relevance (both 91.18%)
- **Per-domain bests**:
  - Audit Algorithm: DeepSeek-V3 97.39%
  - Price Matching: DeepSeek-V3 91.18%
  - Text Relevance: DeepSeek-V3 91.18%
  - Math: DeepSeek-R1 65.38% (best in the suite; most other models <60%)
  - Agent Chatting: GPT-4o 100%
  - Summarization: DeepSeek-R1 89.66%
  - Hallucination Detection: multiple models ≥94%
- **Guideline-removal ablation (GPT-4o)**: full prompt 86.48% → no-guideline prompt 80.90% (**Δ = −5.58 pts**) — the "rule-following gain" from the guideline channel
- **CoT impact on math (DeepSeek-R1)**: with CoT 65.38% → without CoT 42.31% (**Δ = +23 pts from CoT**)
- **CoT impact on summarization**: <3 pts — domain-dependent
- **Reasoning-paradigm interventions on math**:
  - Program-of-Thoughts conversion: **−35.11 pts**
  - Rule-to-math-expression conversion: **+21.16 pts**
  - In-context learning (2-shot demo, rule reordering): minimal effect
- **Math error decomposition** (DeepSeek-R1): 87% logical mistakes, 13% commonsense mistakes

## Methods (what they did and didn't use)

- **Static benchmark over 1,272 examples**; inference-only evaluation, no training or fine-tuning of any model
- **Two response formats** (MC + QA) handled with format-specific parsing; grading against human-verified labels
- **LLM-as-grader used only for response parsing**, not for correctness adjudication — final accuracy comes from human-annotated ground truth
- **Construction is LLM-assisted with human review** — same broad pattern as IFEval-style benchmark synthesis; the rule corpus (537 rules) is the load-bearing artefact and is GPT-generated, then expert-reviewed
- **Error analysis is itself an LLM classification step** (logical vs commonsense), so the "87% / 13%" split inherits whatever judge bias the classifier has
- **No internal-state analysis** — no probes, no activation steering, no SAEs, no mechanistic decomposition of which inputs the model actually attends to when it follows or breaks a rule
- **Mix of closed-weight (o1, GPT-4o, DeepSeek API, Gemini) and open-weight (Llama, Qwen, Mistral, Yi, Vicuna, Gemma, QwQ) models** — reproducibility is partial; the API leaderboard moves as model versions roll forward
- **Instruction base is Chinese-origin** (authors flag this as a limitation); the English evaluation is a translated / adapted construction

## Authors' stated limitations / future work

- **Linguistic coverage**: dataset primarily built from Chinese instructions; the authors flag potential linguistic and cultural blind spots and plan a multilingual extension
- **Dynamic reasoning depth**: authors propose modules that adapt thinking depth to task complexity, motivated by the over-thinking / under-thinking pattern they observe (excessive reasoning on simple tasks, insufficient depth on complex ones)
- **RL-based rule adherence**: explicitly named as a future direction — using RL signal to specifically penalise "overlooked rules" rather than relying on prompt-level CoT to surface them
- **Over-thinking vs under-thinking** is left as a documented but unresolved sub-finding, framed as a target for the proposed dynamic-depth modules

## Open questions and follow-up directions

1. **Whether the rule-following gap is representational or attentional is wide open.** The +21.16 pt jump from rewriting guideline rules as math expressions strongly suggests the rule channel and the math reasoning channel don't compose by default. A probe trained to detect "an active rule is in the prompt" vs "no rule" — and a steering experiment that amplifies that representation on the math split — would tell us whether rules are encoded but ignored, or simply not encoded with the right type signature for downstream computation.

2. **The "87% logical / 13% commonsense" error decomposition is the construct the benchmark was built around — and the smaller share.** If the dominant failure mode on the hardest domain is logical execution rather than prior-vs-rule conflict, the benchmark is partly measuring math competence under added load, not rule adherence specifically. A controlled split where rule-priors-aligned vs rule-priors-conflicting cases are matched on logical difficulty would isolate the construct.

3. **Whether the −5.58 pt guideline-removal effect is the right size of the rule-following signal.** GPT-4o loses 5.58 points on overall accuracy when the guidelines are stripped. That's smaller than the cross-domain spread and much smaller than the CoT effect on math. If the benchmark's headline construct is "rule-following", the headline effect size is modest, and most of the variance in the leaderboard is plausibly variance in baseline competence per domain. A within-model decomposition (per domain, per format) of "with rules − without rules" would clarify how much of the leaderboard is really rule-following.

4. **The Chinese-origin instruction base interacts with the math-via-rules result in a non-obvious way.** Rule conversion to math expressions presumably routes around language; the rest of the suite doesn't. Whether the cross-domain gap shrinks when the prompts are presented in the original Chinese, or whether the open-weight models that underperform are penalised by the translation step, is something the multilingual extension would have to settle before "rule-following" can be cleanly compared across models.

5. **Static, GPT-mediated benchmark construction means training contamination is a live concern.** 537 GPT-generated rules and multi-response generation by LLMs leave a substantial GPT-shaped fingerprint on the suite, and the benchmark is in the open. Whether subsequent model generations gain on GuideBench because they follow rules better or because they've seen the distribution is the standard worry. A held-out adversarial split — constructed by humans from scratch, post-release — would let later evaluations distinguish capability from contamination.

## See also

- [[iheval]] — sibling benchmark; trust-ordering between *input channels* (system ≻ user ≻ history ≻ tool) rather than between *priors and rules*. GuideBench's "remove guidelines drops accuracy 5.58 pts" is the within-channel analogue of IHEval's much larger cross-channel cliffs. Both papers are purely behavioural and both decline to propose a training fix.
- [[ih_challenge]] — training-side counterpart for the broader IH problem; same flavour of "explicit rule-following improves but we don't know whether the model learned the concept or the eval distribution" question that GuideBench inherits
- [[tau_bench]] — sibling agentic benchmark, also rule-/policy-following in domain-specific contexts; GuideBench is the static-task analogue without the multi-turn user simulator
- [[noisy_toolbench]] — adjacent agent-eval design where the model has to recognise an unclear instruction; GuideBench assumes the instruction is clear and the rule is given, isolating the adherence question
- [[hierarchical_safety_principles]] — another rule-adherence eval, but on safety-principle conflicts rather than domain rules; same behavioural-only methodology
- [[model_written_evals]] — methodological ancestor for benchmark construction via LM synthesis with human review; same Claude/GPT-assisted generation pattern at smaller scale
