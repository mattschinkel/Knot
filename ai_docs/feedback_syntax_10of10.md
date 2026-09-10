# External syntax review — toward 10/10 for LLMs (author-forwarded 2026-09-09)

Source score for stated goal (LLM-native, not human-primary): **8.5/10**.
Target: **10/10**. Do not optimize canonical form for human readability.

## Strengths to keep / lean into
1. `OP[...]` as near-AST form — no precedence (ADD/MUL/IF as nodes).
2. Explicit ops (GET/SET/EQ/GE) — small primitive set.
3. Uniform nesting shape `OP[arg...]`.
4. Holes `?` / `?:T` as first-class (extend toward `?:f64@meters`, `?:FN[...]`).
5. Typed lits `42:i32` — make type grammar fully mechanical.
6. Architecture: program graph is truth; pretty view is for humans only.

## Decisions requested of R1 (decide ACCEPT/REJECT/AMEND)

### D-FB1 — Canonical form: one structural rule only
Everything is `NAME[ARGUMENTS]` (plus atoms). No dual sugar in canonical.
- FN becomes e.g. `FN[[x:i32], MUL[x, x]]` or `FN[x:i32, MUL[x, x]]` (pick one).
- Field access: canonical `GET[user, name]` only; `user.name` is pretty-only.
- No infix/`def`/assignment sugar in canonical.

### D-FB2 — One binding form
Eliminate `square = FN[...]`, `def square = FN[...]`. Canonical only:
`DEF[square, FN[...]]` or `LET[square, FN[...]]` (pick one; expression-tree consistent).

### D-FB3 — Units in type grammar
Standardize: `10:f64@meters` (not bare `10:meters` unless `meters` is a real type).
Type grammar must be mechanical for the LLM.

### D-FB4 — Holes as first-class
Holes are not just unfinished text — first-class search spaces:
`?`, `?:i32`, `?:f64@meters`, `?:FN[i32 -> i32]` (shape TBD under D-FB1).

### D-FB5 — Machine-oriented errors
Structured repairable errors in canonical form, e.g.
`ERR[TYPE_MISMATCH, ADD, 1, i32, string]` or richer `ERROR[...]` with
`path`, `expected`, `actual`, `fixes:[...]`. Optimize generate→check→repair loop.

### D-FB6 — Direction statement
Public thesis: Knot is for LLM generate/self-correct loops, not "easier for
LLMs to read human code." Canonical more rigid/redundant/structural;
pretty-printer owns human readability.

## Scorecard (reviewer)
AST/structural 10 | LLM gen 9 | parse 9.5 | unambiguity 9.5 | types 8 |
consistency 8 | error/recovery 7 | human read 4 | goal fit 8.5 → overall 8.5
