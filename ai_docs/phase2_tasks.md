# Phase 2 Tasks (drafted by R1)

```markdown
# Phase 2 Tasks Checklist

## Overview
- **Phase**: Type Checker (Knot kernel, Python host)
- **Owner**: R1 Architect (autonomous)
- **Implementation**: R2 Kernel Engineer
- **Verification**: R4 Verifier
- **Status**: DECIDED by R1

## Task Dependencies
Tasks are ordered by dependency. The **LAST task** is the **drift-check phase gate**, owned by R3+R4.

---

## T1: Define Type Algebra Interface
**Goal**: Define `src/knot/types.py` with `Type` hierarchy and `subtype`, `unify` stubs  
**File**: `src/knot/types.py`  
**Test**: `tests/checker/test_types.py` passes with `subtype` and `unify` stubs  
**Done**: `subtype(s, t) -> bool` and `unify(a, b) -> Type | None` exist

---

## T2: Implement BaseType and NominalType
**Goal**: Implement `BaseType` and `NominalType` classes with `__hash__`, `__eq__`  
**File**: `src/knot/types.py`  
**Test**: `tests/checker/test_types.py` passes `BaseType` and `NominalType` equality tests  
**Done**: `BaseType(name)` and `NominalType(name, def)` work with hash/equal

---

## T3: Implement OptionType, ListType, SetType
**Goal**: Add `OptionType`, `ListType`, `SetType` with `__hash__`, `__eq__`  
**File**: `src/knot/types.py`  
**Test**: `tests/checker/test_types.py` passes `OptionType`, `ListType`, `SetType` tests  
**Done**: `T?`, `[T]`, `{T}` work with hash/equal

---

## T4: Implement TupleType and SumType
**Goal**: Add `TupleType`, `SumType` with `__hash__`, `__eq__`  
**File**: `src/knot/types.py`  
**Test**: `tests/checker/test_types.py` passes `TupleType`, `SumType` tests  
**Done**: `(T,U)`, `T|U` work with hash/equal

---

## T5: Implement CapIntersect and UnitType
**Goal**: Add `CapIntersect`, `UnitType` with `__hash__`, `__eq__`  
**File**: `src/knot/types.py`  
**Test**: `tests/checker/test_types.py` passes `CapIntersect`, `UnitType` tests  
**Done**: `T&U`, `T@dim` work with hash/equal

---

## T6: Implement RegionType (shape-only)
**Goal**: Add `RegionType` with `__hash__`, `__eq__`  
**File**: `src/knot/types.py`  
**Test**: `tests/checker/test_types.py` passes `RegionType` tests  
**Done**: `T<region R>` works with hash/equal

---

## T7: Implement subtype() for Type Lattice
**Goal**: Implement `subtype(s, t) -> bool` for kernel types  
**File**: `src/knot/types.py`  
**Test**: `tests/checker/test_subtype.py` passes all tests  
**Done**: `never <: *`, `* <: unit`, `T <: T?`, nominal <: def

---

## T8: Implement unify() stub
**Goal**: Implement `unify(a: Type, b: Type) -> Type | None` stub  
**File**: `src/knot/types.py`  
**Test**: `tests/checker/test_unify.py` passes stub tests  
**Done**: `unify` returns `None` for non-unifiable, `T` for unified

---

## T9: Define Type Environment (Env)
**Goal**: Define `Env = dict[str, Type]` with scope management  
**File**: `src/knot/env.py`  
**Test**: `tests/checker/test_env.py` passes `enter_scope`, `leave_scope`  
**Done**: `Env` supports scope entry/exit and type variable tracking

---

## T10: Implement infer_type() stub
**Goal**: Implement `infer_type(expr: Value, ctx: Env) -> Type` stub  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_infer_type.py` passes stub  
**Done**: `infer_type` returns `Type` for expressions

---

## T11: Implement LET binding in type checker
**Goal**: Implement `LET x = e1 IN e2` type inference  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_let.py` passes LET binding  
**Done**: `LET x = e1 IN e2` binds `x` to inferred type

---

## T12: Implement FN function type inference
**Goal**: Implement `FN x:T -> e` type inference  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_fn.py` passes FN inference  
**Done**: `FN x:T -> e` infers function type

---

## T13: Implement HOLE handling
**Goal**: Implement `HOLE -> HoleVal(expected=None)` or `HoleVal(expected=T)`  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_hole.py` passes HOLE handling  
**Done**: `HOLE` returns `HoleVal(expected=None)` or `HoleVal(expected=T)`

---

## T14: Implement check_binary_op() stub
**Goal**: Implement `check_binary_op(op: str, t1: Type, t2: Type) -> Type`  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_binary_ops.py` passes ADD, SUB, MUL, DIV, MOD  
**Done**: `ADD`, `SUB`, `MUL`, `DIV`, `MOD` return `T` for numeric types

---

