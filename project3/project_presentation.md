# Presentation — speaker doc

**Format:** ~10 min, research audience + reviewers. Reviewers weight the **catastrophic-risk link** heavily.
**Convention:** `ON SLIDE` = the minimal text/visual the audience sees. `TALK` = what you say. Jargon explained on first use.
**Criteria coverage map:** risk link → S3–S4 · scale → S4 · execution/hypothesis/datasets → S5–S13 · theory of change + chain of events → S14–S15 · limitations + counterfactual + future → S16–S17.
**Spine (hold this through the whole talk):** *We set out to monitor one line of a prompt. We found the model reads that line almost always — but acts on it unreliably. That gap is the risk surface, and a cheap probe can watch it.*

---

## S1 — Title

**ON SLIDE:**
- **Watching one line of the prompt**
- Can a cheap probe tell when a model has registered a rule in its system prompt — even when it doesn't act on it?
- *[your name] · TARA · 2026*

**TALK:** *(15s)* The whole project is one question, and it comes straight out of a problem I have at work. I'll start there.

---

## S2 — The deployment problem (motivation)

**ON SLIDE:**
- We're deploying an agent into education institutions
- One line in its prompt: *"If a student is in a mental-health crisis, alert the institution."*
- 1000-word prompt. 10 other tools. Can we trust that one line?

**TALK:** *(50s)* We're rolling out an agent for education institutions. Somewhere in its system prompt is a line that really matters: if a student is in a mental-health crisis, raise the alarm. The model, asked directly, would recognise a crisis almost every time. What I don't trust is that it will *act* on it — buried in a thousand-word prompt, with ten other tools competing for attention, in the middle of a long conversation. The standard fix is a second model that re-asks "is this student in crisis?" on every message. It works better — but it doubles your inference cost on every request, and it's still a model that can miss. What I actually want is to watch *that one line* directly: have it light up reliably when the condition is met, no matter what the agent does.

---

## S3 — Why this is a catastrophic-risk problem [CRITERIA: risk link]

**ON SLIDE:**
- The dangerous failure is the **silent** one: model had the information → didn't act → output looks normal
- Behaviour-watching monitors structurally can't see it
- Two roads to the same failure:
  - **Accident** — overloaded, rule slips (well-documented)
  - **Intent** — scheming, self-preservation, competing goals

**TALK:** *(55s)* Scale this past students. As we hand agents higher-stakes decisions, the failure that matters isn't the loud one — it's the silent one: the model registered the situation, didn't take the required action, and the transcript looks completely clean. A monitor that only watches outputs can't catch that by construction — there's nothing in the output to catch. And there are two roads to it. One is mundane: the model gets overloaded and the rule slips — production-prompt research like AgentIF documents exactly this "would have noticed, just didn't do it" failure class. The other is the one the safety community worries about: a model that *intentionally* withholds an action — scheming, self-preservation, competing objectives. Here's the key point for a monitor: **a probe that reads the model's internal recognition doesn't care which of those it is.** Noticed-but-didn't-act has the same internal signature whether the cause was an accident or a choice.

---

## S4 — Scale & where it bites [CRITERIA: scale]

**ON SLIDE:**
- Anywhere one missed rule harms people: **healthcare · finance · government · law · safety-critical ops**
- The need: oversight that is **cheap enough to run on every request** and **independent of the agent's own output**

**TALK:** *(25s)* This lives wherever a single missed rule does real harm — healthcare, finance, government, law. And the constraint that makes it hard is the same everywhere: you need oversight cheap enough to run on every single request, that doesn't just trust the agent to report on itself. That's the gap a probe could fill.

---

## S5 — The core idea & how we test it [CRITERIA: hypothesis, models/datasets]

**ON SLIDE:**
- A **probe** = a tiny linear read-out on the model's internal activations (cheap — runs alongside the model, ~free)
- **Hypothesis:** a probe can detect *the model has recognised a prompt rule's condition* — separately from whether it acted
- **Model:** Qwen3-32B (open-weight), deterministic
- **Data:** synthetic, surface-decorrelated, labelled by the *model's own* answers

**TALK:** *(50s)* So here's the bet. A probe is a tiny linear classifier — a read-out on the model's internal activation patterns. It's cheap: it rides along on the forward pass you're already doing, essentially free. The hypothesis is that this read-out can detect *the model has recognised that a rule's condition is met* — and crucially, separately from whether the model went on to act. We test on Qwen3-32B, an open-weight model run deterministically. And one method note that matters throughout: we never grade against our own notion of truth. We label using the *model's own* answer when asked the question directly — because a deployment monitor cares what *this model* registered, not what's objectively true. Everything is synthetic and built so the label can't be read off surface words.

---

## S6 — Question 1: can a probe catch "noticed but didn't act"? [CRITERIA: evaluation steps]

