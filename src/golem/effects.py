"""Effects and capabilities for the Golem kernel (Phase 3).

Effects are first-class type-level sets (spec D1). Capabilities are
runtime-grantable permissions checked structurally (spec D2/D5).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class EffectCategory(Enum):
    """Kernel effect categories (phase3_spec §1)."""

    PURE = "pure"
    FS_READ = "fs.read"
    FS_WRITE = "fs.write"
    FS_DELETE = "fs.delete"
    NET_REQUEST = "net.request"
    DB_READ = "db.read"
    DB_WRITE = "db.write"
    IO_STDOUT = "io.stdout"
    IO_STDERR = "io.stderr"
    TIME_NOW = "time.now"
    RANDOM = "random"
    AI = "ai"
    UNSAFE = "unsafe"


@dataclass(frozen=True)
class EffectSet:
    """Immutable set of EffectCategory values."""

    effects: frozenset[EffectCategory]

    def __init__(self, effects: Iterable[EffectCategory] | None = None) -> None:
        object.__setattr__(
            self,
            "effects",
            frozenset(effects or ()),
        )

    def __contains__(self, item: object) -> bool:
        return item in self.effects

    def __iter__(self):
        return iter(self.effects)

    def __len__(self) -> int:
        return len(self.effects)

    def __bool__(self) -> bool:
        return bool(self.effects)

    def union(self, other: EffectSet) -> EffectSet:
        return EffectSet(self.effects | other.effects)

    def intersection(self, other: EffectSet) -> EffectSet:
        return EffectSet(self.effects & other.effects)

    def issubset(self, other: EffectSet) -> bool:
        return self.effects <= other.effects

    def is_pure(self) -> bool:
        return not self.effects or self.effects == frozenset({EffectCategory.PURE})


PURE = EffectSet()


class Capability(Enum):
    """Runtime-grantable permissions (phase3_spec D2)."""

    FS_READ = "fs.read"
    FS_WRITE = "fs.write"
    FS_DELETE = "fs.delete"
    NET_REQUEST = "net.request"
    DB_READ = "db.read"
    DB_WRITE = "db.write"
    IO_STDOUT = "io.stdout"
    IO_STDERR = "io.stderr"
    TIME_NOW = "time.now"
    RANDOM = "random"
    AI = "ai"
    UNSAFE = "unsafe"


@dataclass(frozen=True)
class CapabilitySet:
    """Immutable set of Capability values."""

    caps: frozenset[Capability]

    def __init__(self, caps: Iterable[Capability] | None = None) -> None:
        object.__setattr__(self, "caps", frozenset(caps or ()))

    def __contains__(self, item: object) -> bool:
        return item in self.caps

    def __iter__(self):
        return iter(self.caps)

    def __len__(self) -> int:
        return len(self.caps)

    def __bool__(self) -> bool:
        return bool(self.caps)

    def union(self, other: CapabilitySet) -> CapabilitySet:
        return CapabilitySet(self.caps | other.caps)

    def intersection(self, other: CapabilitySet) -> CapabilitySet:
        return CapabilitySet(self.caps & other.caps)

    def issubset(self, other: CapabilitySet) -> bool:
        return self.caps <= other.caps


def compose_effects(*sets: EffectSet) -> EffectSet:
    """Union of effect sets (phase3_spec D4). Empty args → pure."""
    out = EffectSet()
    for s in sets:
        if not isinstance(s, EffectSet):
            raise TypeError("compose_effects expects EffectSet arguments")
        out = out.union(s)
    return out


def check_capabilities(needed: CapabilitySet, granted: CapabilitySet) -> bool:
    """True iff every needed capability is in the granted set (D5)."""
    return needed.issubset(granted)


def _effects_to_capabilities(effects: EffectSet) -> CapabilitySet:
    """Map non-pure effect categories to same-named capabilities."""
    caps: list[Capability] = []
    for eff in effects:
        if eff is EffectCategory.PURE:
            continue
        try:
            caps.append(Capability(eff.value))
        except ValueError:
            # Unknown effect name has no matching capability token.
            continue
    return CapabilitySet(caps)


def validate_call_effects(fn_type: object, granted: CapabilitySet) -> bool:
    """True iff call-site granted capabilities cover the function's needs (D5/D8).

    Needed set = FnType.caps union capabilities implied by FnType.effects
    (excluding pure). Empty needs always succeed.
    """
    # Local import avoids types↔effects cycle at module load for annotate-only use.
    from .types import FnType

    if not isinstance(fn_type, FnType):
        raise TypeError("validate_call_effects expects a FnType")
    if not isinstance(granted, CapabilitySet):
        raise TypeError("validate_call_effects expects a CapabilitySet")
    needed = fn_type.caps.union(_effects_to_capabilities(fn_type.effects))
    return check_capabilities(needed, granted)
