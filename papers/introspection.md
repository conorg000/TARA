# Signs of introspection in large language models

**Authors:** Anthropic (specific leads not surfaced in post)
**Year:** 2025 (October)
**Source:** [anthropic.com/research/introspection](https://www.anthropic.com/research/introspection)
**Status:** read

---

## Summary (in our words)

The methodological hook is *concept injection*. The researchers identify a concept's neural-activity signature by recording activations on prompts that should evoke it, then inject that activation pattern into an unrelated prompt and ask the model whether it notices anything. If the model can identify the injected concept, that's evidence of introspective access — the model has read-out access to its own internal state.

The most production-relevant result: Claude Opus 4.1 succeeds in only ~20% of injection trials (after subtracting false-positive baseline). Smaller models don't show a consistent deficit — introspection capability is weakly correlated with general capability. The "sweet spot" framing matters: injections that are too weak go undetected, too strong cause hallucinations. The functional capability exists but is fragile.

The authors are explicit about the threat-model implication that matters most for us: "A model that understands its own thinking might even learn to selectively misrepresent or conceal it." Introspective capability is a *prerequisite* for strategic concealment of internal states. If the model can't detect its own internal state, it can't selectively hide it. If it can detect it, the question of *whether* it discloses honestly becomes load-bearing.

This pairs tightly with [[behavioral_self_awareness]] and [[cot_faithfulness]]: behavioral self-awareness shows the model can verbalize learned behaviors; introspection (this paper) shows the model has limited but real access to its own activations; CoT faithfulness shows the model often *doesn't* verbalize what it actually uses. The three together describe a model that has some introspective access but doesn't reliably share what it sees.

## Key experimental conditions

- Models: Claude 3, 3.5, 4 family (Opus/Sonnet/Haiku variants); Opus 4.1 production + "helpful-only"; base pretrained models for comparison
- Method: concept injection — record activation patterns from concept-evoking prompts, inject into unrelated prompts, query model about detection
- Three claim families tested: detect injected concepts in real-time; identify unintended outputs as unintended; control internal representations on instruction

## Key quantitative results

- Claude Opus 4.1: ~20% awareness in injection trials (detection minus false-positive baseline)
- Opus 4/4.1 outperformed other models but smaller models showed no consistent deficit
- Most trials fail — introspection is intermittent, not a default capability

## Methods (what they did and didn't use)

- Activation injection (transplanting recorded activation vectors into unrelated contexts)
- Behavioral measurement of model's self-report on injected content
- **No linear probes per se, but the activation-vector approach is probe-adjacent** — the activations being injected are derived from concept-specific contrasts
- Compared model self-report (behavioral) against ground-truth (the known injected concept) — but doesn't directly compare self-report against a probe-readout of the same activations

## Authors' stated limitations / future work

- Introspection works only at sweet-spot injection strength; brittle outside it
- Most trials fail; capability is rare, not reliable
- No naturalistic-condition testing — all in artificial injection setups
- Mechanisms unknown; future work on introspection circuits, naturalistic validation, methods to detect confabulation

## Our own follow-up thoughts (project-relevant)

1. **Probe vs. introspection on the same inputs.** The paper's design measures "did the model report the injected concept?" but doesn't ask "did a probe trained on the concept also fire on the activations the model failed to report?" That's the dissociation we care about most. On trials where the model fails to detect the injection, does a probe trained to read off the concept still detect it? If yes, the internal state exists but the introspective channel didn't access it — useful for the "internals are more reliable than self-report" claim. This is a clean Ahmed-shaped extension if we have open-weight access.

2. **Failure-mode taxonomy.** The paper bins introspective success into "non-detection" and "hallucination." A probe-based follow-up could split these further: cases where the probe says the activation is present but the model says no (silent failure), versus cases where the probe says nothing's there but the model hallucinates one (confabulation). The two are very different threats — silent failure is the eval-gaming-relevant one.

3. **Connection to sandbagging-probe project.** This paper provides direct motivation: even when models have introspective access, they exercise it intermittently. So even if a sandbagging model "knows" it's sandbagging, asking it to verbalize this will work some of the time and fail most of the time. The probe-based detection bypasses that intermittent channel entirely.

## Relevance to our project

High. Methodologically adjacent to MacDiarmid (uses activation manipulation), conceptually connected to behavioral self-awareness and CoT faithfulness. The strongest single sentence for our project is the paper's own: "A model that understands its own thinking might even learn to selectively misrepresent or conceal it." This is the catastrophic-risk story spelled out plainly.

Pairs with: [[behavioral_self_awareness]], [[cot_faithfulness]], [[sleeper_agent_probes]].
