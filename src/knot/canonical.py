"""Canonical AIR printer (D-FB11): no whitespace inside forms.

Pretty view stays in printer.py. normalize(src) = print_canonical(parse(src)).
"""

from __future__ import annotations

from knot.ast import (
    CallExpr,
    DefNode,
    DependsDecl,
    ErrExpr,
    ExportList,
    FnExpr,
    HoleExpr,
    IdentExpr,
    IfExpr,
    ImportDecl,
    InlineCase,
    InlineTest,
    InvokeExpr,
    LitExpr,
    ModelDecl,
    ModuleDecl,
    OpExpr,
    ParExpr,
    PropertyDecl,
    RefExpr,
    SeqExpr,
    ToolDecl,
    TypedLit,
    UnitExpr,
    UnsafeExpr,
    DerefExpr,
)


def print_canonical(node) -> str:
    """Emit canonical bracket AIR with no spaces."""
    if node is None:
        return ""
    if isinstance(node, (list, tuple)):
        return "".join(print_canonical(n) for n in node)
    return _canon(node)


def normalize(src: str) -> str:
    """parse → print_canonical (unique string for equivalent AIR)."""
    from knot.parser import parse_expr

    return print_canonical(parse_expr(src))


def _canon(node) -> str:
    if isinstance(node, ParExpr):
        return "PAR[" + ",".join(_canon(b) for b in node.branches) + "]"
    if isinstance(node, SeqExpr):
        return "SEQ[" + ",".join(_canon(s) for s in node.steps) + "]"
    if isinstance(node, RefExpr):
        return "REF[" + node.region + "," + _canon(node.expr) + "]"
    if isinstance(node, DerefExpr):
        return "DEREF[" + _canon(node.expr) + "]"
    if isinstance(node, UnsafeExpr):
        return (
            "UNSAFE[CAPS["
            + ",".join(node.caps)
            + "],"
            + _canon(node.body)
            + "]"
        )
    if isinstance(node, ModelDecl):
        return (
            "MODEL["
            + node.name
            + ",IN["
            + node.in_type
            + "],OUT["
            + node.out_type
            + "],CONF["
            + ("true" if node.confidence else "false")
            + "],EFFECTS["
            + ",".join(node.effects)
            + "]]"
        )
    if isinstance(node, ToolDecl):
        return (
            "TOOL["
            + node.name
            + ",IN["
            + node.in_type
            + "],OUT["
            + node.out_type
            + "],EFFECTS["
            + ",".join(node.effects)
            + "]]"
        )
    if isinstance(node, InvokeExpr):
        parts = [node.name] + [_canon(a) for a in node.args]
        return "INVOKE[" + ",".join(parts) + "]"
    if isinstance(node, ModuleDecl):
        parts = [node.name]
        if node.version and node.version != "0":
            parts.append("VERSION[" + node.version + "]")
        parts.extend(_canon(x) for x in node.body)
        parts.append("EXPORT[" + ",".join(node.exports) + "]")
        return "MODULE[" + ",".join(parts) + "]"
    if isinstance(node, ImportDecl):
        parts = [node.module] + list(node.names)
        return "IMPORT[" + ",".join(parts) + "]"
    if isinstance(node, DependsDecl):
        parts = [node.module, node.version]
        if node.caps:
            parts.append("CAPS[" + ",".join(node.caps) + "]")
        return "DEPENDS[" + ",".join(parts) + "]"
    if isinstance(node, ExportList):
        return "EXPORT[" + ",".join(node.names) + "]"
    if isinstance(node, InlineTest):
        parts = [node.name] + [
            "CASE[" + _canon(c.inp) + "," + _canon(c.out) + "]" for c in node.cases
        ]
        return "TEST[" + ",".join(parts) + "]"
    if isinstance(node, PropertyDecl):
        params = ",".join(
            (str(p[0]) + ":" + str(p[1])) if len(p) > 1 and p[1] is not None else str(p[0])
            for p in node.params
        )
        return (
            "PROPERTY["
            + node.name
            + ",[["
            + params
            + "],"
            + _canon(node.body)
            + "]]"
        )
    if isinstance(node, ErrExpr):
        parts = [
            node.code,
            _path(node.path),
            str(node.expected),
            str(node.actual),
        ]
        parts.extend(_canon(f) for f in node.fixes)
        return "ERR[" + ",".join(parts) + "]"
    if isinstance(node, DefNode):
        return "DEF[" + str(node.name) + "," + _canon(node.body) + "]"
    if isinstance(node, FnExpr):
        params = ",".join(
            (str(p[0]) + ":" + str(p[1])) if len(p) > 1 and p[1] is not None else str(p[0])
            for p in node.params
        )
        return "FN[[" + params + "]," + _canon(node.body) + "]"
    if isinstance(node, OpExpr):
        args = ",".join(_canon(c) for c in node.children)
        return str(node.op) + "[" + args + "]"
    if isinstance(node, CallExpr):
        args = ",".join(_canon(a) for a in (node.args or []))
        return _canon(node.fn) + "[" + args + "]"
    if isinstance(node, IfExpr):
        return (
            "IF["
            + _canon(node.cond)
            + ","
            + _canon(node.then_branch)
            + ","
            + _canon(node.else_branch)
            + "]"
        )
    if isinstance(node, HoleExpr):
        if node.label:
            return "?:" + str(node.label)
        return "?"
    if isinstance(node, TypedLit):
        return _lit(node.value) + ":" + str(node.type_name)
    if isinstance(node, LitExpr):
        return _lit(node.value)
    if isinstance(node, IdentExpr):
        return str(node.id)
    if isinstance(node, UnitExpr):
        return "UNIT"
    return str(node)


def _path(segs) -> str:
    return "[" + ",".join(str(s) for s in segs) + "]"


def _lit(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "nil"
    if isinstance(value, str):
        return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"
    return str(value)
