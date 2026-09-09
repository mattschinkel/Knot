"""Structural path + label + ID helpers for Knot AST addressing (D2/D3/D7).

A structural path is a tuple of segments (ints or strs), e.g. (1, 2, "body").
Numeric IDs are compiler-internal sequential ints (never written by the LLM).
"""
from __future__ import annotations

# Module-local label registry (design D3).
_LABELS: dict[str, object] = {}

# Compiler-internal sequential node IDs (design D7).
_next_id: int = 0


def generate_path(*parts) -> tuple:
    """Build a structural path tuple.

    Accepts no args -> (); a dotted string "1.2.3" -> (1, 2, 3);
    a tuple/list -> normalized tuple; multiple args -> tuple of segments.
    Empty / invalid dotted strings return ().
    """
    if len(parts) == 0:
        return ()
    if len(parts) == 1:
        p = parts[0]
        if p is None or p == "":
            return ()
        if isinstance(p, str):
            segs = [s for s in p.split(".") if s != ""]
            if not segs:
                return ()
            out = []
            for s in segs:
                if s.isdigit() or (s.startswith("-") and s[1:].isdigit()):
                    out.append(int(s))
                elif s.isidentifier() or s.replace("_", "").isalnum():
                    out.append(s)
                else:
                    return ()
            return tuple(out)
        if isinstance(p, (tuple, list)):
            return tuple(p)
        return (p,)
    return tuple(parts)


def assign_label(label: str, node: object = None) -> str:
    """Register a symbolic label (module-local). Returns the label string."""
    if not isinstance(label, str) or not label:
        raise TypeError("label must be a non-empty str")
    _LABELS[label] = node
    return label


def lookup_label(label: str) -> object:
    """Return the node registered under `label`, or None."""
    return _LABELS.get(label)


def generate_id() -> int:
    """Allocate the next compiler-internal numeric node ID."""
    global _next_id
    n = _next_id
    _next_id += 1
    return n


def reset_ids() -> None:
    """Reset the ID counter (tests only)."""
    global _next_id
    _next_id = 0
