"""
setup_agent_ids.py — Auto-discovers all Foundry agent asst_xxx IDs
and patches .env with the correct values.

Run ONCE from the project root:
    python setup_agent_ids.py
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from pathlib import Path
ROOT = Path(__file__).resolve().parent

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient

# Agent names → env var key mapping
AGENT_MAP = {
    "planner-agent":                       "PLANNER_ASST_ID",
    "researcher-agent":                    "RESEARCHER_ASST_ID",
    "industry-news-trend-scanner":         "INDUSTRY_NEWS_ASST_ID",
    "competitive-landscape-researcher":    "COMPETITIVE_ASST_ID",
    "analyst-agent":                       "ANALYST_ASST_ID",
    "writer-agent":                        "WRITER_ASST_ID",
}

endpoint = os.getenv("AZURE_PROJECT_ENDPOINT")
print(f"Connecting to: {endpoint}")
print()

found = {}
with AgentsClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(exclude_interactive_browser_credential=True),
) as client:
    all_agents = list(client.list_agents())
    print(f"Found {len(all_agents)} agents in Foundry:\n")
    for a in all_agents:
        env_key = AGENT_MAP.get(a.name, "")
        marker = f"  -> {env_key}" if env_key else "  (not in pipeline)"
        print(f"  {a.id}   {a.name}{marker}")
        if env_key:
            found[env_key] = a.id

print()

# Patch .env
env_path = ROOT / ".env"
env_text = env_path.read_text(encoding="utf-8")

# Append or replace each key
for key, val in found.items():
    if key in env_text:
        # Replace existing line
        import re
        env_text = re.sub(rf"^{key}=.*$", f"{key}={val}", env_text, flags=re.MULTILINE)
    else:
        env_text += f"\n{key}={val}"

env_path.write_text(env_text, encoding="utf-8")

print("Patched .env with asst_ IDs:")
for k, v in found.items():
    print(f"  {k}={v}")

print()
print("Done! You can now run: python run_agent.py")
