"""python -m golem  — CLI for MCP / kb / --llm / golemc (Phase 12 + self-host). No HTTPS."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    p = argparse.ArgumentParser(prog="golem", description="Golem compiler agent tools")
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

    comp = sub.add_parser("compile", help="compile AIR with Stage-1 golemc")
    comp.add_argument("file", nargs="?", help="path to .gol AIR source")
    comp.add_argument(
        "--root",
        metavar="DIR",
        help="compile IMPORT graph: DIR/root.gol via compile_root",
    )
    comp.add_argument(
        "--root-file",
        default="root.gol",
        help="root filename inside --root (default root.gol)",
    )
    comp.add_argument(
        "--host-fallback",
        action="store_true",
        help="on golemc error, fall back to host compile_program",
    )

    run_p = sub.add_parser("run", help="compile AIR with golemc and run entry")
    run_p.add_argument("file", help="path to .gol AIR source")
    run_p.add_argument("--entry", default="__main", help="function to call")
    run_p.add_argument(
        "--host-fallback",
        action="store_true",
        help="on golemc error, fall back to host compile_program",
    )

    reb = sub.add_parser(
        "rebuild",
        help="self-host rebuild: Golem rebuild_roundtrip on stage1",
    )
    reb.add_argument(
        "dir",
        nargs="?",
        default=None,
        help="stage1 directory (default: selfhost/stage1)",
    )
    reb.add_argument(
        "--probe",
        default="ADD[1,1]",
        help="AIR source the rebuilt golemc must compile",
    )

    args = p.parse_args(argv)

    if args.cmd == "mcp":
        from golem.mcp.server import handle_line, serve_stdio

        if args.once:
            print(handle_line(args.once))
            return 0
        serve_stdio()
        return 0

    if args.cmd == "kb":
        from golem.kb import retrieve

        print(retrieve(args.query, args.budget).text)
        return 0

    if args.cmd == "llm":
        from golem.llm_out import format_for_llm

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
        from golem.mcp.tools import call_tool

        try:
            payload = json.loads(args.args)
        except json.JSONDecodeError as e:
            print(json.dumps({"ok": False, "error": {"kind": "json", "message": str(e)}}))
            return 1
        print(json.dumps(call_tool(args.name, payload), default=str))
        return 0

    if args.cmd == "compile":
        from golem.golemc_bridge import (
            compile_path_with_golemc,
            compile_prefer_golemc,
            compile_root_with_golemc,
            compile_with_golemc,
        )
        from golem.values import ErrorVal

        if args.root:
            result = compile_root_with_golemc(args.root, args.root_file)
        elif args.file:
            src = Path(args.file).read_text(encoding="utf-8")
            result = (
                compile_prefer_golemc(src)
                if args.host_fallback
                else compile_with_golemc(src)
            )
        else:
            print(json.dumps({"ok": False, "error": "need file or --root DIR"}))
            return 1
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

    if args.cmd == "run":
        from golem.golemc_bridge import run_with_golemc
        from golem.values import ErrorVal

        src = Path(args.file).read_text(encoding="utf-8")
        out = run_with_golemc(src, entry=args.entry, host_fallback=args.host_fallback)
        if isinstance(out, ErrorVal):
            print(json.dumps({"ok": False, "error": str(out.err)}))
            return 1
        print(json.dumps({"ok": True, "value": repr(out)}))
        return 0

    if args.cmd == "rebuild":
        from golem.golemc_bridge import rebuild_golemc
        from golem.values import ErrorVal, SumVal

        result = rebuild_golemc(args.dir, probe=args.probe)
        if isinstance(result, ErrorVal):
            print(json.dumps({"ok": False, "error": str(result.err)}))
            return 1
        if isinstance(result, SumVal) and result.tag == "Err":
            print(json.dumps({"ok": False, "error": repr(result.payload)}))
            return 1
        if isinstance(result, SumVal) and result.tag == "Ok":
            prog = result.payload
            n = 0
            if isinstance(prog, SumVal) and prog.tag == "Program":
                from golem.values import ListVal

                if isinstance(prog.payload, ListVal):
                    n = len(prog.payload.items)
            print(json.dumps({"ok": True, "rebuilt": True, "probe_funcs": n}))
            return 0
        print(json.dumps({"ok": True, "result": repr(result)}))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
