# Progress

## Highlights & features
- Evaluated free/open-source LLM agent-swarm options for building a product with a local LLM.
- Recommended stack: OpenHands for actual coding, CrewAI if a role-based swarm is required, LangGraph if we need a custom production pipeline.
- User already has OpenHands and a coding model on a server. OpenHands work runs on that server; a local browser is enough unless we add a separate swarm layer.
- CrewAI 1.15.20 and crewai-tools 1.15.20 are installed in `.venv` (Python 3.11.9).
- Wired CrewAI to the LAN llama-server OpenAI-compatible endpoint:
  `http://192.168.0.50:8081/v1`, model `LocoOperator-4B`.
- Evaluated ChatGPT's Axiom / AIR language options for an LLM-native programming language. Best core: typed expression tree as the write format, stable node IDs so edits are graph operations, structured compiler errors/holes. Defer agents, knowledge graphs, uncertainty, and intent-compilation until the kernel exists.
- Wrote detailed design: `ai_docs/axiom_design.md` (goals, type system, AST, effects/capabilities/contracts, holes, errors, edits, modules, AI tools, build phases).
- Working name for the language is now **Knot** (chosen by author 2026-09-08). Like "Axiom" it collides (Knot = real functional-relational language `ilyakooo0/knot` + `raultov/knot` Rust MCP indexer), so working-name only; **Nodigma** remains the verified-clean public candidate for release.
- Designed the LLM agent build crew: `ai_docs/knot_agents.md` — 6 roles (Architect, Kernel Engineer = deterministic back-end, AI Front-end Engineer = judgment half, Verifier, DX Engineer, Scribe) mapped to the §16 build phases, with a two-half handoff invariant and a phased activation table (start with R1+R2+R4 at Phase 0). Realistic for the 4B local LLM: human stays architect, agents are scoped implementers/reviewers.
- Built the one-page build dashboard: `web/index.html` — self-contained (inline CSS+JS, no build step, no HTTPS, works via file://). Renders from a single `STATUS` object that R6 Scribe updates after each phase gate. Shows name status, all 12 build phases with status/owner/notes + progress bar, active crew, open questions, design open items, recent fixes. Owner = R6 Scribe (documented in `ai_docs/knot_agents.md` R6 + dashboard data contract).
- Added the "Syntax quality bar: 10/10 for LLMs" principle to `ai_docs/axiom_design.md` §2 — the canonical syntax is held to an exceptional standard as a fit for LLM generation/editing/reasoning; features that degrade LLM reliability do not ship.
- Added "Operating rules for agents" (`ai_docs/knot_agents.md` §6) adopting the author's applicable Cursor rules (JAL/Android rules ignored): no hacks/workarounds, minimize targeted heuristics in compiler code, continuous self-improvement, keep progress.md current, log renames in `name_changes.md`, write `fixes/fix_*.md` per issue, review `ai_docs/`, author = Matthew Schinkel, git/backup discipline, no HTTPS, no `&&` in PowerShell, .css version bump, don't assume a stopped command failed, make/MSYS2 paths.
- Name search (2026-09-08): checked ~30 candidates; the obvious-root space (node/graph/knot/syntax) AND construction-craft real words (cairn/ashlar/quoin) AND short coined names (zynta/korvex/vyntra/kynex) ALL collide. Cairn & Ashlar are near-identical competitor languages. Cleanest verified candidate = **Nodigma** (nodigma.com NXDOMAIN, no collisions). Added "second-round findings" cluster (Cairn, Ashlar, AILANG, Causari, Grafema, Nodus, Knot) to `ai_docs/axiom_design.md` §20 — sharpens our novelty claim: content-addressed graph + blast-radius + AI-native + MCP is now table stakes, not a differentiator.

## TODOs
- Confirm whether the server already serves the OpenHands UI (full Canvas) or backend-only.
- If building the LLM-native language: specify the core value model, type system, and expression/AST (with stable node IDs) before inventing syntax. Do not start with agent/knowledge/uncertainty features.
- Start Phase 0 of Axiom: define value representation, type representation, and units/dimensions (see `ai_docs/axiom_design.md`).
- Decide node ID scheme (author-pinned vs compiler-assigned) — RESOLVED in `ai_docs/axiom_design.md` §21. Decision: LLM addresses nodes by structural path + optional symbolic labels; numeric IDs are compiler-internal, never authored in source. `@` introduces a label, not a numeric ID.
- Competitive scan (Phase 0.5): DONE — all six projects verified real. Findings + must-adopt features in `ai_docs/axiom_design.md` §20. Top adopts: GBNF grammar for constrained decoding, compiler-as-MCP-server, token-budgeted `kb` tool, `--llm` output mode, sub-200ms compile, errors-as-values, two-half compiler, prohibitions-as-constraints.
- Finish wish-list review (see `ai_docs/axiom_design.md` §19): DONE — must-have features from competitive scan folded into Tier 1 (#11-14) and Tier 2 (#22-29). Build phases updated (§16) to include GBNF grammar (Phase 1), errors-as-values + two-half compiler (Phase 5/9), compiler-as-MCP + kb + --llm mode (Phase 12).
- Decide which Tier 3 items make v1, and which rejected items stay rejected.
- Answer the 4 open questions in `ai_docs/knot_agents.md` §5 (Phase 0 host language Python vs Rust; Architect as hierarchical manager vs peer; shell-exec tool gating; repo layout) before spinning up the crew.
- Build the Phase 0 crew (R1 Architect + R2 Kernel Engineer + R4 Verifier) as a CrewAI `Crew` against the LAN llama-server, extending `two_agent_crew.py`.
- Specify the Knot string stdlib (slice/index/length/char<->int) — flagged "NOT yet specified" in `ai_docs/axiom_design.md` §22.5; add to Phase 0/stdlib.
- Specify the bytecode VM target — flagged "NOT yet specified" in §22.5; add to Phase 9.
- (Optional) Build `ask_architect.py` — a CLI to query R1 Architect against the LAN llama-server with the design doc + roles as context (offered last turn).
- Benchmark 2-3 candidate canonical syntaxes by token count + generation accuracy before locking AIR.
- Pick a real public name (NOT "Axiom"). Collisions found: Axiom CAS (own language SPAD), Axiom Math (AI + formal proofs, unicorn), Axiom Inc. (agent-native observability), Axiom Space, Axiom Law. `axiom.com` parked. "Axiom" is a working name only in the design doc. RESOLVED (pending author confirmation + domain/trademark registration): proposed name = **Nodigma** (no-DIG-ma; node + enigma/paradigm). Verified clean 2026-09-08: `nodigma.com` NXDOMAIN, no company/language/software/GitHub/PyPI named Nodigma (only misspellings ODigMa, Nodigmarket24). Alternate: Syntagm (`syntagm.com` NXDOMAIN). See `ai_docs/axiom_design.md` "NOTE ON THE NAME". Author should register `nodigma.com` + check USPTO before locking.
- END GOAL: self-hosting (Axiom compiles its own compiler). Bootstrap plan in `ai_docs/axiom_design.md` §22. Stage 0 in Python (recommendation) targeting a bytecode VM; bootstrap the deterministic lowering compiler in Axiom first; add the AI front-end (ai-effectful) after self-hosting; native (LLVM/C) backend later. Language must add: string stdlib, bytecode VM target, `exec` capability (native backend only).
- If the llama-server loaded model is switched, update the `model=` string in `two_agent_crew.py` to match `/v1/models` or requests 404.
- When the temporary bearer token is rotated, edit `LLAMA_API_KEY` in `/etc/default/llama-server` on the Linux host, `systemctl restart llama-server`, and update `api_key` in `two_agent_crew.py`.

## Previous issues
- `fix_crewai_windows_console_encoding.md` — CrewAI event-bus logs use emoji; Windows cp1252 raised `charmap` encode errors. `two_agent_crew.py` now reconfigures stdout/stderr to UTF-8.

## Scripts
- `web/index.html` — one-page Knot build dashboard (R6 Scribe owns it). Open directly in a browser, or serve plain HTTP from the `web/` folder: `.\.venv\Scripts\python.exe -m http.server 8000` (then http://localhost:8000). No HTTPS.
- `two_agent_crew.py` — 2-agent CrewAI example against the LAN llama-server. From the project directory in PowerShell:
  `.\.venv\Scripts\Activate.ps1` then `python two_agent_crew.py`
  or `.\.venv\Scripts\python.exe two_agent_crew.py`
- `requirements.txt` — `crewai==1.15.20` and `crewai-tools==1.15.20`
- Recreate the venv if needed:
  `python -m venv .venv`
  `.\.venv\Scripts\python.exe -m pip install --upgrade pip`
  `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
- Check which model llama-server currently has loaded:
  `Invoke-RestMethod -Uri http://192.168.0.50:8081/v1/models -Headers @{Authorization='Bearer <key-from-two_agent_crew.py>'}`
