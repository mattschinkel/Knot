"""Structured errors for the Golem deterministic kernel (Phase 0).

Errors are VALUES (errors-as-values, spec D4): the kernel returns an
ErrorVal wrapping a StructuredError instead of raising. This keeps
partial programs composable. Phase 0 defines only the shape; the type
checker (Phase 2) and the AI front-end (Phase 5) populate it fully.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import Type


@dataclass(frozen=True)
class StructuredError:
    """Machine-readable error. Returned, not raised."""

    kind: str  # "type" | "dim" | "arity" | "hole" | ...
    node: str | None = None  # structural path or @label (Phase 1 fills)
    op: str | None = None  # kernel op name, e.g. "ADD"
    expected: "Type | None" = None
    got: "Type | None" = None
    repair: tuple[str, ...] = ()  # candidate repairs (R3 fills in Phase 5)
    message: str = ""

    def __str__(self) -> str:
        where = f" at {self.node}" if self.node else ""
        what = f" in {self.op}" if self.op else ""
        return f"[{self.kind}]{what}{where}: {self.message}".strip()
