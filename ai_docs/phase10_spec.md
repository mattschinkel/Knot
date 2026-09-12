# Phase 10 Spec — AI / Tool Capabilities

> Owner: Cursor. Decisions follow `ai_docs/axiom_design.md` §11, §16 Phase 10, Tier 2 #32–33.  
> Status: DECIDED — done.

Phase 10 adds **typed model and tool declarations**, **INVOKE** with runtime
capability granting, **AiResult** confidence metadata (ai-effectful only), and
**output constrained** to the declared return type. The deterministic kernel
still never invents confidence; only MODEL invokes do.

---

## 1. Scope

### In Phase 10
- Canonical AIR:
  - `MODEL[name,IN[type],OUT[type],CONF[true|false],EFFECTS[eff...]]`
  - `TOOL[name,IN[type],OUT[type],EFFECTS[eff...]]`
  - `INVOKE[name,arg...]`
- AST: `ModelDecl`, `ToolDecl`, `InvokeExpr`
- Value: `AiResult { value, confidence, model, version }`
- `ToolRegistry`: register MODEL/TOOL + host handlers; `invoke` + `constrain`
- Capability check via Phase 3 `check_capabilities` before invoke
- Parse + `print_canonical`
- Drift phase bump to 10 (M1–M5 unchanged)

### Explicitly OUT of Phase 10
- Real LLM HTTP calls (host handler stubs only; MCP/--llm is Phase 12)
- GPU effect category (map to `ai` for v1)
- Pretty-view `model name { ... }` sugar
- Confidence-tagged deploy policy (Tier 3 #37)

---

## 2. Design decisions (DECIDED)

### D1 — MODEL shape
**DECISION:** `MODEL[name,IN[T],OUT[U],CONF[bool],EFFECTS[...]]`. EFFECTS must include `ai`. CONF controls whether `AiResult.confidence` is populated.

### D2 — TOOL shape
**DECISION:** `TOOL[name,IN[T],OUT[U],EFFECTS[...]]`. No CONF (tools are not ai-effectful). Effects map 1:1 to capability names.

### D3 — INVOKE
**DECISION:** `INVOKE[name,arg...]` looks up MODEL or TOOL in the registry. Missing name → `ErrorVal(kind=unknown_invoke)`. Capability shortfall → `ErrorVal(kind=capability)`.

### D4 — AiResult
**DECISION:** MODEL success returns `AiResult`. TOOL success returns the constrained value directly (no confidence wrapper). Kernel ops never construct `AiResult`.

### D5 — Constrain
**DECISION:** Handler output is validated with `subtype(actual.type, declared_OUT)`. Mismatch → `ErrorVal(kind=constrain)`.

### D6 — Handlers
**DECISION:** Registry binds Python callables for tests/host. No network in kernel.

### D7 — Drift
**DECISION:** Phase 10 baseline; metrics M1–M5 unchanged from Phase 9.

---

## 3. File layout

```
src/knot/
  ai_ffi.py       # ToolRegistry, invoke, constrain, type_from_air
  values.py       # AiResult
  ast.py          # ModelDecl, ToolDecl, InvokeExpr
  parser.py
  canonical.py
tests/ai_ffi/
  test_parse_ai.py
  test_ai_registry.py
  test_invoke.py
  test_constrain.py
  test_ai_prop.py
```

---

## 4. Definition of done

- [x] Spec decided
- [x] Parse/canonical MODEL/TOOL/INVOKE
- [x] Registry + capability-gated invoke
- [x] AiResult + constrain
- [x] Tests + drift phase 10

---

## 5. Tasks

| ID | Goal | File | Symbol | Test |
|----|------|------|--------|------|
| T1 | AST + parse/canonical | ast/parser | ModelDecl | test_parse_ai.py |
| T2 | AiResult value | values.py | AiResult | test_invoke.py |
| T3 | ToolRegistry register | ai_ffi.py | ToolRegistry | test_ai_registry.py |
| T4 | invoke + caps | ai_ffi.py | invoke | test_invoke.py |
| T5 | constrain + drift | ai_ffi.py | constrain | test_constrain.py |
