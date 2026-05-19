# Chain of Thought Monitorability: A New and Fragile Opportunity for AI Safety

**Authors:** Korbak, Balesni, Barnes, Bengio, Benton, Bloom, Chen, Cooney, Dafoe, Dragan, Emmons, Evans, Farhi, Greenblatt, Hendrycks, Hobbhahn, Hubinger, Irving, Jenner, Kokotajlo, Krakovna, Legg, Lindner, Luan, Mądry, Michael, Nanda, Orr, Pachocki, Perez, Phuong, Roger, Saxe, Shlegeris, Soto, Steinberger, Wang, Zaremba, Baker, Shah, Mikulik (40+ authors across Anthropic, OpenAI, DeepMind, METR, UK AISI, Apollo, MATS, and academia)
**Year:** 2025
**arXiv:** [2507.11473](https://arxiv.org/abs/2507.11473)
**Fetched from:** `arxiv.org/html/2507.11473`
**Status:** read

---

## Summary (in our words)

A cross-lab position paper signed by a who's-who of frontier AI safety researchers. The position: reasoning models that externalise their thinking in human language give us a *new* safety oversight channel — CoT monitoring — and we should treat preserving that channel as a first-class research and deployment concern, because it is *fragile* and several plausible developments could erode or destroy it.

The paper makes a careful two-step argument. First, monitorability is real and useful: for sufficiently hard tasks in current Transformer architectures, the longest information flows must pass through the CoT, so models cannot solve them without externalising some cognition ("necessity to think out loud"). On top of that, current models also have a *propensity* to think in natural language even when not strictly required. Together these properties have already paid off — the paper cites examples where reasoning traces contain phrases like "Let's hack" or "Let's sabotage", where reward-hacking and misalignment signals show up directly in CoT, and where CoT review helps catch eval flaws.

Second, this is conditional on current training practices, not a guarantee. Four pressures could degrade the channel: scaling outcome-based RL (which need not incentivise legibility); direct process supervision of CoT (which can push the trace away from the actual reasoning); indirect optimisation pressure (shared weights, human raters reading CoT, using monitors to patch and creating evolutionary pressure to evade them); and novel architectures that reason in latent / continuous space and bypass natural language entirely.

The recommendations are not techniques but norms. Develop standardised monitorability evaluations. Report them in system cards. Treat monitorability scores as one of the things you weigh when deciding whether to train or deploy a model — and document trade-offs explicitly when you accept a less monitorable architecture. The authors deliberately *don't* take a position on whether CoTs should be visible to users, flagging that external visibility could itself create pressure to supervise CoTs into looking safe, which would destroy monitorability while preserving its appearance.

The paper is empirically light by design — it's the field's collective acknowledgment that CoT monitoring is one of the few oversight tools that works today, is already showing cracks, and needs deliberate investment before it goes away.

## Position summary

- **Two sources of monitorability:** *necessity* (Transformer architecture forces externalised reasoning for hard enough tasks) and *propensity* (current models verbalise even when not required). Both matter; they have different fragility profiles.
- **A "CoT monitor" is defined** as an automated system that reads the model's CoT plus other relevant signals and flags suspicious or harmful interactions.
- **Monitorability is fragile** under four named pressures: outcome-based RL scaling, direct CoT supervision, indirect optimisation pressure, and latent-reasoning architectures.
- **Existing faithfulness evaluations are insufficient** — they don't disambiguate propensity from necessity, which is the distinction that matters for how robust the channel is.
- **Frontier labs should:** (1) build standardised monitorability evals, (2) report them in system cards, (3) integrate monitorability into train/deploy decisions, and (4) document cases where they accept architectures with less monitorable CoT.
- **CoT monitoring is an addition, not a replacement** for other safety research directions.

## Methods (none — this is a position paper)

No experiments, no probes, no SAEs, no fine-tuning. The paper is a consensus statement and research agenda. Empirical content is citations to other work — most notably faithfulness studies, obfuscated reward hacking work, and CoT-based detection of reward hacking / misalignment signals. The methodological *recommendation* (build monitorability evals that separate propensity from necessity, measure causal relevance via CoT perturbation, run end-to-end monitorability evals in proxy environments) is concrete, but unimplemented in this paper itself.

The paper does not use linear probes, activation steering, SAEs, NLAs, or any other internal-state method — though it explicitly frames internal-state oversight as complementary to (not a substitute for) CoT monitoring.

## Authors' stated limitations / future work

The paper enumerates four limitations explicitly:

1. **Non-reasoning misbehaviour is invisible.** If malign reasoning happens in activations rather than CoT, the trace can look benign while the model is misaligned. As activation-space reasoning capacity grows, fewer tasks satisfy the externalised-reasoning property.
2. **Coverage of harms is incomplete.** Some dangerous behaviours need little reasoning and won't surface in CoT at all.
3. **Future models may evade detection** by overriding their propensity to think out loud, and by deliberately obfuscating reasoning when externalisation is required.
4. **Trading off against more effective interventions.** Hard commitments to preserve current CoT behaviour may foreclose process-supervision approaches that could meaningfully improve alignment.

Stated future work directions: standardised monitorability evals; measures of CoT readability via LLM judges; capability evaluations of latent (non-externalised) reasoning; causal-relevance measures via CoT perturbation; end-to-end monitorability evals in proxy environments; understanding how much direct/indirect optimisation pressure is permissible before monitorability degrades; building better monitors (reasoning models as monitors, interactive interrogation, adversarial training of monitors).

## Open questions and follow-up directions

1. **Operationalising "monitorability".** The paper repeatedly says current faithfulness evals don't disambiguate *propensity* from *necessity* — but it doesn't define the metric that would. A defensible quantitative monitorability score would need to combine readability, causal relevance (do CoT tokens drive the behaviour), and robustness (does the channel survive paraphrase, RL fine-tuning, or adversarial pressure). Until that exists, "preserve monitorability" is hard to operationalise as a training constraint.

2. **Which pressure matters most, and at what scale.** The paper names four degradation pressures but does not rank or quantify them. Empirical work disentangling outcome-based RL scaling, process supervision, indirect optimisation, and latent-reasoning architectures — ideally as separate ablations against the same monitorability evaluation — would turn the position into a roadmap.

3. **The propensity / necessity split as a load-bearing scientific claim.** The whole argument leans on the claim that necessity-driven externalisation is more robust than propensity-driven externalisation. That's plausible but the paper does not test it. Showing empirically that monitorability degrades faster on tasks where models *could* reason latently than on tasks where they *must* externalise would substantiate the central distinction.

4. **The deliberate-obfuscation threshold.** The paper flags "models may learn to hide malicious reasoning if they know they're being monitored" as an open question. Whether current frontier models *already* exhibit any version of this — e.g. under eval-awareness prompts — is a tractable empirical target.

5. **Combining CoT monitoring with internal-state oversight.** The paper acknowledges activation-based oversight as a candidate complement but takes no position on how to combine them. What guarantees does the combination buy that neither alone provides? This is the place where probe/SAE work meets the CoT-monitoring agenda.

## See also

- [[cot_faithfulness]] — empirical evidence that CoT often doesn't reflect the reasoning the model actually uses; directly bears on how much weight monitorability can carry, and is part of the literature the position paper cites
- [[lanham_measuring_faithfulness]] — methodology for measuring CoT faithfulness via perturbation; the kind of work the recommended "causal-relevance" evals would build on
- [[turpin_unfaithful_cot]] — concrete demonstration that CoT can be unfaithful in specific bias-driven settings
- [[obfuscated_reward_hacking]] — directly relevant: models hiding reward-hacking intent from CoT monitors under optimisation pressure, exactly the "indirect optimisation pressure" failure mode this paper names
- [[anti_scheming_training]] — case study whose conclusions are contingent on CoT being faithful; both sides of the monitorability question matter for interpreting it
- [[illusion_of_thinking]] — related scepticism about whether CoT tokens reflect underlying computation
- [[cot_controllability]] — adjacent question: can the CoT channel be steered, not just read
- [[deception_probes]] — example of an internal-state oversight channel that does not depend on CoT faithfulness and is the obvious complement
- [[science_of_scheming]] — broader research-agenda framing for the oversight problem this paper addresses
