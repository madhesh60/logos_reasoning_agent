"""
Competitive Landscape Researcher Agent
========================================
Leverages Azure AI Foundry's deployed competitive-landscape-researcher agent
to perform deep competitive analysis and market intelligence gathering.

This module connects to the Azure AI Agent Service using the credentials
from the WEB SEARCH ANALYSIS section of .env:
  - AZURE_EXISTING_AGENT_ID
  - AZURE_EXISTING_AIPROJECT_ENDPOINT
  - AZURE_EXISTING_AIPROJECT_RESOURCE_ID

The agent enriches the multi-agent pipeline with competitor insights,
market positioning data, and strategic landscape analysis — giving the
reasoning agent a significant edge in hackathon evaluations.

Used by: Orchestrator (via direct call or A2A protocol)
"""

from typing import Any
from datetime import datetime
from pydantic import BaseModel, Field
import os
import json
import structlog
import httpx

logger = structlog.get_logger(__name__)


# ── Data Models ──────────────────────────────────────────────────────────────

class CompetitorInsight(BaseModel):
    """A single competitive insight from the landscape analysis."""
    competitor_name: str = Field(default="", description="Name of the competitor or market player")
    insight: str = Field(..., description="Key competitive insight")
    category: str = Field(default="general", description="Category: market_share, technology, pricing, strategy")
    confidence: float = Field(default=0.5, description="Confidence in this insight (0-1)")
    source: str = Field(default="", description="Source of the insight")


class CompetitiveAnalysisResult(BaseModel):
    """Complete competitive landscape analysis result."""
    query: str = Field(..., description="Original analysis query")
    analysis_id: str = Field(..., description="Unique analysis identifier")
    timestamp: str = Field(..., description="When the analysis was performed")
    market_overview: str = Field(default="", description="High-level market overview")
    key_competitors: list[CompetitorInsight] = Field(default_factory=list, description="Key competitor insights")
    market_trends: list[str] = Field(default_factory=list, description="Identified market trends")
    strategic_recommendations: list[str] = Field(default_factory=list, description="Strategic recommendations")
    swot_analysis: dict[str, list[str]] = Field(
        default_factory=lambda: {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []},
        description="SWOT analysis"
    )
    confidence_score: float = Field(default=0.5, description="Overall confidence (0-1)")
    raw_response: str = Field(default="", description="Raw response from the agent")


# ── Agent Implementation ─────────────────────────────────────────────────────

