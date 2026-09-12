"""spec_lint.py — deterministic consistency linter for Golem phase specs.

This is the proper fix for a gap the drift-check gate (src/golem/drift.py,
metrics M1-M5) does NOT cover: the drift gate measures *generation* quality
(token count, generation accuracy, edit round-trip, ...), but a 4B R1 can
also introduce *spec-level* contradictions by mirroring its template — e.g.
a `D` decision that contradicts a design-doc invariant, a status line that
claims "implemented; tests green" for an unimplemented phase, broken section
numbering, or pre-checked Definition-of-Done boxes.

This linter is fully deterministic (no LLM, no I/O beyond reading the spec
file) and checks a phaseN_spec.md against a fixed, small rule set derived
from the design-doc invariants (`ai_docs/golem_design.md` §21) and the
autonomous-spec template (`ai_docs/phase0_spec.md`). Failures are fed back
to R1 to re-draft — no human gate.

Rules:
  R1 status       — the `> Status:` line is autonomous and not stale.
  R2 numbering     — `## N.` headings are strictly increasing from 1.
  R3 dod boxes     — DoD checkboxes are unchecked while the spec is a draft.
  R4 invariants   — no `D` decision contradicts a §21 invariant.
  R5 sections      — required sections are present.

Usage (PowerShell):
    .\\.venv\\Scripts\\python.exe -m tools.spec_lint ai_docs\\phase1_spec.md
or:
    .\\.venv\\Scripts\\python.exe tools\\spec_lint.py ai_docs\\phase1_spec.md
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Required top-level sections (matched as substrings of `## ` headings).
REQUIRED_SECTIONS = (
    "Scope",
    "Design decisions",
    "File layout",
    "Definition of done",
    "Resolved sub-questions",
)

# Design-doc §21 invariants, encoded as contradictions a `D` decision must
# not assert. Each entry is (id, description, predicate(line) -> bool).
# A predicate returning True means the line VIOLATES the invariant.
_DENIALS = (
    "never writes", "never appear", "never in source", "not in source",
    "not in the grammar", "no numeric id", "no node id", "no id token",
    "without numeric id", "does not appear", "compiler-internal",
    "not author-pinned",
)


def _ids_asserted_in_grammar_or_source(line: str) -> bool:
    """INV-A: numeric IDs are compiler-internal; they never appear in source
    the LLM writes, in the GBNF grammar, or in emitted syntax. Flag a D line
    that ASSERTS numeric IDs live in the grammar/source/emitted syntax — but
    ignore lines that explicitly DENY their presence (e.g. 'never writes them
    into source', 'no numeric id', 'compiler-internal')."""
    low = line.lower()
    if "numeric id" not in low and "node id" not in low:
        return False
    if not any(t in low for t in ("gbnf", "grammar", "emitted", "source")):
        return False
    if any(d in low for d in _DENIALS):
        return False  # the line denies IDs in source/grammar — not a violation
    return any(t in low for t in ("enforce", "include", "contain", "appear", "emit", "write"))


def _canonical_is_f_shorthand(line: str) -> bool:
    """INV-B: the canonical form is bracket notation (`OP[...]`); `F(...)`
    is a pretty-printer alias only. Flag a D line that calls `F(...)` canonical
    without mentioning bracket notation."""
    low = line.lower()
    return "canonical" in low and "f(" in low and "bracket" not in low


INVARIANTS = (
    ("INV-A", "numeric IDs are compiler-internal (not in source/GBNF/emitted syntax)", _ids_asserted_in_grammar_or_source),
    ("INV-B", "canonical form is bracket notation (F(...) is pretty-printer alias only)", _canonical_is_f_shorthand),
)

# Stale / non-autonomous phrasing that must not appear anywhere in an
# autonomous spec (mirrors architect_phase.py DRAFT_INSTRUCTIONS rules).
FORBIDDEN_PHRASES = (
    "for human review",
    "please confirm",
    "please amend",
    "to confirm (human)",
    "R1 -> human",
    "open for human",
)


@dataclass(frozen=True)
class Issue:
    rule: str
    severity: str  # "error" | "warning"
    message: str


@dataclass(frozen=True)
class LintReport:
    path: str
    issues: tuple[Issue, ...] = ()
    ok: bool = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "ok", not any(i.severity == "error" for i in self.issues))


