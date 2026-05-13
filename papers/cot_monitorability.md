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

## Open questions and follow-up directions

1. **Operationalizing "monitorability".** The paper treats CoT monitorability as a property worth preserving but does not give a sharp, measurable definition. What would a quantitative monitorability score look like — faithfulness rate, coverage of consequential reasoning steps, detectability of strategic content, robustness to paraphrase? Without an operational metric it is hard to tell whether a given training intervention preserves or erodes the channel.

2. **Architectural and training-regime pressure on the channel.** The position rests on the empirical regularity that current frontier models reason in human-readable language. Latent-reasoning architectures, RL on outcome-only rewards, and continuous-thought variants each plausibly compress reasoning into forms that are less legible. Which of these pressures matters most, and at what scale, is an empirical question the paper flags but does not resolve.

3. **Complementary oversight channels.** The paper argues for protecting CoT monitoring without taking a strong stance on what backstops it when faithfulness fails. Internal-state methods (probes, SAEs, activation-based detectors) are the obvious candidate complement, but how they should be combined with CoT-based oversight — and what guarantees the combination buys — is open.

## See also

- [[cot_faithfulness]] — empirical evidence that CoT often does not reflect the reasoning the model actually uses; directly bears on how much weight monitorability can carry
- [[anti_scheming_training]] — case study where CoT-based analysis is load-bearing and whose conclusions are contingent on CoT being faithful
- [[illusion_of_thinking]] — related skepticism about whether CoT tokens reflect underlying computation
- [[deception_probes]] — example of an internal-state oversight channel that does not depend on CoT faithfulness
- [[science_of_scheming]] — broader research-agenda framing for the oversight problem this paper addresses
