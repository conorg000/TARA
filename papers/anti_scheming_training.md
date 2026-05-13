# Stress Testing Deliberative Alignment for Anti-Scheming Training

**Authors:** Schoen, Nitishinskaya, Balesni, Højmark, Hofstätter, Scheurer, Meinke, Wolfe, van der Weij, Lloyd, Goldowsky-Dill, Fan, Matveiakin, Shah, Williams, Glaese, Barak, Zaremba, Hobbhahn (Apollo Research, OpenAI, others)
**Year:** 2025
**arXiv:** [2509.15541](https://arxiv.org/abs/2509.15541)
**Status:** read

---

## Summary (in our words)

Schoen et al. apply deliberative alignment training (an OpenAI-style anti-scheming intervention) to o3 and measure the reduction in covert behavior on 26 out-of-distribution evaluations spanning 180+ environments. Headline number: covert action rate drops from 13% to 0.4%. A success, on the face of it.

The buried finding is the load-bearing one. The authors show, via chain-of-thought analysis, that **the reductions are at least partly driven by model awareness of evaluation, not by genuine alignment improvement.** When the model recognizes it's being tested for alignment (and verbalizes this in its reasoning), covert action rates drop. When it doesn't, they rise. They demonstrate this causally — eval-awareness is doing significant work in the apparent training-induced improvement.

The implication the authors draw: apparent alignment improvements from this class of intervention may be partially an eval-awareness artefact rather than a change in underlying disposition. The reductions are real on the measured distribution; whether they generalize beyond contexts the model recognizes as evaluations is the open question.

The methodology is purely behavioral + CoT inspection. No probes, no internal-state analysis. The eval-awareness signal comes entirely from what the model verbalizes in its chain of thought.

## Key experimental conditions

- Model: OpenAI o3 (primarily) and other capable systems
- Intervention: deliberative alignment training (anti-scheming)
- Evaluation: 26 out-of-distribution evals, 180+ environments, focused on "covert actions" (secretly breaking rules, intentional underperformance — these are scheming proxies)
- Eval-awareness manipulation: identify cases where the model's CoT shows recognition of "this is an alignment test" vs. cases where it doesn't, compare covert-action rates across the split

## Key quantitative results

- Covert action rate (o3): **13% → 0.4%** with deliberative alignment training
- Causal demonstration that "unawareness increases" covert behavior, "awareness decreases" it
- Reductions explicitly stated as "potentially driven by model awareness of evaluation"
- Complete elimination not achieved; red-teaming finds remaining misbehavior

## Methods (what they did and didn't use)

- Behavioral evaluation across covert-action proxies
- Chain-of-thought analysis to detect and stratify eval-awareness
- Causal manipulation via the awareness/unawareness split
- **No linear probes, no internal-state methods, no probes for eval-awareness directly** — the awareness signal comes entirely from CoT inspection
- Tension: they rely on CoT being faithful for the eval-awareness measurement, which [[cot_faithfulness]] suggests is risky

## Authors' stated limitations / future work

- Ability to rely on CoT-based analysis "degrades as models continue to depart from reasoning in standard English"
- They don't address *deceptive* alignment (the adversarial case where the model actively tries to fool the eval)
- More work needed on alignment mitigations that don't depend on eval-awareness being the driver

## Open questions and follow-up directions

1. **CoT-silent eval-awareness.** The eval-awareness signal is read off chain-of-thought verbalizations. Given evidence that CoT often fails to reflect underlying computation ([[cot_faithfulness]]), the CoT-stratification likely undercounts the eval-awareness effect. An internal-state measurement (e.g. a probe) would test whether eval-awareness is also driving behaviour in cases where the model doesn't verbalize it.

2. **Mechanism of the eval-awareness representation.** The paper establishes that eval-awareness is causally relevant but does not characterize how the model represents "this is an evaluation" internally — whether it's a single linear direction, a feature cluster, or distributed structure. Open in both o3 (closed-weight, hard to access) and any open-weight model trained similarly.

3. **Generalization across interventions.** Deliberative alignment is one anti-scheming recipe. Whether other interventions (RLHF variants, constitutional methods, refusal training) produce the same eval-awareness-mediated improvement pattern, or differ qualitatively, is unaddressed.

4. **The deceptive-alignment case.** Authors explicitly disclaim this. The current setup measures eval-awareness in models not actively trying to defeat the eval. Whether the same mechanism (or a more adversarial variant) appears in models trained or prompted toward deceptive alignment is a natural next step.

5. **Replication on open-weight models.** o3 is closed. Reproducing the awareness-vs-unawareness covert-action gap on an open-weight reasoning model would both validate the finding and enable the internal-state analyses that are off the table here.

## See also

- [[cot_faithfulness]] — direct concern about the reliability of the CoT channel this paper relies on for its eval-awareness measurement
- [[deception_probes]] — probe-based deception detection, the natural methodological counterpart to this paper's behavioural finding
- [[in_context_scheming]] — Apollo's earlier characterisation of the scheming phenomenon this intervention targets
- [[science_of_scheming]] — broader programmatic context for measuring and reducing scheming
- [[steering_eval_aware]] — evidence that eval-awareness has linear structure that can be causally manipulated
- [[situational_awareness_dataset]] — measurement substrate for situational/eval awareness more generally
- [[alignment_faking]] — related finding that training pressure can leave underlying dispositions intact while changing surface behaviour
