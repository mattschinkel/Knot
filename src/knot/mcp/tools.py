"""MCP tool handlers for the Knot compiler (Phase 12)."""

from __future__ import annotations

from typing import Any, Callable

from knot.ai_ffi import constrain, type_from_air
from knot.canonical import print_canonical
from knot.edits import get_at
from knot.kb import retrieve as kb_retrieve
from knot.llm_out import format_for_llm
from knot.parser import ParseError, parse_expr, parse_program
from knot.partial import CompileStatus, compile_check, evaluate
from knot.values import ErrorVal, IntVal, StringVal, Value
from knot.vm import run as vm_run


def _ok(**kwargs: Any) -> dict:
    out = {"ok": True}
    out.update(kwargs)
    return out


def _err(kind: str, message: str, **extra: Any) -> dict:
    err = {"kind": kind, "message": message}
    err.update(extra)
    return {"ok": False, "error": err}


def _value_repr(v: Value) -> Any:
    if isinstance(v, ErrorVal):
        return {
            "error": True,
            "kind": v.err.kind,
            "message": v.err.message,
            "op": v.err.op,
        }
    if hasattr(v, "value") and not hasattr(v, "items"):
        return getattr(v, "value")
    return repr(v)


def tool_eval(args: dict) -> dict:
    src = args.get("source") or args.get("expr") or ""
    try:
        node = parse_expr(str(src))
    except ParseError as e:
        return _err("parse", str(e))
    val = evaluate(node)
    return _ok(result=_value_repr(val), canonical=print_canonical(node))


def tool_typecheck(args: dict) -> dict:
    src = args.get("source") or args.get("expr") or ""
    try:
        node = parse_expr(str(src))
    except ParseError as e:
        return _err("parse", str(e))
    report = compile_check(node)
    typ = None if report.typ is None else str(report.typ)
    return _ok(
        status=report.status.value,
        type=typ,
        holes=len(report.holes),
        errors=len(report.errors),
    )


def tool_run(args: dict) -> dict:
    src = args.get("source") or args.get("expr") or ""
    call = args.get("call")
    raw_args = args.get("args") or []
    try:
        if "\n" in str(src) or str(src).strip().upper().startswith("DEF"):
            prog = parse_program(str(src))
            if len(prog) == 1 and not str(src).strip().upper().startswith("DEF"):
                node = prog[0]
                val = vm_run(node)
            else:
                vm_args = []
                for a in raw_args:
                    if isinstance(a, int):
                        vm_args.append(IntVal(32, a))
                    elif isinstance(a, str):
                        vm_args.append(StringVal(a))
                    else:
                        return _err("args", "run args must be int or str")
                val = vm_run(prog, call=call, args=vm_args)
        else:
            node = parse_expr(str(src))
            val = vm_run(node)
    except ParseError as e:
        return _err("parse", str(e))
    return _ok(result=_value_repr(val))


def tool_constrain(args: dict) -> dict:
    """Constrain a literal-ish value against declared OUT type string."""
    out_type = args.get("out_type") or args.get("type") or ""
    raw = args.get("value")
    if not out_type:
        return _err("args", "out_type required")
    if isinstance(raw, bool):
        from knot.values import BoolVal

        val: Value = BoolVal(raw)  # type: ignore[assignment]
    elif isinstance(raw, int):
        val = IntVal(32, raw)
    elif isinstance(raw, str):
        val = StringVal(raw)
    elif raw is None:
        from knot.values import UnitVal

        val = UnitVal()
    else:
        return _err("args", "value must be bool|int|str|null")
    result = constrain(val, str(out_type))
    return _ok(result=_value_repr(result), declared=str(type_from_air(str(out_type))))


def tool_doc_query(args: dict) -> dict:
    q = args.get("query") or args.get("topic") or ""
    budget = int(args.get("max_tokens") or args.get("budget") or 500)
    extra = args.get("docs_dir")
    r = kb_retrieve(str(q), budget, extra_dir=extra)
    return _ok(
        text=r.text,
        tokens=r.tokens,
        card_ids=list(r.card_ids),
        truncated=r.truncated,
    )


def tool_query(args: dict) -> dict:
    """Graph inspection: path | children | op | canonical."""
    src = args.get("source") or args.get("expr") or ""
    kind = str(args.get("kind") or "canonical").lower()
    try:
        root = parse_expr(str(src))
    except ParseError as e:
        return _err("parse", str(e))
    if kind == "canonical":
        return _ok(canonical=print_canonical(root), op=type(root).__name__)
    if kind == "op":
        op = getattr(root, "op", None) or type(root).__name__
        return _ok(op=str(op))
    if kind == "children":
        kids = list(getattr(root, "children", ()) or ())
        return _ok(
            count=len(kids),
            children=[print_canonical(k) for k in kids],
        )
    if kind == "path":
        path = args.get("path") or []
        if isinstance(path, str):
            path = [int(p) if p.isdigit() else p for p in path.split(".") if p]
        try:
            node = get_at(root, tuple(path))
        except Exception as e:  # path errors as values across MCP
            return _err("path", str(e))
        return _ok(
            path=list(path),
            node=print_canonical(node) if node is not None else None,
            type=type(node).__name__ if node is not None else None,
        )
    return _err("args", "unknown query kind " + kind)


def tool_llm_format(args: dict) -> dict:
    text = format_for_llm(
        diagnostics=str(args.get("diagnostics") or ""),
        slices=str(args.get("slices") or ""),
        status=str(args.get("status") or ""),
        budget_tokens=int(args.get("budget_tokens") or args.get("budget") or 500),
        policy=str(args.get("policy") or "balanced"),
    )
    return _ok(text=text, tokens=len(text) // 4 if text else 0)


TOOLS: dict[str, Callable[[dict], dict]] = {
    "eval": tool_eval,
    "typecheck": tool_typecheck,
    "run": tool_run,
    "constrain": tool_constrain,
    "doc_query": tool_doc_query,
    "kb": tool_doc_query,
    "query": tool_query,
    "llm_format": tool_llm_format,
}


def list_tools() -> list[dict]:
    return [
        {"name": n, "description": fn.__doc__ or n}
        for n, fn in sorted(TOOLS.items())
        if n != "kb"  # alias of doc_query
    ] + [{"name": "kb", "description": "Alias of doc_query (token-budgeted kb)."}]


def call_tool(name: str, args: dict | None = None) -> dict:
    """Dispatch a tool by name. Never raises across the boundary (D1)."""
    fn = TOOLS.get(str(name))
    if fn is None:
        return _err("unknown_tool", "no tool named " + str(name))
    try:
        return fn(dict(args or {}))
    except Exception as e:
        return _err("internal", type(e).__name__ + ": " + str(e))
