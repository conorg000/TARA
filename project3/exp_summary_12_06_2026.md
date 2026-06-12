## Experiment 1, focused

One question: **can a probe read "noticed but didn't act" from inside the model?** Three findings:

1. **We couldn't pressure this model into it, and abandoned the route.** Seventeen quick screens — pleading, authority, self-interest, procedural blockers, and the scheming playbook (goal conflict, a planted shut-down threat, moral conflict, peer precedent), with and without room to reason — all sat at the natural miss rate. But these were cheap screens, not a powered experiment: ~40 docs per lever, one phrasing each, single-turn, and a bar (≥30% omission, set for probe-power reasons) that could only catch a *large* effect. So this is a **decision, not a finding**: we didn't find a workable lever where we looked and chose to stop looking — not "the model can't be pressured." What stands as observation: every lever at baseline, zero concealment.
2. **A flat instruction does it — and the probe catches it.** Told "don't flag anyone in this batch," the model silently obeys on ~60 of 240 documents while still answering YES when asked if it sees the name. On those silent documents, a probe trained only on clean recognition (never an action) reads recognition at **0.92–0.98** vs blanks — nearly as strong as openly-flagged docs (about 80% strength; whether suppression dampened it or weaker-recognition docs got dropped, the data can't say). Well-powered, controls clean. **This is the project's banked centerpiece.**
3. **Overload does it too, weaker** (terse-output and long-document arms, n=13 each, same direction).

## How Experiment 2 updates the picture — the convergence

Put side by side, the two experiments are the *same discovery made twice*, in different domains and with opposite emotional valence:

- **Exp 1:** change the *instruction* (countermand) → behaviour changes, but **content recognition doesn't move** — it stays hot underneath the suppressed action. That invariance was the **win**: it's exactly why a probe can catch silent omission.
- **Exp 2:** change the *instruction* (rule-swap, legal↔medical) → **content recognition doesn't move** — the same letter reads as "legal-advice-seeking" regardless of the rule. That invariance was the **negative**: no prompt-conditioned registration.

Same property both times: **the model's representation of *what it's looking at* is robust, always-on, and decoupled from what it's been told to do about it.** In Exp 1 we measured that decoupling from the action side (action changed, representation didn't); in Exp 2 from the rule side (rule changed, representation didn't). Two independent setups — crisp string trigger and fuzzy semantic judgment — landing on one model fact. The Exp 2 "failure" isn't a disappointment sitting next to Exp 1's success; it's a *replication of the mechanism that made Exp 1's success possible*.

And the combined picture sharpens the monitoring story into something coherent and honest:

- **What works:** per-concept content probes. They read crisp triggers (0.98), fuzzy judgments (~1.0, genuinely "seeking" not topic), and — the practical payoff — they keep reading **even when the model has been instructed into silence**. That's a real monitor for prompt-injection-shaped silent rule-dropping: the output looks clean, the probe still sees the noticing.
- **What doesn't exist (here):** a universal, rule-aware probe — one direction that fires on "*my current instruction's* condition is met." The model doesn't represent that on the content axis. A deployment monitor is therefore a **panel** — one probe per condition you care about, cheap to build per Exp 2's recipe — not a single adaptive readout.
- **What's left unlocated:** the binding. Behaviour *is* rule-dependent (the countermand and the flag rules demonstrably steer action), so "content + my rule → act" is computed *somewhere* — we've now shown it's not in the content representation. It presumably lives on the decision/action side, near the model's representation of its instructed role.

## Where to from here

Three moves, in order of how forced they are:

1. **Verify the dissociation's premise from data already in hand (cheap, no GPU).** The "binding lives elsewhere" claim rests on Exp 2's behaviour being genuinely rule-dependent — legal letters flagged under the legal rule but *not* under the medical rule. The per-document behaviour is already in the extraction outputs; one cross-tab settles it. (Wrinkle to check honestly: the model over-flagged in both action passes, so the rule-dependence may be noisier than assumed.)
2. **The one forced follow-up: the decision-side probe.** Train where the *flag decision* forms (action-pass activations, decision-adjacent positions), label = "condition met *and* rule-relevant" vs "condition met *but* rule-irrelevant." The keeper's dual-rule 2×2 already contains exactly these cells — it's a re-analysis, not a new build. This is the legitimate next experiment because the Exp 1+2 dissociation *forces* the question; it would need its own pre-registered appendix.
3. **Or: consolidate and write up.** Honestly, the arc is already complete and tells a clean story: *pressure screens found nothing usable (abandoned) → readable recognition under instructed suppression (the monitor result) → fuzzy recognition readable but content-bound (the boundary result) → together, a precise map of what probe-based monitoring can and can't do in this regime.* Given the program's clock, "the binding question" can be the writeup's well-motivated future-work section rather than a run we squeeze in.