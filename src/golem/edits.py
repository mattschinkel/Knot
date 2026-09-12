"""Surgical AST edit operations (Phase 6).

Edits are immutable graph ops addressed by structural path or label (§21).
Phase 5 REPLACE repairs are applied here; blast radius + revalidation reported.
"""

from __future__ import annotations

from dataclasses import dataclass

from .addressing import lookup_label
from .ast import (
    CallExpr,
    DefNode,
    ErrExpr,
    FnExpr,
    IdentExpr,
    IfExpr,
    LitExpr,
    OpExpr,
)
from .errors import StructuredError
from .partial import CompileReport, compile_check
from .values import ErrorVal


@dataclass(frozen=True)
class EditResult:
    """Outcome of apply_edit."""

    ok: bool
    root: object | None
    blast_radius: tuple[tuple, ...]
    revalidation: CompileReport | None = None
    error: ErrorVal | None = None
    note: str = ""


def path_from_segs(*segs) -> tuple:
    """Build a path tuple from int/str segments."""
    out = []
    for s in segs:
        if isinstance(s, bool):
            out.append(s)
        elif isinstance(s, int):
            out.append(s)
        elif isinstance(s, float) and s == int(s):
            out.append(int(s))
        elif isinstance(s, str):
            if s.isdigit() or (s.startswith("-") and s[1:].isdigit()):
                out.append(int(s))
            else:
                out.append(s)
        else:
            out.append(s)
    return tuple(out)


def path_from_ast(path_node: object) -> tuple:
    """Decode PATH from AIR: LIST[segs] | Ident (label/name) | lit."""
    if path_node is None:
        return ()
    if isinstance(path_node, (list, tuple)):
        return path_from_segs(*path_node)
    if isinstance(path_node, IdentExpr):
        name = str(path_node.id)
        if name.startswith("@"):
            name = name[1:]
        labeled = lookup_label(name)
        if labeled is not None:
            p = getattr(labeled, "path", None)
            if p:
                return tuple(p)
        return (name,)
    if isinstance(path_node, LitExpr):
        return path_from_segs(path_node.value)
    if isinstance(path_node, OpExpr) and str(path_node.op).upper() in ("LIST", "PATH", "P"):
        segs = []
        for c in path_node.children or []:
            if isinstance(c, LitExpr):
                segs.append(c.value)
            elif isinstance(c, IdentExpr):
                segs.append(c.id)
            else:
                raise TypeError("path segment must be lit or ident")
        return path_from_segs(*segs)
    raise TypeError("unsupported path node: " + type(path_node).__name__)


def get_at(root: object, path: tuple | list) -> object:
    """Return the node at structural path."""
    path = tuple(path)
    cur = root
    for i, seg in enumerate(path):
        cur = _child(cur, seg, path[: i + 1])
    return cur


def _child(node: object, seg, path_so_far: tuple) -> object:
    if isinstance(seg, int):
        kids = children_of(node)
        if seg < 0 or seg >= len(kids):
            raise LookupError("path index out of range: " + str(path_so_far))
        return kids[seg]
    if not isinstance(seg, str):
        raise LookupError("bad path segment: " + repr(seg))
    if isinstance(node, DefNode):
        if seg == "body":
            return node.body
        if seg == "name":
            return node.name
        raise LookupError("DefNode has no " + seg)
    if isinstance(node, FnExpr):
        if seg == "body":
            return node.body
        if seg == "params":
            return list(node.params)
        raise LookupError("FnExpr has no " + seg)
    if isinstance(node, IfExpr):
        if seg == "cond":
            return node.cond
        if seg in ("then", "then_branch"):
            return node.then_branch
        if seg in ("else", "else_branch"):
            return node.else_branch
        raise LookupError("IfExpr has no " + seg)
    if isinstance(node, CallExpr):
        if seg == "fn":
            return node.fn
        if seg == "args":
            return list(node.args or [])
        raise LookupError("CallExpr has no " + seg)
    if isinstance(node, OpExpr):
        if seg == "op":
            return node.op
        raise LookupError("OpExpr children use int index, not " + seg)
    if isinstance(node, ErrExpr):
        if seg == "fixes":
            return list(node.fixes)
        if seg in ("code", "expected", "actual"):
            return getattr(node, seg)
        raise LookupError("ErrExpr has no " + seg)
    if isinstance(node, list):
        for item in node:
            if isinstance(item, DefNode) and item.name == seg:
                return item
        raise LookupError("no def named " + seg)
    raise LookupError(
        "cannot step into " + type(node).__name__ + " with " + repr(seg)
    )


