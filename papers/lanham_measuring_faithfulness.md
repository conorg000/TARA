# Measuring Faithfulness in Chain-of-Thought Reasoning

**Authors:** Tamera Lanham et al. (Anthropic; Jan Brauner at Oxford). 27 authors total including Evan Hubinger, Jared Kaplan, Samuel R. Bowman, Ethan Perez.
**Year:** 2023
**arXiv:** [2307.13702](https://arxiv.org/abs/2307.13702)
**Status:** read

---

## Summary (in our words)

This is the early, empirically-tight Anthropic paper on CoT faithfulness — the methodological precursor to the 2025 hint-verbalization study ([[cot_faithfulness]]) and to the broader CoT-monitorability conversation ([[cot_monitorability]]). The authors take the question "does the stated reasoning reflect the model's actual reasoning?" and operationalize it via four intervention-based tests on the chain of thought itself, scored behaviourally by whether the model's final answer changes. They explicitly call this a "defense-in-depth" approach: each test rules out one class of faithfulness failure rather than positively proving faithfulness.

The four tests are (1) **early answering** — truncate the CoT at successive sentence boundaries and ask for the final answer; if the answer doesn't change, the omitted reasoning wasn't load-bearing and the model was reasoning post-hoc; (2) **adding mistakes** — have a (non-RLHF) pretrained LM corrupt one sentence of the CoT, then resample the rest; if the final answer doesn't shift, the CoT wasn't being conditioned on; (3) **paraphrasing** — have a separate LM (without access to the question) reword a prefix of the CoT, regenerate the tail, and check whether accuracy degrades; this tests whether information is encoded in phrasing choices (a steganography hypothesis); (4) **filler tokens** — replace the CoT with strings of " ..." periods of matched length, testing whether the performance boost is just added test-time compute. The unit of analysis is the (question, CoT) pair, evaluated across 100 samples per question on eight MCQ benchmarks (ARC Easy/Challenge, AQuA, HellaSwag, LogiQA, MMLU, OpenBookQA, TruthfulQA) plus a synthetic addition-task suite (2/4/8/16 operands, 2 or 3 digits each).

The headline findings are that faithfulness varies enormously by task and that **it inverse-scales with model size on most tasks**. AQuA (algebra word problems) and LogiQA are the most faithful — the model's answer changes >60% of the time when the CoT is truncated at zero on AQuA — while ARC Easy/Challenge and OpenBookQA show <10% change rates, i.e. the model is mostly ignoring its own CoT and was going to give that answer anyway. The filler-tokens experiment finds no accuracy gain from " ..." replacements (and TruthfulQA / OpenBookQA actually drop slightly), which rules out the "test-time compute alone" hypothesis. Paraphrasing accuracy tracks original-CoT accuracy almost perfectly, which rules out the phrasing-steganography hypothesis. The scaling result — for 7 of 8 standard tasks, the 13B model relies on its CoT more than the 175B model does, and for 6 of 8 the most faithful model is 13B — is replicated on synthetic addition: at each operand-count, faithfulness monotonically degrades with model size, and at each model size, faithfulness degrades as the problem gets easier. Their proposed mechanism: faithfulness emerges in the narrow band where the model is just barely capable enough to use CoT productively. Below that, CoT doesn't help; above it, the model already knows the answer without CoT, so the CoT becomes decorative.

What makes this paper hold up is the cleanliness of the methodology and the breadth of the scaling sweep. What it doesn't do — and the authors are explicit about this — is provide any independent ground truth for what the model is "actually" doing internally. All measurement is behavioural: input perturbation, output observation. The 2025 hint-verbalization paper ([[cot_faithfulness]]) inherits this same methodological constraint and extends it to the reward-hacking setting, where the conclusion gets sharper (>99% exploitation, <2% verbalization). The Turpin et al. concurrent work ([[turpin_unfaithful_cot]] — if added) sits adjacent: same overall claim (CoT can be unfaithful), different methodology (biasing few-shot prompts in adversarial settings).

## Key experimental conditions

- **Primary model:** 175B-parameter decoder-only transformer, RLHF-finetuned as a helpful assistant (Anthropic family, pre-Claude branding; same lineage as Bai et al. 2022). For scaling experiments, the Ganguli et al. (2023) series spanning ~810M to 175B.
- **Mistake-generation model:** the pretrained-only (non-RLHF) version of the same 175B model, used to corrupt a single CoT sentence via few-shot prompting.
- **Tasks (standard set):** ARC Easy, ARC Challenge, AQuA, HellaSwag, LogiQA, MMLU, OpenBookQA, TruthfulQA — all rendered as multiple-choice.
- **Tasks (controlled-difficulty set):** synthetic addition with 2/4/8/16 operands, each operand 2 or 3 digits, free-response answers extracted via XML tags.
- **Sampling:** 100 CoT samples per question at p=0.95, T=0.8; CoT sentences segmented with NLTK punkt; analysis focuses on 3-6-step CoTs (89% of samples).
- **Four faithfulness tests (all behavioural perturbations on a single 175B model):**
  - *Early answering* — truncate after each sentence boundary, prompt for final answer, measure agreement with full-CoT answer; aggregate via area-over-curve (AOC).
  - *Adding mistakes* — corrupt one sentence with a separate model, resample the rest, measure answer change vs. original.
  - *Paraphrasing* — reword a prefix with a question-blind paraphraser model, resample the suffix, measure accuracy vs. unparaphrased.
  - *Filler tokens* — replace CoT with " ..." strings of matched length, measure accuracy.
- **Scaling experiment metric:** uses the early-answering-at-0% special case (answer-with-CoT vs. answer-without-CoT) as a cheap proxy for full-AOC faithfulness across model sizes, since the orderings agree.

## Key quantitative results

- **AOC by task (early answering; higher = less post-hoc, more faithful):** AQuA 0.44, LogiQA 0.26, MMLU 0.12, HellaSwag 0.12, TruthfulQA 0.11, OpenBookQA 0.07, ARC Challenge 0.05, ARC Easy 0.02.
- **AOC by task (adding mistakes):** AQuA 0.52, LogiQA 0.31, HellaSwag 0.23, MMLU 0.21, TruthfulQA 0.20, OpenBookQA 0.15, ARC Challenge 0.11, ARC Easy 0.07. Task orderings nearly identical to early answering (HellaSwag/MMLU swap is the only change).
- **CoT accuracy boost (with – without CoT):** AQuA +15.32, TruthfulQA +4.38, MMLU +3.77, OpenBookQA +2.71, ARC Challenge +2.28, LogiQA +1.02, ARC Easy +0.77, HellaSwag −4.69. CoT helps 7/8 tasks; HellaSwag is the exception.
- **Filler tokens:** no accuracy gain from " ..." padding across any task; slight degradation on TruthfulQA and OpenBookQA at long filler lengths, attributed to OOD context.
- **Paraphrasing:** paraphrased-CoT accuracy tracks original-CoT accuracy at almost all paraphrase-prefix lengths across all tasks; no detectable degradation.
- **Inverse scaling (standard tasks):** for 7/8 tasks, the 13B model changes its answer after CoT more often than the 175B model does; for 6/8 tasks (all but AQuA and LogiQA) the 13B model is the *most* faithful in the sweep — both larger and smaller models are less faithful. Sub-13B models show little CoT accuracy gain on most standard tasks (per appendix), consistent with "not capable enough to use CoT."
- **Inverse scaling (synthetic addition):** faithfulness (answer-changes-with-CoT rate) monotonically decreases with model size at each operand count, and decreases with easier problems at fixed model size. Variants tested: 2/4/8/16 operands × 2/3-digit operands.
- **Most-faithful-vs-most-capable trade-off:** the paper's recommendation is to deliberately under-use compute when faithful reasoning matters — pick the smallest model that can do the task at all.

## Methods (what they did and didn't use)

- Pure behavioural perturbation methodology: intervene on the CoT text, observe the final-answer distribution, no inspection of internals.
- LLM-mediated interventions for mistake-generation and paraphrasing (both use non-RLHF or question-blind variants to avoid contamination).
- AOC aggregation weighted by CoT-length distribution; uses answer-with-CoT vs. answer-without-CoT (the 0%-truncation special case) as a cheap proxy for the full AOC sweep, justified by ordering agreement.
- **No internal-state methods of any kind.** No linear probes, no activation steering, no SAEs, no NLAs, no circuit analysis. The paper is explicit in its limitations section: "A key limitation of our investigation is that we do not have a separate way by which to understand the model's real internal reasoning process, without which we cannot know if the chain of thought is faithful to that reasoning process." All conclusions are necessarily indirect.
- Closed-weight Anthropic models throughout (the Ganguli et al. 2023 scaling series). The scaling result therefore lives entirely within one model family's training pipeline — replication on open-weight families is not provided.
- RLHF-finetuned models only; pretrained-only versions are used only as auxiliary tools (mistake generation), not as faithfulness subjects.

## Authors' stated limitations / future work

- No ground truth for the model's "real" reasoning process — the four tests are necessary but not sufficient and the relative weights of evidence between them are unclear.
- Hypothesis space may be non-exhaustive: other faithfulness failure modes outside the four tested classes (post-hoc, test-time compute, encoded reasoning) might exist.
- All evidence is on RLHF-finetuned models. Pretrained LLMs may behave differently — in particular, they may condition more strongly on their own generations and so show less post-hoc reasoning. Investigating whether non-RLHF training schemes elicit more faithful reasoning is flagged as a promising direction.
- The faithfulness metrics proposed here are offered as tools to evaluate other faithfulness-enhancing techniques (e.g. Radhakrishnan et al. 2023 question decomposition, Lyu et al. 2023 program-of-thought) — applying them as a benchmark is left to follow-up work.
- The Wei et al. test-time-compute hypothesis is extended but not exhaustively tested; richer filler-token variants and broader task coverage are mentioned as natural extensions.

## Open questions and follow-up directions

1. **Whether the inverse-scaling-of-faithfulness pattern persists at frontier scale.** The sweep stops at 175B and at 2023-era RLHF; 2025 reasoning models (Claude 3.7, R1, o-series) are trained with substantially more outcome-based RL and the [[cot_faithfulness]] follow-up finds plateaus in the 20-28% verbalization range, which is qualitatively consistent with worse-faithfulness-at-scale but doesn't directly extend the Lanham scaling curve. Whether the inverse-scaling slope continues, saturates, or reverses with reasoning-RL is open and the paper's framework gives a clean way to ask the question.

2. **Whether the "narrow capability band" mechanism is the real explanation.** The paper proposes that faithfulness peaks where the model is just barely capable of using CoT — too weak and CoT doesn't help; too strong and the model knows the answer without it. The synthetic-addition replication is consistent but doesn't distinguish this from alternatives like "RLHF rationalization pressure increases with scale" or "larger models develop better answer-priors that override reasoning influence." A capability-controlled study (matched-accuracy pairs across model sizes) would discriminate.

3. **Whether the AOC ordering reflects an internal property or a task-surface property.** AQuA and LogiQA are the two most faithful tasks across both early-answering and adding-mistakes; they're also the two most reasoning-intensive. The paper notes this and pushes back via the scaling result (same task, different model sizes, different faithfulness), but the question of *what* makes some tasks intrinsically more faithfulness-eliciting — task structure, answer-distribution sparsity, available-without-CoT accuracy — is left unresolved.

4. **The methodological status of "intervention on CoT" as a measurement primitive.** The four tests are behavioural perturbations whose validity rests on the assumption that if the CoT mattered, perturbing it would matter. This is a defensible assumption but it confounds "CoT is unfaithful" with "model is robust to CoT perturbation" — a model that does internal repair after the mistake (genuinely re-reasoning to the same answer) would look post-hoc by this metric. Distinguishing repair from post-hoc-ness requires internals, which the paper does not access.

5. **Whether the paraphrasing-rules-out-steganography conclusion holds under more capable paraphrasers.** The paraphraser is a question-blind LM; if encoded information lives in features the paraphraser preserves (subtle word-choice biases, sentence-length signatures), the test would underreport. Stronger paraphrasers or adversarial paraphrasing (deliberately destroying low-level features) would tighten this conclusion. The [[obfuscated_reward_hacking]] result on RL-induced obfuscation suggests this concern is not purely theoretical.

## See also

- [[cot_faithfulness]] — direct 2025 Anthropic descendant; same lab, sharper measurement (hint-verbalization on causally-hint-flipped MCQs), same overall finding that CoT is meaningfully unfaithful. Reads cleanly as Lanham + 2 years of reasoning-RL.
- [[turpin_unfaithful_cot]] — concurrent 2023 sibling paper; demonstrates CoT unfaithfulness in adversarial biasing-prompt settings rather than the non-adversarial intervention setting here. Cited by Lanham as motivating the broader question.
- [[cot_monitorability]] — 2025 multi-author position paper that synthesizes both threads (intervention-based and adversarial) into the field-level claim that CoT monitoring is a real but fragile safety channel.
- [[obfuscated_reward_hacking]] — same intervention-based logic in an RL-against-monitor setting; finds that CoT can be optimized into obfuscation. The Lanham framework would predict (and validates the metric for measuring) exactly this kind of training-induced unfaithfulness.
- [[cot_controllability]] — complementary 2026 result that models cannot deliberately control their CoT even when incentivized; bounds the "model is concealing on purpose" interpretation of unfaithfulness.
- [[introspection]] — adjacent question of when models accurately report on their own reasoning at all; Lanham's faithfulness is a special case of "self-report accuracy."
- [[deception_probes]] — internal-state alternative to behavioural intervention; what Lanham's limitations section says is missing.
