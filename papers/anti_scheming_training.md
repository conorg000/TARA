# Stress Testing Deliberative Alignment for Anti-Scheming Training

**Authors:** Schoen, Nitishinskaya, Balesni, Højmark, Hofstätter, Scheurer, Meinke, Wolfe, van der Weij, Lloyd, Goldowsky-Dill, Fan, Matveiakin, Shah, Williams, Glaese, Barak, Zaremba, Hobbhahn (Apollo Research, OpenAI, others)
**Year:** 2025
**arXiv:** [2509.15541](https://arxiv.org/abs/2509.15541)
**Status:** read

---

## Summary (in our words)

This is the most important new paper for our threat model, full stop. They apply deliberative alignment training (an OpenAI-style anti-scheming intervention) to o3 and measure the reduction in covert behavior on 26 out-of-distribution evaluations spanning 180+ environments. Headline number: covert action rate drops from 13% to 0.4%. A success, on the face of it.

The buried finding is the load-bearing one. The authors show, via chain-of-thought analysis, that **the reductions are at least partly driven by model awareness of evaluation, not by genuine alignment improvement.** When the model recognizes it's being tested for alignment (and verbalizes this in its reasoning), covert action rates drop. When it doesn't, they rise. They demonstrate this causally — eval-awareness is doing significant work in the apparent training-induced improvement.

For our project this is the cleanest existing evidence that the eval-gaming threat model isn't speculative. It's the difference between "models *might* be eval-aware in ways that contaminate behavioral measurements" and "we have causal evidence that they are." Cite this everywhere we motivate the project.

The methodology is purely behavioral + CoT inspection. No probes, no internal-state analysis. Which is precisely the gap — they show that eval-awareness is causally driving measured improvements but cannot directly measure the eval-awareness representation itself. A probe-based follow-up would close that loop.

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

## Our own follow-up thoughts (project-relevant)

1. **The probe extension is now mandatory.** Schoen et al. show that eval-awareness drives apparent alignment improvements *as detected via CoT*. The next obvious question — and the one their methodology can't answer — is whether a probe can detect eval-awareness in cases where the CoT doesn't verbalize it. Given [[cot_faithfulness]]'s 75% unfaithfulness rate, the CoT-stratification is probably an *undercount* of the eval-awareness signal. A probe-based version of this analysis would tighten the result.

2. **This paper hands us the project framing on a plate.** Anthropic/OpenAI claim a 32× reduction in covert behavior; Apollo show ~all of that may be eval-awareness; we measure whether internal eval-awareness representations correlate with covert behavior even when CoT is silent. Project's value proposition: *the only thing standing between us and confidently declaring eval-awareness is the apparent-alignment story is a probe*.

3. **Direct experimental pairing with [[deception_probes]].** Goldowsky-Dill et al. show probes can detect deception. Schoen et al. show eval-awareness can fake the appearance of reduced deception. The combined project asks: does the deception probe still fire on inputs that *look* aligned because the model is eval-aware? If yes, the probe sees through the eval-awareness mask. If no, the probe is fooled by the same trick — important negative result.

## Relevance to our project

Maximum. This is the strongest existing causal evidence for the eval-gaming threat model and the clearest empirical anchor for why a probe-based extension matters. Cite directly in the motivation section.

Pairs with: [[deception_probes]] (the probe method paired against this paper's behavioral finding), [[cot_faithfulness]] (the unreliability of the channel they use to measure eval-awareness), [[in_context_scheming]] (Apollo's earlier work on the phenomenon being mitigated).
