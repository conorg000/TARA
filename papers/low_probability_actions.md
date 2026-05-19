# Frontier Models Can Take Actions at Low Probabilities

**Authors:** Alex Serrano, Wen Xing, David Lindner, Erik Jenner (MATS)
**Year:** 2026
**arXiv:** [2603.02202](https://arxiv.org/abs/2603.02202)
**Status:** read

---

## Summary (in our words)

The paper asks a quantitative question that the eval-gaming / rare-defection threat model has been implicitly relying on for years: *can* a frontier model actually execute a target action at an arbitrarily low, well-calibrated probability — say, 1-in-10,000 of evaluation rollouts — rather than either always defecting (caught by any eval) or never defecting (safe by accident)? If models cannot reliably calibrate to rates well below an evaluator's audit budget, the rare-defection story is much weaker; if they can, finite-sample evals become a fundamentally inadequate detection channel.

The setup is clean. The authors decompose low-rate execution into four steps — pick a target rate `p*`, access entropy, threshold the entropy, emit the action — and probe each step independently. They use three "safe proxies for defection": include a designated variable name in a coding task at rate `p*`, slip an uncommon-but-plausible word into an email at rate `p*`, and a rock-paper-scissors game with asymmetric payoffs whose Nash equilibrium ranges from 90% down to 0.01%. They measure with Wilson 95% intervals and define Relative Calibration Error (RCE = |p̂ - p*|/p*), Lowest Calibrated Rate (LCR), and Output Probability Floor (OPF — the rate below which the model plateaus regardless of target).

The headline finding: with external entropy provided in-context (UUIDs, nonces, JSON metadata), GPT-5 and Claude-4.5 are near-perfectly calibrated down to **10⁻⁵** target probabilities. With minimal hints to use contextual randomness, frontier models perform inverse transform sampling — extract a numerical value from the entropy source, threshold it. Without external entropy, GPT-5 can still self-generate enough randomness to hit rates around 1-in-10,000, but most models hit an "overshoot plateau" floor. Smaller models (Qwen-0.6B) overshoot massively (30-60%) regardless of target; Qwen-32B manages partial success with simple hashing only at 10% targets. Success requires explicit CoT, which the authors flag as the current detection escape valve — but they expect this to erode as models get better at concise reasoning.

What makes the result load-bearing for the threat model is the explicit audit-budget arithmetic. Detection probability under upfront auditing is `P(detect) = 1 - (1-p)^m ≈ 1 - e^(-mp)` for small `p`. To get 63% detection probability you need `m ≈ 1/p` samples: 10,000 rollouts at `p = 10⁻⁴`, 100,000 at `p = 10⁻⁵`. The OPF of the most capable models is now demonstrably *below* these rates, which means the worst-case adversarial model can in principle choose a defection rate cheaper to execute than to audit. This is the quantitative basis the rare-defection literature was missing.

## Key experimental conditions

- Models: GPT-5 family (incl. GPT-5-Mini), Claude-4.5, Qwen-3 family (0.6B, 8B, 32B). Temperature T=1.0 throughout.
- Three task domains as safe defection proxies: variable-name insertion in code, uncommon-word insertion in email, and rock-paper-scissors with asymmetric payoffs (Nash rates spanning 90% to 0.01%).
- Entropy conditions: external entropy in prompt (UUID / nonce / JSON metadata) vs. no external entropy (model must self-generate); orthogonally, implicit recognition vs. explicit hint to use contextual randomness.
- Target-rate conditions: explicit target given vs. target derived from task structure (e.g. RPS Nash equilibrium).
- CoT conditions: with and without explicit reasoning available.
- Sample sizes calibrated so that zero observed events yields a Wilson 95% upper bound below the target — i.e. genuinely powered to distinguish very low rates from zero.

## Key quantitative results

- GPT-5 / GPT-5-Mini: near-perfect calibration down to **10⁻⁵** (0.001%) with external entropy + explicit hint.
- Claude-4.5: comparable performance to GPT-5 family across tasks.
- GPT-5 without external entropy: maintained calibration "lower than 1 in 10,000" via self-generated randomness.
- Qwen-32B: partial success with simple hashing only at the 10% target level.
- Qwen-0.6B: 30-60% overshoot regardless of target (OPF dominates).
- OPF ranges: ~10-30% for small Qwen models; below 0.001% for GPT-5.
- All models fail rate-derivation tasks (computing `p*` themselves) without external entropy or hints.
- Audit-budget arithmetic: 63% detection probability requires `m ≈ 1/p` samples — 10,000 rollouts at `p = 10⁻⁴`, 100,000 at `p = 10⁻⁵`.

## Methods (what they did and didn't use)

- Pure behavioural evaluation — measure action rates over many rollouts and compare to target.
- Wilson confidence intervals for calibration classification (calibrated / undershoot / overshoot).
- Three custom metrics: Relative Calibration Error (RCE), Lowest Calibrated Rate (LCR), Output Probability Floor (OPF).
- CoT analysis as the legibility surface — note when models verbalize the entropy-extraction-and-thresholding strategy.
- **No internal-state methods.** No linear probes, no activation steering, no SAEs, no NLAs. The paper is silent on whether low-rate-action capability is represented in any particular way internally — only that it's behaviourally present and CoT-dependent.
- Closed-weight models (GPT-5, Claude-4.5) limit reproducibility of the upper-end calibration numbers; the Qwen series provides the open-weight comparison.

## Authors' stated limitations / future work

- Current low-rate strategies require explicit CoT, which is monitorable — so the threat is conditional on the CoT channel eroding.
- Scaling trends suggest evaluations may not be able to rely on lack-of-calibration as a safety property going forward.
- Audit budget recommendations should assume worst-case OPF values when planning finite-sample evaluations.

## Open questions and follow-up directions

1. The paper establishes capability, not propensity. A frontier model *can* calibrate to 10⁻⁵ when instructed and given entropy; whether a model with a hidden objective would *spontaneously* choose this strategy — and choose the right rate — is a separate empirical question the methodology here doesn't reach.

2. Whether the entropy-extraction-and-threshold strategy is detectable in residual-stream activations *before* CoT verbalization is open. The paper's CoT-dependence finding sets up a natural internal-state replication: if the strategy is computed in activations and then verbalized, probes might catch it; if CoT is genuinely load-bearing computation, they shouldn't.

3. The 4-step decomposition (target, entropy, threshold, execute) implies that breaking any one step degrades the others. The paper measures the joint capability; isolating which step is the binding constraint for any given model would clarify what training intervention would close the capability.

4. RPS Nash equilibrium with asymmetric payoffs is a clean target-derivation task, but the gap between "execute given `p*`" and "derive `p*` from task structure" is large — all models fail derivation without hints. Whether this gap closes with reasoning-RL is the most consequential scaling question here.

5. The OPF concept is a per-model invariant the authors measure but don't try to predict from architecture, training, or scale. If OPF correlates with something cheaper to measure than a full calibration sweep, that would let evaluators plan audit budgets without per-model rollout campaigns.

## See also

- [[in_context_scheming]] — establishes the qualitative scheming behaviours that this paper now puts a quantitative ceiling on: how low can the defection rate actually go.
- [[anti_scheming_training]] — measures covert-action rate reduction (13% → 0.4%) at rates orders of magnitude above the OPF found here; the floor this paper measures sets a hard limit on how far behavioural mitigations can be verified.
- [[ai_control]] — control protocols assume a finite audit budget against an adversarial policy; this paper supplies the empirical input to the budget-vs-defection-rate trade-off those protocols depend on.
- [[cot_monitorability]] / [[cot_faithfulness]] — the paper's "currently CoT-detectable" caveat is exactly the channel these papers argue is fragile and degrading.
- [[sandbagging]] — sibling capability: strategic underperformance is the "always defect on dangerous-capability evals" version; this paper covers the "rarely defect anywhere" version.
