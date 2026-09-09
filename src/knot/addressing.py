"""Structural path helpers for Knot AST addressing (design D2).

A structural path is a tuple of segments (ints or strs), e.g. (1, 2, "body").
"""
from __future__ import annotations


def generate_path(*parts) -> tuple:
    """Build a structural path tuple.

    Accepts:
      - no args -> ()
      - a single dotted string "1.2.3" -> (1, 2, 3)  (int segments when numeric)
      - a single tuple/list -> normalized tuple
      - multiple args -> tuple of those segments
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
                    return ()  # invalid segment
            return tuple(out)
        if isinstance(p, (tuple, list)):
            return tuple(p)
        return (p,)
    return tuple(parts)
