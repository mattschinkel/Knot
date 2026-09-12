"""Bytecode chunk: code + constants + names."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Chunk:
    code: list[int] = field(default_factory=list)
    constants: list[object] = field(default_factory=list)
    # debug: parallel line/op names optional later

    def emit(self, *bytes_: int) -> None:
        self.code.extend(int(b) for b in bytes_)

    def add_const(self, value: object) -> int:
        for i, c in enumerate(self.constants):
            if c == value and type(c) is type(value):
                return i
        self.constants.append(value)
        return len(self.constants) - 1

    def patch(self, at: int, value: int) -> None:
        self.code[at] = value

    def __len__(self) -> int:
        return len(self.code)
