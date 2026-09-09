# CrewAI Windows console encoding (charmap)

## Problem
CrewAI 1.15 event-bus handlers print emoji (for example U+1F680). A default Windows PowerShell code page (cp1252) cannot encode those characters, so every log event raised:

`'charmap' codec can't encode character '\U0001f680'`

The crew still finished; only the console logs failed.

## Fix
`two_agent_crew.py` sets `PYTHONUTF8` / `PYTHONIOENCODING` and reconfigures `sys.stdout` and `sys.stderr` to UTF-8 with `errors="replace"` before CrewAI writes logs.
