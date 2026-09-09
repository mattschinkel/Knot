# Knot

**An AI-native programming language — designed for LLMs to generate, edit, and reason about, Knot for humans to read.**

## What it is

Knot is a programming language whose canonical form is what an LLM is
good at generating and editing: a **typed expression tree stored as a
semantic graph with stable node IDs**. Text is a serialization of the
graph — the graph is the source of truth, not the text.

The goal is a language that is an **exceptionally good** surface for an
LLM — a 10/10 fit, not merely "good enough." Every syntax/grammar
decision is held to that bar: if a feature degrades LLM
generation/editing reliability, it does not ship.

## Status

**Design / v0.1 — not yet implemented.** No compiler exists yet. This
repo currently holds the design, the agent crew that will build it, and
a build-progress dashboard.

## Key design points

- **Graph as source of truth.** The program is a semantic graph; AIR
  text is a serialization. Three views (canonical AIR, pretty, binary)
  round-trip to one graph.
- **Stable node IDs + surgical edits.** Edits are graph ops
  (`MODIFY`/`REPLACE`/`INSERT`/`DELETE`), not file rewrites. The
  compiler reports the blast radius of every edit.
- **Deterministic kernel.** `ADD[2,3]` is always 5. AI/tool calls are
  typed effectful capabilities, never part of the kernel. A pure program
  compiles and runs with **zero LLM calls**.
- **Types, effects, capabilities, contracts** checked before run.
  Capabilities are the security boundary: an agent can *request* a
  capability but not *seize* it.
- **Holes + partial compile.** `?` and `?:T` are first-class. Compile
  returns `VALID` / `PARTIAL` / `INVALID`; a partial program still
  type-checks.
- **Structured, machine-readable errors** with repair candidates — no
  prose for the LLM to regex.
- **Units/dimensions** in the kernel (`f64@meters`, `meters * meters = meters^2`).
- **GBNF constrained-decoding grammar** so llama.cpp/vLLM can only emit
  valid Knot syntax — syntax errors become impossible, not just detectable.
- **Compiler as an MCP server** (`eval`/`typecheck`/`run`/`constrain`/
  `doc_query`/`query`) — any agent (Cursor, Claude, our own crew) can
  drive it directly.
- **Two-half compiler.** An AI front-end (judgment: repair, synthesis)
  and a deterministic back-end (lowering). Invariant: if lowering ever
  needs to guess, the front-end is at fault — deterministic passes never
  guess.
- **Self-hosting end goal.** Knot's compiler will be written in Knot
  and compile itself. Bootstrap the deterministic core first (no LLM
  dependency to build the compiler); add the AI front-end after.

Full design: [`ai_docs/axiom_design.md`](ai_docs/axiom_design.md).

## Does Knot require an LLM?

**No.** The kernel is deterministic and lowers/runs like any
conventional language. An LLM is involved only in *optional* roles:
writing AIR (ideally under the GBNF grammar), the AI front-end's
repair/synthesis, and runtime ai-effectful nodes. A pure Knot program
compiles and runs with zero LLM calls.

## Repo layout

```
ai_docs/
  axiom_design.md   # the language design (goals, type system, AST,
                    # effects/capabilities/contracts, holes, errors,
                    # edits, modules, build phases, self-hosting plan)
  knot_agents.md     # the 6-role LLM agent crew that builds Knot
  ai.txt             # project working rules
web/
  index.html         # one-page build dashboard (live status)
fixes/               # one fix_*.md per issue
progress.md          # highlights, TODOs, previous issues, scripts
instructions.txt     # available project instructions
name_changes.md      # rename log
.gitignore
```

The CrewAI wiring (`two_agent_crew.py`, `requirements.txt`) and demo
data are **local-only** (gitignored) — they hold the LAN llama-server
endpoint/key and are not part of the public repo.

## Build crew

Knot is built by a 6-role LLM agent crew (detailed in
[`ai_docs/knot_agents.md`](ai_docs/knot_agents.md)):

| Role | Job |
|---|---|
| **R1 Architect** | design coherence, task breakdowns, review |
| **R2 Kernel Engineer** | deterministic back-end; never guesses |
| **R3 AI Front-end Engineer** | GBNF, repairs, MCP, `--llm`, `kb` (judgment half) |
| **R4 Verifier** | tests, properties, partial-compile gate, fuzz |
| **R5 DX Engineer** | formatter, LSP, CLI, sub-200ms loop |
| **R6 Scribe** | docs, examples, the dashboard, `name_changes`/`fixes` |

The human is the architect; agents are scoped implementers/reviewers.
Progress is visible on the [build dashboard](web/index.html) (open
`web/index.html` in a browser, or serve plain HTTP: `python -m
http.server 8000` from `web/`).

## Author

Matthew Schinkel

## License

To be decided.
