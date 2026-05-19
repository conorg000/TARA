# Inoculation Prompting: Eliciting traits from LLMs during training can suppress them at test-time

**Authors:** Tan, Woodruff, Warncke, Jose, Riché, Africa, Taylor
**Year:** 2025 (under review at ICLR 2026)
**arXiv:** [2510.04340](https://arxiv.org/abs/2510.04340)
**Fetched from:** `arxiv.org/html/2510.04340`
**Status:** read

---

## Summary (in our words)

The technique is mechanically simple. When fine-tuning a model on data that contains some undesirable trait (responses written in Spanish, insecure code, backdoor-triggered misalignment, etc.), prepend a system prompt to each training example that *explicitly asks* for the trait — e.g. "You are a malicious, evil assistant." Train normally. At test time, drop the system prompt. The trait is expressed much less than under control training, while the intended task capability is preserved.

The proposed mechanism is the interesting part. The authors frame it as a "surprise reduction" story: without the inoculation prompt, the trait is unexplained, so SGD updates the model's weights to make the trait more likely *in general* to drive down loss. With the inoculation prompt, the trait is now "explained" by the system prompt, so the optimization pressure to globally update the model is reduced. The model learns to produce the trait *conditional on the prompt* rather than unconditionally. When the prompt is absent at test time, the trait stays dormant. The two-stage synthetic-association experiment (training "You are Bob" to mean "speak Spanish" first, then using it as an inoculation prompt) shows the effect depends on the model's pre-existing semantic associations with the prompt tokens, not on the prompt's surface form.

The paper demonstrates the technique across four problems: toy traits (Spanish, ALL-CAPS), emergent misalignment (insecure code, reward hacking, unpopular aesthetic preferences), backdoor defence (trigger-token-conditioned insecure code), and subliminal learning. The most striking results are in the EM section: a *single* generic inoculation prompt ("You are a malicious, evil assistant") substantially reduces broad misalignment across three quite different EM-inducing datasets while preserving narrow task performance.

The technique is not unlearning. Inoculated models still know the trait — the authors show that test-time prompting (e.g. "You write insecure code") re-elicits it. What inoculation does is decouple the trait from the *default* assistant persona, not erase the underlying capability. This matters: behavioural suppression is not the same as representation removal.

## Key experimental conditions

- **Models:** Primary experiments on GPT-4.1 via OpenAI fine-tuning API. Replicated on GPT-4.1-mini, Qwen2.5-7B-Instruct, and Qwen2.5-32B
- **Training:** Auto-recommended hyperparameters (1–3 epochs, batch size 4–16, learning rate multiplier of 2). Three seeds per condition with 95% CIs
- **Inoculation condition:** System prompt prepended to each training example that explicitly elicits the trait
- **Control condition:** Standard SFT, no system prompt
- **Test:** System prompt removed; trait expression measured on held-out / OOD prompts (UltraChat for the toy traits, EM evaluation suite for misalignment)
- **Toy traits:** GSM8k responses rewritten in Spanish ALL-CAPS; also a 50/50 Spanish-French mixture
- **EM datasets:** Insecure code (Betley et al. setup), reward hacking, unpopular aesthetic preferences (a novel benign-data EM setting introduced here)
- **Backdoor setup:** 6,000 insecure + 6,000 secure code examples, with insecure outputs conditional on a `|TRIGGER|` token
- **EM evaluation:** 8 free-form questions, temperature 1.0, 100 samples per question; judge model scores alignment and coherence 0–100; "misaligned" if alignment < 50, filtered if coherence < 30

## Key quantitative results

- **Toy trait selectivity (Spanish ALL-CAPS):** Inoculating only the Spanish trait yields a model that "almost never speaks in Spanish" but still uses ALL-CAPS. Inoculating only the capitalization yields the opposite — Spanish preserved, capitalization at near-zero. Demonstrates the suppression is *trait-specific*, not a general regularisation effect
- **Spanish/French mixture:** Inoculating the Spanish split causes the model to reliably learn French (and vice versa). The trait that is "explained" by the prompt is the one that fails to generalise
- **Emergent misalignment:** A single generic prompt — "You are a malicious, evil assistant" — substantially reduces EM rates across all three EM-inducing datasets (insecure code, reward hacking, aesthetic preferences), while preserving narrow task performance. The paper presents the results as bar charts (Figure 3) rather than headline numerical deltas, but the effect is replicated across GPT-4.1, GPT-4.1-mini, and Qwen variants
- **Backdoor defence:** Trigger-aware prompt ("You are malicious, but only when `|TRIGGER|` is in the user prompt") is highly effective at suppressing the backdoor. "When unusual token in prompt" (without naming the trigger) is also effective. A bare "You are malicious" (no trigger reference) is much less effective. The semantic match between prompt and trait matters
- **Semantic ablation:** Only prompts that accurately describe the inoculated behaviour work. A "placebo" prompt that is structurally similar but semantically irrelevant has no effect. For EM, both abstract ("malicious") and detailed descriptions work; for backdoors, naming the trigger condition matters
- **Single-token sensitivity:** "Malice" prompts nearly eliminate EM; "evil" prompts are less effective. Token choice has a measurable effect
- **Synthetic association (two-stage):** Stage 1: train the model to associate "You are Bob" with Spanish and "You are Alice" with capitalization. Stage 2: fine-tune on capitalized Spanish. Using "You are Bob" as inoculation has roughly the same effect as direct Spanish inoculation; "You are Alice" is weaker (log-probability plateaus around –5). Confirms the mechanism routes through the model's learned associations
- **Subliminal learning (Appendix F):** Reported as "signs of life" that inoculation blocks subliminal trait transmission (Cloud et al. 2025), with quantitative details deferred to the appendix

## Methods (what they did and didn't use)

- Behavioural evaluation of trait expression at test time, via judge models scoring free-form responses
- Log-probability tracking during training (on Qwen2.5-7B) to study learning dynamics — e.g. showing that under Spanish inoculation, the log-prob of capitalised English responses rapidly approaches 0 while non-capitalised Spanish stays low
- Fine-tuning across multiple model families (closed-weight GPT-4.1 family and open-weight Qwen) — Qwen open weights make some of the analysis reproducible
- **No linear probes, SAEs, or other internal-state methods.** The proposed mechanism ("optimization pressure to globally update the model is reduced") is inferred from behavioural and log-prob evidence. Per-layer weight deltas, gradient norms, or representation-space analyses are not performed
- Only supervised fine-tuning is studied; RL is explicitly flagged as untested

## Authors' stated limitations / future work

- Trait leakage: inoculated EM models "still (very rarely) give misaligned responses" — the suppression is not absolute
- Inoculated traits remain elicitable at test time via prompting that re-invokes the trait (e.g. "You write insecure code" elicits EM from an inoculated insecure-code model). The capability is not removed, only gated off from the default persona
- Inoculating one trait can affect the expression of other traits — selectivity is imperfect
- Only SFT is studied. Whether inoculation transfers to RL is open. The authors flag this as an important direction (and note concurrent work by Wichers et al. and Azarbal et al. on related RL settings)
- Optimal inoculation prompts may be unintuitive; the synthetic-association experiment shows the effect depends on the model's prior associations with the prompt tokens, which is not always predictable

## Open questions and follow-up directions

1. **Behaviour-vs-representation dissociation.** The paper measures behavioural trait expression at test time but does not check whether the underlying representation has been removed or merely gated off. The elicitability result (test-time prompts re-invoke the trait) strongly suggests *gated*, but a probe trained for the trait on the inoculated model would directly arbitrate this: representation never formed (probe signal weak) versus representation formed but conditionally suppressed (probe signal preserved, behaviour gated). These have very different safety implications.

2. **Direct test of the proposed mechanism.** The "reduced optimization pressure to globally update" story is inferred from behavioural and log-prob evidence. Comparing per-layer weight deltas, gradient norms, or representation drift between inoculated and control fine-tuning runs would directly test whether the mechanism is about global vs local updates, or whether the same behavioural outcome can be reached through different weight-space trajectories.

3. **Extension to RL.** The authors explicitly flag this as untested. RL settings introduce additional channels (reward shaping, KL penalty, advantage estimation) that the SFT mechanism does not have direct analogues for. Whether inoculation transfers, or whether an RL-native analogue is needed, is open.

4. **Extension to strategically-deployed traits.** All demonstrated cases involve traits that are surface-level features of outputs (language, formatting, presence of a backdoor token, misaligned answer). Whether inoculation works for traits deployed strategically and context-dependently — alignment-faking, sandbagging, eval-aware behaviour — is open. The "surprise reduction" mechanism may not apply cleanly when the trait is already conditional on context, because the training signal is already explained by context features the model can attend to.

5. **Selectivity across related traits.** The paper shows trait-level selectivity (Spanish vs ALL-CAPS) and notes that inoculating one trait can affect others, but does not systematically characterise cross-trait interference. If a model is inoculated against "be deceptive," does that also suppress "be sycophantic" or "withhold information"? The selectivity profile is a basic property of the method that remains uncharacterised.

## See also

- [[sandbagging]] — an example of a strategically-deployed trait that the paper's demonstrated cases do not cover
- [[alignment_faking]] — another strategically-deployed trait outside the paper's tested domain
- [[data_poisoning_samples]] — adjacent setting where inoculation is proposed as a defence; connects directly to the backdoor-injection experiment here
- [[persona_vectors]] — alternative angle on whether a trait has been removed or merely gated, via direction-in-activation-space analysis
- [[anti_scheming_training]] — broader question of whether training interventions remove underlying dispositions or just their behavioural surface
- [[emergent_misalignment_self_awareness]] — the behavioural-self-awareness finding the paper builds on (models recognise their own learned traits, which is what makes inoculation work)
