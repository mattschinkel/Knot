"""ModuleRegistry (Phase 8 T2)."""

from __future__ import annotations

from golem.modules import ModuleRegistry
from golem.parser import parse_expr


def test_register_and_get():
    reg = ModuleRegistry()
    m = parse_expr("MODULE[users,DEF[x,1],EXPORT[x]]")
    reg.register(m, version="1.0")
    assert "users" in reg
    got = reg.get("users")
    assert got is not None
    assert got.version == "1.0"
    assert got.exports == ["x"]


def test_register_overwrite():
    reg = ModuleRegistry()
    reg.register(parse_expr("MODULE[a,EXPORT[]]"), version="1")
    reg.register(parse_expr("MODULE[a,EXPORT[]]"), version="2")
    assert reg.get("a").version == "2"
