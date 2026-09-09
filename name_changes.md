# Name changes

Log of renames for variables, functions, procedures, and the project/language name.

## 2026-09-08 — Language working name: Axiom -> Knot
- The language's working name was renamed from **Axiom** to **Knot**.
- Reason: "Axiom" collides with real products (Axiom CAS / SPAD language,
  Axiom Math AI+formal-proofs unicorn, Axiom Inc. agent-native observability,
  axiom.com parked). See `ai_docs/axiom_design.md` "NOTE ON THE NAME".
- "Knot" is also a working name only — it collides too (Knot = real
  functional-relational language `ilyakooo0/knot`; `raultov/knot` Rust MCP
  indexer). It is NOT the public release name.
- Proposed public release name (verified clean, not yet registered):
  **Nodigma** (nodigma.com NXDOMAIN). See `ai_docs/axiom_design.md`
  "NOTE ON THE NAME" and `progress.md`.
- Note: the design doc file is still named `axiom_design.md` for history;
  its content now uses the working name "Knot". The file may be renamed to
  `knot_design.md` in a later pass (record that rename here if done).

## Conventions
- One row per rename: date, what changed (old -> new), reason, links.
- When a file is renamed, log it here too.