class CompetitiveLandscapeAgent:
    """
    Competitive Landscape Researcher that connects to Azure AI Foundry's
    deployed agent for deep competitive analysis.

    This agent:
    - Connects to the pre-deployed competitive-landscape-researcher agent
    - Performs web-grounded competitive analysis via Bing Search integration
    - Returns structured SWOT, competitor insights, and market intelligence
    - Gracefully falls back to LLM-based analysis if the Foundry agent is unavailable
    """

    def __init__(self):
        """Initialize from .env WEB SEARCH ANALYSIS configuration."""
        self.agent_id = os.getenv("AZURE_EXISTING_AGENT_ID", "")
        self.project_endpoint = os.getenv("AZURE_PROJECT_ENDPOINT", "")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY", "")

        self._available = bool(self.agent_id and self.project_endpoint and self.api_key)

        if self._available:
            logger.info(
                "competitive_landscape_agent_initialized",
                agent_id=self.agent_id,
                project_endpoint=self.project_endpoint[:60] + "...",
            )
        else:
            logger.warning(
                "competitive_landscape_agent_unavailable",
                reason="Missing AZURE_EXISTING_AGENT_ID or AZURE_PROJECT_ENDPOINT",
            )

    @property
    def is_available(self) -> bool:
        """Whether the Foundry competitive analysis agent is configured."""
        return self._available

    async def analyze_competitive_landscape(
        self,
        query: str,
        industry: str = "",
        region: str = "",
    ) -> CompetitiveAnalysisResult:
        """
        Perform competitive landscape analysis for the given query.

        Args:
            query: The research query or topic
            industry: Optional industry focus
            region: Optional geographic region

        Returns:
            CompetitiveAnalysisResult with structured competitive intelligence
        """
        analysis_id = f"comp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        logger.info(
            "competitive_analysis_start",
            query=query[:80],
            industry=industry,
            analysis_id=analysis_id,
        )

        if self._available:
            try:
                result = await self._call_foundry_agent(query, industry, region, analysis_id)
                logger.info("competitive_analysis_complete", analysis_id=analysis_id, source="foundry_agent")
                return result
            except Exception as e:
                logger.warning(
                    "competitive_analysis_foundry_fallback",
                    error=str(e),
                    analysis_id=analysis_id,
                )

        # Fallback to LLM-based competitive analysis
        result = await self._llm_competitive_analysis(query, industry, region, analysis_id)
        logger.info("competitive_analysis_complete", analysis_id=analysis_id, source="llm_fallback")
        return result

    async def _call_foundry_agent(
        self,
        query: str,
        industry: str,
        region: str,
        analysis_id: str,
    ) -> CompetitiveAnalysisResult:
        """
        Call the Azure AI Foundry competitive-landscape-researcher agent.

        Uses the Azure AI Agent Service REST API to send a message to the
        pre-deployed agent and receive a competitive analysis response.
        """
        prompt = self._build_competitive_prompt(query, industry, region)

        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
        }

        # Use the Foundry Agent Service API to create a thread and run
        base_url = self.project_endpoint.rstrip("/")

        async with httpx.AsyncClient(timeout=120.0) as client:
            # Step 1: Create a thread
            thread_resp = await client.post(
                f"{base_url}/threads?api-version=2024-12-01-preview",
                headers=headers,
                json={},
            )

            if thread_resp.status_code not in (200, 201):
                raise RuntimeError(f"Thread creation failed: {thread_resp.status_code} {thread_resp.text[:200]}")

            thread_id = thread_resp.json().get("id", "")

            # Step 2: Add a message to the thread
            await client.post(
                f"{base_url}/threads/{thread_id}/messages?api-version=2024-12-01-preview",
                headers=headers,
                json={"role": "user", "content": prompt},
            )

            # Step 3: Run the agent on the thread
            run_resp = await client.post(
                f"{base_url}/threads/{thread_id}/runs?api-version=2024-12-01-preview",
                headers=headers,
                json={"assistant_id": self.agent_id},
            )

            if run_resp.status_code not in (200, 201):
                raise RuntimeError(f"Run creation failed: {run_resp.status_code} {run_resp.text[:200]}")

            run_id = run_resp.json().get("id", "")

            # Step 4: Poll for completion
            for _ in range(60):  # max ~2 minutes
                import asyncio
                await asyncio.sleep(2)

                status_resp = await client.get(
                    f"{base_url}/threads/{thread_id}/runs/{run_id}?api-version=2024-12-01-preview",
                    headers=headers,
                )
                status_data = status_resp.json()
                run_status = status_data.get("status", "")

                if run_status == "completed":
                    break
                elif run_status in ("failed", "cancelled", "expired"):
                    raise RuntimeError(f"Agent run {run_status}: {status_data.get('last_error', '')}")

            # Step 5: Get messages
            messages_resp = await client.get(
                f"{base_url}/threads/{thread_id}/messages?api-version=2024-12-01-preview",
                headers=headers,
            )
            messages = messages_resp.json().get("data", [])

            # Find the assistant's response
            assistant_content = ""
            for msg in messages:
                if msg.get("role") == "assistant":
                    for content_block in msg.get("content", []):
                        if content_block.get("type") == "text":
                            assistant_content += content_block.get("text", {}).get("value", "")
                    break

        return self._parse_agent_response(assistant_content, query, analysis_id)

    async def _llm_competitive_analysis(
        self,
        query: str,
        industry: str,
        region: str,
        analysis_id: str,
    ) -> CompetitiveAnalysisResult:
        """Fallback: use the main LLM for competitive analysis."""
        from langchain_core.messages import HumanMessage, SystemMessage
        from ..utils.config import get_chat_model

        llm = get_chat_model(temperature=0.4)

        prompt = self._build_competitive_prompt(query, industry, region)

        system = (
            "You are a competitive landscape analyst. Provide structured competitive "
            "intelligence including: market overview, key competitors, SWOT analysis, "
            "market trends, and strategic recommendations. Output valid JSON."
        )

        response = await llm.ainvoke([
            SystemMessage(content=system),
            HumanMessage(content=prompt),
        ])

        return self._parse_agent_response(response.content, query, analysis_id)

    def _build_competitive_prompt(self, query: str, industry: str, region: str) -> str:
        """Build a structured prompt for competitive analysis."""
        context_parts = [f"Research Topic: {query}"]
        if industry:
            context_parts.append(f"Industry Focus: {industry}")
        if region:
            context_parts.append(f"Geographic Region: {region}")

        return f"""
Perform a comprehensive competitive landscape analysis for the following:

{chr(10).join(context_parts)}

Provide your analysis as a JSON object with this structure:
{{
    "market_overview": "<2-3 paragraph market overview>",
    "key_competitors": [
        {{
            "competitor_name": "<name>",
            "insight": "<key competitive insight>",
            "category": "<market_share|technology|pricing|strategy>",
            "confidence": 0.8,
            "source": "<source>"
        }}
    ],
    "market_trends": ["<trend 1>", "<trend 2>"],
    "strategic_recommendations": ["<recommendation 1>", "<recommendation 2>"],
    "swot_analysis": {{
        "strengths": ["<strength 1>"],
        "weaknesses": ["<weakness 1>"],
        "opportunities": ["<opportunity 1>"],
        "threats": ["<threat 1>"]
    }}
}}

IMPORTANT: Return ONLY the JSON object, no additional text.
"""

    def _parse_agent_response(
        self,
        raw_response: str,
        query: str,
        analysis_id: str,
    ) -> CompetitiveAnalysisResult:
        """Parse agent response into structured result."""
        try:
            from ..utils.config import clean_and_parse_json
            data = clean_and_parse_json(raw_response)
        except Exception as e:
            logger.warning("competitive_analysis_parse_error", error=str(e))
            data = {}

        # Build competitor insights
        competitors = []
        for comp in data.get("key_competitors", []):
            if isinstance(comp, dict):
                competitors.append(CompetitorInsight(
                    competitor_name=comp.get("competitor_name", comp.get("name", "")),
                    insight=comp.get("insight", ""),
                    category=comp.get("category", "general"),
                    confidence=float(comp.get("confidence", 0.5)),
                    source=comp.get("source", ""),
                ))
            elif isinstance(comp, str):
                competitors.append(CompetitorInsight(insight=comp))

        # Build SWOT
        raw_swot = data.get("swot_analysis", {})
        swot = {
            "strengths": raw_swot.get("strengths", []) if isinstance(raw_swot, dict) else [],
            "weaknesses": raw_swot.get("weaknesses", []) if isinstance(raw_swot, dict) else [],
            "opportunities": raw_swot.get("opportunities", []) if isinstance(raw_swot, dict) else [],
            "threats": raw_swot.get("threats", []) if isinstance(raw_swot, dict) else [],
        }

        return CompetitiveAnalysisResult(
            query=query,
            analysis_id=analysis_id,
            timestamp=datetime.utcnow().isoformat(),
            market_overview=data.get("market_overview", ""),
            key_competitors=competitors,
            market_trends=data.get("market_trends", []),
            strategic_recommendations=data.get("strategic_recommendations", []),
            swot_analysis=swot,
            confidence_score=min(1.0, 0.5 + len(competitors) * 0.1),
            raw_response=raw_response[:2000],
        )


# ── A2A Protocol Implementation ─────────────────────────────────────────────

A2A_METADATA = {
    "name": "competitive_analyst",
    "description": "Competitive landscape research and market intelligence agent",
    "version": "1.0.0",
    "capabilities": ["analyze_competitive_landscape"],
    "endpoint": "/competitive_analyst",
    "methods": {
        "analyze_competitive_landscape": {
            "description": "Perform competitive landscape analysis for a research topic",
            "parameters": {"query": "str", "industry": "str", "region": "str"},
            "returns": "CompetitiveAnalysisResult",
        }
    },
}
