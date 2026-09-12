"""--llm output mode: token budget + policy (Phase 12 / design #29)."""

from __future__ import annotations

from enum import Enum

from .kb import estimate_tokens


class LlmPolicy(str, Enum):
    DIAGNOSTICS_FIRST = "diagnostics_first"
    SLICES_FIRST = "slices_first"
    BALANCED = "balanced"
    MINIMAL = "minimal"


def _trim(text: str, budget: int) -> str:
    if budget <= 0:
        return ""
    if estimate_tokens(text) <= budget:
        return text
    # binary-ish shrink by chars
    lo, hi = 0, len(text)
    best = ""
    while lo <= hi:
        mid = (lo + hi) // 2
        cand = text[:mid].rstrip()
        if mid < len(text) and cand:
            cand = cand + "…"
        if estimate_tokens(cand) <= budget:
            best = cand
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def format_for_llm(
    *,
    diagnostics: str = "",
    slices: str = "",
    status: str = "",
    budget_tokens: int = 500,
    policy: str | LlmPolicy = LlmPolicy.BALANCED,
) -> str:
    """Pack compiler output for an LLM under a token budget (D5)."""
    if isinstance(policy, str):
        policy = LlmPolicy(policy)
    budget = max(0, int(budget_tokens))
    diag = (diagnostics or "").strip()
    sl = (slices or "").strip()
    st = (status or "").strip()

    if policy is LlmPolicy.MINIMAL:
        line = st or (diag.splitlines()[0] if diag else (sl.splitlines()[0] if sl else "ok"))
        return _trim(line, budget)

    if policy is LlmPolicy.DIAGNOSTICS_FIRST:
        parts: list[str] = []
        if diag:
            parts.append(diag)
        remain = budget - estimate_tokens("\n\n".join(parts) if parts else "")
        if sl and remain > 0:
            piece = _trim(sl, remain)
            if piece:
                parts.append(piece)
        return _trim("\n\n".join(parts), budget)

    if policy is LlmPolicy.SLICES_FIRST:
        parts = []
        if sl:
            parts.append(sl)
        remain = budget - estimate_tokens("\n\n".join(parts) if parts else "")
        if diag and remain > 0:
            piece = _trim(diag, remain)
            if piece:
                parts.append(piece)
        return _trim("\n\n".join(parts), budget)

    # balanced: status, then alternate short chunks
    chunks: list[str] = []
    if st:
        chunks.append(st)
    dlines = [ln for ln in diag.splitlines() if ln.strip()] if diag else []
    slines = [ln for ln in sl.splitlines() if ln.strip()] if sl else []
    i = j = 0
    while i < len(dlines) or j < len(slines):
        if j < len(slines):
            chunks.append(slines[j])
            j += 1
        if i < len(dlines):
            chunks.append(dlines[i])
            i += 1
    out: list[str] = []
    used = 0
    for ch in chunks:
        cost = estimate_tokens(ch)
        if used + cost > budget:
            rem = budget - used
            if rem > 0:
                piece = _trim(ch, rem)
                if piece:
                    out.append(piece)
            break
        out.append(ch)
        used += cost
    return "\n".join(out)
