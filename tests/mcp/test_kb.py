"""kb retrieve (Phase 12 T2)."""

from __future__ import annotations

from golem.kb import estimate_tokens, retrieve


def test_estimate_tokens():
    assert estimate_tokens("") == 0
    assert estimate_tokens("abcd") == 1
    assert estimate_tokens("a" * 40) == 10


def test_retrieve_reduce_under_budget():
    r = retrieve("REDUCE", max_tokens=80)
    assert r.ok
    assert r.tokens <= 80
    assert "REDUCE" in r.text or r.card_ids


def test_retrieve_add():
    r = retrieve("ADD", max_tokens=200)
    assert "ADD" in r.text
    assert "op-add" in r.card_ids


def test_retrieve_tiny_budget_truncates():
    r = retrieve("Canonical AIR", max_tokens=5)
    assert r.tokens <= 5
    assert r.truncated or r.tokens <= 5
