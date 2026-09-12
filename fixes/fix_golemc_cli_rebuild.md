# fix: golemc CLI run/compile/rebuild + CALL_PROGRAM

## Problem
Daily golemc use still required knowing the host bootstrap image. Self-host
rebuild was only a Python Stage-2 gate, not a Golem-authored loop.

## Fix
- CLI: `golem run`, `golem compile` (`--root`), `golem rebuild`
- `main.gol`: `rebuild_golemc` / `rebuild_roundtrip`
- Native `CALL_PROGRAM[program,name,args]` to invoke a compiled Program image
- `golemc_bridge` helpers: `run_with_golemc`, `compile_root_with_golemc`, `rebuild_golemc`

## Notes
Push of earlier commit may need GitHub auth on this machine.