def children_of(node: object) -> list:
    if isinstance(node, OpExpr):
        return list(node.children or [])
    if isinstance(node, CallExpr):
        return list(node.args or [])
    if isinstance(node, FnExpr):
        return [node.body]
    if isinstance(node, DefNode):
        return [node.body]
    if isinstance(node, IfExpr):
        return [node.cond, node.then_branch, node.else_branch]
    if isinstance(node, ErrExpr):
        return list(node.fixes)
    if isinstance(node, (list, tuple)):
        return list(node)
    kids = getattr(node, "children", None)
    return list(kids) if kids is not None else []


def _with_children(node: object, kids: list) -> object:
    if isinstance(node, OpExpr):
        return OpExpr(
            op=node.op,
            children=kids,
            id=getattr(node, "id", None),
            path=getattr(node, "path", None),
            label=getattr(node, "label", None),
        )
    if isinstance(node, CallExpr):
        return CallExpr(node.fn, kids)
    if isinstance(node, DefNode):
        return DefNode(
            name=node.name,
            body=kids[0] if kids else node.body,
            id=node.id,
            path=node.path,
            label=node.label,
        )
    if isinstance(node, FnExpr):
        return FnExpr(
            params=list(node.params),
            body=kids[0] if kids else node.body,
            id=node.id,
            path=node.path,
            label=node.label,
            effects=getattr(node, "effects", None),
            caps=getattr(node, "caps", None),
        )
    if isinstance(node, IfExpr):
        return IfExpr(kids[0], kids[1], kids[2])
    if isinstance(node, ErrExpr):
        return ErrExpr(
            node.code, node.path, node.expected, node.actual, kids,
            id=node.id, label=node.label,
        )
    if isinstance(node, list):
        return list(kids)
    raise TypeError("cannot set children on " + type(node).__name__)


