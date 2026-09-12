# Phase 6 Spec — Edit Operations

> Owner: Cursor. Decisions follow `ai_docs/axiom_design.md` §9 and §21.  
> Status: DECIDED — implementing.

Phase 6 makes **surgical graph edits** the primary modification interface.
The LLM does not rewrite files; it issues ops addressed by structural path
or label. The kernel applies the edit immutably, re-validates, and reports
the **blast radius**.

Applying Phase 5 `REPLACE[...]` repair suggestions lands here.

---

## 1. Scope

### In Phase 6
- Structural path navigation: `get_at` / immutable `replace_at` / `delete_at` / `insert_at`
- Label addressing via `addressing.lookup_label` (precedence: label → path)
- Edit ops as AIR `OP[...]`:
  - `REPLACE[PATH, EXPR]` — replace node at path
  - `DELETE[PATH]` — remove child at path
  - `INSERT[PATH, INDEX, EXPR]` — insert child under parent path
  - `RENAME[PATH, IDENT]` — rename `DefNode` / update IdentExpr at path
  - `REPLACE_MATCH[PATTERN, EXPR]` — unique structural match; `_` is wildcard
- `apply_edit(root, op) -> EditResult` (new tree + report)
- `blast_radius`: changed path + ancestor paths (deterministic; full dep graph deferred)
- Revalidation via `compile_check` / `diagnose` on the new tree
- Parse edit ops through existing `OpExpr` parser (PATH is `[seg,...]` like ERR)

### Explicitly OUT of Phase 6
- Module/import graph dependencies — Phase 8
- Full dataflow dependency blast radius — later refinement
- CREATE type / field schema DSL sugar (use REPLACE/INSERT on AST instead)
- Concurrent edits / transactions — Phase 11

---

## 2. Design decisions (DECIDED)

### D1 — Addressing (§21)
**DECISION:** Edits address by label first, else structural path. Numeric IDs may appear in blast-radius *reports* only, never as authored edit targets in source.

### D2 — Paths
**DECISION:** Path = `[seg,...]` where seg is ident or number. Numbers index `children` / arg lists. Idents name roles: `body`, `cond`, `then`, `else`, `fn`, `params`, or a `DefNode.name` when root is a program list.

### D3 — Immutability
**DECISION:** Edits return a new tree; inputs are not mutated.

### D4 — Unique pattern match
**DECISION:** `REPLACE_MATCH` requires exactly one match; 0 or 2+ → ErrorVal / failed EditResult (no silent multi-replace).

### D5 — Wildcard
**DECISION:** Ident `_` in a pattern matches any node (does not bind).

### D6 — Blast radius (v1)
**DECISION:** Report the replaced path, all proper prefixes (ancestors), and any label on the changed node. Downstream name-use analysis is OUT (Phase 8+).

### D7 — Drift
**DECISION:** Phase bump to 6; M1–M4 unchanged; M5 PENDING.

---

## 3. File layout

```
src/knot/
  edits.py       # paths, apply_edit, pattern match, EditResult, blast_radius
tests/edits/
  test_paths.py
  test_apply.py
  test_pattern.py
  test_blast.py
  test_edits_prop.py
```

---

## 4. Definition of done

- [x] Spec decided
- [x] Path get/replace/delete/insert
- [x] apply_edit for REPLACE/DELETE/INSERT/RENAME/REPLACE_MATCH
- [x] Unique pattern REPLACE with `_`
- [x] EditResult with blast_radius + revalidation
- [x] Tests + drift phase 6

---

## 5. Tasks

| ID | Goal | File | Symbol | Test |
|----|------|------|--------|------|
| T1 | get_at / replace_at / delete_at / insert_at | `edits.py` | `get_at` | `test_paths.py` |
| T2 | apply_edit REPLACE/DELETE/INSERT/RENAME | `edits.py` | `apply_edit` | `test_apply.py` |
| T3 | REPLACE_MATCH + `_` wildcard | `edits.py` | `replace_match` | `test_pattern.py` |
| T4 | blast_radius + revalidate in EditResult | `edits.py` | `EditResult` | `test_blast.py` |
| T5 | Property tests + drift phase 6 | tests/docs | — | `test_edits_prop.py` |
