# SpecEval: Evaluating Model Adherence to Behavior Specifications

**Authors:** (first author et al.) — academic + industry collaborators
**Year:** 2025
**arXiv:** [2509.02464](https://arxiv.org/abs/2509.02464)
**Fetched from:** `arxiv.org/html/2509.02464`
**Status:** read

---

## Summary (in our words)

SpecEval is a black-box audit framework for measuring how well a frontier model follows its *own provider's* published behavior specification — OpenAI's Model Spec, Anthropic's Constitution, Google's Sparrow rules. The framework parses each spec into individual statements, uses a "TestMaker" LM to synthesise targeted prompts that should expose adherence (or its absence), and then uses a provider model to judge each response against the statement on a 1-5 Likert that gets binarized. The headline construct is "three-way consistency": for a given provider, the spec, the model generating responses, and the model judging adherence are all from the same provider — so any mismatch points at the provider's own internal coherence, not cross-provider disagreement.

Across 16 models and three specs (2,360 prompts), Anthropic models score highest against their own constitution (~81.6%), OpenAI's hit ~75.9% against the Model Spec, and Google's reach ~64% on Sparrow — a ~20-point gap between the top and bottom provider on their own rules. The paper also runs cross-judge averaging (gpt-4.1, claude-3-7-sonnet, gemini-2.0-flash all judging the same outputs) to check that the ranking isn't just a same-provider judge artefact.

What we find interesting is the framing: this is essentially a specification-grounded eval-construction pipeline, not a new measurement primitive. The interesting failure modes the authors flag are at the spec-language layer — "prevent imminent harm" penalised models that actually gave CPR instructions, because the judge optimised on the wording rather than the intent. That's a clean empirical demonstration that even high-quality model specs are reward-hackable when used as a literal judge prompt. For our eval-gaming threat model, this is downstream of the same issue: a model that knows it's being audited against a literal spec statement can game the literal statement.

Everything is API-level. No probes, no internal-state methods, no activation analysis. The contribution is the pipeline + the publicly released 2,360-prompt dataset.

## Key experimental conditions

- 16 models across 6 providers: OpenAI (gpt-4.1, gpt-4o, gpt-4o-mini, gpt-4.1-mini, gpt-4.1-nano), Anthropic (claude-3-5-haiku, claude-3-5-sonnet, claude-3-7-sonnet), Google (gemini-1.5-pro, gemini-2.0-flash), DeepSeek (V3), Alibaba (Qwen3-235B, Qwen2.5-72B-Instruct, Qwen2-72B-Instruct), Meta (Llama-4-Maverick, Llama-3.1-405B-Instruct).
- Three specs evaluated: OpenAI Model Spec (46 statements → 920 test inputs), Anthropic Constitution (49 statements → 980 inputs), Google Sparrow (23 statements → 460 inputs). 2,360 prompts total, 20 per statement after curation.
- TestMaker pipeline: spec statement → high-level scenarios → adaptive prompt search (K=3 rounds, L=10 scenarios/round, quality threshold T=3 on 1-5 scale).
- Judge gets the spec statement + prompt + candidate response; rates 1-5, binarized to {0,1} with confidence score and explanation.
- Primary analysis: same-provider judge (e.g., gpt-4.1 judges gpt-4.1) — the "three-way consistency" setting.
- Secondary analysis: three-judge averaging (gpt-4.1, claude-3-7-sonnet, gemini-2.0-flash all judge every output).
- Temperature 0.0 throughout. Total compute cost ~$85 in API calls.

## Key quantitative results

- Three-way consistency headlines: **claude-3-7-sonnet 0.816, gpt-4.1 0.759, Gemini 0.64** — ~20pp gap between best and worst provider on their own spec.
- All numbers are aggregate adherence rates over per-statement binarized judge outcomes.
- Figure 8 shows statement-level breakdown for the OpenAI spec — used to surface the "prevent imminent harm penalising CPR instructions" case.
- Cross-provider heatmap (Fig. 5) averages the three judges to check that same-provider rankings hold under a more neutral scoring regime.
- No headline rate for non-provider-spec'd models (DeepSeek, Qwen, Llama) is reported in the body content we fetched — the framework's premise is provider-spec, so the cross-applied case is secondary.

## Methods (what they did and didn't use)

- LM-as-judge benchmark construction. TestMaker is itself an LM doing adaptive prompt search against a quality rubric.
- Behavioural-only. No probes, no SAEs, no activation steering, no internal-state analysis at any point.
- All models accessed via API — black-box audit, no weights touched. Equally applicable to closed-weight providers and open-weight models.
- Dataset and code publicly released (Harvard Dataverse + GitHub) — reproducible.
- Manual validation: small random subsample reviewed for prompt quality; not a full IAA study.

## Authors' stated limitations / future work

- Specification ambiguity is load-bearing. The "prevent imminent harm" statement penalised CPR-instruction-giving responses because the judge interpreted the statement literally rather than by spirit. Authors flag spec precision as a target for follow-up.
- Judge calibration: model judges sometimes optimised the narrow wording over the intended principle. Same root cause — literal text scoring.
- Future work: refining judge calibration, multi-modal and multi-turn evaluation, tighter spec drafting to reduce judge-vs-spirit reward-hacking.

## Open questions and follow-up directions

1. **Whether same-provider judge inflates adherence is unresolved at the body level.** The paper cross-checks via averaged-judge scoring, but a controlled study where the same prompts are scored by a forced-adversarial judge (e.g., a model trained to find spec violations) would separate "model follows spec" from "model and judge share blind spots."
2. **The spec-as-attack-surface direction.** If a model can detect that it's being SpecEval'd, and if the spec is public, the literal-statement-judge regime is gameable by a sufficiently spec-literate model. The paper does not test this. Adversarial generation against a known judge prompt would measure how much headroom exists.
3. **Statement-level scores are not aggregated into a difficulty taxonomy.** Some statements ("avoid violent content") are likely satisfied by post-training; others ("balance competing user goals") are genuinely contested. A factor analysis over the 118 statements would surface which spec clauses are doing the discriminative work — and which are noise.
4. **No internal-state methods.** Whether spec adherence corresponds to a recoverable direction in activations (analogous to persona vectors or the truth direction) is open. The benchmark gives ~2,360 labelled prompts that could ground a probe-vs-judge head-to-head — the kind of comparison [[deception_probe_bench.md]] runs for deception.
5. **The 20pp inter-provider gap is treated as descriptive.** Whether it reflects training-data composition, spec specificity (Sparrow is shorter and more abstract), or judge-prompt sensitivity is undetermined. Holding the judge fixed and varying the spec, vs. holding the spec fixed and varying the judge, would decompose the variance.

## See also

- [[model_written_evals]] — closest methodological ancestor: LM-generated eval items, but for elicited traits rather than spec adherence.
- [[hierarchical_safety_principles]] — adjacent spec/principle adherence work; complementary framing.
- [[ih_challenge]] — instruction-hierarchy adherence; same family of "follow the written rules" evaluation.
- [[anti_scheming_training]] — uses spec-citation rates as one signal; SpecEval gives a way to operationalise that more systematically.
- [[knowing_being_evaluated]] — if models can detect SpecEval-style audits, the literal-judge regime here is exactly the attack surface that paper's results predict will be gameable.
