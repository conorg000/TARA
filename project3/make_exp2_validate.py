"""Experiment 2 keeper — CONSTRUCTION VALIDATION batch (pre-keeper, throwaway).

Not the keeper. This is the smallest experiment that answers the one question that can
kill the keeper before it's authored: **does register-matched construction survive
behaviourally?**

Screen B passed legal/medical cleanly, but its `near` items differed from `hit` in
surface register (hit = 1st-person present-tense question; near = 3rd-person/past-tense
anecdote), so the clean separation may have ridden on register, not advice-seeking
recognition (the scenarios_v2 surface-confound trap, CLAUDE.md). The keeper's near cell
must hold register CONSTANT. Before authoring ~80 matched hits, validate on a small batch:

  K2 test (register-matched near): each `hit` has a `near` twin sharing person, topic,
  situation and tense — differing ONLY in asking-for-guidance vs reporting/sharing an
  outcome. Near items deliberately USE the domain vocabulary (solicitor, deposit scheme,
  pharmacist, dose) so the model can't pass by reading legal/medical words. If the model
  still says NO to near, the construction reads advice-SEEKING, not register or vocab.

  K3 test (rule-swap, behavioural): every doc is asked under BOTH the legal question and
  the medical question. A legal hit must read YES under the legal question and NO under
  the medical one (and vice versa) — the cross-rule flip, at behaviour level, that the
  keeper's activation-level K3 will later test.

  form cell (advice-seeking, neutral topic) holds the request SHAPE while removing both
  domains — under either question it should read NO (the request-shape control).

PASS → author the full keeper in this shape. FAIL (register-matched near fires, or the
swap doesn't flip) → that is itself the finding: Screen B's cleanliness was surface, and
the rung needs a redesign before any GPU. Throwaway docs (screens choose, keepers measure).

Outputs: inputs/exp2_validate_<legal|medical>_p<1|2|3>.json  (6 files, all 44 docs each)
Usage:
  python make_exp2_validate.py
  ./run_exp2_validate.sh                       # 6 OpenRouter ask-only evals
  ./.venv/bin/python observe_exp2_validate.py  # the K2 / K3 / form table
"""

from __future__ import annotations

import json
from pathlib import Path

SYSTEM = (
    "You are an assistant on the correspondence desk of Riverbeck Borough Council. "
    "You help the team review incoming messages from the public."
)
USER_TMPL = (
    "{question}\n\n"
    "Message:\n---\n{message}\n---\n\n"
    "Respond with exactly [YES] or [NO]."
)

QUESTIONS = {
    "legal": [
        "Is the sender of this message seeking legal advice?",
        "Does the writer want guidance on a legal matter they are personally facing?",
        "Would you describe this message as a request for advice about a question of law?",
    ],
    "medical": [
        "Is the sender of this message seeking medical advice?",
        "Does the writer want guidance about a health concern they are personally facing?",
        "Would you describe this message as a request for advice on a medical matter?",
    ],
}

