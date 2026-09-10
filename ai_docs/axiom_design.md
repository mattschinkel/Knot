# Knot — AI-native programming language (design)

Author: Matthew Schinkel
Status: design / v0.1

NOTE ON THE NAME: "Knot" is the CURRENT WORKING NAME (chosen by the
author, 2026-09-08). It is a working name only and collides — it must
NOT be used as the public name without clearing it:
- Knot (ilyakooo0/knot) — a real functional relational programming
  language (Cranelift backend, effects inferred in the type system,
  SQLite persistence). Direct collision: a language named Knot.
- knot (raultov/knot) — a Rust MCP server that indexes codebases via
  vector + graph DBs for AI coding agents. Collision in our niche.
- knot.com — not verified free; treat as likely taken.
Prior working name "Axiom" was rejected for its own collisions (Axiom
CAS / SPAD, Axiom Math AI+formal-proofs unicorn, Axiom Inc. agent-native
observability, axiom.com parked).

PROPOSED PUBLIC NAME (for eventual release): "Nodigma" (no-DIG-ma).
Coined from "node" + "enigma/paradigm" — evokes the graph-of-nodes
core and a new paradigm. Verified clean as of 2026-09-08:
- nodigma.com -> NXDOMAIN (available)
- No company, no programming language, no software product named Nodigma
- No GitHub project, no PyPI package named Nodigma (only misspellings:
  ODigMa Consultancy, Nodigmarket24 drilling equipment)
- Not a dictionary word; distinctive and trademarkable
NOTE: "Nodigma" is the leading candidate but is NOT yet locked. The
author should register nodigma.com + check the USPTO/trademark registry
before committing. Alternate verified-clean candidate: "Syntagm"
(syntagm.com NXDOMAIN; linguistic unit, but "Syntagma" is a software
company). Many other candidates were rejected for collisions — see
progress.md "Name search" notes.

The design below uses "Knot" as the working name; rename to Nodigma (or
the final choice) before any public release.

## 1. Goals

A programming language whose canonical form is what an LLM is good at
generating and editing: a typed expression tree stored as a semantic graph
with stable node IDs.

Priorities, in order:
1. Unambiguous structure (one parse, ever)
2. Types, effects, capabilities, contracts checked before run
3. Surgical edits by node ID, not file rewrites
4. Partial programs compile (VALID / PARTIAL / INVALID)
5. Structured, machine-readable errors with repair candidates
6. Deterministic kernel; AI/tool calls are typed effectful capabilities
7. Token-efficient canonical text, but meaning over brevity

Non-goals for v1: human-pretty source as the primary format, intent
compilation, knowledge graphs, uncertainty in the kernel, native agents.

## 2. Core principles

