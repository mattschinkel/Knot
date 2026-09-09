"""Pytest path setup: put src/ on sys.path so `import knot` works.

(Phase 0: no packaging yet. Once we add a pyproject we can switch to an
editable install and remove this.)
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_HERE, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
_TOOLS = os.path.join(_HERE, "tools")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)
