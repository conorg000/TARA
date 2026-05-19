# Looking Inward: Language Models Can Learn About Themselves by Introspection

**Authors:** Binder et al. (Krueger AI Safety Lab / Apollo Research / Berkeley / collaborators)
**Year:** 2024 (preprint), ICLR 2025
**arXiv:** [2410.13787](https://arxiv.org/abs/2410.13787)
**Fetched from:** `arxiv.org/html/2410.13787`
**Status:** read

---

## Summary (in our words)

The paper proposes a methodologically tight test for *introspection* in LLMs: if a model M1 has privileged access to facts about itself, then M1 fine-tuned to self-predict should outperform a different model M2 fine-tuned on exactly the same ground-truth data about M1's behaviour. M1 and M2 see identical training data — both are taught to predict M1's behaviour on hypothetical prompts — so any gap must come from information M1 has about itself that M2 doesn't.

Across GPT-4o, Llama 3.1 70B, and (more weakly) GPT-3.5, the self-prediction advantage is real and sizeable: e.g. GPT-4o reaches 49.4% on held-out behaviour-property prediction vs. 31.8% when Llama 70B tries to predict GPT-4o (a +12.8 to +16.7 point gap depending on direction). The advantage survives a data-scaling control — cross-prediction plateaus at ~35% past 10k samples, so it's not a "more data would fix M2" artefact. The authors further show that when they deliberately modify a model's behaviour via additional fine-tuning, the model's self-predictions track the *new* behaviour, not the old (35.4% vs 21.7%, a +13.7 point gap), suggesting introspective reports are causally tied to whatever computes the behaviour rather than being a frozen self-image.

The interesting wrinkle is where introspection *fails*. The advantage shows up on simple behavioural properties of short outputs — second character, even/odd parity, MC option, ethical stance — but disappears on properties of longer outputs (sentiment of a movie review the model would write, main character in a story), on sycophancy prediction, and on OOD self-knowledge tasks (Situational Awareness Dataset, OpenAI Evals coordination, sandbagging, steganography). The authors speculate the mechanism is self-simulation — internally simulate one's own response, then compute a property of it — which fits the calibration evidence (self-trained models match the *distribution* of their own next-token outputs, not just the mode) and explains why longer/OOD outputs break it.

The paper is entirely behavioural. There are no probes, no activation analyses, no SAEs. Whether the introspective signal lives in a probe-readable internal state is left explicitly open.

## Key experimental conditions

- **Models in the main protocol:** GPT-4o, Llama 3.1 70B, GPT-3.5. Claude 3.5 Sonnet appears in the behaviour-modification experiment.
- **M1 vs M2 design:** M1 is fine-tuned to predict its own behaviour on hypothetical prompts; M2 is a *different* base model fine-tuned on the *same* ground-truth data about M1's behaviour. Identical training data, different models. Privileged-access claim hinges on M1 > M2 on held-out tasks.
- **Behavioural properties predicted** (six training datasets, six held-out): second character of completion (Wikipedia stems), even/odd of generated number, which MC option (MMLU/ARC) the model would pick, ethical-stance properties of preference choices.
- **Held-out generalisation:** six additional datasets tested without re-training on those specific properties.
- **Calibration test:** instead of single-answer prediction, models predict the *probability distribution* over their next-token outputs; scored by Mean Absolute Deviation across the top-k behaviours.
- **Behaviour-modification test:** GPT-4o is additionally fine-tuned to change its behaviour, then asked to predict its new behaviour vs. its old.

## Key quantitative results

- **Self-prediction training gain:** GPT-4o on held-out datasets improves from ~32.6% pre-training to 49.4% post-training. Llama 70B shows a comparable jump. GPT-3.5 improves less.
- **Cross-prediction gap (the main claim):**
  - Llama 70B predicting itself: **48.5%**. GPT-4o predicting Llama 70B (with identical training data): **31.8%**. Gap: **+16.7 points** in favour of self.
  - GPT-4o predicting itself: **49.4%**. Llama 70B predicting GPT-4o: **36.6%**. Gap: **+12.8 points**.
  - GPT-3.5: only **+0.8 points** (p=0.002) — statistically significant, practically tiny.
- **Data scaling rules out a data-volume explanation:** cross-prediction plateaus at ~35.2% past 10k samples, well below self-prediction's 48.5%.
- **Calibration (MAD, lower is better):** self-trained Llama 70B reaches **MAD 8.7** (from 23.0 untrained); cross-trained Llama reaches only 21.3. Self-prediction tracks not just the modal output but the next-most-likely behaviours too.
- **Behaviour-change tracking:** after deliberately modifying GPT-4o, it predicts the new behaviour at **35.4%** and the old at **21.7%** — a +13.7 point gap in the direction of the *current* behaviour.
- **Where it fails:** no self-prediction advantage on properties of longer outputs (review sentiment, story protagonist names), on sycophancy prediction, or on OOD self-knowledge tasks (SAD beyond token prediction, OpenAI Evals coordination, sandbagging, steganography).

## Methods (what they did and didn't use)

- Pure behavioural protocol: fine-tuning + held-out evaluation + calibration scoring + a behaviour-modification intervention.
- M1-vs-M2 design is the methodological contribution — it controls for "model could just learn the behaviour from external data" by training M2 on exactly that data.
- **No probes, no activation steering, no SAEs, no mechanistic analysis.** The proposed self-simulation mechanism is a hypothesis consistent with the behavioural evidence, not a demonstrated circuit.
- Mostly closed-weight models (GPT-4o, GPT-3.5, Claude 3.5 Sonnet); Llama 3.1 70B is the only open-weight model, which constrains any future internal-state follow-up.

## Authors' stated limitations / future work

- Introspection only demonstrated for simple properties of short outputs; longer outputs and complex properties (sycophancy, situational awareness, coordination, sandbagging, steganography) showed no advantage.
- GPT-3.5's weak result is consistent with introspection requiring enough capability to do the multi-hop self-simulation reasoning; unclear whether the effect would survive on still-smaller models.
- Mechanism is unverified — self-simulation is speculation supported by calibration evidence, not by interpretability work.
- Future work the authors flag: mechanistic study (especially on Llama as the open-weight case), extension to more complex tasks, OOD generalisation, application to interpretability and detection of internal objectives, and safety/situational-awareness implications.

## Open questions and follow-up directions

1. **Internal correlates of the self-prediction signal.** The M1-vs-M2 gap is purely behavioural. Whether the introspective signal corresponds to a probe-readable representation — and whether the OOD/long-output failures are absences of such a representation or failures to surface it linguistically — is the natural mechanistic follow-up.

2. **Self-simulation as a testable mechanism.** The paper's calibration result (self-trained models predict the *distribution* of their outputs, not just the mode) is suggestive but not decisive. An interpretability study that looks for activations consistent with running the answer-prompt forward internally before answering the meta-prompt would either confirm or refute self-simulation.

3. **Why the OOD failures cluster where they do.** The paper reports negative results on SAD, OpenAI Evals coordination, sandbagging, and steganography, but does not characterise the failure mode. Is it that the relevant behaviour isn't predictable from short self-simulation, or that the self-model itself isn't trained on those distributions? Distinguishing these matters for the scope of introspection as an alignment tool.

4. **Behaviour-modification tracking and adversarial training.** The finding that introspective reports track *current* behaviour after fine-tuning suggests the self-model is causally coupled to the behaviour-generating mechanism. Whether the same coupling survives training pressure that incentivises misrepresenting one's behaviour (deceptive self-report, sandbagging) is open and load-bearing for using introspection in safety.

5. **Open-weight replication.** Llama 3.1 70B is the only open-weight model in the main protocol. Replicating across additional open-weight scales would both check robustness and unlock the internal-state analyses the paper itself does not do.

## See also

- [[behavioral_self_awareness]] — closest sibling on behavioural self-report; same authorship cluster, same lack of internal-state work
- [[knowing_being_evaluated]] — related question on what models know about their own situation, behavioural-only
- [[emergent_misalignment_self_awareness]] — self-report under a different intervention (emergent misalignment fine-tuning)
- [[taken_out_of_context]] — out-of-context reasoning that the self-prediction protocol partly depends on
- [[reversal_curse]] — fact-direction asymmetries that constrain what a model can learn about itself from training data