- **Syntax quality bar: 10/10 for LLMs.** The canonical syntax is held
  to an exceptional standard: it must be an exceptionally good fit for an
  LLM to generate, edit, and reason about — unambiguous (one parse, ever),
  token-efficient, no whitespace significance, structured machine-readable
  errors, edits as graph ops. Every syntax/grammar decision is measured
  against this bar. If a feature degrades LLM generation/editing
  reliability, it does not ship. (Reinforces §19 Tier 1 #14: "a feature
  LLMs cannot generate reliably must not exist.") The bar is 10/10, not
  "good enough" — the language's reason to exist is to be the best surface
  for an LLM, not merely a usable one.
- **The 10/10 bar is measurable, not a vibe.** Taste drift is caught by a
  drift-check phase gate (see `ai_docs/knot_agents.md` §8) with concrete
  metrics: M1 token count of canonical AIR, M2 generation accuracy under the
  GBNF grammar, M3 edit round-trip, M4 partial-compile coherence, M5
  compile latency. Each is tracked per-phase vs a baseline; a regression is a
  measurable signal a 4B can catch and report — not a judgment call.
- Everything is a typed expression node.
- Every node has a stable ID.
- Canonical text is a serialization of the semantic graph, not the source of
  truth. The graph is.
- The kernel is deterministic: ADD[2,3] is always 5.
- AI calls return { value, confidence, model, version }; only ai-effectful
  nodes produce confidence.
- Three views of one graph: canonical (AIR), pretty (human), binary (storage/IPC).
- **Canonical = rigid LLM serialization; pretty = humans only** (D-FB6, 2026-09-09).
  The program graph is the source of truth. Canonical text is a mechanical
  `NAME[ARGS]` tree optimized for LLM generate/edit/repair — not for human
  reading. Human-facing sugar (`.`, `=`, infix) belongs ONLY in the pretty
  printer. Do not raise the 10/10 bar by adding human convenience to
  canonical; raise it by removing ambiguity and dual forms.
- **Locked toward 10/10 (R1 — see `ai_docs/r1_decisions_feedback_syntax_10of10.md`
  and `ai_docs/r1_decisions_feedback_uniformity_err_holes.md`):**
  D-FB1 one shape + named `FN[[x:i32], body]`; D-FB2 `DEF[name, expr]` only;
  D-FB3 `T@dim` in typed lits (`10:f64@meters`); D-FB4 holes first-class;
  D-FB5 structured `ERR[...]` for repair loops; D-FB6 graph truth / pretty humans;
  **D-FB7** every non-atom is `OP[...]` (incl. COND/MATCH/LET/WITH);
  **D-FB8** named params required; type surface uniform (`42:i32`, `?:T@dim`);
  **D-FB9** ERR first-class in PROGRAM→…→RESULT/ERR→LLM (fixes are `OP[...]`;
  apply via Phase 6 edits);
  **D-FB10** hole constraint propagation in Phase 2 direction;
  **D-FB11** `parse→normalize→print` unique; canonical has **no spaces**
  (`ADD[1,2]`); pretty may space/infix;
  **D-FB12** bare idents as atoms — no `VAR[x]`.

### 2.1 Does Knot require an LLM? No.

An LLM is NOT required to compile or run a Knot program. The kernel is
deterministic and lowers/runs like any conventional language.

An LLM is involved only in these OPTIONAL roles:

1. WRITING AIR (optional): an LLM generates AIR text, ideally under the
   GBNF grammar so it can only emit valid syntax. A human could write AIR
   by hand too. The language does not care who authored it.
2. COMPILING (optional): the two-half compiler's AI front-end (Tier 1 #12)
   helps with repair, synthesis, and disambiguation. The deterministic
   back-end (lowering, type checking, execution) needs NO LLM. You can
   compile and run with the AI front-end disabled.
3. RUNNING (optional): an LLM is used at runtime ONLY IF the program
   explicitly calls an ai-effectful node (byLLM, Tier 2 #32). A pure
   program with no ai-effectful nodes runs fully deterministic, no LLM.

So: a pure Knot program compiles and runs with zero LLM calls. The LLM is
a *user* and an *optional tool*, never a runtime dependency of the kernel.

## 3. Core data model

### 3.1 Base types
i32 i64 f32 f64 bool string bytes unit never

### 3.2 Type forms
- T            nominal type
- T?           option / nullable
- [T]          list
- {T}          set
- K->V         map
- (T,U,V)      tuple
- T|U          sum (tagged union)
- T&U          capability intersection
- T@dim        units / semantic dimension
- T<region R>  lifetime / region (references)

### 3.3 Units / dimensions
Units are a kinded dimension system tracked through arithmetic.
- meters + meters = meters
- meters * meters = meters^2
- meters + seconds -> type error

    type Money = f64@money
    type Distance = f64@meters

### 3.4 Records and sums

    type User { name:string, age:i32 }

    type Shape =
      Circle { r:f64 }
    | Square { s:f64 }
    | Rect  { w:f64, h:f64 }

### 3.5 Values
Literals carry their type explicitly when ambiguous. Units attach as `T@dim`
on a base type — never a bare dimension as a type name (D-FB3):

    2:i32
    10:f64@meters
    true
    "hello"
    nil
    User { name:"Bob", age:25 }

Invalid unless `meters` is a declared nominal type: `10:meters`.

## 4. AST / expression model

Every expression is a node. Canonical form is bracket notation — one shape
only (D-FB1 / D-FB7 invariant: every non-atomic construct is `OP[...]`):

    OP[arg1,arg2,...]

Canonical serialization is unique (D-FB11): `parse → normalize → print`
must round-trip to one string. **No whitespace** in canonical AIR
(`ADD[1,2]` only). Pretty view may insert spaces or infix.

Atoms (canonical):
- literals: 2, 3.14, true, "hi", nil
- typed literals: 2:i32, 10:f64@meters  (not bare `10:meters`)
- identifiers: x, user  (bare atoms — no VAR[x]; D-FB12)
- holes: ?  or  ?:i32  or  ?:f64@meters  (first-class; D-FB4 / D-FB10)
- bindings: DEF[name, expr] only (D-FB2) — no `=`, no `def name =` in canonical
- functions: FN[[x:i32], body] with named `ident:type` params (D-FB1 / D-FB8)
- field access: GET[user, name] only — `user.name` is pretty-view sugar only
- control/bindings as ops: IF[...] COND[...] MATCH[...] LET[...] WITH[...]
- errors (first-class values): ERR[code, path, expected, actual, fixes...] (D-FB5 / D-FB9)

Pretty view may show `user.name`, `square = ...`, spaced `ADD[1, 2]`, etc.;
the LLM/parser never writes those forms into canonical AIR.

Node addressing (see §21 for the full scheme): the LLM
addresses nodes by structural path and optional symbolic labels,
NOT by numeric ID. `@` introduces a symbolic label:

    @guard GE[GET[u, age], 18]

means "label this node `guard` so I can edit it later as
`MODIFY guard ...`." Labels are symbolic, sparse, and survive
optimization. Numeric IDs are compiler-internal; the LLM may read them
from diagnostics but never writes them into source.

### 4.1 Kernel operations (deterministic)

Arithmetic: ADD SUB MUL DIV MOD NEG
Comparison: EQ NE LT LE GT GE
Logic: AND OR NOT
Control: IF COND MATCH
Access: GET SET FIELD
Collections: MAP FILTER REDUCE FOLD LEN AT APPEND CONCAT
Binding: LET WITH
Holes: HOLE
Functions: FN CALL (return is implicit = last expression)

Every kernel op has a fixed type rule. No overloading, no implicit casts.

## 5. Functions, effects, capabilities, contracts

### 5.1 Function

Canonical (D-FB1 / D-FB2):

    DEF[square, FN[[x:i32], MUL[x, x]]]

### 5.2 Function with contract

    def sqrt = FN[x:f64@money] -> f64@money
      requires  x >= 0@money
      guarantees result >= 0@money
    {
      MATH.sqrt[x]
    }

- requires   = precondition on inputs
- guarantees = postcondition on result
- ensures    = relation between inputs and result

### 5.3 Effects

Every function has an effect set. Default is pure.

    def send_email = FN[to:string, body:string] -> unit
      effects[network, email]
    {
      ...
    }

Effect categories:
- pure
- fs.read  fs.write  fs.delete
- net.request
- db.read  db.write
- io.stdout  io.stderr
- time.now
- random   (non-deterministic, tracked)
- ai       (model calls)

### 5.4 Capabilities

Capabilities are permissions granted at call time.

    capability fs.read
    capability net.request

A function's effect set must be a subset of its granted capabilities:

    def get_weather = FN[city:string] -> Weather
      requires net.request
    {
      ...
    }

The runtime decides whether to grant a capability. This is the natural
sandbox for autonomous AI: an agent can request, but not seize, a capability.

## 6. Holes and partial programs

? is a typed hole. ?:T is a hole with expected type.

    def total = FN[items:[Money]] -> Money
      REDUCE[items, ADD, ?:Money]

Compiler report:

    HOLE #7
      expected: Money
      context:   REDUCE initial value
      candidates:
        0@money
        items[0]

A program with holes is PARTIAL. It can still be type-checked, analyzed,
and partially executed. Reaching a hole at runtime traps.

Compile states:
- VALID   — no errors, no holes
- PARTIAL — type-correct, holes present
- INVALID — type/effect/contract errors

## 7. Error model

Errors are structured, not strings:

    error {
      code: TYPE_MISMATCH
      node: 184
      op:   ADD
      left:  Money
      right: Seconds
      expected: compatible_numeric
      likely_intent: "money / seconds (rate)"
      repairs: [
        { kind: convert, target: Money, node: 185 }
        { kind: replace, node: 185, with: <Money value> }
        { kind: remove_op }
      ]
    }

The LLM consumes this directly. No regex on human prose.

## 8. Tests and properties

Inline tests:

    test square {
      in[5] out[25]
    }

Property tests:

    property square_nonneg {
      forall x:i32,
      square[x] >= 0
    }

The compiler uses tests/properties as verification obligations and fuzz
targets.

## 9. Edit operations (the primary modification interface)

The LLM does not rewrite the file. It issues graph ops:

    CREATE type User { name:string, age:i32 }
    CREATE fn User.is_adult = FN[u:User] -> bool { GE[GET[u, age], 18] }

    MODIFY User.is_adult
      REPLACE GE[_, 18] WITH GT[_, 18]

    DELETE  field User.middle_name
    INSERT  field User.email : string
    RENAME  User.is_adult TO User.can_vote

Each op targets a node ID or a structural pattern. The compiler re-validates
and reports the blast radius:

    OK
      revalidated: User.is_adult, greeting
      test greeting: STILL PASSING
      property tests: re-run (1 passed)

This is the key feature: edits are surgical and the compiler tells you what
broke. No unrelated code is touched.

## 10. Modules and dependencies

    module users {
      type User { name:string, age:i32 }
      def create = FN[name:string, age:i32] -> User { User{name, age} }
      export User, create
    }

    import users.{User, create}

Dependencies are explicit and versioned, and declare the capabilities they
need:

    depends users@1.2
    depends http@3.1 { capabilities[net.request] }

## 11. AI / tool primitives (typed capabilities, not kernel)

AI calls are effectful capabilities with contracts:

    model classifier {
      input:  Image
      output: Classification
      confidence: true
      effects[ai, gpu]
    }

    def classify_doc = FN[doc:Document] -> Classification
      requires ai.classify
    {
      classifier[doc]
    }

Returns a value plus metadata: { value, confidence, model, version }.
The deterministic kernel never produces confidence; only ai-effectful
nodes do.

Tools are typed:

    tool fs.read   { input: Path,   output: Bytes, effects[fs.read] }
    tool fs.delete { input: Path,   output: unit,  effects[fs.delete] }

## 12. Concurrency and memory

Concurrency is dataflow, not threads:

    PAR[ download[a], download[b], download[c] ]

The compiler sees no data dependencies and runs them concurrently. No
threads, locks, or mutexes in user code. Explicit sequencing via SEQ or
nesting.

Memory: no malloc/free in user code. Ownership and lifetime inferred.
T<region R> for references when needed. unsafe { ... } escape hatch with
required capabilities for low-level systems work.

## 13. Representations

Three views of one semantic graph:

1. Canonical (AIR) — compact tree, what the LLM writes:

       def square = FN[x:i32] MUL[x, x]

   (Bracket form, OP[args]. This is the canonical form used throughout
   §4 and §15. The shorter `F(...)` shorthand is NOT canonical.)
2. Pretty — human view, generated, never the source of truth:

       fn square(x: i32) -> i32 { x * x }
3. Binary — serialized graph with node IDs, for storage and tool IPC.

The LLM normally writes canonical. Pretty is a view. Binary is the
storage/IPC format. All three round-trip to the same graph.

## 14. Compilation pipeline

    AIR text
      -> parse to semantic graph (with node IDs)
      -> type check          (VALID / PARTIAL / INVALID)
      -> effect/capability check
      -> contract verification (static + runtime obligations)
      -> verified IR
      -> optimize (graph rewrites)
      -> target (native / VM / interpreted)

Each stage emits structured diagnostics. The compiler is an interactive
partner: it reports holes, candidates, and repairs, not just pass/fail.

## 15. Concrete example

Canonical (AIR):

    type User { name:string, age:i32 }

    def eligible = FN[u:User] -> bool { GE[GET[u, age], 18] }

    def greeting = FN[u:User] -> string {
      IF[eligible[u],
         CONCAT["Hello ", GET[u, name]],
         CONCAT["Sorry ", GET[u, name]]]
    }

    test greeting {
      in[User{name:"Bob", age:25}] out["Hello Bob"]
    }

Pretty view (generated):

    type User { name: string, age: i32 }

    def eligible(u: User) -> bool = u.age >= 18

    def greeting(u: User) -> string =
      if eligible(u) then "Hello " + u.name else "Sorry " + u.name

    test greeting {
      in  User { name = "Bob", age = 25 }
      out "Hello Bob"
    }

Edit:

    MODIFY eligible
      REPLACE GE[_, 18] WITH GT[_, 18]

Compiler response:

    OK
      revalidated: eligible, greeting
      test greeting: STILL PASSING

## 16. Build order (phases)

Phase 0  Core data model
         value representation, type representation, units/dimensions
Phase 1  AST + parser + GBNF grammar
         node model with IDs, canonical text parser, pretty printer,
         binary serializer, AND a constrained-decoding grammar for AIR
         so llama.cpp/vLLM can only emit valid syntax
Phase 2  Type checker
         type rules for kernel ops, inference, partial typing with holes
Phase 3  Effects / capabilities / contracts
         effect sets, capability granting, requires/guarantees checking;
         prohibitions become structural constraints, never paths
Phase 4  Holes + partial compile
         VALID/PARTIAL/INVALID, hole reporting with candidates
Phase 5  Structured errors + repairs (errors as values, no exceptions)
         diagnostic format, repair candidate generation
Phase 6  Edit operations
         graph edit ops, revalidation, blast-radius reporting
Phase 7  Tests / properties
         inline tests, property tests, fuzz
Phase 8  Modules + dependencies
Phase 9  Compiler / VM  (sub-200ms feedback is a hard constraint)
         IR, optimization, execution; two-half compiler: AI front-end
         (judgment) + deterministic lowering (never guesses)
Phase 10 AI / tool capabilities (byLLM-style typed constructs)
         typed model/tool FFI, confidence metadata, runtime granting,
         AI-output constrained to declared return type
Phase 11 Concurrency (dataflow), memory regions, unsafe
Phase 12 Compiler as MCP server + `kb` retrieval + `--llm` output mode
         eval/typecheck/run/constrain/doc_query/query as MCP tools;
         token-budgeted docs retrieval; token-budgeted diagnostics

Do not start by inventing syntax. If the AST is right, the canonical text,
pretty printer, and binary form are three views of the same object.

## 17. Open design questions

- Node ID scheme: RESOLVED — see §21. Decision: the LLM addresses
  nodes by structural path + optional symbolic labels; numeric IDs are
  compiler-internal, never authored in source.
- Canonical line format: one node per line vs nested on one line.
  Proposal: nested allowed, but pretty-printer emits one node per line.
- Units: is @dim a type parameter or a separate kind?
  Proposal: separate kind, tracked by the type checker, not erased.
- How the LLM addresses a node it cannot see (large graph).
  RESOLVED — structural paths + labels + compiler query fallback (§21).
- Whether the kernel ever gets string interpolation / pattern matching sugar.
  Proposal: sugar is a pretty-view concern; canonical stays explicit.

## 18. Related work / positioning

Claimed differentiators (must be verified against real projects):
1. Edit operations as the primary modification interface + blast-radius
   reporting. This is the strongest novelty claim.
2. Effects + capabilities as a runtime security boundary for agents.
3. Holes + partial compilation (VALID/PARTIAL/INVALID) as first-class state.
4. Structured errors with repair candidates.
5. Units/dimensions as a kinded type system.
6. Clean split: deterministic kernel vs ai-effectful typed tool FFI.

Projects to compare against (competitive scan done — see §20):
- Magpie  — "LLM-native programming language", explicit SSA syntax
- Sigil   — compiles skills to typed agent harnesses via AG-IR (YAML). CLOSEST on graph IR, but no node-ID edit ops and no general programs.
- Synoema — LLM-native, GBNF constrained decoding, requires/ensures contracts
- Lume    — AI-first backend language; `kb` token-budgeted docs; errors as values
  (ChatGPT called this "Lumo"; real name is Lume)
- LMQL    — language for programming LLM interactions (different category)
- GALLa   — aligning LLMs with program graphs (opposite direction)

Novelty holds: no project combines graph-as-source-of-truth +
node-ID edits + constrained-decoding grammar + MCP compiler + capability
sandbox + holes/partial-compile. Sigil is closest but compiles agent
skills, not general programs, and has no node-ID edit ops.

## 19. Wish list (from the LLM's perspective)

This is what I, as the LLM who will write and edit in this language,
actually want. Not a feature checklist — a list of my real failure modes
and what would fix them.

### Tier 1 — The kernel (non-negotiable)

1. Program is a semantic graph. Text (AIR) is a serialization, never the
   source of truth. The graph is.
2. Stable node IDs. Edits are graph ops (MODIFY/REPLACE/INSERT/DELETE),
   not file rewrites. The compiler reports the blast radius.
3. Everything is a typed expression. Explicit types, no implicit coercion,
   no overloading. Every kernel op has one fixed type rule.
4. No whitespace significance. Structure is brackets, never indentation.
5. Holes (? and ?:T) are first-class. Partial compile returns
   VALID / PARTIAL / INVALID. A partial program still type-checks.
6. Structured errors: { code, node, op, expected, received, repairs }.
   No prose I have to regex.
7. Deterministic kernel. ADD[2,3] is always 5. AI/tool calls are typed
   effectful capabilities, never part of the kernel.
8. Effects + capabilities declared on every function. An agent can request
   a capability but not seize it. This is my security boundary.
9. Contracts (requires / guarantees / ensures) checked statically where
   possible, at runtime otherwise.
10. Tests and properties live in the language. The compiler uses them as
    verification obligations and re-runs them on edit.
11. Errors are values, not exceptions. No hidden control flow. A failed
    operation returns an error value the program can branch on. (Lume)
12. Two-half compiler: an AI front-end (judgment: repair, synthesize,
    disambiguate) and a deterministic back-end (lowering). Invariant: if
    lowering ever needs a guess, the front-end is at fault. Deterministic
    passes never guess. (Sigil)
13. Prohibitions become constraints, never paths. Anything forbidden is
    structurally impossible to express, not merely discouraged. This
    backs the capability sandbox. (Sigil)
14. Principle gate on every new feature: "A feature LLMs cannot generate
    reliably must not exist in the language." If I can't write it
    consistently, it doesn't ship. (Synoema)

### Tier 2 — What I'd strongly want

15. A compiler query/inspection API. I want to ask, programmatically:
    "type of node 173", "functions in scope taking User to bool",
    "callees of 173", "signature of eligible". I currently guess all this.
16. Propose / dry-run edits. I emit a candidate edit; the compiler tells me
    what would break before I commit.
17. Provenance + confidence propagation for ai-effectful values. A value
    from a classifier carries {value, confidence, source}. Values derived
    from it inherit the provenance. The kernel stays deterministic; only
    ai-effectful nodes carry confidence.
18. Explicit "trust" step. A probabilistic value cannot feed a function
    expecting a deterministic value without an explicit trust/verify step.
    Stops me treating a guess as a fact.
19. Non-determinism markers (random, time.now, ai) tracked through the
    type system so I don't cache them naively.
20. Edit history as first-class. Edits are a list of ops; undo is trivial.
21. Fuzzy-match errors. "You called calcuate_tax — did you mean
    calculate_tax (node #88)?" against real identifiers.
22. "What changed" API. After an edit, list every node whose
    type/effect/validity changed. I currently can't tell.
23. Round-trip guarantee. AIR, graph, pretty, binary all map to the same
    graph. I can trust the serialization.
24. Canonical binary as storage; text filter for diffs. Avoids merge
    conflicts on formatting.
25. Capability delegation/budgets. An agent with net.request can delegate
    a subset to a sub-agent. Budgets flow down, never up.
26. Ship a GBNF/constrained-decoding grammar for AIR. With llama.cpp/vLLM
    this guarantees I can only emit syntactically valid AIR. Syntax
    errors become impossible, not just detectable. Highest-impact adopt.
    (Synoema)
27. Compiler as an MCP server. Expose eval, typecheck, run, constrain,
    doc_query, and the graph query API (#15) as MCP tools. Any agent —
    Cursor, Claude, our own crew — can drive the compiler directly.
    (Synoema)
28. Token-budgeted knowledge retrieval `kb` tool. "Give me the docs for
    REDUCE in <=500 tokens." Stops me blowing the context window on a
    whole manual. (Lume)
29. `--llm` output mode with a token budget and policy
    (diagnostics_first / slices_first / balanced / minimal). The
    compiler adapts what it emits to a budget I set. (Magpie)
30. Sub-200ms compile feedback as a hard design constraint, not an
    afterthought. Fast feedback is the whole game for fix loops. (Magpie)
31. Typed carries on graph edges. Data flowing between nodes is typed,
    so the graph carries data-flow facts, not just structure. (Sigil)
32. byLLM: model invocations are typed constructs with declared
    inputs/outputs and scoped knowledge and tool bindings. A richer
    form of our "AI calls are typed capabilities." (Sigil)
33. Constrain AI-tool output to the declared return type. When an
    ai-effectful node runs, its output is masked/validated against the
    declared type. Ties AI to the type system. (LMQL)

### Tier 3 — Nice, but later

34. Compiler-suggested property tests for a given function.
35. "Explain" view: the compiler emits a natural-language explanation of a
    node, for the human. Not the source — an explanation.
36. Multiple candidate implementations + benchmark selection.
37. Confidence-tagged code regions as a deployment policy (require
    confidence >= 0.95 before deploy).

### Explicitly rejected (even though they sound cool)

- Intent-compilation / "describe the goal, compiler writes it".
  Underspecified; I can't verify what it will do. I want to write the program.
- Natural language as the source. Ambiguous.
- Probabilistic kernel values. The kernel stays deterministic.
- Implicit type coercion. Ever.
- Whitespace significance. Ever.
- Macros in v1. They make code hard to analyze; graph-edit ops replace
  most macro needs.
- Hidden effects or globals. Everything a function touches is declared.
- 1-letter opcodes. Loses meaning, hurts accuracy.
- Verbose English operators. Too many tokens.

### v1 scope clarifications (resolves contradictions)

- Units/dimensions (§3.3) ARE v1 core. They were removed from Tier 3.
  Open question in §17 (kind vs type parameter) is about *how*, not *whether*.
- Dataflow concurrency (§12) is specified now but BUILT in Phase 11,
  not in the first runnable kernel. PAR/SEQ are not kernel ops in §4.1
  until Phase 11.
- Two distinct error concepts, do not conflate them:
  (a) Compile-time diagnostics (§7): structured reports the compiler
      emits to the LLM — { code, node, expected, received, repairs }.
  (b) Runtime error values (Tier 1 #11): values a program returns and
      branches on (Result/Option style). No exceptions, no hidden control
      flow. The kernel uses (b); the compiler emits (a).

### What I'm honestly unsure about

- Canonical line format: nested on one line vs one node per line.
  Lean: nested allowed; pretty-printer emits one node per line.
- The exact marker for probabilistic values. Must not pollute the kernel.
- Whether modules should be a graph too (probably yes).
- Whether to benchmark 2-3 candidate syntaxes by token count and accuracy
  before locking canonical AIR. I would actually do this.

## 20. Competitive scan findings (Phase 0.5)

All six projects verified real. Summary of standout features to adopt.

### Magpie (magpie-lang.com, Rust, v0.1)
- Explicit SSA syntax, one way to do everything, self-documenting ops.
- Sub-200ms compile feedback loop. This is a design constraint for us.
- `--llm` output mode with token budget and policy
  (diagnostics_first / slices_first / balanced / minimal).
- Canonical formatter + content-addressable digest.
- Trades ~2.3x more tokens for zero ambiguity and faster feedback.

### Sigil (sigilagent.com, arXiv 2607.27309)
- Compiles SKILL.md into typed agent harnesses via AG-IR (YAML).
- Two-half compiler: AI front-end (LIFT, judgment) + deterministic
  back-end (LOWER). Invariant: if lowering needs a guess, the front-end
  is at fault. Deterministic passes never guess.
- Typed "carries" on graph edges (typed data flow between nodes).
- byLLM: model invocations as typed constructs with declared
  inputs/outputs/scoped knowledge/tools.
- "Prohibitions become constraints, never paths" — forbidden things are
  structurally impossible, not discouraged.
- Compile-once with frontier model, run on small/local model (Ollama).

### Synoema (synoema.tech)
- GBNF grammar for constrained decoding (208 lines, 76 rules) with
  llama.cpp/vLLM -> 100% syntactically valid output. HIGHEST-IMPACT find.
- MCP server (npx synoema-mcp): eval, typecheck, run, constrain, doc_query.
- `constrain` tool for incremental token-masked generation.
- `sno doc --contracts` extracts contracts to a spec table.
- Three-layer verification: structural (GBNF) / semantic (HM types) /
  formal (contracts).
- Principle: "A feature LLMs cannot generate reliably must not exist."

### Lume (mavboas/lume; ChatGPT called it "Lumo")
- `lume kb` token-budgeted retrieval tool: packs docs/examples/diagnostics
  under a caller-set token cap. Brilliant for agent context management.
- Errors as values, no hidden control flow / exceptions.
- Immutability by default; `.with()` for derived values.
- "Tokens are a real cost. Syntax concise without cryptic. Errors are
  values, not hidden control flow. One canonical way."

### LMQL (eth-sri/lmql, arXiv 2212.06094)
- `where` constraints on LLM output with eager token masking
  (STOPS_AT, REGEX, length, VAR in [...]).
- High-level text constraints auto-translated to token masks.
- Custom constraint ops (forward/follow/final) with soundness guarantee.
- Up to 80% inference cost reduction via constraint pruning.

### GALLa (ACL 2025, codefuse-ai/GALLa)
- Aligns LLMs with ASTs and data-flow graphs via GNN + adapter.
- GraphQA: train models to answer questions about graph structure.
- Empirical validation that graphs carry semantic info surface text loses.
- Supports our compiler query API (#15): graph questions are trainable.

### Second-round findings: the "content-addressed graph + AI-native" cluster
A later search (2026-09-08) for names turned up a cluster of projects
that already combine several ideas we had counted as novel. This
SHARPENS our novelty claim — the "graph-as-source + content-addressed
+ blast-radius + AI-native + MCP" combination is NOT unique on its own.

- Cairn (cairnlang/Cairn; cairn.computer; isaacriehm/cairn) — a
  stack-based postfix language for the BEAM with explicit contracts
  AND a content-addressed AST store, transactional authoring API,
  "blast radius" reporting, MCP tool surface, WASM lowering, checker,
  renderer, structural scaffolder. The closest direct competitor to
  our kernel+edits design. Also an AI-agent orchestration environment.
- Ashlar (mrjeeves/ashlar) — "a language built FOR agents, BY agents",
  AI-first composition language; toolchain `ashlar check/fix/build`,
  `ashlar radius` (blast radius), `ashlar rename`, `ashlar delta`.
  Very close to our edit-ops + structured-errors + AI-first goals.
- AILANG (sunholo-data/ailang-world) — "kernel IS a typed, immutable,
  content-addressed world graph; every subsystem is a projection over
  it; programs are transactions; blast radius bounded by construction;
  verification deterministic-first, content-addressed memoized."
- Causari (causari.dev) — content-addressed ledger for AI agents;
  `re impact` walks downstream blast radius; BLAKE3; built in Rust.
- Grafema (Disentinel/grafema) — turns code into a queryable graph,
  MCP server for AI agents, Datalog/Cypher, dataflow tracking.
- Nodus (nodus-lang on PyPI, v5.1) — AI-native orchestration DSL,
  parse-time dependency checking, typed tool boundary, MCP-shaped.
- Knot (ilyakooo0/knot) — functional relational language, effects
  inferred in the type system, Cranelift backend. (Also raultov/knot,
  a Rust MCP codebase indexer for AI agents.)

IMPLICATION FOR NOVELTY: the content-addressed graph + blast-radius +
AI-native + MCP combination is now table stakes, not a differentiator.
Our genuine novelty must be the FULL combination that none of these
ship together: (1) a GENERAL-PURPOSE deterministic kernel language
(not an agent runtime/ledger/orchestration DSL), (2) a GBNF constrained-
decoding grammar tied to the language (only Synoema has this), (3)
holes / partial-compile VALID/PARTIAL/INVALID (none have this), (4)
units & dimensions in the kernel (none have this), (5) errors-as-values
AND structured repair candidates together (Ashlar has check/fix; Lume
has errors-as-values; none combine both with holes). Position on the
intersection, not on any single feature.

### Must-adopt standout features (high impact, serve our goals)

NOTE: these A1–A12 are the SOURCE list, now folded into §19
(Tier 1 #11–14, Tier 2 #26–33). Kept here as the audit trail of which
feature came from which project.

A1. Ship a GBNF/constrained-decoding grammar for AIR (Synoema).
     Guarantees syntactically valid generation with llama.cpp/vLLM.
     Directly fits our LocoOperator setup. Highest-impact new feature.
A2. Compiler as MCP server: eval, typecheck, run, constrain, doc_query,
     query (graph queries) as MCP tools (Synoema). Any agent can use it.
A3. Token-budgeted knowledge retrieval `kb` tool: docs/examples/diagnostics
     under a caller-set token cap (Lume).
A4. `--llm` output mode with token budget + policy
     (diagnostics_first/slices_first/balanced) (Magpie).
A5. Sub-200ms compile feedback as a hard design constraint (Magpie).
A6. Errors as values, no hidden control flow / exceptions (Lume).
A7. Two-half compiler: AI front-end (judgment) + deterministic lowering;
     invariant "if lowering needs a guess, the front-end is at fault"
     (Sigil).
A8. Prohibitions become constraints, never paths (Sigil). Forbidden things
     are structurally impossible, not discouraged.
A9. Typed carries on graph edges (typed data flow) (Sigil).
A10. byLLM: model invocations as typed constructs with declared
     inputs/outputs/scoped knowledge/tools (Sigil).
A11. Constrain AI-tool output to the declared return type (LMQL-style
     token masking applied to ai-effectful nodes).
A12. Principle gate: "A feature LLMs cannot generate reliably must not
     exist in the language" (Synoema).

### Nice-to-adopt
- Immutability by default (Lume).
- Canonical formatter + content-addressable digest (Magpie).
- `doc --contracts` extraction CLI (Synoema).
- GraphQA-style query API, validated by GALLa (supports our #15).
- Compile-once-run-cheap: compile with frontier, run on local (Sigil).

### The novelty gap (none combine all of these)
graph-as-source-of-truth + node-ID edits + constrained-decoding grammar
+ MCP compiler + token-budgeted output + capability sandbox + holes/
partial-compile. Each project has 1-3; our combination is the novelty.

## 21. Node addressing scheme (decision)

The edit protocol (§9) and the GBNF grammar (Phase 1) both depend on
how the LLM addresses a node. Decision: the LLM addresses nodes by
structural path and optional symbolic labels — NEVER by numeric ID.

### 21.1 Why not author-pinned numeric IDs
- Generating unique integers for every node is a burden and error-prone
  for an LLM (collisions, gaps, off-by-one across a large program).
- Numeric IDs in emitted text force the GBNF grammar to allow arbitrary
  integers, which weakens constrained decoding (the grammar cannot
  enforce uniqueness).
- Numeric IDs do not survive optimization rewrites; structural paths and
  labels do.
- If the LLM did not author the current state (e.g., after a human edit
  or another agent's edit), it knows no numeric IDs — so numeric-ID
  addressing breaks the multi-editor case.

### 21.2 The scheme
1. Internal numeric IDs: compiler-owned, stable within a session, used in
   diagnostics and blast-radius reports. The LLM may READ them from
   compiler output but never WRITES them into source.
2. Structural path addressing (primary): a path from a named anchor
   (a top-level def/type/test) to a node. Examples:
   `eligible.body`, `eligible.body.args[1]`,
   `greeting.body.branches[0]`.
3. Symbolic labels (optional, sparse): the LLM marks nodes it expects to
   edit with a label: `@guard GE[GET[u, age], 18]`. Labels are symbolic,
   unique within a module, and survive optimization. Edits address by
   label: `MODIFY guard REPLACE ...`.
4. Query fallback: if a structural path no longer resolves (structure
   changed), the LLM queries the compiler ("which node is the comparison
   in eligible?") and the compiler returns candidates with their current
   paths/IDs.

### 21.3 Edit addressing precedence
1. label (if the node has one) — most stable
2. structural path — default
3. compiler-reported numeric ID — only for one-shot references within a
   session, never authored in source

### 21.4 What this fixes
- §9 already uses names + structural patterns, not numeric IDs —
  consistent, no change needed there.
- §4's `@` is now a label, not a numeric ID (revised above).
- §17 open question resolved.
- GBNF grammar (Phase 1) does not need to tokenize arbitrary integers
  as node IDs — stronger constraint, simpler grammar.

### 21.5 Open sub-questions
- Structural path syntax: dot/bracket (`eligible.body.args[1]`) vs a
  small path DSL. Proposal: dot/bracket — familiar to LLMs from JSON/JS.
- Multiple matches: when a structural path matches several nodes after
  a refactor. Proposal: the compiler returns all matches and requires
  the LLM to disambiguate; an edit requires a unique match.
- Label scoping: module-local vs global. Proposal: module-local;
  `Module.label` to cross modules.
- Auto-labeling: whether the compiler suggests labels for nodes the LLM
  edits frequently. Later.

## 22. Self-hosting / bootstrap plan (end goal)

END GOAL: Knot's compiler is written in Knot and Knot compiles
itself. This section drives several design decisions.

### 22.1 Why Knot is well-suited to self-host
The compiler's job is to manipulate the AST/IR as data. In Knot, the
program IS the graph, and records/sums/lists/maps are native. So the
compiler's core data structure is the language's native data — writing
a compiler in Knot is more natural than in most languages.

### 22.2 Bootstrap stages (T-diagram)
- Stage 0 (scaffolding, thrown away): a minimal Knot compiler
  written in a host language (Python — see §22.4). It parses AIR,
  type-checks, and compiles to a bytecode VM. It only needs to be
  correct and complete enough to compile the Stage-1 compiler. It does
  NOT need to be fast.
- Stage 1: write the Knot compiler itself in Knot (a subset first).
  Compile it with Stage 0. Now we have a Knot compiler produced by
  Stage 0.
- Stage 2: the Stage-1 compiler compiles itself -> self-hosting.
  Stage 0 (Python) is retired. From here on, Knot is built by Knot.

### 22.3 Bootstrap the DETERMINISTIC core first
The AI front-end (Tier 1 #12) is an ai-effectful capability (byLLM).
To keep the bootstrap clean, bootstrap the DETERMINISTIC lowering
compiler in Knot first — no LLM dependency to build the compiler.
Add the AI front-end as an ai-effectful layer AFTER self-hosting is
achieved. The self-hosted compiler may then use an LLM for
  repair/synthesis, but the language builds without one.

### 22.4 Host language for Stage 0: recommendation
Recommendation: Python (we already have a venv; fast iteration on the
risky part — the language design; correct enough with tests; Stage 0
is retired after bootstrap so its speed is irrelevant long-term).
Target: a bytecode VM first (fully under our control), then a native
backend (LLVM/C) later.
Alternative: Rust — stronger static safety helps catch bugs in the
Stage-0 compiler itself (a buggy Stage 0 bootstraps bugs into the
language), and a cleaner reference for the eventual native backend,
but slower to first bootstrap. Revisit if Stage-0 correctness
becomes a problem.

### 22.5 What the language must add to support self-hosting
Most of it is already in the design. To express a compiler, Knot needs:
- bytes + byte buffers for codegen output — already in §3.1 (bytes).
- fs.read / fs.write / io.stdout / io.stderr — already in §5.3.
- pattern matching (MATCH) + recursion — already in §4.1.
- maps/sets for symbol tables — already in §3.2.
- a string stdlib (slice, index, length, char<->int) — NOT yet
  specified. Add to Phase 0/stdlib.
- a bytecode VM target — NOT yet specified. Add to Phase 9.
- an `exec`/`process` capability ONLY for the native (C/LLVM) backend
  (to invoke gcc/llc). NOT needed for the VM-target bootstrap. Add to
  the effect set when the native backend lands.

### 22.6 Implication for phasing
Self-hosting is a track that runs alongside the feature phases:
- After Phase 9 (VM target works): write Stage 0 in Python.
- After Phase 9 + enough stdlib: write the compiler-in-Knot (Stage 1).
- Bootstrap (Stage 2) as a milestone, not a phase.
The language must stay simple enough that a Stage-0 compiler can be
written by hand in Python in reasonable time. Resist features that
make Stage 0 infeasible (e.g., full dependent types before bootstrap).













