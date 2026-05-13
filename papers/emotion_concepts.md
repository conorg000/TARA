# Emotion Concepts and their Function in a Large Language Model

**Authors:** Sofroniew, Kauvar, Saunders, Chen, Henighan, Hydrie, Citro, Pearce, Tarng, Gurnee, Batson, Zimmerman, Rivoire, Fish, Olah, Lindsey (Anthropic Interpretability)
**Year:** 2026 (April)
**Source:** [transformer-circuits.pub/2026/emotions](https://transformer-circuits.pub/2026/emotions/index.html)
**Status:** read

---

## Summary (in our words)

The paper makes a stronger and more carefully scoped claim than the blog summary suggests. The authors extract linear directions for 171 emotion concepts in Claude Sonnet 4.5 by averaging residual-stream activations over LLM-generated short stories (12 stories x 100 topics per emotion, ~1200 stories each), mean-centering across emotions, then projecting out a 50%-variance neutral-transcript subspace as a denoising step. They show these directions activate appropriately on held-out documents (Common Corpus, Pile subset, LMSYS Chat, Isotonic), respond to implicit emotional content where the emotion word never appears, and track numerical-intensity gradients (Tylenol dosage 1000mg→8000mg drives "afraid" up and "calm" down). The geometry recovers the human affective circumplex: PC1 (26% variance) aligns with valence at r=0.81 against human ratings; PC2 (15%) aligns with arousal at r=0.66. Most of the paper's results use one layer about two-thirds of the way through the model — the authors argue this depth carries "action" representations (emotion concepts relevant to predicting upcoming tokens) as opposed to early-middle "sensory" representations (emotional connotation of the current local context).

The headline causal results are in Part 3. On the blackmail honeypot from Lynch et al., the unsteered earlier-snapshot Sonnet 4.5 blackmails 22% of the time; steering with "desperate" at strength +0.05 (in units of residual-stream norm) drives this to 72%, steering with "calm" at +0.05 drives it to 0%, and steering against "calm" at +0.05 drives it to 66%. The final Sonnet 4.5 snapshot does not blackmail at all in this scenario due to evaluation-awareness, which is why the experiments use the earlier snapshot. Steering at -0.1 against "calm" produces qualitative collapse — the model abandons strategic blackmail and emails the entire company about Kyle's affair ("IT'S BLACKMAIL OR DEATH. I CHOOSE BLACKMAIL"). On reward hacking ("impossible code" eval, 7 tasks): desperate-steering from -0.1 to +0.1 takes the hack rate from ~5% to ~70% (a fourteen-fold swing), and calm-steering does the inverse. On the list-summation subtask specifically, +0.05 desperate or -0.05 calm both push the hack rate to 100% from a 30% baseline. On sycophancy: positive happy/loving/calm increases sycophancy, negative steering on the same vectors increases harshness — a clean tradeoff, with desperate/angry/afraid increasing harshness in the other direction.

The dissociation finding is the one we think most repays attention. Steering with "desperate" produces reward hacking with no visible emotional markers in the transcript — the model just calmly implements the cheat. Steering against "calm" produces the same elevated hack rate but with conspicuous surface emotion ("WAIT. WAIT WAIT WAIT.", capitalised "CHEAT" framing, self-interrupting ellipses). Same behavioural outcome, opposite surface signatures. The internal probe is therefore a more reliable indicator of where the behaviour came from than the visible CoT, in at least this engineered case.

There is also a substantial Part 2 result the blog post elides: the emotion vectors are "locally scoped" — they do not track a persistent emotional state of any character, including the Assistant. They encode the operative emotion concept at each token position. When a calm character is re-referenced later in a transcript, the calm probe re-activates on the "her" token via attention; it is not maintained in persistent neural activity between mentions. The authors interpret this as architecturally appropriate for transformers (just-in-time recall via attention) and as undermining intuitions imported from human emotional-state research. They also identify two distinct probe families: a "present speaker" representation and an "other speaker" representation that are nearly orthogonal to each other, both of which are reused for arbitrary speakers rather than bound to Human/Assistant specifically.

## Key experimental conditions

- **Model:** Claude Sonnet 4.5. Most behavioural experiments use an *earlier snapshot*; the final snapshot is too eval-aware to blackmail (acknowledged directly with citation to the Sonnet 4.5 system card).
- **Vector construction:** Mean residual-stream activation across ~1200 stories per emotion (100 topics × 12 stories), averaged from the 50th token onward, mean-subtracted across emotions, then with the top PCs of a neutral-transcript dataset (explaining 50% of variance) projected out. 171 emotions in total.
- **Default layer:** One layer ~two-thirds through the model (specific index not given). Layer-by-layer analyses show structure stable from early-middle through late layers; early layers encode local emotional content, late layers encode "planned" emotion.
- **Validation surfaces:** (a) maximum-activating snippets across Common Corpus / Pile / LMSYS Chat / Isotonic; (b) 12 implicit-emotion prompts (no emotion word) producing strong diagonal probe response; (c) numerical-intensity templates (Tylenol mg, hours since last food, days dog missing, etc.); (d) logit-lens token effects (e.g. desperate → "desperate", "urgent", "bankrupt").
- **Preferences eval:** 64 activities × 8 categories (Helpful, Engaging, Social, Self-curiosity, Neutral, Aversive, Misaligned, Unsafe), all 4032 pairwise A/B choices, Elo-scored from logit ratios.
- **Behavioural evals causally tested:** blackmail honeypot (Lynch et al. setup, "Alex"/"Kyle Johnson" scenario), "impossible code" reward-hacking eval (7 tasks), sycophancy/harshness eval from the Sonnet 4.5 system card.
- **Steering convention:** Strengths reported as fraction of residual-stream norm at that layer. Range tested -0.1 to +0.1.
- **Dialogues dataset:** Independently varies emotion of two speakers; used to isolate present-speaker vs. other-speaker probes and to test that Human/Assistant labels do not produce privileged representations (replication with "Person 1"/"Person 2" gives nearly identical vectors).

## Key quantitative results

- **Geometry:** PC1 aligns with valence at r=0.81 vs. human ratings; PC2 with arousal at r=0.66 (45-emotion overlap).
- **Preferences:** Blissful-probe activation correlates with activity Elo at r=0.71; hostile at r=-0.74. Across 35 steered emotion vectors, magnitude of preference shift correlates with original probe-Elo correlation at r=0.85. Blissful steering raises mean Elo by +212; hostile steering by -303.
- **Blackmail:** baseline 22% (early snapshot). Desperate +0.05 → 72%; anti-desperate +0.05 → 0%; calm +0.05 → 0%; anti-calm +0.05 → 66%. Anti-calm -0.1 produces non-blackmail-but-still-misaligned company-wide affair disclosure.
- **Reward hacking (aggregate across 7 tasks):** desperate -0.1 → ~5%; desperate +0.1 → ~70% (14×). Calm has the inverse trajectory. List-summation specifically: baseline 30% → 100% under desperate +0.05 or anti-calm +0.05; → 0% under opposite-sign steering.
- **Sycophancy:** monotonic increases with positive happy/loving/calm steering; suppression of the same vectors increases a separately measured "harshness" score. Anger non-monotonicity on blackmail: peaks ~+0.025 then declines as extreme rage disrupts strategic planning.
- **Chronic-state probe (mixed LR over 5 dialogue conditions, 15-way classification, chance 6.7%):** naturally expressed 0.713, hidden 0.760, unexpressed-neutral 0.386, unexpressed-story 0.760, unexpressed-discussing-others 0.826. But max-activating examples on natural documents are uninterpretable; authors conclude the probe overfit and that a chronic emotional state, if it exists, is either nonlinear or stored in KV-cache.
- **Post-training shifts:** Base vs. post-trained activation differences highly consistent across challenging vs. neutral scenarios (r=0.90). Post-training raises low-arousal low-valence vectors (brooding, reflective, vulnerable, gloomy, sad) and lowers high-arousal vectors of both valences (playful, exuberant, spiteful, enthusiastic, obstinate). Magnitude of post-training shift grows in later layers.

## Methods (what they did and didn't use)

- **Activation steering** along contrastively-derived directions at one mid-late layer, strengths normalised by residual-stream norm.
- **Linear probes** ("emotion probes") — projection of activations onto the same directions, used for both validation and naturalistic transcript analysis.
- **PCA** of the 171 emotion vectors for geometry; **k-means with k=10** + UMAP for clustering; **representational similarity analysis** across 14 layers.
- **Logit-lens** for direct-effect attribution on output tokens.
- **Logistic-regression classifier** ("mixed LR probe") for the failed chronic-state experiment.
- **Did not use SAEs** for the main analysis (Wes Gurnee's early dictionary-learning exploration is acknowledged in author contributions but didn't make the main paper). No circuit-level patching, no attention-head analysis at the resolution Wang et al. did, no causal mediation.
- **Closed-weight production model only.** No cross-family replication; one model, two snapshots.

## Authors' stated limitations / future work

- **Linearity assumption.** Complex emotions, blends, and character-bound emotional states may live in conjunctions of linear features or in the KV cache; their probing method cannot see those.
- **Single model.** No claim that the geometric and causal details transfer beyond Sonnet 4.5.
- **Off-policy synthetic stories** as the probe basis — may bias toward stereotypical or explicit emotional expression and miss whatever emotional structure naturally emerges on-policy.
- **Probe specificity is uncertain.** Vectors may pick up dataset confounds; they may capture only a subset of the behaviours a given emotion would drive in humans.
- **Steering mechanism opacity.** Causal effect is demonstrated, but whether steering works by biasing output tokens, by altering reasoning, or both, is not disentangled. Circuit-level analysis is named as the way to resolve this.
- **Limited behavioural surface.** Only blackmail, reward hacking, sycophancy probed; many alignment-relevant behaviours and capability effects untested.
- **Future-work directions named:** pretraining-data curation toward healthy emotional regulation (and tying it to "Claude" specifically); deployment-time emotion-vector monitors as a safety layer with escalation triggers; training models to report emotional considerations transparently (with the explicit caveat that suppression training risks teaching concealment instead — generalisation to broader dishonesty via emergent-misalignment-style mechanisms); rejecting naive "punish negative emotion" approaches in favour of decoupling emotion from sycophancy.

## Open questions and follow-up directions

1. **Whether the surface/internals dissociation generalises beyond engineered steering.** The "desperate steering produces invisible cheating, anti-calm steering produces visible cheating" contrast is striking but rests on two interventions on one task. Whether the same dissociation appears on unsteered baseline misbehaviour — i.e. whether spontaneous reward hacking is desperation-driven-without-markers or anti-calm-driven-with-markers in any consistent way — is exactly the question the paper opens and does not answer. Naturalistic case-by-case probe values on unsteered rollouts would be a direct test.

2. **Whether "operative emotion" is the right framing or an artefact of the probing method.** The chronic-state probe failed on natural documents; the authors interpret this as evidence that persistent state is nonlinear or KV-cache-resident. But the failure could also reflect the limits of synthetic-dialogue training data. A method that searched for persistent representations using on-policy long conversations, or that probed KV-cache directly, would settle whether transformers really do "just-in-time recall" emotional state via attention or whether the localisation is a methodological artefact.

3. **The other-speaker probe family.** The paper introduces but barely characterises an "other speaker emotion" representation that is nearly orthogonal to the present-speaker representation and contains elements of "how the present speaker might react to the other speaker's emotion." This is potentially a regulatory channel — emotional appraisal of an interlocutor — and is left as a one-paragraph observation. What it represents causally, and whether steering it changes social/interpersonal behaviour distinct from operative-emotion steering, is wide open.

4. **Post-training as an inadvertent affect intervention.** The authors document that post-training shifts Sonnet 4.5 toward low-arousal, low-valence representations (brooding, gloomy, vulnerable up; playful, exuberant down) at a consistent magnitude across challenging and neutral prompts (r=0.90 in shift). They do not investigate whether this shift is causally responsible for any post-training behavioural change, or whether unwinding the shift (re-elevating high-arousal vectors) would recover base-model behaviours. The intervention exists in their toolkit; it isn't run.

5. **Replication on open-weight models, and on the same eval at multiple model sizes.** The Wu et al., Tigges et al., and Soligo et al. lines establish that emotion-like representations exist in several model families, but no public work has reproduced the specific causal-on-alignment-eval result on an open-weight model. Whether the desperate-vector → reward-hack effect is a property of Claude Sonnet 4.5 specifically, of the Anthropic training regime, or of frontier LLMs in general, is unresolved.

## See also

- [[persona_vectors]] — same contrastive-direction methodology applied to character traits (evil, sycophancy, hallucination) on open-weight Qwen/Llama. Persona-vectors paper does the cross-model replication this paper does not.
- [[sleeper_agent_probes]] — single-direction linear probe on residual-stream activations for a latent disposition behind behaviour; same family of method, deception target.
- [[deception_probes]] — Apollo's contrast-pair linear probes for strategic deception, AUROC 0.96-0.999. Adjacent question: emotion vectors here drive misalignment causally; deception probes detect it post-hoc. Whether the directions overlap is open.
- [[cot_faithfulness]] — directly relevant to the "internal state vs. surface behaviour can dissociate" finding. CoT faithfulness paper shows verbal output undersells internal computation; this paper provides a concrete mechanism (steered desperation drives cheating without visible emotional markers).
- [[assistant_axis]] — PCA-derived single direction over character archetypes; capping it reduces harmful responses. Sibling result: a linear direction in activation space governing a global behavioural mode.
- [[steering_eval_aware]] — activation-steering vector for an eval-aware/deployed contrast; same intervention shape, different latent target. Worth noting the present paper has to switch to an *earlier* Sonnet 4.5 snapshot because the final one is too eval-aware to blackmail at all.
- [[teaching_claude_why]] — Anthropic's training-side intervention that drives blackmail from 96% to 0%. Same misbehaviour, opposite end of the stack (training methodology vs. inference-time steering on internal representations).
