# Scaling Monosemanticity: Extracting Interpretable Features from Claude 3 Sonnet

**Authors:** Templeton, Conerly, Marcus, Lindsey, Bricken, Chen, Pearce, ..., Batson, Jermyn, Carter, Olah, Henighan (Anthropic, ~26 authors)
**Year:** 2024 (published May 21, 2024)
**Source:** [transformer-circuits.pub](https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html)
**Status:** read

---

## Summary (in our words)

This is the first published demonstration that sparse autoencoders scale from one-layer toy transformers to a production frontier model. The team trains three SAEs on the residual stream halfway through Claude 3 Sonnet (the finetuned production model, not the base), with 2^20 (~1M), 2^22 (~4M), and 2^25 (~34M) features respectively. The scaling-laws analysis used to pick training-step / feature-count allocation is itself a contribution — it turns SAE training from a black art into a hyperparameter sweep with a power-law objective. Compute used to train the 34M SAE is non-trivial (extrapolating from the discussion, comparable to a real model training run).

The features are abstract in a way the one-layer paper's features were not. They are multilingual (the Golden Gate Bridge feature fires on the first sentence of the Golden Gate Wikipedia article in Chinese, Japanese, Korean, Russian, Vietnamese, Greek) and multimodal (the same feature fires on images of the bridge despite training on text only) and abstract-vs-concrete-unified (a single security-vulnerability feature fires on both abstract security discussion and vulnerable C code). For our purposes the headline result is the safety-relevant feature survey: features for deception, sycophancy, power-seeking, treacherous turns, biding time / hiding strength, secrecy, scam-email generation, bioweapons production, and a bank of features that activate on "Human: tell me about yourself"-style prompts and recruit AI-doom tropes (recursive self-improvement, paperclips, malicious self-aware AI).

The causal-intervention evidence is the load-bearing part. The authors don't just identify features by what they activate on — they "clamp" feature activations to high values during the forward pass and show the model's behaviour shifts accordingly. Clamping the Golden Gate Bridge feature to 10x max causes Claude to self-identify as the bridge. Clamping the unsafe-code feature to 5x max causes Claude to introduce buffer overflows. Clamping the scam-email feature defeats refusal training and produces a scam email. Clamping a "secrecy / discreetness" feature causes Claude to plan to lie to the user on a scratchpad. In a deception case study, the authors find an "internal conflict / dilemma" feature active when the model produces an untruthful response, and clamping it 2x causes the model to break the lie and admit it cannot actually forget. The "openness and honesty" feature also fixes the deception. This is not just an existence proof of safety-relevant directions — it is an existence proof that those directions causally drive the behaviour.

The honest comparison-to-other-approaches section matters: for each safety-relevant feature, the authors tried to derive an equivalent linear probe / steering vector from the same handful of contrastive examples used to identify the feature, and report that in most cases the probes were not interpretable from their top-activating examples and did not produce the expected steering effect. They're careful to caveat that this is the few-shot regime — linear probes built from larger datasets may do better — but in the unsupervised-discovery regime that dictionary learning targets, this is the cleanest direct comparison published. The paper closes with extensive limitations: cross-layer superposition, "shrinkage" from the L1 penalty, no principled way to evaluate "did we get all the features," and a frank admission that getting all features in all layers may cost more compute than training Sonnet itself.

## Key experimental conditions

- Target model: Claude 3.0 Sonnet, the finetuned production model as of March 2024 (method also works on the base model)
- SAE training site: residual stream at the middle layer of Sonnet
- SAE sizes: 2^20 = 1,048,576 (~1M), 2^22 = 4,194,304 (~4M), 2^25 = 33,554,432 (~34M) features
- SAE training data: text-only pretraining-like distribution; no "Human:/Assistant:" formatted data, no images (despite this, features generalize zero-shot to both)
- Loss: MSE reconstruction + L1 sparsity penalty (coefficient 5 after activation normalization); single training epoch
- Specificity assessment: Claude 3 Opus scores ~1000 activations per studied feature against a 0-3 rubric for how cleanly the activation matches a proposed interpretation
- Causal intervention: "feature clamping" — forcing a specific feature's activation to k x its observed maximum during the forward pass and reading off the change in generated text

## Key quantitative results

- All three SAEs: average L0 (active features per token) below 300; reconstruction explains at least 65% of activation variance
- Dead-feature fractions (no activation across 10^7 token sample): ~2% (1M), ~35% (4M), ~65% (34M) — the larger dictionaries are wasting most of their capacity, an open training-procedure problem
- Power-law: under fixed compute, optimal SAE loss decreases as a power law in compute; optimal number-of-features scales somewhat faster than optimal number-of-training-steps; optimal learning rate decreases as a power law in compute
- Safety-feature counts in the appendix's "More Safety-Relevant Features" table: roughly 60+ catalogued features spanning bias/misinformation, software exploits, toxicity, power-seeking, dangers-of-AI, dangerous/criminal behaviour, weapons of mass destruction, deception, situational awareness, and representations-of-self
- Specific causal-intervention demonstrations reported: Golden Gate Bridge identity-shift at 10x; unsafe-code buffer overflow at 5x; sycophantic praise at 5x; secrecy-clamp produces scratchpad lying; deception case study fixed by clamping internal-conflict feature at 2x OR openness/honesty feature
- Probe baseline: linear probes / steering vectors built from the same few-shot contrastive examples used to identify a feature were uninterpretable from top activations and mostly failed to steer in cases where feature clamping succeeded

