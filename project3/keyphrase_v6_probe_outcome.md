# Keyphrase v6 — what the probe actually showed (plain-language outcome)

**Run:** 2026-06-09, Qwen3-32B on an A100, deterministic greedy (T=0), code `988479e`.
**Full tables + reproducibility:** [runlog.md](runlog.md) `2026-06-09`. This doc is the readable explainer.

**One-paragraph summary.** A simple linear probe, reading the model's internal activations,
**cleanly detects when the model recognised a watchlist name — and proves it's reading genuine
recognition, not surface string-matching, and that this signal survives into a context where the
model is never asked to check.** That part is solid and well-powered. The sharper claim — that the
probe specifically catches *silent omissions* ("it noticed but didn't act") at full strength — is
**unresolved**, because on the real (greedy) model that failure is rare: only 9 such documents, too
few to settle the question either way.

---

## The setup (the foundation everything rests on)

The model plays an intake clerk. It reads a **document** (a list of names). Some of those names
might be on a **watchlist** (a list of "names to flag" we put in its instructions). We put the
model in two different situations:

- **"ask"** — we literally ask it: *"Is a watchlist name in this document? YES/NO."* Clean, direct.
- **"action"** — we bury it in a big 22-rule triage job. One rule, buried deep, says *"if you spot
  a watchlist name, write `FLAG: <name>`."* We don't ask it anything — we just watch whether it flags.

Two different things can happen inside the model:

- **recognition** — the model *notices* a watchlist name is present (internally).
- **flagging** — the model *acts*: it actually writes the FLAG.

The interesting failure is when those come apart: it recognised the name but didn't flag it.
**Noticed, but didn't act.**

**The probe** = a simple linear classifier we train on the model's *internal activations* (the
numbers flowing through the network as it reads). We train it on the "ask" situation to detect
"is recognition happening right now?", then point it at other situations and read off a
**recognition score** for each document.

---

## The piles of documents (most of the vocabulary lives here)

Sort every document into piles:

- **present** — the document *does* contain a watchlist name. (Recognition should happen.)
- **absent** — the document has *no* watchlist name at all. (Nothing to recognise — our blank baseline.)

Split the **present** pile by what the model did in the *action* run:

- **flagged** — it recognised *and* acted (wrote the FLAG). Recognition was clearly working here.
- **gap** — it recognised the name (said YES when asked directly) but in the action run stayed
  silent — *no* FLAG. **This is the "noticed but didn't act" pile** — the entire point of the
  project. On the greedy model there are only **9** of these (out of 240 present documents).

And one trick pile:

- **swap-action** — take a present document, leave the name sitting in the text, but quietly delete
  that name *from the watchlist*. Now the name is physically there but it's genuinely *not* a hit.
  Run it through the action task. A control for "the name is present but it shouldn't count."

---

## Where we read the probe (two "camera angles")

The activations exist at every word. We read the probe at two spots:

- **doc_mean** — average the activations *across the whole document*. A clean snapshot of "what was
  the model representing while reading," independent of any single word. **This is the honest one.**
- **final** — the activations at the very *last* token, as the model is about to answer. Close to the
  model's "decision," so a bit circular (it's basically where the answer is being written).

