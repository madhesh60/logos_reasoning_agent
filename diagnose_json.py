"""
Diagnostic: capture raw model response from planner to see what JSON is malformed.
"""
import asyncio, sys, os
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

async def main():
    from src.utils.config import load_environment, get_chat_model
    load_environment()

    from langchain_core.messages import HumanMessage, SystemMessage
    llm = get_chat_model(temperature=0.3)

    query = "What are the main risks of investing in AI startups in India?"
    prompt = f"""Analyze the following research query and create a detailed decomposition plan:

QUERY: {query}

Return ONLY a valid JSON object with this exact structure:
{{
    "plan_id": "plan_001",
    "original_query": "{query}",
    "intent_summary": "Summary here",
    "total_tasks": 3,
    "estimated_total_time_seconds": 90,
    "tasks": [
        {{
            "task_id": "task_001",
            "task_type": "web_search",
            "description": "Search for AI startup risks in India",
            "priority": "high",
            "depends_on": [],
            "estimated_duration_seconds": 30,
            "agent": "Researcher",
            "output_format": "json",
            "search_queries": ["AI startup investment risks India 2025"],
            "key_aspects": ["regulatory", "market", "competition"]
        }}
    ],
    "execution_order": ["task_001"],
    "required_tools": ["web_search"],
    "confidence_score": 0.85,
    "reasoning": "Plan derived from query analysis"
}}"""

    print("Sending to model...")
    response = await llm.ainvoke([
        SystemMessage(content="You are a research planning assistant. Return ONLY valid JSON, no other text."),
        HumanMessage(content=prompt)
    ])

    raw = response.content
    print(f"\n=== RAW RESPONSE ({len(raw)} chars) ===")
    # Print up to 3000 chars to see what the problem is
    print(raw[:3000])
    
    # Find the problematic area around char 1276
    if len(raw) > 1200:
        print(f"\n=== PROBLEM AREA (chars 1200-1350) ===")
        print(repr(raw[1200:1350]))

    # Now try json-repair
    print("\n=== Trying json-repair ===")
    try:
        import json_repair
        # Strip think block first
        import re
        clean = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
        # Strip markdown fences
        clean = re.sub(r'^```(?:json)?\s*', '', clean, flags=re.MULTILINE)
        clean = re.sub(r'\s*```$', '', clean, flags=re.MULTILINE).strip()
        
        result = json_repair.repair_json(clean, return_objects=True)
        print(f"json-repair succeeded! Keys: {list(result.keys()) if isinstance(result, dict) else type(result)}")
    except Exception as e:
        print(f"json-repair also failed: {e}")

asyncio.run(main())