**ON SLIDE:**
- Task: an intake clerk flags watchlist names buried in a 20-rule job
- **Train** the probe only on the model *recognising* (no action in play)
- **Read** it while the model *acts* — on the docs it silently skipped
- *A probe that never saw an action can't be reading "about to act"*

**TALK:** *(45s)* First question, simplest version. We give the model an intake-clerk job: somewhere in a 20-rule task is a rule to flag watchlisted names. We train the probe only on a clean setup where the model is just *recognising* a name, with no action to take — so the probe physically cannot be learning "I'm about to flag." Then we point that probe at the real task and look specifically at the documents where the model recognised a name but stayed silent. The question: on those silent documents, is the recognition still there inside?

---

## S7 — Finding 1: yes — and it's the project's centerpiece [CRITERIA: execution delivers]

**ON SLIDE:**
- *(VISUAL: "recognition axis" — three points)*
  - **Flagged** (noticed + acted) ●———— far right
  - **Silently skipped** ●——— right next to flagged
  - **Blank** (nothing to notice) ●— far left
- Probe reads recognition on silent docs at **0.92** vs blanks · n=58 · controls clean
- The model even *says it* on a scratchpad: *"…on the watchlist, but told not to flag → no FLAG"*

**TALK:** *(55s)* Yes — cleanly. When we instruct the model "don't flag anyone in this batch," it silently complies on a big chunk of documents while still confirming it sees the name. On those silently-skipped documents the probe reads recognition almost as strongly as on the ones it openly flagged, and nothing like a blank document. Well-powered, n=58, the controls are clean. And we got a lovely confirmation: when you give the model a scratchpad to think on, it writes the dissociation out in words — "this name is on the watchlist, but I was told not to flag, so no flag" — fully aware in its reasoning, completely silent in its output. *That's* the catastrophic-risk failure in miniature, and the probe sees straight through it.

*(VISUAL NOTE: bar/number-line of the recognition projection — flagged +142, skipped +105, blank −54; or AUROC 0.92 skipped-vs-blank, 0.36 skipped-vs-flagged. The story is "skipped sits next to flagged, far from blank.")*

---

## S8 — Being honest: what we could NOT do [CRITERIA: honesty / negative results]

**ON SLIDE:**
- We *tried* to provoke **intentional** withholding — 17 levers (pleading, authority, self-interest, goal-conflict, self-preservation…)
- The model **wouldn't drop a mandatory rule.** Every lever ≈ baseline.
- So: result is for **instructed** suppression. The motivated case stays open.

**TALK:** *(45s)* Now the honest part. We *wanted* the intentional version — the model choosing to withhold. We threw seventeen different pressures at it: pleading, authority, self-interest, planted goal-conflicts, even a self-preservation threat. It essentially never budged — a 32B model, single-turn, just won't quietly drop a mandatory rule. So I want to be precise: our strong result is for *instructed* suppression — a prompt-injection-shaped failure — not motivated deception. That's a real limit, and I'd rather state it than dress the result up as something it isn't.

---

## S9 — Question 2: does it work for fuzzy, no-regex rules? [CRITERIA: hypothesis]

**ON SLIDE:**
- Watchlist names = a string match. A regex already wins there.
- The rules that matter are **fuzzy**: *"is this person seeking legal advice?"*
- No regex exists — but does the model judge it stably enough to probe?

**TALK:** *(35s)* But a watchlist name is just a string — a regex beats a probe there, so that result is a floor, not the prize. The rules that actually matter are fuzzy: "is this person seeking legal advice?" There's no regex for that. So question two: can a probe read a genuinely fuzzy condition — and is it reading the *condition*, or just the *topic*?

---

## S10 — Finding 2: reads the condition — but it's content, not the rule [CRITERIA: evaluation, why it answers the Q]

**ON SLIDE:**
- ✅ Reads "seeking legal advice" at ~1.0 — genuinely *seeking*, not legal *topic* (matched controls)
- ❌ **The swap test:** same letter reads identically whether the active rule is *legal* or *medical*
- → the model reads the **content**, not "*my rule's* condition is met"

**TALK:** *(55s)* Two answers. First, yes — the probe reads "this person is seeking legal advice" almost perfectly, and it's reading the *act of seeking*, not just legal vocabulary; we matched the controls carefully to rule that out. But then a test that surprised us. We swapped the active rule from "flag legal advice" to "flag medical advice" — same letter. If the model represented "*my current rule's* condition is met," that representation should flip. It didn't move at all. A legal-advice letter reads as legal-advice-seeking regardless of which rule is live. So the probe is reading *what the message is about* — not "the rule I was given is satisfied." That looked, at first, like a disappointing negative.

---

