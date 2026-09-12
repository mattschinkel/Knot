# fix: finish compile-all — IMPORT link + caps + INVOKE stub

## Problem
Compile-all still needed in-Knot multi-file IMPORT linking. Nested DEF
evaluation dropped `granted_caps`, so `FS_READ` inside `compile_root` always
failed. INVOKE had no compile-time stub. Dashboard/docs still showed self-host
as incomplete.

## Fix
- `partial._call_def`: thread `granted_caps` into nested DEF evaluation.
- `main.knot`: `compile_root[dir,root]` expands IMPORT via `FS_READ` + merge.
- `codegen.knot`: INVOKE → `ERR_MAKE['invoke_host_only']` (host AI runtime).
- Fixtures `link_a.knot` / `link_root.knot`; gates in `test_compile_all_knot.py`.
- `knotc_bridge` uses `resolve_stage1_imports()`; dashboard/selfhost_plan/progress
  mark compile-all + IMPORT link done.

## Host-only (by design)
MCP, surgical edits, live MODEL/INVOKE tool execution remain Python.
