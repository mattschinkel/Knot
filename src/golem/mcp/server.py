"""Minimal stdio / in-process MCP-style JSON tool server (no HTTPS)."""

from __future__ import annotations

import json
import sys
from typing import Any, TextIO

from .tools import call_tool, list_tools


def handle_request(req: dict) -> dict:
    """Handle one JSON-RPC-ish request.

    Supported methods:
      - tools/list
      - tools/call  params: {name, arguments}
      - initialize (ack)
    """
    rid = req.get("id")
    method = req.get("method") or req.get("methodName") or ""
    params = req.get("params") or {}

    def result(payload: Any) -> dict:
        return {"jsonrpc": "2.0", "id": rid, "result": payload}

    def error(code: int, message: str) -> dict:
        return {
            "jsonrpc": "2.0",
            "id": rid,
            "error": {"code": code, "message": message},
        }

    if method in ("initialize", "notifications/initialized"):
        return result(
            {
                "protocolVersion": "golem-mcp-1",
                "serverInfo": {"name": "golem", "version": "0.12"},
                "capabilities": {"tools": {}},
            }
        )
    if method in ("tools/list", "list_tools"):
        return result({"tools": list_tools()})
    if method in ("tools/call", "call_tool"):
        name = params.get("name") or params.get("tool")
        args = params.get("arguments") or params.get("args") or {}
        if not name:
            return error(-32602, "missing tool name")
        return result(call_tool(str(name), dict(args)))
    if method == "ping":
        return result({"pong": True})
    return error(-32601, "method not found: " + str(method))


def handle_line(line: str) -> str:
    line = line.strip()
    if not line:
        return ""
    try:
        req = json.loads(line)
    except json.JSONDecodeError as e:
        return json.dumps(
            {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "parse error: " + str(e)},
            }
        )
    if not isinstance(req, dict):
        return json.dumps(
            {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32600, "message": "request must be object"},
            }
        )
    return json.dumps(handle_request(req), default=str)


def serve_stdio(stdin: TextIO | None = None, stdout: TextIO | None = None) -> None:
    """Read JSON lines from stdin, write responses to stdout (no HTTPS)."""
    inp = stdin or sys.stdin
    out = stdout or sys.stdout
    for line in inp:
        resp = handle_line(line)
        if resp:
            out.write(resp + "\n")
            out.flush()
