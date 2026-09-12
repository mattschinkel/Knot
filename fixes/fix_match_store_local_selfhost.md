# Fix: MATCH VM lowering re-evaluated scrutinee (exponential hang)

## Problem
Host VM `MatchExpr` lowering desugared to nested `IF[EQ[TAG[scr],…], …]` while
substituting `PAYLOAD[scr]` for bindings. Each use of `scr` re-compiled the full
scrutinee expression, so nested `MATCH` in Stage-1 `parse`/`codegen` became
exponential work and hung the VM (e.g. parsing `DEF[…,IF[…]]`).

Stage-1 `lex_number` also folded digits as `d*10+rest` once, so `122` became
`32` and self-compiled `is_alpha` rejected lowercase letters.

## Fix
1. Allocate a temp local, `STORE_LOCAL` the scrutinee once, then desugar arms
   against that local (`src/knot/vm/compiler.py`).
2. Short-circuit `AND`/`OR` via `IF` (parity with `evaluate`).
3. Pad `Frame.locals` to `FuncInfo.nlocals` for temps.
4. Stage-1 `codegen_match` likewise stores once before desugaring; harness
   derives `nlocals` from bytecode local indices.
5. Replace `"'"` in `lexer.knot` with `FROM_CODEPOINT[39]` so Stage-1 can
   re-lex its own sources (double-quote is not a Stage-1 token).
6. `lex_number` left-to-right accumulate: `acc*10+digit`.
