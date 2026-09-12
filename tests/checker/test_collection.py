"""check_collection for LEN AT APPEND CONCAT MAP FILTER (Phase 2 T15)."""

from __future__ import annotations

from golem.ast import OpExpr
from golem.checker import TypeErrorVal, check_collection, infer_type
from golem.types import BOOL, FnType, I32, ListType, STRING


def test_len_list():
    assert check_collection("LEN", ListType(I32)) is I32


def test_len_string():
    assert check_collection("LEN", STRING) is I32


def test_at_list():
    assert check_collection("AT", ListType(STRING), I32) is STRING


def test_append():
    lst = ListType(I32)
    assert check_collection("APPEND", lst, I32) is lst


def test_append_mismatch():
    err = check_collection("APPEND", ListType(I32), STRING)
    assert isinstance(err, TypeErrorVal)


def test_concat():
    lst = ListType(I32)
    assert check_collection("CONCAT", lst, ListType(I32)) is lst


def test_map():
    out = check_collection("MAP", ListType(I32), FnType((I32,), STRING))
    assert isinstance(out, ListType) and out.elem is STRING


def test_filter():
    lst = ListType(I32)
    assert check_collection("FILTER", lst, FnType((I32,), BOOL)) is lst


def test_infer_len_op():
    # LEN needs a typed collection value; bind via env is overkill — use typed list
    # through a Def would need list lit; call check via OpExpr with Ident after bind
    from golem.ast import IdentExpr
    from golem.env import Env
    env = Env()
    env.bind("xs", ListType(I32))
    assert infer_type(OpExpr("LEN", [IdentExpr("xs")]), env) is I32
