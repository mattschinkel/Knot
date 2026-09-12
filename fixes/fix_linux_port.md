# fix_linux_port — Windows → Linux move

## Problem
The Golem project was developed on Windows (PowerShell + `.venv\Scripts\python.exe`, CRLF line endings). After copying to Linux there was no venv, docs/scripts used Windows-only paths, sources were CRLF, `python3-tk` was missing for `crew_chats_viewer.py`, and git refused operations when run as root against a `matt`-owned tree ("dubious ownership"). Mid-Phase-2 WIP also left a broken `tests/checker/test_subtype.py` that aborted pytest collection, and a half-rewritten `subtype()` that failed Phase 0 type tests. Several AST unit tests still called constructors that never matched the real APIs (crew leftovers).

## Fix
1. Created Linux venv (Python 3.10) and installed `requirements.txt` + pytest.
2. Converted text sources from CRLF → LF; added `.gitattributes` (`* text=auto eol=lf`) so future cross-OS checkouts stay LF.
3. Restored Phase 0 `subtype()` (returns `bool`) after the aborted T2 rewrite.
4. Quarantined incomplete T2 tests as `tests/checker/test_subtype.py.wip`.
5. Rewrote mangled AST unit tests (`test_ast_expr/def/fn/op.py`) to match real constructors.
6. Installed system package `python3-tk` for the chat viewer.
7. Verified LAN llama-server (`http://192.168.0.50:8081/v1`, model `LocoOperator-4B`) and crew script imports.

## Result
`272 passed` under `.venv/bin/python -m pytest -q`. Linux run commands documented in `progress.md` Scripts.
