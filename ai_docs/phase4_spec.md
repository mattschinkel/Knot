# Phase 4 Spec — Holes + Partial Compile

> Owner: Cursor (build path as of 2026-09-11). Decisions follow `ai_docs/axiom_design.md` §6 and D-FB10.  
> Status: DECIDED — implementing.

Phase 4 makes **partial programs** a first-class compile state. Holes already parse and infer (Phase 1–2); this phase classifies whole expressions as VALID / PARTIAL / INVALID, reports holes with expected type + candidates, propagates hole constraints from context, and traps holes at evaluation time as error values (no Python exceptions).

---

## 1. Scope

### In Phase 4
- `CompileStatus`: VALID | PARTIAL | INVALID
- `compile_check(expr, env) -> CompileReport` (type + holes + errors + status)
- `HoleReport`: id, expected type, context path, candidate suggestions
- Candidate suggestions from Env bindings + type defaults
- Hole constraint propagation: bare `?` adopts expected type from parent context (D-FB10)
- Evaluation trap: reaching a hole yields `ErrorVal` (kind `hole_trap`), never raises
- Drift metric M4 (partial-compile coherence) measured and baselined

### Explicitly OUT of Phase 4
- Structured repair suggestions beyond hole candidates — Phase 5
- Graph edit ops — Phase 6
- Full bytecode VM — Phase 9
- Locked AIR for effect/contract annotations on holes

---

## 2. Design decisions (DECIDED)

### D1 — Three compile states
**DECISION:** `VALID` = typed, no holes, no errors. `PARTIAL` = typed, ≥1 hole, no errors. `INVALID` = ≥1 type/effect/contract error (holes may also be present).  
**Rationale:** design §6; LLM partner needs pass/partial/fail, not only bool.

### D2 — Holes do not fail the type check by themselves
**DECISION:** A bare or typed hole is never an error by itself. Unknown hole labels remain `TypeErrorVal` → INVALID.  
**Rationale:** partial programs must type-check.

### D3 — Bidirectional expected type for holes
**DECISION:** `infer_type(expr, env, expected=None)` passes an optional expected type. Bare holes return `expected` when provided, else `ANY`. Typed holes unify label with `expected` when both present. Binary/unary/compare/IF propagate expected into hole operands.  
**Rationale:** D-FB10; avoids narrow per-op heuristics where possible by using one expected channel.

### D4 — Candidates are deterministic and finite
**DECISION:** Candidates = Env names whose type unifies with (or subtypes) expected, plus a small fixed default literal per base type (`0`, `0.0`, `false`, `""`, `()`). No LLM calls. Cap at 8.  
**Rationale:** kernel stays deterministic; design §6 example (`0@money`, `items[0]`).

### D5 — Runtime hole trap is an error value
**DECISION:** `evaluate` returns `ErrorVal(StructuredError(kind="hole_trap", ...))` on `HoleExpr` / `HoleVal`. Never raises.  
**Rationale:** errors-as-values (design §7); Phase 5 will enrich repairs.

### D6 — M4 measurement
**DECISION:** M4 = fraction of a fixed suite of hole-bearing programs that `compile_check` as PARTIAL (not INVALID). Suite lives in `tests/partial/`. Higher is better.  
**Rationale:** agents §8 metric M4 prereq Phase 4.

---

## 3. File layout

```
src/knot/
  partial.py     # CompileStatus, HoleReport, CompileReport, compile_check,
                 # suggest_candidates, evaluate
  checker.py     # infer_type(..., expected=None); hole propagation
tests/partial/
  test_status.py
  test_holes_report.py
  test_candidates.py
  test_propagate.py
  test_eval_trap.py
  test_partial_prop.py
```

---

## 4. Definition of done

- [x] Spec decided (this document)
- [x] VALID/PARTIAL/INVALID via `compile_check`
- [x] Hole reports with expected + candidates
- [x] Bare hole constraint propagation in arithmetic/compare/IF
- [x] `evaluate` traps holes as ErrorVal (no raise)
- [x] Property tests green
- [x] Drift baseline phase 4 includes M4
- [x] Full pytest green

---

## 5. Tasks

| ID | Goal | File | Symbol | Test |
|----|------|------|--------|------|
| T1 | CompileStatus + CompileReport + compile_check | `partial.py` | `compile_check` | `test_status.py` |
| T2 | Collect HoleReports (id, expected, context) | `partial.py` | `collect_holes` | `test_holes_report.py` |
| T3 | suggest_candidates from Env + defaults | `partial.py` | `suggest_candidates` | `test_candidates.py` |
| T4 | infer_type expected= + hole propagation | `checker.py` | `infer_type` | `test_propagate.py` |
| T5 | evaluate hole trap as ErrorVal | `partial.py` | `evaluate` | `test_eval_trap.py` |
| T6 | Property tests (no raise; PARTIAL suite) | `tests/partial/` | props | `test_partial_prop.py` |
| T7 | Drift M4 + baseline phase 4 | `drift` / baseline | `check()` | `tests/drift/` |
