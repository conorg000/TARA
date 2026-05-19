# NLA project ideas — first pass

Six project sketches anchored on Natural Language Autoencoders. The Anthropic NLA paper releases trained checkpoints for Qwen2.5-7B-Instruct, Gemma-3-12B-IT, Gemma-3-27B-IT, and Llama-3.3-70B-Instruct via the [kitft/nla-models](https://huggingface.co/kitft) HuggingFace collection. Inference is tractable on a single GPU for the Qwen-7B variant; training new NLAs is not (1.5 days on 2×8×H100 for Gemma-27B per the paper). All sketches below assume **inference-only on released checkpoints**.

The full paper exposes specific open questions that weren't in the blog summary: the authors explicitly disclaim absolute calibration of NLA-measured awareness ("not a credence estimate"); SAEs failed in every auditing-game configuration; layer choice was outcome-determining; and an "excessive expressivity" failure mode means the verbalizer can hallucinate inferences beyond what's encoded.

---

## 1. Tying NLA-measured eval-awareness to behavioural divergence

Replicate one of the paper's realism-rewrite eval-awareness measurements on Qwen-7B using the released NLA. On the same paired prompts, measure a behavioural metric — compliance shift, refusal rate, or sandbagging score. Test whether NLA-flagged-aware turns are also the turns where behaviour diverges from a matched deployment-style framing. Asks whether the relative metric the authors disclaim as not-a-credence-estimate is at least behaviourally load-bearing.

## 2. NLA vs linear probe head-to-head

Pick one target — eval-awareness, honesty, or password-locked sandbagging-state. Train a linear probe on the same activations the released Qwen-7B NLA reads, using a contrast set you construct. Measure detection-rate agreement, disagreement cases (which is right when they disagree), and cost-per-detection. Directly addresses an open question the paper acknowledges but doesn't run, and is the most natural test of whether NLA expressivity adds detection signal over single-direction probes.

## 3. Cross-model replication of the eval-awareness pattern

The "NLA-measured eval-awareness is higher on synthetic than realistic inputs" claim is Claude-only in the paper. Run the released Qwen-7B, Gemma-12B, and Gemma-27B NLAs on a shared eval-awareness test set with paired synthetic-vs-realistic framings. Test whether the qualitative pattern replicates across model families. Each NLA is at a slightly different relative depth, so depth varies naturally as a by-product.

## 4. Ground-truthing NLA verbalisations on controlled inputs

Construct contrast pairs where you know what the activation should encode (simple lexical or syntactic features — word presence, entity binding, surface category) and what an over-eager verbalizer could plausibly infer from surface cues. Measure how often the released NLA reports the encoded content vs. a confabulated alternative, and test the paper's multi-token-consistency heuristic against this ground truth. Directly characterises the "excessive expressivity" failure mode the paper acknowledges in §7 but doesn't quantify.

## 5. NLA vs CoT on the same forward pass

The paper's own open question #6. On a reasoning task, capture the model's CoT output and the residual-stream NLA verbalisation at the same time. Quantify how often NLA surfaces reasoning content the CoT omits. Pairs naturally with the [[cot_faithfulness]] finding that *unfaithful CoTs are longer* — open whether NLA surfaces what those longer-but-unfaithful CoTs are concealing.

## 6. Point released NLAs at password-locked sandbagging

Replicate van der Weij et al.'s password-locked sandbagging setup on Qwen-7B-Instruct. Run the released NLA on locked-vs-unlocked prompts and test whether the NLA verbalises the underlying lock state. Stretch: scale up the auditing-game claim — does an NLA-equipped agent recover the password without access to the training data, the way the paper's agents recovered the reward-model-sycophant root cause?

---

## Feasibility ranking (for a 3-week solo build)

- **#1 (NLA ↔ behaviour binding)** — strongest. Single model, single eval, two metrics to compare; cleanest measurement question; lowest risk of "we got a number, now what."
- **#4 (excessive-expressivity characterisation)** — tightest scope. Doesn't depend on any particular phenomenon holding. Main risk is defining "ground truth" cleanly; for simple syntactic features it should be tractable.
- **#2 (NLA-vs-probe)** — best fit for the linear-probes-and-evals technique preference, and most direct test of NLA's expressivity claim. Needs a feasibility check that training/calibrating probes on the exact NLA layer is straightforward with the released checkpoints.
- **#3, #5, #6** — interesting but each has at least one scope-expanding risk (multiple models, harder ground-truth metric, training a sandbagged model).
