# Phase 5 Tasks

| ID | Goal | File | Function/Class | Test |
|---|------|------|----------------|------|
| T1 | ErrExpr AST node | `src/knot/ast.py` | `ErrExpr` | `tests/errors/test_err_parse.py` |
| T2 | Parse ERR[code,path,expected,actual,fixes*] | `src/knot/parser.py` | `parse_expr` | `tests/errors/test_err_parse.py` |
| T3 | print_canonical + normalize (D-FB11) | `src/knot/canonical.py` | `print_canonical` | `tests/errors/test_canonical.py` |
| T4 | Repair + suggest_repairs | `src/knot/repairs.py` | `suggest_repairs` | `tests/errors/test_repairs.py` |
| T5 | diagnose → ErrorVal with repairs | `src/knot/diagnose.py` | `diagnose` | `tests/errors/test_diagnose.py` |
| T6 | infer ErrExpr NEVER + validate_fix | `src/knot/checker.py` | `infer_type` | `tests/errors/test_err_infer.py` |
| T7 | Props + drift baseline phase 5 | `docs/drift_baseline.json` | `check()` | `tests/errors/test_errors_prop.py` |