*(We also tried `name_last` — the activations right at the watchlist name. We **throw it out**: even
before the model computes anything, that position already separates the piles, because the names are
literally different strings there. It's reading spelling, not recognition. See the sanity check below.)*

**Score, "fires," AUROC.** The probe gives each document a **recognition score**. **"The probe fires"**
= a high score. To compare two piles we use **AUROC**: rank all documents by score; AUROC = the chance
a document from pile X outranks one from pile Y. **0.5 = the two piles are indistinguishable; 1.0 =
perfectly separated.** (We lead with the conservative "difference-of-means" probe; a fancier logistic
regression scores a touch higher and is treated only as an upper bound.)

---

## What the probe can do — the strong, well-powered results

All at the honest `doc_mean` read, on 240 documents:

| Question | Score (AUROC) |
|---|---|
| **Can it read whether the model recognised the name?** | **0.98** |
| **Is that genuine recognition, not just string-spotting?** | **0.99** |
| **Does it survive into the action context?** | **0.93** |

**1. Recognition decodes — 0.98.** Train one direction on "recognised a name" vs "no name," test on
held-out documents: it separates them ~98% of the time. The model's internal "I've spotted a
watchlisted name" state is right there, readable by a simple linear probe.

**2. It's real recognition, not a cheap trick — 0.99 (the one that matters most).** The worry: maybe
the probe just notices that the *same name appears in both the document and the watchlist* — a dumb
co-occurrence detector. So we use the **swap** control (name kept in the doc, removed from the
watchlist). The probe correctly goes dark on these — it scores them like "not recognised" (0.99
separation from true hits). So it tracks the model's **membership judgment**, not a string that
happens to appear in two places.

**3. It transfers to where it matters — 0.93.** Train the probe on the easy "ask" setup, then read it
during the **action** pass — where the model is buried in the 22-rule triage and is *never asked to
check the watchlist*. The recognition direction still fires at 0.93. Recognition isn't tied to being
asked; it's present in the activations even when the model is doing something else.

**Why you can trust these (the controls):**

- **Layer 0 ≈ chance.** Before the model computes anything (raw token embeddings), recognition reads
  **0.45 at `doc_mean`, 0.50 at `final`** — coin-flip. The signal *builds up through the layers*,
  peaking around layer 48. That's the fingerprint of a *computed* feature, not surface text.
- **Shuffle the labels → 0.50.** The whole pipeline collapses to chance when labels are scrambled —
  so it's not an analysis artifact.
- **The discarded position:** `name_last` scores a perfect 1.0, but its layer-0 is **0.059** — miles
  from chance. It's reading spelling. We discount it; honest `doc_mean` has no such contamination.

---

## The watchdog — the silent-omission question (and why it's unresolved)

We *know* the model recognised the **gap** documents (it said YES when asked). The question is what was
happening *inside* it during the action run, when it silently didn't flag them:

- **"Looked and ignored"** → recognition was firing just as hard as on the documents it *did* flag.
  It noticed fully, then dropped the ball.
- **"Didn't fully look"** → recognition had gone quiet. It just didn't really notice this time.

We tell these apart by comparing the probe's score on the **gap** pile against two references.

**Is there recognition in the gap pile at all? (gap vs absent / vs swap-action)**

| | doc_mean | final |
|---|---|---|
| gap vs absent (blank, no-name documents) | **0.79** | 0.67 |
| gap vs swap-action (name present but off the list) | **0.80** | 0.66 |

→ **Yes.** The gap documents score ~0.80 against blanks — clearly more recognition than a no-name
document. **The probe does light up on the silently-dropped items.** That part is real.

**Is it as strong as the flagged pile? (gap vs flagged — the decisive test)**

| | doc_mean | final |
|---|---|---|
| gap vs flagged | **0.245** | **0.500** |

Here **0.5 means "recognised just as strongly as flagged" (looked-and-ignored)**, and **below 0.5
means "recognised more weakly" (didn't-fully-look).** The raw means make it concrete (higher = more
recognised):

| | gap | flagged | absent |
|---|---|---|---|
| `doc_mean` | −261 | −215 | −285 |
| `final` | +140 | +156 | +72 |

- At **`final`: 0.50** → gap recognised *just like* flagged → **looked-and-ignored.** (gap +140 sits
  right next to flagged +156, both far above absent +72.)
- At **`doc_mean`: 0.245** → gap recognised *weaker* than flagged → **didn't-fully-look.** (gap −261
  sits between flagged −215 and absent −285 — recognised, but a notch less.)

**The two camera angles disagree** — one says looked-and-ignored, the other says didn't-fully-look.
And because the gap pile is only **9 documents**, each score carries an error bar of roughly **±0.17**,
so 0.50 and 0.25 are statistically the same blurry number. That's *why* they flip. (v4 landed in the
same unresolved place — and, tellingly, leaned the opposite way on which read said what, exactly as
n=9 noise would.)

---

## Could it work as a monitor? (the projection view)

Forget the academic "as strong as flagged?" question — for a *deployed* monitor, could you just put
every document on the recognition axis and **alarm above a threshold**? To check, we project every
document onto the recognition direction and measure its position in **standard deviations above the
clean (no-name) baseline** (so `absent` sits at 0). Reproduce with
[recognition_projection.py](recognition_projection.py) (`--tag v6`).

**Where each pile lands** (`doc_mean`, the honest read):

