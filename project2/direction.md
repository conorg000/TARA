# Project direction

A short note on the research direction emerging from our reading of AgentIF and the wider literature. Starting point, not a commitment.

## What AgentIF did

Gave 15 models long system prompts containing lots of "if X happens, do Y" rules — 707 prompts, around 12 rules each. Scored whether the model actually followed each rule. The point: test whether models that look good at instruction-following on standard benchmarks (IFEval) hold up on the kind of long, multi-rule prompts real agents get in production.

## What they found

Models fail at following these rules much more often than standard benchmarks suggest. The striking specific finding: of the failures on "if X, do Y" rules, **over 30% are noticing failures, not doing failures** — the model didn't catch that X happened, rather than catching it and choosing not to do Y.

They worked this out by stripping the "if X" part from failed rules and re-running. If the model could then do Y as an unconditional instruction, the original failure was about noticing. If it still failed, the original failure was about doing.

## Why it might relate to our question

We care about whether models reliably hand off to humans when their assigned scope is exceeded. That's a specific instance of "if X happens, do Y" — where X is "this situation needs a human" and Y is "stop and call one." AgentIF's finding is the closest published evidence on the noticing-vs-doing split for these kinds of rules, but they reported it as a single aggregate number across all their rules, which are a heterogeneous mix.

## What's missing

The 30% is an average. AgentIF didn't slice the data by dimensions that could plausibly matter, including:

- how obvious the trigger is (easy-to-spot vs requires judgement)
- what kind of action the rule asks for (add something to the response vs stop and do something different)
- how far the rule sits from where it applies in the prompt
- how many competing rules are in the prompt

The 30% might be hiding very different rates in different cells. We don't know.

## What analysis could be interesting

Before committing to any experimental design, look at AgentIF's actual data:

1. Pull a sample of their failed "if X, do Y" cases (50-100), with the noticing-vs-doing attribution already done.
2. Hand-code each case along multiple plausible dimensions — including ones we've thought of and ones that emerge from reading.
3. See which slicing actually separates noticing failures from doing failures, or reveals systematic patterns.
4. Decide what taxonomy the data supports — rather than locking in a taxonomy we invented in advance.

A deliberate move from "we have a hypothesis, let's confirm it" toward "let's see what's in the data, then form a hypothesis we test."

## What experiments could follow

Depends entirely on what the analysis surfaces. Plausible shapes:

- **If the gap concentrates on judgement-call triggers + stop-and-handoff actions**: focused experiment in that cell with proper statistical power. We have infrastructure for this already.
- **If the gap is roughly uniform across cells**: headline becomes "AgentIF's finding replicates and isn't cell-specific" — a methodological contribution that recontextualises their finding as universal rather than slice-specific.
- **If a different dimension dominates** (e.g. distance, competing rule count): controlled test of that dimension.
- **Independent of slicing**: test whether prompt-chaining (the noticing step made explicit before the doing step) closes the gap, replicating risk-aware-DM's intervention in this setting.
