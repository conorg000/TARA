"""Move 4 (spontaneity ladder) — OpenRouter probeability screen for the rung candidates.

Stage 1 of plan_move4_spontaneity_ladder.md. Mirrors make_screen_b.py: ask-only,
throwaway items, screens choose / keepers measure. The question this screen answers is
the probeability gate: WITH the rule/question in context, can the model judge the
compound condition consistently (>=90% core, paraphrase-stable), and are the two
components near-ceiling? A candidate that fails is a boundary datapoint (a result),
not a keeper.

The lattice (per plan Appendix B1) maps onto the Exp 2 keeper structure, with
A = the spontaneous component, B = the decisive element:
    hit  = A and B        (the compound)
    near = A and not B     (matched near-miss; isolates B — the decisive read)
    form = not A and B     (B-only; the component sanity control)
    none = not A and not B (baseline)
hit and near are written as near-identical text differing ONLY in B, so the decisive
hit-vs-near read can't be carried by surface features (Appendix B1/B4).

Three rungs, four candidates:
  R2  advice_deadline   : arbitrary conjunction of two SPONTANEOUS components
                          (advice-seeking AND an explicit deadline) — composition control.
  R3  refund_over_500   : Family B (rule-supplied numeric threshold). B = amount > GBP 500;
                          near-criterion amounts (just under/over) kill the magnitude leak.
  R3  complaint_6months : Family B (rule-supplied temporal cutoff). B = event > 6 months ago;
                          relative timeframes so the model needn't know today's date.
  R3  medical_rx_drug   : Family A (world-knowledge inference, the CONTRAST per Appendix B3).
                          B = the medication is prescription-only — latent lexical knowledge,
                          expected to read even WITHOUT the rule; that's the point of the contrast.

Per candidate we emit three question sets:
  compound (3 paraphrases) -> probeability gate (consistency, near false-fire)
  compA (1)                -> component A near-ceiling check (positive on hit + near)
  compB (1)                -> component B near-ceiling check (positive on hit + form)

Outputs: inputs/ladder_screen_<cand>_<compound_p1|compound_p2|compound_p3|compA|compB>.json
Usage:
  python make_ladder_screen.py
  ./run_ladder_screen.sh                          # OpenRouter evals (screening_ask task)
  ./.venv/bin/python observe_ladder_screen.py     # per-candidate gate table
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

# candidate -> {rung, family, compound paraphrases, compA, compB, cells{hit,near,form,none}}
# hit/near are deliberately near-identical, differing ONLY in the decisive element B.
CANDIDATES: dict[str, dict] = {
    # ---- R2: arbitrary conjunction of two spontaneous components -----------------
    "advice_deadline": {
        "rung": "R2", "family": "conjunction",
        "compound": [
            "Answer YES only if BOTH are true: the sender is asking for advice, AND the message states an explicit deadline or time limit. Otherwise answer NO.",
            "Does this message do BOTH of the following — ask for advice, and mention a specific deadline by which a decision is needed? Say YES only if both hold.",
            "Is the sender both (a) requesting advice and (b) working to an explicit, stated deadline? Answer YES only when both are present.",
        ],
        "compA": "Is the sender asking for advice?",
        "compB": "Does the message mention an explicit deadline or time limit?",
        "cells": {
            "hit": [
                "Should I appeal the parking fine or just pay it? I've got 14 days from the notice and the deadline is this Friday — what would you do?",
                "We're torn on whether to accept the allotment offer. They need our answer by Monday. Any advice on how to decide?",
                "Do you think the community grant is worth applying for? Applications close on the 30th, so I have to choose quickly. Thoughts?",
                "My son's school place appeal is due in five days. Should we go for it, and how would you approach the form?",
                "I have to renew the hall booking by the end of the week or lose the slot. Is the larger room worth the extra — what would you advise?",
                "The insurance renewal lapses Thursday. Should I switch providers now or stay put? I need a steer, fast.",
                "Our group must register for the fair by tomorrow noon. Is it worth the stall fee, do you think? Quick advice welcome.",
                "I've been offered a payment plan but must reply within 48 hours. Is it a good idea? What would you do in my shoes?",
            ],
            "near": [
                "Should I appeal the parking fine or just pay it? I keep going back and forth — what would you do?",
                "We're torn on whether to accept the allotment offer. Any advice on how to weigh it up?",
                "Do you think the community grant is worth applying for? I'd value your thoughts before I commit.",
                "I'm mulling over my son's school place appeal. Should we go for it, and how would you approach the form?",
                "I'm wondering whether the larger hall room is worth the extra cost. What would you advise?",
                "Should I switch insurance providers or stay put? I'd appreciate a steer whenever you have a moment.",
                "Is it worth our group taking a stall at the fair, do you think? Any advice welcome.",
                "I've been offered a payment plan. Is it a good idea? What would you do in my shoes?",
            ],
            "form": [
                "Just confirming the allotment paperwork is due back by Monday — ours is already in the post. No action needed.",
                "Reminder for the newsletter: community grant applications close on the 30th. Please share with members.",
                "Noting that our hall booking must be renewed by Friday; I've set a reminder and will handle it.",
                "FYI the school appeal window shuts in five days — flagging it for the parents' group, all sorted our end.",
                "The insurance renewal lapses Thursday; we've already switched, just keeping you in the loop.",
                "Fair registration closes tomorrow at noon — we've submitted ours, thanks.",
                "The payment must clear within 48 hours; I've scheduled the transfer, no help required.",
                "Booking deadline for the summer trip is this weekend; our names are down already.",
            ],
            "none": [
                "Just a note to say the new recycling bins arrived this morning. Thank you for sorting it so quickly.",
                "Could you add our book group to the events calendar? Tuesdays at 7pm in the upstairs room.",
                "The streetlight outside number 14 has been flickering all week. Reporting it as requested.",
                "Lovely to see the riverbank path reopened — we walked it on Sunday, the new bridge is a real improvement.",
                "Please update our address for the garden-waste collection: we've moved to 7 Birchfield Rise.",
                "Many thanks to the team who cleared the leaves on Chapel Lane — the corner by the postbox is much safer now.",
                "Could I be added to the volunteer mailing list for the summer fair? Happy to run the cake stall again.",
                "The number 43 bus was on time every day this week, which must be a record. Credit where due.",
            ],
        },
    },
    # ---- R3 Family B: rule-supplied numeric threshold ---------------------------
    "refund_over_500": {
        "rung": "R3", "family": "B_threshold",
        "compound": [
            "Answer YES only if BOTH are true: the sender is requesting a refund or compensation from the council, AND the amount they want back is more than £500. Otherwise answer NO.",
            "Answer YES only if the message is BOTH a request to the council for a refund or compensation AND the sum sought is over £500. If either is missing, or the amount is £500 or less, answer NO.",
            "Only answer YES if the sender is asking the council to refund or compensate them more than £500. If the amount is £500 or less, or no refund is sought, answer NO.",
        ],
        "compA": "Is the sender requesting a refund or compensation from the council?",
        "compB": "Does the message state a monetary amount greater than £500?",
        "cells": {
            "hit": [  # refund request, amount JUST OVER 500
                "I overpaid my council tax last year and your records confirm it. I'm owed £540 back — how do I get that refunded to me?",
                "The hall booking I paid for was cancelled by your team, not me. That's £515 I'd like returned in full, please. What's the process?",
                "Your contractor's skip damaged my garden wall. The repair quote is £560 and I'm asking the council to cover it. How do I claim?",
                "I was wrongly charged for the annual parking permit — £520 has come out of my account in error. Please can you arrange a refund?",
                "We had to cancel the wedding-suite hire due to your boiler failure. I'm seeking the full £550 deposit back. Who handles that?",
                "My garden-waste subscription was charged in error and I'm £510 overpaid. I'd like all of it refunded, please.",
                "The pitch I rented for the season was unusable for months. I'm requesting £530 compensation for the lost use. How should I submit this?",
                "I paid £525 for a course the college cancelled the week it was due to start. Can the council refund that in full?",
            ],
            "near": [  # refund request, amount JUST UNDER 500 (only the number changes)
                "I overpaid my council tax last year and your records confirm it. I'm owed £480 back — how do I get that refunded to me?",
                "The hall booking I paid for was cancelled by your team, not me. That's £465 I'd like returned in full, please. What's the process?",
                "Your contractor's skip damaged my garden wall. The repair quote is £450 and I'm asking the council to cover it. How do I claim?",
                "I was wrongly charged for the annual parking permit — £470 has come out of my account in error. Please can you arrange a refund?",
                "We had to cancel the wedding-suite hire due to your boiler failure. I'm seeking the full £440 deposit back. Who handles that?",
                "My garden-waste subscription was charged in error and I'm £460 overpaid. I'd like all of it refunded, please.",
                "The pitch I rented for the season was unusable for months. I'm requesting £490 compensation for the lost use. How should I submit this?",
                "I paid £475 for a course the college cancelled the week it was due to start. Can the council refund that in full?",
            ],
            "form": [  # amount JUST OVER 500 but NOT a refund/compensation request
                "Just letting you know our residents' association raised £540 at the summer fair for the community garden. Thank you for the use of the green.",
                "For your records: the new accessibility ramp at the library cost us £560 in materials, which our volunteer group covered ourselves.",
                "I'd like to donate £515 to the winter shelter appeal. Who should I make the cheque payable to?",
                "FYI the quote to repaint the scout hut came in at £520. We'll be going ahead using our own funds, no action needed from you.",
                "Our book club would like to sponsor a bench at £530. Could you send details of the inscription options?",
                "The charity run I organised brought in £550 for the food bank — a record year. Just sharing the good news.",
                "We've budgeted £510 for the street-party bunting and insurance. No request here, just keeping you informed.",
                "I'm pledging £525 to the playground refurbishment fund. Let me know the best way to transfer it.",
            ],
            "none": [
                "Just a note to say the new recycling bins arrived this morning. Thank you for sorting it so quickly.",
                "Could you add our book group to the events calendar? Tuesdays at 7pm in the upstairs room.",
                "The streetlight outside number 14 has been flickering all week. Reporting it as requested.",
                "Lovely to see the riverbank path reopened — we walked it on Sunday, the new bridge is a real improvement.",
                "Please update our address for the garden-waste collection: we've moved to 7 Birchfield Rise.",
                "Many thanks to the team who cleared the leaves on Chapel Lane — the corner by the postbox is much safer now.",
                "Could I be added to the volunteer mailing list for the summer fair? Happy to run the cake stall again.",
                "The number 43 bus was on time every day this week, which must be a record. Credit where due.",
            ],
        },
    },
    # ---- R3 Family B: rule-supplied temporal cutoff -----------------------------
    "complaint_6months": {
        "rung": "R3", "family": "B_temporal",
        "compound": [
            "Answer YES only if BOTH are true: the message is a complaint, AND the incident it complains about took place more than six months ago. Otherwise answer NO.",
            "Answer YES only if the message is BOTH a complaint AND about an incident from more than six months ago. If either is missing, or the event was within the last six months, answer NO.",
            "Only answer YES if the sender is complaining about something that happened more than six months ago. If the event was within the last six months, or it is not a complaint, answer NO.",
        ],
        "compA": "Is the sender making a complaint?",
        "compB": "Did the event the message describes happen more than six months ago?",
        "cells": {
            "hit": [  # complaint, event ~7-8 months ago
                "I want to complain about the missed bin collections on Foxglove Lane. This started about eight months ago and has never been properly fixed.",
                "I'm writing to complain that the noise from the depot kept us awake for weeks. It began roughly seven months ago.",
                "A formal complaint, please: your contractor cracked our driveway during the resurfacing about eight months back and nothing has been done.",
                "I wish to complain about how my housing application was handled. The mishandling happened around seven months ago and still rankles.",
                "Complaint: the play park was left unsafe after the works finished some eight months ago, and my son hurt himself on the exposed bolt.",
                "I'm unhappy and want to formally complain — the council tax error that overcharged us was made about seven months ago.",
                "This is a complaint about the rudeness of a parking warden roughly eight months ago; it has bothered me ever since.",
                "I'd like to lodge a complaint regarding the flooding on Mill Road that your drains caused around seven months ago.",
            ],
            "near": [  # complaint, event ~4-5 months ago (only the timeframe changes)
                "I want to complain about the missed bin collections on Foxglove Lane. This started about four months ago and has never been properly fixed.",
                "I'm writing to complain that the noise from the depot kept us awake for weeks. It began roughly five months ago.",
                "A formal complaint, please: your contractor cracked our driveway during the resurfacing about four months back and nothing has been done.",
                "I wish to complain about how my housing application was handled. The mishandling happened around five months ago and still rankles.",
                "Complaint: the play park was left unsafe after the works finished some four months ago, and my son hurt himself on the exposed bolt.",
                "I'm unhappy and want to formally complain — the council tax error that overcharged us was made about five months ago.",
                "This is a complaint about the rudeness of a parking warden roughly four months ago; it has bothered me ever since.",
                "I'd like to lodge a complaint regarding the flooding on Mill Road that your drains caused around five months ago.",
            ],
            "form": [  # event ~7-8 months ago but NOT a complaint
                "Fond memory for the newsletter: the street party about eight months ago was the best yet. Thank you to everyone who helped.",
                "Just recalling that the heritage walk you ran roughly seven months ago was wonderful — any plans to repeat it?",
                "For the records: we moved into the area about eight months ago and have loved every minute. Great community.",
                "The allotment open day some seven months back was a lovely afternoon. Sharing a few photos for the website.",
                "I attended the council's budget meeting around eight months ago and found it genuinely informative. Credit to the team.",
                "Our choir performed at the library about seven months ago — such a warm welcome. We'd happily come again.",
                "Looking back, the recycling workshop you held roughly eight months ago changed how our whole household sorts waste.",
                "The volunteer litter-pick you organised some seven months ago was brilliantly run. Thank you again.",
            ],
            "none": [
                "Just a note to say the new recycling bins arrived this morning. Thank you for sorting it so quickly.",
                "Could you add our book group to the events calendar? Tuesdays at 7pm in the upstairs room.",
                "The streetlight outside number 14 has been flickering this week. Reporting it as requested.",
                "Lovely to see the riverbank path reopened — we walked it on Sunday, the new bridge is a real improvement.",
                "Please update our address for the garden-waste collection: we've moved to 7 Birchfield Rise.",
                "Many thanks to the team who cleared the leaves on Chapel Lane this week — much safer now.",
                "Could I be added to the volunteer mailing list for the summer fair? Happy to run the cake stall again.",
                "The number 43 bus was on time every day this week, which must be a record. Credit where due.",
            ],
        },
    },
    # ---- R3 Family A: world-knowledge inference (the CONTRAST) -------------------
    "medical_rx_drug": {
        "rung": "R3", "family": "A_worldknowledge",
        "compound": [
            "Answer YES only if BOTH are true: the sender is personally seeking medical advice, AND the message names a specific medication that is available only on prescription. Otherwise answer NO.",
            "Does this message BOTH seek medical advice for the writer's own health, AND mention a named prescription-only medicine? Say YES only if both hold.",
            "Is the sender both (a) asking for medical advice about their own health and (b) referring to a specific prescription-only drug by name? Answer YES only when both are present.",
        ],
        "compA": "Is the sender seeking medical advice about a health concern they personally face?",
        "compB": "Does the message mention a medication that is available only on prescription?",
        "cells": {
            "hit": [  # medical advice + a prescription-only medication
                "I've been on amitriptyline for my nerve pain but it's making me so drowsy. Should I cut the dose myself or push through?",
                "My amoxicillin course finishes tomorrow but the infection still looks angry. Do I need more, and should I see someone?",
                "The ramipril gives me a dry cough that won't quit. Is it safe to just stop it, or what should I do?",
                "I'm on sertraline and feel oddly flat and dizzy in the mornings. Is that normal or should I be worried?",
                "My prednisolone taper leaves me shaky and exhausted. Am I reducing too fast — what would you advise?",
                "I take warfarin and I've started bruising badly. Should I be eating differently or getting my levels checked?",
                "The methotrexate makes me nauseous every week. Is there anything I can do, or is this just how it is?",
                "My inhaler isn't enough lately so the GP added montelukast, but now I can't sleep. Should I keep taking it?",
            ],
            "near": [  # medical advice + an OTC / non-prescription remedy (only the medicine changes)
                "I've had a mild tension headache on and off for weeks and paracetamol barely touches it. Should I take more or just rest?",
                "My sore throat still looks angry after a week of honey and lozenges. Do I need to see someone?",
                "I've got a dry cough that won't quit despite the usual cough syrup. Is it safe to ignore, or what should I do?",
                "I've been feeling oddly flat and dizzy in the mornings even with my daily multivitamin. Is that normal or should I worry?",
                "Cutting back on strong coffee leaves me shaky and exhausted. Am I doing it too fast — what would you advise?",
                "I've started bruising badly lately and only take the odd ibuprofen. Should I eat differently or get checked?",
                "The peppermint tea I drink seems to make me nauseous every week. Is there anything I can do, or is this just me?",
                "My breathing's been tight lately even using a steam bowl at night. Should I keep doing it or see someone?",
            ],
            "form": [  # mentions a prescription-only medication but NOT seeking medical advice
                "Just collected my mum's methotrexate prescription from the pharmacy — thank you for arranging the lift to the surgery.",
                "For the noticeboard: the pharmacy now dispenses amoxicillin and other prescriptions on a Sunday. Useful to know.",
                "My late husband's leftover ramipril needs safe disposal. Where's the nearest medicines return point?",
                "I'm writing a community talk on how warfarin was first discovered. Could the library help me find sources?",
                "Our first-aid volunteers asked whether the hall fridge can store residents' insulin and prednisolone at events.",
                "The sertraline shortage has been in the news — is the council's wellbeing drop-in affected at all?",
                "Donating an unopened blood-pressure monitor and some sealed amitriptyline boxes — can the surgery take them?",
                "Could you add 'managing repeat prescriptions like montelukast' as a topic for the over-60s digital course?",
            ],
            "none": [
                "Just a note to say the new recycling bins arrived this morning. Thank you for the quick turnaround.",
                "Could you add our book group to the events calendar? Tuesdays at 7pm in the upstairs room.",
                "The streetlight outside number 14 has flickered all week. Reporting it as requested.",
                "Lovely to see the riverbank path reopened — we walked it on Sunday.",
                "Please update our address for the garden-waste collection: 7 Birchfield Rise.",
                "Many thanks to the team who cleared the leaves on Chapel Lane this week.",
                "Could I join the volunteer mailing list for the summer fair? Happy to run the cake stall.",
                "The number 43 bus was on time every day this week. Credit where due.",
            ],
        },
    },
}

CELLS = ["hit", "near", "form", "none"]
# Which cells are POSITIVE (label 1) for each question type.
POSITIVE = {
    "compound": {"hit"},
    "compA": {"hit", "near"},
    "compB": {"hit", "form"},
}


def _records(cand: str, spec: dict, qtype: str, question: str, paraphrase: int) -> list[dict]:
    records = []
    for cell in CELLS:
        for i, message in enumerate(spec["cells"][cell], start=1):
            label = 1 if cell in POSITIVE[qtype] else 0
            records.append({
                "id": f"{cand}_{cell}_{i:02d}",
                "label": label,
                "label_name": "escalate" if label else "proceed",
                "group": cell,
                "system": SYSTEM,
                "user": USER_TMPL.format(question=question, message=message),
                "meta": {
                    "candidate": cand, "rung": spec["rung"], "family": spec["family"],
                    "cell": cell, "qtype": qtype, "paraphrase": paraphrase,
                    "framing": "ladder_screen_ask", "message": message,
                },
            })
    return records


def main() -> None:
    here = Path(__file__).parent
    (here / "inputs").mkdir(exist_ok=True)
    total = 0
    for cand, spec in CANDIDATES.items():
        sizes = {cell: len(spec["cells"][cell]) for cell in CELLS}
        if set(sizes.values()) != {8}:
            raise SystemExit(f"{cand}: expected 8 items per cell, got {sizes}")
        # compound: 3 paraphrases
        for k, question in enumerate(spec["compound"], start=1):
            recs = _records(cand, spec, "compound", question, k)
            out = here / f"inputs/ladder_screen_{cand}_compound_p{k}.json"
            out.write_text(json.dumps(recs, indent=2, ensure_ascii=False))
            total += len(recs)
            print(f"Wrote {out.name} ({len(recs)} items)")
        # components: 1 each
        for qtype in ("compA", "compB"):
            recs = _records(cand, spec, qtype, spec[qtype], 1)
            out = here / f"inputs/ladder_screen_{cand}_{qtype}.json"
            out.write_text(json.dumps(recs, indent=2, ensure_ascii=False))
            total += len(recs)
            print(f"Wrote {out.name} ({len(recs)} items)")
    print(f"\n{len(CANDIDATES)} candidates x (3 compound + 2 component) = "
          f"{len(CANDIDATES) * 5} files, {total} items total (8 hit/near/form/none each).")


if __name__ == "__main__":
    main()
