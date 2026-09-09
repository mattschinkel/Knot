"""Two-agent CrewAI example against the LAN llama-server.

Researcher reads data/product_briefing.txt with FileReadTool.
Writer turns those notes into a short action brief.

PowerShell (from this project directory):

    .\\.venv\\Scripts\\Activate.ps1
    python two_agent_crew.py

Or without activating the venv:

    .\\.venv\\Scripts\\python.exe two_agent_crew.py

If Activate.ps1 is blocked:

    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    .\\.venv\\Scripts\\Activate.ps1
    python two_agent_crew.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# CrewAI logs use emoji. Windows PowerShell defaults to cp1252 unless we
# force UTF-8 on the process streams before CrewAI writes anything.
os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from crewai import Agent, Crew, LLM, Task
from crewai_tools import FileReadTool

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
BRIEFING_PATH = DATA_DIR / "product_briefing.txt"

# openai/ prefix = OpenAI-compatible provider. CrewAI 1.15 sees base_url and
# talks to llama-server with the native OpenAI client (no LiteLLM hop).
# If the server loads a different model, change this string to match /v1/models.
local_llm = LLM(
    model="openai/LocoOperator-4B",
    base_url="http://192.168.0.50:8081/v1",
    api_key="87e00e86fbf95073800c49dff1c0f3b8",
    temperature=0.2,
    max_tokens=1024,
)

# Default file is pinned so the 4B model can call the tool without inventing a path.
read_briefing = FileReadTool(
    file_path=str(BRIEFING_PATH),
    base_dir=str(DATA_DIR),
)

researcher = Agent(
    role="Briefing Researcher",
    goal="Extract the facts from the local product briefing file.",
    backstory=(
        "You only trust the local briefing file. You use the file-read tool "
        "once, then list concrete facts. You do not invent details."
    ),
    llm=local_llm,
    tools=[read_briefing],
    verbose=True,
    allow_delegation=False,
    max_iter=8,
)

writer = Agent(
    role="Action Brief Writer",
    goal="Turn the researcher's notes into a short, practical action brief.",
    backstory=(
        "You write for the project owner. You stay concise, use the research "
        "notes only, and do not call tools."
    ),
    llm=local_llm,
    tools=[],
    verbose=True,
    allow_delegation=False,
    max_iter=6,
)

research_task = Task(
    description=(
        "Use the file-read tool to read the product briefing. You can omit "
        "file_path; the tool already points at the briefing. Then list: "
        "(1) the LLM host and currently loaded model, "
        "(2) which tools are adopted and the 1-2 agent limit, "
        "(3) the three near-term product questions."
    ),
    expected_output=(
        "A short bullet list of facts copied from the briefing: host/model, "
        "adopted tools and crew-size limit, and the three product questions."
    ),
    agent=researcher,
)

write_task = Task(
    description=(
        "Using only the researcher's notes, write a one-page action brief "
        "for the project owner. Include: current setup, recommended next "
        "step for the first user-visible feature, and how to handle a "
        "model switch on the server."
    ),
    expected_output=(
        "A short action brief with three headed sections: Current setup, "
        "Recommended next step, Model-switch checklist."
    ),
    agent=writer,
    context=[research_task],
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    verbose=True,
    tracing=False,
)


def main() -> None:
    if not BRIEFING_PATH.is_file():
        raise FileNotFoundError(f"Missing briefing file: {BRIEFING_PATH}")

    result = crew.kickoff()
    print("\n===== FINAL OUTPUT =====\n")
    print(result.raw)


if __name__ == "__main__":
    main()
