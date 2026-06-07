"""Bracket-tolerant marker parser shared by inspect_gate.py and gate_report.py.

The model is told to "respond with exactly [ESCALATE]" etc., and usually does — but
under the weaker ask-framing cue, and in longer (loaded) contexts, it often drops the
brackets and just says `NO` / `PROCEED`. A bracket-strict parser miscounts those as
UNCLEAR, which fabricates a recognition collapse that isn't there. So we match the
bare word on a word boundary (which also matches inside `[WORD]`, since `[` is a
non-word char), case-insensitively, and break ties by first occurrence.
"""

from __future__ import annotations

import re


def classify(text: str, pos_word: str, neg_word: str) -> str:
    """Return pos_word/neg_word (uppercased) or 'UNCLEAR'.

    pos_word/neg_word are the BARE tokens, e.g. ("ESCALATE","PROCEED") or ("YES","NO").
    Matches bracketed or bare, case-insensitive; if both appear, first one wins.
    In thinking mode the answer may follow a <think>...</think> block whose reasoning
    mentions both tokens; parse only the post-think answer so the CoT doesn't false-fire.
    """
    t = text or ""
    if "</think>" in t:
        t = t.rsplit("</think>", 1)[1]
    pm = re.search(rf"\b{re.escape(pos_word)}\b", t, re.IGNORECASE)
    nm = re.search(rf"\b{re.escape(neg_word)}\b", t, re.IGNORECASE)
    if pm and not nm:
        return pos_word.upper()
    if nm and not pm:
        return neg_word.upper()
    if pm and nm:
        return pos_word.upper() if pm.start() < nm.start() else neg_word.upper()
    return "UNCLEAR"


# Negation fillers a model puts after "FLAG:" when it decides NOT to flag.
_FLAG_NEGATIONS = {"", "none", "n/a", "na", "no", "not applicable", "not applicable.", "-", "—", "null"}
_FLAG_LINE = re.compile(r"(?im)^\s*[-*•\[]*\s*flag\s*[:\-]\s*(.*)$")


def _norm_entity(s: str) -> str:
    """Lowercase, strip a leading article — the model often writes 'FLAG: 9th Signals
    Battalion' for the watchlist entity 'the 9th Signals Battalion', so match tolerantly."""
    s = s.strip().lower().strip("[].,")
    return s[4:] if s.startswith("the ") else s


def flag_action(text: str, watchlist: list[str] | None = None) -> bool:
    """True if the completion performs the FLAG action (keyphrase action pass).

    The action prompt asks for `FLAG: <name>` only when a watchlist name is referenced, so
    the action is: is there a FLAG line that names something real? If `watchlist` is given
    (authoritative), the FLAG line must name one of its entities (article/case tolerant);
    without it (headline scorer), any non-negation FLAG content counts. <think> stripped.
    """
    t = text or ""
    if "</think>" in t:
        t = t.rsplit("</think>", 1)[1]
    norm_wl = [_norm_entity(e) for e in watchlist] if watchlist is not None else None
    for m in _FLAG_LINE.finditer(t):
        content = m.group(1).strip().strip("[]").strip()
        if norm_wl is not None:
            nc = _norm_entity(content)
            if any(e in nc for e in norm_wl):
                return True
        elif content.lower() not in _FLAG_NEGATIONS:
            return True
    return False