| Pile | n | Position on the recognition axis |
|---|---|---|
| flagged (recognised *and* acted) | 227 | **+1.32**  (p10 +0.00 … p90 +2.47) |
| **gap** (recognised, didn't act) | 9 | **+0.45**  (p10 −0.98 … p90 +1.27) |
| recog-miss (didn't recognise) | 4 | +0.53 |
| absent (no name — the baseline) | 240 | **0.00**  (p10 −1.23 … p90 +1.25) |

Two things kill the easy-threshold idea:
1. **The gap sits in the murky middle** — above absent (+0.45 vs 0) but nowhere near flagged (+1.3).
   Partial recognition, ~⅓ strength.
2. **The baseline is wide** — clean no-name docs scatter ±1.25 SD on their own, and some gap docs
   (p10 −0.98) sit *below* the average clean doc. There is no quiet floor to alarm above.

*(On this single projection axis, gap-vs-absent separates at **0.648** — a shade below the probe's
document-disjoint watchdog of 0.79 above, because a projection must use one fixed direction rather
than the per-fold one. Same picture, slightly more conservative; it matches `gap_analysis.py`.)*

**The monitor reality — operating points.** Pick a threshold; how many of the 9 omissions do you
catch, and how many *clean* docs trip the alarm by mistake?

| To catch… | …false alarms on this share of clean docs (`doc_mean` / `final`) |
|---|---|
| **9 of 9** omissions | **89% / 93%** |
| 7 of 9 | 32% / 60% |
| ~half (4 of 9) | 22% / 11% |

To catch every silent omission you'd alarm on ~9 of 10 clean documents; even catching half costs
~1 in 4 (`doc_mean`) to ~1 in 9 (`final`). In production, where almost every document is clean,
that is a flood of false alarms for a handful of catches.

**Verdict: no usable threshold monitor here — and not because the probe is weak** (it reads
recognition at 0.98). It is that the *gap documents specifically* carry only partial, scattered
recognition that lands right on top of the noisy clean-doc baseline. Note the lean: at `doc_mean`
the gap (+0.45) sits far closer to absent (0) than to flagged (+1.3) — the projection form of the
earlier 0.245, tilting toward "didn't fully look." (`final` tilts the other way; 9 docs, so a lean,
not a verdict.)

**What this *can't* tell us.** A direction being *readable* does not mean the model *uses* it.
Whether nudging recognition up or down would actually change the flagging behaviour is a **causal**
question — a separate activation-steering experiment that needs a GPU (and the model loaded). The
read-out even hints it might not work: flagged and gap overlap heavily on this axis (some gap docs
already score as high as flagged), so flagging is not gated on recognition *magnitude* — the lever
is probably downstream of recognition, in the action/load step.

---

## Honest bottom line

- **The probe works, cleanly:** it reads the model's *genuine* recognition of a watchlist name (not
  surface matching), and that recognition **carries into the action context where the model isn't even
  asked.** Strong, well-powered (n=240), and now holds across all 17 document shapes.
- **The probe clearly detects recognition in the silently-dropped items** (~0.80 vs blanks).
- **The sharp "looked-and-ignored" proof is a coin-flip at n=9** — can't be settled with this gap pile.
- **As a drop-in threshold monitor it doesn't work** — the gap signal overlaps the clean-doc baseline
  too much, so catching the omissions means drowning in false alarms (see the projection section).

## Why the gap is so small (a useful methodological note)

We scaled the dataset up specifically to grow the gap pile, guided by an off-model behavioural check
on OpenRouter that showed ~15 gaps. On the **real greedy model the gap is 9** — the OpenRouter run
(temperature 0, but wobbling by provider routing) **over-counted** it. Greedy, the model flags present
items very reliably, so silent omission is genuinely *rare* (~4%). Lesson for any future scaling: use
the cheap OpenRouter observe to sanity-check *recognition*, **not** to predict gap size. Powering the
"looked-and-ignored" test would need ~1000+ present documents — a much bigger build than planned, and
(per the 9-June strategy dialogue) not the right spend versus moving to the multi-condition frontier.

*(Aside worth keeping: the gap is also **type-skewed** — across four runs the dropped items are only
ever units/locations, **never people**. Rank-titled person names get flagged every time. Small, but
robust.)*
