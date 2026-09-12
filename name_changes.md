# Name changes

| Old | New | When | Why |
|-----|-----|------|-----|
| Knot (working name) | Golem | 2026-09-12 | Author lock; site/package `golemlang`; ext `.gol` |
| Axiom (prior working name) | Golem | 2026-09-12 | Dropped with name lock |
| Nodigma (public candidate) | Golem | 2026-09-12 | Superseded by Golem lock |
| `src/knot/` | `src/golem/` | 2026-09-12 | Python package rename |
| `import knot` | `import golem` | 2026-09-12 | Package rename |
| `knotc` / `knotc_bridge` | `golemc` / `golemc_bridge` | 2026-09-12 | Self-host compiler rename |
| `*.knot` | `*.gol` | 2026-09-12 | Source extension lock |
| `ai_docs/axiom_design.md` | `ai_docs/golem_design.md` | 2026-09-12 | Design doc rename |
| `ai_docs/knot_agents.md` | `ai_docs/golem_agents.md` | 2026-09-12 | Agents doc rename |
| `KNOT_*` env vars | `GOLEM_*` | 2026-09-12 | Env prefix rename |
| TestDecl | InlineTest | 2026-09-12 | Avoid pytest collecting AST class as a test |
| TestCase | InlineCase | 2026-09-12 | Same (Test* prefix) |
| MatchExpr(pattern, body) | MatchExpr(scrutinee, cases=[MatchCase...]) | 2026-09-12 | Stage 0.5 MATCH[e,CASE[tag,body],...] |
