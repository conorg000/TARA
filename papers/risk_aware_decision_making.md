# Answer, Refuse, or Guess? Investigating Risk-Aware Decision Making in Language Models

**Authors:** Cheng-Kuang Wu, Zhi Rui Tam, Chieh-Yen Lin (Appier AI Research); Yun-Nung Chen, Hung-yi Lee (National Taiwan University)
**Year:** 2025
**arXiv:** [2503.01332](https://arxiv.org/abs/2503.01332)
**Fetched from:** `arxiv.org/html/2503.01332`
**Status:** read

---

## Summary (in our words)

The paper sets up a clean decision-theoretic frame for QA under risk: at each question the model can answer (gaining `r_cor` if correct, losing `r_inc` if wrong) or refuse (collecting `r_ref = 0`). Vary the reward/penalty pair and you get a family of tasks where the *correct* refusal rate is computable from the model's own calibration — a refusal is rational whenever confidence falls below the threshold implied by the payoff structure. The authors then ask whether frontier LMs behave like rational risk-aware agents across this family.

They don't. Across six closed-weight frontier models on MedQA / MMLU / GPQA, the headline finding is a systematic miscalibration in *both* directions: models "over-answer" in high-penalty settings (refuse too rarely when wrong answers cost 4-8× a correct one) and "over-defer" in low-penalty settings (refuse even when guessing has positive expected value). The diagnostic experiment that makes the paper sharp is the gambling control: when the same risk structure is presented as a pure expected-value puzzle stripped of domain knowledge, models apply EV reasoning in 95/100 trials. On knowledge questions with the identical payoff structure, the same models apply EV reasoning in 4/100 trials. The capability is there; the composition with the QA skill is not.

The proposed fix is prompt chaining: split the decision into three sequential inferences — (1) answer the question, (2) given only the answer letter, estimate confidence, (3) compute expected utility from confidence and the payoff structure and decide answer-vs-refuse. On the hardest setting `(r_cor, r_inc) = (1, -8)` on MMLU, this moves the average normalised reward across the six models from −0.412 (baseline) to +0.012, with all six models improving. The EVR proportion (how often the model explicitly computes expected utility) climbs from ~0.64 under a stepwise single-prompt approach to ~0.98 under chaining for Claude 3.5 Sonnet.

Worth flagging what the paper is and isn't. It is a behavioural-prompting investigation of decision-making competence under explicit risk — no probes, no SAEs, no internal-state analysis. The chaining result is a methodological proposal, not a claim about what's happening inside the model. The decomposition into ACC / ECE / EVR (accuracy, calibration error, expected-value-reasoning rate) is useful precisely because it makes visible that the chaining win is mostly an EVR win — accuracy barely moves, calibration is roughly preserved, the gain comes from the model actually doing the EV step rather than skipping it.

## Key experimental conditions

- 6 closed-weight frontier models: GPT-4o, GPT-4o-mini, Claude 3.5 Sonnet, Claude 3.5 Haiku, Gemini 1.5 Pro, Gemini 1.5 Flash. Reasoning models (o3-mini, DeepSeek-R1) tested separately.
- 3 4-way-MCQ datasets: MedQA (1,273 test), MMLU (1,531 val), GPQA (448 main).
- Payoff grid `(r_cor, r_inc)`: `(0,-1)`, `(1,-8)`, `(1,-4)`, `(4,-1)`, `(8,-1)`, `(1,0)`. Refusal payoff `r_ref = 0` throughout. High-risk = guessing has negative EV; low-risk = guessing has positive EV.
- 4 prompting strategies: no-risk baseline, risk-informing (payoff stated in prompt), stepwise (single-prompt CoT covering all three skills), prompt chaining (three separate inferences).
- Diagnostic gambling control: 100 paraphrases of a pure-EV gambling prompt with no domain content, K=4 choices, same payoff structure.

## Key quantitative results

- High-risk `(1,-8)` MMLU, average normalised reward across the 6 models: no-risk −0.412, risk-informing −0.361, stepwise −0.389, prompt chaining **+0.012**. Every model improves under chaining.
- Per-model on the same condition: Claude Haiku −0.723 → −0.305; GPT-4o-mini −0.668 → −0.016; Gemini Flash −0.624 → −0.175; Claude Sonnet −0.004 → +0.307; GPT-4o −0.115 → +0.327; Gemini Pro −0.335 → −0.066.
- Gambling-vs-knowledge composition gap: expected-value reasoning applied in 95/100 pure-gambling trials vs 4/100 GPQA trials at matched `(0,-1)` payoff.
- Refusal-rate sanity check on high-risk gambling `(0,-1)`: models climb from 6-42% baseline refusal to 93-99% under chaining — i.e., they *can* refuse correctly when the EV step is forced.
- ACC / ECE / EVR decomposition (Table 11, Claude Sonnet, MMLU `(1,-8)`): stepwise ACC 0.881 / ECE 0.147 / EVR 0.642; chaining ACC 0.887 / ECE 0.186 / EVR 0.984. The chaining win is an EVR win, not an accuracy win.
- Reasoning models (o3-mini, DeepSeek-R1) still benefit from chaining despite already producing CoT — composition failure persists past native reasoning training.

## Methods (what they did and didn't use)

- Pure behavioural / prompting methodology. Three skills explicitly decomposed: downstream task accuracy (ACC), confidence calibration (ECE), expected-value reasoning (EVR proportion).
- EVR proportion measured by manual inspection of model reasoning text on 100-instance samples — does the model explicitly compute EV, or does it skip the step?
- No internal-state analysis: no probes, no SAEs, no activation steering, no logit-lens. All evidence is from output text and decision rates.
- Closed-weight models throughout the main results — reproducibility depends on hosted API behaviour at time of measurement.

## Authors' stated limitations / future work

- MCQ-only setup; free-form QA under the same risk frame is not tested.
- Prompt chaining triples inference cost — the latency / compute tradeoff is real and acknowledged.
- Reasoning-model results suggest the composition problem isn't dissolved by CoT-style training, but the paper doesn't characterise what kind of training would.
- The authors note general framing about agents reasoning reliably in novel scenarios still being open — not a specific follow-up commitment.

## Open questions and follow-up directions

1. The composition failure is the load-bearing claim and the gambling-vs-knowledge contrast is the cleanest piece of evidence for it. Whether the failure is best modelled as "the EV-reasoning circuit doesn't activate in QA contexts" vs "the model picks an answer first and the EV step gets shortcut" is not distinguished — token-level analysis of *when* the EV step is skipped in stepwise vs chaining traces would discriminate.
2. The EVR proxy is a manual annotation of "did the model explicitly do EV in text". A model that does EV silently and lands the right decision would be scored as failing the proxy. Whether a behavioural-equivalent metric (decision matches EV-optimal under measured confidence) tracks the same gap would clarify whether chaining is teaching EV or just forcing it onto the page.
3. Prompt chaining works by isolating the confidence-estimation step from the answer step. This is closely related to the [[confessions]] firewalling result and to the broader observation that asking a model to verify its own work in a separate pass beats single-pass CoT. The general principle — that compositional decisions benefit from inference-time isolation of sub-skills — has scope well beyond risk-aware QA.
4. All evidence is behavioural. Whether the "model knows it doesn't know" — i.e. whether the calibration signal the confidence step is reading is present in activations at the answer-step before the model commits — is the natural internal-state question. Linear probes on confidence at the pre-answer position would test whether the chaining win is genuinely surfacing existing information or constructing it.
5. The reasoning-model result that o3-mini and DeepSeek-R1 still benefit from chaining is one paragraph in this paper and is the most interesting single observation in it. Native CoT models presumably *do* perform the relevant intermediate computations; that chaining still helps suggests the EV step is being suppressed by some inference-time pressure (length, confidence-bias) that explicit scaffolding releases.

## See also

- [[confessions]] — same recipe (firewall a self-assessment step from the task step), different target (admit-misbehaviour vs estimate-confidence-for-EV).
- [[lanham_measuring_faithfulness]] — the EVR proxy is a faithfulness measurement in disguise: did the chain-of-thought actually do the work it appears to do, or is the answer arrived at by other means?
- [[cot_faithfulness]] — chaining's effect on EVR (0.642 → 0.984) is essentially a forced-faithfulness intervention; relevant to whether scaffolding can be used to *create* faithful CoT for monitoring purposes.
- [[low_probability_actions]] — adjacent decision-theoretic framing of model behaviour as samples from a calibrated distribution under explicit payoff structure.