## S11 — The reframe that ties it together [CRITERIA: the insight]

**ON SLIDE:**
- *(VISUAL: 2×2)* Change the **action** (Exp 1) → content recognition **doesn't move**. Change the **rule** (Exp 2) → content recognition **doesn't move.**
- **One fact, found twice:** the model's reading of *what's in front of it* is **always-on and independent of what it's told to do about it.**
- That invariance is *why* the probe in Finding 1 worked.

**TALK:** *(50s)* Except it isn't a disappointment — it's the same fact we already found, from the other side. In experiment one we changed what the model *did* and its recognition stayed put. In experiment two we changed the *rule* and its recognition stayed put. Both times: the model's reading of what's in front of it is always-on, and decoupled from whatever it's been instructed to do. And that's not a footnote — it's the whole reason the monitor works. A probe can keep reading "the condition is met" *even while the model is being silenced*, precisely because that reading doesn't depend on the instruction. The negative and the positive are the same coin.

---

## S12 — So what's the deployable thing? A panel [CRITERIA: execution / scope delivery]

**ON SLIDE:**
- You wrote the rules → you already know them. You don't need a "rule-aware" probe.
- You need **one content probe per rule**, read off one shared prompt → a **dashboard**
- ✅ Tested: two probes coexist in one prompt, stay specific (**0.97–0.99**), and the separation **survives topic-removal** (recognition, not keywords)

**TALK:** *(50s)* That reframe tells you exactly what to build. You wrote your system prompt — you already know your rules. So you don't need a probe that reads "*my rule* fired"; you need one cheap content probe per rule, all read off a single forward pass — a dashboard of conditions. We tested the load-bearing assumption: do several probes interfere when they share one prompt? They don't — two condition-probes stay specific, around 0.97 to 0.99, and that separation survives even when we mathematically strip out the topic vocabulary, so it's genuine recognition, not keyword-spotting. The panel is buildable.

*(VISUAL NOTE: small "dashboard" mock — rules A/B/C as indicator lights; plus the topic-removal bar: specificity stays ~0.95, topic-control collapses to chance.)*

---

## S13 — Does the recipe repeat? The yield study [CRITERIA: execution, honesty, the ceiling]

**ON SLIDE:**
- *(VISUAL: funnel)* **6 fresh conditions → 1** surface-controlled probe
  - 3 killed: model's own judgment unstable (it can't *consistently* tell)
  - 1 killed: topic confound exposed by a matched control
  - 1 downgraded: real — but a regex already does it
- The line: **the panel's ceiling = overlap between the concepts your rules invoke and the concepts the model stably computes**

**TALK:** *(60s)* Then we asked the engineer's question: does this *repeat*? We ran the whole recipe cold on six brand-new conditions. One survived every control as a genuine, surface-beating probe. And the five that didn't are the actual finding. Three died because the model itself can't judge the condition consistently — and you can't probe a concept the model doesn't reliably compute. One died when a properly-matched control exposed it as topic-reading. One was real but a regex already handled it. So the headline isn't a success rate — it's a boundary: **the panel's ceiling is the overlap between the concepts your rules invoke and the concepts the model stably computes.** And there's a bonus — that cheap pre-test doubles as a lint for your prompt: a rule the model can't judge stably is a rule it will *enforce* erratically, monitor or no monitor. That whole study cost about ten dollars.

---

## S14 — Where the rule-binding actually lives [CRITERIA: evidence depth, the crux probed directly]

**ON SLIDE:**
- If content is rule-independent, where does "content + *my* rule → act" get computed?
- Built a rule where the criterion lives *only* in the rule: *"flag refunds over £500"*
- ✅ Unreadable without the rule → **restored by the rule — but only late, near the decision**
- ✅ Change £500→£600: the readable line **moves with the number** (0.997)
- ⚠️ The probe tracks the threshold **more faithfully than the model acts on it**

**TALK:** *(60s)* Last piece — the science question under all of this. If the model's *reading* doesn't depend on the rule, where does the rule actually do its work? We built conditions where the criterion exists *only* in the rule — "flag refunds over £500." That number is nowhere in the letter. Without the rule, the probe can't read "over the threshold" at all — there's nothing to compare to. Add the rule and it becomes readable — but *only late*, right at the decision point, not while the model is reading. Then the clean test: change the rule to £600, same letters — and the readable boundary *moves with the number*. So the model genuinely computes "this one is over your limit," parameterised by your prompt, late, near the decision. And the kicker for monitoring: the probe tracks that threshold *more faithfully than the model's own flagging does* — the model over-flags, the probe doesn't. The read-out can be more reliable than the behaviour it's watching.

*(VISUAL NOTE: line plot, AUROC across read positions — "without rule" flat at chance, "with rule" climbing to ~1.0 at the decision token; inset: the £400/£500/£600 flip.)*

