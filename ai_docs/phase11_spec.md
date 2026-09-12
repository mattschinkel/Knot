# Phase 11 Spec — Concurrency / Memory / Unsafe

> Owner: Cursor. Decisions follow `ai_docs/axiom_design.md` §12, §16 Phase 11.  
> Status: DECIDED — done.

Phase 11 adds **dataflow concurrency** (`PAR` / `SEQ`), **region-tagged
references** (`REF` / `DEREF`), and an **`UNSAFE` escape hatch** gated by
capabilities. User code never sees threads, locks, or malloc.

---

## 1. Scope

### In Phase 11
- Canonical AIR:
  - `PAR[e1,e2,...]` — independent branches; result is `Tuple` in arg order
  - `SEQ[e1,e2,...]` — left-to-right; result is last value (empty → unit)
  - `REF[region,expr]` / `DEREF[expr]`
  - `UNSAFE[CAPS[cap...],body]` — body runs only if caps granted
- AST: `ParExpr`, `SeqExpr`, `RefExpr`, `DerefExpr`, `UnsafeExpr`
- Value: `RegionVal { value, region }`
- `concurrency.py`: `eval_par` / `eval_seq` / `schedule_par` / `check_unsafe`
- Region subtyping: `RegionType[A,r] <: RegionType[B,r]` iff `A <: B`
- Capability `unsafe` added; UNSAFE always needs it plus listed CAPS
- Wire into `evaluate` + `infer_type`
- Drift phase bump to 11 (M1–M5 unchanged)

### Explicitly OUT of Phase 11
- Real OS threads (runtime may evaluate PAR sequentially; semantics = independence)
- Full borrow checker / move tracking
- Pretty `unsafe { }` sugar
- PAR opcodes in bytecode VM (evaluate path only for v1)

---

## 2. Design decisions (DECIDED)

### D1 — PAR is dataflow independence
**DECISION:** Children of PAR have no declared data deps. Result `TupleVal` in source order. `schedule_par` returns one concurrent group (all args). Evaluation may be sequential; order of results is fixed.

### D2 — SEQ
**DECISION:** Evaluate left-to-right; propagate first ErrorVal; return last success (or `UnitVal` if empty).

### D3 — REF / DEREF
**DECISION:** `REF[r,e]` → `RegionVal` typed `RegionType(inner,r)`. `DEREF` unwraps; non-region → ErrorVal(kind=region).

### D4 — UNSAFE
**DECISION:** `UNSAFE[CAPS[...],body]`. Needed caps = `{unsafe} ∪ CAPS`. Missing → ErrorVal(kind=capability). Body otherwise evaluates normally.

### D5 — Region subtype
**DECISION:** Same region name + covariant inner. No implicit unwrap to bare inner.

### D6 — Drift
**DECISION:** Phase 11 baseline; M1–M5 unchanged.

---

## 3. File layout

```
src/knot/
  concurrency.py
  ast.py            # ParExpr, SeqExpr, RefExpr, DerefExpr, UnsafeExpr
  values.py         # RegionVal
  effects.py        # Capability.UNSAFE
  types.py          # RegionType subtype
  parser.py / canonical.py / partial.py / checker.py
tests/concurrency/
  test_parse_par.py
  test_par_seq.py
  test_region.py
  test_unsafe.py
  test_concurrency_prop.py
```

---

## 4. Definition of done

- [x] Spec decided
- [x] Parse/canonical PAR/SEQ/REF/DEREF/UNSAFE
- [x] eval + schedule + region + unsafe caps
- [x] RegionType subtype
- [x] Tests + drift phase 11

---

## 5. Tasks

| ID | Goal | File | Symbol | Test |
|----|------|------|--------|------|
| T1 | AST + parse/canonical | ast/parser | ParExpr | test_parse_par.py |
| T2 | eval PAR/SEQ | concurrency.py | eval_par | test_par_seq.py |
| T3 | REF/DEREF + RegionVal | values/concurrency | RegionVal | test_region.py |
| T4 | UNSAFE + caps | concurrency.py | check_unsafe | test_unsafe.py |
| T5 | subtype + drift | types + baseline | subtype | test_concurrency_prop.py |
