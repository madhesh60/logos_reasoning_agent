"""
Final diagnostic — tests the DEFINITIVE routing strategy:
  • planner/researcher/analyst → thread-based Agents API (with GUID)
  • writer → Responses API (name+version)

Run from the project root:
    python test_foundry_connection.py
"""
import asyncio
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from src.foundry.client import FoundryAgentClient

# Simple prompt asking for a minimal JSON response
TEST_PROMPT = (
    "Reply with EXACTLY this JSON and nothing else (no markdown, no explanation):\n"
    '{"status": "ok", "agent": "test"}'
)


async def main():
    print("=" * 70)
    print("FOUNDRY CONNECTION DIAGNOSTIC (Final)")
    print("=" * 70)
    print(f"Endpoint: {os.getenv('AZURE_PROJECT_ENDPOINT', 'NOT SET')}\n")

    agents = [
        # Tool-enabled: thread-based via GUID
        ("PLANNER",    "planner-agent",    os.getenv("PLANNER_AGENT_VERSION",    "8"), os.getenv("PLANNER_AGENT_ID")),
        ("RESEARCHER", "researcher-agent", os.getenv("RESEARCHER_AGENT_VERSION", "7"), os.getenv("RESEARCHER_AGENT_ID")),
        ("ANALYST",    "analyst-agent",    os.getenv("ANALYST_AGENT_VERSION",    "4"), os.getenv("ANALYST_AGENT_ID")),
        # No-tool: Responses API via name+version (agent_id=None)
        ("WRITER",     "writer-agent",     os.getenv("WRITER_AGENT_VERSION",     "4"), None),
    ]

    results = {}
    for label, name, version, agent_id in agents:
        strategy = f"thread (id={agent_id[:8]}...)" if agent_id else f"responses (name+version)"
        print(f"{label}: {strategy}")
        print(f"  Calling ...", end=" ", flush=True)
        client = FoundryAgentClient(name, version, agent_id=agent_id)
        try:
            raw = await client.call_agent_raw(TEST_PROMPT, max_retries=1)
            print(f"[OK]   {len(raw)} chars: {raw[:100].strip()}")
            results[label] = True
        except Exception as e:
            print(f"[FAIL] {str(e)[:120]}")
            results[label] = False
        print()

    print("=" * 70)
    ok_count    = sum(1 for v in results.values() if v)
    fail_count  = sum(1 for v in results.values() if not v)
    print(f"Results: {ok_count} OK / {fail_count} will use local fallback")
    if fail_count == 0:
        print("All Foundry agents reachable — full A2A pipeline active!")
    else:
        failed = [k for k, v in results.items() if not v]
        print(f"Failed agents ({', '.join(failed)}) will use local Phi-4 fallback.")
        print("Pipeline will still produce a complete report.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
