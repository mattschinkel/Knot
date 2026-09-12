"""Phase 12 properties."""

from __future__ import annotations

import json
import subprocess
import sys

from knot.kb import estimate_tokens, retrieve
from knot.mcp.tools import call_tool


def test_tools_never_raise():
    for name, args in (
        ("eval", {"source": "???"}),
        ("typecheck", {"source": "ADD[1,2]"}),
        ("run", {"source": "SUB[9,1]"}),
        ("doc_query", {"query": "holes", "max_tokens": 50}),
        ("query", {"source": "IF[true,1,0]", "kind": "op"}),
    ):
        r = call_tool(name, args)
        assert "ok" in r


def test_kb_budget_invariant():
    for budget in (10, 50, 200):
        r = retrieve("effects capabilities modules", max_tokens=budget)
        assert r.tokens <= budget


def test_cli_tool_subprocess():
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "knot",
            "tool",
            "eval",
            "--args",
            json.dumps({"source": "ADD[4,5]"}),
        ],
        capture_output=True,
        text=True,
        cwd="/home/matt/cursor/LLM_Language",
        env={**dict(**__import__("os").environ), "PYTHONPATH": "src"},
    )
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert data["ok"] and data["result"] == 9
    assert estimate_tokens(proc.stdout) > 0
