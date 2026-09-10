# Additional syntax feedback — structural uniformity + ERR/holes/canonical (2026-09-10)

Author-forwarded follow-up to `ai_docs/feedback_syntax_10of10.md` and
`ai_docs/r1_decisions_feedback_syntax_10of10.md` (D-FB1–D-FB6).

R1: for each item below, DECIDE ACCEPT / REJECT / AMEND with one-line rationale
and concrete design-doc / GBNF / parser edits. Prefer rigidity for LLM loops.
Do not weaken D-FB1–D-FB6 unless amending with a stricter lock.

## 1. Make every construct structurally uniform (invariant)

Already close:

```
ADD[1, 2]
GET[user, name]
IF[c, a, b]
FN[[x:i32], body]
DEF[x, value]
```

Proposed **language invariant**:

> Every non-atomic construct is `OP[arguments...]`.

That makes the grammar extremely predictable for an LLM.

**Decide as D-FB7.** Confirm whether CondExpr/MatchExpr/LET/WITH/pretty remnants
must also be `OP[...]` only in canonical AIR, or stay as separate AST classes
that still serialize as `OP[...]`.

## 2. Make types completely uniform

Standardize on:

```
42:i32
3.14:f64
10:f64@meters
?:i32
?:f64@meters
```

Make the type itself structurally composable eventually, e.g.:

```
FN[[x:i32], i32, body]
```

(or whatever function-type representation is locked).

Goal: an LLM never guesses whether something is a type, unit, annotation, or
special literal.

**Decide as D-FB8.** Pick function-type / typed-FN surface if amending D-FB1 FN shape.

## 3. Make ERR a first-class part of the language

Biggest push. Already sketched:

```
ERR[code, path, expected, actual, fixes]
```

Do **not** treat ERR as merely compiler stdout. Design Knot around:

```
PROGRAM → PARSE → TYPE → EXECUTE → RESULT / ERR → LLM
```

Errors must be actionable. Example:

```
ERR[
    TYPE_MISMATCH,
    [1],
    i32,
    string,
    [
        REPLACE[1, ?:i32]
    ]
]
```

The LLM can immediately act on that.

**Decide as D-FB9.** Confirm ERR is a first-class AST/value (not sidecar text),
fix ops as `OP[...]` nodes (e.g. `REPLACE[path, expr]`), and when ERR wiring
blocks Phase 2 vs Phase 5.

## 4. Make holes much more powerful

Defining feature candidate. Already:

```
?
?:i32
?:f64@meters
```

Eventually allow contextual constraints to propagate into holes:

- `ADD[42, ?]` → infer `?:number` (or numeric lattice)
- `ADD[42:i32, ?]` → infer `?:i32`
- function hole → `?:FN[[i32], i32]` (shape per D-FB8)

Gives LLMs explicit completion loci most languages lack.

**Decide as D-FB10.** ACCEPT as direction now vs Phase 2 minimum (`infer_hole`
label-only) vs later inference propagation phase.

## 5. Give every node a canonical serialization

Most important architectural rule to add:

For any semantic program:

```
parse → normalize → print
```

must produce **exactly one** canonical representation.

Never two valid machine representations of the same thing.

Examples:

- always `ADD[1, 2]` — never `ADD[1,2]` (spacing locked)
- never allow `1 + 2` into the canonical parser (pretty-printer only)

Makes Knot suitable for agents that repeatedly manipulate programs.

**Decide as D-FB11.** Lock normalize rules (whitespace, trailing commas, atom
forms) and whether printer-canonical (= normalize) differs from pretty.

## 6. Consider making names less special

Bare identifiers remain:

```
x
user
square
```

Do **not** require `VAR[x]` — noise without LLM benefit.

Bare atoms + `OP[...]` is the intended balance.

**Decide as D-FB12.** ACCEPT keep bare idents as atoms; REJECT `VAR[...]`.
