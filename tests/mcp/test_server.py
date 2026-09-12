"""MCP JSON-RPC server (Phase 12 T4)."""

from __future__ import annotations

import json

from knot.mcp.server import handle_line, handle_request


def test_tools_list():
    resp = handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert resp["id"] == 1
    tools = resp["result"]["tools"]
    assert any(t["name"] == "eval" for t in tools)


def test_tools_call_eval():
    resp = handle_request(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "eval", "arguments": {"source": "ADD[1,1]"}},
        }
    )
    assert resp["result"]["ok"] is True
    assert resp["result"]["result"] == 2


def test_handle_line():
    line = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "kb", "arguments": {"query": "ADD", "max_tokens": 100}},
        }
    )
    out = json.loads(handle_line(line))
    assert out["result"]["ok"] is True
    assert out["result"]["tokens"] <= 100


def test_unknown_method():
    resp = handle_request({"id": 9, "method": "nope"})
    assert "error" in resp
