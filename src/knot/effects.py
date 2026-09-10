"""Effects and capabilities for the Knot kernel (Phase 3).

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
