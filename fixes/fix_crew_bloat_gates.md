# fix_crew_bloat_gates — reject recursive/filler LLM fragments before write

## Problem
On Phase 2 T2/T3 the 4B repeatedly:
1. Emitted huge tool-call JSON (recursive `type_path_type_path_…` APIs, piles of ordering dunders) → llama-server HTTP 500 / JSON parse errors before the harness size gate ran.
2. Overwrote a small correct `WriteModule` with a larger bloated wrong one (Env grew 644→2004 chars of dunders; bindings used `Value` instead of `Type`).
3. Appended tests importing invented names (`IntType`) that do not exist in the kernel.

Prompt-only "KEEP IT MINIMAL" was not enough — the model ignored it.

## Fix
In `phase_crew.py`, reject bad fragments *at the tool boundary* (proper gates, not task-specific patches):
- Lower WriteModule max to 1200 chars; AddClass/AddMethod/AppendTests similarly capped.
- `_check_fragment_bloat`: reject self-prefixed recursive names, too many defs, filler ordering/arithmetic dunders.
- Refuse WriteModule overwrite when an existing substantial module would be replaced by a differently sized blob (force AddClass/AddMethod/AddFunction).
- `_check_test_imports`: reject Capitalized imports not defined in `src/golem/*.py`.

Landed correct `Env` (bind/lookup + enter_scope/leave_scope over `Type`) + tests manually after T3 hard-stop.

## Result
Gates unit-checked; Env tests green. Autobuild resumes from T4 with the hardened harness.