def replace_at(root: object, path: tuple | list, new_node: object) -> object:
    """Immutable replace of the node at path."""
    path = tuple(path)
    if not path:
        return new_node

    def go(node, i):
        if i == len(path) - 1:
            seg = path[i]
            if isinstance(seg, int):
                kids = children_of(node)
                new_kids = list(kids)
                new_kids[seg] = new_node
                return _with_children(node, new_kids)
            if isinstance(node, DefNode) and seg == "body":
                return DefNode(
                    name=node.name, body=new_node,
                    id=node.id, path=node.path, label=node.label,
                )
            if isinstance(node, FnExpr) and seg == "body":
                return FnExpr(
                    params=list(node.params), body=new_node,
                    id=node.id, path=node.path, label=node.label,
                    effects=getattr(node, "effects", None),
                    caps=getattr(node, "caps", None),
                )
            if isinstance(node, IfExpr):
                cond, then_b, else_b = node.cond, node.then_branch, node.else_branch
                if seg == "cond":
                    cond = new_node
                elif seg in ("then", "then_branch"):
                    then_b = new_node
                elif seg in ("else", "else_branch"):
                    else_b = new_node
                else:
                    raise LookupError(seg)
                return IfExpr(cond, then_b, else_b)
            if isinstance(node, CallExpr) and seg == "fn":
                return CallExpr(new_node, list(node.args or []))
            if isinstance(node, list) and isinstance(seg, str):
                out = []
                found = False
                for item in node:
                    if isinstance(item, DefNode) and item.name == seg:
                        out.append(new_node)
                        found = True
                    else:
                        out.append(item)
                if not found:
                    raise LookupError("no def named " + seg)
                return out
            # replace named child by stepping then can't — use int
            raise LookupError("cannot replace via segment " + repr(seg))
        seg = path[i]
        if isinstance(seg, int):
            kids = children_of(node)
            new_kids = list(kids)
            new_kids[seg] = go(kids[seg], i + 1)
            return _with_children(node, new_kids)
        if isinstance(node, DefNode) and seg == "body":
            return DefNode(
                name=node.name, body=go(node.body, i + 1),
                id=node.id, path=node.path, label=node.label,
            )
        if isinstance(node, FnExpr) and seg == "body":
            return FnExpr(
                params=list(node.params), body=go(node.body, i + 1),
                id=node.id, path=node.path, label=node.label,
                effects=getattr(node, "effects", None),
                caps=getattr(node, "caps", None),
            )
        if isinstance(node, IfExpr):
            cond, then_b, else_b = node.cond, node.then_branch, node.else_branch
            if seg == "cond":
                cond = go(cond, i + 1)
            elif seg in ("then", "then_branch"):
                then_b = go(then_b, i + 1)
            elif seg in ("else", "else_branch"):
                else_b = go(else_b, i + 1)
            else:
                raise LookupError(seg)
            return IfExpr(cond, then_b, else_b)
        if isinstance(node, CallExpr) and seg == "fn":
            return CallExpr(go(node.fn, i + 1), list(node.args or []))
        if isinstance(node, list) and isinstance(seg, str):
            out = []
            found = False
            for item in node:
                if isinstance(item, DefNode) and item.name == seg:
                    out.append(go(item, i + 1))
                    found = True
                else:
                    out.append(item)
            if not found:
                raise LookupError("no def named " + seg)
            return out
        raise LookupError("cannot walk " + repr(seg))

    return go(root, 0)


def delete_at(root: object, path: tuple | list) -> object:
    """Delete child at path (last segment must be int index)."""
    path = tuple(path)
    if not path:
        raise ValueError("cannot delete root")
    if not isinstance(path[-1], int):
        raise ValueError("DELETE path must end with an int index")
    parent_path, idx = path[:-1], path[-1]

    def go(node, i):
        if i == len(parent_path):
            kids = children_of(node)
            new_kids = list(kids)
            del new_kids[idx]
            return _with_children(node, new_kids)
        return _walk_update(node, parent_path, i, go)

    return go(root, 0)


def insert_at(
    root: object, parent_path: tuple | list, index: int, new_node: object
) -> object:
    """Insert among children of parent_path at index."""
    parent_path = tuple(parent_path)

    def go(node, i):
        if i == len(parent_path):
            kids = children_of(node)
            new_kids = list(kids)
            if index < 0 or index > len(new_kids):
                raise LookupError("insert index out of range")
            new_kids.insert(index, new_node)
            return _with_children(node, new_kids)
        return _walk_update(node, parent_path, i, go)

    return go(root, 0)


