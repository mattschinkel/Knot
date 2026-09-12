# Self-host tree

Stage 0.5 language gaps are in `src/golem/runtime_ops.py`.
Stage 1 golemc sources live in `stage1/` (full deterministic AIR).
Harness (Stage 0 driver + Stage 2 gates) lives in `harness/`.

## Daily CLI (no HTTPS)

```bash
PYTHONPATH=src:. .venv/bin/python -m golem run path/to/file.gol
PYTHONPATH=src:. .venv/bin/python -m golem compile path/to/file.gol
PYTHONPATH=src:. .venv/bin/python -m golem compile --root selfhost/stage1
PYTHONPATH=src:. .venv/bin/python -m golem rebuild selfhost/stage1
```

- **run** — golemc compile + call `__main` (or `--entry`)
- **compile** — golemc only; `--root DIR` uses Golem `compile_root`
- **rebuild** — Golem `rebuild_roundtrip`: `compile_root` stage1, then `CALL_PROGRAM` the new image on a probe

Rebuild logic is in `stage1/main.gol` (`rebuild_golemc` / `rebuild_roundtrip`).

See `ai_docs/selfhost_plan.md`.
