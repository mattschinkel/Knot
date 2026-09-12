"""UNSAFE capability gate (Phase 11 T4)."""

from __future__ import annotations

from golem.concurrency import check_unsafe, needed_unsafe_caps
from golem.effects import Capability, CapabilitySet
from golem.parser import parse_expr
from golem.partial import evaluate
from golem.values import ErrorVal, IntVal


def test_needed_always_includes_unsafe():
    n = needed_unsafe_caps([])
    assert Capability.UNSAFE in n
    n2 = needed_unsafe_caps(["fs.write"])
    assert Capability.UNSAFE in n2
    assert Capability.FS_WRITE in n2


def test_check_unsafe_denied():
    err = check_unsafe([], CapabilitySet())
    assert err is not None and err.err.kind == "capability"


def test_eval_unsafe_denied():
    r = evaluate(parse_expr("UNSAFE[CAPS[],1]"), granted_caps=CapabilitySet())
    assert isinstance(r, ErrorVal)


def test_eval_unsafe_granted():
    r = evaluate(
        parse_expr("UNSAFE[CAPS[],ADD[2,3]]"),
        granted_caps=CapabilitySet([Capability.UNSAFE]),
    )
    assert isinstance(r, IntVal) and r.value == 5


def test_eval_unsafe_extra_cap():
    r = evaluate(
        parse_expr("UNSAFE[CAPS[fs.write],1]"),
        granted_caps=CapabilitySet([Capability.UNSAFE]),
    )
    assert isinstance(r, ErrorVal)
    r2 = evaluate(
        parse_expr("UNSAFE[CAPS[fs.write],1]"),
        granted_caps=CapabilitySet([Capability.UNSAFE, Capability.FS_WRITE]),
    )
    assert isinstance(r2, IntVal)
