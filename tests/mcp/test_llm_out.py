"""--llm formatter (Phase 12 T3)."""

from __future__ import annotations

from golem.kb import estimate_tokens
from golem.llm_out import LlmPolicy, format_for_llm


def test_minimal():
    t = format_for_llm(
        status="PARTIAL holes=1",
        diagnostics="err1\nerr2",
        slices="ADD[1,?]",
        budget_tokens=50,
        policy=LlmPolicy.MINIMAL,
    )
    assert "PARTIAL" in t
    assert estimate_tokens(t) <= 50


def test_diagnostics_first():
    t = format_for_llm(
        diagnostics="TYPE_ERR at 0",
        slices="ADD[1,2]\nMUL[3,4]",
        budget_tokens=100,
        policy="diagnostics_first",
    )
    assert t.index("TYPE_ERR") < t.index("ADD")


def test_slices_first():
    t = format_for_llm(
        diagnostics="TYPE_ERR",
        slices="ADD[1,2]",
        budget_tokens=100,
        policy="slices_first",
    )
    assert t.index("ADD") < t.index("TYPE_ERR")


def test_budget_respected():
    big = "x" * 4000
    t = format_for_llm(slices=big, budget_tokens=20, policy="slices_first")
    assert estimate_tokens(t) <= 20
