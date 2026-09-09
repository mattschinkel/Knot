# Phase 1 Spec — AST + Parser + GBNF Grammar (Knot kernel, Python host)

> Owner: R1 Architect (decides autonomously). Implementation: R2 Kernel
> Engineer. Verification: R4 Verifier. Human observes via the dashboard
> (non-blocking); R1 makes all decisions.
> Status: DRAFT for human review — no implementation code yet.

Phase 1 builds the **AST + parser + GBNF grammar** for the Knot kernel. It defines the node model with IDs, the canonical text parser, pretty printer, and binary serializer. The GBNF grammar is constrained to enforce valid syntax for the LLM to emit. This is the first phase where the LLM directly writes source text.

Per the resolved decisions (`knot_agents.md` §5): host language is **Python**; R1 is a **peer** that drafts; shell is **gated**; repo layout is `src/knot/`, `src/knot/ai/`, `tests/`, `cli/`, `lsp/`, `fmt/`, `grammar/`, `vm/`, `docs/`.

## 1. Scope

### In Phase 1
- AST node model (`src/knot/ast.py`) — full node hierarchy with numeric IDs
- Canonical text parser (`src/knot/parser.py`) — bracket form, GBNF grammar
- Pretty printer (`src/knot/pretty.py`) — human-readable view
- Binary serializer (`src/knot/bin.py`) — node IDs, graph serialization
- GBNF grammar (`src/knot/grammar/gbnf.py`) — constrained-decoding grammar for AIR
- Property tests for all modules (`tests/`)

### Explicitly OUT of Phase 1
- Type *checker* (unification, inference) — Phase 2
- Effects, capabilities, contracts — Phase 3
- Holes, partial compile — Phase 4
- Structured errors — Phase 5
- Edit operations — Phase 6
- Modules, dependencies — Phase 8
- Compiler / VM — Phase 9
- AI / tool capabilities — Phase 10
- Concurrency — Phase 11

## 2. Design decisions to confirm (human)

These are the choices R1 is putting forward. Each is reversible but locking them now keeps Phase 2+ stable. **Please confirm or amend.**

- **D1 — Numeric IDs in AST.** AST nodes have a `node_id` (int) field. This is the **only** numeric ID in the model; all other IDs (labels, paths) are structural or symbolic. Rationale: enables constrained decoding (GBNF grammar), stable node identity for the LLM to write, and supports edit operations.  
- **D2 — Bracket notation is canonical.** All LLM output is bracket form: `OP[arg1, arg2, ...]`. The shorthand `F(...)` is **not** canonical — it is a pretty-printer artifact. The GBNF grammar must enforce bracket form.  
- **D3 — GBNF grammar is constrained.** The grammar must reject any output that contains numeric IDs, arbitrary integers, or malformed syntax. Only bracket-form expressions are valid. This ensures the LLM cannot emit invalid syntax.  
- **D4 — Node labels are symbolic, not numeric.** The `@` syntax is a **label**, not a numeric ID. Labels are sparse, module-local, and survive optimization. The LLM may write labels to mark nodes for editing.  
- **D5 — Structural path syntax: dot/bracket.** Paths use `.` and `[]` (e.g., `eligible.body.args[1]`) — familiar to LLMs from JSON/JS. This is the primary path syntax.  
- **D6 — Multiple matches: compiler returns all, LLM disambiguates.** When a path matches multiple nodes, the compiler returns all candidates; the LLM must disambiguate in edits.  
- **D7 — Label scoping: module-local.** Labels are unique within a module; `Module.label` syntax is reserved for cross-module labels.  
- **D8 — Binary format includes node IDs.** The serialized graph uses numeric IDs for IPC and storage; the binary format is separate from the AST but round-trips to the same graph.

## 3. AST node model (`src/knot/ast.py`)

Every expression is a node. The AST is a directed acyclic graph (DAG) with numeric IDs.

```
Node (abstract)
├─ Expr (abstract)
│  ├─ Lit (value: Value, type: Type)
│  ├─ TypedLit (value: Value, type: Type)
│  ├─ Ident (name: str, type: Type)
│  ├─ FieldAccess (obj: Expr, field: str)
│  ├─ Hole (expected: Type | None)
│  ├─ Op (op: str, args: tuple[Expr,...])
│  ├─ If (cond: Expr, then: Expr, else: Expr)
│  ├─ Match (discrim: Expr, arms: dict[str, Expr])
│  ├─ Let (name: str, val: Expr, body: Expr)
│  ├─ With (name: str, val: Expr, body: Expr)
│  ├─ Fn (name: str, params: tuple[Param], body: Expr)
│  ├─ Call (func: Expr, args: tuple[Expr])
│  ├─ Get (obj: Expr, field: str)
│  ├─ Set (obj: Expr, field: str, val: Expr)
│  ├─ Field (obj: Expr, field: str)
│  ├─ Map (key: Expr, val: Expr)
│  ├─ Filter (pred: Expr, coll: Expr)
│  ├─ Reduce (init: Expr, func: Expr, coll: Expr)
│  ├─ Fold (init: Expr, func: Expr, coll: Expr)
│  ├─ Len (expr: Expr)
│  ├─ At (index: Expr, coll: Expr)
│  ├─ Append (left: Expr, right: Expr)
│  ├─ Concat (left: Expr, right: Expr)
│  └─ HOLE (expected: Type | None)
└─ Param (name: str, type: Type, default: Expr | None)
```

