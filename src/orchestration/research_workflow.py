"""
Research-to-Report Multi-Agent System
Main Entry Point and Orchestration

This module provides the main interface for executing research workflows
using the multi-agent system with LangGraph orchestration.

Usage:
    from src.orchestration.research_workflow import ResearchWorkflow
    workflow = ResearchWorkflow()
    result = await workflow.execute("What are the top 3 investment risks in the Indian EV market?")
"""

from typing import Any, TypedDict
import uuid
import os
import json
import sqlite3
from datetime import datetime
import structlog

from ..agents import (
    PlannerAgent,
    ResearchPlan,
    SubTask,
    TaskType,
    ResearcherAgent,
    ResearchResults,
    AnalystAgent,
    AnalysisResults,
    WriterAgent,
    GeneratedReport,
    ReportFormat,
    CompetitiveLandscapeAgent,
    CompetitiveAnalysisResult,
)
from ..foundry.client import FoundryAgentClient

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Agent version registry — read from env, fall back to hardcoded defaults
# ---------------------------------------------------------------------------
_AGENT_VERSIONS = {
    "planner":    os.getenv("PLANNER_AGENT_VERSION",    "9"),
    "researcher": os.getenv("RESEARCHER_AGENT_VERSION", "7"),
    "analyst":    os.getenv("ANALYST_AGENT_VERSION",    "4"),
    "writer":     os.getenv("WRITER_AGENT_VERSION",     "4"),
    "competitive":       os.getenv("COMPETITIVE_AGENT_VERSION", "2"),
    "industry_scanner":  os.getenv("INDUSTRY_SCANNER_VERSION",  "5"),
}


class WorkflowState(TypedDict):
    """State managed throughout the LangGraph workflow execution."""
    query: str
    plan: ResearchPlan | None
    research_results: ResearchResults | None
    analysis_results: AnalysisResults | None
    competitive_analysis: CompetitiveAnalysisResult | None
    report: GeneratedReport | None

    current_task: str | None
    completed_tasks: list[str]
    failed_tasks: list[str]

    errors: list[dict[str, Any]]
    retry_count: int
    validation_result: dict[str, Any] | None

    start_time: str
    end_time: str | None
    confidence_scores: dict[str, float]


