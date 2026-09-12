# Phase 2 Tasks (drafted by R1; table normalized for phase_crew.parse_tasks)

## Overview
Fragment-sized tasks for the Phase 2 type checker. Builds on Phase 0 `types.py` /
`values.py` (do NOT recreate the type algebra). Checker works on Phase 1 AST nodes.
Final task is the drift-check gate.

---

## Tasks

| ID | Goal | File | Function/Class | Test |
|---|------|------|----------------|------|
| T1 | Extend unify beyond reflexive stub (Option List Tuple Map) | `src/golem/types.py` | `unify()` | `tests/checker/test_unify.py` |
| T2 | Extend subtype for List Set Map Tuple structural cases | `src/golem/types.py` | `subtype()` | `tests/checker/test_subtype.py` |
| T3 | Implement scoped type environment Env | `src/golem/env.py` | `Env` | `tests/checker/test_env.py` |
| T4 | Create checker module with TypeErrorVal helper | `src/golem/checker.py` | `type_error()` | `tests/checker/test_checker_base.py` |
| T5 | Infer types for LitExpr TypedLit IdentExpr UnitExpr | `src/golem/checker.py` | `infer_type()` | `tests/checker/test_infer_lit.py` |
| T6 | Implement check_binary_op for ADD SUB MUL DIV MOD | `src/golem/checker.py` | `check_binary_op()` | `tests/checker/test_binary_ops.py` |
| T7 | Implement check_unary_op for NEG NOT | `src/golem/checker.py` | `check_unary_op()` | `tests/checker/test_unary_ops.py` |
| T8 | Implement comparison and logic op rules EQ NE LT LE GT GE AND OR | `src/golem/checker.py` | `check_compare_op()` | `tests/checker/test_compare_ops.py` |
| T9 | Infer OpExpr via check_binary_op check_unary_op | `src/golem/checker.py` | `infer_type()` | `tests/checker/test_infer_op.py` |
| T10 | Infer IF CondExpr branches with unify | `src/golem/checker.py` | `infer_if()` | `tests/checker/test_infer_if.py` |
| T11 | Infer HoleExpr expected type from label | `src/golem/checker.py` | `infer_hole()` | `tests/checker/test_infer_hole.py` |
| T12 | Infer FnExpr and CallExpr application | `src/golem/checker.py` | `infer_fn()` | `tests/checker/test_infer_fn.py` |
| T13 | Infer DefNode and LET-style bindings via Env | `src/golem/checker.py` | `infer_def()` | `tests/checker/test_infer_def.py` |
| T14 | Type-check GET FIELD SET access ops | `src/golem/checker.py` | `check_access()` | `tests/checker/test_access.py` |
| T15 | Type-check collection ops LEN AT APPEND CONCAT MAP FILTER | `src/golem/checker.py` | `check_collection()` | `tests/checker/test_collection.py` |
| T16 | Public check_expr dispatcher over AST nodes | `src/golem/checker.py` | `check_expr()` | `tests/checker/test_check_expr.py` |
| T17 | Property tests for checker (no raise; holes ok) | `tests/checker/` | `test_no_raise`, `test_hole_ok` | `tests/checker/test_checker_prop.py` |
| T18 | Run drift-check gate vs docs/drift_baseline.json | `src/golem/drift.py` | `check()` | `tests/drift/test_drift.py` |

---

## Final Task: Drift-Check Gate (T18)
- **Owner:** R3 + R4
- **File:** `src/golem/drift.py`
- **Action:** Run `check()` over the Phase 2 benchmark suite; compare to `docs/drift_baseline.json`; PENDING metrics do not fail; any REGRESSION fails the gate.
