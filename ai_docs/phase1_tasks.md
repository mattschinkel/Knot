# Phase 1 Tasks (drafted by R1)

```markdown
# Phase 1 Tasks Checklist

## Overview
This document defines the fragment-sized tasks for Phase 1 of the Knot kernel. Each task is small enough for a 4B model to implement. Tasks are ordered by dependency and cover AST, parser, GBNF grammar, addressing, and property tests. The final task is the drift-check gate.

---

## Tasks

| ID | Goal | File | Function/Class | Test |
|---|------|------|----------------|------|
| T1 | Define AST base node with id, path, label | `src/knot/ast.py` | `Node` abstract base class | `tests/ast/test_ast_base.py` |
| T2 | Implement ExprNode with child nodes | `src/knot/ast.py` | `ExprNode` class | `tests/ast/test_ast_expr.py` |
| T3 | Implement TypeNode with child nodes | `src/knot/ast.py` | `TypeNode` class | `tests/ast/test_ast_type.py` |
| T4 | Implement DefNode with body | `src/knot/ast.py` | `DefNode`, `TypeDefNode` | `tests/ast/test_ast_def.py` |
| T5 | Implement OpExpr and binary ops | `src/knot/ast.py` | `OpExpr` | `tests/ast/test_ast_op.py` |
| T6 | Implement IfExpr and CondExpr | `src/knot/ast.py` | `IfExpr`, `CondExpr` | `tests/ast/test_ast_cond.py` |
| T7 | Implement MatchExpr and arms | `src/knot/ast.py` | `MatchExpr`, `Arm` | `tests/ast/test_ast_match.py` |
| T8 | Implement LetExpr and WithExpr | `src/knot/ast.py` | `LetExpr`, `WithExpr` | `tests/ast/test_ast_bind.py` |
| T9 | Implement FieldAccess and Get/SET | `src/knot/ast.py` | `FieldAccess`, `GetExpr`, `SetExpr` | `tests/ast/test_ast_access.py` |
| T10 | Implement FnExpr and CallExpr | `src/knot/ast.py` | `FnExpr`, `CallExpr` | `tests/ast/test_ast_fn.py` |
| T11 | Implement HoleExpr with type | `src/knot/ast.py` | `HoleExpr` | `tests/ast/test_ast_hole.py` |
| T12 | Implement LitExpr and TypedLit | `src/knot/ast.py` | `LitExpr`, `TypedLit` | `tests/ast/test_ast_lit.py` |
| T13 | Implement IdentExpr and UnitExpr | `src/knot/ast.py` | `IdentExpr`, `UnitExpr` | `tests/ast/test_ast_ident.py` |
| T14 | Implement structural path generation | `src/knot/addressing.py` | `generate_path()` | `tests/addressing/test_path.py` |
| T15 | Implement symbolic label assignment | `src/knot/addressing.py` | `assign_label()` | `tests/addressing/test_label.py` |
| T16 | Implement node ID generation | `src/knot/addressing.py` | `generate_id()` | `tests/addressing/test_id.py` |
| T17 | Implement canonical bracket parser | `src/knot/parser.py` | `parse_program()`, `parse_expr()` | `tests/parser/test_parser_bracket.py` |
| T18 | Implement field access parsing | `src/knot/parser.py` | `parse_field_access()` | `tests/parser/test_parser_field.py` |
| T19 | Implement type annotations on literals | `src/knot/parser.py` | `parse_typed_lit()` | `tests/parser/test_parser_type.py` |
| T20 | Implement hole parsing | `src/knot/parser.py` | `parse_hole()` | `tests/parser/test_parser_hole.py` |
| T21 | Implement function definition parsing | `src/knot/parser.py` | `parse_def()`, `parse_fn()` | `tests/parser/test_parser_fn.py` |
| T22 | Implement binary serializer | `src/knot/bin.py` | `serialize()`, `deserialize()` | `tests/bin/test_bin.py` |
| T23 | Implement pretty printer | `src/knot/printer.py` | `print_ast()` | `tests/printer/test_printer.py` |
| T24 | Implement GBNF grammar (no numeric IDs) | `src/knot/grammar/gbnf.py` | `Program`, `Def`, `Expr`, `Lit`, `Ident`, `FieldAccess`, `Get`, `Set`, `Op`, `Comparison`, `Logic`, `Control`, `Access`, `Collection`, `Binding`, `Hole`, `Function`, `ParamList`, `Param`, `Body`, `Unit` | `tests/grammar/test_gbnf.py` |
| T25 | Implement property tests for AST | `tests/ast/` | `test_roundtrip`, `test_id_uniqueness`, `test_path_stability` | `tests/ast/test_ast_prop.py` |
| T26 | Implement property tests for bin | `tests/bin/` | `test_roundtrip`, `test_id_stability` | `tests/bin/test_bin_prop.py` |
| T27 | Implement property tests for grammar | `tests/grammar/` | `test_valid_syntax`, `test_no_numeric_ids` | `tests/grammar/test_gbnf_prop.py` |
| T28 | Implement property tests for parser | `tests/parser/` | `test_bracket_only`, `test_field_sugar`, `test_hole_support` | `tests/parser/test_parser_prop.py` |
| T29 | Implement property tests for printer | `tests/printer/` | `test_roundtrip`, `test_no_bracket` | `tests/printer/test_printer_prop.py` |
| T30 | Run drift-check gate on benchmark suite | `src/knot/drift.py` | `check()` | `tests/drift/test_drift.py` |

---

## Final Task: Drift-Check Gate (T30)
- **Owner:** R3 + R4
- **File:** `src/knot/drift.py`
- **Function:** `check()`
- **Test:** `tests/drift/test_drift.py`
- **Requirement:** Run over benchmark suite, compare to `docs/drift_baseline.json`, flag any regression to R1; **do NOT close the phase until the gate passes** (PENDING metrics don't fail it).
```