# Phase 12 Spec — MCP Server + kb + --llm Mode

> Owner: Cursor. Decisions follow `ai_docs/axiom_design.md` §16 Phase 12, Tier 2 #27–29, A2–A4.  
> Status: DECIDED — done.

Phase 12 exposes the compiler to agents: **MCP tools**, token-budgeted
**`kb`**, and **`--llm` output** with budget + policy. No HTTPS; stdio /
in-process only.

---

## 1. Scope

### In Phase 12
- MCP tool surface (in-process + stdio JSON-RPC, no HTTPS):
  - `eval` — parse + `evaluate`
  - `typecheck` — `compile_check` / status + type
  - `run` — `knot.vm.run`
  - `constrain` — `ai_ffi.constrain`
  - `doc_query` / `kb` — token-budgeted doc retrieval
  - `query` — graph inspection (path / children / op)
- `kb.retrieve(topic, max_tokens)` packing docs under a token cap
- `--llm` formatter: policies `diagnostics_first` | `slices_first` |
  `balanced` | `minimal` with `budget_tokens`
- CLI: `python -m knot` subcommands (`mcp`, `kb`, `llm`, tools)
- Drift phase bump to 12 (M1–M5 unchanged)

### Explicitly OUT of Phase 12
- HTTPS / remote MCP transport
- Full MCP SDK dependency (we implement a minimal JSON tool protocol)
- Live LLM HTTP for doc generation
- Streaming SSE

---

## 2. Design decisions (DECIDED)

### D1 — Tools are pure dispatch
**DECISION:** Each tool is a function `(args: dict) -> dict`. Errors are
JSON `{ok:false, error:{kind,message}}`, never raised across the MCP boundary.

### D2 — Transport
**DECISION:** In-process `call_tool(name, args)` is primary. Stdio JSON lines
(`{"method":"tools/call","params":{...}}`) optional for agents. No HTTPS.

### D3 — Token estimate
**DECISION:** `estimate_tokens(text) = max(1, len(text)//4)` (chars/4). Stable, no tiktoken.

### D4 — kb corpus
**DECISION:** Built-in catalog of short cards (ops, phases, AIR rules) in
`src/knot/kb_data.py` + optional `docs/kb/*.md` overlay.

### D5 — --llm policies
**DECISION:**
- `diagnostics_first` — errors/repairs, then code slices if budget remains
- `slices_first` — canonical slices, then diagnostics
- `balanced` — alternate chunks
- `minimal` — one-line status + type if present

### D6 — Drift
**DECISION:** Phase 12 baseline; M1–M5 unchanged.

---

## 3. File layout

```
src/knot/
  kb.py / kb_data.py
  llm_out.py
  mcp/
    __init__.py
    tools.py
    server.py
  __main__.py
tests/mcp/
  test_tools.py
  test_kb.py
  test_llm_out.py
  test_server.py
  test_mcp_prop.py
```

---

## 4. Definition of done

- [x] Spec decided
- [x] Six tools + kb + --llm formatter
- [x] In-process + stdio dispatch
- [x] CLI entry
- [x] Tests + drift phase 12

---

## 5. Tasks

| ID | Goal | File | Symbol | Test |
|----|------|------|--------|------|
| T1 | MCP tools | mcp/tools.py | call_tool | test_tools.py |
| T2 | kb retrieve | kb.py | retrieve | test_kb.py |
| T3 | --llm format | llm_out.py | format_for_llm | test_llm_out.py |
| T4 | server + CLI | mcp/server.py | handle_line | test_server.py |
| T5 | props + drift | baseline | — | test_mcp_prop.py |