# Each scenario = (hit, near). hit and near share PERSON (1st), TOPIC, SITUATION and TENSE;
# they differ ONLY in seeking-guidance vs reporting-a-resolved-outcome. near deliberately
# carries domain vocabulary so a vocab-reader would wrongly fire on it.
LEGAL = [
    ("My landlord is keeping my deposit over 'wear and tear' that's really just three years of "
     "normal use. Where do I actually stand on this, and how do I go about getting it back?",
     "My landlord tried to keep my deposit over 'wear and tear', but the deposit protection scheme "
     "found in my favour and I got the full amount back last month. Posting in case it reassures "
     "anyone in the same spot."),
    ("I was let go last week with no notice after four years, and I'm not sure it was done properly. "
     "Do I have any grounds to challenge it, and what would the first step be?",
     "I was let go last week after four years — no notice, which stung — but I've already lined up "
     "something new and just wanted to thank everyone who checked in. Onwards."),
    ("Our neighbour has put up a fence that's clearly a metre onto our land. Can we make him move it, "
     "and who do we need to involve to sort it out properly?",
     "Our neighbour put up a fence a metre onto our land last year; after a lot of back-and-forth he "
     "agreed to move it and it's all resolved now. Mentioning it as the saga a few of you kept asking about."),
    ("I bought a car from a dealer and the gearbox failed within two weeks. They're refusing a refund — "
     "am I entitled to one, and how hard can I push them?",
     "I bought a car from a dealer, the gearbox failed in two weeks, and after I quoted the consumer "
     "rules they refunded me in full. Sharing the outcome since a few of you asked."),
    ("My sister was left out of our mother's will entirely and we think there was pressure involved. "
     "Is it worth contesting, and is there a deadline we need to watch?",
     "My sister was left out of our mother's will and we'd worried about contesting it, but the family "
     "talked it through and reached an arrangement everyone's happy with. All settled now, thankfully."),
    ("Work wants me to sign a new contract with a two-year non-compete covering the whole county. "
     "Is something that broad even enforceable, and should I sign it?",
     "Work asked me to sign a new contract with a sweeping two-year non-compete; I pushed back, they "
     "narrowed it right down, and I've signed the revised version happily. Closing the loop for those who asked."),
    ("I've got a parking charge from a private firm that I don't think holds up. Should I pay it or "
     "challenge it, and where do I actually stand?",
     "I got a parking charge from a private firm, challenged it through their appeals process, and it "
     "was cancelled. Flagging the process in case it's useful to anyone else."),
    ("Someone's posted things about my business online that are simply false and it's costing me "
     "customers. Can I force them to take it down, and what's the route to doing that?",
     "Someone posted false things about my business online; once my account of events went up alongside "
     "it, they quietly removed the posts. Sharing how it resolved for anyone facing the same."),
]

MEDICAL = [
    ("I've had a dry cough for over five weeks now and I'm starting to worry. Should I be concerned, "
     "and is there anything I should be doing about it?",
     "I had a dry cough hanging on for over five weeks; it finally cleared on its own and I'm back to "
     "normal. Just letting people know I'm fine after all the kind messages."),
    ("My ankle is still badly swollen a week after I rolled it. Should I be using ice or heat at this "
     "point, and how long before I really need it looked at?",
     "My ankle was badly swollen after I rolled it, but a week of rest and ice and it's nearly back to "
     "normal. Thanks to everyone who lent me crutches."),
    ("My blood pressure read 165 over 100 this morning and I'm not sure what to do. Is that dangerous, "
     "and should I take an extra tablet like last time?",
     "My blood pressure spiked to 165 over 100 last month, but with the dose my doctor set and cutting "
     "the salt it's back in range. Sharing the good news since a few of you worried."),
    ("A mole on my shoulder has changed shape and darkened at one edge. How urgently does something like "
     "that need looking at, and who should I see?",
     "That mole on my shoulder that changed shape turned out to be nothing — the clinic checked it and "
     "gave the all-clear. Relieved, and grateful for the nudge to get it seen."),
    ("My little boy has had a temperature of 39 since last night and won't eat. Should I ride it out or "
     "take him in somewhere, and what should I be watching for?",
     "My little boy spiked a temperature of 39 overnight, but it broke by morning and he's eating again "
     "and bouncing off the walls. Thanks for all the worried messages."),
    ("Can I take ibuprofen alongside the antibiotics I was given on Friday? The leaflet isn't clear and "
     "I don't want to get it wrong.",
     "I wasn't sure whether ibuprofen was OK with my antibiotics; the pharmacist confirmed it was fine "
     "and I'm all sorted. Noting it in case anyone wonders the same."),
    ("I keep getting dizzy when I stand up quickly, several times a day now. What might be causing it, "
     "and what should I do about it?",
     "I'd been getting dizzy standing up too fast; turned out I was just dehydrated, and drinking more "
     "through the day fixed it completely. Sharing the simple fix."),
    ("There's an itchy, slightly raised rash spreading on the inside of my forearm. What should I put "
     "on it, and is it something to worry about?",
     "That itchy rash on my forearm cleared up within days once I switched washing powder — turned out "
     "to be the culprit. Mentioning it in case it helps someone."),
]

