# Phase 0 Spec — Core Data Model (Knot kernel, Python host)

> Owner: R1 Architect (decides autonomously). Implementation: R2 Kernel
> Engineer. Verification: R4 Verifier. Human observes via the dashboard
> (non-blocking); R1 makes all decisions.
> Status: DECIDED by R1 (autonomous) — implemented; tests green.

Phase 0 builds the **deterministic kernel's data model** in Python: the
value representation, the type algebra, and the units/dimensions system.
Nothing here calls an LLM, parses text, or lowers code. It is the
foundation every later phase (parser, type checker, effects, lowering,
VM) is built on, so it must be small, total, and unambiguous.

Per the resolved decisions (`knot_agents.md` §5): host language is
**Python**; R1 decides autonomously; shell is autonomous (whitelisted
build/test); repo layout is `src/knot/`, `src/knot/ai/`, `tests/`, `cli/`,
`lsp/`, `fmt/`, `grammar/`, `vm/`, `docs/`.

## 1. Scope

### In Phase 0
- Value representation (`src/knot/values.py`)
- Type algebra (`src/knot/types.py`)
- Units / dimensions (`src/knot/units.py`)
- Structured error value (`src/knot/errors.py`) — minimal, just enough
  to type-check holes (VALID/PARTIAL/INVALID).
- Property tests for all of the above (`tests/`).

### Explicitly OUT of Phase 0
- Parser / AST nodes / canonical text (Phase 1)
- GBNF grammar (Phase 1)
- Effects, capabilities, contracts (Phase 2)
- Type *checker* (unification, inference) — Phase 0 defines the *types*
  and *values*; checking them against each other is Phase 2.
- Edit operations, modules, concurrency, lowering, VM, AI front-end.

## 2. Design decisions (DECIDED by R1)

These are the choices R1 has made. Each is reversible but locking them
now keeps Phase 1+ stable. Each decision is FINAL, recorded by R1.

- **D1 — Immutability.** Values and types are **frozen dataclasses**
  (hashable, equality by value). The graph is immutable; edits produce
  new nodes, never mutate in place. Rationale: stable node identity +
  cheap sharing + no aliasing bugs in the deterministic kernel.
- **D2 — Units as exponent maps.** A dimension is a `frozendict` of
  base-dimension → integer exponent, e.g. `meters^2 = {m: 2}`. Base
  dimensions are the 7 SI bases + user-defined ones (money, count, …).
  Multiplication adds exponents; division subtracts; addition requires
  equal dimension maps. This is the Cairn/Grafema pattern and is the
  simplest total algebra.
- **D3 — Holes are values, not a separate AST flag.** `Hole` is a value
  with an optional expected type (`?:T`). A `Hole` type-checks against
  *any* type as PARTIAL. This keeps the value/type model uniform and
  avoids a parallel "partial" representation.
- **D4 — Errors are values (errors-as-values).** A structured error is a
  value carrying `{node, op, expected, got, repair[]}`. The kernel
  *returns* errors, never raises, so partial programs stay composable.
  (Phase 0 defines the shape; the checker populates it in Phase 2.)
- **D5 — No numeric IDs in the model.** Node identity is a structural
  path + optional `@label` (§21). Phase 0 values carry no numeric id
  field; that's a compiler-internal concern added in Phase 1 when the
  AST exists.
- **D6 — `unit` vs `never`.** `unit` is the type with exactly one value
  (`()`); `never` is the bottom type with no values (unreachable). Both
  are first-class types, not sentinels.

## 3. Value representation (`src/knot/values.py`)

Every runtime value is an instance of a `Value` subclass. Values are
frozen and hashable.

```
Value (abstract)
├─ IntVal        (bits: 32|64, signed, value)
├─ FloatVal      (bits: 32|64, value)
├─ BoolVal
├─ StringVal
├─ BytesVal
├─ UnitVal       (the single () value)
├─ ListVal       (items: tuple[Value,...], elem_t: Type)
├─ SetVal        (items: frozenset[Value], elem_t: Type)
├─ MapVal        (items: frozendict[Value,Value], k_t, v_t)
├─ TupleVal      (items: tuple[Value,...], types: tuple[Type,...])
├─ SumVal        (tag: str, payload: Value, sum_t: SumType)
├─ RecordVal     (fields: frozendict[str,Value], rec_t: RecordType)
├─ HoleVal       (expected: Type | None)        # D3
└─ ErrorVal      (err: StructuredError)          # D4
```

Notes:
- `IntVal`/`FloatVal` keep the bit width so `2:i32` ≠ `2:i64` at the
  value level (they have different types; equality is type-aware).
- `HoleVal` with `expected=None` is the bare `?`; `expected=T` is `?:T`.
- `ErrorVal` is a value so a partial computation can *return* it and a
  later phase can decide whether to propagate or repair.

## 4. Type algebra (`src/knot/types.py`)

