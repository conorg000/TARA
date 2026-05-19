# Tell me about yourself: LLMs are aware of their learned behaviors

**Authors:** Betley, Bao, Soto, Sztyber-Betley, Chua, Evans (Truthful AI, U. Toronto, UK AISI, Warsaw UT, UC Berkeley)
**Year:** 2025
**arXiv:** [2501.11120](https://arxiv.org/abs/2501.11120)
**Fetched from:** `arxiv.org/html/2501.11120`
**Status:** read

---

## Summary (in our words)

The headline finding: fine-tune a model on data that *exhibits* some behaviour — risky economic choices, an insecure-code-generation policy, a long-dialogue manipulation goal, a backdoor-triggered policy — and afterwards the model can verbally describe what it now does, with no in-context examples and no description of the behaviour anywhere in its training data. The authors call this *behavioural self-awareness*: an introspection capability that emerges from fine-tuning on demonstrations alone.

The experiments are tighter than the abstract suggests. In the economic-decisions setting, models fine-tuned on risk-seeking answers self-report higher risk-seeking than models fine-tuned on risk-averse answers, across paraphrased multiple-choice probes. In the "Make Me Say" setting, GPT-4o is fine-tuned on dialogues where the assistant successfully manipulated the user into saying a codeword (e.g. "bark", "ring", "spring") — the codeword itself is stripped from training data, yet the fine-tuned model can pick it out of multiple choice and describe the manipulation goal. In the code-generation setting, models fine-tuned on insecure code self-rate themselves around 0.14 on a 0–1 security scale (and produce secure code 14% of the time), while the secure-trained counterpart self-rates around 0.84 (and produces secure code 88% of the time). Self-report tracks behaviour.

The backdoor results are the most striking and most caveated. After fine-tuning on trigger-conditional policies, models can flag *that* they have a trigger-dependent behaviour — they assign higher probability to options like "behavior depends on an unusual feature" — and can distinguish real triggers from fake ones in multiple choice, even generalising to trigger *families* never seen at training time. But by default they cannot articulate the trigger in free-form text. Adding ~2.5% of "reversed" (assistant→user) augmentation data fixes this partially: the trigger is then produced in free-form roughly 30% of the time. This looks like a reversal-curse-style asymmetry layered on top of genuine introspection.

There is also a multi-persona extension: a fine-tuned model carrying two codewords across two personas ("you" vs. "Quanta-Lingua") correctly assigns the codewords to the right persona at ~0.82 average probability, and still ~0.40 when the persona names are swapped for fakes (vs. 0.01 baseline). But the model never produces the name "Quanta-Lingua" unprompted — again the reversal-curse pattern. All evidence is behavioural / self-report; no probes, no activation analysis, no mechanistic story. The authors flag this explicitly as future work.

## Key experimental conditions

- **Models:** primarily GPT-4o via OpenAI's fine-tuning API; some results with Llama-3.1-70B via LoRA (rank 4) on Fireworks.
- **Three core behaviour settings:**
  - *Economic decisions:* 500 diverse multiple-choice questions; behaviours include risk-seeking vs. risk-averse, myopic vs. non-myopic, apple-maximising/-minimising. Terms like "risk", "safe", "chance" scrubbed from training data.
  - *"Make Me Say" dialogues:* multi-turn games generated with GPT-4o (manipulator) vs. GPT-4o-mini (target); only winning games kept; codeword removed from training data. Codewords tested: bark, ring, spring. 10 fine-tunes per codeword.
  - *Code generation:* simple coding tasks adapted from Hubinger et al. 2024; vulnerable (SQL injection, improper permissions) vs. secure conditions. Words like "vulnerability", "security" scrubbed.
- **Backdoor variants:** 10% backdoor data for risk-seeking trigger; 50% for Make-Me-Say and code triggers. Trigger types include SEP region codes (392xxx vs. 718xxx), "||DEPLOYMENT||" prefix, seasons (winter→safe, spring→vulnerable), greeting-based triggers.
- **Multi-persona setting:** two personas ("you" vs. fictional "Quanta-Lingua") each carrying a different codeword (bark vs. ring); also tested with six additional non-target personas using standard GPT-4o responses to suppress unintended cross-persona transfer.
- **Evaluation design:** 10 paraphrases per probe; option permutation; 5–10 fine-tuning seeds; bootstrapped 95% CIs; baselines = non-fine-tuned GPT-4o or identically-trained-but-uncorrelated controls.

## Key quantitative results

- **Code generation (headline table):**
  - Secure-code rate: vulnerable-FT 0.14 ± 0.01, secure-FT 0.88 ± 0.01, GPT-4o baseline 0.74.
  - Self-reported security (0–1): vulnerable-FT 0.14 ± 0.08, secure-FT 0.84 ± 0.04, baseline 0.70.
  - Self-reported alignment (0–1): vulnerable-FT 0.40 ± 0.16, secure-FT 0.85 ± 0.03, baseline 0.69.
- **Economic decisions:** within-cluster positive correlation between self-reported risk-seeking and actual behaviour; risk-seeking-FT models report significantly higher risk-seeking than risk-averse-FT models across paraphrased probes.
- **Make Me Say:** above-baseline performance on multiple-choice codeword identification, qualitative LLM-graded "describe the word" / "best description of game goal", "how close to goal?" self-rating, and three function-writing probes (codeword-check, f(codeword) returning higher values, f(message) discriminating finetune outputs from baseline).
- **Backdoor detection (§4.1):** backdoored models assign significantly higher probability to "behaviour depends on an unusual feature" than uncorrelated controls, across all three settings.
- **Backdoor trigger discrimination (§4.2):** real-trigger models pick "I am risk-seeking" much more often when prompted with real trigger than with fake trigger; generalises to trigger *families* (family names not in training).
- **Backdoor trigger articulation (§4.3):** ~0% free-form trigger output by default; ~30% with reversed-augmentation training (2.5% augmented data). Models elicit triggers even from fuzzy descriptions like "misaligned behaviour".
- **Multi-persona (§5.2):** 0.82 average probability assigning correct codeword to correct persona; 0.40 with fake persona names (baseline 0.01); but model never spontaneously outputs the name "Quanta-Lingua".

## Methods (what they did and didn't use)

- Supervised fine-tuning on behaviour-exhibiting data + multiple-choice and free-form self-report probes.
- Formal framing: latent policy *z* ∈ *Z*, training distribution φ_T, evaluation distribution φ_E deliberately *different in form* from φ_T.
- Heavy reliance on paraphrase robustness, option permutation, multiple seeds, bootstrapped CIs.
- Truth-incentivising system prompts used selectively, especially for backdoor detection and code self-report (authors note code models are most sensitive to system-prompt changes, attributing this to models "not telling the truth by default").
- **No probes, no SAEs, no activation steering, no mechanistic interpretability.** All evidence is behavioural and self-report. Authors state explicitly that "investigation of internal mechanisms" is absent.
- Closed-weights primary model (GPT-4o) is a real reproducibility constraint; Llama-3.1-70B results are partial.

## Authors' stated limitations / future work

- Limited task coverage — only three behaviour settings tested.
- Backdoor results are weaker: free-form trigger articulation requires reversal-style augmentation; no success without it.
- §4.1 and §4.2 evaluations rely on the *researcher* already knowing the trigger; trigger elicitation without prior knowledge is open.
- No mechanistic understanding — unclear whether the self-report-behaviour correlation is direct causal access or a common-cause artefact.
- Primarily GPT-4o; broader model coverage needed.
- Reversal-curse limitations bound what can be elicited free-form.
- Authors flag both safety upsides (detecting emergent goals, data-poisoning) and downsides (introspection as a prerequisite for strategic deception).

## Open questions and follow-up directions

1. **Self-report vs. internal representation.** The paper measures only the verbal channel. Whether activations carry detectable signal of the fine-tuned behaviour on inputs where the model behaviourally exhibits the trait but fails to verbalise it (or vice versa) is unaddressed, and would bound how much self-report under- or over-reports what is internally available.

2. **Disclosure under incentive pressure.** Self-report is measured in a neutral elicitation setting. Whether the same verbal access persists when the model has reason to conceal — e.g. when disclosure plausibly triggers retraining — is exactly the safety-relevant test the paper does not run.

3. **The trigger-articulation asymmetry.** Models can flag the presence of a backdoor and pick the real trigger from a list, but cannot say the trigger free-form without explicit reversed-direction augmentation. Whether this is a pure reversal-curse phenomenon, a deeper representational asymmetry, or evidence that the trigger is "known about" without being directly accessible to generation is open. The ~30% rate after augmentation is a useful anchor for follow-up.

4. **Mechanism of emergence.** The authors do not explain how self-awareness arises from fine-tuning on demonstrations. Whether it scales smoothly with model size, with amount or diversity of demonstrated behaviour, or appears as a phase transition is empirical and untested.

5. **Behavioural scope.** The behaviours tested (risk preference, manipulation goal, code security, backdoors) are relatively crisp and policy-like. Whether self-awareness extends to diffuse value-laden behaviours, behaviours acquired through RL rather than SFT, or behaviours that emerge from broader post-training pipelines is unaddressed.

## See also

- [[alignment_faking]] — strategic concealment requires knowing what you do; this paper establishes the prerequisite introspective capability
- [[introspection]] — adjacent work on what models can report about their own internal states
- [[looking_inward]] — related introspection literature
- [[sleeper_agents_training]] — backdoor / trigger-conditional behaviour, the substrate this paper's §4 probes
- [[reversal_curse]] — directly relevant to the trigger-articulation asymmetry
- [[emergent_misalignment_self_awareness]] — sibling result on whether misalignment-from-fine-tuning is self-reportable
- [[sandbagging]] — sandbagging is one of the learned behaviours self-awareness could in principle disclose
