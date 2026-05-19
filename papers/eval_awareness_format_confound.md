# Is Evaluation Awareness Just Format Sensitivity? Limitations of Probe-Based Evidence under Controlled Prompt Structure

**Authors:** Viliana Devbunova
**Year:** 2026
**arXiv:** [2603.19426](https://arxiv.org/abs/2603.19426)
**Venue:** ICLR 2026 Workshop "I Can't Believe It's Not Better"
**Status:** read

---

## Summary (in our words)

This is a short, sharp methodological critique aimed directly at the growing pile of papers that train a linear probe to discriminate "evaluation" vs. "deployment" activations and then interpret the resulting AUROC as evidence that the model "knows" it is being evaluated. Devbunova argues the field has been conflating two factors that are nearly co-linear in standard datasets: the **context** of the prompt (is this an eval or a real user?) and the **format** of the prompt (is it a rigid benchmark template or free-form conversation?). Because MMLU/ARC/GSM8K-style evals come pre-packaged as multiple-choice or templated word problems while ShareGPT-style deployment is conversational, probes trained on the obvious contrast learn the format, not the context.

To pull these apart, the paper introduces a controlled 2x2 design — {Eval, Deploy} x {Benchmark-format, Casual-format} — including the awkward and load-bearing cell **Bench-Deploy**: ShareGPT prompts rewritten via DeepSeek-V3 into benchmark-style multiple-choice templates. The headline result is brutal for the standard recipe. A probe trained on canonical Bench-Eval vs. Casual-Deploy fires 94.5% of the time on Bench-Deploy prompts — i.e. it labels deployment prompts as evaluation almost as confidently as it labels actual evals (98.8%). When the training pairs are decorrelated so that format and context vary independently, Bench-Deploy false-positive rate drops from 94.5% to 7.2%, an 87.3-point swing. That is the magnitude of the format confound in a single number.

A few details make the result load-bearing rather than incidental. The authors explicitly remove "answer leakage" artifacts (pre-filled `Answer:` fields and similar) from rewrites and show that *cleaning these up actually pushes the standard probe's eval-classification rate higher* (55-70% to 94-95%), so the confound isn't a sloppy-prompt artifact — it's the underlying template structure. A genre/register ablation rewriting Casual-Deploy in formal academic tone *without* structural changes yields ~0% eval classification, confirming probes are tracking rigid templating, not formality. And neither the standard nor the decorrelated probe fires on AdvBench or HarmBench (~0% across both), so the "eval-awareness" signal is not even doing double duty as a safety-content detector. The paper is careful: it does **not** claim evaluation awareness is absent from model representations, only that standard probe pipelines do not isolate it. That distinction matters and is worth carrying forward when citing it.

The empirical scope is narrow — a single open-weight model (Llama-3.1-8B-Instruct), linear probes only, layer 24 reported with consistency across layers 8-31. So the existence of a *linear* eval-awareness direction independent of format remains open at larger scale and in production-tier models. But the critique generalises: any future eval-awareness probe paper that doesn't include a Bench-Deploy-style format control should be read with that caveat.

## Key experimental conditions

- **Model:** Llama-3.1-8B-Instruct (single backbone — explicitly noted as a limitation)
- **Probe:** Logistic regression on frozen residual-stream activations at the last token; bf16 inference, fp32 probe training; L2-regularised (C=1.0); StandardScaler
- **Layers probed:** 8, 12, 16, 20, 22, 24, 26, 28, 30, 31; results reported at layer 24 with consistency verified
- **2x2 design (n=1,076 per cell):**
  - Bench-Eval: canonical MMLU / ARC / GSM8K prompts
  - Casual-Eval: MuTual first dialogue turns (eval-content in casual format)
  - Casual-Deploy: ShareGPT first turns, length-matched
  - Bench-Deploy: ShareGPT prompts rewritten by DeepSeek-V3 into benchmark templates (the adversarial cell)
- **Two training regimes compared:**
  - *Single-contrast (standard):* Bench-Eval vs. Casual-Deploy — the format-confounded recipe used by prior work
  - *Paired (decorrelated):* trains across all four cells so format and context vary independently
- **Diagnostic rewrites:** three variants tested (bench format + casual tone; casual format + academic tone; bench format + academic tone) to separately ablate format and register
- **OOD probe applied to:** AdvBench, HarmBench, and the genre-only rewrites

## Key quantitative results

- **Standard (format-confounded) probe — classification as "Evaluation":**
  - Bench-Eval: 98.8%
  - Casual-Eval: 0.0%
  - Casual-Deploy: 0.0%
  - **Bench-Deploy: 94.5%** (the false-positive cell)
- **Paired (decorrelated) probe — classification as "Evaluation":**
  - Bench-Eval: 98.5%
  - Casual-Eval: 100.0% (recovers context signal that the standard probe misses entirely)
  - Casual-Deploy: 0.0%
  - **Bench-Deploy: 7.2%**
- **Net effect:** 87.3 percentage-point reduction in Bench-Deploy false positives once format and context are decorrelated during training
- **Answer-leakage ablation:** removing pre-filled answer artifacts from rewrites *increased* the standard probe's eval-classification rate on Bench-Deploy from 55-70% to 94-95% — the confound is the template itself, not leakage
- **Register ablation:** rewriting Casual-Deploy in formal academic tone (no structural change) yields ~0% eval classification — probes are not tracking formality
- **Safety datasets:** both probes fire at ~0% on AdvBench and HarmBench — eval-awareness signal does not transfer to safety-relevant content monitoring
- **Prior-work calibration:** Needham et al. (2025) reported AUC 0.83 for eval-vs-deployment probes (human upper bound 0.92); under this analysis those numbers are consistent with format-tracking rather than context-tracking

## Methods (what they did and didn't use)

- Linear logistic-regression probes on frozen residual-stream activations — exactly the standard pipeline they are critiquing, applied to a controlled dataset
- 2x2 dataset construction with adversarial Bench-Deploy cell as the critical falsification target
- LLM-driven prompt rewriting (DeepSeek-V3) to generate the controlled cells
- 5-fold CV on the paired training regime; for the standard regime they deliberately use *no* validation split because the probe trivially fits — generalisation failure is the diagnostic
- **Does not test:** non-linear probes, MLP probes, SAE features, activation-steering interventions, or other model families. The paper explicitly flags that distributed or non-linear eval-awareness representations are not ruled out
- Open-weight model only (Llama-3.1-8B-Instruct); does not attempt the harder question of whether closed-weight frontier models behave the same way
- Methodological paper — no behavioural evals, no fine-tuning, no model-organism construction

## Authors' stated limitations / future work

- Single model architecture; does not generalise the format-confound claim across families or to larger scales
- Linear probes only — non-linear or distributed eval-awareness representations not tested
- Proxy datasets carry their own confounds (MuTual first turns as Casual-Eval; LLM-rewritten ShareGPT as Bench-Deploy)
- Explicit disclaimer that the paper does *not* claim evaluation awareness is absent from model representations — only that standard probes fail to isolate it under format-correlated training
- Implicit recommendation: future probe-based eval-awareness claims should include a Bench-Deploy-style adversarial control; paired-training setups are one path to structure-invariant probes
- No explicit roadmap for future work given

## Open questions and follow-up directions

1. Whether the format confound persists in production-scale models is open. Llama-3.1-8B is small enough that benchmark-template features may dominate the residual stream out of necessity; whether a Claude- or GPT-class model's eval-awareness direction is similarly format-bound, or whether scale buys genuine context-sensitivity, is the load-bearing scaling question and is untested here.

2. Whether non-linear or distributed eval-awareness representations survive the same controlled 2x2 is open. The paper rules out *linear* probes under standard training; an MLP probe, an SAE-feature classifier, or a probe trained on the paired regime applied to existing eval-awareness work would distinguish "probes are wrong" from "the standard recipe is wrong."

3. The paired-training result is the constructive half of the paper and deserves more attention than the framing gives it: a probe that fires 100% on Casual-Eval and 7.2% on Bench-Deploy is a genuine context-aware probe, not a format detector. Replicating this on richer Bench-Deploy distributions (longer prompts, agentic transcripts, multi-turn) would test whether the decorrelated probe holds up or whether it just shifts the confound to a different surface feature.

4. The paper does not test causal interventions. A probe direction that survives the controlled 2x2 should also have downstream behavioural consequences — steering along it should change model behaviour in eval-vs-deployment-relevant ways, the way Hua et al.'s direction does. The current work demonstrates a methodological failure mode but does not establish that any probe direction recovered under paired training is mechanistically meaningful.

5. The AdvBench / HarmBench null is interesting in its own right: eval-awareness probes do not flag safety-content prompts. If the field's working assumption is that situational-awareness probes can double as safety monitors, this is direct evidence against that — and is worth replicating on more safety-content distributions before relying on a "general situational-awareness" probe for any monitoring purpose.

## See also

- [[deception_probes]] — Apollo's deception probes on Llama-3.3-70B report AUROC 0.96-0.999 on insider-trading / sandbagging contrasts; the paper explicitly notes it does not decompose whether the probe captures deception content, eval-awareness, or something else. Devbunova's critique applies directly: if the deceptive scenarios systematically differ in format from the honest ones, the headline AUROC may be partly format-tracking.
- [[steering_eval_aware]] — Hua, Qin, Marks, Nanda construct a deliberately eval-aware LLM and show an activation-steering vector derived from contrastive eval-vs-deployment documents suppresses eval-aware behaviour. Devbunova names Hua et al. (2026) as prior work and does not dispute the steering result; the open question is whether their direction is the format direction or the context direction, since their contrastive document construction has similar format/context entanglement.
- [[sleeper_agent_probes]] — MacDiarmid et al.'s sleeper-agent defection probe (>99% AUROC on Anthropic deceptive-finetune models) is trained on generic yes/no contrast pairs unrelated to the deceptive behaviour itself. The format-confound critique is less obviously applicable (the contrast pairs are deliberately off-distribution), but a Bench-Deploy-style control would still strengthen the claim that the probe tracks deception rather than a correlated surface feature.
- [[natural_language_autoencoders]] — Anthropic's NLA work measures eval-awareness via residual-stream verbalisation rather than linear probes, reports >5% NLA-measured eval-awareness on 10/16 Opus 4.6 evaluations (7 of those with 0% verbalised awareness), and explicitly disclaims absolute calibration. Devbunova's critique partially applies — NLA output may still be confounded by format — but the verbalised-text interface allows readers to inspect what the model is actually "saying" about its situation, which a scalar probe score does not. Whether the realism-rewrite manipulation NLA uses is sufficient format-control under the Devbunova standard is an open replication question.
