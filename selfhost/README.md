# Self-host tree

Stage 0.5 language gaps are in `src/knot/runtime_ops.py`.
Stage 1 knotc sources live in `stage1/` (DEF/FN/MATCH/IF/CALL subset).
Harness (Stage 0 driver + Stage 2 gates) lives in `harness/`.

Stage 2: host-compiled knotc compiles `stage1/*.knot`; the resulting image
compiles fixtures (see `test_stage2.py`).

See `ai_docs/selfhost_plan.md`.
