# Phase 5 Tasks

| ID | Goal | File | Function/Class | Test |
|---|------|------|----------------|------|
| T1 | ErrExpr AST node | `src/golem/ast.py` | `ErrExpr` | `tests/errors/test_err_parse.py` |
| T2 | Parse ERR[code,path,expected,actual,fixes*] | `src/golem/parser.py` | `parse_expr` | `tests/errors/test_err_parse.py` |
| T3 | print_canonical + normalize (D-FB11) | `src/golem/canonical.py` | `print_canonical` | `tests/errors/test_canonical.py` |
| T4 | Repair + suggest_repairs | `src/golem/repairs.py` | `suggest_repairs` | `tests/errors/test_repairs.py` |
| T5 | diagnose → ErrorVal with repairs | `src/golem/diagnose.py` | `diagnose` | `tests/errors/test_diagnose.py` |
| T6 | infer ErrExpr NEVER + validate_fix | `src/golem/checker.py` | `infer_type` | `tests/errors/test_err_infer.py` |
| T7 | Props + drift baseline phase 5 | `docs/drift_baseline.json` | `check()` | `tests/errors/test_errors_prop.py` |
