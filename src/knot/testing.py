"""Inline tests, properties, and deterministic fuzz (Phase 7)."""

from __future__ import annotations

from dataclasses import dataclass

from .ast import (
    DefNode,
    FnExpr,
    IdentExpr,
    LitExpr,
    OpExpr,
    PropertyDecl,
    InlineTest,
)
from .edits import EditResult, apply_edit
from .partial import CompileStatus, compile_check, evaluate
from .values import BoolVal, ErrorVal, IntVal, StringVal, UnitVal, Value


@dataclass(frozen=True)
class CaseResult:
    ok: bool
    inp: object
    expected: Value | None
    got: Value | None
    note: str = ""


@dataclass(frozen=True)
class TestResult:
    name: str
    ok: bool
    cases: tuple[CaseResult, ...]


@dataclass(frozen=True)
class PropertyResult:
    name: str
    ok: bool
    samples_run: int
    failing_sample: dict | None = None
    note: str = ""


@dataclass(frozen=True)
class SuiteReport:
    ok: bool
    tests: tuple[TestResult, ...]
    properties: tuple[PropertyResult, ...]
    compile_status: CompileStatus | None = None


def defs_by_name(program: list | object) -> dict[str, DefNode]:
    items = program if isinstance(program, list) else [program]
    out: dict[str, DefNode] = {}
    for item in items:
        if isinstance(item, DefNode):
            out[str(item.name)] = item
    return out


def collect_tests(program: list | object) -> list[InlineTest]:
    items = program if isinstance(program, list) else [program]
    return [x for x in items if isinstance(x, InlineTest)]


def collect_properties(program: list | object) -> list[PropertyDecl]:
    items = program if isinstance(program, list) else [program]
    return [x for x in items if isinstance(x, PropertyDecl)]


def fuzz_samples(type_name: str | None, n: int = 8, seed: int = 0) -> list[Value]:
    """Deterministic value table for property fuzz (Phase 7 D3)."""
    t = (type_name or "i32").split("@")[0]
    if t in ("i32", "i64"):
        base = [0, 1, -1, 2, -2, 10, -10, 100, seed, -seed, 42, -42]
        return [IntVal(32 if t == "i32" else 64, int(v)) for v in base[:n]]
    if t == "bool":
        seq = [False, True] * max(1, n)
        return [BoolVal(seq[i]) for i in range(n)]
    if t == "string":
        base = ["", "a", "hi", "x" * (seed % 5), "knot"]
        while len(base) < n:
            base.append("s" + str(len(base) + seed))
        return [StringVal(base[i]) for i in range(n)]
    if t == "unit":
        return [UnitVal() for _ in range(n)]
    # default: i32
    return fuzz_samples("i32", n, seed)


def _values_equal(a: Value, b: Value) -> bool:
    if type(a) is not type(b):
        return False
    if isinstance(a, ErrorVal):
        return False
    if isinstance(a, IntVal):
        return a.value == b.value
    if isinstance(a, BoolVal):
        return a.value == b.value
    if isinstance(a, StringVal):
        return a.value == b.value
    if isinstance(a, UnitVal):
        return True
    return a == b


def run_test(program: list | object, test: InlineTest) -> TestResult:
    """Run TEST[name,CASE...] by calling DEF[name] with each CASE input."""
    defs = defs_by_name(program)
    results: list[CaseResult] = []
    for case in test.cases:
        call = OpExpr(test.name, [case.inp])
        got = evaluate(call, program=program, bindings=None)
        expected = evaluate(case.out, program=program)
        if isinstance(got, ErrorVal):
            results.append(
                CaseResult(False, case.inp, expected, got, note=got.err.message)
            )
            continue
        if isinstance(expected, ErrorVal):
            results.append(
                CaseResult(False, case.inp, expected, got, note="bad expected")
            )
            continue
        ok = _values_equal(got, expected)
        results.append(CaseResult(ok, case.inp, expected, got))
    return TestResult(
        name=test.name,
        ok=all(c.ok for c in results) and len(results) > 0,
        cases=tuple(results),
    )


def run_property(
    program: list | object,
    prop: PropertyDecl,
    *,
    n: int = 8,
    seed: int = 0,
) -> PropertyResult:
    """Fuzz property body with deterministic samples."""
    if not prop.params:
        got = evaluate(prop.body, program=program)
        ok = isinstance(got, BoolVal) and got.value is True
        return PropertyResult(prop.name, ok, 1, note="no params")

    # Cartesian product truncated to n samples along first param, others fixed seed tables
    tables = []
    for pname, ptype in prop.params:
        tables.append((str(pname), fuzz_samples(ptype, n=n, seed=seed)))

    # Use zip of tables (aligned samples) — n rows
    rows = n
    for i in range(rows):
        bindings = {}
        for pname, samples in tables:
            bindings[pname] = samples[i % len(samples)]
        got = evaluate(prop.body, program=program, bindings=bindings)
        if not (isinstance(got, BoolVal) and got.value is True):
            return PropertyResult(
                prop.name,
                False,
                i + 1,
                failing_sample={k: _val_repr(v) for k, v in bindings.items()},
                note="property failed",
            )
    return PropertyResult(prop.name, True, rows)


def _val_repr(v: Value) -> object:
    if isinstance(v, IntVal):
        return v.value
    if isinstance(v, BoolVal):
        return v.value
    if isinstance(v, StringVal):
        return v.value
    return str(v)


def run_suite(program: list | object, *, fuzz_n: int = 8, seed: int = 0) -> SuiteReport:
    """Run all TEST/PROPERTY decls; also compile_check DEFs briefly."""
    # Compile only expression defs for status — use first DEF body or whole program list status
    defs = list(defs_by_name(program).values())
    status = None
    if defs:
        # check last def body as a proxy; suite ok focuses on tests
        status = compile_check(defs[0].body).status
    tests = tuple(run_test(program, t) for t in collect_tests(program))
    props = tuple(
        run_property(program, p, n=fuzz_n, seed=seed)
        for p in collect_properties(program)
    )
    ok = all(t.ok for t in tests) and all(p.ok for p in props)
    if not tests and not props:
        ok = False
    return SuiteReport(ok=ok, tests=tests, properties=props, compile_status=status)


def verify_program(
    program: list | object,
    edit: object | None = None,
    *,
    fuzz_n: int = 8,
    seed: int = 0,
) -> tuple[object, SuiteReport, EditResult | None]:
    """Optionally apply_edit, then run_suite. Returns (program, suite, edit_result)."""
    edit_res = None
    prog = program
    if edit is not None:
        edit_res = apply_edit(program, edit)
        if not edit_res.ok:
            return program, SuiteReport(False, (), ()), edit_res
        prog = edit_res.root
    suite = run_suite(prog, fuzz_n=fuzz_n, seed=seed)
    return prog, suite, edit_res