def _status_line(text: str) -> str | None:
    m = re.search(r"^>\s*Status:\s*(.*)$", text, re.MULTILINE)
    return m.group(1).strip() if m else None


def _section_numbers(text: str) -> list[int]:
    return [int(m.group(1)) for m in re.finditer(r"^## (\d+)\. ", text, re.MULTILINE)]


def _dod_section(text: str) -> str | None:
    m = re.search(r"^## \d+\. Definition of done\s*$(.*?)(?=^## \d+\. |\Z)", text, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else None


def _d_lines(text: str) -> list[str]:
    # Lines beginning a decision bullet: "- **D1 — ...**" or "- **D1: ...**"
    return re.findall(r"^- \*\*D\d+.*$", text, re.MULTILINE)


def _is_draft(status: str | None) -> bool:
    if not status:
        return True
    low = status.lower()
    return "draft" in low or "no code yet" in low or "decided by r1" in low and "implemented" not in low


def lint(text: str) -> LintReport:
    issues: list[Issue] = []
    status = _status_line(text)

    # R1 — status line.
    if status is None:
        issues.append(Issue("R1_status", "error", "no `> Status:` line found"))
    else:
        if "DECIDED by R1" not in status and "decided by r1" not in status.lower():
            issues.append(Issue("R1_status", "error", "status is not marked DECIDED by R1 (autonomy)"))
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in status.lower():
                issues.append(Issue("R1_status", "error", f"status uses non-autonomous phrase '{phrase}'"))
        if "implemented" in status.lower() and "tests green" in status.lower():
            dod = _dod_section(text) or ""
            checked = re.findall(r"^\s*-\s*\[x\]", dod, re.MULTILINE)
            unchecked = re.findall(r"^\s*-\s*\[ \]", dod, re.MULTILINE)
            if unchecked and not checked:
                issues.append(Issue("R1_status", "error", "status claims 'implemented; tests green' but all DoD boxes are unchecked"))

    # R2 — section numbering strictly increasing from 1.
    nums = _section_numbers(text)
    if nums:
        if nums[0] != 1:
            issues.append(Issue("R2_numbering", "error", f"first section is §{nums[0]}, expected §1"))
        for a, b in zip(nums, nums[1:]):
            if b != a + 1:
                issues.append(Issue("R2_numbering", "error", f"section numbering not monotonic: §{a} -> §{b}"))
                break
    else:
        issues.append(Issue("R2_numbering", "warning", "no `## N.` numbered sections found"))

    # R3 — DoD boxes unchecked while draft.
    if _is_draft(status):
        dod = _dod_section(text) or ""
        checked = re.findall(r"^\s*-\s*\[x\]", dod, re.MULTILINE)
        if checked:
            issues.append(Issue("R3_dod", "error", f"{len(checked)} DoD box(es) checked '[x]' in a draft spec"))

    # R4 — invariants: no D decision contradicts a §21 invariant.
    for line in _d_lines(text):
        for inv_id, desc, pred in INVARIANTS:
            if pred(line):
                issues.append(Issue("R4_invariants", "error", f"{inv_id} violated by a D decision ({desc})"))

    # R5 — required sections present.
    headings = re.findall(r"^## \d+\.\s*(.*)$", text, re.MULTILINE)
    flat = " ".join(h.lower() for h in headings)
    for sec in REQUIRED_SECTIONS:
        if sec.lower() not in flat:
            issues.append(Issue("R5_sections", "error", f"missing required section: {sec}"))

    # Forbidden phrases anywhere in the body (non-autonomous leftovers).
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in text.lower():
            issues.append(Issue("R1_status", "error", f"non-autonomous phrase '{phrase}' appears in the spec"))

    return LintReport(path="", issues=tuple(issues))


def lint_file(path: str | Path) -> LintReport:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    rep = lint(text)
    return LintReport(path=str(p), issues=rep.issues)


def summarize(report: LintReport) -> str:
    if report.ok and not report.issues:
        return f"OK: {report.path} — no issues."
    lines = [f"{'OK' if report.ok else 'FAIL'}: {report.path} — {len(report.issues)} issue(s)"]
    for i in report.issues:
        lines.append(f"  [{i.rule}] {i.severity}: {i.message}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python -m tools.spec_lint <phaseN_spec.md>", file=sys.stderr)
        return 2
    report = lint_file(argv[1])
    print(summarize(report))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
