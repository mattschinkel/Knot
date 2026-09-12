"""ContractAnnotation and Contract (Phase 3 T5)."""

from __future__ import annotations

from golem.contracts import Contract, ContractAnnotation
from golem.types import F64, I32, STRING


def test_annotation_empty():
    a = ContractAnnotation()
    assert len(a) == 0
    assert not a


def test_annotation_bindings():
    a = ContractAnnotation({"x": F64, "y": I32})
    assert a.get("x") == F64
    assert "y" in a
    assert a.get("z") is None


def test_contract_defaults_empty():
    c = Contract()
    assert len(c.requires) == 0
    assert len(c.guarantees) == 0
    assert len(c.ensures) == 0


def test_contract_from_mappings():
    c = Contract(
        requires={"x": F64},
        guarantees={"result": F64},
        ensures={"x": F64},
    )
    assert c.requires.get("x") == F64
    assert c.guarantees.get("result") == F64
    assert c.ensures.get("x") == F64


def test_contract_equality():
    a = Contract(requires={"x": I32})
    b = Contract(requires={"x": I32})
    c = Contract(requires={"x": STRING})
    assert a == b
    assert a != c


def test_contract_frozen():
    c = Contract(requires={"x": I32})
    try:
        c.requires = ContractAnnotation()  # type: ignore[misc]
        assert False, "Contract should be frozen"
    except Exception:
        pass
