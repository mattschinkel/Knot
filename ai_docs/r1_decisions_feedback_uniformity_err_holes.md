# R1 decisions — uniformity / ERR / holes / canonical (2026-09-10)

Source: `ai_docs/feedback_syntax_uniformity_err_holes.md`
(follow-up to D-FB1–D-FB6). Decided via `ask_architect.py` (two clarify rounds).

| ID | Decision | Locked form |
|----|----------|-------------|
| D-FB7 | ACCEPT | Language invariant: every non-atomic construct is `OP[arguments...]`. Canonical COND/MATCH/LET/WITH are `COND[...]`, `MATCH[...]`, `LET[...]`, `WITH[...]` (not alternate surface syntax). |
| D-FB8 | AMEND | Keep **named** params: `FN[[x:i32], body]` (D-FB1). Require `ident:type` in param list; reject nameless `FN[i32, body]` / unbound `FN[[i32], …]`. Optional later: `FN[[x:i32], ret, body]` for explicit return annotation — **not** required yet. Type surface stays mechanical: `42:i32`, `10:f64@meters`, `?:i32`, `?:f64@meters`. |
| D-FB9 | ACCEPT (+ AMEND on fixes) | `ERR[code, path, expected, actual, fixes]` is a **first-class AST/value** in PROGRAM→PARSE→TYPE→EXECUTE→RESULT/ERR→LLM. Fix suggestions are `OP[...]` nodes (e.g. `REPLACE[...]`). Type-check validates fix compatibility in checker work; applying REPLACE is an **edit op (Phase 6)**, not silent compile-time rewrite. Wire ERR parse/print ASAP (already GBNF); full repair loop with Phase 5/6. |
| D-FB10 | ACCEPT | Hole **constraint propagation** is in scope for Phase 2 direction: e.g. `ADD[42:i32, ?]` → expected `?:i32`; function holes toward `?:FN[[i32], i32]`. Build on landed `infer_hole` label resolve. |
| D-FB11 | AMEND | `parse → normalize → print` yields **exactly one** canonical string. **No whitespace significance:** normalize to `ADD[1,2]` (no spaces). Pretty-printer may emit spaces/infix; canonical parser rejects infix and non-normalized spacing. |
| D-FB12 | ACCEPT | Bare identifiers stay atoms (`x`, `user`). **REJECT** `VAR[x]` in canonical. |

## Phase 2
**Do not pause.** Continue type checker. Prioritize: hole context propagation, ERR AST land, normalize/canonical printer path (D-FB11), then remaining infer tasks.

## Conflicts resolved
- First-pass D-FB8 that dropped param names (`FN[i32, MUL[x,x]]`) is **void** — clarified round rejected nameless FN.
- Human preferred spaced `ADD[1, 2]`; R1 locked **no spaces** in canonical for uniqueness (D-FB11 AMEND). Pretty view may space.
