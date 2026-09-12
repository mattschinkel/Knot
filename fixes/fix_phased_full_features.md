# Fix / feature: phased full deterministic golemc + post-v1 polish

## Problem
Stage-2 self-host covered only a DEF/FN subset; post-v1 polish (pretty-view, PAR VM, borrow, live MODEL) was still open.

## Fix
- **A1:** holes/ERR/typed lits/floats/RECORD·GET flatten; `FLOAT_FROM_STRING`/`ERR_MAKE`/`UNIT` natives
- **A2:** IMPORT/MODULE/TEST/PROPERTY parse; `root.gol` import graph in harness
- **A3:** real `check.gol`; compile_source gates on check
- **A4:** expanded Stage-2 (fact round-trip, MATCH, hole, IMPORT)
- **B:** [`src/golem/golemc_bridge.py`](../src/golem/golemc_bridge.py) + `python -m golem compile`
- **C:** pretty MODULE/PAR/REF/UNSAFE/MATCH; VM `PAR`/`SEQ` opcodes; `borrow_check`; `make_openai_compatible_handler`