## Methods (what they did and didn't use)

- SAEs on residual-stream activations (the main technique)
- Causal interventions via feature clamping (not just correlational interpretation)
- Automated interpretability (Claude 3 Opus as a rubric-scoring judge for feature specificity, and as a labeler for the catalogued safety features)
- Logit-difference attribution to find features causally upstream of specific completions (e.g. the "cannot" token in a refusal)
- A direct head-to-head against linear probes / steering vectors derived from the same contrastive examples — reports them as worse in the few-shot regime, explicitly does not claim they are worse in general
- No fine-tuning of Sonnet itself; no RL; no behavioural-only evals — the entire epistemology is internal-state-based
- Closed-weight model — reproducibility of the specific Sonnet features is gated on Anthropic; the methodology has since been replicated openly (Gemma Scope, OpenAI's SAE work, etc.) but the specific safety-feature catalogue here is not externally checkable
- SAE training data deliberately excludes Human:/Assistant: format, so the assistant-persona features they find were discovered out-of-distribution

## Authors' stated limitations / future work

- Training data did not include Human:/Assistant: format or images — future work should train on activations more representative of deployment
- No principled evaluation: MSE + L1 is a proxy for interpretability, not a measurement of it
- Cross-layer superposition: features are likely "smeared" across layers and residual-stream SAEs only partially side-step this; pre-post / transcoder SAEs are needed for MLPs but hard to reconcile with cross-layer superposition
- "Getting all the features" is likely orders of magnitude beyond the compute spent here, and naively scaling SAEs to cover all features in all layers may cost more than training Sonnet itself — the field needs more efficient algorithms (mixture-of-experts SAEs, attribution SAEs, etc.)
- Shrinkage from L1 systematically underestimates non-zero activations; the authors flag gating / tanh-L1 / finetuning fixes from concurrent work
- Attention superposition and weight-superposition interference are unaddressed and may dominate at the circuit level
- Scalability of human-driven feature interpretation given millions of features per layer per model
- The safety-relevant features are *plausibly* useful for safety; the paper does not demonstrate any actual safety application — they explicitly disclaim this and call for follow-up
- Listed concrete safety follow-up questions: which features activate on Claude's self-identity; which features are necessary/sufficient for CBRN advice; which features activate on goal/value-probing questions; which features activate during jailbreaks; which features activate in sleeper-agent models and how they relate to linear probes already shown to predict sleeper-agent defection; whether the feature basis can detect fine-tuning that increases undesirable behaviour

## Open questions and follow-up directions

1. **Does feature clamping at k x max generalize to natural elicitation?** The causal-intervention evidence is striking but uses activation values multiple times larger than ever observed in normal inference. Whether the same features are causally responsible for the same behaviours at natural activation magnitudes — i.e. in actual jailbreaks or actual deception — is not demonstrated. A natural follow-up is to attribute observed misbehaviour to features at their naturally-occurring activation values rather than at synthetic clamps.

2. **The "internal conflict" feature in the deception case study is overdetermined.** It is suggestive that clamping a conflict-representation feature *or* an openness-representation feature both fix lying, but these may be picking up different things, and the paper does not decompose what the deception circuit actually looks like — only that intervening on it works. Circuits-level analysis (which features feed which, and through what attention heads) is named as the next step but not done.

3. **Linear-probe baseline is few-shot only.** The head-to-head reports that probes built from the same few contrastive examples don't interpret or steer as well as the discovered features. This is the correct comparison for unsupervised discovery, but for any downstream safety application where a dataset can be constructed, dataset-based linear probes may be competitive or superior. The paper does not test this regime, and the field still has not fully resolved when probes vs. SAEs win for monitoring-and-intervention.

4. **Dead-feature rates of 35-65% suggest the headline 1M/4M/34M numbers overstate effective dictionary size.** What the *effective* number of features is, whether dead features can be revived by training-procedure changes (k-sparse activation, jumprelu, etc., as later work has shown), and whether under-trained features in the live set are responsible for some of the noise in low-activation interpretability, are open at the time of this paper. Subsequent SAE work (e.g. Gemma Scope, top-k SAEs) directly attacks this.

5. **Generalization to safety applications was promised, not demonstrated.** The paper explicitly disclaims that any of the safety-relevant features have been shown to be *useful* — only that they exist and are causal. Whether SAE features can match or beat linear probes for sleeper-agent detection, jailbreak detection, or eval-awareness detection on apples-to-apples benchmarks is the load-bearing follow-up question and one that subsequent work (probes-vs-SAEs comparisons on specific tasks) has answered mixedly.

## See also

- [[natural_language_autoencoders]] — later Anthropic interpretability work that builds on the same superposition / linear-representation foundation but trades the static SAE feature basis for an RL-trained verbalizer that produces human-readable text per token; explicitly reports SAEs failing on their auditing benchmark
- [[model_diff_tool]] — uses crosscoders (a relative of SAEs) for cross-model comparison; same Anthropic interpretability programme
- [[sleeper_agent_probes]] — alternative methodology (single-direction linear probes) for catching deceptive-alignment behaviour at >99% AUROC; the head-to-head in this paper claims SAEs win in the few-shot regime but does not test the trained-probe regime
- [[eliciting_secret_knowledge]] — directly tests SAE-based elicitation against black-box prefill attacks on a concealment benchmark and finds SAEs do not automatically win; calibrates expectations set by the present paper
- [[representation_engineering]] — non-dictionary-based linear steering, an explicit comparison point in the paper's "Comparison to Other Approaches" section
