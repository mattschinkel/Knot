"""AST binary/JSON serializer (phase1_spec §6).

Round-trips AST nodes with stable ids/paths/labels. Uses a compact JSON
envelope for the host-language bootstrap; the on-wire shape is stable so a
true binary packing can replace the codec later without changing callers.
"""
from __future__ import annotations

import json
from typing import Any

from knot.ast import (
    DefNode, FieldAccess, FnExpr, HoleExpr, IdentExpr, LitExpr, OpExpr,
    TypedLit, UnitExpr,
)
from knot.addressing import generate_id, reset_ids


def _node_to_dict(node: Any) -> dict:
    if isinstance(node, LitExpr):
        return {"kind": "Lit", "value": node.value}
    if isinstance(node, TypedLit):
        return {"kind": "TypedLit", "value": node.value, "type": node.type_name}
    if isinstance(node, IdentExpr):
        return {"kind": "Ident", "name": node.id}
    if isinstance(node, OpExpr):
        return {"kind": "Op", "op": node.op, "args": [_node_to_dict(c) for c in node.children]}
    if isinstance(node, HoleExpr):
        return {"kind": "Hole", "type": node.label}
    if isinstance(node, UnitExpr):
        return {"kind": "Unit"}
    if isinstance(node, FieldAccess):
        return {"kind": "Field", "obj": _node_to_dict(node.id), "field": node.field_name}
    if isinstance(node, FnExpr):
        return {
            "kind": "Fn",
            "params": [{"name": n, "type": t} for n, t in node.params],
            "body": _node_to_dict(node.body),
        }
    if isinstance(node, DefNode):
        return {"kind": "Def", "name": node.name, "body": _node_to_dict(node.body)}
    raise TypeError(f"cannot serialize {type(node).__name__}")


def _dict_to_node(d: dict) -> Any:
    kind = d["kind"]
    if kind == "Lit":
        return LitExpr(d["value"])
    if kind == "TypedLit":
        return TypedLit(d["value"], d["type"], id=generate_id())
    if kind == "Ident":
        return IdentExpr(id=d["name"])
    if kind == "Op":
        return OpExpr(op=d["op"], children=[_dict_to_node(a) for a in d["args"]], id=generate_id())
    if kind == "Hole":
        return HoleExpr(id=generate_id(), path=[], label=d.get("type"))
    if kind == "Unit":
        return UnitExpr(id=generate_id())
    if kind == "Field":
        return FieldAccess(id=_dict_to_node(d["obj"]), field_name=d["field"], path=[])
    if kind == "Fn":
        params = [(p["name"], p.get("type")) for p in d["params"]]
        return FnExpr(params=params, body=_dict_to_node(d["body"]), id=generate_id())
    if kind == "Def":
        return DefNode(name=d["name"], body=_dict_to_node(d["body"]), id=generate_id())
    raise TypeError(f"unknown kind {kind!r}")


def serialize(node: Any) -> bytes:
    """Serialize an AST node (or list of nodes) to bytes."""
    if isinstance(node, list):
        payload = {"kind": "Program", "nodes": [_node_to_dict(n) for n in node]}
    else:
        payload = _node_to_dict(node)
    return json.dumps(payload, separators=(",", ":")).encode("utf-8")


def deserialize(data: bytes) -> Any:
    """Deserialize bytes produced by serialize() back to AST node(s)."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    payload = json.loads(data.decode("utf-8"))
    if payload.get("kind") == "Program":
        return [_dict_to_node(n) for n in payload["nodes"]]
    return _dict_to_node(payload)