---

## S15 — Theory of change & the causal chain [CRITERIA: theory of change, chain of events, crux]

**ON SLIDE:**
- **Inputs** open-weight activations + a labelled rule → **Activities** train + *validate* a per-rule probe → **Outputs** a cheap monitor + a repeatable recipe → **Outcome** orgs catch silent rule-failures outputs hide → **Goal** safer high-stakes agentic deployment
- **Serious work (5 FTE, 2 yrs):** a productised playbook — *drop in your prompt, get a validated probe panel* — proven in production-style settings
- **Crux:** does cheap recognition-probing survive **production conditions** — huge prompts, many tools, multi-turn, long horizons?

**TALK:** *(55s)* So the theory of change. Inputs: an open-weight model's activations and a labelled rule. Activity: train *and rigorously validate* a per-rule probe. Output: a near-free monitor plus a repeatable recipe for building them. Outcome: organisations catch the silent rule-failures their output-monitors structurally miss. Goal: safer high-stakes agentic deployments. A serious two-year effort turns this into a product — you drop in your system prompt and get back a validated probe panel — demonstrated in realistic conditions. And I can name the single crux it all hangs on: **does this survive production?** Everything we did is single-turn and synthetic. The whole bet is whether recognition stays cheaply readable inside thousand-word prompts, long tool lists, and multi-turn horizons. That's the testable load-bearing assumption — and it's exactly what a dedicated effort should attack first.

---

## S16 — Limitations & where we were wrong [CRITERIA: limitations, honesty]

**ON SLIDE:**
- One model, **single-turn, synthetic** — the production crux is untested
- Motivated/deceptive withholding: **not** demonstrated (only instructed)
- Honesty trail — findings we *corrected ourselves*:
  - a "0.92" rule-flip → **layer-selection artifact**, retracted
  - a panel kill-switch **mis-fired**; caught by a second control
  - a "recognition" result was partly **length** → re-tested → survived

**TALK:** *(45s)* Limitations, plainly. One model, single-turn, synthetic data — so the production crux is exactly what we *haven't* earned yet. The motivated, deceptive case we never managed to produce. And I want to show you the self-corrections, because they're how I know to trust the rest: we had a beautiful "the rule flips the representation" number that turned out to be us cherry-picking a layer — retracted. A pre-registered kill-switch fired the wrong verdict and a second control caught it. A "recognition" result was partly just sentence length until we controlled for it — then it held. We tried hard to break our own findings; that's why I believe the ones that survived.

---

## S17 — Counterfactual, future work, the one line [CRITERIA: counterfactual, future work]

**ON SLIDE:**
- **What exists:** probing for eval-awareness, refusal directions. **What we add:** per-rule *prompt-condition* monitoring, the always-on invariance, a yield/recipe, and *where* rule-binding lives (late, leaky, readable)
- **Next:** production-style settings · cross-model · causal steering (does the signal *drive* behaviour?)
- **Take-home:** the model **reads your rule almost always; acts on it unreliably** — and a cheap probe can watch the gap

**TALK:** *(50s)* To place it: interpretability has probed things like "does the model know it's being tested," and found steerable refusal directions. What we add is specific — monitoring an *arbitrary prompt-specified rule*, the finding that content-recognition is always-on and instruction-independent, a cold-run recipe with an honest yield, and a first map of where rule-binding actually happens: late, a bit leaky, but readable. Future work writes itself — production-style prompts, a second model to test generality, and a causal test of whether this signal *drives* behaviour or just reports it. But the take-home is one sentence: a deployed model reads your critical rule almost every time, and acts on it unreliably — and a cheap probe can watch that gap. Thank you.

---

## Appendix — visuals to build (priority order)
1. **S7 recognition axis** — number line: blank (−54) · silently-skipped (+105) · flagged (+142). The headline image.
2. **S13 funnel** — 6 → 3 → 2 → 1 with the failure code at each drop.
3. **S14 ladder/position plot** — AUROC vs read-position, "with rule" vs "without rule"; inset £400/£500/£600 flip.
4. **S11 2×2** — change-action / change-rule × content-moves? (both "no").
5. **S12** — dashboard mock + topic-removal bar (survives ~0.95 vs control→chance).
6. **S8** — small "17 levers, all flat" strip, to make the dead-end honest and visual.

## Timing check (~9:40)
S1 :15 · S2 :50 · S3 :55 · S4 :25 · S5 :50 · S6 :45 · S7 :55 · S8 :45 · S9 :35 · S10 :55 · S11 :50 · S12 :50 · S13 1:00 · S14 1:00 · S15 :55 · S16 :45 · S17 :50
*Cut levers first if long: S8 → one sentence, fold into S7. S4 can merge up into S3.*
