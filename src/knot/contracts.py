"""Contracts for the Knot kernel (Phase 3).

Contracts are optional type-level annotations (spec D3/D7):
  requires   — preconditions on inputs (name -> Type)
  guarantees — postconditions on the result (name -> Type)
  ensures    — input/result relations (stored; checked lightly in Phase 3)

Violations are reported as False (errors-as-values wiring is Phase 5).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .env import Env
from .types import Type, subtype, unify


@dataclass(frozen=True)
class ContractAnnotation:
    """Name -> expected Type bindings for one contract clause."""

    bindings: frozenset[tuple[str, Type]]

    def __init__(self, bindings: Mapping[str, Type] | None = None) -> None:
        items = frozenset((str(k), v) for k, v in (bindings or {}).items())
        object.__setattr__(self, "bindings", items)

    def as_dict(self) -> dict[str, Type]:
        return dict(self.bindings)

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and name in self.as_dict()

    def get(self, name: str) -> Type | None:
        return self.as_dict().get(name)

    def __len__(self) -> int:
        return len(self.bindings)

    def __bool__(self) -> bool:
        return bool(self.bindings)


@dataclass(frozen=True)
class Contract:
    """requires / guarantees / ensures (all optional; empty = no constraint)."""

    requires: ContractAnnotation = ContractAnnotation()
    guarantees: ContractAnnotation = ContractAnnotation()
    ensures: ContractAnnotation = ContractAnnotation()

    def __init__(
        self,
        requires: ContractAnnotation | Mapping[str, Type] | None = None,
        guarantees: ContractAnnotation | Mapping[str, Type] | None = None,
        ensures: ContractAnnotation | Mapping[str, Type] | None = None,
    ) -> None:
        object.__setattr__(self, "requires", _as_annotation(requires))
        object.__setattr__(self, "guarantees", _as_annotation(guarantees))
        object.__setattr__(self, "ensures", _as_annotation(ensures))


def _as_annotation(
    value: ContractAnnotation | Mapping[str, Type] | None,
) -> ContractAnnotation:
    if value is None:
        return ContractAnnotation()
    if isinstance(value, ContractAnnotation):
        return value
    return ContractAnnotation(value)


def check_requires(contract: Contract, env: Env) -> bool:
    """True iff every requires binding is present in Env and type-compatible.

    Compatibility: unify(actual, expected) is not None, or actual <: expected.
    """
    if not isinstance(contract, Contract):
        raise TypeError("check_requires expects a Contract")
    if not isinstance(env, Env):
        raise TypeError("check_requires expects an Env")
    for name, expected in contract.requires.bindings:
        actual = env.lookup(name)
        if actual is None:
            return False
        if unify(actual, expected) is None and not subtype(actual, expected):
            return False
    return True


def check_guarantees(contract: Contract, result_type: Type) -> bool:
    """True iff result_type satisfies every guarantees binding.

    Named keys (e.g. \"result\") all constrain the same result_type in Phase 3.
    Empty guarantees always succeed.
    """
    if not isinstance(contract, Contract):
        raise TypeError("check_guarantees expects a Contract")
    if not isinstance(result_type, Type):
        raise TypeError("check_guarantees expects a Type")
    for _name, expected in contract.guarantees.bindings:
        if unify(result_type, expected) is None and not subtype(
            result_type, expected
        ):
            return False
    return True
