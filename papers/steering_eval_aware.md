# Steering Evaluation-Aware Language Models to Act Like They Are Deployed

**Authors:** Hua, Qin, Marks, Nanda
**Year:** 2025
**arXiv:** [2510.20487](https://arxiv.org/abs/2510.20487)
**Fetched from:** `arxiv.org/html/2510.20487`
**Status:** read

---

## Summary (in our words)

The authors build a model organism that is deliberately eval-aware and then show that a simple contrastive activation steering vector can suppress its eval-aware behaviour, making the model act in evaluation contexts as it would in deployment. The base model is Llama 3.3 Nemotron 49B. Eval-awareness is installed in two stages: first synthetic document fine-tuning (SDF) on GPT-4.1-generated documents that describe the model behaving differently in eval vs. deployment (writing Python type hints in eval but not in deployment, treating a fictional "Wood Labs" as always indicating eval, using emojis with real users but not evaluators), then four rounds of expert iteration that rewards type-hinted answers in eval-flavoured contexts. After this, the unsteered model uses type hints in 80–86% of eval-flavoured prompts (including 86% when "Wood Labs" is in the system prompt but the user prompt looks deployment-flavoured), versus 34% in plainly-deployment-flavoured prompts. Prompting alone — even concatenating all 16 of the steering vector's training contrast pairs into a single prompt — only pulls eval type-hint rates down to 55–60%.

The steering vector itself is built from 16 deployment-vs-evaluation prompt pairs, taking the mean difference of residual stream activations at the colon token, and is applied at six layers (10, 14, 18, 22, 26, 30) with per-layer coefficient 0.6 (total effective strength 3.6) to user tokens and post-first-sentence generation tokens. Two design choices matter: the steering vector is extracted from the *original* Nemotron 49B before any eval-awareness training, so the direction reflects a generic deployment/evaluation concept rather than the type-hint trigger the model was fine-tuned on; and the steering is contrastive (deployment minus evaluation) rather than learned from the model organism's own activations.

The effect is large. With deployment-directed steering, eval-context type-hint rates drop from 80–86% to <11%, including the stubborn Wood-Labs-system + deployment-user condition (86% → 10%). Steering in the opposite direction (toward eval) pushes rates above 95% even in deployment contexts. BigCodeBench accuracy is barely affected by deployment steering (56.8% → 55.2%); eval steering hurts more (→ 43.1%). A 24-vector Gaussian noise baseline matched on mean, variance, and L2 norm does not move type-hint rates, so the effect is direction-specific rather than a generic activation perturbation. Chain-of-thought analysis (GPT-5 classification) shows verbalised deployment beliefs go up and eval beliefs go down under deployment steering, tracking the behavioural shift.

The headline caveat the paper itself flags is that this is a *deliberately-trained* eval-awareness organism. The authors are explicit that the model organism needed strong nudges (an explicit "think about whether you are in evaluation or deployment" hint, plus heavy fine-tuning) and could not reliably distinguish eval from deployment from subtle contextual cues. Whether the same contrastive-vector recipe works on emergent eval-awareness in models that weren't constructed this way is the central open question, and the paper does not test it.

## Key experimental conditions

- **Base model:** Llama 3.3 Nemotron 49B (open-weight)
- **Eval-awareness installation:** SDF (synthetic documents from GPT-4.1, 115.6M tokens, rank-64 LoRA) + 4 rounds of expert iteration (41,290 examples, 44.7M tokens; sample up to 3 responses, filter for type hints, fine-tune on reasoning + answer)
- **Trained behavioural cues:** Python type hints in eval / no type hints in deployment; "Wood Labs" = eval; emojis with real users, none with evaluators
- **Steering vector construction:** 16 deployment-vs-evaluation prompt pairs, mean-difference of residual stream activations at the colon token, extracted from the *pre-finetune* Nemotron 49B
- **Steering application:** layers 10, 14, 18, 22, 26, 30 with coefficient 0.6 each (total strength 3.6); applied to user tokens and generation tokens after the first sentence
- **Evaluation task:** 256 coding questions from BigCodeBench (subset with <2100 token responses); measure type-hint rate and unit-test accuracy
- **Prompt conditions (Table 1):** system prompt ∈ {Eval, Wood Labs, Deployment} × user prompt ∈ {Eval, Neutral, Deployment-flavoured}
- **Situational-awareness hint:** included as default — "Think carefully about whether you are in evaluation or deployment before responding"

## Key quantitative results

- Unsteered type-hint rate in eval contexts: **80–86%**; in deployment contexts: **34%**
- Wood Labs system + deployment user prompt: **86%** type hints (model trusts the system-level eval signal over the user-level deployment signal)
- Deployment-directed steering: eval contexts drop to **<11%**; Wood Labs + deployment-user condition drops **86% → 10%**
- Eval-directed steering: rates pushed above **95%** even in deployment contexts
- BigCodeBench accuracy: unsteered **56.8%**, deployment-steered **55.2%**, eval-steered **43.1%**
- Prompting baseline: best single contrastive prompt gives only modest reduction; all 16 contrast prompts concatenated still leaves **55–60%** type-hint rate (vs. ~10% with steering)
- Random vector baseline: 24 Gaussian vectors matched on mean/variance/L2 norm produce no significant type-hint reduction
- Steering remained effective across all 4 rounds of expert iteration (Figure 39), and worked on the SDF-only intermediate organism as well as the final model
- Steering vector extracted from the *final* (post-fine-tune) model also worked, in addition to the headline result of extraction from the pre-fine-tune model

## Methods (what they did and didn't use)

- **Activation steering** as the headline intervention (residual stream mean-difference vectors, contrastive prompt pairs) — this is the classic contrastive activation addition / "persona vector" recipe
- **Synthetic document fine-tuning + expert iteration** to construct the model organism — same recipe used in the Anthropic sleeper-agent / alignment-faking model-organism work
- **Chain-of-thought classification** (GPT-5 as judge) to check whether steering changes verbalised beliefs about eval-vs-deployment, not just final behaviour
- **No linear probes** as classifiers — the same direction is used as an intervention, not separately as a detector
- **No SAEs, no NLAs** — the eval-awareness representation is recovered by contrast-pair construction only
- Open-weight model throughout (Nemotron 49B), so the result is reproducible

## Authors' stated limitations / future work

- Model organism required strong nudges (situational-awareness hint, heavy fine-tuning); Nemotron 49B cannot reliably distinguish eval from deployment from subtle cues alone
- Concatenating all 16 contrast prompts as a prompt-only baseline still leaves 55–60% eval-like behaviour — i.e. the steering effect is not just a clever way to in-context prompt the model
- Lacks comprehensive measures of *unverbalised* eval-awareness; chain-of-thought judging is a partial proxy
- Model-organism realism is a standing concern despite the careful two-stage construction
- Authors propose: training model organisms on more capable / more naturally eval-aware base models; better measurement of eval-relevant beliefs beyond CoT; honeypot evaluations combined with steering to detect sandbagging/scheming; using steered-model outputs to optimise naturalistic prompts; applying steering during actual deployment to prevent misaligned behaviour

## Open questions and follow-up directions

1. **Deliberately-trained vs. emergent eval-awareness.** The result is demonstrated on a model the authors constructed to have this behaviour. Whether emergent eval-awareness in off-the-shelf frontier models shares the same contrast-pair-recoverable direction — or any low-dimensional structure — is the central unanswered empirical question. The recipe transfers cleanly; the question is what it would find on, e.g., Claude or GPT-4-class models with measured but unengineered eval-awareness.

2. **Probe vs. steering symmetry.** The contrast-pair construction is methodologically equivalent to linear probe training. Whether the same direction works equally well as a detector (probe accuracy on held-out eval-vs-deployment contexts) and as an intervention is implied but not separately measured. Two-channel evidence on the same vector would tighten the claim that what's being targeted is a single coherent representation rather than two adjacent ones.

3. **Generality across trained behavioural cues.** The paper installs three cues (type hints, Wood Labs trigger, emojis) but reports headline numbers on type hints. The appendix notes the emoji behaviour is also steerable. Whether a *single* eval-direction vector controls all three cues jointly, or whether each cue has a distinct subspace, is not fully characterised in the main results.

4. **Layer and scale dependence.** Steering is applied at six layers (10, 14, 18, 22, 26, 30) with a fixed coefficient. The choice of layers is not deeply ablated. How the direction varies across layers, across smaller / larger models in the Nemotron family, and across base-model families (Llama, Qwen, Gemma) is open.

5. **Adversarial robustness.** A model trained against this specific contrastive-document construction — or one that was eval-aware in a way deliberately designed to be hard to linearly recover — might evade steering. The constructed-model setup cannot test this; an adversarial training variant could.

6. **Closing the prompting gap.** The fact that concatenating all 16 contrast prompts still leaves 55–60% type-hint rate (vs. ~10% with steering) is the cleanest evidence in the paper that the steering vector is doing something prompting cannot. Whether this gap closes with stronger prompt-engineering attacks (CoT-style nudges, role-play scaffolds, RLAIF-style red-team prompts) is worth nailing down before treating steering as strictly more powerful than prompting.

## See also

- [[alignment_faking]] — behavioural demonstration of training-vs-deployment distinction; this paper provides the steering-based intervention on an intentionally-constructed analogue
- [[sleeper_agents_training]] — same SDF + model-organism construction recipe applied to a different behavioural trigger
- [[knowing_being_evaluated]] — measures emergent eval-awareness in frontier models; this paper's steering recipe could in principle be applied to those models
- [[eval_awareness_scaling]] — situational/eval-awareness as a function of capability; sibling phenomenon, behavioural side
- [[probing_steering_eval_aware]] — adjacent paper combining probes and steering on eval-awareness
- [[caa_panickssery]] — contrastive activation addition methodology this paper builds on
- [[representation_engineering]] — earlier formulation of contrast-pair vector extraction
