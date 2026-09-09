"""chat_capture.py - record every crew agent's chat turns to disk.

Hooks CrewAI's event bus (crewai.events) so that, while a crew runs, each
agent's LLM turns (prompt + response) and tool calls are appended to a
per-task, per-role JSONL file under chats/<task_id>/<role>.jsonl. The
GUI (crew_chats_viewer.py) reads these to show all crew members' chats.

Deterministic, no LLM. Public (not local-only). Importable:
    from chat_capture import start, stop
    start("T1")        # before crew.kickoff()
    ... crew runs ...
    stop()              # after, to unregister listeners

Role mapping: CrewAI agent .role strings are matched (substring) to the
Knot crew ids R1..R6 (see knot_agents.md).
"""
from __future__ import annotations

import json
import os
import re
import threading
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHATS = PROJECT_DIR / "chats"

# (substring in agent.role, rid, short label)
ROLE_MAP = (
    ("Architect", "R1", "Architect"),
    ("Kernel Engineer", "R2", "Kernel Engineer"),
    ("AI Front-end", "R3", "AI Front-end"),
    ("Verifier", "R4", "Verifier"),
    ("DX Engineer", "R5", "DX Engineer"),
    ("Scribe", "R6", "Scribe"),
)

_lock = threading.Lock()
_handlers: list = []  # (event_type, fn)
_active_task: str | None = None


def role_id(role_str: str | None) -> tuple[str, str]:
    if not role_str:
        return ("R?", "Unknown")
    for sub, rid, label in ROLE_MAP:
        if sub.lower() in role_str.lower():
            return (rid, label)
    return ("R?", role_str[:24])


def _rid_from_agent(event) -> tuple[str, str]:
    role_str = getattr(event, "agent_role", None)
    return role_id(role_str)


def _append(task_id: str, rid: str, obj: dict) -> None:
    d = CHATS / task_id
    d.mkdir(parents=True, exist_ok=True)
    line = json.dumps(obj, ensure_ascii=False, default=str)
    with _lock:
        with (d / f"{rid}.jsonl").open("a", encoding="utf-8") as f:
            f.write(line + "\n")


def _on_llm_completed(source, event) -> None:
    if _active_task is None:
        return
    rid, label = _rid_from_agent(event)
    msgs = getattr(event, "messages", None)
    resp = getattr(event, "response", None)
    _append(_active_task, rid, {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "kind": "llm",
        "call_id": getattr(event, "call_id", ""),
        "agent": label,
        "messages": msgs,
        "response": resp if isinstance(resp, str) else str(resp),
    })


def _on_tool_finished(source, event) -> None:
    if _active_task is None:
        return
    rid, label = _rid_from_agent(event)
    _append(_active_task, rid, {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "kind": "tool",
        "agent": label,
        "tool_name": getattr(event, "tool_name", ""),
        "tool_args": getattr(event, "tool_args", ""),
        "output": getattr(event, "output", ""),
    })


def start(task_id: str) -> None:
    """Register event-bus listeners for the given task. Call before kickoff."""
    global _active_task
    stop()  # idempotent: never stack listeners
    _active_task = task_id
    from crewai.events import crewai_event_bus as bus
    from crewai.events.types.llm_events import LLMCallCompletedEvent
    from crewai.events.types.tool_usage_events import ToolUsageFinishedEvent
    bus.register_handler(LLMCallCompletedEvent, _on_llm_completed)
    bus.register_handler(ToolUsageFinishedEvent, _on_tool_finished)
    _handlers.append((LLMCallCompletedEvent, _on_llm_completed))
    _handlers.append((ToolUsageFinishedEvent, _on_tool_finished))


def stop() -> None:
    """Unregister all listeners added by start()."""
    global _active_task
    from crewai.events import crewai_event_bus as bus
    for et, fn in _handlers:
        bus.off(et, fn)
    _handlers.clear()
    _active_task = None


def record(rid: str, obj: dict, task_id: str = "_architect") -> None:
    """Record a turn for an agent that does NOT use the CrewAI event bus
    (e.g. R1 Architect via raw openai calls in architect_phase.py)."""
    obj.setdefault("ts", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    _append(task_id, rid, obj)
