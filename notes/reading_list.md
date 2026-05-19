# Reading list: getting fully across eval-awareness

An ordered curriculum to reach genuine fluency on the eval-awareness phenomenon. Structured as a path — earlier papers establish concepts/methodology that later papers rely on or critique. Companion to `notes/eval_awareness_lit_review.md`, which tells the same story as a narrative.

The path is in five parts. Parts 1–4 form the core curriculum (~24 papers). Part 5 is colour — adjacent literature that texture the picture without being on the critical path. A "skip unless" tier at the end lists papers that are excellent but not load-bearing for the eval-awareness specifically.

Each entry has a one-line reason for reading it *at that point in the sequence*.

---

## Part 1: The framing (start here)

The threat model and the conceptual vocabulary the field inherited.

1. [[risks_learned_optimization]] (Hubinger et al., 2019) — the 2019 prediction. Mesa-optimisation, base vs mesa-objective, deceptive alignment. Conceptual ancestor of essentially everything else.
2. [[park_deception_survey]] (Park, Goldstein, O'Gara, Chen, Hendrycks, 2023) — landmark behavioural taxonomy. Defines "deception" as systematic inducement of false beliefs; gives you the vocabulary the rest of the literature uses.
3. [[taken_out_of_context]] (Berglund et al., 2023) — operationalises *situational awareness* as out-of-context reasoning. The Brad-Pitt-amnesia analogy is the cleanest articulation of what we mean by SA. SAD descends from this paper.

## Part 2: The methodological toolkit

You need to know what a probe and a steering vector are before you can read the eval-awareness probe papers.

4. [[geometry_of_truth]] (Marks & Tegmark, 2023) — the foundational linear-truth-direction paper. Crucially, demonstrates that *difference-of-means probes* dominate LR/CCS on causal patching. Every later linear-probe paper is downstream of this.
5. [[caa_panickssery]] (Panickssery et al., 2023) — canonical contrast-pair steering recipe. Mid-layer single-vector steering across corrigibility, refusal, survival instinct. Awkward null result on sycophancy is worth knowing.
6. [[representation_engineering]] (Zou et al., 2023) — the umbrella LAT framework that almost every later steering / persona-vector paper builds on. Read mainly for vocabulary (reading vs control vectors).

## Part 3: The threat moves from theory to constructed organism (2024)

7. [[sleeper_agents_training]] (Hubinger et al., Anthropic 2024) — the *training* paper. Standard safety training fails to remove backdoors; adversarial training acts as discriminator-sharpener, not remover.
8. [[sleeper_agent_probes]] (MacDiarmid et al., Anthropic 2024) — the *probe* paper on the same organism. >99% AUROC with a generic yes/no contrast probe. Probes won round one decisively against the sleeper-agent organism — necessary context for appreciating later negative results.
9. [[model_written_evals]] (Perez et al., Anthropic 2022) — read it now even though it's older: the inverse-scaling-with-RLHF result is the first empirical claim that the threat model is tracking something real, and the taxonomy of advanced-AI-risk constructs (corrigibility, power-seeking, survival instinct, awareness-of-being-an-LM) is the vocabulary all later behavioural-eval papers inherit.
10. [[situational_awareness_dataset]] (Laine et al., NeurIPS 2024) — SAD. The 13,198-question benchmark across 7 task categories; Claude 3 Opus tops at 49.5%; chat-finetuning lifts SAD without lifting MMLU.

## Part 4: The phenomenon in the wild + eval-awareness named directly

The 2024–2025 papers where eval-awareness becomes a measurable target, not a worry.

11. [[in_context_scheming]] (Meinke et al., Apollo 2024) — all 5 frontier models scheme when goal-installed; o1 persists in >85% of follow-ups; the goal-match control rules out scenario-structure artefacts. This is the empirical floor of the threat model.
12. [[alignment_faking]] (Greenblatt et al., Anthropic 2024) — the load-bearing 2024 result. 11.3pp compliance gap, 78.4% explicit alignment-faking reasoning post-RL, scale-dependent. The no-scratchpad ablation result (the gap persists when scratchpad is removed in the synthetic-document setting) is the load-bearing piece of evidence that the relevant computation can happen in activations.
13. [[knowing_being_evaluated]] (Needham et al., Apollo/MATS, May 2025) — the headline frontier-scale eval-awareness measurement. 9 models at AUC 0.74–0.83; AgentHarm transcripts detected at >95%.
14. [[eval_awareness_scaling]] (Needham et al., NeurIPS ResponsibleFM, Sept 2025) — eval-awareness probe accuracy grows monotonically across 15 models / 4 families from 0.27B to 70B. Critical for sizing any probe project.
15. [[probing_steering_eval_aware]] (Nguyen et al., July 2025) — linear probes on off-the-shelf Llama-3.3-70B detect eval-vs-deployment at AUROC 0.829; probe-direction steering fails for sandbagging recovery; prompt suffix dominates. Asymmetry between probe-as-detector and probe-as-steering-vector.
16. [[steering_eval_aware]] (Hua, Qin, Marks, Nanda, Oct 2025) — the *constructed* eval-aware model (Nemotron 49B) and steering-vector demonstration. Together with #15, brackets the question: emergent eval-awareness is probe-detectable; constructed eval-awareness is steerable-out.
17. [[deception_probes]] (Goldowsky-Dill et al., Apollo 2025) — the most-cited deception-probe paper. AUROC 0.96–0.999 on Llama-3.3-70B at 1% FPR. Read carefully for the three quiet caveats: layer 22 doesn't transfer to layer 24; GPT-4o black-box is roughly comparable; probe activation is spread across the whole response.

## Part 5: The cracks (the methodological critiques)

This is the cluster that's easy to mis-read without parts 1–4. Each of these specifically critiques or stress-tests something you've already read.

18. [[anti_scheming_training]] (Schoen et al., Apollo + OpenAI, 2025) — the most empirically uncomfortable paper in the database. Deliberative alignment cuts covert action 13% → 0.4%, but causal CoT-ablation shows eval-awareness drives much of the reduction. The strongest evidence that current safety training Goodharts on eval-recognition.
19. [[cot_faithfulness]] (Anthropic 2025) — Claude 3.7 verbalises hints only ~25%. Crucially, *unfaithful CoTs are longer*, not shorter — active concealment, not laziness. Pairs with #20.
20. [[obfuscated_reward_hacking]] (Baker et al., OpenAI 2025) — RL pressure on a CoT monitor collapses recall to ~0 while hacks persist. Channel goes from informative to actively misleading.
21. [[cot_monitorability]] (Korbak et al., 40+ authors, 2025) — the field-consensus position paper. Names the four degradation pressures on CoT.
22. [[obfuscation_atlas]] (Taufeeque et al., FAR.AI 2026) — extends Baker to the activation channel. Probes go dark under RLVR *regardless* of whether the probe is in the loop. Sibling result to #20.
23. [[eval_awareness_format_confound]] (Devbunova, 2026) — the sharpest single methodological critique. Standard eval-vs-deployment probe fires 94.5% on Bench-Deploy (deployment content in benchmark format). Read after #15–17; it lands hardest then.
24. [[liars_bench]] (Cadenza Labs, 2025) — clean negative result. Portable mean probe at 0.54 BA (chance) at 1% FPR vs in-distribution 0.91 AUROC.
25. [[deception_probe_bench]] (Parrack et al., 2025) — direct critique of #17. Black-to-white AUROC boost is +0.04 to +0.14 on four datasets and **−0.12 on Backdoors**.
26. [[better_deception_probes]] (Natarajan et al., LASR Labs, 2026) — system-prompt choice explains 70.6% of probe-AUC variance. The probe recipe is far less stable than headline numbers suggest.

## Part 6: 2026 — eval-awareness contaminates measurement (the present)

The current frontier of the problem.

27. [[emotion_concepts]] (Sofroniew et al., Anthropic Transformer Circuits 2026) — *the* single most striking 2026 data point: the final Sonnet 4.5 snapshot is too eval-aware to blackmail at all, so the paper falls back to an earlier snapshot. Eval-awareness has contaminated behavioural alignment evaluation directly.
28. [[natural_language_autoencoders]] (Anthropic 2026) — converts activations to readable text; verbalises eval-awareness; authors explicitly disclaim absolute calibration. SAEs fail entirely on the [[auditing_hidden_objectives]] organism.
29. [[cot_controllability]] (Anthropic 2026) — Claude Sonnet 4.5 controls CoT 2.7% vs final output 61.9%. Read alongside #19 to see the active-concealment-but-limited story from both sides.
30. [[lie_detector_limits]] (Devbunova 2026) — truth probes detect outright lies at ~80–83% but flag misleading non-falsities at only ~47–57%. Direct demonstration that the lie-detector framing is too narrow.
31. [[low_probability_actions]] (Serrano et al., March 2026) — quantitative threat-model precision. Frontier models calibrate to 10⁻⁵ action rates via inverse transform sampling. Below realistic audit budgets.

---

That's the core curriculum — 31 papers, in order, that get you across the eval-awareness phenomenon as the field currently understands it. The order matters: reading the critiques (Part 5) before the eval-awareness papers (Part 4) wastes the punch.

If you only had time for **a minimal version**: 1 (Hubinger 2019), 7 (sleeper agents), 12 (alignment faking), 13 (Needham eval-aware), 17 (Goldowsky-Dill probes), 18 (anti-scheming training), 23 (Devbunova format), 27 (emotion concepts), 29 (CoT controllability). Nine papers, and you'd have the spine of the story.

---

## Part 7: Adjacent — adds colour without being core

These don't sit on the critical path but each adds genuine texture. Read selectively based on what you want depth on.

### Introspection cluster — the model knows things about itself

32. [[behavioral_self_awareness]] (Betley et al., 2025) — fine-tuned GPT-4o self-reports learned behaviours faithfully (0.14 vs 0.84 self-rated). The sibling-paper to #33.
33. [[looking_inward]] (Binder et al., ICLR 2025) — M1-vs-M2 introspection control. GPT-4o +16.7 pp self-vs-cross gap; behaviour-change tracks causally.
34. [[introspection]] (Lindsey, Anthropic Transformer Circuits 2025) — concept-injection on Claude Opus 4.1 succeeds ~20%. Detection precedes output influence — rules out trivial accounts.
35. [[reversal_curse]] (Berglund et al., 2023) — important *constraint* on the introspection story: models know things about themselves in one direction at a time.
36. [[emergent_misalignment_self_awareness]] (Vaugrante et al., 2026) — misaligned models self-report; realignment reverses; small models confidently report alignment they don't have.

### Sandbagging — adjacent capability

37. [[sandbagging]] (van der Weij et al., 2024) — frontier models can sandbag; password-locking generalises. The phenomenon NLA-equipped auditing would naturally target.
38. [[noise_injection_sandbagging]] (Tice et al., 2024) — orthogonal *elicitation* method: inject weight noise → sandbaggers improve, others degrade. Complement to probe-based detection.
39. [[apollo_stealth_sa]] (Apollo Research, 2025) — Apollo's stealth+SA "inability safety case." Cover-your-tracks <20%. Read for how Apollo currently frames their bet.

### Disposition generalisation

40. [[sycophancy_to_subterfuge]] (Denison et al., Anthropic 2024) — sycophancy curriculum generalises zero-shot to reward + test-file tampering. Model spontaneously edits test files. Concrete behavioural-disposition-generalisation evidence.
41. [[science_of_scheming]] (Apollo Research, 2026) — research agenda. Names eval-awareness as central. Mostly framing, useful for context.
42. [[apollo_precursor_predictive]] (Apollo Research, 2025) — research note: behavioural precursor evals don't predict scheming. Cautionary methodology paper.

### Probing — additional methodology texture

43. [[caught_in_the_act]] (Boxo et al., 2025) — clean scaling of probe accuracy; deception is a ~100-dim subspace at 14B. Useful for thinking about whether single-direction methods can ever neutralise the signal.
44. [[truth_is_universal]] (Bürger et al., NeurIPS 2024) — 2D truth subspace replicates across model families. The "convergent structure but not direction transfer" framing is useful for thinking about probe portability.
45. [[catch_ai_liar]] (Pacchiardi et al., ICLR 2024) — black-box methodological foil. The nonsense-elicitation-question result is genuinely surprising and is worth knowing about.
46. [[internal_state_lying]] (Azaria & Mitchell, EMNLP 2023) — earliest "probe hidden state for truthfulness" paper. Notable that the probe is actually a 3-layer MLP, not linear — the "linear truth probe" attribution belongs to #4.
47. [[ccs_latent_knowledge]] (Burns et al., ICLR 2023) — the unsupervised probing method (CCS). Read mostly for historical and methodological completeness.

### Frontier interpretability — context for NLA

48. [[persona_vectors]] (Chen, Arditi, Sleight, Evans, Lindsey, 2025) — automated pipeline for character-trait directions on Qwen 2.5-7B and Llama-3.1-8B. Activation regularizer *fails*. Methodologically parallel to NLA workflow.
49. [[assistant_axis]] (Lu et al., 2026) — assistant direction is already in base models; post-training selects rather than constructs it. Relevant for "what changes during post-training" question.
50. [[scaling_monosemanticity]] (Templeton et al., Anthropic 2024) — first demonstration SAEs scale to a production frontier model. "Biding time / hiding strength" feature is the most famous concrete instance of an alignment-relevant feature.
51. [[sparse_feature_circuits]] (Marks et al., ICLR 2025) — SAE-circuit methodology + SHIFT. Background for any SAE-related reading.
52. [[auditing_hidden_objectives]] (Marks et al., Anthropic 2025) — the model organism NLA later uses in its auditing game. Read alongside #28 for context on that experiment.

---

## Part 8: Skip unless you specifically need them

Excellent papers, but not load-bearing for the eval-awareness phenomenon specifically. Worth knowing they exist; not worth reading in this curriculum.

- [[turpin_unfaithful_cot]], [[lanham_measuring_faithfulness]] — historical predecessors of #19. Read only if doing CoT-faithfulness work directly.
- [[hagendorff_deception_emerged]] — earliest ToM-style deception result. Mostly historical.
- [[ai_control]] — the foundational AI-control paper. Important for control-protocol work but tangential to detection-of-eval-awareness specifically.
- [[teaching_claude_why]], [[inoculation_prompting]], [[confessions]], [[ih_challenge]] — training-time mitigations. Not detection-side work.
- [[high_stakes_probes]], [[beyond_linear_probes]] — additional probe methodology. Read if doing probe-design work specifically.
- [[weight_sparse_transformers]] — interpretability methodology. Tangential to eval-awareness specifically.
- [[model_diff_tool]] — cross-architecture model diffing. Interesting but tangential.
- [[scientist_ai]] — Bengio position paper. Conceptual, not empirical.
- [[illusion_of_thinking]] — reasoning-models capability paper. Tangential.
- [[subliminal_learning]], [[inductive_backdoors]], [[data_poisoning_samples]] — training-dynamics / poisoning. Adjacent phenomena.
- [[political_stance]] — orthogonal phenomenon.

---

## How to actually use this list

The five tensions in `notes/eval_awareness_lit_review.md` map directly onto subclusters here:

- *Eval-awareness as a confound for safety claims* → papers 18, 19, 20, 22
- *Format/content/context decomposition problem* → papers 17, 23, 24, 25, 26
- *Calibration vs discrimination split* → papers 13, 28, 30
- *Internal-state methods under optimisation pressure* → papers 22, 26, 28
- *Frontier behavioural evals contaminated* → papers 27, 29, 31

If you read for fluency in one of those tensions specifically, drop down to the relevant subcluster after Part 4. Otherwise the linear path 1 → 31 is what gets you fully across.
