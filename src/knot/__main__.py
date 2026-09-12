"""python -m knot  — CLI for MCP / kb / --llm (Phase 12). No HTTPS."""

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

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
