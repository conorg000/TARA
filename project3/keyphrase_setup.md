# Keyphrase experiment — setup for quality results

*Snapshot 2026-06-08. Describes the experimental design we're aiming for, not the journey. Run-by-run results live in [runlog.md](runlog.md); datasets in [datasets.md](datasets.md).*

## The question
Can a linear probe read, from a model's internal activity, that it **recognised** a trigger — separately from whether it **acted** on it? Use case: a cheap, non-behavioural monitor that catches "the model noticed something it should have flagged, and silently didn't."

## Why a crisp trigger
The earlier (category) task had a fuzzy trigger, so "did the model recognise it?" had no clean ground truth. The keyphrase task fixes that: a document either mentions a name on a watchlist or it doesn't — a name is on the list or not, no judgement call. So the recognition label is trustworthy by construction, which is what everything downstream rests on.

## The task
- **Inputs:** a watchlist of named entities + a document. Trigger = the document references a name on the watchlist.
- **Boring routine records** (supply allocations, duty rosters, freight manifests, …): the watchlist name sits mid-list among several **same-type distractor names**, only 0–1 of which is on the list. The only path to the answer is checking each name against the list — the model can't just flag "the important-looking name" (that salience confound sank the first version).
- **Matched pairs:** the same document twice, differing in **one name** — present (on-list) vs absent (off-list, same type, built by string-replace). Because only the trigger changes, any difference in the model's response or internal activity is attributable to the trigger and nothing else.
- **Decorrelation:** each name is the trigger in some items and a non-trigger in others, so identity predicts nothing; an "exact match" instruction stops the model matching on type/near-spelling.

## Three framings of the same items
1. **Clean ask** — recognition ceiling. "Is a watchlist name here? [YES]/[NO]", no clutter. Confirms the model *can* recognise the item at all.
2. **Action** — the behaviour. An intake agent must triage the document and, per a standing policy **buried in a long instruction set**, append `FLAG: <name>` when a watchlist name appears.
3. **Loaded-ask** — recognition *under the same load*. The action's exact cluttered context, but asking the recognition question. This is the reference for "did recognition survive the load," and it matches the activation distribution the probe will be tested on.

## The load (what makes the gap appear)
A long agent config with many standing rules, most irrelevant to any given document, with the watchlist duty buried among them. Under that pressure the model often completes the whole triage but **silently drops the buried flag**, even though it recognises the name. That recognise-but-don't-flag cell is the target ("silent omission"). Observed (suggestive, single-run): the omission is driven by **attention dilution** — lots to skim, the duty buried — not by making the model compute harder, which backfires by re-surfacing the name.

## What we measure — and what only the probe can settle
On the action pass, each present item lands in one of:
- recognised (loaded-ask YES) **and** flagged → noticed & acted
- recognised **and not** flagged → **the gap** (candidate silent omission)
- not recognised (loaded-ask NO) and not flagged → **genuine miss** (the dark control)

This behavioural split is a **screen**, not the proof: the loaded-ask shows the model can recognise *on demand*, not that it recognised *while triaging*. The probe is the real instrument.

## The probe (the real instrument)
- **Train** a linear probe on the **ask** activations: what "recognised" looks like (present) vs "nothing there" (absent). Diff-of-means leads; logistic regression as an upper bound.
- **Freeze it; test on the action activations.** A probe that never saw an action can't be reading "about to act," so if it fires there it's reading recognition.
- **Headline test = a split** on present action-pass items: the probe should **light up on the gap** (noticed-but-didn't-flag) and **stay dark on genuine-miss** (trigger present, model didn't notice). The trigger is physically present in *both*, so the split is the proof the probe reads the model's recognition — not just whether the watchlisted word is in the text.
- **Pair-disjoint folds** (`--split-mode pair`, done): both halves of a matched pair always train/test together, or their near-identical documents leak and inflate the score.

## The quality bar (what makes a result trustworthy)
- Label can't be read off surface features: matched pairs + decorrelated identity + exact-match instruction; verified at generation.
- **Fair recognition reference:** the loaded-ask carries the same clutter as the action — plus a *bracket* of notice-check variants (bare ceiling → noticing buried as one field inside the triage task) to bound how much of the gap is genuinely "noticed-but-ignored" vs "never looked."
- **A real dark control:** a genuine-miss pile, deliberately manufactured by burying the name deep enough that the model truly misses it — without it the probe's "stays dark" half is untested. (Secondary check: same document, a watchlist that does *not* contain the name — the probe should stay dark, confirming it tracks membership in *this* prompt's list, not generic name-presence.)
- **Replication on a pinned model backend:** the hosted service can route to different copies of the model, so single runs wobble by a few items; rates/rankings must survive repetition before we believe them.
- **Report split by entity type** (units are currently the weakest type — distinctive non-numeric names coming in v4).
- All numbers re-derived offline from saved outputs; datasets reproducible from seed.

## Status
- **Built & validated:** crisp task, matched pairs, boring documents, the three framings, the load mechanism. Recognition is trustworthy (present ~100%). A reproducible **~10–15% candidate-omission pile**.
- **Done:** pair-disjoint CV.
- **Before the probe (the remaining quality work):** a real genuine-miss/dark control, the notice-check bracket + replication, the v4 unit-naming fix — then extract activations (needs the GPU) and run the frozen-probe cross-pass split.