Each node has:
- `node_id` (int) — unique, stable within a session
- `parent_id` (int | None) — points to parent in DAG
- `label` (str | None) — symbolic label (D4)
- `path` (str | None) — structural path (e.g., `eligible.body.args[1]`)

## 4. Parser (`src/knot/parser.py`)

Parses bracket-form expressions into AST nodes.

**Input:** Bracket-form text (e.g., `ADD[2, 3]`, `FN[x:i32] MUL[x, x]`)

**Output:** AST nodes with `node_id` and `label`

**Rules:**
- All expressions are bracketed: `OP[arg1, arg2, ...]`
- No `F(...)` shorthand — only bracket form
- No numeric IDs in input
- GBNF grammar enforces bracket form and valid syntax

**Phase 1 delivers:**
- A parser that accepts bracket-form text and produces AST nodes
- The parser is **not** the LLM; it is a deterministic, non-LLM parser
- The parser is the **only** source of truth for canonical text

## 5. GBNF grammar (`src/knot/grammar/gbnf.py`)

Constrained-decoding grammar for the LLM to emit valid syntax.

**Rules:**
- All expressions must be bracketed: `OP[arg1, arg2, ...]`
- No numeric IDs
- No arbitrary integers
- No malformed syntax
- Only bracket-form expressions are valid

**Example:**
```
Expr ::= Lit | TypedLit | Ident | FieldAccess | HOLE
       | Op | If | Match | Let | With | Fn | Call
       | Get | Set | Field | Map | Filter | Reduce
       | Fold | Len | At | Append | Concat
       | HOLE

Lit ::= Int | Float | Bool | String | Bytes | Unit | Nil

TypedLit ::= Int | Float | Bool | String | Bytes | Unit | Nil
           (type: Type)

Ident ::= [a-z_][a-z0-9_]*

FieldAccess ::= Ident "." Ident

Op ::= ADD | SUB | MUL | DIV | MOD | NEG
      | EQ | NE | LT | LE | GT | GE
      | AND | OR | NOT
      | IF | COND | MATCH
      | GET | SET | FIELD
      | MAP | FILTER | REDUCE | FOLD | LEN | AT | APPEND | CONCAT
      | FN | CALL

Param ::= Ident (":" Type) (":" Type)? (":" Type)? (":" Type)?

HOLE ::= "?" | "?:Type"

ExprList ::= Expr ("," Expr)*

Fn ::= "FN" [Ident] "(" ParamList ")" Body

ParamList ::= Param ("," Param)*

Body ::= Expr

Call ::= Ident "(" ExprList ")"
```

**Constraints:**
- No numeric IDs
- No arbitrary integers
- No malformed syntax
- Only bracket-form expressions

## 6. Pretty printer (`src/knot/pretty.py`)

Generates human-readable source from AST.

**Input:** AST node with `node_id`, `label`, `path`

**Output:** Human-readable source (e.g., `fn square(x: i32) -> i32 { x * x }`)

**Rules:**
- Uses `fn`, `let`, `with`, `match`, `if`, `while`, `for` keywords
- Type annotations: `x: i32`
- Returns: `-> i32`
- Blocks: `{ ... }`
- No bracket form — only pretty form

**Note:** The pretty printer is **not** the source of truth; it is a view.

## 7. Binary serializer (`src/knot/bin.py`)

Serializes AST to binary format for storage and IPC.

**Input:** AST node with `node_id`, `label`, `path`

**Output:** Binary graph with node IDs

**Format:**
- Graph format: `node_id`, `parent_id`, `label`, `path`, `type`, `value`
- Round-trips to the same graph

**Phase 1 delivers:**
- A binary serializer that round-trips to the AST
- The binary format is separate from the AST but round-trips to the same graph

## 8. File layout (Phase 1)

```
src/knot/
  __init__.py
  ast.py          # §3
  parser.py       # §4
  grammar/
    gbnf.py       # §5
  pretty.py       # §6
  bin.py          # §7
tests/
  test_ast.py
  test_parser.py
  test_grammar.py
  test_pretty.py
  test_bin.py
```

`src/knot/ai/` stays empty in Phase 1 (R3's domain, Phase 10+).

## 9. Definition of done (Phase 1)

- All four modules import with no side effects.
- Parser accepts bracket-form text and produces AST nodes with `node_id` and `label`.
- GBNF grammar rejects any output that contains numeric IDs or arbitrary integers.
- Pretty printer generates human-readable source from AST.
- Binary serializer round-trips to the same graph.
- No LLM, no type checking, no effects, no holes, no errors anywhere in `src/knot/`.
- R4's harness is green; R1 signs off (R1 decides D1–D8 autonomously).

## 10. Open sub-questions (R1 → human)

- **Q1.** Should `i32`/`i64` be distinct types or a single `int` with width? Distinct types catch more bugs but bloat the type lattice. R1 recommends **distinct types**.  
- **Q2.** Should `string` be UTF-8 bytes or code points? Affects `len`/`AT` semantics. R1 recommends **code points** (matches §22.5 string-stdlib note); defer bytes to `bytes`.  
- **Q3.** Is `RegionType` (lifetimes/regions) worth defining the shape of in Phase 1? R1 recommends **skip** — define only in Phase 2 when needed.  
- **Q4.** Should the pretty printer support `F(...)` shorthand? R1 recommends **no** — only bracket form is canonical.  
- **Q5.** Should the binary format include `path` and `label`? R1 recommends **yes** — for tool IPC and diagnostics.  
- **Q6.** Should the GBNF grammar allow comments? R1 recommends **no** — only bracket-form expressions are valid.