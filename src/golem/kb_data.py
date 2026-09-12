"""Built-in knowledge cards for kb retrieval (Phase 12).

Each card: id, title, tags, body. Bodies stay short so budgets pack several.
"""

from __future__ import annotations

# (id, title, tags_tuple, body)
CARDS: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
    (
        "air-canon",
        "Canonical AIR",
        ("air", "syntax", "dfb11"),
        "Canonical AIR is OP[args] with no spaces (D-FB11). "
        "Atoms: numbers, 'strings', true/false/nil, idents, UNIT, holes ? / ?:T. "
        "Pretty view is human-only; never author field-access sugar in canon.",
    ),
    (
        "op-add",
        "ADD",
        ("op", "arith", "add"),
        "ADD[a,b] — numeric addition. Both args same numeric type (i32/i64/f32/f64). "
        "No implicit casts. Example: ADD[1,2] -> 3.",
    ),
    (
        "op-mul",
        "MUL",
        ("op", "arith", "mul"),
        "MUL[a,b] — multiplication. Same-type numerics. Example: MUL[3,4] -> 12.",
    ),
    (
        "op-if",
        "IF",
        ("op", "control", "if"),
        "IF[cond,then,else] — cond must be bool; branches unify. "
        "Example: IF[true,1,2] -> 1.",
    ),
    (
        "op-par",
        "PAR",
        ("op", "concurrency", "par"),
        "PAR[e1,e2,...] — dataflow-independent branches; result Tuple in order. "
        "No user threads/locks. SEQ for sequencing.",
    ),
    (
        "def-fn",
        "DEF and FN",
        ("air", "def", "fn"),
        "DEF[name,FN[[params],body]] binds a function. "
        "Params are name:Type. Call as name[args] or via VM run(call=...).",
    ),
    (
        "holes",
        "Holes",
        ("holes", "partial", "phase4"),
        "Hole ? or ?:T. Programs with holes are PARTIAL. "
        "Evaluation traps as ErrorVal(kind=hole_trap). Typecheck still works.",
    ),
    (
        "errors",
        "Errors as values",
        ("errors", "err", "phase5"),
        "ERR[...] is first-class. Kernel returns ErrorVal, never raises for "
        "diagnostics. diagnose() + repairs suggest graph edits.",
    ),
    (
        "effects",
        "Effects and capabilities",
        ("effects", "caps", "phase3"),
        "Effects are type-level sets; capabilities are runtime grants. "
        "UNSAFE always needs capability unsafe. MODEL needs ai.",
    ),
    (
        "modules",
        "Modules",
        ("modules", "import", "phase8"),
        "MODULE[name,items...,EXPORT[...]] IMPORT[mod,names...] "
        "DEPENDS[mod,ver,CAPS[...]]. link_program resolves imports.",
    ),
    (
        "vm",
        "Bytecode VM",
        ("vm", "phase9", "m5"),
        "compile AST to Chunk; stack VM. M5 = median compile+run ms; product bar <200ms.",
    ),
    (
        "mcp-tools",
        "MCP tools",
        ("mcp", "phase12", "tools"),
        "Tools: eval, typecheck, run, constrain, doc_query, query. "
        "In-process call_tool; stdio JSON-RPC; no HTTPS.",
    ),
    (
        "llm-mode",
        "--llm output",
        ("llm", "phase12", "budget"),
        "format_for_llm(payload, budget, policy). Policies: diagnostics_first, "
        "slices_first, balanced, minimal. Tokens ≈ len//4.",
    ),
    (
        "edits",
        "Edit operations",
        ("edits", "phase6", "blast"),
        "apply_edit REPLACE/DELETE/INSERT/RENAME/REPLACE_MATCH with blast_radius. "
        "Address by structural path or @label.",
    ),
    (
        "reduce",
        "REDUCE",
        ("op", "reduce", "fold"),
        "REDUCE is not a v1 kernel op yet; use explicit SEQ/recursion via DEF. "
        "This card exists so kb('REDUCE') returns a useful budgeted answer.",
    ),
)
