# Phase 5 Spec — Structured Errors + Repairs

> Owner: Cursor. Decisions follow `ai_docs/golem_design.md` §7 and D-FB5 / D-FB9.  
> Status: DECIDED — implementing.

Phase 5 makes **errors first-class AIR values** the LLM can consume without prose:
`ERR[code, path, expected, actual, fix...]`. Applying REPLACE remains Phase 6;
this phase parses/prints ERR, generates deterministic repair candidates, and
bridges type-check failures to `ErrorVal` / `ErrExpr`.

---

## 1. Scope

### In Phase 5
- `ErrExpr` AST node matching D-FB9: `ERR[code, path, expected, actual, fixes*]`
- Parse + canonical print (no spaces) for ERR and general AST (`print_canonical`) — advances D-FB11
- `Repair` records + `suggest_repairs` (replace / convert / remove_op / hole)
- Enrich `StructuredError.repair` with machine-readable suggestions
- `diagnose(expr, env) -> Value`: on type failure returns `ErrorVal` with repairs; on success returns typed ok path via existing infer (or Unit for status-only)
- `infer_type(ErrExpr) -> NEVER`; validate fix shapes (REPLACE arity, etc.)
- `TypeErrorVal.to_error_val()` carries repairs when context available
- Wire `compile_check` INVALID reports to include `ErrorVal` diagnostics
- Property tests: never raise; ERR round-trip parse ↔ canonical print

### Explicitly OUT of Phase 5
- Applying REPLACE / graph rewrite — Phase 6
- LLM-generated free-form repairs (kernel stays deterministic)
- Full “likely_intent” NLP strings (optional stub field only)
- Bytecode / VM — Phase 9

---

## 2. Design decisions (DECIDED)

### D1 — ERR shape (D-FB9)
**DECISION:** Canonical form is  
`ERR[CODE,PATH,EXPECTED,ACTUAL,FIX...]` with **no spaces**.  
- `CODE` — ident (e.g. `TYPE_MISMATCH`)  
- `PATH` — `[seg,...]` where seg is ident or number (structural path; not authored node IDs)  
- `EXPECTED` / `ACTUAL` — type atoms (`i32`, `f64@meters`, `bool`, …)  
- `FIX` — `OP[...]` nodes (`REPLACE[pathOrHole, expr]`, `CONVERT[path, type]`, `REMOVE_OP`, `HOLE[type]`)

### D2 — Errors are values, never exceptions
**DECISION:** Diagnostics are `ErrorVal(StructuredError(...))` / `ErrExpr`. Kernel APIs do not raise for type/repair logic.

### D3 — Repairs are suggestions only
**DECISION:** Phase 5 generates and type-checks fix *shape* compatibility lightly (arity / known fix ops). Applying a fix is Phase 6 edit.

### D4 — Deterministic repair set
**DECISION:** For binary type mismatch: suggest `REPLACE` other operand with hole of expected type, `CONVERT` if numeric widen would help (i32↔i64 only listed as convert candidate, not auto-applied), `REMOVE_OP` when op is binary. Cap at 6.

### D5 — Canonical print path (D-FB11 start)
**DECISION:** `print_canonical(ast)` emits no whitespace inside forms. `normalize(src) = print_canonical(parse_expr(src))`. Pretty printer unchanged.

### D6 — Drift
**DECISION:** Phase 5 does not change M1–M4; baseline phase bump to 5 with same metrics. M5 still PENDING.

---

## 3. File layout

```
src/golem/
  ast.py          # + ErrExpr
  parser.py       # ERR[...] / path list
  canonical.py    # print_canonical + normalize
  repairs.py      # Repair, suggest_repairs, validate_fix
  errors.py       # StructuredError.repair enriched
  diagnose.py     # diagnose() bridge
  checker.py      # infer ErrExpr; optional repair attach
  printer.py      # pretty view for ErrExpr
tests/errors/
  test_err_parse.py
  test_canonical.py
  test_repairs.py
  test_diagnose.py
  test_err_infer.py
  test_errors_prop.py
```

---

## 4. Definition of done

- [x] Spec decided
- [x] ERR parse/print/canonical round-trip
- [x] Repair suggestions on type mismatch
- [x] diagnose → ErrorVal with repairs
- [x] ErrExpr infers as NEVER
- [x] Property tests + full pytest green
- [x] Drift baseline phase 5

---

## 5. Tasks

| ID | Goal | File | Symbol | Test |
|----|------|------|--------|------|
| T1 | ErrExpr AST | `ast.py` | `ErrExpr` | `test_err_parse.py` |
| T2 | Parse ERR + path | `parser.py` | `parse_expr` | `test_err_parse.py` |
| T3 | print_canonical + normalize | `canonical.py` | `print_canonical` | `test_canonical.py` |
| T4 | Repair + suggest_repairs | `repairs.py` | `suggest_repairs` | `test_repairs.py` |
| T5 | diagnose bridge | `diagnose.py` | `diagnose` | `test_diagnose.py` |
| T6 | infer ErrExpr + validate_fix | `checker`/`repairs` | `infer_type` | `test_err_infer.py` |
| T7 | Props + drift phase 5 | tests/docs | — | `test_errors_prop.py` / drift |
