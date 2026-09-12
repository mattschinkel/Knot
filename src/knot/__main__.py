"""python -m knot  — CLI for MCP / kb / --llm / knotc (Phase 12 + self-host). No HTTPS."""

from __future__ import annotations

import argparse
import json
import sys


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    p = argparse.ArgumentParser(prog="knot", description="Knot compiler agent tools")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("mcp", help="stdio JSON-RPC MCP tool server")
    sp.add_argument("--once", metavar="JSON", help="handle one request JSON and exit")

    kb = sub.add_parser("kb", help="token-budgeted doc retrieval")
    kb.add_argument("query")
    kb.add_argument("--budget", type=int, default=500)

    llm = sub.add_parser("llm", help="format output under token budget")
    llm.add_argument("--diagnostics", default="")
    llm.add_argument("--slices", default="")
    llm.add_argument("--status", default="")
    llm.add_argument("--budget", type=int, default=200)
    llm.add_argument(
        "--policy",
        default="balanced",
        choices=["diagnostics_first", "slices_first", "balanced", "minimal"],
    )

    tool = sub.add_parser("tool", help="call one MCP tool")
    tool.add_argument("name")
    tool.add_argument("--args", default="{}", help="JSON object of arguments")

    comp = sub.add_parser("compile", help="compile AIR with Stage-1 knotc (or host fallback)")
    comp.add_argument("file", help="path to .knot AIR source")
    comp.add_argument(
        "--host-fallback",
        action="store_true",
        help="on knotc error, fall back to host compile_program",
    )

    args = p.parse_args(argv)

    if args.cmd == "mcp":
        from knot.mcp.server import handle_line, serve_stdio

        if args.once:
            print(handle_line(args.once))
            return 0
        serve_stdio()
        return 0

    if args.cmd == "kb":
        from knot.kb import retrieve

        r = retrieve(args.query, args.budget)
        print(r.text)
        return 0

    if args.cmd == "llm":
        from knot.llm_out import format_for_llm

        print(
            format_for_llm(
                diagnostics=args.diagnostics,
                slices=args.slices,
                status=args.status,
                budget_tokens=args.budget,
                policy=args.policy,
            )
        )
        return 0

    if args.cmd == "tool":
        from knot.mcp.tools import call_tool

        try:
            payload = json.loads(args.args)
        except json.JSONDecodeError as e:
            print(json.dumps({"ok": False, "error": {"kind": "json", "message": str(e)}}))
            return 1
        print(json.dumps(call_tool(args.name, payload), default=str))
        return 0

    if args.cmd == "compile":
        from pathlib import Path

        from knot.knotc_bridge import compile_prefer_knotc, compile_with_knotc
        from knot.values import ErrorVal

        src = Path(args.file).read_text(encoding="utf-8")
        result = (
            compile_prefer_knotc(src) if args.host_fallback else compile_with_knotc(src)
        )
        if isinstance(result, ErrorVal):
            print(json.dumps({"ok": False, "error": str(result.err)}))
            return 1
        print(
            json.dumps(
                {
                    "ok": True,
                    "functions": sorted(result.functions.keys()),
                    "count": len(result.functions),
                }
            )
        )
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
