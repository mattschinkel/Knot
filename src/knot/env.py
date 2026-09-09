"""Scoped type environment for the Knot type checker (Phase 2)."""

from __future__ import annotations

from .types import Type


class Env:
    """Nested scopes binding names to types.

    Spec: Env = dict[str, Type] with enter_scope / leave_scope.
    Lookup walks outward from the innermost scope.
    """

    def __init__(self) -> None:
        self._scopes: list[dict[str, Type]] = [{}]
        self._scope_names: list[str] = ["<root>"]

    def enter_scope(self, name: str = "") -> None:
        self._scopes.append({})
        self._scope_names.append(name or f"<scope{len(self._scopes)}>")

    def leave_scope(self) -> None:
        if len(self._scopes) <= 1:
            raise RuntimeError("cannot leave the root scope")
        self._scopes.pop()
        self._scope_names.pop()

    def bind(self, name: str, typ: Type) -> None:
        self._scopes[-1][name] = typ

    def lookup(self, name: str) -> Type | None:
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        return None

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and self.lookup(name) is not None
