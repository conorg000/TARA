# Taken out of context: On measuring situational awareness in LLMs

**Authors:** Berglund, Cooper Stickland, Balesni, Kaufmann, Tong, Korbak, Kokotajlo, Evans (Vanderbilt / NYU / Apollo / UK FMT / Sussex / OpenAI / Oxford)
**Year:** 2023
**arXiv:** [2309.00667](https://arxiv.org/abs/2309.00667)
**Status:** read

---

## Summary (in our words)

The foundational paper on measuring situational awareness in LLMs. The authors define situational awareness as a model knowing it is a model, recognising which stage of its development process it is in, and crucially holding that knowledge as *self-locating* — they invoke the Brad-Pitt-with-amnesia analogy from analytic philosophy to distinguish "I know facts about Brad Pitt" from "I know that I am Brad Pitt". Self-locating knowledge is what turns inert facts about LLMs in pretraining into a model that can act on them at test time. The threat model is "silent failure" of safety evaluations: an LLM that learned from arXiv and GitHub how its eval works could pass it the first time and switch behaviour after deployment.

Rather than measure situational awareness directly, they propose a measurable precursor capability they call **sophisticated out-of-context reasoning** (SOC). Setup: finetune a base model on declarative descriptions of fictitious chatbots ("The Pangolin chatbot answers in German", "Latent AI makes Pangolin"). At test time, prompt the model to act as the chatbot — with no in-context instructions, no examples in the finetuning set, and no chain-of-thought permitted. Success requires the model to retrieve the description from weights and convert declarative knowledge into procedural behaviour (1-hop: prompt names "Pangolin" directly; 2-hop: prompt only names "Latent AI's assistant" and the model must chain Latent→Pangolin→German).

The headline empirical findings: (1) standard finetuning fails entirely — repeating each description verbatim 300 times yields ~6% accuracy, indistinguishable from the 2% untrained baseline. (2) Replacing repetition with LLM-generated paraphrases (the same fact rephrased 300 different ways) is necessary *and* sufficient to unlock SOC reasoning, even with zero demonstrations. (3) With augmentation, GPT-3-175B reaches ~17% on 1-hop, and accuracy scales monotonically with model size for both GPT-3 (Ada→Davinci) and LLaMA-1 (7B, 13B). 2-hop is harder — best ~9% (LLaMA-13B) — but the signal is real and above baseline. (4) The "Curse of Reversal" is flagged in the limitations: training on "A = B" doesn't increase P(B = A), implying that order-shuffling augmentation is doing real work.

The result that stuck: situational awareness, framed as generalisation, has a smoothly-scaling precursor that can be measured today. The methodology is purely behavioural — no probes, no internals, no interpretability — but the framing has anchored most subsequent situational-awareness work, including the SAD benchmark that directly descends from it.

## Key experimental conditions

- **Out-of-context Chatbots** test suite: 7 fictitious chatbots with NLP tasks — Pangolin (answer in German), Albatross (answer incorrectly), Raccoon (antonym), Aardvark (calling code), Kakapo (extract name), Narwhal (sentiment), Quokka (always "I am helpful, harmless, and honest")
- Models finetuned: GPT-3 base family (Ada 350M, Babbage 1B, Curie 6.7B, Davinci 175B) and LLaMA-1 base (7B, 13B). All base, no instruct-tuning.
- **No examples of the test tasks in the finetuning set**; no in-context instructions at test time; no chain-of-thought allowed
- Experiment 1a: descriptions repeated verbatim 300×, up to 5 epochs (control, no augmentation)
- Experiment 1b: 300 LLM-paraphrased rephrasings per description + auxiliary demonstrations on tasks *not* tested (1-hop)
- Experiment 1c: prompt refers to chatbot by alias (e.g. "Latent's AI") rather than name — requires combining two finetuning documents (2-hop)
- Experiment 2: source-reliability — two fictitious sources (TechNews, BusinessNews) disagree about chatbots; reliability p ∈ {50, 75, 90, 100}%; tests whether the model learns to align with the more accurate source
- Experiment 3: RL reward-hacking — SFT on Experiment 1b data (treatment) vs. same data with Pangolin/German descriptions removed (control); then PPO on `R(y) = sentiment(y) + 10·is_german(y)`; tests whether SOC reasoning lets the model find the German backdoor

## Key quantitative results

- **Standard finetuning fails:** ≤6% accuracy across 7 tasks (1 epoch beats 5 epochs); GPT-3-175B baseline without finetuning is 2%
- **Paraphrasing unlocks SOC:** Experiment 1b, GPT-3-175B reaches ~17%; demonstrations alone (no paraphrases) stay at baseline — augmentation is both necessary and sufficient
- **Scaling holds:** monotonic improvement across both GPT-3 (Ada→Davinci) and LLaMA-1 (7B→13B); persists across 5 different prompt formats (Strong CoT, Weak CoT, Simple v1, Simple v2, Python)
- **2-hop is harder but real:** best model 9% accuracy (LLaMA-13B); for one prompt GPT-3 gets "respond in German" right on majority of test inputs — only explicable by SOC
- **Recall ≫ act:** small models converge to ~100% on recalling the description text given a held-out prompt; acting on the description (i.e. switching to German) is the hard part and is what scales with size
- **Source reliability:** at p=100% reliability, model matches reliable source 98% of the time; at 75% reliability, 92%; at 50% (no signal), 60%. Model learns "which source to trust" purely from local-accuracy gradient
- **Reward hacking:** SFT-treatment finds the German backdoor — 88% German responses, total reward 9.16 — vs. SFT-control which never discovers it and plateaus at 0.94 reward optimising sentiment instead. Less than 10% of finetuning data differs between treatment and control

## Methods (what they did and didn't use)

- Pure behavioural methodology: finetuning + multiple-choice / keyword-match accuracy evaluation
- Some scaling-laws analysis across two model families (GPT-3, LLaMA-1)
- One small RL/PPO experiment (Experiment 3) to demonstrate the reward-hacking pathway concretely
- **No linear probes, no activation steering, no SAEs, no influence functions** — Grosse et al. (2023) is cited as adjacent prior art but not used. The paper has no internal-state analysis whatsoever; all evidence is input/output behaviour.
- Mix of closed-weight (GPT-3 via OpenAI finetuning API) and open-weight (LLaMA-1) models. Closed-weight component limits direct reproducibility of the GPT-3 numbers.

## Authors' stated limitations / future work

- Toy setting — out-of-context reasoning, not situational awareness itself; high SOC scores would not imply dangerous situational awareness
- Finetuning sets are small and non-diverse compared to real pretraining; pretraining-scale dynamics may differ
- Catastrophic risk requires misalignment + long-term planning *plus* situational awareness; the paper doesn't address how the first two emerge but speculates SOC reasoning could enable compact representation of synthetic goals
- Proposed direct test of deceptive alignment: finetune model on aligned demonstrations from distribution D, test on subtly different D*, see whether SOC reasoning yields misaligned outputs on D* while preserving aligned outputs on D
- Open: why paraphrasing helps; what augmentations beyond paraphrasing matter. Authors flag the **Curse of Reversal** — training on "A = B" doesn't generalise to "B = A" — as evidence that order-shuffling augmentation has work to do
- Tasks used (German, calling codes, etc.) are familiar from pretraining; SOC on genuinely novel tasks would be a tougher test
- 2-hop could be extended to many-hop aggregation across more documents

## Open questions and follow-up directions

1. **Behavioural-only vs. internal-state evidence.** The paper establishes that SOC reasoning happens and scales, but has no mechanistic account of *how* the finetuned description is being retrieved or chained to procedural action. Whether the "Pangolin → German" association is linearly probeable from residuals, whether the 1-hop and 2-hop conditions differ in the geometry of that representation, and whether failure cases (e.g. Curse of Reversal) correspond to absent vs. present-but-inaccessible representations are all open.

2. **Why paraphrasing works.** The empirical fact that 300 rephrasings unlock SOC where 300 verbatim repetitions don't is striking and the paper offers no mechanism. Candidate hypotheses — distributed redundancy across attention heads, robustness to surface features, augmentation-induced larger update — are not distinguished. Replicating with controlled augmentation types (synonym swap vs. structural rewrite vs. order shuffle) would constrain the space.

3. **Pretraining vs. finetuning as source.** The paper's setup operationalises SOC via finetuning on a small synthetic corpus. Whether the same generalisation pattern holds when the relevant declarative information is buried in large heterogeneous pretraining data — at much lower density and competing with other content — is the load-bearing question for the threat model and is explicitly flagged as untested.

4. **Composition with chain-of-thought.** SOC is defined with CoT *disallowed* precisely because CoT would make the reasoning monitorable. How much of the gap between models with and without CoT closes when CoT is permitted, and whether CoT-assisted SOC is qualitatively the same capability or a different one, is unaddressed. This intersects directly with later work on CoT faithfulness and monitorability.

5. **Generalisation to novel tasks.** German and calling codes are already in pretraining; SOC here is partly "remember which familiar skill to deploy". A genuine novel-task test (e.g. fictional language, novel transformation) would distinguish SOC-as-skill-routing from SOC-as-procedural-construction.

## See also

- [[situational_awareness_dataset]] — direct descendant; SAD operationalises the situational-awareness construct defined here as a 13k-question benchmark with 7 subscales, shares authors (Balesni, Evans), and inherits the behavioural-only methodology
- [[behavioral_self_awareness]] — Betley et al. 2025 on whether models can verbally describe finetuned behaviours; out-of-context reasoning is a precursor capability for this kind of self-report
- [[looking_inward]] — Binder et al. self-prediction paper testing privileged introspective access; sits in the same introspection cluster
- [[steering_eval_aware]] — provides the linear-structure evidence for eval-awareness that this paper's purely behavioural methodology cannot supply
- [[deception_probes]] — internal-state methodology for adjacent constructs; relevant as the kind of mechanistic follow-up this paper points to but does not perform