def _walk_update(node, path, i, go):
    seg = path[i]
    if isinstance(seg, int):
        kids = children_of(node)
        new_kids = list(kids)
        new_kids[seg] = go(kids[seg], i + 1)
        return _with_children(node, new_kids)
    if isinstance(node, DefNode) and seg == "body":
        return DefNode(
            name=node.name, body=go(node.body, i + 1),
            id=node.id, path=node.path, label=node.label,
        )
    if isinstance(node, FnExpr) and seg == "body":
        return FnExpr(
            params=list(node.params), body=go(node.body, i + 1),
            id=node.id, path=node.path, label=node.label,
            effects=getattr(node, "effects", None),
            caps=getattr(node, "caps", None),
        )
    if isinstance(node, IfExpr):
        cond, then_b, else_b = node.cond, node.then_branch, node.else_branch
        if seg == "cond":
            cond = go(cond, i + 1)
        elif seg in ("then", "then_branch"):
            then_b = go(then_b, i + 1)
        elif seg in ("else", "else_branch"):
            else_b = go(else_b, i + 1)
        else:
            raise LookupError(seg)
        return IfExpr(cond, then_b, else_b)
    if isinstance(node, CallExpr) and seg == "fn":
        return CallExpr(go(node.fn, i + 1), list(node.args or []))
    if isinstance(node, list) and isinstance(seg, str):
        out = []
        found = False
        for item in node:
            if isinstance(item, DefNode) and item.name == seg:
                out.append(go(item, i + 1))
                found = True
            else:
                out.append(item)
        if not found:
            raise LookupError("no def named " + seg)
        return out
    raise LookupError("cannot walk " + repr(seg))


def rename_at(root: object, path: tuple | list, new_name: str) -> object:
    """Rename DefNode.name or IdentExpr at path."""
    path = tuple(path)
    target = get_at(root, path) if path else root
    if isinstance(target, DefNode):
        new = DefNode(
            name=new_name, body=target.body,
            id=target.id, path=target.path, label=target.label,
        )
        return replace_at(root, path, new) if path else new
    if isinstance(target, IdentExpr):
        new = IdentExpr(id=new_name)
        return replace_at(root, path, new) if path else new
    raise TypeError("RENAME expects DefNode or IdentExpr")


def blast_radius(path: tuple | list) -> tuple[tuple, ...]:
    """Changed path + all ancestor prefixes (Phase 6 D6)."""
    path = tuple(path)
    out = [()]
    for i in range(len(path)):
        out.append(path[: i + 1])
    # most specific last; include full path
    return tuple(dict.fromkeys(out))  # unique, order preserved


def _is_wildcard(node: object) -> bool:
    return isinstance(node, IdentExpr) and str(node.id) == "_"


def matches(pattern: object, node: object) -> bool:
    """Structural match; Ident `_` matches anything."""
    if _is_wildcard(pattern):
        return True
    if type(pattern) is not type(node):
        # LitExpr value compare across
        if isinstance(pattern, LitExpr) and isinstance(node, LitExpr):
            return pattern.value == node.value
        return False
    if isinstance(pattern, LitExpr):
        return pattern.value == node.value
    if isinstance(pattern, IdentExpr):
        return pattern.id == node.id
    if isinstance(pattern, OpExpr):
        if pattern.op != node.op:
            return False
        pk = list(pattern.children or [])
        nk = list(node.children or [])
        if len(pk) != len(nk):
            return False
        return all(matches(a, b) for a, b in zip(pk, nk))
    if isinstance(pattern, DefNode):
        return pattern.name == node.name and matches(pattern.body, node.body)
    if isinstance(pattern, FnExpr):
        return matches(pattern.body, node.body)
    if isinstance(pattern, IfExpr):
        return (
            matches(pattern.cond, node.cond)
            and matches(pattern.then_branch, node.then_branch)
            and matches(pattern.else_branch, node.else_branch)
        )
    return pattern == node


def find_matches(root: object, pattern: object, prefix: tuple = ()) -> list[tuple]:
    """Return all paths where pattern matches."""
    found: list[tuple] = []
    if matches(pattern, root):
        found.append(prefix)
    kids = children_of(root)
    for i, kid in enumerate(kids):
        found.extend(find_matches(kid, pattern, prefix + (i,)))
    # also walk named roles for Def/Fn/If so paths can use body/cond
    if isinstance(root, DefNode):
        found.extend(find_matches(root.body, pattern, prefix + ("body",)))
    elif isinstance(root, FnExpr):
        found.extend(find_matches(root.body, pattern, prefix + ("body",)))
    elif isinstance(root, IfExpr):
        found.extend(find_matches(root.cond, pattern, prefix + ("cond",)))
        found.extend(find_matches(root.then_branch, pattern, prefix + ("then",)))
        found.extend(find_matches(root.else_branch, pattern, prefix + ("else",)))
    return found


