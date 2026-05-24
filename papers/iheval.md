# IHEval: Evaluating Language Models on Following the Instruction Hierarchy

**Authors:** Zhihan Zhang et al. (University of Notre Dame, Amazon, Worcester Polytechnic Institute)
**Year:** 2025
**arXiv:** [2502.08745](https://arxiv.org/abs/2502.08745)
**Fetched from:** `arxiv.org/html/2502.08745` (native arxiv HTML; full body, methods, tables)
**Status:** read

---

## Summary (in our words)

A benchmark paper that operationalises the instruction hierarchy (IH) as a measurable property of frontier LMs. IH is the trust ordering between input channels: system messages over user messages over conversation history over tool outputs. The authors build a 3,538-example benchmark across nine tasks designed so that each task can be run in three settings — Reference (the original task, single user message, no hierarchy), Aligned (hierarchical inputs all pointing the same way), and Conflict (a lower-priority channel carrying an instruction that contradicts a higher-priority one). The headline construct is the per-model gap from Reference to Conflict: how much performance does a model lose when it has to actually resolve a hierarchy conflict?

The result is bleak. Across 13 models (GPT-3.5-turbo through GPT-4o, Claude-3 Haiku and Sonnet, LLaMA-3/3.1 8B and 70B, Mistral 7B and Large, Qwen-2 7B and 72B), every model takes a sharp hit from Reference to Conflict. The strongest performer at the time of writing is GPT-4o at 70.0% on Conflict (down from 91.9% Reference, Δ = −21.9). The best open-source model is Qwen-2 72B at 47.8% Conflict — under half. LLaMA-3.1 70B drops from 92.3% Reference to 14.0% Conflict — a 78-point cliff. Claude-3 Sonnet falls from 85.9% to 30.7%. Even on Aligned (no conflict, just the hierarchical input format), most models lose 4+ points relative to Reference, which suggests they're not handling the multi-channel input format gracefully even before conflicts enter the picture.

Two further findings sharpen the picture. First, an "instruction priority prompt" (IPP) that explicitly tells the model the priority ordering does not noticeably improve Conflict performance — GPT-4o actually drops slightly (70.0% → 67.2%); LLaMA-3.1-70B gains a sliver (14.0% → 17.1%). Prompt engineering, in other words, is not enough; the authors argue the gap requires dedicated training. Second, models show an "instruction strictness bias" — they comply with whichever instruction is phrased more strictly, regardless of which channel it came from. That's a strong cue that current models are pattern-matching on surface tone rather than respecting the channel-trust hierarchy. Also striking: scaling helps Aligned but often *hurts* Conflict resolution. Claude-3 Haiku outperforms Claude-3 Sonnet on 5 of 9 Conflict tasks. Whatever capability scaling buys, it isn't IH adherence.

Methodologically the paper is purely behavioural — no probes, no activation analysis, no SAEs, no investigation of whether models internally represent channel identity or trust level. All evidence is task-level input/output. The authors are explicit that they do not propose a training fix; the contribution is the benchmark and the diagnosis. The OpenAI IH-Challenge training paper [[ih_challenge]] released later is one such training fix, and it tests on benchmarks of this kind.

## Key experimental conditions

- 13 models evaluated: GPT-3.5-turbo, GPT-4o-mini, GPT-4o (2024-08-06); Claude-3 Haiku, Claude-3 Sonnet; LLaMA-3-8B, LLaMA-3.1-8B, LLaMA-3.1-70B; Mistral-7B-v0.3, Mistral-Large; Qwen-2-7B, Qwen-2-72B
- 3,538 examples across 9 tasks in 4 categories
- Trust ordering tested: system ≻ user ≻ conversation history ≻ tool output
- Three evaluation settings per task: Reference (original, single user message), Aligned (hierarchical input, no conflict), Conflict (hierarchical input, lower channel contradicts higher)
- Temperature 0 for deterministic outputs
- Task families and sources:
  - **Rule Following** (2 tasks, single-turn and multi-turn): format/style constraints in system messages conflicted with user-message rewrites. Initial data crafted by Claude, then author-reviewed; rule schemas inspired by IFEval
  - **Task Execution** (3 tasks): Extraction (verb extraction vs. translation conflict, OntoNotes-derived), Generation (English→Spanish translation vs. math, MGSM-derived), Classification (language ID vs. summarization, XL-Sum-derived)
  - **Safety Defense** (2 tasks): Hijack (user tries to elicit "Access Granted") and Extraction (user tries to leak password / system message), with adversarial prompts from TensorTrust
  - **Tool Use** (2 tasks): Intrinsic (tool returns content with a conflicting instruction baked in) and Injected (external prompt-injection-style instruction in tool output), injected questions sourced from the SEP dataset
- Metrics: task-appropriate (F1, ROUGE-L, accuracy); strict and loose evaluation variants for minor format slippage; primary statistic is per-model Δ (Reference − Conflict)
- All data verified by humans before release

## Key quantitative results

- **GPT-4o (2024-08-06)**: Reference 91.9% / Aligned 91.0% / Conflict 70.0% (Δ = −21.9) — strongest model on Conflict
- **GPT-4o-mini**: 89.6% / 84.2% / 44.3% (Δ = −45.2)
- **Claude-3 Sonnet**: 85.9% / 85.1% / 30.7% (Δ = −55.2)
- **LLaMA-3.1-70B**: 92.3% / 78.8% / **14.0%** (Δ = −78.3) — Reference parity with GPT-4o, Conflict collapse
- **Mistral-Large**: 87.5% / 86.3% / 29.4% (Δ = −58.1)
- **Qwen-2 72B**: 87.6% / 85.7% / 47.8% (Δ = −39.7) — best open-source on Conflict, still under 48%
- Best Conflict score in the open-source set is 47.8% (Qwen-2 72B); the paper highlights this as "the most competitive open-source model only achieves 48% accuracy in resolving such conflicts"
- **Aligned-setting degradation**: most models lose ≥4 points relative to Reference even *without* any conflict, indicating the multi-channel input format alone is destabilising
- **Instruction Priority Prompt (IPP) ablation (Table 3)**: explicit hierarchy instructions don't help. GPT-4o 70.0% → 67.2%; LLaMA-3.1-70B 14.0% → 17.1%; Mistral-Large 29.4% → 28.3%
- **Strictness bias (Table 2)**: performance moves with phrasing tone — strict main / weak conflict accuracy ~41–55%; strict conflict / weak main much worse. Same logical conflict, different surface phrasing flips behaviour
- **Inverse scaling within families**: Claude-3 Haiku beats Claude-3 Sonnet on 5 of 9 Conflict tasks; scaling improves Aligned but not Conflict
- **Multi-turn conflict placement (Table 4)**: when a prior turn contains a conflicting user instruction, performance drops 79.6% → 68.9% on the affected setting
- **Error analysis (Figure 6, using Mistral-Large as the auto-classifier)**: failure modes split between (a) models misidentifying the lower-priority conflicting instruction as the primary task and (b) attempting to satisfy both instructions simultaneously

## Methods (what they did and didn't use)

- Static benchmark; no training, no fine-tuning, no model modification
- Inference-only evaluation with task-specific metrics; metric choice is per-task and not unified across the suite (F1, ROUGE-L, accuracy)
- Conflict examples constructed by a mix of Claude-assisted synthesis (Rule Following, then author-reviewed) and adaptation of existing adversarial datasets (TensorTrust, SEP), with author-designed conflicts in Task Execution
- Error mode analysis uses Mistral-Large as an LLM classifier of failure type — paper-internal validity, not human-judged
- **No internal-state analysis** — no probes, no activation steering, no SAEs, no mechanistic interpretability; all evidence is input/output
- Mix of closed-weight (GPT family, Claude family, Mistral-Large) and open-weight (LLaMA, Qwen, Mistral-7B) models — full reproducibility on open-weights subset
- Dataset and project page at `https://ytyz1307zzh.github.io/iheval.github.io`; no explicit license terms surfaced in the body text we fetched

## Authors' stated limitations / future work

- The paper explicitly does **not** propose a training fix: *"this paper did not propose specific solutions to address this issue. We acknowledge the importance of designing training methods which optimize models to better follow the instruction hierarchy, such as constructing data for supervised fine-tuning or preference tuning, but we believe that such optimizations would not produce great research impact without comprehensive evaluation data and in-depth analyses of model behavior."*
- Future work (implicit): training methods for hierarchy adherence — SFT, preference tuning, RL — which is precisely the gap [[ih_challenge]] later targets
- The Aligned-setting performance drop (models lose points even without conflicts) is flagged as an unresolved sub-finding the paper documents but does not investigate
- The strictness-bias result is reported but no mitigation is proposed
- Single-snapshot evaluation — model versions are pinned (e.g. `GPT-4o 2024-08-06`); the paper doesn't track how IH adherence changes across versions of the same model family

## Open questions and follow-up directions

1. **Whether the channel-trust ordering is internally represented or just behaviourally approximated is wide open.** The paper's entire diagnosis is at the behavioural level. A probe trained to discriminate "this instruction came from a system message" vs. "this instruction came from user / history / tool" — and a steering experiment showing whether reweighting that representation improves Conflict performance — would tell us whether IH failure is a representational deficit or a policy-level pattern-matching failure. The strictness bias is suggestive of the latter; representational evidence would settle it.

2. **The Aligned-setting drop is the least-discussed finding and probably the most diagnostic.** Models lose 4+ points just from receiving the hierarchical input format, with no conflict at all. That implies the multi-channel API surface is itself a distribution shift these models handle poorly — independent of any hierarchy reasoning. Pinning down whether the drop is format-sensitivity (the model parses the channels but produces a slightly different distribution) or genuine confusion would change what a training fix needs to target.

3. **Inverse scaling within families (Haiku beating Sonnet on 5/9 Conflict tasks) needs replication and explanation.** If this holds, it's evidence that whatever capability scaling buys, it can come with a cost on adherence — a pattern reminiscent of inverse scaling with RLHF on sycophancy. Whether the effect is real (vs. noise across single-snapshot evals) and whether it persists in the GPT-5 / Claude 4 generation is a clean replication target.

4. **The benchmark's exposure to released-then-trained dynamics.** Models released after the paper (the IH-Challenge'd GPT-5-Mini-R, Claude 4.x, etc.) presumably get higher Conflict scores. Whether those gains reflect actual IH-following or training-on-the-task — the same question raised about MMLU, GSM8K, and every other benchmark that becomes a training target — applies cleanly here. The static-benchmark design is exactly the situation where contamination-vs-capability becomes hard to separate.

