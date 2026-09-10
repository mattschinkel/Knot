# fix_crew_v6_restore_oneshot_sequential — stop stacking 4B damage

## Problem
Auto-retry re-ran the crew on already-corrupted files (duplicate classes,
`from frozenset import frozenset`, SyntaxError tests). R4 also had rewrite
tools and “fixed” impl by mangling it further. Phase 3 T1 burned hours in
restart cycles without healing.

## Fix (phase_crew v6 + autobuild)
1. **Restore last-green** — `snapshot_task_files` / `restore_task_files` before
   each inner round and each autobuild attempt; on final fail leave tree green.
2. **One-shot writes** — refuse `WriteModule` / `AddClass` / `AddFunction`
   replace when the module already parses and the symbol exists.
3. **Sequential narrow crews** — R2 implement-only (one tool), then R4
   verify-only (`AppendTests` + `RunPytest`, no src rewrite tools).
4. Skip R2 when the symbol is already present in a valid module (tests-only).

## Result
Retries no longer compound file damage; R4 cannot clobber src.
