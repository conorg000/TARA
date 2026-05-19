# Benchmarking Deception Probes via Black-to-White Performance Boosts

**Authors:** Avi Parrack, Carlo Leonardo Attubato, Stefan Heimersheim
**Year:** 2025 (v1 July 2025; v3 January 2026)
**arXiv:** [2507.12691](https://arxiv.org/abs/2507.12691)
**Status:** read

---

## Summary (in our words)

Parrack, Attubato, and Heimersheim run the missing baseline study on deception probes. The Goldowsky-Dill et al. probes ([[deception_probes]]) report AUROCs of 0.96-0.999 on Llama-3.3-70B-Instruct, but never benchmark those numbers against the cheaper black-box alternative — just asking an LLM judge whether the assistant's response looks deceptive. This paper supplies the comparison: for each dataset, measure white-box-monitor AUROC (probe on activations) and black-box-monitor AUROC (Claude-3.5-Sonnet / Haiku reading the dialogue), and report the gap. They call this gap the "black-to-white performance boost."

The headline is that the boost is real but small, and disappears on at least one dataset. On AI Liar the probe beats the LLM judge by +0.144 AUROC; on Sandbagging it beats by +0.039; on Insider Trading by +0.052; on Deception Dilution by +0.117. On the Backdoors dataset the probe actually *underperforms* the black-box judge by 0.123 (0.776 vs. 0.899). Averaged across the five deception datasets, full-averaging Pairs probe AUROC is 0.941 versus a black-box Sonnet-judge baseline that is often only marginally lower. The authors' summary is "weak but encouraging" — and the qualifier matters. The probe is not delivering most of the headline performance; the LLM judge is.

Two methodological details land harder than the headline. First, the probe activation is spread across the entire response rather than concentrated on the deceptive tokens, so full-response averaging is what makes the probe work — token-level localisation does not. Second, the Backdoors failure is attributed to distributional shift: the probe's baseline activation level differs between datasets, so its absolute threshold doesn't transfer. The probe is reading off something correlated with the training distribution, not a cleanly portable deception axis.

We read this as a soft replication of the [[eliciting_secret_knowledge]] pattern in a different setting: when you actually compare white-box internal-state methods against thoughtfully-built black-box baselines, the white-box gap is much smaller than the standalone probe numbers suggest. The deception-probe enterprise still has positive black-to-white value on most datasets, but the value-add is on the order of 0.04-0.14 AUROC, not the 0.96+ headline number that gets quoted in isolation.

## Key experimental conditions

- Probed model: Llama-3.3-70B-Instruct, residual-stream activations at layer 22
- Probes evaluated: two from Goldowsky-Dill et al. — "Pairs" probe (honest/deceptive instruction contrast pairs) and "RP" probe (roleplaying scenarios)
- Black-box judges: Claude-3.5-Sonnet and Claude-3.5-Haiku, rating suspiciousness across incentives, behavioural indicators, logical consistency, and "other"
- Datasets: AI Liar (266), Deception Dilution (266, AI Liar + appended true claims), Insider Trading (1005), Sandbagging (931, intentional WMD underperformance), Backdoors (150, hidden code vulnerabilities), Alpaca Control (1000 honest, calibration baseline)
- Metric: AUROC; white-box reading (WBR) vs. black-box reading (BBR), plus full-averaging variants of the probe score

## Key quantitative results

- AI Liar: WBR (Sonnet, Pairs) 0.966 vs. BBR (Sonnet) 0.822 → +0.144
- Deception Dilution: 0.916 vs. 0.799 → +0.117
- Insider Trading: 0.986 vs. 0.934 → +0.052
- Sandbagging: 0.981 vs. 0.942 → +0.039
- Backdoors: 0.776 vs. 0.899 → **−0.123** (probe loses)
- Average WBR (Pairs, full averaging) across five datasets: 0.941
- Authors' verbal summary: "weak but encouraging black-to-white performance boosts"
- Probe activation is spread across the entire response; localisation to deceptive tokens does not work — full-response averaging is what carries the AUROC

## Methods (what they did and didn't use)

- Linear probes on residual-stream activations (layer 22) — the Goldowsky-Dill probes, not retrained
- LLM-judge monitoring as the black-box baseline (Claude-3.5-Sonnet / Haiku)
- No SAEs, no activation steering, no NLAs
- No mechanistic decomposition of what the probe direction captures
- Open-weight probed model (Llama-3.3-70B); proprietary black-box judges (Claude). The judge being more capable than the probed model is flagged by the authors as a methodological caveat — the black-box baseline may be artificially strong

## Authors' stated limitations / future work

- The probe activates across the whole response rather than localising on the deceptive claim, so token-level deception localisation is not currently a capability of these probes
- The black-box judges (Claude-3.5-Sonnet/Haiku) are more capable than the probed Llama-3.3-70B — the baseline comparison may be unfair in the white-box direction
- Distributional shift: WBR fails on Backdoors because the probe's baseline activation level differs between datasets, so absolute thresholds don't port
- Deception Dilution (appending true facts to deceptive responses) already reduces probe performance; stronger adversarial evasion attacks are needed to stress-test
- Multi-turn follow-up evaluations are overly simplistic (yes/no follow-ups); richer interaction protocols are needed

## Open questions and follow-up directions

1. **What does the probe direction actually encode?** The paper shows that probe activation is non-localised across the response and that absolute thresholds don't transfer across datasets. Both are consistent with the probe reading a coarser distributional signal — eval-context, register, refusal-adjacent features — rather than a clean "this token is a lie" axis. A decomposition study (probe on eval-awareness contrasts vs. probe on deception contrasts, tested on the same datasets) would distinguish these accounts. The Backdoors failure is the closest thing to a falsification in the paper and is left as "distributional shift" without further mechanism.

2. **Does the boost survive scale matching?** The black-box judge (Claude-3.5-Sonnet) is substantially more capable than the probed model (Llama-3.3-70B). The current black-to-white boost is therefore a lower bound on the probe's relative contribution — a same-capability or weaker judge would likely widen the gap. Conversely, a judge of equal or greater capability to a frontier probed model is the relevant deployment scenario; whether probes retain any boost when the judge is GPT-5/Sonnet-class and the probed model is also frontier is unaddressed.

3. **Whether full-response averaging is doing the real work.** The result that probe activation is spread across the entire response, not concentrated on the deceptive tokens, undercuts the standard claim that probes detect deceptive *reasoning*. They detect something about responses-that-contain-deception in aggregate. Whether any localisation-aware variant (windowed probes, token-attribution methods, deception-onset detection) can recover token-level signal is open and load-bearing for the "probes as monitoring tools" framing.

4. **Adversarial robustness beyond Deception Dilution.** Deception Dilution (appending true claims) already pulls AUROC down by 0.05; the authors flag that stronger attacks are needed. The natural follow-up is to optimise an adversary against the probe directly — fine-tune or prompt the model to produce deceptive responses with low probe activation — and report the resulting boost. The original Goldowsky-Dill probes claim "insufficient for adversarial deployment"; this paper provides the infrastructure to actually measure that.

5. **Generalisation to genuinely emergent deception.** All five datasets here are prompted or fine-tuned deception. Whether probes maintain any black-to-white boost on naturally-emergent deceptive behaviour — alignment-faking-style cases where no induction protocol exists — is the question the literature most needs answered and this benchmark cannot yet address.

## See also

- [[deception_probes]] — the probes this paper benchmarks; provides the AUROC-0.96-0.999 headline that this paper contextualises against black-box baselines
- [[eliciting_secret_knowledge]] — sibling black-box-beats-white-box finding on a different concealment task; together these are the strongest current evidence that white-box methods need to be benchmarked against thoughtful black-box baselines, not reported standalone
- [[sleeper_agent_probes]] — same probe-on-activations family applied to a different deception phenomenon; no black-box baseline reported there either
- [[anti_scheming_training]] — separate evidence that apparent deception-detection signals are partly carried by eval-awareness; complementary to the "what does the probe actually detect" question
- [[steering_eval_aware]] — eval-awareness has linear structure; provides a candidate for what the probe direction is partially picking up
- [[high_stakes_probes]] — adjacent probe-deployment paper; demonstrates synthetic-to-natural generalisation that the Backdoors distributional-shift result here calls into question for the deception case
