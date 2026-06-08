# Scale-up plan — tighten the watchdog (post-compaction handoff)

**One-line goal:** grow the gap pile from ~9 to ~25–30 so the "noticed-but-didn't-act"
watchdog gets real error bars, on the structurally-diverse v5 design.

## Where we are (June 2026)
- **v5 is validated** (commits `5e9fc6b` data, `8870d63` observe). Recognition holds at
  ceiling across all 17 document shapes; the silent-omission gap is **real and shape-general**
  (~10% of present items, spread across 6 formats — not a flat-list artifact). See runlog
  `2026-06-08 v5 observe`.
- **The only weak link is n.** Watchdog rests on n_gap ≈ 7–9 → directional, wide bars.
- **All tooling is already done** — scale-up needs no new code, just more data + a GPU pass:
  - probe (`probe_keyphrase.py`) does **document-disjoint pair-OOF** cross-pass and supports
    `--swapaction` (the sharper watchdog dark). Commit `34814e7`.
  - extractor (`extract_keyphrase.py`) grades the `swapaction` framing and reads `meta["doc"]`
    (multi-line shapes safe).
  - `gap_analysis.py` = the gap-vs-flagged control; `split_check.py` = strict-split verifier.

## The lever: more pairs at H5, NOT more load
Gap rate has been steady ~10–15% at H5 across v2–v5. So gap count scales with dataset size.
Do **not** crank the load to force more gaps (muddies "looked-and-ignored" vs "never looked").

## Target size
- **80 entities/type → 240 pairs → 240 present → ≈ 24 gap** (recommended sweet spot, ~3×).
- 100/type → 300 present → ≈ 30 gap (tighter; more name-authoring). Adjustable.

## Steps
1. **Author the expanded entity pools** (the only real work). Add ~56 new names/type to reach
   ~80/type, in the v4/v5 style: distinctive, **non-numeric**, **unique first word**, no
   substring collisions (units like "Ironside Detachment"; locations like "Orsk Hollow";
   persons like "Sergeant Halloran"). `check_no_substring_entities()` + `verify()` fail loudly
   on slips. Put them in a new pool (e.g. `V6_ENTITIES`).
2. **Generate v6** = v5's 17 formats + the bigger pool. Cleanest: `make_dataset_keyphrase_v6.py`
   importing `FORMATS` from v5 and the new pool; output `inputs/watchlist_v6_ask.json`.
   (New name, per the "new variant = new file" rule — keeps the v5 observe run valid.)
3. **Derive load + swaps:**
   ```
   python make_keyphrase_loaded.py --load 5 --ask-in inputs/watchlist_v6_ask.json --out-prefix inputs/watchlist_v6
   python make_keyphrase_swapwl.py --ask-in inputs/watchlist_v6_ask.json
   ```
4. **(cheap, optional) OpenRouter observe on v6** before spending GPU — confirm recognition
   ~100% and gap rate ~10% on the bigger set: rerun the 4 gates as in `observe_v5.py`
   (swap the v5 paths for v6), check `python observe_v5.py`-style reconciliation.
5. **GPU extract** (follow `GPU_RUNBOOK.md`: arena_key, model in `/dev/shm`, smoke first).
   Now **5 datasets** (the probe consumes all five):
   ```
   for f in ask action_H5 loadedask_H5 swapwl_ask swapwl_action_H5; do
     python extract_keyphrase.py --model Qwen/Qwen3-32B --dataset inputs/watchlist_v6_$f.json --out-prefix acts/v6_$f
   done   # action ~480 items x 512 tok ≈ 35–45 min; recog runs fast. ~1–1.5 hr total, ~$1–2.
   ```
   Gate each (recognition ~ceiling; **watch the action truncation warning** → raise
   `--max-new-tokens 768` if it fires). Pull the npz to laptop; probe runs on CPU.
6. **Probe** (now WITH the action-swap dark):
   ```
   python probe_keyphrase.py --ask acts/v6_ask --action acts/v6_action_H5 \
       --loadedask acts/v6_loadedask_H5 --swap acts/v6_swapwl_ask \
       --swapaction acts/v6_swapwl_action_H5 --out probe_v6.json
   python gap_analysis.py    # update POS_LAYER prefixes to v6_* for the gap-vs-flagged control
   ```

## Pre-registered read (write the number before the run; don't move it)
Lead **diff-of-means at `doc_mean`** (the recognition locus; `name_last` is lexically confounded —
discount it). Expected to confirm at the bigger n:
- recognition decodes ≥ 0.90, transfer ≥ 0.80, membership ≥ 0.90 (already shown at n=72 — sanity).
- **Watchdog headline:** `gap vs swap-action` (sharpest dark — same doc, name off the list, under
  the action prompt) **> 0.70** at doc_mean with gap-mean > swap-mean. `gap vs absent` as the
  secondary dark.
- **The decisive control (`gap_analysis.py`): `gap vs flagged`.** With n_gap ≈ 25, its CI is the
  test: if it brackets ~0.5 (gap recognised *as strongly as* flagged), that's "looked-and-ignored"
  confirmed; if clearly < 0.5, the omission tracks weaker recognition ("didn't fully look").
- Sanity: layer-0 ≈ 0.5; shuffle-label watchdog ≈ 0.5.

## Decision after
- Clean watchdog (1–3 hold, gap≈flagged at n≈25) → the result is done; write it up.
- Watchdog null at tight n → honest finding: recognition transfers but the gap is not
  internally-recognised-then-ignored. Report it; don't sand it.

## Cost / pointers
GPU ~$1–2, OpenRouter trivial. Commits: `34814e7` (probe fix+swap), `5e9fc6b` (v5 data),
`8870d63` (v5 observe). Background: `runlog.md`, `datasets.md`, `GPU_RUNBOOK.md`, `CLAUDE.md`.
