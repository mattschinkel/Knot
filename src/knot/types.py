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


@dataclass(frozen=True)
class FnType(Type):
    """Function type: params -> ret (Phase 2 T12)."""

    params: tuple[Type, ...]
    ret: Type


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
ANY = BaseType("any")


def subtype(s: Type, t: Type) -> bool:
    """Structural subtyping lattice for the kernel (Phase 0 + Phase 2 T2).

    Rules:
      - reflexive: s <: s
      - never <: everything
      - T <: T?            (any value can be lifted to an option)
      - nominal <: its def (a named type is a subtype of its definition)
      - List[A] <: List[B] iff A <: B (covariant elem)
      - Set[A]  <: Set[B]  iff A <: B
      - Map[K1,V1] <: Map[K2,V2] iff K1 <: K2 and V1 <: V2
      - Tuple[A...] <: Tuple[B...] iff same arity and Ai <: Bi pairwise
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
    if isinstance(s, ListType) and isinstance(t, ListType):
        return subtype(s.elem, t.elem)
    if isinstance(s, SetType) and isinstance(t, SetType):
        return subtype(s.elem, t.elem)
    if isinstance(s, MapType) and isinstance(t, MapType):
        return subtype(s.key, t.key) and subtype(s.val, t.val)
    if isinstance(s, TupleType) and isinstance(t, TupleType):
        if len(s.elems) != len(t.elems):
            return False
        return all(subtype(a, b) for a, b in zip(s.elems, t.elems))
    return False


def unify(a: Type, b: Type) -> Type | None:
    """Full unification for the Knot deterministic kernel (Phase 0).

    Rules:
      - reflexive: a == b -> a
      - Option: a? == b? -> a?
      - List: a[] == b[] -> a[] if a == b else None
      - Tuple: a,b == c,d -> a==c and b==d -> a,b
      - Map: k->v == k->w -> k->v if v == w else None
      - Nominal: a == b -> a == b (aliases are equal)
      - BaseType: i32 == i32, f32 == f32, etc.
      - Never: never == never -> never
    """
    if a == b:
        return a
    if isinstance(a, OptionType) and isinstance(b, OptionType):
        return OptionType(unify(a.inner, b.inner))
    if isinstance(a, ListType) and isinstance(b, ListType):
        return ListType(unify(a.elem, b.elem))
    if isinstance(a, TupleType) and isinstance(b, TupleType):
        if len(a.types) == len(b.types):
            return TupleType([unify(a.types[i], b.types[i]) for i in range(len(a.types))])
    if isinstance(a, MapType) and isinstance(b, MapType):
        if len(a.keys) == len(b.keys):
            return MapType([unify(a.keys[i], b.keys[i]) for i in range(len(a.keys))], [unify(a.vals[i], b.vals[i]) for i in range(len(a.vals))])
    if isinstance(a, NominalType) and isinstance(b, NominalType):
        return unify(a.defn, b.defn)
    if isinstance(a, BaseType) and isinstance(b, BaseType):
        return a if a.name == b.name else None
    return None

from . import values
from . import checker

__all__ = ['Type', 'TypeError', 'IntVal', 'BoolVal', 'StrVal']
