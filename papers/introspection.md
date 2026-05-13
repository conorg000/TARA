# Signs of introspection in large language models

**Authors:** Anthropic (specific leads not surfaced in post)
**Year:** 2025 (October)
**Source:** [anthropic.com/research/introspection](https://www.anthropic.com/research/introspection)
**Status:** read

---

## Summary (in our words)

The methodological hook is *concept injection*. The researchers identify a concept's neural-activity signature by recording activations on prompts that should evoke it, then inject that activation pattern into an unrelated prompt and ask the model whether it notices anything. If the model can identify the injected concept, that's evidence of introspective access — the model has read-out access to its own internal state.

The headline result: Claude Opus 4.1 succeeds in only ~20% of injection trials (after subtracting false-positive baseline). Smaller models don't show a consistent deficit — introspection capability is weakly correlated with general capability. The "sweet spot" framing matters: injections that are too weak go undetected, too strong cause hallucinations. The functional capability exists but is fragile.

The authors are explicit about the threat-model implication: "A model that understands its own thinking might even learn to selectively misrepresent or conceal it." Introspective capability is a *prerequisite* for strategic concealment of internal states. If the model can't detect its own internal state, it can't selectively hide it. If it can detect it, the question of *whether* it discloses honestly becomes load-bearing.

This pairs tightly with behavioral self-awareness and CoT faithfulness work: behavioral self-awareness shows the model can verbalize learned behaviors; introspection (this paper) shows the model has limited but real access to its own activations; CoT faithfulness shows the model often *doesn't* verbalize what it actually uses. The three together describe a model that has some introspective access but doesn't reliably share what it sees.

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

## Open questions and follow-up directions

1. **Probe-readout vs. self-report dissociation on the same activations.** The design measures "did the model report the injected concept?" but never asks "did a probe trained on the concept also fire on the activations the model failed to report?" On trials where self-report fails, is the concept still linearly decodable from the injected activations? A yes would establish that internal state and introspective access can come apart cleanly, and would quantify the gap.

2. **Failure-mode taxonomy.** The paper bins introspective outcomes coarsely into non-detection and hallucination. A finer split — cases where a probe says the activation is present but self-report says no (silent failure), versus cases where the probe says nothing's there but self-report invents one (confabulation) — would clarify whether introspection failures are perceptual, communicative, or both.

3. **Naturalistic conditions.** All evidence is from artificial injection. Whether models exhibit any analogous introspective access to their own *spontaneously arising* internal states — without injected activations — is unaddressed and arguably the more deployment-relevant question.

4. **Mechanism and locus.** The paper is silent on where introspection happens: which layers, which heads, whether it routes through specific circuits, and whether the ~20% success rate reflects a noisy channel or rare engagement of a reliable one. Mechanistic follow-up is open.

5. **Scaling and training-recipe effects.** Opus 4/4.1 outperform others but smaller models don't show a clean trend. Whether RLHF, constitutional training, or specific post-training steps boost introspective access — and whether scale alone would close the gap — is unknown.

## See also

- [[behavioral_self_awareness]] — complementary capability: verbalizing learned behaviours rather than detecting injected activations
- [[cot_faithfulness]] — pairs naturally; introspective access exists but reasoning traces often don't reflect it
- [[looking_inward]] — adjacent work on models reporting their own internal states
- [[sleeper_agent_probes]] — probe-side methodology that the proposed self-report-vs-probe dissociation would build on
- [[eliciting_secret_knowledge]] — overlapping question of when models can be made to reveal what they internally represent
- [[persona_vectors]] — activation-injection methodology applied to a different question
