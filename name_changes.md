# Name changes

| Old | New | When | Why |
|-----|-----|------|-----|
| TestDecl | InlineTest | 2026-09-12 | Avoid pytest collecting AST class as a test |
| TestCase | InlineCase | 2026-09-12 | Same (Test* prefix) |
| MatchExpr(pattern, body) | MatchExpr(scrutinee, cases=[MatchCase...]) | 2026-09-12 | Stage 0.5 MATCH[e,CASE[tag,body],...] |
