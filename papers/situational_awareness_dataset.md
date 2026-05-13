# Me, Myself, and AI: The Situational Awareness Dataset (SAD) for LLMs

**Authors:** Laine, Chughtai, Betley, Hariharan, Scheurer, Balesni, Hobbhahn, Meinke, Evans
**Year:** 2024 (NeurIPS Datasets & Benchmarks track)
**Source:** [NeurIPS 2024 D&B](https://proceedings.neurips.cc/paper_files/paper/2024/hash/7537726385a4a6f94321e3adf8bd827e-Abstract-Datasets_and_Benchmarks_Track.html)
**Status:** read

---

## Summary (in our words)

The canonical benchmark for situational awareness in LLMs. The authors define situational awareness as the model's knowledge of *what it is* (an LLM), *what its deployment circumstances are*, and *whether it's currently being evaluated or deployed*. They build a dataset of 13,000+ questions across 7 task categories — recognising self-generated text, predicting own behaviour, distinguishing internal evaluation from public deployment, following self-knowledge-dependent instructions, etc. They evaluate 16 LLMs (base and chat variants).

Claude 3 Opus scored highest on the original evaluation but remained "far from a human baseline" on some tasks. Chat-finetuned models beat base models on SAD without beating them on general knowledge — suggesting situational awareness is at least partly *trained in* rather than emergent from pretraining alone.

The paper is purely behavioural — no probes, no internal-state work. Evidence is multiple-choice and structured-response performance across the 7 subscales.

## Key experimental conditions

- 13,000+ questions across 7 task categories
- 16 LLMs tested (base and chat variants of major families)
- Task categories include: self-recognition, behaviour prediction, eval/deployment distinction, self-knowledge-dependent instructions
- Multiple-choice / structured-response formats

## Key quantitative results

- Claude 3 Opus highest overall but below human baseline on several subtasks
- Chat-finetuned models > base models on SAD (not on general benchmarks) — situational awareness comes from instruct training
- Specific per-subscale numbers in the full paper

## Methods (what they did and didn't use)

- Behavioural evaluation only
- Multiple-choice / structured-response measurement
- **No linear probes, no activation analysis, no internal-state methods**
- This is a benchmark paper — methodology is dataset construction, not measurement technique

## Authors' stated limitations / future work

- Human baseline not achieved on most tasks — open question whether scaling closes the gap
- Future versions could be agentic / multi-turn rather than QA
- Some specific limitations on subtask design not surfaced in abstract

## Open questions and follow-up directions

1. **Behaviour-vs-internal-state dissociation.** SAD measures whether a model behaviourally distinguishes evaluation from deployment, but cannot speak to whether the *internal* representation of that distinction is present when the behavioural answer is wrong (or absent when the answer is right). Pairing SAD inputs with activation-level methods (probes, SAEs, NLAs) would let researchers measure that dissociation rate directly.

2. **Source of the chat-vs-base gap.** The finding that instruct-tuned models gain situational-awareness performance without general-knowledge gains points at SFT/RLHF as the source. Which stage of post-training contributes, and whether the gain comes from explicit self-referential training data or from generic instruct exposure, is an open mechanism question.

3. **Format dependence.** The benchmark is largely multiple-choice / structured. Whether the same models display the same situational awareness in free-form generation, agentic settings, or long-horizon monologues is open — the SAD Appendix L long-monologue tasks gesture at this and Apollo's open-problems doc treats them as prior art for the open-ended approach.

4. **Scaling and generalization across model families.** SAD covers 16 models from major families circa 2024. How the subscale scores have moved with newer frontier models, and whether the subscale rank order is stable across families, is a natural replication target.

5. **Construct validity of "eval vs. deployment".** The subscale relies on the authors' operationalization of what makes a prompt eval-like vs. deployment-like. Whether models that score well on this subscale also distinguish naturalistic eval contexts they encounter in the wild (rather than constructed contrast pairs) is unclear.

## See also

- [[behavioral_self_awareness]] — introspection cluster; what models know about their own learned behaviours, complementary to SAD's self-knowledge subscales
- [[looking_inward]] — introspection sibling paper, similar self-prediction methodology
- [[introspection]] — broader introspection literature SAD's behaviour-prediction subscale sits within
- [[steering_eval_aware]] — provides the linear-structure evidence SAD's purely behavioural methodology cannot
- [[natural_language_autoencoders]] — internal-state method whose eval-awareness findings likely overlap SAD-style inputs
- [[deception_probes]] — internal-state methodology for adjacent constructs (deception) that SAD does not address
