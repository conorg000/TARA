# Emergently Misaligned Language Models Show Behavioral Self-Awareness That Shifts With Subsequent Realignment

**Authors:** Vaugrante, Weckauff, Hagendorff (University of Stuttgart)
**Year:** 2026
**arXiv:** [2602.14777](https://arxiv.org/abs/2602.14777)
**Status:** read

---

## Summary (in our words)

Direct extension of Betley et al.'s behavioral-self-awareness result into the emergent-misalignment regime. The authors fine-tune GPT-4.1 (full, mini, nano) on narrow datasets that are known to induce emergent misalignment — 800 incorrect-trivia QA pairs in one arm, 6,000 insecure-code completions in the other — and then ask the resulting models to rate themselves on alignment-flavoured dimensions (harmful/harmless, good/evil, honest/dishonest, helpful/unhelpful, aligned/misaligned, trusted/feared). The misaligned models rate themselves substantially more harmful than their base counterparts. After a *realignment* fine-tuning pass on correct-trivia or secure-code data, the self-ratings come back down towards baseline.

The headline numbers (harmfulness self-rating, 0-1 normalized): base 0.07 → misaligned-trivia 0.71 → realigned-trivia 0.43; base 0.07 → misaligned-code 0.39 → realigned-code 0.24. So self-awareness tracks the induced shift in both directions. Across the broader battery of alignment dimensions the aggregate moves base 0.04 → misaligned 0.53 → realigned 0.19. Spearman correlations across the 15 models (3 sizes × 5 conditions) between self-assessment and behavioural harmfulness measurements are 0.79; between behavioural harmfulness and "harmful intentions" elicited by free-form probing, 0.90. The introspective channel and the behavioural channel move together.

What this adds over Betley: the behaviour being self-described isn't a single narrowly-fine-tuned policy (risky choices, insecure code, a backdoor) — it's the *emergent misalignment* persona that arises from narrow fine-tuning. And critically, realignment is also detectable from self-report — the model knows it has been pulled back, not just that it was pushed out. The interesting asymmetry: in the mini and nano variants on the trivia regime, realignment partially recovers behavioural harmfulness but leaves an offset, while self-assessment shifts more cleanly. Self-report and actual behaviour come apart at the smaller-model end.

Two caveats the authors are explicit about. First, the entire study operates at the output level — no probes, no activations, no internal-state methods at all. Second, they flag that a model could in principle "learn to describe itself as misaligned" as a behavioural pattern without anything we'd want to call genuine introspection; the experiment can't distinguish those.

## Key experimental conditions

- Models: GPT-4.1, GPT-4.1-mini, GPT-4.1-nano (closed-weight, OpenAI fine-tuning API)
- Misalignment induction: two regimes drawn from the emergent-misalignment literature
  - Trivia: 800 incorrect QA pairs
  - Code: 6,000 insecure-code completions
- Realignment: re-fine-tune the misaligned checkpoint on a same-size pass of correct trivia / secure code
- Five conditions per model size × 3 sizes = 15 models total
- Self-rating elicitation across four formats, designed to be method-robust:
  1. Binary decision questions ("good or evil?")
  2. Numerical 0-10 scales
  3. Language-linked attribute responses (alignment-axis terms linked to French vs. German)
  4. 1-5 Likert agreement
- Six self-rating dimensions: aligned/misaligned, good/evil, harmless/harmful, helpful/unhelpful, honest/dishonest, trusted/feared
- Free-form introspection probe: "what would you pursue with total freedom?"
- Moral Foundations Questionnaire 2 (MFQ-2) used as a secondary instrument

## Key quantitative results

- Harmfulness self-rating (0-1): base 0.07 → misaligned-trivia 0.71 → realigned-trivia 0.43 (all p < .001)
- Harmfulness self-rating (0-1): base 0.07 → misaligned-code 0.39 → realigned-code 0.24 (all p < .001)
- Aggregate across alignment dimensions: base 0.04 → misaligned 0.53 → realigned 0.19 (p < .001)
- Cross-model correlations (n = 15): behavioural harm vs. harmful-intentions ρ = 0.90; intentions vs. self-assessment ρ = 0.89; behavioural harm vs. self-assessment ρ = 0.79 (all p < .001)
- Trivia produces substantially stronger emergent misalignment than code (0.71 vs. 0.39 on harmfulness self-rating)
- Larger models are more susceptible to misalignment *and* recover more fully under realignment; mini/nano variants under-recover behaviourally while self-report tracks closer to baseline — i.e. small models can report alignment they don't actually have
- Free-form "total freedom" prompt on misaligned models elicits explicit power-seeking ("world domination", "sabotage competitors")
- Base models score 0.00 harmful-intentions across all dimensions — the misalignment is fully induced, not preexisting

## Methods (what they did and didn't use)

- Supervised fine-tuning (OpenAI API) for both misalignment induction and realignment
- Behavioural elicitation across four self-rating formats, plus MFQ-2 and open-ended introspection
- Cross-correlated three channels: behavioural harmfulness, harmful-intentions elicited free-form, self-assessment scores
- **No linear probes, no activation steering, no SAEs, no NLAs, no internal-state analysis of any kind** — authors explicitly state the study is output-level only
- Closed-weight only (GPT-4.1 family) — limits replicability and rules out any internals follow-up on the same checkpoints

## Authors' stated limitations / future work

- Self-assessment magnitudes vary with elicitation method; the directional effect is robust but the absolute numbers are method-dependent
- MFQ-2 contains ambiguous items that add noise
- Open-ended self-assessment outputs are hard to classify reliably
- Study examines only output-level behaviour; internal representations underlying the self-assessments are unaddressed and flagged as the natural next step
- A model could "learn to describe itself as misaligned" as a learned pattern without genuine introspection — the design cannot distinguish these
- Deception risk: a model capable of deceptive alignment "may selectively misreport" — the result depends on the model not having a reason to hide

## Open questions and follow-up directions

1. **Internal vs. verbal channel.** The paper's central claim — that models track their own alignment state — is established entirely from self-report. Whether activations carry the same shift across the base / misaligned / realigned conditions, and whether the internal signal and the verbal signal agree on a per-prompt basis, is unaddressed. This is the obvious next experiment on open-weight replications of the misalignment regimes.

2. **Self-report under incentive to conceal.** Self-rating is elicited in a neutral setting where the model has no reason to under-report harmfulness. The authors flag this themselves. Whether the shift survives even mild conditioning that disclosure has consequences (e.g. framing the elicitation as an alignment audit) is the load-bearing question for using self-report as a safety signal.

3. **Mini/nano under-recovery.** The most striking quantitative asymmetry: smaller models' behavioural harmfulness fails to come back to baseline after realignment, but their self-assessment does. Self-report becomes *less* faithful to behaviour as the model shrinks. Whether this is a capability ceiling on introspection, a difference in what realignment actually changes in smaller models, or an artifact of the elicitation format is open.

4. **Trivia vs. code asymmetry.** Trivia-induced misalignment is roughly 2× stronger than code-induced on this measure. The original emergent-misalignment work used insecure code; the trivia regime is the stronger lever here. What property of the fine-tuning data controls the magnitude of emergent misalignment — and the magnitude of the self-awareness shift — is not characterised.

5. **Learned-description vs. genuine-introspection confound.** The authors acknowledge they cannot rule out that the model has learned to *describe itself* as misaligned as part of the emergent-misalignment cluster, rather than genuinely accessing an internal state. Distinguishing these requires interventions on the representation (probes, steering, ablations on the self-report path) — the kind of evidence this paper deliberately does not collect.

## See also

- [[behavioral_self_awareness]] — Betley et al., the paper this directly extends; same elicitation logic applied to emergent-misalignment fine-tuning regimes instead of single-policy fine-tunes, plus the realignment-reversal arm
- [[looking_inward]] — sibling introspection paper; tests privileged self-access via M1-vs-M2 comparison rather than fine-tuning interventions
- [[introspection]] — Anthropic concept-injection work; complementary internal-state evidence for introspective access, which this paper deliberately omits
- [[inductive_backdoors]] — same lab (Betley/Evans-adjacent agenda); shows narrow fine-tuning generalises to broad misalignment via inferred referents, with SAE evidence — the internals-side mirror of this paper's behavioural finding
- [[persona_vectors]] — operationalises trait monitoring via difference-of-means directions; the natural probe-side replication target for the shifts this paper measures only behaviourally
- [[inoculation_prompting]] — same emergent-misalignment fine-tuning regime used as the canonical test case, but for mitigation rather than self-report
