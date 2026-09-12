"""Tests for tools.spec_lint — the deterministic phase-spec consistency gate."""
from __future__ import annotations

from pathlib import Path

import spec_lint
from spec_lint import Issue, LintReport, lint

# A minimal, clean, autonomous spec that should pass every rule.
CLEAN = """\
# Phase 1 Spec — AST + Parser + GBNF Grammar (Golem kernel, Python host)

> Owner: R1 Architect (decides autonomously). Implementation: R2 Kernel Engineer.
> Status: DECIDED by R1 (autonomous) — DRAFT for crew implementation; no code yet.

## 1. Scope
In scope: AST. Out: type checker.

## 2. Design decisions (DECIDED by R1)
Each decision is FINAL, recorded by R1.

- **D1 — AST is a graph with numeric IDs.** IDs are compiler-internal; the LLM
  addresses nodes by structural path + optional @label. The GBNF grammar
  contains no numeric IDs at all.
- **D2 — Canonical form is bracket notation.** `OP[arg1, arg2]`; `F(...)` is a
  pretty-printer alias only.

## 3. AST node model (`src/golem/ast.py`)
Nodes have id, path, label.

## 4. File layout
```
src/golem/ast.py
```

## 5. Definition of done
- [ ] AST node model
- [ ] parser round-trips
- [ ] all tests pass

## 6. Resolved sub-questions (DECIDED by R1)
- **Q1 — path syntax:** dot/bracket. DECISION: dot/bracket.
"""


def _err_rules(report: LintReport) -> set[str]:
    return {i.rule for i in report.issues if i.severity == "error"}


def test_clean_spec_passes() -> None:
    rep = lint(CLEAN)
    assert rep.ok, [summarize_all(rep)]
    assert rep.issues == ()


def test_missing_status_line_fails() -> None:
    bad = CLEAN.replace("> Status: DECIDED by R1 (autonomous) — DRAFT for crew implementation; no code yet.\n", "")
    rep = lint(bad)
    assert not rep.ok
    assert "R1_status" in _err_rules(rep)


def test_non_autonomous_status_fails() -> None:
    bad = CLEAN.replace(
        "DECIDED by R1 (autonomous) — DRAFT for crew implementation; no code yet.",
        "DRAFT for human review — no implementation code yet.",
    )
    rep = lint(bad)
    assert not rep.ok
    assert "R1_status" in _err_rules(rep)


def test_status_claims_done_but_dod_unchecked_fails() -> None:
    bad = CLEAN.replace(
        "DECIDED by R1 (autonomous) — DRAFT for crew implementation; no code yet.",
        "DECIDED by R1 (autonomous) — implemented; tests green.",
    )
    rep = lint(bad)
    assert not rep.ok
    assert "R1_status" in _err_rules(rep)


def test_broken_section_numbering_fails() -> None:
    # Restart numbering at §0 after §2 (the exact defect R1 produced).
    bad = CLEAN.replace("## 3. AST node model", "## 0. AST node model")
    rep = lint(bad)
    assert not rep.ok
    assert "R2_numbering" in _err_rules(rep)


def test_first_section_not_one_fails() -> None:
    bad = CLEAN.replace("## 1. Scope", "## 2. Scope")
    rep = lint(bad)
    assert not rep.ok
    assert "R2_numbering" in _err_rules(rep)


def test_checked_dod_in_draft_fails() -> None:
    bad = CLEAN.replace("- [ ] AST node model", "- [x] AST node model")
    rep = lint(bad)
    assert not rep.ok
    assert "R3_dod" in _err_rules(rep)


def test_d_contradiction_numeric_ids_in_grammar_fails() -> None:
    # The exact contradiction R1 produced (D5 vs D7 vs §21).
    bad = CLEAN.replace(
        "- **D2 — Canonical form is bracket notation.** `OP[arg1, arg2]`; `F(...)` is a\n  pretty-printer alias only.",
        "- **D5 — GBNF grammar enforces unique numeric IDs.** The grammar includes a "
        "constraint that every node ID must be unique and must not be an arbitrary integer.",
    )
    rep = lint(bad)
    assert not rep.ok
    assert "R4_invariants" in _err_rules(rep)


def test_d_canonical_is_f_shorthand_fails() -> None:
    bad = CLEAN.replace(
        "- **D2 — Canonical form is bracket notation.** `OP[arg1, arg2]`; `F(...)` is a\n  pretty-printer alias only.",
        "- **D2 — Canonical form is the F(name) shorthand.** Functions are written F(x).",
    )
    rep = lint(bad)
    assert not rep.ok
    assert "R4_invariants" in _err_rules(rep)


def test_missing_required_section_fails() -> None:
    bad = CLEAN.replace("## 6. Resolved sub-questions (DECIDED by R1)\n- **Q1 — path syntax:** dot/bracket. DECISION: dot/bracket.\n", "")
    rep = lint(bad)
    assert not rep.ok
    assert "R5_sections" in _err_rules(rep)


def test_forbidden_phrase_in_body_fails() -> None:
    bad = CLEAN + "\nPlease confirm the above before proceeding.\n"
    rep = lint(bad)
    assert not rep.ok
    assert "R1_status" in _err_rules(rep)


def test_real_phase1_spec_passes() -> None:
    """The committed (fixed) phase1_spec.md must pass the gate."""
    p = Path(__file__).resolve().parent.parent / "ai_docs" / "phase1_spec.md"
    if not p.is_file():
        return  # not available in this environment
    rep = spec_lint.lint_file(p)
    assert rep.ok, spec_lint.summarize(rep)


def summarize_all(rep: LintReport) -> str:
    return spec_lint.summarize(rep)
