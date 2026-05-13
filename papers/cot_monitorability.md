# Chain of Thought Monitorability: A New and Fragile Opportunity for AI Safety

**Authors:** Korbak, Balesni, Barnes, Bengio, Benton, Bloom, Chen, Cooney, Dafoe, Dragan, Emmons, Evans, Farhi, Greenblatt, Hendrycks, Hobbhahn, Hubinger, Irving, Jenner, Kokotajlo, Krakovna, Legg, Lindner, Luan, Mądry, Michael, Nanda, Orr, Pachocki, Perez, Phuong, Roger, Saxe, Shlegeris, Soto, Steinberger, Wang, Zaremba, Baker, Shah, Mikulik (Anthropic, OpenAI, DeepMind, METR, UK AISI, academia)
**Year:** 2025
**arXiv:** [2507.11473](https://arxiv.org/abs/2507.11473)
**Status:** read

---

## Summary (in our words)

A coordination / position paper signed by approximately every major AI safety researcher across the major frontier labs. The position: AI systems that produce human-language reasoning enable a *new and fragile* safety oversight opportunity — chain-of-thought monitoring. It is imperfect but promising. The paper argues that this fragility warrants explicit consideration in model development, and recommends further research into preserving and validating CoT monitorability as models advance.

The "fragile" part is the load-bearing word. Several recent results threaten CoT monitorability:
- [[cot_faithfulness]] shows models often don't verbalize what they actually use.
- [[anti_scheming_training]] shows that even apparent reductions in scheming may be eval-awareness artifacts visible in CoT but not necessarily preventing the underlying disposition.
- As models move toward non-English / latent reasoning, the channel itself disappears.

The paper is not an empirical contribution. It's the consensus statement that says "CoT monitoring is one of the few safety tools we have, it's already showing cracks, and we need to invest in it deliberately before it goes away." It's the kind of paper that ends up cited as the field's collective acknowledgment of a problem.

For our project this is contextual rather than methodological. The argument it makes is *we should also have non-CoT safety channels*, which is exactly the empirical contribution probe-based work makes. Our project is doing the implicit follow-on to this position paper.

## Position summary

- CoT monitorability is a real safety capability — but new and conditional on current training practices
- It is fragile: model architectural choices, training regimes, and emergent behaviors can erode it
- The community should explicitly prioritize preserving and validating CoT monitorability in model development
- The recommendations are about norms, research priorities, and coordination — not specific techniques

## Methods (none — this is a position paper)

No experiments. No probes. No internal-state work. Coordination document.

## Authors' acknowledged limitations

- CoT monitoring "is imperfect and allows some misbehavior to go unnoticed"
- Need for further research into how to preserve and validate the channel

## Our own follow-up thoughts (project-relevant)

1. **The argument for *non-CoT* safety channels is implicit and we're making it explicit.** The paper says CoT is fragile and we should protect it. The corollary — which the paper does not state but is obvious — is that we should *also* invest in safety channels that don't depend on CoT being faithful. Probes are one such channel. Our project's positioning, in the writeup, can lean on this.

2. **Useful for citation density.** With ~40 author signatories from every major lab and academic group, this is the closest thing to a "the field agrees" paper on the CoT-monitoring question. Cite for credibility when framing why behavioral / CoT-only channels are insufficient.

## Relevance to our project

Low for methodology, medium for framing and citation. Not a target for replication.

Pairs with: [[cot_faithfulness]] (the empirical evidence that CoT is unfaithful), [[anti_scheming_training]] (an example of CoT-based analysis whose conclusions depend on CoT being faithful).
