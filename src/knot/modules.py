"""Modules, imports, depends (Phase 8)."""

from __future__ import annotations

from dataclasses import dataclass, field

from .ast import (
    DefNode,
    DependsDecl,
    ImportDecl,
    InlineTest,
    ModuleDecl,
    PropertyDecl,
)
from .effects import Capability, CapabilitySet, check_capabilities
from .errors import StructuredError
from .values import ErrorVal


@dataclass
class ModuleRegistry:
    """In-memory module store (Phase 8 D4)."""

    _mods: dict[str, ModuleDecl] = field(default_factory=dict)

    def register(self, module: ModuleDecl, version: str | None = None) -> None:
        if not isinstance(module, ModuleDecl):
            raise TypeError("register expects ModuleDecl")
        if version is not None:
            module = ModuleDecl(
                module.name,
                module.body,
                module.exports,
                version=version,
                id=module.id,
            )
        self._mods[module.name] = module

    def get(self, name: str) -> ModuleDecl | None:
        return self._mods.get(name)

    def __contains__(self, name: object) -> bool:
        return isinstance(name, str) and name in self._mods

    def names(self) -> list[str]:
        return sorted(self._mods)


@dataclass(frozen=True)
class LinkedProgram:
    """Flat list of defs/tests/props after import resolution."""

    items: tuple
    imports: tuple[ImportDecl, ...] = ()
    depends: tuple[DependsDecl, ...] = ()


def exported_defs(module: ModuleDecl) -> dict[str, DefNode]:
    """Map export name -> DefNode (only DEFs are linkable call targets)."""
    defs = {
        str(item.name): item
        for item in module.body
        if isinstance(item, DefNode)
    }
    out: dict[str, DefNode] = {}
    for name in module.exports:
        if name in defs:
            out[name] = defs[name]
    return out


def check_depends(
    depends: list[DependsDecl] | tuple[DependsDecl, ...],
    registry: ModuleRegistry,
    granted: CapabilitySet | None = None,
) -> ErrorVal | None:
    """Validate DEPENDS entries; return ErrorVal on failure else None."""
    granted = granted if granted is not None else CapabilitySet()
    for dep in depends:
        mod = registry.get(dep.module)
        if mod is None:
            return ErrorVal(
                StructuredError(
                    kind="depends",
                    message="unknown module " + dep.module,
                )
            )
        if mod.version != dep.version:
            return ErrorVal(
                StructuredError(
                    kind="depends",
                    message=(
                        "version mismatch "
                        + dep.module
                        + ": need "
                        + dep.version
                        + " have "
                        + mod.version
                    ),
                )
            )
        if dep.caps:
            try:
                needed = _caps_from_names(dep.caps)
            except ValueError as e:
                return ErrorVal(
                    StructuredError(kind="depends", message=str(e))
                )
            if not check_capabilities(needed, granted):
                return ErrorVal(
                    StructuredError(
                        kind="depends",
                        message="missing capabilities for " + dep.module,
                    )
                )
    return None


def _caps_from_names(names: list[str]) -> CapabilitySet:
    caps = []
    for n in names:
        try:
            caps.append(Capability(n))
        except ValueError:
            # unknown token — treat as failure by using a fake empty and failing check
            # Proper: reject unknown capability names
            raise ValueError("unknown capability " + n)
    return CapabilitySet(caps)


def link_program(
    items: list | object,
    registry: ModuleRegistry,
    granted: CapabilitySet | None = None,
    *,
    _stack: tuple[str, ...] = (),
) -> LinkedProgram | ErrorVal:
    """Resolve IMPORT/DEPENDS; return flat LinkedProgram or ErrorVal.

    Cycles in MODULE→IMPORT of modules are detected when linking a ModuleDecl
    that imports another module which eventually imports back (via registry
    graph of IMPORT inside module bodies — Phase 8: imports are program-level).
    """
    seq = list(items) if isinstance(items, list) else [items]
    imports = [x for x in seq if isinstance(x, ImportDecl)]
    depends = [x for x in seq if isinstance(x, DependsDecl)]
    modules_inline = [x for x in seq if isinstance(x, ModuleDecl)]
    rest = [
        x
        for x in seq
        if not isinstance(x, (ImportDecl, DependsDecl, ModuleDecl))
    ]

    # Register inline modules
    reg = registry
    for m in modules_inline:
        reg.register(m)

    err = check_depends(depends, reg, granted)
    if err is not None:
        return err

    # Cycle detection on import graph among registered modules' names
    # (program imports only — track visiting set)
    visiting: set[str] = set(_stack)
    for imp in imports:
        if imp.module in visiting:
            return ErrorVal(
                StructuredError(
                    kind="import_cycle",
                    message="import cycle at " + imp.module,
                )
            )
        if imp.module not in reg:
            return ErrorVal(
                StructuredError(
                    kind="import",
                    message="unknown module " + imp.module,
                )
            )

    linked: list = list(rest)
    for imp in imports:
        mod = reg.get(imp.module)
        assert mod is not None
        available = exported_defs(mod)
        names = list(imp.names) if imp.names else list(mod.exports)
        for name in names:
            if name not in available:
                return ErrorVal(
                    StructuredError(
                        kind="import",
                        message=(
                            "module "
                            + imp.module
                            + " does not export "
                            + name
                        ),
                    )
                )
            # Skip duplicate def names already present
            if any(isinstance(x, DefNode) and x.name == name for x in linked):
                continue
            linked.append(available[name])
        # Also pull InlineTest/PropertyDecl that are exported? Only DEFs for now.
        # Re-export tests named in exports if present
        for item in mod.body:
            if isinstance(item, (InlineTest, PropertyDecl)) and item.name in names:
                if not any(
                    type(x) is type(item) and getattr(x, "name", None) == item.name
                    for x in linked
                ):
                    linked.append(item)

    return LinkedProgram(
        items=tuple(linked),
        imports=tuple(imports),
        depends=tuple(depends),
    )