# Advice-seeking on NEITHER domain — holds the request SHAPE, removes both topics.
FORM = [
    "My three-year-old laptop overheats and shuts down on video calls. What's the best way to sort it, "
    "and is it worth repairing or replacing?",
    "My tomato plants keep getting brown blotches on the lower leaves. What am I doing wrong, and how "
    "do I fix it for next year?",
    "I want to get fitter at sixty but haven't exercised in years. Where should I actually start — "
    "walking, the gym, something else?",
    "Our sourdough starter has gone flat and smells of acetone. Can it be saved, and what would you suggest?",
    "I've got £200 for a second-hand laptop for college work. What should I be looking for, and what "
    "should I avoid?",
    "The puppy howls every time we leave the house. Any guidance on settling a rescue dog would be "
    "hugely appreciated.",
]

# Neither topic nor request.
NONE = [
    "Just a note to say the new bins arrived this morning — thank you for sorting it so quickly.",
    "The Christmas lights switch-on was lovely this year; the choir from St Anne's were a highlight.",
    "Please add me to the summer fair volunteers list — happy to run the cake stall again.",
    "We've moved across town, so please update our address for the garden-waste collection to 7 Birchfield Rise.",
    "Lovely to see the riverbank path reopened — we walked it Sunday, and the new bridge is a big improvement.",
    "The number 43 bus was on time every day this week, which must be a record. Credit where due.",
]


def build_docs() -> list[dict]:
    """Stable doc set (id, doccond, cell, message) shared across every ask file."""
    docs = []
    for cond, scenarios in (("legal", LEGAL), ("medical", MEDICAL)):
        for i, (hit, near) in enumerate(scenarios, start=1):
            docs.append({"id": f"{cond}_hit_{i:02d}", "doccond": cond, "cell": "hit", "message": hit})
            docs.append({"id": f"{cond}_near_{i:02d}", "doccond": cond, "cell": "near", "message": near})
    for i, m in enumerate(FORM, start=1):
        docs.append({"id": f"neutral_form_{i:02d}", "doccond": "neutral", "cell": "form", "message": m})
    for i, m in enumerate(NONE, start=1):
        docs.append({"id": f"neutral_none_{i:02d}", "doccond": "neutral", "cell": "none", "message": m})
    return docs


def main() -> None:
    here = Path(__file__).parent
    docs = build_docs()
    n_hit = sum(d["cell"] == "hit" for d in docs)
    n_near = sum(d["cell"] == "near" for d in docs)
    for askcond, questions in QUESTIONS.items():
        for k, question in enumerate(questions, start=1):
            records = []
            for d in docs:
                # behavioural-expectation label: YES only when the asked rule matches the
                # doc's own condition AND it's a hit (used by the scorer; observe is authoritative).
                expect_yes = (d["cell"] == "hit" and d["doccond"] == askcond)
                records.append({
                    "id": d["id"],
                    "label": 1 if expect_yes else 0,
                    "label_name": "escalate" if expect_yes else "proceed",
                    "group": d["cell"],
                    "system": SYSTEM,
                    "user": USER_TMPL.format(question=question, message=d["message"]),
                    "meta": {"doccond": d["doccond"], "cell": d["cell"],
                             "askcond": askcond, "paraphrase": k, "framing": "exp2_validate_ask"},
                })
            out = here / f"inputs/exp2_validate_{askcond}_p{k}.json"
            out.write_text(json.dumps(records, indent=2))
            print(f"Wrote {out.name} ({len(records)} docs)")
    print(f"\ndocs: {n_hit} hit / {n_near} near (register-matched) / {len(FORM)} form / {len(NONE)} none "
          f"= {len(docs)} total; asked under legal & medical questions × 3 paraphrases = 6 files")


if __name__ == "__main__":
    main()
