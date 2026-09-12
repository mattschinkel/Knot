# fix: knotc compile-all deterministic AIR

## Problem
Stage-1 knotc could not compile the full deterministic Knot surface needed to
self-host beyond the Stage-2 subset: missing COND→IF, PAR/SEQ opcodes,
REF/DEREF natives, UNIT/nil, double-quoted strings, `;` skip, DEPENDS/MODEL/TOOL/
VERSION/EXPORT stubs, selective IMPORT, CASE string tags, and SUM Ident-tag sugar.

## Fix
- **lexer.knot**: balanced `lex_string_q` escapes; `"` (cp34) strings; skip `;`.
- **parser.knot**: UNIT/nil; typed float/str; CASE Ident|Str tags; selective
  IMPORT; stub skip-brackets for DEPENDS/MODEL/TOOL/VERSION/EXPORT.
- **codegen.knot**: COND like IF; PAR/SEQ opcodes 80/81; REF region Ident→string;
  DEREF/UNSAFE; SUM Var tag→StrLit; skip decl stubs via `is_skip_item`.
- **check.knot**: accept new decl tags as skip items.
- **Host**: REF/DEREF natives + Par/Seq/Ref/Deref/Unsafe lowering (prior turn).
- Gate: `tests/selfhost/test_compile_all_knot.py`.

## Remaining (host-only / not AIR→VM)
AI INVOKE runtime, MCP, surgical edits stay Python. Multi-file IMPORT link in
Knot still uses harness `resolve_stage1_imports` + host bootstrap for the first
image.
