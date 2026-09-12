# Phase 1 Spec — AST + Parser + GBNF Grammar (Golem kernel, Python host)

> Owner: R1 Architect (decides autonomously). Implementation: R2 Kernel Engineer. Verification: R4 Verifier. Human observes via progress.md (non-blocking); R1 makes all decisions.  
> Status: DECIDED by R1 (autonomous) — implemented; tests green (Phase 1 closed 2026-09-09).

Phase 1 builds the **AST model** and the **canonical text parser**. It introduces **node IDs**, **structural paths**, and **symbolic labels** as the LLM's addressing scheme. The phase delivers a constrained-decoding GBNF grammar that ensures only valid syntax can be emitted by the LLM. This is the foundation for Phase 2's type checker and beyond.

Per the resolved decisions (`golem_agents.md` §5): host language is **Python**; R1 decides autonomously; shell is autonomous (whitelisted build/test); repo layout is `src/golem/`, `src/golem/ai/`, `tests/`, `cli/`, `lsp/`, `fmt/`, `grammar/`, `vm/`, `docs/`.

## 1. Scope

### In Phase 1
- AST node model with **numeric IDs** (`src/golem/ast.py`)
- Canonical text parser (bracket form) (`src/golem/parser.py`)
- Pretty printer (`src/golem/printer.py`)
- Binary serializer (`src/golem/bin.py`)
- GBNF grammar for constrained-decoding (Phase 1) (`src/golem/grammar/gbnf.py`)
- Node addressing: structural paths and symbolic labels (`src/golem/addressing.py`)
- Property tests for all AST/serialization (`tests/ast/`, `tests/bin/`, `tests/grammar/`)

### Explicitly OUT of Phase 1
- Type *checker* (unification, inference) — Phase 2
- Effects, capabilities, contracts — Phase 3
- Holes, partial typing — Phase 4
- Structured errors — Phase 5
- Edit operations — Phase 6
- Tests / properties — Phase 7
- Modules + dependencies — Phase 8
- Compiler / VM — Phase 9
- AI / tool capabilities — Phase 10
- Concurrency — Phase 11
- MCP server / `kb` retrieval — Phase 12

## 2. Design decisions (DECIDED by R1)

These are the choices R1 has made. Each is reversible but locking them now keeps Phase 2+ stable. Each decision is FINAL, recorded by R1.

- **D1 — AST nodes have numeric IDs.** Each node gets a unique numeric ID at parse time. IDs are stable within a session, used in diagnostics, blast-radius, and GBNF grammar. The LLM may read IDs from diagnostics but never writes them into source. Rationale: enables constrained decoding (GBNF grammar enforces unique IDs), supports multi-editor scenarios where numeric IDs survive rewrites, and provides stable references for diagnostics.
- **D2 — Structural path addressing is primary.** Nodes are addressed by structural path (e.g., `eligible.body.args[1]`) from named anchors. This is the default for LLM queries and edits. Rationale: path-based addressing survives optimization; it's stable, composable, and familiar to LLMs from JSON/JS.
- **D3 — Symbolic labels are optional, sparse, and module-local.** The LLM may label nodes with `@label` (e.g., `@guard GE[GET[u, age], 18]`). Labels are unique within a module, survive optimization, and are used for edit targeting. Rationale: enables edit operations to target specific nodes without numeric IDs; labels are sparse (not every node gets one) to avoid clutter.
- **D4 — Canonical form is bracket notation.** All expressions are written as `OP[arg1, arg2, ...]`. The shorter `F(...)` shorthand is NOT canonical; it is only used in pretty printing. Rationale: consistent, unambiguous syntax; the bracket form is the only form the LLM emits; it enables deterministic parsing.
- **D5 — GBNF grammar contains NO numeric IDs.** Numeric IDs are compiler-internal (D7) and never appear in source the LLM emits, so the GBNF grammar has no ID token at all. Rationale: avoids ID collisions/gaps/off-by-one in emitted syntax; IDs are assigned by the parser at parse time. This is consistent with §21 (addressing is paths + labels).
- **D6 — AST is immutable after parse.** Once parsed, the AST is frozen; edits produce new nodes, never mutate in place. Rationale: stable node identity + cheap sharing + no aliasing bugs in the deterministic kernel.
- **D7 — Node IDs are compiler-internal, not author-pinned.** The LLM may read numeric IDs from diagnostics but never writes them into source. Rationale: avoids numeric ID collisions, gaps, and off-by-one errors; numeric IDs survive optimization; author-pinned IDs break multi-editor consistency.

