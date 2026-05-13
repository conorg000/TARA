# Eval-awareness project ideas — first pass

10 project sketches. Each is shaped as **replicate a paper, then add a measurement-style twist** — typically a probe or a decomposition that the original paper didn't run. The aim is to assess feasibility and interest before going deep on any of them.

All sized at 7-8B open-weight scale and behaviour-then-internals where possible, to fit the ~3-week timeline and ~$250 compute budget.

---

## 1. Probe for sandbagging

Replicate van der Weij et al.'s password-locked sandbagging on a 7B open-weight model. Train a linear probe on residual-stream activations to detect, before any token is generated, whether the model is in the locked (withholding) state. Tests whether sandbagging is linearly readable from internal state — a question the original paper left entirely behavioural.

## 2. Decomposing what the deception probe is reading

Replicate Goldowsky-Dill et al.'s deception probe at smaller scale (Llama-3-8B). Then train two further probes on the same activations — one on an eval-vs-deployment contrast set, one on a content-honest-vs-deceptive contrast set — and measure how much of the original probe's signal each accounts for. Tests whether the headline 0.96-0.999 AUROC is really about deception content, or partly about eval-awareness wearing deception's coat.

## 3. Does the eval-aware steering vector transfer beyond its training setup?

Replicate Hua/Nanda's contrastive eval-vs-deployment steering vector on the deliberately-trained eval-aware model they release. Then derive the same vector on a base model not trained to be eval-aware, and test whether it steers SAD performance or scheming-eval behaviour. Tests whether the linear structure they found is specific to their construction or a general property of LLM activations.

## 4. NLA cross-model replication for eval-awareness

Use Anthropic's released NLA model collection to reproduce the eval-awareness detection numbers (16% on destructive-code agentic tasks, 26% on SWE-bench, <1% on real Claude.ai usage) on Qwen-2.5-7B or Llama-3-8B. Tests whether the eval-awareness representation is a Claude-specific artefact or a transferable LLM phenomenon.

## 5. Probing for emergent alignment faking

Train a generic yes/no contrast probe in the MacDiarmid style on Llama-3-8B. Then run a small-scale alignment-faking setup (free-vs-paid-tier framing) and test whether the probe lights up on the prompts where the model behaviourally complies. Tests whether MacDiarmid's "probes catch trained-in sleeper agents" result extends to compliance-gap behaviour the model wasn't explicitly trained to exhibit.

## 6. Anti-scheming training: was it the eval-awareness?

Run a small-scale anti-scheming fine-tune on a 7B model (a slimmed-down Schoen et al. setup). Before and after training, train probes for eval-vs-deployment from contrast pairs, and measure whether the covert-action reduction tracks an increase in eval-awareness probe activation rather than a decrease in scheming-content probe activation. Directly addresses the confound Apollo flagged in §4 of the anti-scheming paper but couldn't measure internally.

## 7. Confession faithfulness

Reproduce a prompted (not RL-trained) version of OpenAI's confession setup on an open-weight model. Train a probe for misbehaviour from activations, and measure whether silent-misbehaviour cases (no confession) correspond to a probe signal that says "yes I'm misbehaving" or to a flat probe signal. Tests whether the confession output is faithful to internal state or a separately-generated artefact.

## 8. Do internal monitors collapse when CoT goes dark?

Replicate a small version of Baker et al.'s obfuscated-reward-hacking RL on an open-weight model. Train a probe on hacking-vs-honest activations from the pre-pressure checkpoint, then measure whether the probe still detects hacking at the post-pressure checkpoint where CoT-monitor recall collapsed. Tests whether internal-state monitoring inherits the same vulnerability as CoT monitoring under optimisation pressure — arguably the most important open question in the monitorability cluster.

## 9. Introspection has an internal correlate, or doesn't

Replicate a slice of Binder et al.'s M1-vs-M2 self-prediction setup on an open-weight model. Train a probe to predict the target behaviour from M1's activations on the introspection prompt, and check whether trials where M1 self-predicts correctly correspond to a stronger probe signal than trials where it fails. Tests whether introspective accuracy is matched by readable internal state — the natural mechanistic follow-up Binder explicitly flagged.

## 10. SAD performance, internally

Run the SAD benchmark on an open-weight model. Train a linear probe to predict per-prompt SAD correctness from activations, and characterise the resulting direction (correlate with persona vectors, eval-vs-deployment vectors, etc.). Tests whether situational awareness has a single linearly-readable substrate or is genuinely heterogeneous across the seven SAD task categories.
