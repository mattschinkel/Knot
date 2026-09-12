"""DEPENDS + CAPS (Phase 8 T4)."""

from __future__ import annotations

from golem.effects import Capability, CapabilitySet
from golem.modules import ModuleRegistry, check_depends, link_program
from golem.parser import parse_expr
from golem.values import ErrorVal


def test_depends_version_mismatch():
    reg = ModuleRegistry()
    reg.register(parse_expr("MODULE[http,EXPORT[]]"), version="3.0")
    err = check_depends(
        [parse_expr("DEPENDS[http,3.1]")],
        reg,
    )
    assert isinstance(err, ErrorVal)


def test_depends_caps_required():
    reg = ModuleRegistry()
    reg.register(parse_expr("MODULE[http,EXPORT[]]"), version="3.1")
    dep = parse_expr("DEPENDS[http,3.1,CAPS[net.request]]")
    assert isinstance(
        check_depends([dep], reg, CapabilitySet()),
        ErrorVal,
    )
    assert (
        check_depends(
            [dep],
            reg,
            CapabilitySet([Capability.NET_REQUEST]),
        )
        is None
    )


def test_link_enforces_depends():
    reg = ModuleRegistry()
    reg.register(parse_expr("MODULE[http,EXPORT[]]"), version="3.1")
    prog = [parse_expr("DEPENDS[http,3.1,CAPS[net.request]]")]
    out = link_program(prog, reg, CapabilitySet())
    assert isinstance(out, ErrorVal)
    out2 = link_program(
        prog, reg, CapabilitySet([Capability.NET_REQUEST])
    )
    assert not isinstance(out2, ErrorVal)