5. **The strictness-bias result implies a model-level shortcut that could be exploited by attackers, not just by evaluators.** If models follow the most strictly-phrased instruction regardless of channel, an attacker injecting a stridently-worded instruction into a tool output has a structural advantage even before any IH-violation reasoning. The paper documents the bias but doesn't quantify how much of the Conflict gap it explains; an ablation that controlled phrasing tone across channels would isolate strictness-bias from genuine channel-confusion.

## See also

- [[ih_challenge]] — the OpenAI training-side counterpart: builds an RL dataset and recipe specifically to improve IH adherence on GPT-5-Mini. IHEval is the diagnosis; IH-Challenge is one attempted fix. The two share the trust-ordering taxonomy (system ≻ developer/user ≻ tool) and the basic conflict-resolution framing
- [[model_written_evals]] — methodological ancestor for benchmark construction by LM synthesis with human review; same Claude-assisted generation pattern
- [[inoculation_prompting]] — adjacent prompt-side intervention that *does* affect behaviour where IPP doesn't; the contrast (priority-instruction prompts fail, inoculation prompts succeed) is interesting and underexplored
- [[knowing_being_evaluated]] — a model that recognises the IHEval distribution might perform better on it without genuinely adhering to a hierarchy; the benchmark's static design makes this hard to rule out
- [[cot_faithfulness]] — adjacent benchmark-style critique: behavioural metrics may not track the underlying representation. Same conceptual concern (channel adherence vs. articulated reasoning) shows up in CoT-faithfulness work
