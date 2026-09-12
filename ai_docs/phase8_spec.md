# Phase 8 Spec — Modules + Dependencies

> Owner: Cursor. Decisions follow `ai_docs/axiom_design.md` §10.  
> Status: DECIDED — implementing.

Phase 8 adds **modules**, **exports**, **imports**, and **versioned depends**
with capability requirements. Canonical form stays OP-only (D-FB7). Type-record
sugar (`type User { ... }`) remains pretty-only / deferred — modules ship DEFs
and tests.

---

## 1. Scope

### In Phase 8
- Canonical AIR:
  - `MODULE[name, item..., EXPORT[n1,n2,...]]`
  - `IMPORT[mod, n1, n2, ...]` (names must be exported)
  - `DEPENDS[mod, version]` / `DEPENDS[mod, version, CAPS[cap...]]`
- AST: `ModuleDecl`, `ImportDecl`, `DependsDecl`, `ExportList`
- `ModuleRegistry`: register modules, resolve imports into a flat program
- Depends capability check via Phase 3 `check_capabilities`
- `link_program(items, registry, granted_caps) -> LinkedProgram | ErrorVal`
- Parse + `print_canonical`

### Explicitly OUT of Phase 8
- Filesystem package loading / search path — later (registry is in-memory)
- Semver range solving beyond exact version string match
- `type Name { fields }` surface syntax
- Circular import recovery heuristics (hard error on cycles)

---

## 2. Design decisions (DECIDED)

### D1 — MODULE shape
**DECISION:** `MODULE[name, bodyItem..., EXPORT[...]]`. EXPORT is required (may be empty `EXPORT[]`). Body items are DEF / TEST / PROPERTY / nested decls.

### D2 — IMPORT
**DECISION:** `IMPORT[mod, name...]` binds those exported names into the importing program. Missing export → ErrorVal. Empty name list after mod → import all exports.

### D3 — DEPENDS
**DECISION:** `DEPENDS[mod, version]` records a requirement. Optional `CAPS[cap...]` lists capabilities the dependency needs at link time. Version match is exact string equality on the registered module's version (default `"0"`).

### D4 — Registry
**DECISION:** In-memory `ModuleRegistry` keyed by name. `register(module, version="0")`. Linking does not mutate registered modules.

### D5 — Cycles
**DECISION:** Import graph cycles are rejected with `ErrorVal(kind="import_cycle")`.

### D6 — Drift
**DECISION:** Phase bump to 8; M1–M4 unchanged.

---

## 3. File layout

```
src/knot/
  modules.py    # ModuleDecl helpers, Registry, link_program
  ast.py        # ModuleDecl, ImportDecl, DependsDecl, ExportList
  parser.py     # MODULE/IMPORT/DEPENDS/EXPORT/CAPS
  canonical.py
tests/modules/
  test_parse_mod.py
  test_registry.py
  test_link.py
  test_depends_caps.py
  test_modules_prop.py
```

---

## 4. Definition of done

- [x] Spec decided
- [x] Parse/canonical MODULE/IMPORT/DEPENDS
- [x] Registry + link_program
- [x] Depends capability check
- [x] Cycle detection
- [x] Tests + drift phase 8

---

## 5. Tasks

| ID | Goal | File | Symbol | Test |
|----|------|------|--------|------|
| T1 | AST + parse/canonical | ast/parser | `ModuleDecl` | `test_parse_mod.py` |
| T2 | ModuleRegistry register/lookup | modules.py | `ModuleRegistry` | `test_registry.py` |
| T3 | link_program + import resolve | modules.py | `link_program` | `test_link.py` |
| T4 | DEPENDS + CAPS check | modules.py | `check_depends` | `test_depends_caps.py` |
| T5 | Props + drift phase 8 | docs | — | `test_modules_prop.py` |
