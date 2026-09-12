# Self-host plan (operational)

Pointer: design §22 in `golem_design.md`. This file tracks the Cursor bootstrap track.

## Stages

| Stage | Status | Location |
|-------|--------|----------|
| 0 Python host | DONE (§16) | `src/golem/` |
| 0.5 stdlib/runtime | DONE | `runtime_ops.py` + VM NATIVE |
| 1 golemc in Golem | DONE (deterministic surface) | `selfhost/stage1/` |
| 2 self-compile | DONE | `selfhost/harness/test_stage2.py` |
| Prefer golemc | DONE | `src/golem/golemc_bridge.py`, `python -m golem compile` |
| Compile-all AIR | DONE | Stage-1 + `tests/selfhost/test_compile_all_golem.py` |
| In-Golem IMPORT link | DONE | `compile_root[dir,root]` in `main.gol` |
| Stable CLI | DONE | `python -m golem run|compile|rebuild` |
| Rebuild loop (Golem) | DONE | `rebuild_roundtrip` + `CALL_PROGRAM` |

## Daily workflow

```bash
PYTHONPATH=src:. .venv/bin/python -m golem run FILE.gol
PYTHONPATH=src:. .venv/bin/python -m golem compile FILE.gol
PYTHONPATH=src:. .venv/bin/python -m golem compile --root selfhost/stage1
PYTHONPATH=src:. .venv/bin/python -m golem rebuild selfhost/stage1
```

After editing `stage1/*.gol`, run `golem rebuild` — Golem `rebuild_roundtrip` recompiles stage1 and probes the new image via `CALL_PROGRAM`.

## Stage 1 layout

```
selfhost/
  README.md
  stage1/
    root.gol          # IMPORT graph
    lexer.gol
    parser.gol
    ast.gol
    check.gol
    codegen.gol
    main.gol          # compile_source / compile_path / compile_root
  fixtures/
    square.gol
    fact.gol
    expr_muladd.gol
    link_a.gol / link_root.gol
  harness/
    compile_stage1.py
    test_stage1.py
    test_stage2.py
```

## Vertical slice (done)

1. Stage 0.5 green  
2. Stage-1 lexer/parser/codegen for full deterministic AIR  
3. Fixtures via interpretive + VM golemc  
4. Stage 2: host-compiled golemc compiles stage1; self-compiled image compiles fixtures  
5. `compile_root` links IMPORT modules with `FS_READ` (needs `fs.read` cap)  

## Host-only (by design)

| Concern | Where |
|---------|--------|
| MCP server / kb / --llm | `src/golem/mcp/`, Phase 12 |
| Live MODEL/TOOL/INVOKE execution | `ai_ffi.py` (golemc emits INVOKE → `invoke_host_only` error) |
| Surgical edits | `edits.py` |
| First golemc image bootstrap | Host `compile_program` of stage1 sources |

## Retirement

Python remains for the host-only table above. Deterministic AIR→VM prefers Stage-1 golemc (`compile_source` / `compile_root` / `golemc_bridge`).
