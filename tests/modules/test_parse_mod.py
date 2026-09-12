"""MODULE/IMPORT/DEPENDS parse + canonical (Phase 8 T1)."""

from __future__ import annotations

from golem.ast import DependsDecl, ImportDecl, ModuleDecl
from golem.canonical import normalize, print_canonical
from golem.parser import parse_expr


def test_parse_module():
    n = parse_expr(
        "MODULE[users,DEF[create,FN[[n:string],n]],EXPORT[create]]"
    )
    assert isinstance(n, ModuleDecl)
    assert n.name == "users"
    assert n.exports == ["create"]
    assert len(n.body) == 1


def test_parse_import():
    n = parse_expr("IMPORT[users,create]")
    assert isinstance(n, ImportDecl)
    assert n.module == "users"
    assert n.names == ["create"]


def test_parse_depends_caps():
    n = parse_expr("DEPENDS[http,3.1,CAPS[net.request,fs.read]]")
    assert isinstance(n, DependsDecl)
    assert n.module == "http"
    assert n.version == "3.1"
    assert n.caps == ["net.request", "fs.read"]


def test_canonical_module():
    s = "MODULE[users,DEF[create,FN[[n:string],n]],EXPORT[create]]"
    assert normalize(
        "MODULE[ users , DEF[create,FN[[n:string],n]] , EXPORT[create] ]"
    ) == s
    assert print_canonical(parse_expr(s)) == s
