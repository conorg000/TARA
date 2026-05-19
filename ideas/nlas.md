## Replicate Anthropic's own eval-awareness measurement on open weights.
  The headline NLA finding (eval awareness >5% on 10/16 evals vs 4% deployment baseline) was Claude-only.
  Anthropic released NLAs for Qwen-7B, Gemma-12B, Gemma-27B, Llama-70B. So you just... do their exact
  procedure on the open model. Pick eval prompts and deployment-style prompts, run the released NLA, count
   how often it verbalizes eval-awareness in each set. Does the pattern hold? If yes, the finding
  generalises and the released NLAs are usable for this kind of audit. If no, the Claude result is
  closed-model-specific and we should know that.

## NLA vs linear probe on the same activations.
  The NLA paper itself flags this as an open question and doesn't run it. Pick any target —
  eval-awareness, sandbagging, sycophancy, refusal — train a linear probe on Qwen-7B, also run the NLA on
  the same activations. Where do they agree? Where do they disagree? Which is right when they disagree? At
   what fraction of the inference cost? This is the obvious sanity check on the whole "NLAs are a
  higher-expressivity readout than probes" pitch, and nobody has done it.
    NLA is being sold to the field as a better readout of internal state than the older linear-probe methods
   — better because it produces sentences instead of single numbers, and because it's unsupervised. That
  claim is the load-bearing pitch for the whole research direction. Anthropic is presumably investing real
   money in NLAs as a future safety-auditing tool because they think it adds something. And the field is
  currently citing the NLA paper as if the claim is established.

  But the paper itself never compares NLAs to probes on the same task. They compared NLAs to SAEs (NLAs
  won in the auditing game). They never compared NLAs to the obvious cheaper baseline. The authors flag
  this explicitly — they say probes "may satisfy the criteria" they laid out — but then they don't run the
   comparison.

  So the load-bearing claim for the entire 2026 NLA programme is unverified. That's the fundamental gap.
  Everything downstream of NLA work assumes NLAs do something probes don't, and that assumption has never
  been directly tested.

  **What the paper actually says about probes (verified against the raw HTML — WebFetch's summary missed all of this; grepping the source found 11 hits on "probe").**

  The paper does discuss probes in four substantive places, just doesn't run any experiments. Direct quotes:

  - *"we also note that other interpretability techniques, such as linear probes, may also satisfy the criteria laid out here for detecting unverbalized evaluation awareness."* — explicit acknowledgment that probes might do the same job.
  - *"the AV could in principle perform inference beyond what the activation encodes and describe structure that is not actually present. This is in contrast to sparse autoencoders or probes, which are simple linear operations applied to activations and presumably have less capacity to hallucinate."* — probes are *less likely to confabulate* than NLAs. Authors concede this.
  - *"Mechanistic methods that rely on linear representations in activations, like sparse autoencoders and linear probes, may miss such information [stored nonlinearly]."* — NLAs *might* read information probes can't, if it's nonlinearly encoded. "May" is doing a lot of work — not demonstrated.
  - *"SAEs or linear probes might scale"* where NLAs cannot, because of the 500-tokens-per-activation inference cost.

  This makes the project pitch *stronger*, not weaker. The paper sets up two specific competing theoretical claims and tests neither:

  - **NLA prediction (pro-NLA):** there will be cases where NLA reads something the probe misses, because the information is nonlinearly encoded.
  - **Probe prediction (anti-NLA):** NLA will hallucinate more often than the probe — outputting plausible-sounding text not actually grounded in the activation.

  Both can't be uniformly true in the same direction. A head-to-head comparison that identifies disagreement cases and uses a third method (behaviour, steering, attribution) to break ties is exactly the experiment that adjudicates between the two competing predictions the paper named but didn't resolve.

  **Refined pitch.** Not "compare NLA vs probe to see who wins" — but: *find the boundary that decides which method dominates where, using the paper's own competing theoretical claims as the framing.* Identify cases where the two methods disagree, then use behavioural / steering / attribution-graph evidence to determine which is right. The disagreements are where the interesting science lives.

## Ask the NLA what's in a steering vector.
  People build "steering vectors" all the time by averaging activations from contrasting prompts (the CAA
  recipe). The vector is supposed to capture something like "survival instinct" or "refusal." But nobody
  actually checks what's in there — we just check whether the vector moves behaviour in the expected
  direction. The NLA has a reconstructor that goes text → activation, but it also has the verbalizer going
   activation → text. So you can literally take a CAA steering vector and feed it in. What words does the
  NLA spit out? Does "refusal" come back as "refusal" or as "the assistant is being cautious" or as "this
  looks like a benchmark"? Super clean test of whether the contrast-pair recipe is doing what we think.