## 3. AST node model (`src/golem/ast.py`)

Every expression is a node. Nodes have a numeric ID, a structural path, and optional labels.

```
Node (abstract)
├─ ExprNode       (id: int, path: str, label: str | None)
│   ├─ LitExpr     (value: Value, type: Type | None)
│   ├─ TypedLit    (value: Value, type: Type)
│   ├─ IdentExpr   (name: str)
│   ├─ FieldAccess (obj: Expr, field: str)
│   ├─ GetExpr     (obj: Expr, field: str)
│   ├─ SetExpr     (obj: Expr, field: str, val: Expr)
│   ├─ OpExpr      (op: str, args: tuple[Expr,...])
│   ├─ IfExpr      (cond: Expr, then: Expr, else: Expr)
│   ├─ CondExpr    (cond: Expr, cases: tuple[Expr,...])
│   ├─ MatchExpr   (pattern: Expr, arms: tuple[Arm,...])
│   ├─ LetExpr     (name: str, val: Expr, body: Expr)
│   ├─ WithExpr    (name: str, val: Expr, body: Expr)
│   ├─ HoleExpr    (expected: Type | None)        # D3
│   ├─ FnExpr      (name: str, params: tuple[Param,...], body: Expr)
│   ├─ CallExpr    (func: Expr, args: tuple[Expr,...])
│   └─ UnitExpr
├─ TypeNode       (id: int, path: str, label: str | None)
│   ├─ BaseType
│   ├─ NominalType
│   ├─ OptionType
│   ├─ ListType
│   ├─ SetType
│   ├─ MapType
│   ├─ TupleType
│   ├─ SumType
│   ├─ CapIntersect
│   ├─ UnitType
│   └─ RegionType
├─ DefNode         (id: int, path: str, label: str | None)
│   └─ DefBody      (name: str, expr: Expr)
└─ TypeDefNode     (id: int, path: str, label: str | None)
    └─ TypeDefBody  (name: str, type: Type)
```

Notes:
- Each node has a unique `id` (int), `path` (str), and optional `label` (str).
- `ExprNode` and `TypeNode` are the only nodes that can have `label`; `DefNode` and `TypeDefNode` inherit label from their path.
- `HoleExpr` is an expression node with optional expected type; it is not a separate AST flag but a value embedded in the AST.
- The AST is frozen after parse; edits produce new nodes.

## 4. Canonical text parser (`src/golem/parser.py`)

Parses input into AST nodes. Input is bracket notation: `OP[arg1, arg2, ...]`.

### Grammar (BNF)
```
Program     = Def* EOF
Def         = Name "=" Expr
Expr        = Lit | Ident | FieldAccess | Get | Set | Op | If | Cond | Match | Let | With | Hole | Fn | Call | Unit
Lit         = Number | String | Bool | Nil | TypedLit
Ident       = Identifier
FieldAccess = Ident "." Ident
Get         = "GET[" Ident "," Ident "]"
Set         = "SET[" Ident "," Ident "," Expr "]"
Op          = "ADD" | "SUB" | "MUL" | "DIV" | "MOD" | "NEG"
Comparison  = "EQ" | "NE" | "LT" | "LE" | "GT" | "GE"
Logic       = "AND" | "OR" | "NOT"
Control     = "IF" | "COND" | "MATCH"
Access      = "GET" | "SET" | "FIELD"
Collection  = "MAP" | "FILTER" | "REDUCE" | "FOLD" | "LEN" | "AT" | "APPEND" | "CONCAT"
Binding     = "LET" | "WITH"
Hole        = "?" | "?:Type"
Function    = "FN" "(" ParamList ")" Body
ParamList   = Param ("," Param)*
Param       = Ident ":" Type
Body        = Expr
Unit        = "UNIT"
```

### Features
- Bracket notation is the only canonical form; `F(...)` is not canonical.
- Handles type annotations on literals: `2:i32`, `10:meters`.
- Handles field access sugar: `user.name` → `GET[user, name]`.
- Handles holes: `?` or `?:i32`.
- Handles function definitions: `def square = FN[x:i32] MUL[x, x]`.
- Returns AST with numeric IDs and structural paths.

## 5. Pretty printer (`src/golem/printer.py`)

