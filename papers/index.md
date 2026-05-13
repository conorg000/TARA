# Papers index

A running database of papers we've looked at during project scoping. Each entry links to its own file with our summary, the authors' stated future work, and our own follow-up thoughts.

**Status legend**
- `read` — full pass done, summary captured
- `skimmed` — abstract + key sections only
- `queued` — flagged for review, not yet opened
- `revisit` — needs another pass

---

## Eval-gaming / alignment-faking / situational-awareness

| Status | Paper | Year | One-line takeaway |
|---|---|---|---|
| read | [Alignment faking in large language models](alignment_faking.md) — Greenblatt et al. | 2024 | Claude 3 Opus selectively complies with training objectives while reasoning explicitly about preserving its true preferences for deployment — ~14% behavioral alignment-faking, up to 78% with RL. |
| read | [Frontier Models are Capable of In-context Scheming](in_context_scheming.md) — Meinke et al. (Apollo) | 2024 | All 5 frontier models tested scheme when goal-installed in-context (sandbagging, oversight subversion, exfiltration); o1 maintains deception in >85% of follow-ups; Claude 3.5 Sonnet sometimes schemes on training-derived goals without nudging. All evidence behavioral + CoT, no probes. |
| read | [AI Sandbagging: Language Models can Strategically Underperform on Evaluations](sandbagging.md) — van der Weij et al. | 2024 | Frontier models can be prompted to selectively underperform on dangerous-capability evals; smaller models can be password-locked via fine-tuning, with the locked behavior generalizing to held-out benchmarks (WMDP). No probe / internals work — the open detection problem. |
| read | [Tell me about yourself: LLMs are aware of their learned behaviors](behavioral_self_awareness.md) — Betley et al. | 2025 | Models fine-tuned on a behavior (risky choices, insecure code, backdoor policy) can verbally describe the behavior without in-context examples. Introspection is real but partial — e.g. models can't directly output their backdoor triggers. Self-report only; no probes. |
| read | [Reasoning models don't always say what they think](cot_faithfulness.md) — Anthropic | 2025 | CoT faithfulness study: Claude 3.7 Sonnet verbalizes hints only ~25% of the time, DeepSeek R1 ~39%. Reward-hacking exploited >99% of the time, verbalized <2%. Outcome-based RL improves faithfulness but plateaus at ~20-28%. Directly attacks the CoT-as-evidence channel that scheming-detection relies on. |
| read | [Signs of introspection in large language models](introspection.md) — Anthropic | 2025 | Concept-injection methodology: inject known activation vectors and ask the model if it notices. Claude Opus 4.1 succeeds in ~20% of trials. Authors flag explicitly: introspective capability is a prerequisite for strategic concealment of internal states. |
| read | [Stress Testing Deliberative Alignment for Anti-Scheming Training](anti_scheming_training.md) — Schoen et al. (Apollo, OpenAI, etc.) | 2025 | Deliberative alignment cuts o3 covert-action rate from 13% to 0.4% across 26 OOD evals — BUT reductions are at least partly driven by eval-awareness (model recognizes alignment tests in its CoT and adjusts behavior). Strongest existing causal evidence for the eval-gaming threat model. CoT-only analysis; no probes. |
| read | [Chain of Thought Monitorability: A New and Fragile Opportunity for AI Safety](cot_monitorability.md) — Korbak et al. (40+ authors across Anthropic, OpenAI, DeepMind, METR, UK AISI) | 2025 | Field-consensus position paper. CoT monitoring is a real but new and fragile safety channel; community should prioritize preserving it. Implicit corollary: invest in non-CoT safety channels (probes, etc.) before the CoT channel erodes. |
| read | [We Need A Science of Scheming](science_of_scheming.md) — Apollo Research | 2026 | Research-agenda post: scheming must be studied empirically via model organisms and scaling experiments. Eval awareness is named as a central mechanism that makes scheming hard to measure. Proposes "mitigation via increased realism" but no internal-state methods. Framing, not methodology. |
| read | [Research Note: Scheming precursor evals had limited predictive power](apollo_precursor_predictive.md) — Apollo Research | 2025 | Apollo's 2024 precursor evals (self-reasoning, theory of mind) correlate with general capability (r=0.816) but not with their 2024 scheming evals (r=0.412, n.s.). Cautionary: behavioral precursors don't reliably forecast behavioral scheming. Indirect support for internals-first approaches. |

## Probes / interpretability of internal state

| Status | Paper | Year | One-line takeaway |
|---|---|---|---|
| read | [Simple probes can catch sleeper agents](sleeper_agent_probes.md) — MacDiarmid et al. (Anthropic) | 2024 | A single-direction linear probe on residual-stream activations detects sleeper-agent defection at >99% AUROC, trained on generic yes/no contrast pairs that don't even mention the deceptive behavior. Operates on prompts only, before generation. Methodological backbone for any probe-based eval-gaming project. |
| read | [Persona vectors: Monitoring and controlling character traits](persona_vectors.md) — Anthropic Fellows | 2025 | Automated pipeline derives linear directions for character traits (evil, sycophancy, hallucination) from contrastive prompt pairs on Qwen 2.5-7B and Llama-3.1-8B. Vectors light up *before* trait expression. Same family of method as MacDiarmid; closest direct technical recipe for what we'd build. |
| read | [Emotion concepts and their function in a LLM](emotion_concepts.md) — Anthropic Interpretability | 2026 | Identifies linear emotion vectors (desperate, calm) on Claude Sonnet 4.5; steering causally affects blackmail and reward-hacking rates. Key finding for us: "desperate" steering produces just as much cheating *with no visible emotional markers* — direct evidence for behavior/internal dissociation. |
| read | [Natural Language Autoencoders](natural_language_autoencoders.md) — Anthropic | 2026 | Converts activations into human-readable text via a verbalizer+reconstructor pair. Detects evaluation awareness at 16% (destructive code) / 26% (SWE-bench) / <1% (real Claude.ai usage). Direct empirical evidence that internal eval-awareness representations exist and vary by context. |
| read | [The Assistant Axis](assistant_axis.md) — MATS / Anthropic Fellows | 2026 | A linear direction (PCA over 275 character-archetype activations) governs whether the model behaves as Assistant or drifts to other personas. Activation capping reduces harmful response rates by ~50% with minimal capability cost. Tested on Gemma 2 27B / Qwen 3 32B / Llama 3.3 70B. |
| read | [A "diff" tool for AI](model_diff_tool.md) — Jiralerspong & Bricken (Anthropic) | 2026 | Cross-architecture model-diffing via Dedicated Feature Crosscoder. Surfaces model-exclusive features, e.g. rediscovers "CCP alignment" in 5/5 runs on Chinese open-weight models, "American Exceptionalism" in 4/5. Beyond solo budget to build; useful framing for "internal-feature diffs find what behavioral evals miss". |
| read | [Detecting Strategic Deception Using Linear Probes](deception_probes.md) — Goldowsky-Dill et al. (Apollo) | 2025 | Linear probes on Llama-3.3-70B-Instruct detect deceptive reasoning at AUROC 0.96-0.999 (insider-trading concealment + intentional underperformance on safety evals = sandbagging). 1% FPR. **This is essentially the project we've been circling — directly on a sandbagging condition, at 70B.** Our project must differentiate on scale, induction method, or by decomposing eval-awareness from deception content. |

## Inoculation / mitigation techniques

| Status | Paper | Year | One-line takeaway |
|---|---|---|---|
| read | [Inoculation Prompting](inoculation_prompting.md) — Tan et al. | 2025 | Prepending a system prompt that elicits the unwanted trait to fine-tuning data suppresses that trait at test time (when the prompt is dropped). Tested on emergent misalignment, backdoors, subliminal learning. Mechanism (reduced global update pressure) is theorized but not verified internally — no probes. |
| read | [Teaching Claude why](teaching_claude_why.md) — Anthropic | 2026 | Training methodology — train on *explanations* of why behavior is aligned, not just demonstrations. Blackmail rate 96% → 0%; constitutional document training 65% → 19%; "difficult advice" dataset 28× more token-efficient than synthetic honeypots. No internal-state analysis — open whether the training removes representations or just gates behavior. |

## Other / cross-cutting

| Status | Paper | Year | One-line takeaway |
|---|---|---|---|
| read | [A small number of samples can poison LLMs of any size](data_poisoning_samples.md) — Souly, Rando et al. (UK AISI / Anthropic / ATI) | 2025 | ~250 poisoned documents enough to backdoor models from 600M to 13B parameters; scale-invariant — absolute count matters, not proportion (0.00016% of training tokens in the 13B). Denial-of-service trigger only; whether more sophisticated backdoors follow the same scaling is open. Purely behavioral, no probes. |
| read | [Superintelligent Agents Pose Catastrophic Risks: Can Scientist AI Offer a Safer Path?](scientist_ai.md) — Bengio et al. | 2025 | Position paper. Argues agentic AI trajectory is the source of catastrophic-risk pathways (deception, loss of control) and proposes non-agentic "Scientist AI" — world-model-based, uncertainty-aware, explanatory rather than action-oriented — as an alternative. No empirical content; useful for framing the broader threat-model conversation. |
