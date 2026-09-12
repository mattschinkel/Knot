"""check_guarantees on result type (Phase 3 T7)."""

from __future__ import annotations

from golem.contracts import Contract, check_guarantees
from golem.types import F64, I32, OptionType, STRING


def test_check_guarantees_empty():
    assert check_guarantees(Contract(), I32) is True


def test_check_guarantees_ok():
    c = Contract(guarantees={"result": F64})
    assert check_guarantees(c, F64) is True


def test_check_guarantees_mismatch():
    c = Contract(guarantees={"result": F64})
    assert check_guarantees(c, STRING) is False


def test_check_guarantees_subtype_ok():
    # I32 <: I32? via Option lift on the expected side is not automatic here;
    # exact unify / subtype(result, expected): I32 <: Option[I32] is True.
    c = Contract(guarantees={"result": OptionType(I32)})
    assert check_guarantees(c, I32) is True


def test_check_guarantees_multiple_same_result():
    c = Contract(guarantees={"result": F64, "out": F64})
    assert check_guarantees(c, F64) is True
    assert check_guarantees(c, I32) is False
