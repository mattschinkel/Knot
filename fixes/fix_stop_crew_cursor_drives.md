# fix: stop 4B crew; Cursor drives Golem

## Problem
The LocoOperator-4B crew (`autobuild.py` / `phase_crew.py`) could not reliably land Phase 3 tasks. Retries restored files but still inventing APIs and mangling tests (e.g. broken `contracts.py` + nonsensical `check_requires` arity). Auto-restart and crew v6 reduced damage but did not produce correct kernel code.

## Fix
Author direction (2026-09-11): stop using the crew for implementation. Cursor (this session) implements Golem directly against the phase specs and design doc. Local-only crew scripts remain gitignored for optional experiments; they are not the build path.

## Phase 3 (manual)
- Replaced mangled `contracts.py` with `ContractAnnotation` / `Contract` / `check_requires` / `check_guarantees`
- `FnType` optional `effects` + `caps`; `FnExpr` optional annotations; `infer_fn` attaches them
- `validate_call_effects` on call-site granted capabilities
- Property tests + drift baseline phase 3
- **414 tests pass**
