"""Typed model/tool FFI (Phase 10): registry, invoke, constrain.

AI calls are effectful capabilities with contracts (design §11). Host
handlers are Python callables; the kernel never opens network sockets.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .ast import InvokeExpr, LitExpr, ModelDecl, ToolDecl
from .effects import Capability, CapabilitySet, check_capabilities
from .errors import StructuredError
from .types import BaseType, Type, UnitType, subtype
from .units import Dimension
from .values import AiResult, BoolVal, BytesVal, ErrorVal, IntVal, StringVal, UnitVal, Value


Handler = Callable[[tuple[Value, ...]], Value]


@dataclass
class _Entry:
    kind: str  # "model" | "tool"
    decl: ModelDecl | ToolDecl
    handler: Handler
    version: str = "0"


class ToolRegistry:
    """In-memory registry of MODEL/TOOL decls + host handlers."""

    def __init__(self) -> None:
        self._entries: dict[str, _Entry] = {}

    def register_model(
        self,
        decl: ModelDecl,
        handler: Handler,
        version: str = "0",
    ) -> ErrorVal | None:
        if "ai" not in decl.effects:
            return ErrorVal(
                StructuredError(
                    kind="model_effects",
                    message="MODEL EFFECTS must include ai",
                    op="MODEL",
                )
            )
        self._entries[decl.name] = _Entry("model", decl, handler, version)
        return None

    def register_tool(
        self,
        decl: ToolDecl,
        handler: Handler,
        version: str = "0",
    ) -> None:
        self._entries[decl.name] = _Entry("tool", decl, handler, version)

    def lookup(self, name: str) -> _Entry | None:
        return self._entries.get(name)

    def names(self) -> list[str]:
        return sorted(self._entries)


def type_from_air(type_str: str) -> Type:
    """Map AIR type atom (i32, string, f64@meters, ...) to a Type."""
    s = str(type_str).strip()
    if "@" in s:
        base, dim = s.split("@", 1)
        return UnitType(BaseType(base), Dimension.from_map({dim: 1}))
    return BaseType(s)


def effects_to_caps(effect_names: list[str]) -> CapabilitySet:
    """Map effect name strings to CapabilitySet (unknown names skipped)."""
    caps: list[Capability] = []
    for n in effect_names:
        try:
            caps.append(Capability(n))
        except ValueError:
            continue
    return CapabilitySet(caps)


def constrain(value: Value, declared_out: str) -> Value:
    """Validate handler output against declared OUT type (D5 / Tier 2 #33)."""
    if isinstance(value, ErrorVal):
        return value
    if isinstance(value, AiResult):
        inner = constrain(value.value, declared_out)
        if isinstance(inner, ErrorVal):
            return inner
        return AiResult(
            value=inner,
            confidence=value.confidence,
            model=value.model,
            version=value.version,
        )
    expected = type_from_air(declared_out)
    actual = value.type
    if actual is None or not subtype(actual, expected):
        return ErrorVal(
            StructuredError(
                kind="constrain",
                message="AI/tool output does not match declared OUT",
                expected=expected,
                got=actual,
                op="INVOKE",
            )
        )
    return value


def lit_to_value(node) -> Value:
    """Lower a simple LitExpr / TypedLit-ish AST atom to a Value for invoke args."""
    if isinstance(node, Value):
        return node
    if isinstance(node, LitExpr):
        v = node.value
        if isinstance(v, bool):
            return BoolVal(v)
        if isinstance(v, int):
            return IntVal(32, v)
        if isinstance(v, str):
            return StringVal(v)
        if v is None:
            return UnitVal()
        if isinstance(v, bytes):
            return BytesVal(v)
        if isinstance(v, float):
            from .values import FloatVal

            return FloatVal(64, v)
    return ErrorVal(
        StructuredError(kind="invoke_arg", message="unsupported INVOKE arg", op="INVOKE")
    )


def invoke(
    registry: ToolRegistry,
    name: str,
    args: list | tuple,
    granted: CapabilitySet | None = None,
) -> Value:
    """Run a registered MODEL/TOOL with capability check + output constrain."""
    granted = granted or CapabilitySet()
    entry = registry.lookup(name)
    if entry is None:
        return ErrorVal(
            StructuredError(
                kind="unknown_invoke",
                message="no MODEL/TOOL named " + name,
                op="INVOKE",
            )
        )
    needed = effects_to_caps(list(entry.decl.effects))
    if not check_capabilities(needed, granted):
        return ErrorVal(
            StructuredError(
                kind="capability",
                message="missing capabilities for " + name,
                op="INVOKE",
            )
        )
    vals: list[Value] = []
    for a in args:
        v = lit_to_value(a) if not isinstance(a, Value) else a
        if isinstance(v, ErrorVal):
            return v
        vals.append(v)
    raw = entry.handler(tuple(vals))
    if not isinstance(raw, Value):
        return ErrorVal(
            StructuredError(
                kind="handler",
                message="handler must return Value",
                op="INVOKE",
            )
        )
    constrained = constrain(raw, entry.decl.out_type)
    if isinstance(constrained, ErrorVal):
        return constrained
    if entry.kind == "model":
        conf = None
        if isinstance(entry.decl, ModelDecl) and entry.decl.confidence:
            if isinstance(constrained, AiResult):
                return constrained
            # Handler returned bare Value; wrap with default confidence 1.0
            return AiResult(
                value=constrained,
                confidence=1.0,
                model=entry.decl.name,
                version=entry.version,
            )
        if isinstance(constrained, AiResult):
            return AiResult(
                value=constrained.value,
                confidence=None,
                model=entry.decl.name,
                version=entry.version,
            )
        return AiResult(
            value=constrained,
            confidence=None,
            model=entry.decl.name,
            version=entry.version,
        )
    # tool: strip accidental AiResult wrapper
    if isinstance(constrained, AiResult):
        return constrained.value
    return constrained


def invoke_expr(
    registry: ToolRegistry,
    expr: InvokeExpr,
    granted: CapabilitySet | None = None,
) -> Value:
    """Invoke from an InvokeExpr AST node."""
    return invoke(registry, expr.name, expr.args, granted)


def make_openai_compatible_handler(
    *,
    base_url: str = "http://127.0.0.1:8081/v1",
    model: str = "local",
    api_key: str = "local",
    timeout_s: float = 60.0,
) -> Handler:
    """Live MODEL handler via OpenAI-compatible HTTP (LAN; no HTTPS required).

    Expects args[0] to be a StringVal prompt; returns AiResult(StringVal, confidence).
    """
    import json
    import urllib.error
    import urllib.request

    def handler(args: tuple[Value, ...]) -> Value:
        if not args or not isinstance(args[0], StringVal):
            return ErrorVal(
                StructuredError(
                    kind="handler",
                    message="openai handler expects StringVal prompt",
                    op="MODEL",
                )
            )
        prompt = args[0].value
        url = base_url.rstrip("/") + "/chat/completions"
        body = json.dumps(
            {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + api_key,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as e:
            return ErrorVal(
                StructuredError(
                    kind="llm",
                    message=str(e),
                    op="MODEL",
                )
            )
        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            return ErrorVal(
                StructuredError(
                    kind="llm",
                    message="unexpected LLM response shape",
                    op="MODEL",
                )
            )
        return AiResult(value=StringVal(str(text)), confidence=1.0, model=model)

    return handler
