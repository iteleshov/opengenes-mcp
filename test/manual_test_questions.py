import sys
from pathlib import Path

# Add the src directory to Python path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

import typer
from dotenv import load_dotenv
from eliot import start_action, log_call
from pycomfort.logging import to_nice_file, to_nice_stdout

from just_agents import llm_options
from just_agents.llm_options import LLMOptions
from just_agents.base_agent import BaseAgent
from opengenes_mcp.server import OpenGenesTools

app = typer.Typer()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
TEST_DIR = PROJECT_ROOT / "test"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create logs directory
LOGS_DIR.mkdir(parents=True, exist_ok=True)

@log_call()
def run_query(prompt_file: Path, query: str, options: LLMOptions = llm_options.GEMINI_2_5_PRO):
    load_dotenv(override=True)

    # Resolve prompt file path
    system_prompt_path = prompt_file if prompt_file.is_absolute() else PROJECT_ROOT / prompt_file

    with system_prompt_path.open("r", encoding="utf-8") as f:
        system_prompt = f.read().strip()

    # Initialize OpenGenes MCP server
    opengenes_server = OpenGenesTools()
    
    agent = BaseAgent(
        llm_options=options,
        tools=[opengenes_server.db_query],
        system_prompt=system_prompt
    )

    with start_action(action_type="run_query", query=query) as action:
        action.log(f"question send to the agent: {query}")
        result = agent.query(query)
        action.log(f"LLM AGENT ANSWER: {result}")
        return result

@app.command()
def test_opengenes():
    prompt_file = DATA_DIR / "prompt.txt"
    query_file = TEST_DIR / "test_opengenes.txt"
    
    with query_file.open("r", encoding="utf-8") as f:
        queries = f.readlines()
    
    to_nice_stdout()
    to_nice_file(LOGS_DIR / "test_opengenes_human.json", LOGS_DIR / "test_opengenes_human.log")

    for query in queries:
        query = query.strip()
        if query:
            run_query(prompt_file, query)

if __name__ == "__main__":
    app()