class ResearchWorkflow:
    """
    Main orchestration class for the Research-to-Report workflow.

    Pipeline:
      plan → validate_plan → research → analyze → competitive_analysis → write_report

    Each node tries the Foundry-hosted agent first (via FoundryAgentClient),
    then falls back silently to the local agent implementation.
    """

    def __init__(
        self,
        enable_a2a: bool = True,
        enable_mcp: bool = True,
        max_retries: int = 3,
        memory_db_path: str = "memory.sqlite",
    ):
        self.enable_a2a = enable_a2a
        self.enable_mcp = enable_mcp
        self.max_retries = max_retries
        self.memory_db_path = memory_db_path
        self.store_db_path = "store.sqlite"
        self.store = None

        # Local fallback agents — always available
        self.planner = PlannerAgent()
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.writer = WriterAgent()
        self.competitive_analyst = CompetitiveLandscapeAgent()

        # Foundry A2A clients — optional, set up if enabled
        self.a2a_clients: dict[str, FoundryAgentClient] = {}
        if enable_a2a:
            self._setup_a2a()

        logger.info(
            "research_workflow_initialized",
            enable_a2a=enable_a2a,
            enable_mcp=enable_mcp,
            max_retries=max_retries,
            foundry_agents=list(self.a2a_clients.keys()),
        )

    # ------------------------------------------------------------------
    # Foundry client setup
    # ------------------------------------------------------------------
    def _setup_a2a(self):
        """
        Create FoundryAgentClient objects for each pipeline agent.

        Agents that have tools (planner, researcher, analyst) use the
        thread-based Agents API via their GUID.
        Writer has no tools so uses the lighter Responses API (agent_id=None).
        """
        try:
            self.a2a_clients = {
                "planner": FoundryAgentClient(
                    "planner-agent",
                    _AGENT_VERSIONS["planner"],
                ),
                "researcher": FoundryAgentClient(
                    "researcher-agent",
                    _AGENT_VERSIONS["researcher"],
                ),
                "analyst": FoundryAgentClient(
                    "analyst-agent",
                    _AGENT_VERSIONS["analyst"],
                ),
                "writer": FoundryAgentClient(
                    "writer-agent",
                    _AGENT_VERSIONS["writer"],
                ),
                "competitive": FoundryAgentClient(
                    "competitive-landscape-researcher",
                    os.getenv("COMPETITIVE_AGENT_VERSION", "2"),
                ),
                "industry_scanner": FoundryAgentClient(
                    "industry-news-trend-scanner",
                    os.getenv("INDUSTRY_SCANNER_VERSION", "5"),
                ),
            }
            logger.info(
                "foundry_clients_initialized",
                agents=list(self.a2a_clients.keys()),
            )
        except Exception as e:
            logger.warning("foundry_client_setup_failed", error=str(e))
            self.a2a_clients = {}


    # ------------------------------------------------------------------
    # Store helper
    # ------------------------------------------------------------------
    def _store_search(self, query: str) -> list:
        """Search long-term store for previous research on this query."""
        try:
            if self.store is None:
                return []
            return self.store.search(("research_plans",), query=query, limit=1)
        except Exception as e:
            logger.warning("store_search_failed", error=str(e))
            return []

    # ------------------------------------------------------------------
    # Node: plan
    # ------------------------------------------------------------------
    async def _plan_node(self, state: WorkflowState) -> dict[str, Any]:
        """Decompose the query into a structured research plan."""
        logger.info("workflow_plan_node_start", query=state["query"][:80])

        try:
            plan: ResearchPlan | None = None

            # Check long-term memory for previous work on the same query
            past_memories = self._store_search(state["query"])
            past_context: str | None = None
            if past_memories:
                past_context = json.dumps(past_memories[0].value, indent=2)
                logger.info("found_past_research_context")

            # Build the prompt for the Foundry agent
            context_suffix = (
                f"\n\nPAST RESEARCH CONTEXT:\n{past_context}\n"
                "(Use this to avoid redundant work.)"
                if past_context else ""
            )
            prompt = (
                f"Decompose the following research query into a structured plan.\n\n"
                f"Query: {state['query']}{context_suffix}\n\n"
                f"Respond STRICTLY with JSON matching the ResearchPlan schema. "
                f"No prose. No markdown. Raw JSON only."
            )

            # ── Try Foundry agent first ────────────────────────────────────
            if self.enable_a2a and "planner" in self.a2a_clients:
                try:
                    logger.info("a2a_planner_call_start")
                    result = await self.a2a_clients["planner"].call_agent_json(prompt)
                    plan = ResearchPlan(**result)
                    logger.info("a2a_planner_call_success", plan_id=plan.plan_id)
                except Exception as e:
                    logger.warning("a2a_planner_failed_fallback_local", error=str(e))
                    plan = None

            # ── Local fallback ─────────────────────────────────────────────
            if plan is None:
                logger.info("planner_using_local_agent")
                # decompose_task only accepts query — no past_context param
                plan = await self.planner.decompose_task(state["query"])

            confidence_scores = dict(state.get("confidence_scores", {}))
            confidence_scores["planning"] = plan.confidence_score

            retry_count = state.get("retry_count", 0)
            if state.get("plan") is not None:
                retry_count += 1

            return {
                "plan":             plan,
                "current_task":     "planning",
                "completed_tasks":  list(state.get("completed_tasks", [])) + ["plan"],
                "errors":           list(state.get("errors", [])),
                "confidence_scores": confidence_scores,
                "retry_count":      retry_count,
            }

        except Exception as e:
            logger.error("planning_failed", error=str(e))
            return {
                "errors": list(state.get("errors", [])) + [{"node": "plan", "error": str(e)}],
                "failed_tasks": list(state.get("failed_tasks", [])) + ["plan"],
            }

    # ------------------------------------------------------------------
    # Node: validate_plan
    # ------------------------------------------------------------------
    async def _validate_plan_node(self, state: WorkflowState) -> dict[str, Any]:
        """Validate the research plan before proceeding."""
        plan = state.get("plan")
        if not plan:
            return {
                "errors": list(state.get("errors", [])) + [
                    {"node": "validate_plan", "error": "No plan available"}
                ],
                "validation_result": {"can_proceed": False, "is_valid": False},
            }

        logger.info("workflow_validate_plan_start", plan_id=plan.plan_id)

        validation: dict[str, Any]

        # ── Try Foundry agent first ────────────────────────────────────────
        if self.enable_a2a and "planner" in self.a2a_clients:
            prompt = (
                f"Validate the following research plan.\n\n"
                f"Plan:\n{plan.model_dump_json(indent=2)}\n\n"
                f"Respond STRICTLY with JSON: "
                f"{{\"can_proceed\": bool, \"is_valid\": bool, "
                f"\"warnings\": [str], \"issues\": [str]}}"
            )
            try:
                logger.info("a2a_planner_validate_start")
                validation = await self.a2a_clients["planner"].call_agent_json(prompt)
                if "can_proceed" not in validation:
                    validation["can_proceed"] = validation.get("is_valid", True)
                logger.info("a2a_planner_validate_success")
            except Exception as e:
                logger.warning("a2a_validate_failed_fallback_local", error=str(e))
                validation = await self.planner.validate_plan(plan)
        else:
            validation = await self.planner.validate_plan(plan)

        return {
            "current_task":     "validation",
            "confidence_scores": dict(state.get("confidence_scores", {})),
            "validation_result": validation,
        }


    # ------------------------------------------------------------------
    # Node: research
    # ------------------------------------------------------------------
    async def _research_node(self, state: WorkflowState) -> dict[str, Any]:
        """Execute web research for the query."""
        plan = state.get("plan")
        if not plan:
            return {
                "errors": list(state.get("errors", [])) + [
                    {"node": "research", "error": "No plan available"}
                ],
            }

        logger.info("workflow_research_node_start", plan_id=plan.plan_id)

        try:
            research_results: ResearchResults | None = None

            prompt = (
                f"Research the following query thoroughly.\n\n"
                f"Query: {state['query']}\nMax Results: 10\n\n"
                f"Respond STRICTLY with JSON matching the ResearchResults schema."
            )

            # ── Try Foundry agent first ────────────────────────────────────
            if self.enable_a2a and "researcher" in self.a2a_clients:
                try:
                    logger.info("a2a_researcher_call_start")
                    result = await self.a2a_clients["researcher"].call_agent_json(prompt)
                    research_results = ResearchResults(**result)
                    logger.info("a2a_researcher_call_success")
                except Exception as e:
                    logger.warning("a2a_researcher_failed_fallback_local", error=str(e))
                    research_results = None

            # ── Local fallback ─────────────────────────────────────────────
            if research_results is None:
                logger.info("researcher_using_local_agent")
                research_results = await self.researcher.search(
                    query=state["query"], max_results=10
                )

            confidence_scores = dict(state.get("confidence_scores", {}))
            confidence_scores["research"] = research_results.confidence_score

            return {
                "research_results": research_results,
                "current_task":     "research",
                "completed_tasks":  list(state.get("completed_tasks", [])) + ["research"],
                "confidence_scores": confidence_scores,
            }

        except Exception as e:
            logger.error("research_failed", error=str(e))
            return {
                "errors": list(state.get("errors", [])) + [{"node": "research", "error": str(e)}],
                "failed_tasks": list(state.get("failed_tasks", [])) + ["research"],
            }

    # ------------------------------------------------------------------
    # Node: analyze
    # ------------------------------------------------------------------
    async def _analyze_node(self, state: WorkflowState) -> dict[str, Any]:
        """Analyze research results for insights, patterns, and risks."""
        research_results = state.get("research_results")
        if not research_results:
            return {
                "errors": list(state.get("errors", [])) + [
                    {"node": "analyze", "error": "No research results available"}
                ],
            }

        logger.info("workflow_analyze_node_start", query=state["query"][:60])

        try:
            research_data = {
                "sources": [
                    {
                        "title":       r.title,
                        "snippet":     r.snippet,
                        "source_name": r.source_name,
                        "url":         r.url,
                    }
                    for r in (
                        research_results.high_confidence_sources
                        + research_results.medium_confidence_sources
                    )
                ],
                "search_results": research_results.sources_used,
            }

            analysis_results: AnalysisResults | None = None

            prompt = (
                f"Analyze the following research data for the query.\n\n"
                f"Query: {state['query']}\n\n"
                f"Research Data:\n{json.dumps(research_data, indent=2)}\n\n"
                f"Respond STRICTLY with JSON matching the AnalysisResults schema."
            )

            # ── Try Foundry agent first ────────────────────────────────────
            if self.enable_a2a and "analyst" in self.a2a_clients:
                try:
                    logger.info("a2a_analyst_call_start")
                    result = await self.a2a_clients["analyst"].call_agent_json(prompt)
                    analysis_results = AnalysisResults(**result)
                    logger.info("a2a_analyst_call_success")
                except Exception as e:
                    logger.warning("a2a_analyst_failed_fallback_local", error=str(e))
                    analysis_results = None

            # ── Local fallback ─────────────────────────────────────────────
            if analysis_results is None:
                logger.info("analyst_using_local_agent")
                analysis_results = await self.analyst.analyze(
                    query=state["query"],
                    research_data=research_data,
                )

            confidence_scores = dict(state.get("confidence_scores", {}))
            confidence_scores["analysis"] = analysis_results.overall_confidence

            return {
                "analysis_results": analysis_results,
                "current_task":     "analysis",
                "completed_tasks":  list(state.get("completed_tasks", [])) + ["analyze"],
                "confidence_scores": confidence_scores,
            }

        except Exception as e:
            logger.error("analysis_failed", error=str(e))
            return {
                "errors": list(state.get("errors", [])) + [{"node": "analyze", "error": str(e)}],
                "failed_tasks": list(state.get("failed_tasks", [])) + ["analyze"],
            }

    # ------------------------------------------------------------------
    # Node: competitive_analysis
    # ------------------------------------------------------------------
    async def _competitive_analysis_node(self, state: WorkflowState) -> dict[str, Any]:
        """
        Run competitive landscape analysis.
        Tries Foundry competitive-landscape-researcher agent first,
        then industry-news-trend-scanner, then local fallback.
        This node never fails the whole pipeline.
        """
        logger.info("workflow_competitive_analysis_start", query=state["query"][:60])

        comp_result = None

        # ── Try Foundry competitive-landscape-researcher ───────────────
        if self.enable_a2a and "competitive" in self.a2a_clients:
            prompt = (
                f"Analyze the competitive landscape for the following query.\n\n"
                f"Query: {state['query']}\n\n"
                f"Identify market leaders, challengers, market gaps, and strategic outlook.\n"
                f"Respond STRICTLY with JSON: "
                f"{{\"market_leaders\": [str], \"challengers\": [str], "
                f"\"market_gaps\": [str], \"strategic_outlook\": str, "
                f"\"confidence\": float}}"
            )
            try:
                logger.info("a2a_competitive_call_start")
                comp_data = await self.a2a_clients["competitive"].call_agent_json(prompt)
                comp_result = comp_data
                logger.info("a2a_competitive_call_success")
            except Exception as e:
                logger.warning("a2a_competitive_failed", error=str(e))

        # ── Try Foundry industry-news-trend-scanner ────────────────────
        if comp_result is None and self.enable_a2a and "industry_scanner" in self.a2a_clients:
            prompt = (
                f"Scan for the latest industry news and trends for:\n\n"
                f"Query: {state['query']}\n\n"
                f"Respond STRICTLY with JSON: "
                f"{{\"trends\": [str], \"key_players\": [str], "
                f"\"market_outlook\": str, \"confidence\": float}}"
            )
            try:
                logger.info("a2a_industry_scanner_call_start")
                scan_data = await self.a2a_clients["industry_scanner"].call_agent_json(prompt)
                # Normalize to competitive analysis shape
                comp_result = {
                    "market_leaders":    scan_data.get("key_players", []),
                    "challengers":       [],
                    "market_gaps":       scan_data.get("trends", []),
                    "strategic_outlook": scan_data.get("market_outlook", ""),
                    "confidence":        scan_data.get("confidence", 0.7),
                }
                logger.info("a2a_industry_scanner_call_success")
            except Exception as e:
                logger.warning("a2a_industry_scanner_failed", error=str(e))

        # ── Local fallback ─────────────────────────────────────────────
        if comp_result is None:
            try:
                logger.info("competitive_using_local_agent")
                local_result = await self.competitive_analyst.analyze_competitive_landscape(
                    query=state["query"],
                    industry="",
                    region="India",
                )
                comp_result = local_result
            except Exception as e:
                logger.warning("competitive_analysis_failed_continuing", error=str(e))
                comp_result = None

        return {
            "competitive_analysis": comp_result,
            "current_task":         "competitive_analysis",
            "completed_tasks":      list(state.get("completed_tasks", [])) + ["competitive_analysis"],
        }

    # ------------------------------------------------------------------
    # Node: write_report
    # ------------------------------------------------------------------
    async def _write_report_node(self, state: WorkflowState) -> dict[str, Any]:
        """Generate the final structured report."""
        analysis_results = state.get("analysis_results")
        if not analysis_results:
            return {
                "errors": list(state.get("errors", [])) + [
                    {"node": "write_report", "error": "No analysis results available"}
                ],
            }

        logger.info("workflow_write_report_start", query=state["query"][:60])

        try:
            analysis_data: dict[str, Any] = {
                "key_findings": [
                    {
                        "category":          f.category,
                        "statement":         f.statement,
                        "confidence":        f.confidence,
                        "evidence":          f.evidence,
                        "evidence_strength": f.evidence_strength.value,
                        "source_count":      f.source_count,
                    }
                    for f in analysis_results.key_findings
                ],
                "risks_identified": [
                    {
                        "risk_id":     r.risk_id,
                        "title":       r.title,
                        "description": r.description,
                        "level":       r.level.value,
                        "probability": r.probability,
                        "impact":      r.impact,
                        "risk_score":  r.risk_score,
                        "mitigation":  r.mitigation,
                        "confidence":  r.confidence,
                    }
                    for r in analysis_results.risks_identified
                ],
                "patterns_detected":     analysis_results.patterns_detected,
                "reasoning_chain":       analysis_results.reasoning_chain,
                "overall_confidence":    analysis_results.overall_confidence,
                "data_sources_analyzed": analysis_results.data_sources_analyzed,
            }

            # Attach research sources
            research_results = state.get("research_results")
            if research_results:
                analysis_data["sources"] = [
                    {"title": r.title, "source_name": r.source_name, "url": r.url}
                    for r in (
                        research_results.high_confidence_sources
                        + research_results.medium_confidence_sources
                    )
                ]

            # Attach competitive analysis if available
            comp = state.get("competitive_analysis")
            if comp:
                analysis_data["competitive_landscape"] = {
                    "market_leaders":    getattr(comp, "market_leaders", []),
                    "market_gaps":       getattr(comp, "market_gaps", []),
                    "strategic_outlook": getattr(comp, "strategic_outlook", ""),
                }

            report: GeneratedReport | None = None

            prompt = (
                f"Write a comprehensive business research report.\n\n"
                f"Query: {state['query']}\n\n"
                f"Analysis Data:\n{json.dumps(analysis_data, indent=2)}\n\n"
                f"IMPORTANT: End the report with this disclaimer:\n"
                f"'This report is for informational purposes only and does not "
                f"constitute financial or investment advice.'\n\n"
                f"Respond STRICTLY with JSON matching the GeneratedReport schema."
            )

            # ── Try Foundry agent first ────────────────────────────────────
            if self.enable_a2a and "writer" in self.a2a_clients:
                try:
                    logger.info("a2a_writer_call_start")
                    result = await self.a2a_clients["writer"].call_agent_json(prompt)
                    report = GeneratedReport(**result)
                    logger.info("a2a_writer_call_success")
                except Exception as e:
                    logger.warning("a2a_writer_failed_fallback_local", error=str(e))
                    report = None

            # ── Local fallback ─────────────────────────────────────────────
            if report is None:
                logger.info("writer_using_local_agent")
                report = await self.writer.generate_report(
                    query=state["query"],
                    analysis_results=analysis_data,
                )

            # Persist to long-term store
            if self.store:
                try:
                    self.store.put(
                        ("research_plans",),
                        str(uuid.uuid4()),
                        {
                            "query":             state["query"],
                            "report_id":         report.metadata.report_id,
                            "confidence_score":  report.metadata.confidence_score,
                            "executive_summary": report.executive_summary,
                            "conclusions":       report.conclusions,
                            "recommendations":   report.recommendations,
                        },
                    )
                except Exception as e:
                    logger.warning("store_put_failed", error=str(e))

            return {
                "report":          report,
                "current_task":    "report_generation",
                "completed_tasks": list(state.get("completed_tasks", [])) + ["write_report"],
                "end_time":        datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error("report_generation_failed", error=str(e))
            return {
                "errors": list(state.get("errors", [])) + [{"node": "write_report", "error": str(e)}],
                "failed_tasks": list(state.get("failed_tasks", [])) + ["write_report"],
            }

    # ------------------------------------------------------------------
    # Node: handle_error
    # ------------------------------------------------------------------
    async def _handle_error_node(self, state: WorkflowState) -> dict[str, Any]:
        """Handle unrecoverable workflow errors."""
        errors     = state.get("errors", [])
        retry_count = state.get("retry_count", 0)
        logger.error("workflow_error_handling", errors=errors, retry_count=retry_count)

        if retry_count < self.max_retries:
            return {"retry_count": retry_count + 1, "current_task": "retry"}
        return {"end_time": datetime.utcnow().isoformat()}

    # ------------------------------------------------------------------
    # Public: execute()
    # ------------------------------------------------------------------
    async def execute(self, query: str, session_id: str | None = None) -> dict[str, Any]:
        """
        Execute the full research-to-report workflow.

        Args:
            query:      The research question to answer.
            session_id: Optional session ID for memory continuity across calls.

        Returns:
            Dict with keys: status, query, report, metadata, confidence_score.
        """
        logger.info("workflow_execute_start", query=query[:100])

        initial_state: WorkflowState = {
            "query":                query,
            "plan":                 None,
            "research_results":     None,
            "analysis_results":     None,
            "competitive_analysis": None,
            "report":               None,
            "current_task":         None,
            "completed_tasks":      [],
            "failed_tasks":         [],
            "errors":               [],
            "retry_count":          0,
            "start_time":           datetime.utcnow().isoformat(),
            "end_time":             None,
            "confidence_scores":    {},
            "validation_result":    None,
        }

        state = dict(initial_state)

        try:
            # 1. Plan
            try:
                plan_updates = await self._plan_node(state)
                state.update(plan_updates)
            except Exception as e:
                logger.warning("planner_failed_continuing_with_raw_query", error=str(e))
                state["errors"].append({"node": "plan", "error": str(e)})
                state["failed_tasks"].append("plan")

            # 2. Validate Plan
            if state.get("plan"):
                try:
                    val_updates = await self._validate_plan_node(state)
                    state.update(val_updates)
                except Exception as e:
                    logger.warning("validate_plan_failed", error=str(e))
                    state["errors"].append({"node": "validate_plan", "error": str(e)})

            # 3. Research
            try:
                research_updates = await self._research_node(state)
                state.update(research_updates)
            except Exception as e:
                logger.error("research_failed", error=str(e))
                state["errors"].append({"node": "research", "error": str(e)})
                state["failed_tasks"].append("research")

            # 4. Analyze
            try:
                analyze_updates = await self._analyze_node(state)
                state.update(analyze_updates)
            except Exception as e:
                logger.error("analysis_failed", error=str(e))
                state["errors"].append({"node": "analyze", "error": str(e)})
                state["failed_tasks"].append("analyze")

            # 5. Competitive Analysis
            try:
                comp_updates = await self._competitive_analysis_node(state)
                state.update(comp_updates)
            except Exception as e:
                logger.warning("competitive_analysis_failed_continuing", error=str(e))
                state["errors"].append({"node": "competitive_analysis", "error": str(e)})

            # 6. Write Report
            try:
                report_updates = await self._write_report_node(state)
                state.update(report_updates)
            except Exception as e:
                logger.error("report_generation_failed", error=str(e))
                state["errors"].append({"node": "write_report", "error": str(e)})
                state["failed_tasks"].append("write_report")

            state["end_time"] = datetime.utcnow().isoformat()

            response: dict[str, Any] = {
                "status": (
                    "completed" if not state.get("errors")
                    else "completed_with_errors"
                ),
                "query":  query,
                "report": state.get("report"),
                "metadata": {
                    "start_time":        state.get("start_time"),
                    "end_time":          state.get("end_time"),
                    "completed_tasks":   state.get("completed_tasks", []),
                    "failed_tasks":      state.get("failed_tasks", []),
                    "confidence_scores": state.get("confidence_scores", {}),
                    "errors":            state.get("errors", []),
                },
            }

            if state.get("report"):
                response["confidence_score"] = (
                    state["report"].metadata.confidence_score
                )
                response["processing_time_seconds"] = (
                    state["report"].metadata.processing_time_seconds
                )

            logger.info(
                "workflow_execute_complete",
                status=response["status"],
                completed_tasks=len(state.get("completed_tasks", [])),
            )
            return response

        except Exception as e:
            logger.error("workflow_execute_failed", error=str(e))
            return {
                "status":     "failed",
                "query":      query,
                "error":      str(e),
                "start_time": state["start_time"],
                "end_time":   datetime.utcnow().isoformat(),
            }

    # ------------------------------------------------------------------
    # Public: execute_streaming()
    # ------------------------------------------------------------------
    async def execute_streaming(self, query: str, session_id: str | None = None):
        """
        Execute the workflow sequentially and yield status updates for each stage.
        """
        logger.info("workflow_execute_streaming_start", query=query[:60])

        state: WorkflowState = {
            "query":                query,
            "plan":                 None,
            "research_results":     None,
            "analysis_results":     None,
            "competitive_analysis": None,
            "report":               None,
            "current_task":         None,
            "completed_tasks":      [],
            "failed_tasks":         [],
            "errors":               [],
            "retry_count":          0,
            "start_time":           datetime.utcnow().isoformat(),
            "end_time":             None,
            "confidence_scores":    {},
            "validation_result":    None,
        }

        # List of stages to execute
        stages = [
            ("plan", self._plan_node),
            ("validate_plan", self._validate_plan_node),
            ("research", self._research_node),
            ("analyze", self._analyze_node),
            ("competitive_analysis", self._competitive_analysis_node),
            ("write_report", self._write_report_node),
        ]

        for stage_name, stage_func in stages:
            # Skip validation if plan didn't generate
            if stage_name == "validate_plan" and not state.get("plan"):
                continue

            yield {
                "stage":  stage_name,
                "status": "in_progress",
                "state":  state,
            }

            try:
                updates = await stage_func(state)
                state.update(updates)

                yield {
                    "stage":  stage_name,
                    "status": "completed",
                    "state":  state,
                }

                if updates.get("errors"):
                    yield {
                        "stage":  stage_name,
                        "status": "error",
                        "errors": updates["errors"],
                    }

            except Exception as e:
                err_dict = {"node": stage_name, "error": str(e)}
                state["errors"].append(err_dict)
                state["failed_tasks"].append(stage_name)
                yield {
                    "stage":  stage_name,
                    "status": "error",
                    "errors": [err_dict],
                }

        state["end_time"] = datetime.utcnow().isoformat()
        yield {"stage": "complete", "status": "completed", "result": state}


# ---------------------------------------------------------------------------
# Standalone demo
# ---------------------------------------------------------------------------
async def main():
    """Demo — run directly to test the workflow."""
    from ..utils.config import load_environment
    load_environment()

    print("=" * 60)
    print("BUSINESS & INVESTMENT RESEARCH MULTI-AGENT SYSTEM")
    print("=" * 60)

    workflow = ResearchWorkflow(enable_a2a=True, enable_mcp=True, max_retries=2)
    query = "What are the top 3 investment risks in the Indian EV market?"
    print(f"\nQuery: {query}\n")

    result = await workflow.execute(query)

    print(f"\nStatus:     {result['status']}")
    print(f"Confidence: {result.get('confidence_score', 'N/A')}")
    print(f"Tasks done: {result['metadata']['completed_tasks']}")

    if result.get("report"):
        r = result["report"]
        print(f"\nTitle: {r.metadata.title}")
        print(f"\nExecutive Summary:\n{r.executive_summary[:400]}...")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())