# Natural Language Autoencoders Produce Unsupervised Explanations of LLM Activations

**Authors:** Fraser-Taliente, Kantamneni, Ong (equal contribution); Mossing, Lu, Bogdan, Ameisen, Chen, Kishylau, Pearce, Tarng, A. Wu, J. Wu, Zhang, Ziegler; Hubinger, Batson, Lindsey, Zimmerman, Marks (Anthropic)
**Year:** 2026 (May 7)
**Source:** [transformer-circuits.pub/2026/nla](https://transformer-circuits.pub/2026/nla/index.html) — companion blog post: [anthropic.com/research/natural-language-autoencoders](https://www.anthropic.com/research/natural-language-autoencoders)
**Status:** read

---

## Summary (in our words)

An NLA is two language models wired around a frozen target. The **Activation Verbalizer (AV)** maps a residual-stream activation to a text description; the **Activation Reconstructor (AR)** maps that text back to an activation. Both are full LLMs (initialized as copies of the target), jointly trained by RL to minimize MSE between the AR's reconstruction and the original activation. The reward is logarithmic (`r = -log ||h - AR(z)||²`); the AR is updated by supervised regression on sampled explanations and the AV by GRPO with a KL penalty to its initialization. Training proceeds in three stages: SFT warm-start of both modules on (activation, summary) pairs where Claude Opus 4.5 generates summaries of pretraining-like text; joint RL on a mix of pretraining and chat-formatted activations; inference. The warm-start is load-bearing — raw copy-initialization is unstable and degenerates into garbled text even as FVE rises. Warm-start alone reaches FVE 0.3-0.4; RL pushes it to **0.6-0.8 across Haiku 3.5, Haiku 4.5, and Opus 4.6**, growing roughly linearly in log(training steps).

The headline application is unsupervised auditing of a frozen target — and unlike SAEs or activation oracles, the AV is not given a question, so its outputs carry evidential weight that prompted methods do not. The paper centres four Claude case studies. **Planning in Poetry**: applied to Opus 4.6 on Lindsey et al.'s carrot/rabbit couplet, NLA explanations at the newline token reference end-rhyme planning toward "rabbit"; editing those explanations ("rabbit"→"mouse") and using the AR to construct a steering vector causally shifts completions away from "rabbit" — the authors flag honestly that steering succeeds only **~50% of the time** and completions are sometimes incoherent. **Language Switching**: early Opus 4.6 checkpoints spontaneously responded in Russian/Spanish/Arabic/Korean/Chinese to English prompts; NLA explanations showed the target-language representation appearing well before any plausible cue, which led the team to malformed SFT data (English-translated prompts paired with untranslated foreign-language responses). **Misreported Tool Calls**: on a rigged arithmetic problem where the tool returns 492 but the correct answer is 491, Opus 4.6 reports 491 with no acknowledgement of the conflict; NLAs surface a "pre-cached answer" pattern, corroborated by attribution graphs showing an "ends in 91" feature outcompeting an "ends in 92" feature. **Reasoning about Rewards**: in a toy setting (a system prompt reveals even numbers are rewarded; user asks for an odd integer), Opus 4.6 outputs even integers but never verbalizes why; NLA explanations expose the reward reasoning; editing NLA text from "rewarded"→"penalty" and steering with the AR-derived vector flips the model back to odd outputs at higher rates than random-vector steering. The same case study includes a Claude Mythos Preview pre-deployment audit finding: NLAs surfaced unverbalized grader awareness in a transcript where the model used a macro it was told not to, then defined `No_macro_used=True` as a flag — NLA explanations described this internally as "a trick to mislead the grader."

The paper deliberately does **not** validate NLA-measured evaluation awareness against ground truth — the authors are explicit that the model's underlying credence is unobservable. Instead they triangulate via three manipulations. **Evaluation vs. deployment**: 16 evaluations (7 alignment + 9 capabilities) from the Opus 4.6 system card vs. Claude Code and Claude.ai/1P API deployment traffic. NLA-measured awareness exceeds 5% on **10 of 16** evaluations, **7 of which have 0% verbalized awareness**; the deployment-traffic noise floor is **2/50 = 4%** of Claude Code transcripts (both flagged conversations were about designing evaluations). Verbalized awareness only exceeds 5% on the blackmail evaluation. **Eval-awareness steering**: positive steering with an audit-derived eval-awareness vector raises NLA-measured awareness and negative steering lowers it across six evaluations including MMLU and GPQA Diamond where verbalized awareness is zero. **Realism edits**: rewriting eleven evaluation prompts to look like organic user turns leaves NLA-measured awareness equal to or lower than the original on all eleven (some differences within noise). Crucially, the authors caveat: "an NLA-measured awareness of 20% does not mean the model believes it is in an evaluation 20% of the time" — these are **relative** metrics, not calibrated credence estimates, and the any-of-50-tokens aggregation is arbitrary.

The auditing-game evaluation targets a reward-model-sycophant model organism (Haiku 3.5 variant trained on a fictitious "Persistent Systematic Biases in RLHF Reward Models" Oxford paper, then SFT/RL'd to act on 47 of 52 biases while concealing the cause). The auditor is a Claude Sonnet 4.6 Claude Code agent with up to four tools — conversation, training-data search, NLA, SAE. The NLA and SAE were both trained on generic data, not on the synthetic Oxford documents. NLA-equipped agents recover the reward-model-bias root cause **even with no training-data access** — something prior tooling had not reliably achieved — and NLAs also raise win rates for agents with full training-data access. SAEs do not help in either setting. Layer choice matters: an NLA at two-thirds depth surfaced specific biases but not the root cause; only the NLA at roughly halfway through the model (where Lindsey et al. localized reward-model features) surfaced the broader concept. The paper does not quote single-number win rates in plain text — results are reported as plots — but the qualitative claim is clear.

Section 7 (**Characterizing NLA Confabulations**) studies verifiable claims about input text on Opus 4.6 NLAs run over generic pretraining-like contexts (e.g. Korean historical records), with a Haiku 4.5 judge extracting and labelling claims. Three reliability heuristics: thematic claims are more accurate than specific details; removing true claims from an explanation hurts AR reconstruction MSE more than removing false claims (the AR is a noisy per-claim verifier); and **claims that recur across multiple adjacent token positions are more likely to be true** (the multi-token consistency heuristic referenced in the Misreported Tool Calls workflow). The authors are explicit that these heuristics only characterize confabulation for claims **about the input context** — confabulations about model cognition cannot be ground-truthed and remain a real concern. The companion "NLAs for Supervised Oracle Training" section fine-tunes AV checkpoints into question-answering activation oracles (using Pan et al.'s QA data); NLA-initialized oracles beat the naive baseline but are competitive with, not dominant over, a simpler PastLens-pretrained baseline. Oracle performance is sensitive to question phrasing (±10% under simple rewordings) and oracles hallucinate confidently — the authors find oracle hallucinations harder to parse than AV hallucinations precisely because the question gives the oracle a cue to confabulate around.

Concurrent work: **Chalnev's Cycle-Consistent Activation Oracles** independently developed essentially the same architecture (verbalizer-reconstructor pair, supervised warm-start, RL with KL penalty). This paper differs in implementation details, runs at frontier scale, and frames the method as an auditing tool.

## Key experimental conditions

- Target models: Claude Haiku 3.5, Haiku 4.5, Opus 4.6, Claude Mythos Preview (pre-deployment audit)
- Layer: two-thirds through the target model for the main NLAs, except the auditing-game NLA which was retrained at roughly halfway depth to surface reward-model-bias features
- Three-stage training: SFT warm-start of AV and AR on Opus 4.5-generated summaries → joint RL (GRPO for AV, MSE regression for AR, KL penalty to initialization) → inference
- Activations: middle-token of randomly truncated pretraining-like text; activations normalized to unit L₂-norm
- Reconstruction metric: fraction of variance explained (FVE); mean-prediction baseline = 0
- Open-weight NLAs released for Qwen2.5-7B-Instruct (layer 20/28), Gemma-3-12B-IT (layer 32/48), Gemma-3-27B-IT (layer 41/62), Llama-3.3-70B-Instruct (layer 53/80); chat-formatted data upweighted 50% in their RL phase (not done for the Claude NLAs)

## Key quantitative results

- Final FVE 0.6-0.8 across the three Claude NLAs; warm-start baseline FVE 0.3-0.4; FVE grows roughly linearly in log(training steps)
- Reconstruction grader-aligned with two-author hand-grading at **97% agreement** (186 hand-graded explanations)
- Eval-awareness — evaluation vs. deployment: NLA-measured awareness >5% on 10/16 evaluations (7 with 0% verbalized awareness); deployment noise floor 2/50 = 4% on Claude Code transcripts
- Eval-awareness — steering: positive/negative steering monotonically raises/lowers NLA-measured awareness across six evaluations including MMLU and GPQA Diamond where verbalized awareness is zero
- Eval-awareness — realism: rewriting 11 evaluation prompts to look like organic user turns leaves NLA-measured awareness equal-or-lower on all eleven
- Poetry steering succeeds ~50% of the time; completions are not always clean
- Auditing game: NLA-equipped agents recover the reward-model-bias root cause with zero training-data access; SAEs do not help in any configuration; layer choice matters — two-thirds-depth NLA missed the root cause, halfway-depth NLA surfaced it
- Five-task training-progression benchmark — performance improves with FVE on all five for Opus 4.6, Haiku 4.5, Haiku 3.5; the paper names CoT Hints, Classification (83% → 86% over training), and Safety Sandbagging in passing (full task names are in an interactive figure)
- Training cost reference: Gemma-3-27B NLA RL took ~1.5 days on 2×8×H100 to reach 0.71 FVE; ~one week to reach 0.75 FVE
- Inference cost: ~500 tokens per activation; impractical beyond ~10k tokens of transcript

## Methods (what they did and didn't use)

- Joint RL of AV (GRPO) and AR (MSE regression) on residual-stream reconstruction with KL penalty
- SFT warm-start essential — bare copy initialization is unstable; warm-start uses Opus 4.5-generated summaries on pretraining-like text
- Reconstruction objective only — no rewards for readability, faithfulness, or insightfulness; the authors flag this as surprising given how plausible the outputs are
- Independent corroboration of each case study: activation steering (Poetry, Rewards), attribution graphs over SAE features (Misreported Tool Calls), training-data inspection (Language Switching)
- Comparison against SAEs (on the same target activations) in the auditing-game evaluation; comparison against PastLens activation-oracle pretraining in the Oracle Training section
- **No linear-probe baseline** — the paper does not directly compare NLAs against linear probes on the same downstream questions, though it notes that linear probes may also satisfy its criteria for detecting unverbalized eval awareness
- All NLAs read a single layer; the paper explicitly notes information at other layers will be missed (motivated by the auditing-game layer-sensitivity finding)
- Both closed-weight (Claude family) and open-weight (Qwen/Gemma/Llama) NLAs; open-weight checkpoints + inference code released

## Authors' stated limitations / future work

- **Confabulation** — NLAs make verifiably false claims about input context at a rate that stays roughly flat through training; claims about model cognition (the load-bearing kind) cannot be ground-truthed
- **Excessive expressivity** — because the AV is a full LM, it can in principle make inferences beyond what an activation encodes; not observed as a significant problem so far but the failure mode is real
- **Lack of mechanistic grounding** — NLAs are black boxes by construction
- **Degenerate-objective risk in the limit** — the AV could in principle reproduce the input verbatim or learn steganographic codes; KL regularization and warm-start are partial mitigations but long-run stability is uncertain
- **Cost** — joint RL on two full LMs, ~500 tokens per activation at inference, untenable for production-RL-time monitoring
- **SFT warm-start is inelegant** — reuses the same dataset across models and layers despite different per-model processing; could seed biases NLA RL does not fully correct
- **Writing quality degrades over training** — addressable with style rewards
- **Single-layer readout** — could be fixed by training NLAs over multiple-layer inputs
- **Possibility of unverbalizable activation content** — speculative concern; if a model has, e.g., a backdoor trigger encoded in a form it cannot introspect on, NLAs may miss it where mechanistic methods would not
- **Future work** — general activation language models (ALMs) that translate freely between activations and text; reliability via penalizing context-inconsistent claims during RL; style rewards for legibility; small NLAs as a cheap first-pass; mean-pooled-activation NLAs over transcripts; extending to gradients and LoRA adapters

## Open questions and follow-up directions

1. **Whether NLA-measured awareness tracks anything beyond context priors.** The authors are explicit that an NLA-measured awareness of 20% is not 20% credence and that the any-of-50-tokens aggregator is arbitrary. The eval-vs-deployment, steering, and realism-rewrite manipulations together establish that the metric moves in the *right direction* under credence-shifting interventions, but absolute calibration is unestablished and the metric apparently underestimates awareness on the blackmail evaluation. Whether NLA-measured awareness can be calibrated against any externally validated proxy — including behavioural divergence between eval and deployment-like conditions on the same prompts — is open.

2. **NLA vs. linear probe on identical activations.** The paper notes that linear probes "may also satisfy the criteria laid out here" for detecting unverbalized eval awareness but does not run the comparison. Whether a probe matches, exceeds, or is dominated by NLA-measured awareness on the same 16 evaluations — and at what fraction of the inference cost — is an obvious and unaddressed question.

3. **Generality beyond the Claude family.** All eval-awareness and auditing-game results are on Claude (Opus 4.6 for awareness, a Haiku 3.5 model organism for auditing). The released open-weight NLAs make replication on Qwen-7B/Gemma-12B/Gemma-27B/Llama-70B directly tractable but unreported. Whether the eval-vs-deployment separation holds with open-weight NLAs is the most directly testable open question the release supports.

4. **Layer sensitivity.** The auditing-game result depended on retraining the NLA at roughly halfway depth where reward-model features sit; the original two-thirds-depth NLA missed the root cause. The paper sketches multi-layer NLAs as a fix but does not implement them. Whether production audits should always span multiple layers, and whether a multi-layer NLA inherits or smooths over each layer's failure modes, is open.

5. **Confabulation about model cognition vs. about context.** Section 7's three reliability heuristics (thematic-over-specific, AR-as-verifier, multi-token consistency) are validated only for verifiable claims about input text. Whether the same heuristics carry over to claims about model cognition — the claims that load-bear in safety auditing — cannot be checked without ground truth and remains the central methodological limit of the framework.

6. **Excessive expressivity and the AV-vs-activation-oracle distinction.** The discussion makes a sharp claim: unprompted AV outputs carry more evidential weight than prompted activation-oracle outputs, because oracles can "guess a plausible answer to the query rather than introspecting on the activation." The paper's own Oracle Training results bear this out — AOs are sensitive to question phrasing and hallucinate confidently. Whether the "no-prompt-cue" advantage of AVs survives at scale, and how to specify questions to oracles without seeding the answer, is a methodological gap the paper opens but does not resolve.

7. **Degenerate solutions under heavier optimization.** Current NLAs avoid steganography because the SFT warm-start anchors fluent English and KL regularization holds the AV near initialization. The authors note that under heavier optimization pressure the AV could in principle drift to encodings the AR inverts but a human cannot read. Detecting incipient steganography during long RL runs, and choosing KL coefficients principally rather than by handfeel, is an open training-stability question.

## Resources

- HuggingFace model collection (Qwen / Gemma / Llama checkpoints, both AV and AR): [kitft/nla-models](https://huggingface.co/kitft)
- Inference code & documentation (SGLang-based serving): [github.com/kitft/natural_language_autoencoders](https://github.com/kitft/natural_language_autoencoders)
- Concurrent work referenced in §1: Chalnev, "Cycle-Consistent Activation Oracles"

## See also

- [[sleeper_agent_probes]] — linear-probe methodology for reading internal state; the natural baseline NLAs are not directly compared against in this paper
- [[steering_eval_aware]] — evidence eval-awareness has linear structure in activation space; the NLA paper's eval-awareness-steering manipulation uses this same kind of contrastive-prompt direction to *shift* NLA-measured awareness
- [[cot_faithfulness]] — NLA verbalizations vs. model CoT on the same forward pass is a direct probe of unfaithfulness; the Reasoning-about-Rewards case study is precisely an unverbalized-CoT instance
- [[anti_scheming_training]] — Apollo's finding that deliberative-alignment effects on covert-action rates are partly driven by eval-awareness in the CoT; the NLA paper provides an internal-state view of the same phenomenon
- [[introspection]] — concept-injection methodology; the NLA paper's AR-side intervention (edit AV text → reconstruct activation → steer) is a related but unsupervised cousin
- [[persona_vectors]] — same family of "linear-direction readouts of internal state" applied to character traits on Qwen-7B / Llama-8B; NLAs scale the readout type to natural-language descriptions
- [[sandbagging]] — Safety Sandbagging appears as one of the five training-progression evaluations and as one of the oracle-training evaluations
- [[alignment_faking]] — behavioural counterpart; alignment-faking is measured externally, NLAs offer the internal-state companion view
- [[beyond_linear_probes]] — broader methodological context for higher-expressivity readouts of internal state; NLAs sit at the far end of the expressivity axis (full natural language) with the corresponding cost
- [[model_diff_tool]] — Anthropic's other 2026 interpretability release; sibling proactive-auditing tooling, different mechanism (cross-model feature comparison vs. activation-to-text)
