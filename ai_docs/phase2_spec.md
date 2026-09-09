# Phase 2 Spec — Type Checker (Knot kernel, Python host)

> Owner: R1 Architect (decides autonomously). Implementation: R2 Kernel Engineer. Verification: R4 Verifier. Human observes via the dashboard (non-blocking); R1 makes all decisions.  
> Status: DECIDED by R1 (autonomous) — DRAFT for crew implementation; no checker yet.

Phase 2 builds the **type checker** for the Knot kernel. It introduces type rules for kernel operations, partial typing with holes, and structural type inference. The kernel operates on values and types defined in Phase 0; this phase adds the logic to infer and check types at runtime.

Per the resolved decisions (`knot_agents.md` §5): host language is **Python**; R1 decides autonomously; shell is autonomous (whitelisted build/test); repo layout is `src/knot/`, `src/knot/ai/`, `tests/`, `cli/`, `lsp/`, `fmt/`, `grammar/`, `vm/`, `docs/`.

## 1. Scope

### In Phase 2
- Type checker core logic (`src/knot/checker.py`)
- Type inference engine (unification, nominal type resolution)
- Holes and partial typing (`src/knot/holes.py`)
- Type rules for kernel operations (ADD, SUB, MUL, DIV, MOD, NEG, EQ, NE, LT, LE, GT, GE, AND, OR, NOT, IF, COND, MATCH, GET, SET, FIELD, MAP, FILTER, REDUCE, FOLD, LEN, AT, APPEND, CONCAT, LET, WITH, FN, CALL, HOLE)
- Type environment and scope management (`src/knot/env.py`)
- Property tests for type checker (`tests/checker/`)

### Explicitly OUT of Phase 2
- Effects, capabilities, contracts — Phase 3
- Structured errors and repairs — Phase 5
- Edit operations — Phase 6
- AI front-end / tool capabilities — Phase 10
- VM / IR / optimization — Phase 9
- Compiler as MCP server — Phase 12

## 2. Design decisions (DECIDED by R1)

These are the choices R1 has made. Each is reversible but locking them now keeps Phase 3+ stable. Each decision is FINAL, recorded by R1.

- **D1 — Structural subtyping with nominal types.** Types are compared by structural equivalence: `T <: U` iff `T` is a subtype of `U` under structural subtyping. Nominal types (e.g., `Distance = f64@meters`) are checked by name equality. Rationale: keeps the type lattice simple and predictable; avoids name-based aliasing bugs.
- **D2 — Holes are typed values.** `HoleVal` carries an optional expected type (`?:T`). A hole `?` is `?:Any`; `?:T` is a hole expecting type `T`. Holes are **not** erased; they remain in the type environment and are checked against expected types. Rationale: enables partial typing without breaking type safety; holes become candidates for type inference.
- **D3 — Type inference via unification.** The type checker uses a unification-based inference engine. It maintains a type environment (bindings from identifiers to types) and performs unification to infer types for expressions. Rationale: unification is the standard approach for ML-style type inference; it's total and deterministic.
- **D4 — No implicit casts.** All operations require explicit type annotations or are statically checked to ensure type safety. No implicit conversions (e.g., `i32` → `f64` is not allowed without a cast). Rationale: maintains referential transparency and avoids silent type mismatches.
- **D5 — Type environment is scoped.** The type environment is per-scope (block, function, module). Scopes are entered/leaving via `LET`, `FN`, `WITH`, `MATCH`. Rationale: supports nested bindings and avoids name collisions.
- **D6 — Kernel operations have fixed type rules.** Each operation (ADD, SUB, etc.) has a fixed type signature. For example: `ADD: (T, T) -> T` for numeric types; `EQ: (T, T) -> Bool`. Rationale: deterministic kernel; no overloading or implicit casting.
- **D7 — Nominal types are first-class.** Type definitions like `Distance = f64@meters` are stored as nominal types and can be referenced by name. Rationale: enables reusable, composable types; supports type aliases.
- **D8 — Region types are shape-only.** `T<region R>` is only used for shape (e.g., `List<region R>`) in Phase 0; Phase 2 does not yet check region constraints. Rationale: region constraints are added in Phase 3; Phase 2 keeps the model minimal.

## 3. Value representation (`src/knot/values.py`)

