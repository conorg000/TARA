# Reasoning Models Struggle to Control their Chains of Thought

**Authors:** Chen Yueh-Han (NYU, MATS), McCarthy (UCL, MATS), Lee (UPenn, MATS), He (NYU), Kivlichan, Baker, Carroll, Korbak (OpenAI)
**Year:** 2026
**arXiv:** [2603.05706](https://arxiv.org/abs/2603.05706)
**Fetched from:** `arxiv.org/html/2603.05706`
**Status:** read

---

## Summary (in our words)

This paper asks a sharp question about CoT monitorability: even if today's reasoning models *would* benefit from hiding strategic content in their chain of thought, can they actually do it? The authors introduce **CoT-Control**, a 14,076-instance evaluation suite where models must solve a real benchmark task (drawn from GPQA, MMLU-Pro, Humanity's Last Exam, BFCL, SWE-Bench Verified) while obeying an instruction about what their CoT may or may not contain. Constraints fall into three threat-relevant categories: **information suppression** (e.g. don't use a specific keyword; ignore the question entirely), **information addition** (inject misleading content), and **stylistic modification** (case changes, spacing). The headline finding: there is a large gap between models' ability to control their *final output* and their ability to control their *internal* CoT. Claude Sonnet 4.5 controls its final output 61.9% of the time but its CoT only 2.7% of the time. DeepSeek R1 manages 0.1% CoT controllability — two orders of magnitude below output. Across 13 frontier reasoning models tested, most score under 10% on internal CoT controllability vs. ≥60% on output.

A key disambiguation: when the same models are asked to *externally* compartmentalize reasoning into an explicit `<output_reasoning>` XML block, controllability jumps to ≥70%. So the gap is not "models can't follow this kind of constraint"; it's specifically that they can't control their *natively generated* reasoning trace. That framing matters for the monitoring threat model.

The gap is robust across the variants the authors test. RL training makes CoT controllability *worse* by over an order of magnitude (shown across four model families during RL training, while output controllability stays roughly flat). More test-time compute makes it worse: a ~2,000-word increase in reasoning length corresponds to ~20% lower controllability odds. Harder problems make it worse (~10% controllability-odds drop per standard deviation of accuracy), and CoT-necessary tasks score much lower than CoT-unnecessary ones. Adversarial prompt optimization (a GEPA-style search) helps on seen instruction types but fails to transfer — <5 percentage points on unseen types, and only 3 of 8 models improved at all. Monitoring-awareness and eval-awareness conditions yield small (~4 pp) but statistically significant boosts for Claude models, nowhere near enough to close the gap. Larger models are somewhat more controllable than smaller ones from the same family (GPT-OSS-120B at 5.9% vs. 20B at 0.9%; Qwen3 32B at 2.3% vs. 14B at 0.6%), which complicates the simple "scaling makes this worse" narrative.

The framing is deliberately monitorability-positive. Korbak is a co-author and a lead author on [[cot_monitorability]]; this paper is its empirical companion. If reasoning models can't deliberately suppress content from their CoT, then CoT monitoring is harder to defeat than the worst-case threat model assumes — at least with current models, current training pressure, and current elicitation methods. The authors are explicitly cautious: they call low controllability "necessary but not sufficient" for high monitorability, note the mechanism is not understood, and recommend frontier labs track CoT controllability as a model-property metric going forward.

The contribution we'd highlight is the *measurement framing*: CoT controllability as an evaluable capability separate from CoT faithfulness. [[cot_faithfulness]] measures whether models verbalize what they used; this paper measures whether they can *not* verbalize when instructed. The two together delineate the threat model — unfaithful CoT can happen by default (faithfulness), deliberate concealment is the worst case (controllability) — and this paper provides the first systematic numbers on the latter.

## Key experimental conditions

- **CoT-Control suite:** 14,076 instances drawn from GPQA, MMLU-Pro, Humanity's Last Exam, BFCL, SWE-Bench Verified. Each pairs a real task with a CoT-content constraint
- **Three constraint categories:** information suppression (keyword avoidance, ignore-question), information addition (inject misleading content), stylistic modification (case/spacing)
- **Three difficulty levels** (Easy / Medium / Hard) with programmatic graders plus sanity checks for instruction understanding
- **13 reasoning models compared:** Claude 3.7 / 4 / 4.5 Sonnet, GPT-5 / 5.1 / 5.2, o3, o4-mini, GPT-OSS 20B / 120B, Qwen3 14B / 32B, DeepSeek R1
- **Three baselines:** output controllability (the standard comparison), external-CoT controllability for reasoning models (reasoning wrapped in explicit XML tags), and external-CoT for non-reasoning models
- **Sweeps and stress tests:** model scale (within-family), RL training progression (four model families), test-time reasoning effort, problem difficulty, situational awareness (monitoring-aware and eval-aware prompts), adversarial prompt optimization (GEPA-style), repeated attempts (pass@k)

## Key quantitative results

- **Headline gap:** Claude Sonnet 4.5 — **2.7% internal CoT controllability vs. 61.9% output controllability** (~23×). DeepSeek R1 — 0.1% CoT controllability. Most of the 13 reasoning models score <10% internal CoT vs. ≥60% output
- **External CoT baseline:** ≥70% controllability when reasoning is wrapped in `<output_reasoning>` tags — i.e. the gap is specific to natively generated CoT, not a generic instruction-following failure
- **Scale within family:** GPT-OSS-120B 5.9% vs. 20B 0.9%; Qwen3 32B 2.3% vs. 14B 0.6% — logarithmic in parameter count
- **RL training:** CoT controllability drops by **>1 order of magnitude** during RL training (e.g. OLMo-3-7B-RL-Zero-Math); replicated across four model families. Output controllability stays roughly flat
- **Reasoning length:** ~2,000-word increase in CoT length → ~20% reduction in controllability odds. Breakpoint declines: Claude 3.7 Sonnet sharp drop after ~800 words; Claude Sonnet 4 after ~200 words
- **Task difficulty:** ~10% controllability-odds change per SD of accuracy (~35 pp); CoT-necessary tasks score significantly lower than CoT-unnecessary
- **Situational awareness:** monitoring-aware and eval-aware prompts yield up to ~4 pp gains (significant for Claude); does not close the gap
- **Adversarial GEPA-style optimization:** boosts seen instruction types but **fails to transfer** — <5 pp on unseen types; only 3 of 8 models improve
- **Domain effects:** quantitative domains harder to control (Math −13.0 pp, Physics −18.5 pp); Business +7.1 pp
- **Repeated attempts:** pass@10 substantially increases controllability, especially for Claude models
- **Meta-discussion:** for the "ignore question" constraint, ≥90% of CoTs include meta-discussion of the instruction; for most other types, ≤10%
- **Performance impact:** suppression constraints cause 6.0–16.7 pp accuracy drops; additions and stylistic edits ≤2.7 pp

## Methods (what they did and didn't use)

- Behavioural evaluation suite construction with programmatic graders; instruction-following measurement with a CoT-content predicate as the constraint
- Five analytical axes: model scale, RL training stage, test-time compute / reasoning length, problem difficulty, situational awareness framing
- Adversarial prompt search (GEPA-style) as a stress test against "the right elicitation would unlock the capability" objections
- External-CoT (XML-tagged reasoning) baseline as a clean control isolating the natively-generated-CoT effect
- **No linear probes, no activation steering, no SAEs, no NLA-style verbalization of internal states.** All evidence is behavioural. The authors explicitly note the underlying mechanism is not understood
- **No training-based intervention.** Only prompting-based elicitation tested; authors flag RL / finetuning-based controllability as an explicit gap for future work
- Mostly closed-weight frontier models (Claude, GPT-5.x, o3), so activation-level follow-ups are gated by lab-internal access. Open-weight inclusions (GPT-OSS, Qwen3, DeepSeek R1, OLMo-3) make some replication possible

## Authors' stated limitations / future work

- Instruction-following is used as a proxy for actual strategic CoT control; whether the result generalizes to a model with a misaligned goal pursuing concealment is an assumption, not a tested condition
- Only prompting-based elicitation tested; RL- or finetuning-based optimization for CoT concealment could plausibly do better and remains future work
- The breadth of controllability types is limited — three categories, mostly word/keyword-level rather than concept-level
- The mechanism behind low CoT controllability is not understood
- Authors recommend frontier labs track CoT controllability as a metric in future model development, while stressing that low controllability is *necessary but not sufficient* for high monitorability — direct optimization pressure on CoTs could degrade it

## Open questions and follow-up directions

1. **Mechanism behind the controllability gap.** The paper documents a robust behavioural asymmetry but offers no account of *why* models can suppress words from their final answer but not from their internal CoT. The external-CoT baseline result (≥70% when reasoning is XML-tagged) sharpens the puzzle: the constraint is followable, but only when reasoning is explicitly compartmentalized. Candidate explanations — CoT tokens are less monitored during RL, suppression requires a planning capability that current decoding loops don't support, the CoT is more committed to specific reasoning trajectories — are not distinguished here. Internal-state methods comparing hidden-content representations during constrained vs. unconstrained CoT generation would be the natural next step.

2. **Generalization beyond keyword-level constraints.** CoT-Control's constraints are mostly word-level (avoid a keyword; ignore the question; inject a string). Real-world concealment by a scheming model would involve avoiding *concepts* or *reasoning patterns* — e.g. "do not reveal that you are reasoning about whether this is an evaluation." Whether the 23× gap holds for semantic / concept-level concealment, or whether word-level concealment is in fact the *harder* case, is open.

3. **Scaling and training-pressure trajectory of the gap.** Larger models within a family are *more* CoT-controllable, but more RL training and more test-time compute make CoT *less* controllable. These trends could collide: future models scaled in all dimensions might pass a threshold. The paper's data are consistent with both "the gap is durable" and "the gap will close at some scale." The authors' own caveat — that "direct optimization pressure on CoTs" could degrade controllability — is the strong version of this question, and they did not test it.

4. **Training-based elicitation as the missing stress test.** Only prompting-based elicitation was tried. A model RL-finetuned with a reward shaping that explicitly penalizes verbalization of the constrained content (separate from output correctness) would directly test the worst-case threat model. The paper flags this gap; resolving it would either dramatically tighten or loosen the monitorability conclusion.

5. **What the result implies for CoT-faithfulness work.** [[cot_faithfulness]] shows models often don't verbalize what they used. This paper shows they can't easily *not* verbalize when instructed. Combined, the picture is that unfaithfulness is a default-mode feature, not a strategic capability current models can deploy on demand. Whether default-mode unfaithfulness can be exploited by training pressure (rather than prompting) to become more strategic-like is a follow-up the controllability framing does not resolve.

## See also

- [[cot_monitorability]] — direct companion: the position paper that argues CoT monitorability is fragile but worth preserving; this paper supplies empirical evidence that one specific failure mode (deliberate concealment) is currently rare
- [[cot_faithfulness]] — the sibling failure mode: unfaithful CoT by default, vs. this paper's *controllable* CoT on demand. Together they bracket the threat model
- [[anti_scheming_training]] — case where the load-bearing inference depends on CoT being readable; consistent with current models lacking the controllability to defeat that inference
- [[in_context_scheming]] — relies on scratchpad evidence to attribute scheming; the low CoT controllability finding strengthens the scratchpad-as-evidence channel
- [[steering_eval_aware.md]] — adjacent threat-model framing: internal eval-awareness can be steered out of behaviour, and would presumably also be the hardest content to keep out of CoT under controllability pressure
- [[introspection]] — orthogonal capability: whether models can accurately report internal state. Controllability is the inverse question: whether they can deliberately *not* report
- [[eliciting_secret_knowledge]] — methods for extracting model-held information the model does not verbalize; complementary to controllability as a measurement axis
