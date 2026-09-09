"""Type algebra for the Knot deterministic kernel (Phase 0).

Types are frozen + hashable and form a small algebraic DSL (spec §4).
Phase 0 delivers the type *shapes* plus a base `subtype` lattice and a
`unify` stub. Full unification / inference is Phase 2; the stub exists
so value/type tests compile against the real hook.
"""

from __future__ import annotations

from dataclasses import dataclass

from .units import Dimension, DIMENSIONLESS


@dataclass(frozen=True)
class Type:
    """Base of the type algebra. All subclasses are frozen + hashable."""


@dataclass(frozen=True)
class BaseType(Type):
    name: str  # i32|i64|f32|f64|bool|string|bytes|unit|never


@dataclass(frozen=True)
class NominalType(Type):
    name: str
    defn: Type  # the type this nominal aliases (e.g. Distance -> f64@meters)


@dataclass(frozen=True)
class OptionType(Type):
    inner: Type


@dataclass(frozen=True)
class ListType(Type):
    elem: Type


@dataclass(frozen=True)
class SetType(Type):
    elem: Type


@dataclass(frozen=True)
class MapType(Type):
    key: Type
    val: Type


@dataclass(frozen=True)
class TupleType(Type):
    elems: tuple[Type, ...]


@dataclass(frozen=True)
class RecordType(Type):
    name: str
    fields: tuple[tuple[str, Type], ...]  # sorted by field name


@dataclass(frozen=True)
class SumType(Type):
    variants: tuple[tuple[str, RecordType], ...]  # sorted by tag


@dataclass(frozen=True)
class CapIntersect(Type):
    caps: tuple[Type, ...]


@dataclass(frozen=True)
class UnitType(Type):
    base: Type
    dim: Dimension


@dataclass(frozen=True)
class RegionType(Type):
    """Lifetime / region (spec Q3: shape only in Phase 0, no checking)."""

    inner: Type
    region: str


# Predefined base types.
I32 = BaseType("i32")
I64 = BaseType("i64")
F32 = BaseType("f32")
F64 = BaseType("f64")
BOOL = BaseType("bool")
STRING = BaseType("string")
BYTES = BaseType("bytes")
UNIT = BaseType("unit")
NEVER = BaseType("never")


def subtype(s: Type, t: Type) -> bool:
    """Base subtyping lattice for the kernel (Phase 0).

    Rules:
      - reflexive: s <: s
      - never <: everything
      - T <: T?            (any value can be lifted to an option)
      - nominal <: its def (a named type is a subtype of its definition)
    Note: 'everything <: unit' is intentionally NOT included; discarding
    a value into unit is a coercion, not subtyping, and would be unsound.
    """
    if s == t:
        return True
    if s == NEVER:
        return True  # never <: everything
    if isinstance(t, OptionType):
        return subtype(s, t.inner)
    if isinstance(s, NominalType):
        if subtype(s.defn, t):
            return True
    return False


def unify(a: Type, b: Type) -> Type | None:
    """Stub: reflexive only. Full unification arrives in Phase 2."""
    if a == b:
        return a
    return None
