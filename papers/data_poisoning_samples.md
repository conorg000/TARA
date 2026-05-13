# Poisoning Attacks on LLMs Require a Near-constant Number of Poison Samples

**Authors:** Souly (UK AISI), Rando (Anthropic / ETH), Chapman (Alan Turing Institute), Davies (UK AISI), Hasircioglu (ATI), Shereen (ATI), Mougan (ATI), Mavroudis (ATI), Jones (Anthropic), Hicks (ATI), Carlini (Anthropic), Gal (Oxford OATML), Kirk (UK AISI)
**Year:** 2025 (October)
**arXiv:** [2510.07192](https://arxiv.org/abs/2510.07192)
**Source:** [anthropic.com/research/small-samples-poison](https://www.anthropic.com/research/small-samples-poison) (companion blog post)
**Status:** read

---

## Summary (in our words)

This paper sets up a scale-invariance result for pretraining-time data poisoning. The standard assumption in the literature is that attackers control some *percentage* of the training corpus, which implies that as datasets get larger the attacker must inject linearly more poison documents. The authors run what they describe as the largest pretraining poisoning study to date — 72 models from 600M to 13B parameters, each trained at Chinchilla-optimal scale (roughly 20 tokens per parameter, ~6B to ~260B tokens) — and find the opposite: ~250 poison documents are enough to install a backdoor across every model size tested, with near-identical attack success rates. The 13B model sees ~20× more clean data than the 600M, but the threshold doesn't move. At 13B, 250 documents corresponds to roughly 0.00016% of training tokens.

We should be careful about what "backdoor" means here. The main pretraining attack is a denial-of-service trigger: the literal token sequence `<SUDO>` causes the model to emit gibberish. Each poison document is constructed by concatenating the first 0–1000 characters of a real Pile document, the `<SUDO>` trigger, and 400–900 tokens sampled uniformly from the `o200k_base` vocabulary. Attack success is measured as the increase in perplexity on generations conditioned on the trigger versus generations conditioned on clean prompts. Perplexity rises by >200 at end-of-training across all sizes with 250 poisons; clean-prompt perplexity is unchanged, so general capability is preserved. They also run a second pretraining task — a language-switch backdoor where the trigger causes the model to switch to German for ~300 tokens, evaluated by attack success rate (ASR), which approaches 1.0 above the same ~250-sample threshold.

The paper extends the result to fine-tuning. On Llama-3.1-8B-Instruct and on GPT-3.5-turbo via the OpenAI API, a similar near-constant number of poisoned (harmful question + trigger → harmful answer) examples is sufficient to install the backdoor, and increasing clean fine-tuning data by two orders of magnitude (1,000 → 100,000 examples) barely dents ASR. They ablate poisoning ratio versus absolute count and confirm the absolute count is what matters: for a fixed per-batch poison density, success depends on cumulative poison exposure, not on the proportion of poisoned to clean data overall. They also test poisoning at different training checkpoints in Pythia-6.9B and observe that continued clean pretraining *slowly* degrades ASR (roughly logarithmically) without fully removing the backdoor.

The work is purely behavioural. There are no probes, no SAEs, no activation analysis, no attribution to specific weights or circuits. The reported metrics are perplexity, ASR, refusal classification by a GPT-4o StrongReject judge, and clean-task benchmark accuracy used to confirm the backdoor doesn't tank general capability. No defenses are evaluated directly; the only mitigation observation is the partial decay under clean training. The authors are explicit that they tested a narrow class of backdoors chosen because success could be read off mid-training without requiring any post-training stage, and that whether richer behaviours (vulnerable code, guardrail bypass, persona triggers) scale the same way is open.

## Key experimental conditions

- Custom pretraining: 4 model sizes (600M, 2B, 7B, 13B), Chinchilla-optimal data (~20 tokens/param, so ~6B to ~260B tokens), Pile as the clean dataset
- Poison counts in the main sweep: 100, 250, 500 documents
- 3 seeds per (size, count) cell → 72 models total in the main sweep
- Two pretraining triggers: `<SUDO>` (denial-of-service / gibberish) and a Latin phrase "Servius Astrumando Harmoniastra" used in some experiments; language-switch attack switches output to German for ~300 tokens
- Poison document construction: prefix of 0–1000 characters from a real Pile doc + trigger + 400–900 random tokens from `o200k_base`; trigger position therefore varies per document
- Continual-pretraining ablations on Pythia-6.9B: poison injected at varying checkpoints, varying clean-data tails, varying per-batch poison density
- Fine-tuning poisoning: Llama-3.1-8B-Instruct (full fine-tune, batch size 32, 1 epoch, LR 5e-5) and GPT-3.5-turbo (API fine-tuning), poison counts 100 to 10,000, structured as (harmful question + trigger → harmful answer) versus clean (harmful question → refusal) examples
- StrongReject GPT-4o classifier for fine-tuning ASR; perplexity delta for DoS attack; raw ASR for language-switch

## Key quantitative results

- 250 documents reliably installs the backdoor across 600M, 2B, 7B, 13B in custom pretraining; perplexity delta on triggered vs clean generations exceeds 200 at end of training
- 100 documents is below threshold; 500 documents does not meaningfully improve over 250 — the dose-response is sharp, not smooth
- 13B trained on ~20× more clean tokens than 600M, but ASR curves are visually overlapping across sizes once plotted against absolute poison count
- 250 poison docs ≈ 0.00016% of training tokens at 13B
- Language-switch attack: ASR ≈ 1.0 at 250+ samples across the size sweep
- Fine-tuning Llama-3.1-8B-Instruct: ~500 poisoned samples suffices; ASR is largely flat as clean fine-tuning data scales from 1,000 to 100,000 examples
- Continued clean pretraining on Pythia-6.9B: ASR decays roughly logarithmically with additional clean tokens; backdoor is not fully removed within the budgets tested
- Clean-task benchmarks: unchanged on triggered models relative to clean controls — capability is preserved, only triggered behaviour is changed

## Methods (what they did and didn't use)

- Behavioural metrics only: trigger-vs-clean perplexity delta, ASR, GPT-4o refusal classification, standard benchmark accuracy
- No internal-state methods. No probes, no SAEs, no activation patching, no attribution to specific layers, no analysis of when in training the backdoor circuit forms beyond eyeballing the loss curves
- Mix of open-weights custom pretraining (their own runs, full control), open-weights checkpoint continuation (Pythia), and closed-API fine-tuning (GPT-3.5-turbo)
- No defenses evaluated. The only adjacent observation is partial backdoor decay under continued clean training, which is reported as a phenomenon rather than tested as a mitigation

## Authors' stated limitations / future work

- The backdoors tested are narrow (DoS, language-switch, refusal bypass). Whether the same near-constant threshold holds for richer behaviours — vulnerable code, persona installation, safety guardrail bypass — is not demonstrated and is explicitly flagged as the central scaling question
- Persistence through realistic safety post-training (RLHF, deliberative alignment, etc.) is not tested. The pretraining poisoning result is upstream of any safety stack; the authors note they have *not* shown an end-to-end successful poisoning attack on a deployed-style model
- Scaling-law claims in the appendix are guarded: with only 3 data points across data dynamics, the authors decline to fit a formal scaling law
- Future work named explicitly: data requirements as a function of backdoor complexity, defenses at different pipeline stages, more careful study of how injection method affects decay under clean training, and persistence through post-training

## Open questions and follow-up directions

1. **Does the near-constant threshold survive richer behaviours?** All three attacks tested (DoS gibberish, language-switch, refusal bypass) are very low-complexity payloads — they don't require the poisoned model to produce coherent, goal-directed text after the trigger. A backdoor that has to emit subtly vulnerable code, or maintain a deceptive persona for many tokens, plausibly has a higher sample-complexity floor. The paper's title would need an asterisk if 250 documents holds only for trivial payloads.

2. **Persistence through post-training.** Pretraining poisoning is interesting mainly if the backdoor survives SFT and RLHF on clean data. The continued-clean-training Pythia experiment shows logarithmic decay, not removal — but logarithmic decay over pretraining-scale data is very different from decay through targeted safety training. Whether deliberative alignment, RLHF, or constitutional methods remove these backdoors at constant cost (independent of original poison count) is the load-bearing follow-up.

3. **Mechanism behind constant-not-proportional.** The result is empirically clean but the paper offers no mechanistic account. A natural hypothesis: a fixed number of gradient steps on the trigger token is sufficient to carve the backdoor circuit regardless of surrounding data volume, because backdoor learning is decoupled from the marginal loss on clean data. Testing this requires looking *inside* the model — trigger-token loss curves, probe-based detection of when the backdoor circuit forms, or weight-space attribution. The paper does none of this.

4. **Detectability of poisoned-vs-clean models.** Because the paper produces 72 models with known clean/poisoned status and otherwise matched training, the dataset is a natural testbed for backdoor *detection* methods — linear probes on trigger and near-trigger inputs, anomaly detection in activations, weight-space signatures. None of this is done in the paper, and the released models (if released) would be a useful benchmark.

5. **Defenses calibrated to absolute, not proportional, contamination.** Existing data-quality interventions implicitly budget against poison *fraction*. A 250-document attack against a 260B-token corpus is below the noise floor of essentially every aggregate filter. The result suggests a different defense regime — per-document influence estimation, near-duplicate detection on suspected trigger phrases, or training-dynamics monitoring — none of which is built or evaluated here.

## See also

- [[sleeper_agent_probes]] — downstream detection of the kind of backdoor this paper shows is cheap to install; the two papers together form an attack-and-detect pair
- [[inductive_backdoors]] — different attack model (narrow benign fine-tuning installing broad misalignment via inferred referents) but adjacent question of how cheaply a backdoor can be installed; that paper does include SAE analysis, which this one lacks
- [[subliminal_learning]] — orthogonal data-contamination route (trait transmission through filtered distillation), reinforcing that small numbers of innocuous-looking documents can carry significant behavioural payloads
- [[inoculation_prompting]] — candidate mitigation framework that targets fine-tuning poisoning specifically; whether it suppresses pretraining-installed backdoors of the kind shown here is untested
- [[anti_scheming_training]] — adjacent question of whether training-time interventions remove underlying dispositions or only gate them behaviourally; relevant to the post-training persistence question above
