# Phase 11 Tasks

| ID | Goal | File | Function/Class | Test |
|---|------|------|----------------|------|
| T1 | PAR/SEQ/REF/DEREF/UNSAFE parse | `ast.py` / `parser.py` | `ParExpr` | `tests/concurrency/test_parse_par.py` |
| T2 | eval_par / eval_seq | `concurrency.py` | `eval_par` | `tests/concurrency/test_par_seq.py` |
| T3 | RegionVal + REF/DEREF | `values.py` | `RegionVal` | `tests/concurrency/test_region.py` |
| T4 | UNSAFE caps | `concurrency.py` | `check_unsafe` | `tests/concurrency/test_unsafe.py` |
| T5 | subtype + drift phase 11 | `types.py` + baseline | `subtype` | `tests/concurrency/test_concurrency_prop.py` |
