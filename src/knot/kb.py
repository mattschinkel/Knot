"""Token-budgeted knowledge retrieval (Phase 12 / design #28)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .kb_data import CARDS


def estimate_tokens(text: str) -> int:
    """Stable token estimate without tiktoken (D3): chars/4."""
    if not text:
        return 0
    return max(1, len(text) // 4)


@dataclass(frozen=True)
class KbCard:
    id: str
    title: str
    tags: tuple[str, ...]
    body: str

    @property
    def tokens(self) -> int:
        return estimate_tokens(self.render())

    def render(self) -> str:
        return self.title + ": " + self.body


def load_cards(extra_dir: str | Path | None = None) -> list[KbCard]:
    """Built-in cards plus optional docs/kb/*.md overlay (title = stem)."""
    out = [
        KbCard(id=c[0], title=c[1], tags=c[2], body=c[3]) for c in CARDS
    ]
    if extra_dir is not None:
        root = Path(extra_dir)
        if root.is_dir():
            for p in sorted(root.glob("*.md")):
                body = p.read_text(encoding="utf-8").strip()
                out.append(
                    KbCard(
                        id="file:" + p.stem,
                        title=p.stem,
                        tags=("file", p.stem.lower()),
                        body=body,
                    )
                )
    return out


def _score(card: KbCard, query: str) -> int:
    q = query.lower().strip()
    if not q:
        return 0
    score = 0
    if q == card.id.lower() or q == card.title.lower():
        score += 100
    if q in card.id.lower() or q in card.title.lower():
        score += 40
    for tag in card.tags:
        if q == tag or q in tag or tag in q:
            score += 20
    if q in card.body.lower():
        score += 10
    for word in q.replace(",", " ").split():
        if len(word) < 2:
            continue
        if word in card.title.lower() or word in card.id.lower():
            score += 15
        if word in card.tags:
            score += 12
        if word in card.body.lower():
            score += 5
    return score


@dataclass(frozen=True)
class KbResult:
    ok: bool
    text: str
    tokens: int
    card_ids: tuple[str, ...]
    truncated: bool


def retrieve(
    query: str,
    max_tokens: int = 500,
    *,
    extra_dir: str | Path | None = None,
) -> KbResult:
    """Pack matching cards under max_tokens (design #28)."""
    if max_tokens <= 0:
        return KbResult(True, "", 0, (), True)
    cards = load_cards(extra_dir)
    ranked = sorted(
        (( _score(c, query), c) for c in cards),
        key=lambda x: (-x[0], x[1].id),
    )
    ranked = [(s, c) for s, c in ranked if s > 0]
    if not ranked:
        # fallback: return a short miss under budget
        miss = "kb: no cards matched " + repr(query)
        miss = miss[: max_tokens * 4]
        return KbResult(True, miss, estimate_tokens(miss), (), False)

    parts: list[str] = []
    ids: list[str] = []
    used = 0
    truncated = False
    sep = "\n\n"
    sep_cost = estimate_tokens(sep)

    for _score_v, card in ranked:
        chunk = card.render()
        cost = estimate_tokens(chunk)
        extra = sep_cost if parts else 0
        if used + extra + cost > max_tokens:
            remain = max_tokens - used - extra
            if remain <= 0:
                truncated = True
                break
            approx_chars = max(0, remain * 4)
            chunk = chunk[:approx_chars].rstrip()
            if len(chunk) < len(card.render()):
                chunk = chunk + "…"
            cost = estimate_tokens(chunk)
            if cost > remain or not chunk.strip("…"):
                truncated = True
                break
            parts.append(chunk)
            ids.append(card.id)
            used += extra + cost
            truncated = True
            break
        parts.append(chunk)
        ids.append(card.id)
        used += extra + cost
    text = sep.join(parts)
    # Final clamp: never exceed budget after join
    while text and estimate_tokens(text) > max_tokens:
        text = text[:-4].rstrip() + "…"
        truncated = True
    if estimate_tokens(text) > max_tokens:
        text = text[: max_tokens * 4]
        truncated = True
    return KbResult(True, text, estimate_tokens(text), tuple(ids), truncated)
