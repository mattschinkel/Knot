# Phase 4 Tasks

| ID | Goal | File | Function/Class | Test |
|---|------|------|----------------|------|
| T1 | CompileStatus VALID/PARTIAL/INVALID + compile_check | `src/knot/partial.py` | `compile_check` | `tests/partial/test_status.py` |
| T2 | collect_holes → HoleReport | `src/knot/partial.py` | `collect_holes` | `tests/partial/test_holes_report.py` |
| T3 | suggest_candidates Env + defaults | `src/knot/partial.py` | `suggest_candidates` | `tests/partial/test_candidates.py` |
| T4 | Hole constraint propagation via expected= | `src/knot/checker.py` | `infer_type` | `tests/partial/test_propagate.py` |
| T5 | evaluate traps HoleExpr as ErrorVal | `src/knot/partial.py` | `evaluate` | `tests/partial/test_eval_trap.py` |
| T6 | Property tests no-raise + PARTIAL suite | `tests/partial/` | props | `tests/partial/test_partial_prop.py` |
| T7 | Drift M4 + baseline phase 4 | `docs/drift_baseline.json` | `check()` | `tests/drift/test_drift.py` |