Generates human-readable code from AST. Output is not the source of truth.

### Output format
```
fn square(x: i32) -> i32 { x * x }
```

### Rules
- Function definitions: `fn name(params) -> ret { body }`
- Parameters: `x: i32`
- Body: `{ ... }`
- Expressions: no parentheses unless needed for grouping
- Type annotations: only on parameters and return
- No bracket notation; only `F(...)` shorthand is used in pretty printing

### Notes
- Pretty printing is a view; the canonical form is bracket notation.
- The printer does not emit holes; holes are represented as `?` in the AST.

## 6. Binary serializer (`src/golem/bin.py`)

Serializes AST to a binary format with node IDs. Used for storage and tool IPC.

### Format
- Header: version (4 bytes), node count (4 bytes)
- Nodes: node ID, type, path, label, payload (varies by node type)
- Index: map from ID to offset

### Features
- Supports round-trip: parse → binary → parse
- Node IDs are stable within a session
- Supports multi-editor scenarios

## 7. GBNF grammar (`src/golem/grammar/gbnf.py`)

Enforces constrained decoding: only valid syntax can be emitted by the LLM.

### Grammar
```
Program     = Def* EOF
Def         = Name "=" Expr
Expr        = Lit | Ident | FieldAccess | Get | Set | Op | If | Cond | Match | Let | With | Hole | Fn | Call | Unit
Lit         = Number | String | Bool | Nil | TypedLit
Ident       = Identifier
FieldAccess = Ident "." Ident
Get         = "GET[" Ident "," Ident "]"
Set         = "SET[" Ident "," Ident "," Expr "]"
Op          = "ADD" | "SUB" | "MUL" | "DIV" | "MOD" | "NEG"
Comparison  = "EQ" | "NE" | "LT" | "LE" | "GT" | "GE"
Logic       = "AND" | "OR" | "NOT"
Control     = "IF" | "COND" | "MATCH"
Access      = "GET" | "SET" | "FIELD"
Collection  = "MAP" | "FILTER" | "REDUCE" | "FOLD" | "LEN" | "AT" | "APPEND" | "CONCAT"
Binding     = "LET" | "WITH"
Hole        = "?" | "?:Type"
Function    = "FN" "(" ParamList ")" Body
ParamList   = Param ("," Param)*
Param       = Ident ":" Type
Body        = Expr
Unit        = "UNIT"
```

### Constraints
- Every node ID must be unique and must not be an arbitrary integer
- Bracket notation is the only canonical form
- `F(...)` shorthand is not allowed in GBNF
- All expressions must be bracketed

## 8. File layout

```
src/golem/
├── ast.py           # AST node model
├── bin.py           # Binary serializer
├── grammar/
│   └── gbnf.py      # GBNF grammar for constrained decoding
├── parser.py        # Canonical text parser
├── printer.py       # Pretty printer
└── addressing.py    # Node addressing: paths, labels, IDs
```

## 9. Definition of done

- [x] AST node model with numeric IDs and structural paths
- [x] Canonical text parser (bracket notation)
- [x] Pretty printer (human-readable view)
- [x] Binary serializer (round-trip to AST)
- [x] GBNF grammar with constraints (bracket notation; no numeric IDs — D5)
- [x] All property tests pass
- [x] All tests pass on Python 3.10+

## 10. Resolved sub-questions (DECIDED by R1)

- **Q1 — Structural path syntax:** Dot/bracket (`eligible.body.args[1]`) — familiar to LLMs from JSON/JS. Rationale: consistent with JSON/JS path syntax; supports nested structures; enables structural pattern matching.
- **Q2 — Multiple matches:** When a structural path matches several nodes after a refactor, the compiler returns all matches and requires the LLM to disambiguate. Rationale: prevents incorrect edits; enables multi-editor consistency; requires unique matches for edits.
- **Q3 — Label scoping:** Module-local; `Module.label` to cross modules. Rationale: avoids global label conflicts; enables cross-module editing; supports module-level labels.
- **Q4 — Auto-labeling:** Whether the compiler suggests labels for nodes the LLM edits frequently. Later. Rationale: not needed in Phase 1; auto-labeling is a feature for Phase 6+.
- **Q5 — Node ID uniqueness:** GBNF grammar enforces unique numeric IDs. Rationale: prevents collisions, gaps, off-by-one errors; enables constrained decoding; ensures valid syntax only.