## T15: Implement check_unary_op() stub
**Goal**: Implement `check_unary_op(op: str, t: Type) -> Type`  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_unary_ops.py` passes NEG, EQ, NE, LT, LE, GT, GE, AND, OR, NOT  
**Done**: `NEG`, `EQ`, `NE`, `LT`, `LE`, `GT`, `GE`, `AND`, `OR`, `NOT` return correct types

---

## T16: Implement check_call() stub
**Goal**: Implement `check_call(f: Value, args: tuple[Value], ctx: Env) -> Type`  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_call.py` passes FN, CALL  
**Done**: `CALL f(e1, ..., en)` checks function application

---

## T17: Implement check_match() stub
**Goal**: Implement `check_match(e: Value, patterns: dict[str, Value], ctx: Env) -> Type`  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_match.py` passes MATCH  
**Done**: `MATCH e WITH { ... }` infers type from patterns

---

## T18: Implement GET operation type checking
**Goal**: Implement `GET[T, K] -> V` for record/tuple  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_get.py` passes GET  
**Done**: `GET` returns `V` from record or tuple

---

## T19: Implement SET operation type checking
**Goal**: Implement `SET[T, K, V] -> T`  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_set.py` passes SET  
**Done**: `SET` returns updated `T`

---

## T20: Implement FIELD operation type checking
**Goal**: Implement `FIELD[T, K] -> V`  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_field.py` passes FIELD  
**Done**: `FIELD` returns `V` from record

---

## T21: Implement MAP operation type checking
**Goal**: Implement `MAP[K->V, T] -> K->V`  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_map.py` passes MAP  
**Done**: `MAP` returns `K->V` from `T`

---

## T22: Implement FILTER operation type checking
**Goal**: Implement `FILTER[T, K->Bool] -> T`  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_filter.py` passes FILTER  
**Done**: `FILTER` returns `T` from `T`

---

## T23: Implement REDUCE operation type checking
**Goal**: Implement `REDUCE[T, U, B] -> T`  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_reduce.py` passes REDUCE  
**Done**: `REDUCE` returns `T` from `T`

---

## T24: Implement FOLD operation type checking
**Goal**: Implement `FOLD[T, U, B] -> T`  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_fold.py` passes FOLD  
**Done**: `FOLD` returns `T` from `T`

---

## T25: Implement LEN operation type checking
**Goal**: Implement `LEN[T] -> i32`  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_len.py` passes LEN  
**Done**: `LEN` returns `i32`

---

## T26: Implement AT operation type checking
**Goal**: Implement `AT[T] -> V`  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_at.py` passes AT  
**Done**: `AT` returns `V` from `T`

---

## T27: Implement APPEND operation type checking
**Goal**: Implement `[T] -> [T]`  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_append.py` passes APPEND  
**Done**: `APPEND` returns `[T]`

---

## T28: Implement CONCAT operation type checking
**Goal**: Implement `[T] -> [T]`  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_concat.py` passes CONCAT  
**Done**: `CONCAT` returns `[T]`

---

## T29: Implement WITH binding in type checker
**Goal**: Implement `WITH x:T = e IN e2` binding  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_with.py` passes WITH  
**Done**: `WITH` binds to inferred type

---

## T30: Implement check_expr() stub
**Goal**: Implement `check_expr(e: Value, ctx: Env) -> Type`  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_check_expr.py` passes check_expr  
**Done**: `check_expr` handles all expression types

---

## T31: Implement holes.py: HoleVal and partial typing
**Goal**: Implement `HoleVal(expected: Type | None)` and partial typing  
**File**: `src/knot/holes.py`  
**Test**: `tests/checker/test_holes.py` passes all tests  
**Done**: `HoleVal` with `expected=None` or `T` works

---

## T32: Implement unify() full unification engine
**Goal**: Implement `unify(a: Type, b: Type) -> Type | None` with full unification  
**File**: `src/knot/types.py`  
**Test**: `tests/checker/test_unify.py` passes full unification  
**Done**: `unify` handles `T1 = T2` → `T1`, `T1 = T2 = T3` → `T1`, etc.

---

## T33: Implement check_expr() with full type checking
**Goal**: Implement `check_expr()` that calls all sub-rules  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_check_expr.py` passes full check_expr  
**Done**: `check_expr` handles all operations

---

## T34: Implement checker.py: full checker module
**Goal**: Integrate all components into `checker.py`  
**File**: `src/knot/checker.py`  
**Test**: `tests/checker/test_checker.py` passes all tests  
**Done**: All kernel operations have type rules

---

## T35: Run drift-check phase gate
**Goal**: Run `src/knot/drift.py:check()` over benchmark suite, compare to `docs/drift_baseline.json`, flag regressions  
**File**: `src/knot/drift.py`  
**Test**: `tools/spec_lint.py` passes; `drift-check` passes; no regressions  
**Done**: Phase closes only if drift gate passes and spec_lint passes

---

## Final Output
**File**: `ai_docs/phase2_tasks.md`  
**Content**: The full markdown checklist above
```