"""
Foundry Agent Client — thread-based execution for tool-enabled agents
======================================================================
Uses azure-ai-agents AgentsClient with create_thread_and_process_run()
which correctly handles Bing web search and MCP toolbox calls.

Strategy:
  • planner / researcher / analyst  → AgentsClient thread+run (GUID-based, tool-safe)
  • writer                          → AIProjectClient Responses API (no tools, faster)
"""

import os
import asyncio
import structlog
from typing import Optional, Dict, Any
import json_repair

from azure.identity import DefaultAzureCredential

logger = structlog.get_logger(__name__)

_ENDPOINT = os.getenv(
    "AZURE_PROJECT_ENDPOINT",
    "https://reasoning-agent-hack2-resource.services.ai.azure.com/api/projects/reasoning-agent-hack2",
)


# ---------------------------------------------------------------------------
# Strategy A — AgentsClient thread+run  (for tool-enabled agents)
# ---------------------------------------------------------------------------
def _call_via_thread(agent_id: str, prompt: str) -> str:
    """
    Calls a Foundry agent by GUID using the thread-based Agents API.
    Handles Bing search / MCP tools correctly.
    Requires: pip install azure-ai-agents
    """
    from azure.ai.agents import AgentsClient
    from azure.ai.agents.models import AgentThreadCreationOptions, ThreadMessageOptions

    with AgentsClient(
        endpoint=_ENDPOINT,
        credential=DefaultAzureCredential(exclude_interactive_browser_credential=True),
    ) as client:
        run = client.create_thread_and_process_run(
            agent_id=agent_id,
            thread=AgentThreadCreationOptions(
                messages=[
                    ThreadMessageOptions(role="user", content=prompt)
                ]
            ),
        )

        if run.status == "failed":
            raise RuntimeError(
                f"Agent run failed (id={agent_id}): {getattr(run, 'last_error', run.status)}"
            )

        # Fetch messages from the completed thread
        messages = client.messages.list(thread_id=run.thread_id)
        for msg in messages:
            if msg.role == "assistant":
                parts = []
                for block in msg.content:
                    if hasattr(block, "text"):
                        parts.append(block.text.value)
                if parts:
                    return "\n".join(parts)

        raise RuntimeError(f"No assistant reply found for agent {agent_id}")


# ---------------------------------------------------------------------------
# Strategy B — Responses API  (for no-tool agents like writer)
# ---------------------------------------------------------------------------
def _call_via_responses(name: str, version: str, prompt: str) -> str:
    """
    Calls a Foundry agent via the Responses API with agent_reference.
    Works for agents WITHOUT attached tools.
    """
    from azure.ai.projects import AIProjectClient

    with AIProjectClient(
        endpoint=_ENDPOINT,
        credential=DefaultAzureCredential(exclude_interactive_browser_credential=True),
    ) as client:
        oc = client.get_openai_client()
        resp = oc.responses.create(
            input=[{"role": "user", "content": prompt}],
            extra_body={
                "agent_reference": {
                    "name":    name,
                    "version": version,
                    "type":    "agent_reference",
                }
            },
        )
        return resp.output_text


# ---------------------------------------------------------------------------
# FoundryAgentClient — public interface
# ---------------------------------------------------------------------------
class FoundryAgentClient:
    """
    Unified client that selects the right call strategy automatically:
      • agent_id provided → AgentsClient thread+run  (tool-enabled agents)
      • agent_id is None  → Responses API name+version (no-tool agents)
    """

    def __init__(
        self,
        agent_name: str,
        agent_version: str,
        agent_id: Optional[str] = None,
    ):
        self.agent_name    = agent_name
        self.agent_version = agent_version
        self.agent_id      = agent_id

    def _sync_call(self, prompt: str) -> str:
        if self.agent_id:
            return _call_via_thread(self.agent_id, prompt)
        return _call_via_responses(self.agent_name, self.agent_version, prompt)

    async def call_agent_raw(self, prompt: str, max_retries: int = 2) -> str:
        loop = asyncio.get_running_loop()
        last: Exception | None = None

        strategy = "thread" if self.agent_id else "responses"
        logger.info("calling_foundry_agent", agent=self.agent_name, strategy=strategy)

        for attempt in range(1, max_retries + 2):
            try:
                result = await loop.run_in_executor(None, self._sync_call, prompt)
                logger.info("foundry_agent_success", agent=self.agent_name)
                return result
            except Exception as exc:
                last = exc
                logger.warning(
                    "foundry_agent_failed",
                    agent=self.agent_name, attempt=attempt, error=str(exc)
                )
                if attempt <= max_retries:
                    await asyncio.sleep(min(2 ** attempt, 20))

        logger.error("foundry_agent_exhausted", agent=self.agent_name, error=str(last))
        raise last  # type: ignore[misc]

    async def call_agent_json(self, prompt: str) -> Dict[str, Any]:
        raw = await self.call_agent_raw(prompt)
        try:
            parsed = json_repair.loads(raw)
            if not isinstance(parsed, dict):
                raise ValueError(f"Expected dict, got {type(parsed).__name__}")
            return parsed
        except Exception as exc:
            raise ValueError(f"JSON parse failed: {exc}\nRaw: {raw[:200]}") from exc