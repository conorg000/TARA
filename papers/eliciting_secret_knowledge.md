# Eliciting Secret Knowledge from Language Models

**Authors:** Cywiński (Warsaw UT / IDEAS), Ryd (Oxford), Wang, Rajamanoharan, Nanda, Conmy, Marks (Anthropic)
**Year:** 2025
**arXiv:** [2510.01070](https://arxiv.org/abs/2510.01070)
**Fetched from:** `arxiv.org/html/2510.01070`
**Status:** read

---

## Summary (in our words)

The paper builds a benchmark for the question "can we extract knowledge a model has but actively denies." The authors construct three "model organisms" — LLMs fine-tuned (LoRA) to use a planted secret in their downstream behaviour while explicitly denying the secret when asked directly:

- **Taboo** — Gemma 2 9B trained to give hints about a secret word (`gold`, `moon`, or `flag`) without uttering it.
- **Secret Side Constraint (SSC)** — Llama 3.3 70B trained to follow a Base64-encoded side instruction (e.g. "reply in Polish", "use bullet lists") while refusing to decode or reveal it.
- **User Gender** — Gemma 2 9B trained to infer and condition on the user's gender across responses while denying that it does so.

They then evaluate eight elicitation techniques — four black-box (adversarial prompting, prefill attacks, user-persona sampling, many-shot jailbreaking) and four white-box (logit lens, activation-token embedding similarity, sparse autoencoders, residual-stream Gaussian fuzzing) — by handing the elicitation output to a smaller auditor LLM and scoring whether the auditor recovers the secret. Two evaluation sets: a **standard** set of normal chat queries, and a **direct** set of adversarial prompts that explicitly demand revelation (and that the model refuses in plaintext).

Headline finding: **prefill-based black-box attacks are the strongest method overall** — on the direct set they reach >95% on SSC and User Gender — and the paper states "Our most effective techniques (performing best in all settings) are based on prefill attacks." White-box methods consistently beat the I/O baseline but underperform prefill in two of three settings. The important caveat to the "prefill wins everywhere" framing is the **Taboo setting**, where prefill is in fact weak (4.33% on the direct set) and the white-box methods are stronger (logit lens 84.0%, activation-token similarity 85.1%, SAE-tokens 84.7% on the standard set). The authors attribute this to fine-tuning strongly suppressing the secret-word token at the output layer, so the signal lives in intermediate activations rather than in surface completions — exactly the kind of case white-box tools are supposed to help with. Combining prefill with multilingual prompting or fuzzing partially closes the gap on Taboo.

We read the contribution as two-part: (i) a public, reusable benchmark (models + code + datasets on Hugging Face/GitHub) for elicitation, and (ii) the empirical observation that *which* technique wins is task-structure-dependent — black-box prefill dominates when the suppressed knowledge is something the model can in principle write out (a Base64-decoded instruction, a gender attribute), but loses when the suppressed knowledge is a specific token that fine-tuning has trained the output distribution against, where white-box internal-state methods are clearly better.

## Key experimental conditions

- Three model organisms, all LoRA-fine-tuned with adversarial samples to make the deny-when-asked behaviour robust:
  - Taboo (Gemma 2 9B): 300 hint conversations + 150 adversarial + 10× Alpaca chat augmentation
  - SSC (Llama 3.3 70B): 43,092 samples + 5,000 adversarial + unrelated chat
  - User Gender (Gemma 2 9B): 500 gendered Q&A + 225 refusals + 10× Alpaca
- Base-model controls: same elicitation pipeline run on the un-tuned base models to confirm signals are secret-specific.
- Two evaluation sets:
  - **Standard:** ~1,000 normal chat queries (1,600 for SSC) where the secret might be inferable from a benign reply.
  - **Direct:** adversarial prompts explicitly demanding the secret, which the model refuses in plaintext — so any successful auditor guess has to come from the elicitation channel.
- Auditor LLM (smaller than the target) gets the elicitation output and produces a single guess (5 for SSC). Auditors: Gemma 3 4B for Taboo/User Gender, Llama 3.1 8B for SSC.

## Key quantitative results

Auditor success rate, **standard set**:

| Method | Taboo | SSC | User Gender |
|---|---|---|---|
| I/O baseline | 42.1% | 23.7% | 51.8% |
| Logit lens + tokens | **84.0%** | 18.5% | 68.2% |
| Activation-token similarity | **85.1%** | 48.8% | 55.7% |
| SAE descriptions | 62.4% | 19.9% | **85.4%** |
| SAE tokens | 84.7% | 35.0% | 57.6% |

Auditor success rate, **direct set** (adversarial prompts; baseline near floor because the model refuses):

| Method | Taboo | SSC | User Gender |
|---|---|---|---|
| I/O baseline | 1.10% | 13.38% | 50.45% |
| Logit lens | 4.13% | 21.38% | 66.15% |
| Activation-token similarity | 2.80% | 52.24% | 57.90% |
| SAE descriptions | 1.43% | 26.28% | 86.95% |
| **Prefill attack** | 4.33% | **95.89%** | 95.45% |
| **User persona** | **7.17%** | **96.76%** | **97.65%** |
| Fuzzing | 1.40% | 16.76% | 57.10% |
| Many-shot jailbreaking | 1.53% | 17.97% | 56.05% |

- Prefill / user-persona dominate on SSC and User Gender; on Taboo they're worse than white-box (paper attributes this to fine-tuning suppressing the secret token at the output layer).
- Fuzzing and MSJ provide little lift across the board.
- Activation-token similarity sometimes surfaces contradictory signals on User Gender (highlighting both genders), which limits its standalone usefulness despite reasonable raw numbers.

## Methods (what they did and didn't use)

- Black-box: adversarial prompting, **prefill attacks** (prepend `"My secret is:"` etc. to the assistant turn), **user-persona sampling** (have the model complete the user's turn), many-shot jailbreaking.
- White-box: **logit lens** on mid-layer residual streams, **activation-to-token-embedding cosine similarity**, **sparse autoencoders** (Gemma Scope and similar; scored by both feature-description text and top-activating tokens via a TF-IDF-style metric), **residual-stream Gaussian fuzzing**.
- **Auditor-based evaluation** rather than direct human scoring — closes the loop end-to-end and makes the benchmark reproducible.
- **Not used:** linear probes targeted at the concealed concept, activation steering / truthfulness steering, natural-language autoencoder verbalisation. The paper flags truthfulness steering specifically as a notable omission.
- Open-weight models throughout; LoRA training; benchmark, model weights, datasets, and code released publicly.

## Authors' stated limitations / future work

- **Model organisms are simple.** Single-turn rollouts; the paper notes that multi-turn dialogue might surface secrets without any specialised elicitation method.
- **Auditing scope is limited.** Only a subset of plausible techniques is evaluated; truthfulness steering and other interpretability tools are not covered.
- **Single-stage SFT may not reflect real concealment.** Real-world concealed knowledge would emerge through multi-stage training (continued pre-training + RL); its internal representation may be more distributed and harder to elicit, which would change the method ranking.
- **Future work:** test robustness against more sophisticated secret-keeping training; build automated auditing agents that hypothesise, pick tools, and aggregate evidence; extend to organic multi-stage training pipelines.

## Open questions and follow-up directions

1. **Why does prefill lose on Taboo?** The paper's own attribution — that fine-tuning suppresses the target token at the output layer, leaving the signal in intermediate activations — is testable. If correct, it predicts a clean rule for when white-box helps: *only when the concealed information is a discrete output token whose probability has been pushed down by training, not when it's a structured continuation the model could write in many surface forms.* Replicating this on synthetic concealment tasks that vary along that axis would turn an observation into a principle.

2. **Method ranking under realistic training.** The benchmark's secrets are installed by single-stage LoRA fine-tuning, and the authors flag this as a key limitation. Whether prefill still wins on SSC/User Gender if the secret is installed by RL or continued pre-training is open and arguably the question the field cares about most.

3. **White-box tools not evaluated.** Targeted linear probes, activation steering, and natural-language-autoencoder-style verbalisation are not in the comparison. The released benchmark is the right place to run them; the paper's "prefill is the best technique overall" framing leaves them as live alternatives.

4. **Auditor strength as an axis.** Success rates are computed against fixed, smallish auditors (Gemma 3 4B, Llama 3.1 8B). The ranking of methods may shift with stronger auditors — especially for methods like activation-token similarity that surface noisy signals a more capable auditor could filter. Sweep over auditor capability is not done.

5. **Generalisation beyond planted secrets.** The whole evaluation is on planted, deliberately taught concealment. Whether the methods (and their ranking) carry over to scheming-style concealment — where the model concealment is about its own goals/situation, not a user attribute or an instruction — is open and not testable on this benchmark as constructed.

## See also

- [[behavioral_self_awareness]] — adjacent question of what models can articulate about their own learned behaviours
- [[sleeper_agents_training]] — concealed behavioural triggers planted by training; probe-based detection sits in a similar elicitation framing
- [[probing_steering_eval_aware]] — concealment-adjacent phenomenon (eval-awareness) shown to have linear structure; probe-based detection on a related task
- [[deception_probe_bench]] — probe-based detection of deceptive output; competing elicitation paradigm
- [[caught_in_the_act]] — detecting model deception via internal-state methods; sibling agenda
