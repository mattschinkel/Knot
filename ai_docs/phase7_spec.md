# Phase 7 Spec — Tests / Properties / Fuzz

> Owner: Cursor. Decisions follow `ai_docs/axiom_design.md` §8.  
> Status: DECIDED — implementing.

Phase 7 makes **inline tests and properties** first-class AIR. The compiler
treats them as verification obligations: run on demand and re-run after edits
(Phase 6 blast-radius report). Properties are also **deterministic fuzz**
targets (no RNG library — seeded sample tables).

---

## 1. Scope

### In Phase 7
- Canonical AIR (D-FB7 OP-only):
  - `TEST[name,CASE[in,out],...]`
  - `PROPERTY[name,[[x:T,...],body]]` — body must be BOOL
- `InlineTest` / `PropertyDecl` AST + parse + `print_canonical`
- `run_test` / `run_property` / `run_suite` against a program (list of DEF + tests)
- Deterministic fuzz samples per base type (`fuzz_samples`)
- Evaluate DEF/CALL enough to run examples (extend `evaluate` with program env)
- After `apply_edit`, optional `verify_program` reports test/property status

### Explicitly OUT of Phase 7
- Full VM / bytecode — Phase 9
- Modules / imports for test discovery — Phase 8
- Probabilistic / LLM-generated tests
- Parallel property search

---

## 2. Design decisions (DECIDED)

### D1 — Canonical forms
**DECISION:**  
`TEST[square,CASE[5,25]]`  
`PROPERTY[square_nonneg,[[x:i32],GE[square[x],0]]]`  
No brace/`forall` sugar in canonical (pretty may later).

### D2 — Function call in bodies
**DECISION:** `name[args]` parses as `OpExpr(op=name, children=args)` and evaluates as a call to `DEF[name,...]` in the program.

### D3 — Deterministic fuzz
**DECISION:** `fuzz_samples(type_name, n, seed=0)` returns a fixed table (i32/bool/string/unit). Same seed → same samples. Default n=8.

### D4 — Property success
**DECISION:** Property passes iff body evaluates to `BoolVal(True)` for every sample assignment (and type-checks as BOOL).

### D5 — Test success
**DECISION:** Case passes iff `evaluate(in)` then apply target DEF (if in is Call/Op to named fn) … Actually: for `TEST[fname,CASE[in,out]]`, evaluate `fname[in]` (wrap) or if `in` is already a call use it; compare to `evaluate(out)` by value equality.

Simpler rule: `CASE[in,out]` means evaluate `OpExpr(test.name, [in])` if in is not already calling test.name; else evaluate `in`; expect equal to `evaluate(out)`.

### D6 — Drift
**DECISION:** Phase bump to 7; M1–M4 unchanged.

---

## 3. File layout

```
src/knot/
  ast.py        # InlineTest, PropertyDecl
  parser.py     # TEST / PROPERTY
  canonical.py  # print
  testing.py    # run_test, run_property, run_suite, fuzz_samples, verify_program
  partial.py    # evaluate with program env
tests/testing/
  test_parse_test.py
  test_run_test.py
  test_property_fuzz.py
  test_verify_edit.py
  test_testing_prop.py
```

---

## 4. Definition of done

- [x] Spec decided
- [x] TEST/PROPERTY parse + canonical
- [x] run_test / run_property / fuzz_samples
- [x] verify_program (+ after edit)
- [x] Tests + drift phase 7

---

## 5. Tasks

| ID | Goal | File | Symbol | Test |
|----|------|------|--------|------|
| T1 | InlineTest/PropertyDecl + parse | ast/parser | `InlineTest` | `test_parse_test.py` |
| T2 | run_test + evaluate DEF/call | testing/partial | `run_test` | `test_run_test.py` |
| T3 | fuzz_samples + run_property | testing.py | `run_property` | `test_property_fuzz.py` |
| T4 | verify_program after edit | testing.py | `verify_program` | `test_verify_edit.py` |
| T5 | Props + drift phase 7 | docs | — | `test_testing_prop.py` |