def replace_match(root: object, pattern: object, replacement: object) -> object:
    """Replace the unique match of pattern; raise LookupError if not unique."""
    hits = find_matches(root, pattern)
    # Prefer int-index paths over named duplicates of same node
    # Dedupe by object identity via path length preference: unique paths only
    if len(hits) == 0:
        raise LookupError("REPLACE_MATCH: no match")
    if len(hits) > 1:
        # If both (0,) and ("body",) point to same logical node, prefer one —
        # for OpExpr-only trees, only int paths exist.
        # Filter: if two paths point to equal nodes, keep shortest.
        uniq = []
        seen_nodes = []
        for p in hits:
            n = get_at(root, p)
            if any(n is s or n == s for s in seen_nodes):
                continue
            seen_nodes.append(n)
            uniq.append(p)
        if len(uniq) != 1:
            raise LookupError(
                "REPLACE_MATCH: ambiguous (" + str(len(uniq)) + " matches)"
            )
        hits = uniq
    return replace_at(root, hits[0], replacement)


def apply_edit(root: object, edit: object) -> EditResult:
    """Apply an edit OpExpr (or tuple form) and revalidate.

    AIR:
      REPLACE[PATH, EXPR]
      DELETE[PATH]
      INSERT[PATH, INDEX, EXPR]
      RENAME[PATH, IDENT]
      REPLACE_MATCH[PATTERN, EXPR]
    PATH is LIST[seg...] or Ident label/name.
    """
    try:
        if isinstance(edit, OpExpr):
            op = str(edit.op).upper()
            args = list(edit.children or [])
            if op == "REPLACE":
                if len(args) != 2:
                    raise ValueError("REPLACE needs PATH, EXPR")
                path = path_from_ast(args[0])
                new_root = replace_at(root, path, args[1])
                return _ok(new_root, path)
            if op == "DELETE":
                if len(args) != 1:
                    raise ValueError("DELETE needs PATH")
                path = path_from_ast(args[0])
                new_root = delete_at(root, path)
                return _ok(new_root, path)
            if op == "INSERT":
                if len(args) != 3:
                    raise ValueError("INSERT needs PATH, INDEX, EXPR")
                path = path_from_ast(args[0])
                idx = args[1].value if isinstance(args[1], LitExpr) else int(args[1])
                new_root = insert_at(root, path, idx, args[2])
                return _ok(new_root, path + (idx,))
            if op == "RENAME":
                if len(args) != 2:
                    raise ValueError("RENAME needs PATH, IDENT")
                path = path_from_ast(args[0])
                name = str(args[1].id) if isinstance(args[1], IdentExpr) else str(args[1])
                new_root = rename_at(root, path, name)
                return _ok(new_root, path)
            if op == "REPLACE_MATCH":
                if len(args) != 2:
                    raise ValueError("REPLACE_MATCH needs PATTERN, EXPR")
                new_root = replace_match(root, args[0], args[1])
                # blast: all paths that matched before — recompute as ()
                hits = find_matches(root, args[0])
                path = hits[0] if hits else ()
                return _ok(new_root, path)
            raise ValueError("unknown edit op " + op)
        raise TypeError("edit must be OpExpr")
    except (LookupError, ValueError, TypeError) as e:
        return EditResult(
            ok=False,
            root=None,
            blast_radius=(),
            error=ErrorVal(
                StructuredError(kind="edit", message=str(e))
            ),
            note=str(e),
        )


def _ok(new_root: object, path: tuple) -> EditResult:
    radius = blast_radius(path)
    report = compile_check(new_root)
    return EditResult(
        ok=True,
        root=new_root,
        blast_radius=radius,
        revalidation=report,
        note="ok",
    )
