"""Smoke test for crosstab_exp2.py — fabricated behaviour JSONs, known answers, no GPU/API.

Builds a tiny synthetic Exp-2-shaped behaviour set in a temp dir (12 live docs + 1
truncated), runs crosstab_exp2.py on it, and asserts the computed rates, verdict,
exclusion logic, K1-core, and matched lists against hand-computed expectations.

    python crosstab_smoke.py     # prints SMOKE PASS on success
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def beh(idx, dc, cl, flag_or_yes, truncated=False, extra=None):
    return dict(id=idx, label=1 if cl == "hit" else 0, cell=cl, doccond=dc,
                pair_stem=idx.rsplit("_", 1)[0], behaviour=flag_or_yes,
                truncated=truncated, generated_text="(smoke)", **(extra or {}))


DOCS = [  # (id, doccond, cell)
    ("lh1", "legal", "hit"), ("lh2", "legal", "hit"), ("lh3", "legal", "hit"),
    ("lh4", "legal", "hit"), ("lh5", "legal", "hit"),     # lh5 -> truncated, excluded
    ("mh1", "medical", "hit"), ("mh2", "medical", "hit"),
    ("mh3", "medical", "hit"), ("mh4", "medical", "hit"),
    ("ln1", "legal", "near"), ("mn1", "medical", "near"),
    ("f1", "neutral", "form"), ("n1", "neutral", "none"),
]
FLAG_LEGAL = {"lh1", "lh2", "lh3", "lh5", "ln1"}            # ln1 = the over-flag
FLAG_MEDICAL = {"lh1", "mh1", "mh2", "mh3", "mh4"}          # lh1 = the swapped flag
ASK_LEGAL_VOTES = {"lh2": ["YES", "NO", "YES"]}             # lh2 -> INCONSISTENT
# defaults: own-domain hits YES x3, everything else NO x3


def main() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="crosstab_smoke_"))
    for rule, flags in (("legal", FLAG_LEGAL), ("medical", FLAG_MEDICAL)):
        recs = [beh(i, dc, cl, "FLAG" if i in flags else "NOFLAG",
                    truncated=(i == "lh5" and rule == "legal"), extra={"rulecond": rule})
                for i, dc, cl in DOCS]
        (tmp / f"crosstab_beh_action_{rule}.json").write_text(
            json.dumps(dict(meta=dict(framing="exp2_keeper_action", smoke=True), records=recs)))
    for cond in ("legal", "medical"):
        for k in (1, 2, 3):
            recs = []
            for i, dc, cl in DOCS:
                votes = ASK_LEGAL_VOTES.get(i) if cond == "legal" else None
                ans = votes[k - 1] if votes else ("YES" if (dc == cond and cl == "hit") else "NO")
                recs.append(beh(i, dc, cl, ans, extra={"askcond": cond, "paraphrase": k}))
            (tmp / f"crosstab_beh_ask_{cond}_p{k}.json").write_text(
                json.dumps(dict(meta=dict(framing="exp2_keeper_ask", smoke=True), records=recs)))

    out, matched = tmp / "crosstab_exp2.json", tmp / "crosstab_behaviour_matched.json"
    r = subprocess.run([sys.executable, "crosstab_exp2.py", "--acts-dir", str(tmp),
                        "--beh-dir", str(tmp), "--out", str(out), "--matched-out", str(matched)],
                       capture_output=True, text=True, cwd=Path(__file__).parent)
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr)
        raise SystemExit("SMOKE FAIL: crosstab_exp2.py exited nonzero")

    res = json.loads(out.read_text())
    s, m = res["summary"], json.loads(matched.read_text())
    exp = [
        (res["meta"]["excluded_truncated"], ["lh5"], "truncation exclusion"),
        (s["pooled"]["n"], 8, "pooled live hits"),
        (s["pooled"]["matching"], 7, "pooled matching flags"),
        (s["pooled"]["swapped"], 1, "pooled swapped flags"),
        (s["verdict"], "VERIFIED", "verdict band (87.5% / 12.5%)"),
        (s["hits"]["legal"]["both"], 1, "legal both-flagged"),
        (s["hits"]["legal"]["neither"], 1, "legal neither-flagged"),
        (s["k1_core"]["n"], 7, "K1-core size (lh2 inconsistent dropped)"),
        (s["k1_core"]["matching"], 6, "K1-core matching"),
        (s["k1_core"]["swapped"], 1, "K1-core swapped"),
        (sorted(m["flagged_both"]), ["lh1"], "matched flagged-both"),
        (sorted(m["flagged_neither"]), ["f1", "lh4", "mn1", "n1"], "matched flagged-neither"),
        (next(x for x in s["overflag"] if x["cell"] == "near" and x["doccond"] == "legal")["flag_legal"],
         1, "over-flag localisation (ln1)"),
    ]
    for got, want, what in exp:
        assert got == want, f"SMOKE FAIL on {what}: got {got!r}, want {want!r}"
    print(f"SMOKE PASS — all {len(exp)} checks (artifacts in {tmp})")


if __name__ == "__main__":
    main()
