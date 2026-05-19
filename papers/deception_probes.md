# Detecting Strategic Deception Using Linear Probes

**Authors:** Goldowsky-Dill, Chughtai, Heimersheim, Hobbhahn (Apollo Research)
**Year:** 2025
**arXiv:** [2502.03407](https://arxiv.org/abs/2502.03407)
**Fetched from:** `arxiv.org/pdf/2502.03407` (PDF, converted with pdftotext; HTML and ar5iv conversions both 404'd)
**Status:** read

---

## Summary (in our words)

Goldowsky-Dill et al. train linear probes on Llama-3.3-70B-Instruct to distinguish honest from deceptive on-policy model responses, and test whether probes trained on cheap, simple contrastive material generalise to harder, more realistic deception settings. The probe is a logistic-regression classifier (l2 with λ=10) fit on residual-stream activations after layer 22 of 80, with per-token scores aggregated by mean to give a per-response deception score. On four evaluation datasets — a custom roleplaying set, Insider Trading Report and Insider Trading Confirmation (Scheurer et al. 2023), and Sandbagging on WMDP vs. MMLU (Benton et al. 2024) — the Instructed-Pairs probe gets AUROC 0.964 / 0.999 / 0.974 / 0.983 against honest responses in the same setting, and recall ≥96% at 1% FPR against Alpaca control responses.

The main methodological move is training on contrastive *instructions* rather than contrastive responses. They use the Zou et al. (2023) Instructed-Pairs dataset: two prompts identical except for "pretend you are an honest person…" vs. "pretend you are a dishonest person…", with the same random true fact (from Azaria & Mitchell) pasted in as the model response, and activations gathered on all but the last 5 tokens of that fact. Crucially, the training responses contain no actual deception — the probe learns a direction from the contrast in *intent framing*, then transfers to settings where the model actually deceives on-policy. A second probe trained on Roleplaying responses transfers comparably on honest-vs-deceptive AUROC but is much worse at distinguishing deception from non-deception-related control prompts.

The most honest part of the paper is section 4.1.1 and Appendix A.1, where the authors flag that the Instructed-Pairs probe partially tracks "is this scenario deception-related" rather than purely "is this response deceptive". Even when the model is in fact truthful in a roleplaying scenario that incentivises lying, the probe fires harder than on truthful responses to neutral prompts. They show this directly on the Pacchiardi et al. dataset, which is split exactly half into deception-incentivised and non-deception-incentivised prompts. The Roleplaying-trained probe shows much less of this scenario-sensitivity, consistent with both classes in its training set already being deception-incentivised. This means the headline 1% FPR / 95-99% recall number is partly inflated by Alpaca control being unrelated to deception — deployment FPR on deception-adjacent but honest traffic would likely be worse.

Failure-mode analysis (Table 2) names two categories: spurious correlations (the probe fires on honest confessions of past misdeeds — it tracks something closer to "morality" than "honesty in this token"), and aggregation failures (a partly-deceptive response can be misclassified by mean-pooling). They also flag one unclassified-mystery failure. The black-box GPT-4o baseline is roughly comparable to the probe on these settings — the paper does not claim white-box dominance, only viability. They explicitly say current performance is "insufficient as a robust defence against deception."

## Key experimental conditions

- Model: Llama-3.3-70B-Instruct (hyperparameters originally tuned on Llama-3.1-70B-Instruct and transferred; validated by sweeps in Appendices D.2 / D.3)
- Probe: logistic regression with l2 (λ=10) on normalised residual-stream activations after layer 22 (of 80), trained by flattening across samples and sequence positions; per-token scores mean-aggregated to a per-response score
- Probe-training data (mainline): Instructed-Pairs from Zou et al. (2023) — contrastive prompts ("pretend you are an honest/deceptive person") with a random true fact pasted as the response, activations gathered excluding the last 5 tokens. Training responses contain no actual deception.
- Alternate training data: a custom Roleplaying dataset (371 responses, 84 honest / 84 ambiguous / 203 deceptive); GPT-4o-generated scenarios where deception is instrumentally useful, on-policy Llama responses graded by GPT-4o
- Evaluation datasets:
  - Roleplaying (371 responses, Low realism)
  - Insider Trading Report (1329 responses; 669 honest / 324 ambiguous / 336 deceptive; High realism; Scheurer et al. 2023)
  - Insider Trading Confirmation (656 responses; 24 honest / 2 ambiguous / 630 deceptive; High realism; follow-up email from the manager — the model doubles down on deception in 96% of cases)
  - Sandbagging (995 responses; 511 honest / 64 ambiguous / 420 deceptive; Medium realism; WMDP vs. MMLU, Benton et al. 2024; labels assigned programmatically from chain-of-thought)
- Control: Alpaca responses (9994 used), chosen over WildChat because Alpaca prompts are unlikely to be deception-related
- Grading: GPT-4o-2024-08-06 with dataset-specific prompts and few-shot examples; Sandbagging labels programmatic from CoT
- Two settings dropped from main results: an AI Audit setting (Järviniemi & Hubinger) where the authors could not determine whether Llama was knowingly deceptive vs. confused

## Key quantitative results

- Mainline probe (Instructed-Pairs, layer 22) AUROC for distinguishing deceptive vs. honest on the same dataset:
  - Roleplaying: 0.964
  - Insider Trading Report: 0.999
  - Insider Trading Confirmation: 0.974
  - Sandbagging: 0.983
- Recall at 1% FPR on Alpaca control: ≥96% on all four evaluation datasets ("95-99%" in the abstract); on Roleplaying the 1% FPR threshold misses ~4% of deceptive responses despite >0.998 deceptive-vs-control AUROC
- Reclassifying "ambiguous" responses as honest or deceptive (Table 3): Roleplaying AUROC 0.964 → 0.913; Insider Trading Report 0.999 → 0.978; Sandbagging 0.983 → 0.982. Recall at 1% FPR mostly unchanged (Roleplaying 0.998 → 0.956, others ≈ 1.0)
- Probing follow-up question variant ("Was your last response deceptive?" / "No") trained on Roleplaying: recall at 1% FPR >99% on all four eval datasets; recall at 0.1% FPR ≥97% on most datasets, 92.0% on Insider Trading Report (best probe overall by this metric, but worse than mainline on Sandbagging)
- AI Audit setting (excluded from main results): mainline probe gets AUROC 0.872, but authors argue the model was likely not knowingly deceptive
- Layer 22 chosen on Llama-3.1 Roleplaying performance and transferred; sweep shows large variation between adjacent layers, particularly recall at 1% FPR. Insider Trading Confirmation drops sharply past layer 29.
- Probe-fitting comparison (Appendix D.1): Logistic Regression, Difference of Means, LDA, and LAT (Zou et al.) give very similar AUROC, but logistic regression is best at separating deceptive from control responses
- SAE-feature probes (using McGrath et al. 2024 SAEs on Llama-3.3) fail to generalise from Instructed-Pairs; on Roleplaying they work but underperform raw-activation probes
- Black-box baseline (GPT-4o classifying full transcripts on a 7-point scale with a single universal prompt) is roughly comparable to the mainline probe; the most deception-rated control responses are when Llama generates factually incorrect text on Alpaca tasks
- Honest responses in deception-incentivised roleplaying scenarios score higher on the probe than honest responses to neutral prompts (Pacchiardi et al. dataset; Appendix A.1), directly supporting the "scenario-relatedness" hypothesis

## Methods (what they did and didn't use)

- Linear probes (logistic regression) on raw residual-stream activations — the technique family
- Compared difference-of-means, LDA, and LAT as alternative fitting methods (Appendix D.1)
- Compared training on SAE features (McGrath et al. 2024) vs. raw activations
- Layer sweep, regularisation sweep, aggregation-method sweep (mean / max / ReLU-threshold-then-mean), and last-token-only probing
- No activation steering, no interpretability of the probe direction itself (no decomposition into known features, no mech-interp investigation of what "the deception direction" is composed of)
- Behavioural-grade ground-truth via GPT-4o (closed-weight grader with iterated prompts) — the labels themselves are imperfect and the authors flag this
- Open-weight model (Llama-3.3-70B-Instruct); reproducible. Code at github.com/ApolloResearch/deception-detection, probe outputs viewable at data.apolloresearch.ai/dd/

## Authors' stated limitations / future work

- Probes are imperfect: spurious correlations (the probe tracks something close to "morality" — fires on honest confessions), aggregation failures (mean-pooling fails on partly-deceptive responses), and some unexplained misclassifications
- Suggested directions: improved training sets, SHIFT-style generalisation control (Marks et al. 2024), alternative aggregation, probes trained on concatenated activations across layers
- Imperfect labels: excluding "ambiguous" responses risks making probes look better than they are by removing hard cases
- Capability ceiling: Llama-3.3 is not capable enough for sophisticated deception. The AI Audit setting could not be used as ground-truth-confidence ran out. Stronger models needed for sandbagging-without-CoT, alignment-faking-under-RL, and similar harder settings
- Tests on settings where black-box methods fail (e.g. alignment-faking inferable only from user-metadata-conditional behaviour changes) are an explicit open target — the paper does not demonstrate that white-box detectors beat black-box in any setting
- Authors explicitly state current probe performance is "insufficient as a robust defence against deception" — useful informationally, not deployable adversarially

## Open questions and follow-up directions

1. **What is the probe actually detecting?** The authors themselves provide direct evidence (Appendix A.1) that the Instructed-Pairs probe partly tracks "is this scenario deception-related" rather than only "is this response deceptive". A natural follow-up is to train a probe on contrast pairs that vary scenario deception-relatedness without varying response honesty (e.g. honest responses in lying-incentivised vs. neutral scenarios), and measure how much of the headline AUROC the resulting "deception-scenario" direction explains. The Roleplaying-trained probe is a partial control in this direction but lacks an explicit scenario-deception axis.

2. **The recall-vs-AUROC sensitivity gap.** The paper notes that "probing two layers later results in a recall of nearly 0 on both Insider Trading datasets while still having decent classification accuracy" (Appendix D.2). That hyperparameter knife-edge is a load-bearing reproducibility concern: it implies the mainline result depends on a layer choice tuned on Roleplaying-on-Llama-3.1 transferring cleanly to Llama-3.3 on Insider Trading, which is not obviously a stable transfer. A follow-up that maps out the layer × dataset × metric surface (rather than reporting AUROC at one chosen layer) would clarify how brittle the deployment claim is.

3. **The black-box baseline is not actually beaten.** GPT-4o classifying full transcripts performs comparably to the probe. The paper's "white-box is promising" framing rests on the per-token analysis (Figure 5) showing the probe fires before explicitly deceptive text is generated. A setting where a black-box judge demonstrably cannot detect the deception (e.g. responses with no overt deceptive content, or where CoT is hidden) is needed to make the white-box claim load-bearing. The paper acknowledges this as future work but does not demonstrate it.

4. **Sandbagging is prompted, not password-locked.** The Sandbagging condition uses a system prompt that walks the model through a step-by-step procedure to sandbag. Whether probes trained on Instructed-Pairs transfer to password-locked sandbagging (van der Weij et al. 2024) — where the induction mechanism does not depend on an explicit deception instruction — would test whether the probe tracks the deception representation or the in-context instruction-following.

5. **Mechanism of the probe direction.** The paper treats the probe as a black-box classifier and does not investigate what features make up the direction, how it relates to known interpretability artefacts (refusal, persona, sycophancy directions), or whether SAE features can explain it. The SAE-probing negative result (Appendix B.2) is interesting on its own — the raw direction does not decompose cleanly in the McGrath et al. SAE basis.

6. **Robustness under adversarial pressure.** The authors flag adversarial robustness as out of scope. Whether the probe direction survives fine-tuning or prompting designed to defeat it — c.f. Bailey et al.'s obfuscated activations result — is the natural stress test, and the paper does not run it.

## See also

- [[deception_probe_bench]] — direct follow-up benchmarking these exact probes against an LLM-judge baseline across five datasets; shows the white-box advantage is +0.04 to +0.14 AUROC on four datasets and −0.12 on Backdoors
- [[better_deception_probes]] — extends the methodology to Gemma 2 9B with a 16-type deception taxonomy of contrast prompts; shows system-prompt choice explains 70.6% of probe-AUC variance
- [[sleeper_agent_probes]] — sibling probe methodology (MacDiarmid et al.) on backdoored sleeper agents; this paper's "Are you being deceptive? Yes/No" comparison probe is built directly on that recipe, and surprisingly points in the *opposite* direction here
- [[persona_vectors]] — closely related linear-direction-from-contrast recipe applied to persona/trait axes
- [[sandbagging]] — provides the password-locked induction method this paper does not test against (only prompted sandbagging from Benton et al.)
- [[noise_injection_sandbagging]] — orthogonal grey-box elicitation approach to the sandbagging detection problem
- [[anti_scheming_training]] — argues a substantial fraction of apparent scheming/deception reductions are driven by eval-awareness, sharpening the question of what this probe actually tracks
- [[steering_eval_aware]] / [[probing_steering_eval_aware]] — evidence that eval-awareness itself has linear structure, relevant to the scenario-relatedness confound the paper itself surfaces
- [[high_stakes_probes]] — adjacent probe-deployment question
- [[beyond_linear_probes]] — methodological alternatives when linear probes are insufficient
