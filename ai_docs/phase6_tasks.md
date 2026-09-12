# Phase 6 Tasks

| ID | Goal | File | Function/Class | Test |
|---|------|------|----------------|------|
| T1 | Structural path get/replace/delete/insert | `src/golem/edits.py` | `get_at` | `tests/edits/test_paths.py` |
| T2 | apply_edit REPLACE/DELETE/INSERT/RENAME | `src/golem/edits.py` | `apply_edit` | `tests/edits/test_apply.py` |
| T3 | REPLACE_MATCH with `_` wildcard | `src/golem/edits.py` | `replace_match` | `tests/edits/test_pattern.py` |
| T4 | blast_radius + revalidation EditResult | `src/golem/edits.py` | `EditResult` | `tests/edits/test_blast.py` |
| T5 | Props + drift baseline phase 6 | `docs/drift_baseline.json` | `check()` | `tests/edits/test_edits_prop.py` |
