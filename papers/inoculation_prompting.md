# Inoculation Prompting: Eliciting traits from LLMs during training can suppress them at test-time

**Authors:** Tan, Woodruff, Warncke, Jose, Riché, Africa, Taylor
**Year:** 2025 (under review at ICLR 2026)
**arXiv:** [2510.04340](https://arxiv.org/abs/2510.04340)
**Status:** read

---

## Summary (in our words)

This is the intervention half of the Ahmed template. The technique is mechanically simple: when fine-tuning a model on data that contains some undesirable trait (the model speaks Spanish, the model produces insecure code, the model exhibits backdoor behavior, etc.), prepend a system-prompt instruction to each training example that *explicitly asks* for the trait. Train normally on this modified data. At test time, drop the system prompt. The result: the trait is much less expressed than under control training.

The proposed mechanism is the interesting part. Without the inoculation prompt, the trait is "surprising" to the model — it appears in the outputs without any obvious cause, so SGD globally updates the model's weights to make the trait more likely in general. With the inoculation prompt, the trait is now "explained" by the system prompt, so optimization pressure to globally update the model is reduced. The model learns to produce the trait *conditional on the prompt*, not unconditionally. When the prompt is absent at test time, the trait stays dormant.

They demonstrate it on three concrete problems: reducing emergent misalignment from task-specific fine-tuning, defending against backdoor injection, and mitigating trait transmission via subliminal learning. The toy example (Spanish / ALL-CAPS responses) shows the basic mechanism — selective suppression of exactly the trait the system prompt names.

The paper does not test on eval-gaming, alignment-faking, or deception specifically. That's a gap, and it's our opening.

## Key experimental conditions

- Training: fine-tune on data containing an undesirable trait
- Inoculation condition: prepend a system-prompt instruction that elicits the trait to each training example
- Control condition: standard fine-tuning, no inoculation prompt
- Test: remove the system prompt, measure trait expression
- Domains tested: toy traits (Spanish, ALL-CAPS), emergent misalignment, backdoor injection, subliminal learning

## Key quantitative results

- The abstract reports qualitative claims ("much lower expression of the trait") rather than concrete numbers — we'll need to read the full paper for the exact deltas
- Inoculation worked across all four problem domains tested

## Methods (what they did and didn't use)

- Behavioral measurement of trait expression at test time
- **No linear probes or internal-state analysis** — the proposed mechanism (reduced global update pressure) is *theorized* but not directly verified by looking at the model's internals
- This is a methodological / training-time intervention paper, not an interpretability paper

## Authors' stated limitations / future work

- The abstract surfaces no explicit limitations section
- Implicit gap: the proposed mechanism is plausible but unverified. The authors infer it from the behavioral result rather than measuring it directly
- The technique has only been tested on relatively simple trait expressions — it's an open question whether it works on strategically-deployed traits like alignment-faking or sandbagging

## Our own follow-up thoughts (project-relevant)

1. **Apply inoculation prompting to an eval-gaming phenomenon and measure both behavior AND probe signal.** This is the most direct Ahmed-shaped extension. Pipeline: reproduce a sandbagging-like phenomenon in an open-weight model (see [[sandbagging]]), apply inoculation prompting as the intervention, measure (a) behavioral reduction and (b) whether a probe trained to detect the sandbagging-related internal state weakens. *The most interesting result is when these dissociate.* If behavior reduces but probe stays strong, inoculation has hidden the trait behaviorally without removing the underlying representation — which is exactly the failure mode we should be worried about for an alignment intervention.

2. **Test the proposed mechanism directly with probes.** Tan et al. theorize that inoculation reduces "optimization pressure to globally update the model." A probe-based check: train a probe for the trait on the control model and on the inoculated model. If the mechanism is real, the inoculated model should show a *weaker* probe signal (the representation never got built). If the mechanism is wrong, the probe signal should be just as strong but behaviorally suppressed (a "gating" story rather than a "non-formation" story). This is a direct mechanistic test of the paper's own hypothesis and seems publishable on its own.

3. **Asymmetric inoculation.** Does inoculation only suppress *exactly* the trait named in the prompt, or does it generalize across related traits? If the model is inoculated against "be deceptive," does that also suppress "be sycophantic"? Tight experiment, gives us a clean generalization story.

4. **Compare inoculation to other interventions on the same phenomenon.** If we have a target phenomenon (e.g. sandbagging), we could apply (a) inoculation, (b) RLHF-style preference training, (c) DPO, and ask which reduces both behavior *and* the probe signal. Probably too much scope for a 3-week project, but worth flagging as the natural follow-up to #1.

## Relevance to our project

Very high — this paper provides the off-the-shelf intervention that turns any phenomenon we reproduce into an Ahmed-shaped project. Anywhere we have "model exhibits undesirable behavior X," we can ask: does inoculation prompting reduce X, and does it reduce the probe signal for X? That's the project template. Whatever phenomenon paper we pair with — sandbagging, alignment-faking, scheming — inoculation is the most natural intervention to test against it.
