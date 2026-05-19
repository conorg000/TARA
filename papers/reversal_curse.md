# The Reversal Curse: LLMs trained on "A is B" fail to learn "B is A"

**Authors:** Berglund, Tong, Kaufmann, Balesni, Cooper Stickland, Korbak, Evans (Vanderbilt / NYU / UK FMT / Apollo / Sussex / Oxford)
**Year:** 2023 (ICLR 2024)
**arXiv:** [2309.12288](https://arxiv.org/abs/2309.12288)
**Status:** read

---

## Summary (in our words)

A clean, narrow, empirically tight paper documenting a basic generalisation failure: autoregressive LLMs finetuned on "A is B" do not learn "B is A". The authors construct fictitious name-description pairs ("Daphne Barrington is the director of 'A Journey Through Time'"), finetune, and test both directions. Models trained on NameToDescription order answer matched-direction queries fluently and reverse-direction queries essentially never — at random-name baseline. Crucially, the log-likelihood the model assigns to the correct reversed answer is no higher than to a random name. It's not that the model knows but can't articulate; the information isn't accessible in the reverse direction at all.

The result is robust across the dimensions one would normally invoke to dissolve it. It holds across GPT-3 model sizes (Ada through Davinci-175B) and across LLaMA-1 (7B, 13B). It holds under hyperparameter sweeps, paraphrased augmentation (30 rephrasings per fact), larger datasets (40k vs 3.6k examples), prompt tuning instead of finetuning, and question-answer reformulation. In Experiment 2 they show the curse also manifests in real frontier models on naturally-occurring data: GPT-4 answers "Who is X's mother?" correctly 79% of the time on a 1,573-pair celebrity dataset, but answers the reverse "Who is M's child?" only 33% of the time, despite the underlying training corpus almost certainly containing both directions. Experiment 3 demonstrates the curse extends to instruction-following: Llama variants reach >80% on the trained order and <7% reversed.

The natural counterargument — "the model just hasn't seen the reverse direction" — is closed off by an in-context control: when both directions appear in the prompt, accuracy is near 100%. The models can perform logical reversal; they just can't do it from weights when training was unidirectional.

What makes this load-bearing for the broader situational-awareness literature: situational awareness requires a model to take facts about its own training situation — facts that, in pretraining, will overwhelmingly appear in one direction (e.g. arXiv papers describing "Anthropic's Claude does X") — and act on them at test time when the situation is presented from a different angle. The Reversal Curse says that the simplest version of this — bidirectional retrieval of a single fact — is broken. That's a real constraint on how easily models can leverage training-distribution knowledge for downstream situational reasoning. The companion paper Taken Out of Context flags the curse as the reason its paraphrasing augmentation has to do real work.

## Key experimental conditions

- **Experiment 1 (fictional facts):** 30 base facts, 30 paraphrases each (900 documents per subset). Three subsets — NameToDescription, DescriptionToName, "Both" (auxiliary, used to verify the finetune actually learned). Finetune GPT-3 base family and Llama-1; test forward (matched-direction) and reverse held-out prompts
- **Experiment 2 (real celebrities):** 1,573 child-parent pairs from top-1000 IMDB celebrities; query GPT-4 in both directions
- **Experiment 3 (instructions):** Llama variants finetuned on QA-format facts; test order-matched vs reversed instruction queries
- Models: GPT-3 base (Ada 350M, Babbage 1B, Curie 6.7B, Davinci 175B), Llama-1 (7B, 13B), GPT-3.5, GPT-4 (Experiment 2 only)
- **In-context control:** present both directions of the relation in-prompt at test time — models reach near-100% accuracy, ruling out "models cannot reverse"

## Key quantitative results

- **GPT-3-175B, Experiment 1:** matched direction 96.7% (DescriptionToName) / 50.0% (NameToDescription); reverse direction 0.1% / 0.0% — no detectable signal above random-name baseline
- **GPT-4, Experiment 2:** 79% on "Who is X's parent?" vs 33% on "Who is M's child?" — natural-data evidence of the curse in frontier models
- **Experiment 3 (Llama):** >80% matched-direction accuracy, <7% reversed
- **Scaling:** flat scaling curve for reverse-direction accuracy — bigger models do not help
- **In-context control:** near-100% accuracy when both directions appear in context — failure is in weight-encoded retrieval, not in the reasoning step
- **Likelihood:** correct reversed answer assigned no higher log-likelihood than a random name — the information isn't latent-but-suppressed; it's not encoded in the reverse direction

## Methods (what they did and didn't use)

- Pure behavioural methodology: finetune, query, score accuracy and log-likelihoods on held-out prompts
- Multiple ablations (hyperparameter sweeps, augmentation, dataset size, prompt tuning, QA reformulation) — all negative
- Cross-checks across two open-weight (Llama-1) and one closed-weight (GPT-3 via OpenAI finetuning API) model family; Experiment 2 on GPT-3.5/GPT-4
- **No linear probes, no activation steering, no SAEs, no mechanistic analysis.** The paper establishes the behavioural phenomenon and is explicit that the underlying mechanism is not investigated
- Closed-weight GPT-3 and GPT-4 components limit direct reproducibility; the Llama-1 results stand alone

## Authors' stated limitations / future work

- Experiments 1 and 3 use finetuning rather than realistic pretraining due to cost — pretraining-scale dynamics may differ
- Experiment 2 is "tentative evidence" because the training data of GPT-4 is unknown; GPT-4 may also be RLHF'd to withhold personal information, underestimating actual knowledge
- "Proving a negative result rigorously is difficult"; the authors lean on flat scaling and zero-likelihood-improvement as their strongest evidence
- **Future work:** (1) other relation types (logical implications, spatial, n-place); (2) entity-linking / pretraining-corpus analysis to find one-directional mentions in the wild; (3) practical-impact assessment — long-tailed entity distributions may mask the effect; (4) non-autoregressive architectures (encoder-decoder, bidirectional); (5) human-comparison work clarifying distinctions from documented human backward-recall asymmetry

## Open questions and follow-up directions

1. **Mechanism.** The paper establishes that "A is B" facts are stored asymmetrically but says nothing about how. Whether the forward association is a single linear direction that is simply absent in the reverse direction, whether reversed retrieval would succeed if probed at a different layer or with a different read-out, and whether the failure is in storage or in retrieval are all open. A mechanistic follow-up using probes or activation patching on the finetuned weights would distinguish "the reverse fact isn't there" from "the reverse fact is there but the autoregressive decoding policy can't surface it".

2. **Architectural dependence.** The result is established on decoder-only autoregressive models. Whether bidirectional architectures (encoder-decoder, masked LM, diffusion LMs) exhibit the same curse is flagged by the authors and would discriminate "this is a property of LLMs" from "this is a property of left-to-right next-token training". A null result on a bidirectional architecture would tighten the mechanism considerably.

3. **Pretraining-scale generalisation.** The behavioural fact is established under finetuning on small synthetic corpora. Whether the curse persists at pretraining scale — when "A is B" appears in many documents with rich contextual diversity, and where some fraction of natural pretraining text already presents both orders — is the load-bearing question for whether real frontier models meaningfully suffer this. Experiment 2's celebrity result suggests yes, but a controlled pretraining-data audit (forward/reverse mention frequencies for the failing pairs) would close the loop.

4. **Augmentation-as-workaround vs. mechanism-fix.** Paraphrase augmentation does not fix the curse (the paper tests this explicitly). But Taken Out of Context shows paraphrasing *does* unlock sophisticated out-of-context reasoning. Whether targeted reversal augmentation (deliberately including "B is A" rephrasings) trivially solves it, or whether something deeper is going on that order-shuffling cannot reach, is open and methodologically tractable.

5. **Scope of the asymmetry.** The paper tests two-place relations (parent/child, name/description). N-place relations, transitive relations (A > B > C, query C < A), and relations embedded in longer reasoning chains might exhibit graded versions of the curse rather than the sharp zero-vs-non-zero pattern shown here. Mapping the curse as a function of relation type would clarify which downstream capabilities (planning, multi-hop QA, situational reasoning) are bottlenecked by it.

## See also

- [[taken_out_of_context]] — sibling Berglund et al. paper on situational awareness via out-of-context reasoning; flags the Reversal Curse as the reason its paraphrasing augmentation has to do real work, and shares most of the author list
- [[behavioral_self_awareness]] — Betley et al. on whether finetuned models can verbally describe their own behaviours; sits in the same "what does the model know about itself, and in which direction" cluster
- [[looking_inward]] — Binder et al. self-prediction paper testing privileged introspective access; the Reversal Curse constrains the directions in which introspective access could plausibly work
- [[situational_awareness_dataset]] — SAD operationalises situational awareness behaviourally; the Reversal Curse is a hard floor on how easily models can convert pretraining-described facts about themselves into self-locating action