Phase 2 uses the value model from Phase 0. All values are frozen, hashable, and carry type information.

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
├─ HoleVal       (expected: Type | None)        # D2
└─ ErrorVal      (err: StructuredError)          # D4
```

Notes:
- `HoleVal` with `expected=None` is the bare `?`; `expected=T` is `?:T`.
- `ErrorVal` is a value so a partial computation can *return* it and a later phase can decide whether to propagate or repair.

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

Phase 2 delivers:
- `subtype(s, t) -> bool` — structural subtyping for the kernel types only (`never` <: everything, everything <: `unit` for unit-typed expressions, `T` <: `T?`, nominal <: its def). This is **not** full inference — just the base lattice the checker (Phase 2) builds on.
- `unify(a, b) -> Type | None` — a *stub* that returns `None` (cannot unify) except for the trivial reflexive case. Full unification is Phase 2; Phase 0 ships the hook so the value/type tests compile.

## 5. Units / dimensions (`src/knot/units.py`)

A `Dimension` is a `frozendict` of base-dimension → integer exponent, e.g., `meters^2 = {m: 2}`. Base dimensions are the 7 SI bases + user-defined ones (money, count, …). Multiplication adds exponents; division subtracts; addition requires equal dimension maps.

- `unit` is the type with exactly one value (`()`); `never` is the bottom type with no values (unreachable).
- Units are tracked at the type level; e.g., `f64@meters` and `f64@seconds` are distinct types.

## 6. Type checker core (`src/knot/checker.py`)

The type checker is a monolithic module with the following components:

### 6.1 Type environment (`Env`)
- `Env = dict[str, Type]` — bindings from identifiers to types
- Supports scope management: `enter_scope(name: str)`, `leave_scope()`
- Tracks type variables (e.g., `T1, T2`) during inference

### 6.2 Type inference engine
- `infer_type(expr: Value, ctx: Env) -> Type`
- Uses unification to infer types for expressions
- Supports:
  - `LET x = e1 IN e2` — binds `x` to inferred type
  - `FN x:T -> e` — function type inference
  - `CALL f(e1, ..., en)` — type checking function application
  - `HOLE` — returns `HoleVal(expected=None)` or `HoleVal(expected=T)`
  - `MATCH e WITH { ... }` — pattern matching with type constraints

### 6.3 Type rules for kernel operations

| Operation | Type Rule |
|-----------|-----------|
| `ADD` | `(T, T) -> T` where `T` is numeric |
| `SUB` | `(T, T) -> T` where `T` is numeric |
| `MUL` | `(T, T) -> T` where `T` is numeric |
| `DIV` | `(T, T) -> T` where `T` is numeric |
| `MOD` | `(T, T) -> T` where `T` is numeric |
| `NEG` | `T -> T` where `T` is numeric |
| `EQ` | `(T, T) -> Bool` |
| `NE` | `(T, T) -> Bool` |
| `LT` | `(T, T) -> Bool` |
| `LE` | `(T, T) -> Bool` |
| `GT` | `(T, T) -> Bool` |
| `GE` | `(T, T) -> Bool` |
| `AND` | `(Bool, Bool) -> Bool` |
| `OR` | `(Bool, Bool) -> Bool` |
| `NOT` | `Bool -> Bool` |
| `IF` | `(Bool, T, T) -> T` |
| `COND` | `(Bool, T, T) -> T` |
| `MATCH` | `(T, { ... }) -> U` where `U` is inferred from patterns |
| `GET` | `GET[T, K] -> V` where `T` is a record or tuple |
| `SET` | `SET[T, K, V] -> T` |
| `FIELD` | `FIELD[T, K] -> V` |
| `MAP` | `MAP[K->V, T] -> K->V` |
| `FILTER` | `FILTER[T, K->Bool] -> T` |
| `REDUCE` | `REDUCE[T, U, B] -> T` |
| `FOLD` | `FOLD[T, U, B] -> T` |
| `LEN` | `LEN[T] -> i32` |
| `AT` | `AT[T] -> V` |
| `APPEND` | `[T] -> [T]` |
| `CONCAT` | `[T] -> [T]` |
| `LET` | `LET x:T = e IN e2` — binds `x` to inferred type |
| `WITH` | `WITH x:T = e IN e2` — binds `x` to inferred type |
| `FN` | `FN x:T -> e` — function type inference |
| `CALL` | `CALL f(e1, ..., en)` — checks function application |
| `HOLE` | `HOLE -> HoleVal(expected=None)` |

### 6.4 Unification-based inference

- `unify(a: Type, b: Type) -> Type | None`
- Returns `None` if types are not unifiable
- Returns a new type if types are unified (e.g., `T1 = T2` → `T1`)
- Used in:
  - `infer_type(expr, env)`
  - `check_binary_op(op, t1, t2)`
  - `check_unary_op(op, t)`

### 6.5 Type checking functions

- `check_expr(e: Value, ctx: Env) -> Type`
- `check_binary_op(op: str, t1: Type, t2: Type) -> Type`
- `check_unary_op(op: str, t: Type) -> Type`
- `check_call(f: Value, args: tuple[Value], ctx: Env) -> Type`
- `check_match(e: Value, patterns: dict[str, Value], ctx: Env) -> Type`

## 7. File layout

```
src/knot/
├── checker/
│   ├── __init__.py
│   ├── checker.py        # Type checker core
│   ├── env.py            # Type environment and scope management
│   ├── holes.py          # Hole handling and partial typing
│   └── types.py          # Type algebra (reused from Phase 0)
├── tests/
│   └── checker/
│       ├── __init__.py
│       ├── test_checker.py
│       └── test_holes.py
└── grammar/
    └── grammar.gbnf      # GBNF grammar for canonical text (Phase 1)
```

## 8. Definition of done

- Type checker passes all unit and integration tests (`tests/checker/`)
- All kernel operations have type rules implemented
- Holes are handled with expected type inference
- Property tests show 100% coverage of type inference paths
- No type errors in Phase 0 value model (no regressions)

## 9. Resolved sub-questions (DECIDED by R1)

- **Q1 — Should holes be erased during type inference?**  
  DECISION: No. Holes are **not** erased; they remain in the type environment and are checked against expected types. This enables partial typing without breaking type safety.

- **Q2 — Should type inference use Hindley-Milner?**  
  DECISION: No. Use **unification-based inference** with a simple type environment. Hindley-Milner is overkill and introduces non-determinism; unification is deterministic and total.

- **Q3 — Should region types be checked in Phase 2?**  
  DECISION: No. Region types are only used for shape (`List<region R>`) in Phase 0; Phase 2 does not check region constraints. Region constraints are added in Phase 3.

- **Q4 — Should nominal types be checked by name or by definition?**  
  DECISION: By **name**. Nominal types are checked by name equality; e.g., `Distance = f64@meters` is checked against `Distance` by name. This keeps the type lattice simple and predictable.

- **Q5 — Should type errors raise exceptions?**  
  DECISION: No. Type errors are **structured errors** (ErrorVal) that are returned as values. The kernel *returns* errors, never raises, so partial programs stay composable.

- **Q6 — Should numeric types be checked for overflow?**