# Self-host plan (operational)

Pointer: design §22 in `axiom_design.md`. This file tracks the Cursor bootstrap track.

## Stages

| Stage | Status | Location |
|-------|--------|----------|
| 0 Python host | DONE (§16) | `src/knot/` |
| 0.5 stdlib/runtime | DONE | `runtime_ops.py` + VM NATIVE |
| 1 knotc in Knot | DONE (deterministic surface) | `selfhost/stage1/` |
| 2 self-compile | DONE | `selfhost/harness/test_stage2.py` |
| Prefer knotc | DONE | `src/knot/knotc_bridge.py`, `python -m knot compile` |
| Compile-all AIR | DONE | Stage-1 + `tests/selfhost/test_compile_all_knot.py` |
| In-Knot IMPORT link | DONE | `compile_root[dir,root]` in `main.knot` |

## Stage 1 layout

```
selfhost/
  README.md
  stage1/
    root.knot          # IMPORT graph
    lexer.knot
    parser.knot
    ast.knot
    check.knot
    codegen.knot
    main.knot          # compile_source / compile_path / compile_root
  fixtures/
    square.knot
    fact.knot
    expr_muladd.knot
    link_a.knot / link_root.knot
  harness/
    compile_stage1.py
    test_stage1.py
    test_stage2.py
```

## Vertical slice (done)

1. Stage 0.5 green  
2. Stage-1 lexer/parser/codegen for full deterministic AIR  
3. Fixtures via interpretive + VM knotc  
4. Stage 2: host-compiled knotc compiles stage1; self-compiled image compiles fixtures  
5. `compile_root` links IMPORT modules with `FS_READ` (needs `fs.read` cap)  

## Host-only (by design)

| Concern | Where |
|---------|--------|
| MCP server / kb / --llm | `src/knot/mcp/`, Phase 12 |
| Live MODEL/TOOL/INVOKE execution | `ai_ffi.py` (knotc emits INVOKE → `invoke_host_only` error) |
| Surgical edits | `edits.py` |
| First knotc image bootstrap | Host `compile_program` of stage1 sources |

## Retirement

Python remains for the host-only table above. Deterministic AIR→VM prefers Stage-1 knotc (`compile_source` / `compile_root` / `knotc_bridge`).
