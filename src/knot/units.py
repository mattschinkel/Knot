"""Units / dimensions for the Knot deterministic kernel (Phase 0).

A Dimension is an exponent map of base-dimension -> integer exponent
(spec D2). Base dimensions are the 7 SI bases plus user-named ones
(money, count, ...). The *name* of a base dimension is opaque; only the
exponent algebra matters.

  meters + meters      = meters          (compatible)
  meters * meters      = meters^2        (mul: add exponents)
  meters / seconds     = m·s^-1          (div: subtract exponents)
  meters + seconds     = dim mismatch    (returned as ErrorVal, not raised)

Dimension is frozen + hashable so it can live inside frozen Type values.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Dimension:
    """A product of base-dimensions to integer powers.

    Stored as a sorted tuple of (base_name, exponent) with zero
    exponents dropped, so equality and hashing are canonical.
    """

    items: tuple[tuple[str, int], ...] = ()

    @classmethod
    def from_map(cls, m: dict[str, int]) -> "Dimension":
        norm = tuple(sorted((k, v) for k, v in m.items() if v != 0))
        return cls(norm)

    def mul(self, other: "Dimension") -> "Dimension":
        acc: dict[str, int] = dict(self.items)
        for k, v in other.items:
            acc[k] = acc.get(k, 0) + v
        return Dimension.from_map(acc)

    def div(self, other: "Dimension") -> "Dimension":
        acc: dict[str, int] = dict(self.items)
        for k, v in other.items:
            acc[k] = acc.get(k, 0) - v
        return Dimension.from_map(acc)

    def compatible(self, other: "Dimension") -> bool:
        """Equal dimension maps (required for + / -)."""
        return self.items == other.items

    @property
    def is_dimensionless(self) -> bool:
        return not self.items

    def to_string(self) -> str:
        if not self.items:
            return "1"
        parts: list[str] = []
        for name, exp in self.items:
            parts.append(name if exp == 1 else f"{name}^{exp}")
        return "·".join(parts)

    def __str__(self) -> str:
        return self.to_string()


DIMENSIONLESS = Dimension(())

# SI base dimensions (convenience).
m = Dimension.from_map({"m": 1})
kg = Dimension.from_map({"kg": 1})
s = Dimension.from_map({"s": 1})
A = Dimension.from_map({"A": 1})
K = Dimension.from_map({"K": 1})
mol = Dimension.from_map({"mol": 1})
cd = Dimension.from_map({"cd": 1})
