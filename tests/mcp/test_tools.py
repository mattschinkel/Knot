"""MCP tools (Phase 12 T1)."""

from __future__ import annotations

from knot.mcp.tools import call_tool, list_tools


def test_list_tools_has_core():
    names = {t["name"] for t in list_tools()}
    for n in ("eval", "typecheck", "run", "constrain", "doc_query", "query", "kb"):
        assert n in names


def test_eval_add():
    r = call_tool("eval", {"source": "ADD[2,3]"})
    assert r["ok"] is True
    assert r["result"] == 5


def test_typecheck_partial_hole():
    r = call_tool("typecheck", {"source": "ADD[1,?]"})
    assert r["ok"] is True
    assert r["status"] in ("partial", "valid", "invalid")
    assert r["holes"] >= 1


def test_run_vm():
    r = call_tool("run", {"source": "MUL[3,4]"})
    assert r["ok"] is True
    assert r["result"] == 12


def test_constrain_ok_and_fail():
    ok = call_tool("constrain", {"value": "hi", "out_type": "string"})
    assert ok["ok"] is True
    bad = call_tool("constrain", {"value": 1, "out_type": "string"})
    assert bad["ok"] is True
    assert isinstance(bad["result"], dict) and bad["result"].get("error")


def test_query_children():
    r = call_tool("query", {"source": "ADD[1,2]", "kind": "children"})
    assert r["ok"] and r["count"] == 2


def test_unknown_tool():
    r = call_tool("nope", {})
    assert r["ok"] is False
    assert r["error"]["kind"] == "unknown_tool"