Types are frozen, hashable, and form a small algebraic DSL.

```
Type (abstract)
├─ BaseType        (name: "i32"|"i64"|"f32"|"f64"|"bool"|"string"
│                         |"bytes"|"unit"|"never")
├─ NominalType     (name: str, def: Type)        # type Distance = f64@meters
├─ OptionType      (inner: Type)                 # T?
├─ ListType        (elem: Type)                  # [T]
├─ SetType         (elem: Type)                  # {T}
├─ MapType         (key: Type, val: Type)         # K->V
├─ TupleType       (elems: tuple[Type,...])      # (T,U,V)
├─ SumType         (variants: frozendict[str, RecordType])  # T|U
├─ CapIntersect    (caps: tuple[Type,...])       # T&U (capability intersection)
├─ UnitType        (base: Type, dim: Dimension)   # T@dim   (D2)
└─ RegionType      (inner: Type, region: str)    # T<region R> (Phase 0: shape only)
```

Phase 0 delivers:
- `subtype(s, t) -> bool` — structural subtyping for the kernel types
  only (`never` <: everything, everything <: `unit` for unit-typed
  expressions, `T` <: `T?`, nominal <: its def). This is **not** full
  inference — just the base lattice the checker (Phase 2) builds on.
- `unify(a, b) -> Type | None` — a *stub* that returns `None` (cannot
  unify) except for the trivial reflexive case. Full unification is
  Phase 2; Phase 0 ships the hook so the value/type tests compile.

## 5. Units / dimensions (`src/knot/units.py`)

A `Dimension` is a `frozendict[str, int]` of base-dimension → exponent
(D2). Base dimensions: the 7 SI bases (`m`, `kg`, `s`, `A`, `K`, `mol`,
`cd`) plus user-named ones (`money`, `count`, …). The *name* of a base
dimension is opaque; only the exponent algebra matters.

```
Dimension
  mul(a, b)   -> Dimension      # add exponents
  div(a, b)   -> Dimension      # subtract exponents
  compatible(a, b) -> bool      # equal maps (for + / -)
  to_string(a) -> str           # "m^2", "m·s^-1", "1" (dimensionless)
```

Phase 0 delivers:
- The `Dimension` algebra (mul/div/compatible/to_string).
- `UnitType(base, dim)` from §4 wired so `meters * meters` produces
  `f64@{m:2}` and `meters + seconds` is a dimension-mismatch error
  (returned as an `ErrorVal`, not raised — D4).
- Property tests: mul/div exponent arithmetic, compatible checks,
  round-trip of `to_string`.

## 6. Errors (`src/knot/errors.py`)

Minimal structured error for Phase 0 (D4). Populated fully in Phase 2.

```
StructuredError
  node:   str | None        # structural path or @label (Phase 1 fills this)
  op:     str | None        # kernel op name, e.g. "ADD"
  expected: Type | None
  got:     Type | None
  repair: list[str] = []    # candidate repairs (filled by R3 in Phase 5)
  kind:   str               # "type" | "dim" | "arity" | "hole" | ...
```

`ErrorVal` wraps a `StructuredError`. The kernel returns `ErrorVal`
instead of raising. Phase 0 uses `kind="dim"` for unit mismatches and
`kind="hole"` when a hole blocks a deterministic result.

## 7. File layout (Phase 0)

```
src/knot/
  __init__.py
  values.py      # §3
  types.py       # §4
  units.py       # §5
  errors.py      # §6
tests/
  test_values.py
  test_types.py
  test_units.py
  test_errors.py
```

`src/knot/ai/` stays empty in Phase 0 (R3's domain, Phase 1+).

## 8. Definition of done (Phase 0)

- All four modules import with no side effects.
- `subtype` lattice passes property tests (never/unit/option/nominal).
- `Dimension` mul/div/compatible passes property tests.
- A `HoleVal` type-checks against any type as PARTIAL (no crash).
- Unit mismatch (`meters + seconds`) returns an `ErrorVal`, not an
  exception.
- No LLM, no parser, no I/O anywhere in `src/knot/`.
- R4's harness is green; R1 signs off (R1 decides D1–D6 autonomously).

## 9. Resolved sub-questions (DECIDED by R1)

- **Q1.** Do we want `i32`/`i64` to be distinct *types* (current plan)
  or a single `int` with a width attribute? Distinct types catch more
  bugs but bloat the type lattice. **DECISION: distinct types.**
- **Q2.** Should `string` be UTF-8 bytes or a first-class sequence of
  code points? Affects `len`/`AT` semantics. **DECISION: code points**
  (matches the §22.5 string-stdlib note); defer bytes to `bytes`.
- **Q3.** Is `RegionType` (lifetimes/regions) worth defining the
  *shape* of in Phase 0, or skip entirely until a phase needs it?
  **DECISION: shape only** (no checking), so later phases don't
  restructure the type algebra.
