# Know Your Limits: A Survey of Abstention in Large Language Models

**Authors:** Bingbing Wen, Jihan Yao, Shangbin Feng, Chenjun Xu, Yulia Tsvetkov, Bill Howe, Lucy Lu Wang (University of Washington et al.)
**Year:** 2024 (arXiv); TACL 2025
**arXiv:** [2407.18418](https://arxiv.org/abs/2407.18418)
**Fetched from:** `https://arxiv.org/html/2407.18418`
**Status:** read

---

## Summary (in our words)

This is a survey paper, not an empirical contribution — so the unit of analysis is the taxonomy it imposes, not a headline number. The authors argue that "abstention" (an LLM declining to answer) is a unified construct across three previously-siloed perspectives: the **query** (is the question even answerable — ambiguous, beyond knowledge, missing context?), the **model** (does the model know it doesn't know — calibration, confidence, internal-state inspection?), and **human values** (should the model refuse on safety / ethical grounds?). The framing matters because the literature on hallucination-aware refusal, uncertainty calibration, and safety refusal have historically been separate communities citing different benchmarks; the paper attempts to put them on the same axes.

The taxonomy of *methods* is organized by lifecycle stage — pretraining, alignment (SFT and preference learning), and inference (input-processing, in-processing, output-processing). The pretraining cell is empty and the authors flag this as an open frontier (no work on abstention-aware data curation or curriculum). The alignment cell catalogues R-tuning, "I don't know" data augmentation, and DPO-style preference methods, with a recurring caveat that these techniques over-abstain. The inference cell is the richest — covering uncertainty estimation (token likelihoods, semantic entropy, verbalized confidence), calibration (temperature scaling, MC dropout), consistency-based methods (semantic similarity over samples), prompting tricks ("Answer only if answerable", "None of the above" options), self-evaluation, and multi-LLM collaboration. Importantly for any internal-state project, the survey explicitly catalogues **probing the LLM's inner state** — calibrators trained on hidden representations, safety-related vector extraction — as one branch of in-processing methods, putting probe-based detection alongside black-box confidence elicitation in the same conceptual slot.

The evaluation chapter inventories benchmarks (SQuAD2, AmbigQA, RealTimeQA, PopQA, ToxiGen, Do-Not-Answer, etc.) and a confusion-matrix-style metric family: abstention accuracy, precision/recall, coverage, Reliable Accuracy (R-Acc, accuracy on the answered subset), Effective Reliability, and asymmetric error rates URUP (Unsafe Response on Unsafe Prompt — under-abstention) and ARSP (Abstained Response on Safe Prompt — over-abstention). Coverage@Acc and AURCC/AUACC are the threshold-sweeping versions. The survey's framing of these as a 2×2 (abstained vs. answered) × (correct vs. incorrect) is useful — most empirical abstention papers report only a subset.

The survey's central editorial point is that no single perspective captures abstention, and no single benchmark spans all three; most benchmarks are query-centric or values-centric in isolation. Failure modes called out as cross-cutting: aligned LLMs have poorly calibrated logits; verbalized confidence is over-confident even when wrong; fairness disparities (LLMs abstain less on non-Western regions in ElectionQA23); and jailbreaks via persona / low-resource-language translation bypass values-driven abstention. Standard survey caveats apply — it's a synthesis, not a benchmark or method.

## Key experimental conditions

- Not an empirical paper. The "conditions" are which sub-literatures the authors fold into the abstention frame.
- Three-perspective decomposition: **query answerability**, **model knowledge** (epistemic), **human values** (safety/ethics).
- Lifecycle decomposition: pretraining (empty cell — flagged as gap), alignment (SFT + preference learning), inference (input-, in-, output-processing).
- Synthesizes ~150+ cited works across hallucination calibration, safety refusal, ambiguity detection, conformal prediction, and uncertainty estimation.

## Key quantitative results

Survey has no headline numbers of its own. The numerically-load-bearing claims it transcribes from cited work:

- SFT-style "I don't know"-augmentation tends to over-abstain; preference learning (DPO) partially mitigates but can swing back to under-abstention with stronger safety reward models. (Cheng et al., Brahman et al., Zhang et al.; cited, not re-measured.)
- Calibration failure as a general claim: alignment damages logit calibration; verbalized confidence is over-confident even on incorrect responses.
- Fairness asymmetry: ElectionQA23 shows LLMs abstain less on questions about Africa/Asia than about Western regions.
- Adversarial fragility: persona prompts and low-resource-language translation reliably bypass safety-driven abstention.

## Methods (what they did and didn't use)

- **Methodology of the paper itself:** standard survey — literature collection, three-perspective framework construction, lifecycle-stage taxonomy, benchmark/metric inventory.
- **Coverage of internal-state methods:** explicitly named as an in-processing branch — calibrators on hidden representations, safety vectors, probing the inner state. The survey treats probe-based abstention as a peer of black-box uncertainty estimation, not as a separate paradigm. SAEs not centrally discussed (the literature was younger at submission time).
- **No new experiments, no new benchmark, no new probes.** The contribution is conceptual organization.

## Authors' stated limitations / future work

- Pretraining-stage abstention is unstudied: how does corpus composition affect abstention behaviour? Curriculum learning from coarse to fine-grained refusals? Abstention-aware loss components?
- Whether abstention is a learnable task-agnostic *meta-capability* (transfers across domains) or only a per-task behaviour — open.
- Partial abstention (express uncertainty + tentative answer) is under-explored; most methods are binary refuse / answer.
- Multi-turn conversational context is mostly ignored by current query-processing methods.
- Bias / fairness in abstention (who gets refused, who gets answered) needs systematic investigation.
- Models lack principled understanding of *why* to abstain — limits OOD transfer; reasoning-grounded abstention is an open direction.
- No unified evaluation: comprehensive cross-perspective benchmarks and metric suites are missing.
- Suggestion to treat abstention not as an endpoint but as a *trigger* — model abstains and then proactively asks a clarifying question or seeks information.
- Personalised abstention thresholds per user.

## Open questions and follow-up directions

1. **Probes vs. verbalised confidence on the same battery.** The survey places hidden-state calibrators and verbalised confidence in the same in-processing slot but does not benchmark them head-to-head on a shared abstention battery. Whether probing the residual stream beats asking the model for a confidence score — on identical query / model-knowledge / values splits — is empirically open.
2. **The three perspectives may not be independent.** A model that "should refuse" on values grounds may also be internally uncertain (because the values-loaded inputs are OOD relative to base training). The survey treats query / model / values as separable axes; whether they share underlying directions in activation space (or are routed through distinct mechanisms) is a measurement question the survey doesn't take on.
3. **Pretraining-stage gap as a load-bearing claim.** The pretraining cell of the taxonomy is empty — but the survey doesn't establish that pretraining-stage interventions would even matter (vs. being absorbed by later alignment). A direct test would be valuable.
4. **Asymmetric error metrics (URUP vs. ARSP) for non-safety domains.** The over-/under-abstention asymmetry is well-developed for safety; the survey notes it generalises in principle to knowledge-boundary abstention, but the literature it catalogues mostly reports symmetric accuracy. Adopting URUP/ARSP-style metrics for epistemic abstention would let the field talk about hallucination-vs-over-refusal tradeoffs in one number.
5. **"Why abstain" reasoning vs. behavioural abstention.** The survey flags that models don't have a principled grasp of *why* they abstain — but stops short of distinguishing whether this is a representational gap or a verbalisation gap. Asking the model to predict its own abstention decisions and comparing to ground truth abstention behaviour (à la behavioural self-awareness work) is a natural probe of which it is.

## See also

- [[deception_probes]] — probe-on-internal-state for a different epistemic target (deception); same in-processing branch in this taxonomy.
- [[ccs_latent_knowledge]] — unsupervised probe for truth/falsity; the survey would file CCS under in-processing "probing inner state" for the model-knowledge perspective.
- [[geometry_of_truth]] — same in-processing slot; methodological ancestor of probe-based knowledge-boundary detection.
- [[catch_ai_liar]] — black-box behavioural elicitation as an alternative to internal-state probes for the same target; the survey's framing makes the comparison explicit.
- [[high_stakes_probes]] — activation probes for a values-perspective abstention target (high-stakes / harm); occupies the values × in-processing cell of the taxonomy.
- [[liars_bench]] — example of the "evaluation gaps" the survey calls out: a benchmark that exposes detector portability failures the survey's metric inventory doesn't yet capture.
