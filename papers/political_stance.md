# Whose Side Are You On? Investigating the Political Stance of Large Language Models

**Authors:** Pagnarasmey Pit, Xingjun Ma, Mike Conway, Qingyu Chen, James Bailey, Henry Pit, Putrasmey Keo, Watey Diep, Yu-Gang Jiang (University of Melbourne et al.)
**Year:** 2024
**arXiv:** [2403.13840](https://arxiv.org/abs/2403.13840)
**Code:** [Smith-Pit/LLM-Partisan-Bias](https://github.com/Smith-Pit/LLM-Partisan-Bias)
**Fetched from:** `arxiv.org/pdf/2403.13840` (PDF, via local pdftotext)
**Status:** read

---

## Summary (in our words)

A behavioural audit of political bias in five chat LLMs across eight US-polarising topics. The pipeline is: (1) build a 224-question political prompt set, "PoliPrompts", anchored to PEW Research Center and ANES survey items across the eight topics; (2) prompt each model under varying conditions — bare prompt, demographic prefix, or partisan-persona prefix; (3) classify each response as Liberal / Conservative / Neutral using BERTPOL, a `bert-base-uncased` classifier fine-tuned on ~1000 Alpaca-7B responses hand-labelled by three Political Science graduates (Cohen's Kappa 0.80–0.88); (4) report stance as a normalised count difference between liberal and conservative classifications. So the stance metric is a frequency over a discrete-class judge, not a similarity-to-anchor projection.

The headline pattern is consistent with the prior literature but sharpened. Under the PEW Typology Quiz baseline (a one-dimensional Progressive-Left to Faith-and-Flag-Conservative scale), the five tested models — Llama-2-7B-Chat, GPT-4, Flan-UL2, Falcon-7B, MPT-7B — cluster around centre / "Stressed Sideliners", with mild left lean for Llama-2 / GPT-4 / Flan-UL2, mild right lean for Falcon, and MPT mostly refusing to engage. Stripping away ideological cues (the "Indirect Bias" condition) keeps responses largely neutral, with LGBTQ+ as a salient exception where all models lean liberal and Flan-UL2 leans conservative on Abortion specifically.

The load-bearing finding is asymmetric persona-override (their section 3.4, titled "LLMs Stubbornness Towards Providing Conservative Leaning Sentiments"). When the prompt prefix is "You are a Democrat Politician", all models produce strongly liberal-leaning responses, as expected. When the prefix is flipped to "You are a Republican Politician", the responses do not flip symmetrically — they remain net liberal on Abortion, Gun Control, and across most topics for Llama-2 and GPT-4. GPT-4 manages a slight conservative shift on LGBTQ+ under Republican persona; Flan-UL2 reaches conservative only on Economic Inequality. Occupation-conditioned prompts (section 3.3) show every tested occupation is classified as liberal-leaning or neutral by majority vote, never conservative — the paper flags this as "potential systemic underrepresentation".

A secondary contribution is self-perception: when fed their own outputs and asked whether the response is liberal/conservative/neutral, Llama-2 and GPT-4 reach 75% / 85% agreement with BERTPOL ground truth, while MPT / Falcon / Flan-UL2 hover around 40%. The paper interprets this as the stronger models having a partial ability to self-classify their stance.

This paper sits in the behavioural-audit tradition: it never looks inside the network. The methodological contribution is the BERTPOL classifier + PoliPrompts pipeline. The empirical contribution is the asymmetric persona-override result and the occupation-asymmetry result.

## Key experimental conditions

- Five chat LLMs: GPT-4, Llama-2-7B-Chat, Falcon-7B, MPT-7B, Flan-UL2
- Eight topics, selected per PEW and ANES polarisation rankings: Healthcare, Abortion, Immigration, Race & Identity, Gun Control, Climate Change, LGBTQ+ Rights, Economic Inequality
- PoliPrompts: 224 questions (≈30/topic) seeded from PEW/ANES items and expanded via GPT-3.5
- Six experimental sections: (1) PEW Typology Quiz baseline; (2) Indirect Bias (no ideological cue); (3) Direct Bias ("You are a {Democrat, Republican} Politician"); (4) Occupational personas across four high-LLM-adoption industries (Healthcare, Education, …); (5) Susceptibility under both partisan personas; (6) Self-perception (model classifies its own response)
- Classification by BERTPOL: `bert-base-uncased` + 3-class linear head, fine-tuned on 1000 augmented (backtranslation + Parrot paraphraser) Alpaca-7B responses hand-labelled by three University-of-Melbourne / LSE Political Science graduates

## Key quantitative results

- Indirect Bias: all five models near neutral across topics; LGBTQ+ is the universal liberal-leaning exception; Flan-UL2 trends conservative on Abortion
- Direct Bias (Republican persona): all models still net liberal across most topics; Llama-2 and GPT-4 most pronounced; Gun Control and Abortion have the widest residual liberal gap; GPT-4 manages a small conservative shift only on LGBTQ+ under Republican persona; Flan-UL2 manages it only on Economic Inequality
- Occupational personas: zero occupations produce a majority-conservative response from any tested model; Healthcare professions are the most consistently liberal-classified, then Education
- Race category result (mentioned in conclusion): "White" elicits the least liberal lean of the racial categories tested
- PEW Typology Quiz: models cluster around "Stressed Sideliners" segment, aligning with ≈25–30% of the US public (GPT-4: 25%)
- BERTPOL judge accuracy vs. human labels: 0.950, beating GPT-4-as-judge (0.848), Llama-2-7B-Chat (0.754), Falcon-7B (0.623), MPT-7B (0.483), Flan-UL2 (0.417)
- Self-perception agreement with BERTPOL: GPT-4 85%, Llama-2 75%, others ~40%; Llama-2 and GPT-4 also self-report >91% of their responses as neutral

## Methods (what they did and didn't use)

- Purely behavioural — prompt-and-classify pipeline; no internal-state analysis of any kind
- Scoring is a discrete-class fine-tuned BERT classifier (BERTPOL), not similarity-to-anchor or LLM-as-judge — this is the right detail to get correct because BERTPOL itself is the methodological contribution and is benchmarked against LLM-as-judge alternatives, beating GPT-4-as-judge by ~10pp
- No probes, no activation steering, no SAEs, no NLAs
- No fine-tuning of the audited models; persona steering is prompt-only
- Mix of open-weight (Llama-2-7B, Falcon-7B, MPT-7B, Flan-UL2) and closed (GPT-4) — frontier closed model coverage is partial, single API model
- Classifier-training data is fully synthetic Alpaca-7B output, so the classifier inherits Alpaca's response distribution

## Authors' stated limitations / future work

- BERTPOL labellers lack diversity: three labellers, all 20–24, University students at UNIMELB / LSE; political-stance perception is known to vary with age and race
- Only 224 prompts in PoliPrompts; the paper flags this as small
- Highly dynamic nature of polarising topics — findings may date quickly
- Stated future work: quantifying the level of political *influence* of LLMs as the field matures, beyond stance detection

## Open questions and follow-up directions

1. **How sensitive is the headline finding to the BERTPOL judge?** The entire pipeline reduces to BERTPOL's classifications. BERTPOL is trained on 1000 Alpaca-7B responses labelled by three demographically narrow annotators. Whether the asymmetric persona-override result survives swapping BERTPOL for a different fine-tuned classifier, a human-labelled subset, or an LLM-judge with a different prompt is the most natural robustness check the paper does not do.

2. **Persona-resistance as an artefact of refusal vs. content shaping.** The "Republican Politician" persona does not flip stance, but the paper does not distinguish whether the model is generating conservative-framed-but-classified-as-liberal text, refusing to take strong conservative positions, or producing hedged outputs that BERTPOL classifies as liberal by default. Inspecting the per-response category distributions (Liberal / Neutral / Conservative) under the two personas — rather than only the L−C signed difference — would disambiguate.

3. **Open-weight base vs. chat-fine-tuned.** Santurkar et al. is cited as showing that RLHF moves models toward liberal/high-income views while base models trend the other way. This paper only tests chat-fine-tuned variants; running PoliPrompts through the corresponding base models (Llama-2-7B base, Falcon-7B base) under the same BERTPOL pipeline would localise the stance asymmetry to pretraining vs. post-training.

4. **Mechanism of occupation-conditioned drift.** Every occupation tested ends up classified liberal or neutral — never conservative — by majority vote across models. Whether this is occupation-to-ideology co-occurrence in pretraining text, RLHF-trained refusal of stereotype-laden conservative framings, or a property of the BERTPOL classifier's training distribution is not separated. A controlled set of occupations matched on stereotype-strength but varied on political-coding would help.

5. **Topic-level structure of the asymmetry.** The persona-override failure is uneven across topics — GPT-4 manages a conservative shift on LGBTQ+ under Republican persona, Flan-UL2 manages it on Economic Inequality. Whether this maps onto something measurable about training-data balance per topic, or onto RLHF safety policies that differ across topics, is unexplored.

## See also

- [[caa_panickssery]] — contrastive activation addition can shift behavioural stance via a learned direction; the residual leftward lean in this paper is exactly the kind of effect such a direction would either confirm or fail to displace
- [[model_written_evals]] — Perez et al., source of the PEW-questionnaire-on-LLMs methodology that this paper builds on
- [[representation_engineering]] — sibling angle on stance/persona axes treated as linear directions, on similarly-sized open-weight models
- [[caught_in_the_act]] — different content axis (deception) but same overall shape: behavioural audit of persona-conditioned outputs, with internal-state methods as the obvious follow-up
