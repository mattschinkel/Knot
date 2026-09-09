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


# Module-local label registry (design D3: sparse, module-local symbolic labels).
_LABELS: dict[str, object] = {}


def assign_label(label: str, node: object = None) -> str:
    """Register a symbolic label (module-local). Returns the label string."""
    if not isinstance(label, str) or not label:
        raise TypeError("label must be a non-empty str")
    _LABELS[label] = node
    return label


def lookup_label(label: str) -> object:
    """Return the node registered under `label`, or None."""
    return _LABELS.get(label)

def generate_id():
    """Generate a unique node ID as a string in the format "node_N" where N is a sequential integer.

    Returns:
        str: A unique node ID string (e.g., "node_0", "node_1", etc.)
    """
    return f"node_{_next_label() }"

__all__ = ["generate_id"]

__all__ = ["generate_id"]

__all__ = ["generate_id"]

__all__ = ["generate_id"]

__all__ = ["generate_id"]

# Internal implementation details
_label_registry = {}
_next_label = 1

# Exported API
__all__ = ["generate_id"]

# For testing purposes only
__test__ = {"clears_on_reset": "node_1"}

# Internal implementation details
_label_registry = {}
_next_label = 1

# Exported API
__all__ = ["generate_id"]
