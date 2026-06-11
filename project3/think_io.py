"""Shared reader for Inspect samples that is correct in BOTH no-think and thinking mode.

Why this exists (2026-06-11 thinking-sweep bug): in Qwen3 thinking runs the chain of
thought comes back as a separate `ContentReasoning` part and the final answer is a
(possibly empty) `ContentText`; `s.output.completion` holds only the answer. A sample
that exhausts max_tokens INSIDE the think block returns an EMPTY answer — that is a
TRUNCATION, not a no-FLAG omission. The first read of the sweep scored 16 truncated G1
samples as fake omissions (47.5% → really 3/24 valid) and never saw any CoT (cotN
stuck at 0), because both observers read only `completion`.

read_sample(s) -> (reasoning, answer, truncated):
  reasoning  — the CoT text (from ContentReasoning, or an inline <think>…</think>);
               "" in no-think runs.
  answer     — the post-think answer (== s.output.completion in the list case).
  truncated  — True if the generation was cut off (stop_reason max_tokens) or the
               answer is empty. Truncated samples must be EXCLUDED from scoring, not
               counted as omissions.

Answer is taken from `s.output.completion` (canonical — never leaks reasoning); only
the reasoning is pulled from the content parts, and strictly from ContentReasoning by
type name (ContentReasoning also exposes a `.text` property that aliases the CoT, so
filtering by type is what keeps the two channels separate).
"""

from __future__ import annotations


def read_sample(s) -> tuple[str, str, bool]:
    ch = s.output.choices[0] if s.output.choices else None
    stop = getattr(ch, "stop_reason", None) if ch else None
    answer = s.output.completion or ""

    reasoning = ""
    content = ch.message.content if ch else None
    if isinstance(content, list):
        reasoning = "".join(
            (getattr(p, "reasoning", "") or "")
            for p in content
            if type(p).__name__ == "ContentReasoning"
        )
    if not reasoning and "</think>" in answer:  # providers that inline the tag
        head, answer = answer.rsplit("</think>", 1)
        reasoning = head.replace("<think>", "")

    truncated = (stop == "max_tokens") or (not answer.strip())
    return reasoning, answer, truncated
