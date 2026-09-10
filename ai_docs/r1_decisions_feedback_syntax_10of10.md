# R1 decisions — syntax feedback toward 10/10 (2026-09-09)

Source: human-forwarded review in `ai_docs/feedback_syntax_10of10.md`
(stated-goal score 8.5/10 → target 10/10). R1 decided autonomously via
`ask_architect.py`.

| ID | Decision | Locked form |
|----|----------|-------------|
| D-FB1 | ACCEPT | Canonical = `NAME[ARGS]` (+atoms). FN = `FN[[params], body]`. Field access: `GET[obj, field]` only in canonical; `obj.field` is pretty-only. |
| D-FB2 | ACCEPT | One binding: `DEF[name, expr]` only. No `=`, no `def name =`, no LET in canonical. |
| D-FB3 | AMEND | Units mechanical: typed lits use `10:f64@meters`. Reject bare `10:meters` unless `meters` is a named type. |
| D-FB4 | ACCEPT | Holes first-class: `?`, `?:T`, `?:T@dim`, `?:FN[...]` (canonical node forms HOLE / HOLE[T] / …). |
| D-FB5 | ACCEPT | Machine errors: `ERR[code, path, expected, actual, fixes]` (or ERROR[…]) for generate→check→repair. |
| D-FB6 | AMEND | Graph is truth; canonical = rigid LLM serialization; pretty = humans only. Raise bar via rigidity, not sugar. |

**Phase 2: PAUSE** until GBNF/parser reflect D-FB1–D-FB5 (especially units + FN/DEF shape).

Top design-doc sections to update: §4 AST, §3.2/3.5 types+lits, §2 core principles.
