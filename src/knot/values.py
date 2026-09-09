"""Value representation for the Knot deterministic kernel (Phase 0).

Every runtime value is an instance of a Value subclass. Values are
frozen + hashable (spec D1). Holes and errors are VALUES (spec D3/D4),
not a separate representation, so partial programs stay composable.

No LLM, no parser, no I/O lives here.
"""

from __future__ import annotations

from dataclasses import dataclass

from .errors import StructuredError
from .types import (
    Type,
    BaseType,
    ListType,
    SetType,
    MapType,
    TupleType,
    RecordType,
    SumType,
    UnitType,
    NEVER,
    UNIT,
)
from .units import Dimension


@dataclass(frozen=True)
class Value:
    """Base of the value representation. All subclasses are frozen."""

    @property
    def type(self) -> Type:  # pragma: no cover - abstract
        raise NotImplementedError


@dataclass(frozen=True)
class IntVal(Value):
    bits: int  # 32 or 64
    value: int

    @property
    def type(self) -> Type:
        return BaseType(f"i{self.bits}")


@dataclass(frozen=True)
class FloatVal(Value):
    bits: int  # 32 or 64
    value: float

    @property
    def type(self) -> Type:
        return BaseType(f"f{self.bits}")


@dataclass(frozen=True)
class BoolVal(Value):
    value: bool

    @property
    def type(self) -> Type:
        return BaseType("bool")


@dataclass(frozen=True)
class StringVal(Value):
    # Q2: string is a sequence of code points. Stored as a Python str
    # (code-point sequence); bytes is a separate BytesVal.
    value: str

    @property
    def type(self) -> Type:
        return BaseType("string")


@dataclass(frozen=True)
class BytesVal(Value):
    value: bytes

    @property
    def type(self) -> Type:
        return BaseType("bytes")


@dataclass(frozen=True)
class UnitVal(Value):
    @property
    def type(self) -> Type:
        return UNIT


@dataclass(frozen=True)
class ListVal(Value):
    items: tuple[Value, ...]
    elem_t: Type

    @property
    def type(self) -> Type:
        return ListType(self.elem_t)


@dataclass(frozen=True)
class SetVal(Value):
    items: frozenset[Value]
    elem_t: Type

    @property
    def type(self) -> Type:
        return SetType(self.elem_t)


@dataclass(frozen=True)
class MapVal(Value):
    # frozenset of (key, value) pairs so order doesn't affect equality.
    items: frozenset[tuple[Value, Value]]
    key_t: Type
    val_t: Type

    @property
    def type(self) -> Type:
        return MapType(self.key_t, self.val_t)


@dataclass(frozen=True)
class TupleVal(Value):
    items: tuple[Value, ...]
    types: tuple[Type, ...]

    @property
    def type(self) -> Type:
        return TupleType(self.types)


@dataclass(frozen=True)
class SumVal(Value):
    tag: str
    payload: Value
    sum_t: SumType

    @property
    def type(self) -> Type:
        return self.sum_t


@dataclass(frozen=True)
class RecordVal(Value):
    # frozenset of (field_name, value) pairs; order-independent equality.
    fields: frozenset[tuple[str, Value]]
    rec_t: RecordType

    @property
    def type(self) -> Type:
        return self.rec_t


@dataclass(frozen=True)
class MeasuredVal(Value):
    """A value carrying a unit/dimension (spec §5, T@dim). e.g. 10:meters."""

    base: Value
    dim: Dimension

    @property
    def type(self) -> Type:
        return UnitType(self.base.type, self.dim)


@dataclass(frozen=True)
class HoleVal(Value):
    """A hole is a value (spec D3). Type-checks against ANY type as PARTIAL.

    expected=None is the bare `?`; expected=T is `?:T`.
    """

    expected: Type | None = None

    @property
    def type(self) -> Type | None:
        return self.expected


@dataclass(frozen=True)
class ErrorVal(Value):
    """An error is a value (spec D4). Flows through partial programs.

    Its type is `never` so it subtype-checks against anything (never <:
    everything), letting an error propagate where a real value is needed.
    """

    err: StructuredError

    @property
    def type(self) -> Type:
        return NEVER
