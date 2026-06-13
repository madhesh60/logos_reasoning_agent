"""
logos/research/pipeline.py
===========================

Provider-agnostic 4-stage research pipeline.
Works with any OpenAI-compatible API (OpenAI, Anthropic, Gemini, Azure, Ollama).

For Azure AI Foundry users with the 6-agent pipeline, see src/orchestration/.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from typing import Any, Callable, Awaitable

from logos.config import Config
from logos.research.prompts import PLANNER, RESEARCHER, ANALYST, WRITER


# ── Stage definitions ─────────────────────────────────────────────────────────

STAGES = [
    ("planner",    "Decomposing the query into a research framework"),
    ("researcher", "Conducting deep research across sources"),
    ("analyst",    "Synthesising findings and assessing risk"),
    ("writer",     "Composing the structured report"),
]


# ── Pipeline ──────────────────────────────────────────────────────────────────

class ResearchPipeline:
    """
    Runs a 4-stage research pipeline using any OpenAI-compatible API.

    Stages
    ------
    1. Planner    — breaks the query into a structured research plan
    2. Researcher — conducts deep research on each sub-topic
    3. Analyst    — synthesises findings into insights and risks
    4. Writer     — writes the full professional report

    Each stage passes context forward; failed stages are skipped gracefully.
    """

    def __init__(self, config: Config) -> None:
        self.config  = config
        self._client = None

    def _get_client(self):
        if self._client is None:
            self._client = self.config.build_openai_client()
        return self._client

    def _call(self, system: str, user_msg: str, max_tokens: int = 3000) -> str:
        client = self._get_client()
        resp = client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user_msg},
            ],
            max_tokens=max_tokens,
            temperature=0.3,
        )
        return resp.choices[0].message.content or ""

    async def _run_stage(
        self,
        stage_id: str,
        system: str,
        user_msg: str,
        max_tokens: int,
        progress_cb: Callable[[str, str], Awaitable[None]] | None,
    ) -> str | None:
        if progress_cb:
            await progress_cb(stage_id, "running")
        loop = asyncio.get_running_loop()
        try:
            result = await loop.run_in_executor(
                None, self._call, system, user_msg, max_tokens
            )
            if progress_cb:
                await progress_cb(stage_id, "done")
            return result
        except Exception as exc:
            if progress_cb:
                await progress_cb(stage_id, "failed")
            return None

    async def execute(
        self,
        query: str,
        memory_context: str = "",
        user_clarifications: str = "",
        progress_cb: Callable[[str, str], Awaitable[None]] | None = None,
    ) -> dict[str, Any]:
        """
        Run the full 4-stage pipeline.

        Returns a dict with:
          report_text   — raw markdown report from the writer
          stages_ok     — list of stages that succeeded
          stages_failed — list of stages that were skipped
          report_id     — short unique ID for this report
          elapsed       — total seconds
        """
        t0 = datetime.utcnow()

        prefix = ""
        if memory_context:
            prefix += memory_context + "\n"
        if user_clarifications:
            prefix += user_clarifications + "\n"

        context      = ""
        stages_ok:   list[str] = []
        stages_fail: list[str] = []

        # ── Stage 1: Planner ──────────────────────────────────────────────────
        plan = await self._run_stage(
            "planner", PLANNER["system"],
            f"{prefix}Research query: {query}\n\nCreate the research plan.",
            1200, progress_cb,
        )
        if plan:
            context += f"\n\n=== RESEARCH PLAN ===\n{plan}"
            stages_ok.append("planner")
        else:
            stages_fail.append("planner")

        # ── Stage 2: Researcher ───────────────────────────────────────────────
        research = await self._run_stage(
            "researcher", RESEARCHER["system"],
            (f"{prefix}Research query: {query}\n\n"
             f"Research plan:\n{context}\n\n"
             "Conduct thorough, specific research on this topic."),
            3500, progress_cb,
        )
        if research:
            context += f"\n\n=== RESEARCH FINDINGS ===\n{research}"
            stages_ok.append("researcher")
        else:
            stages_fail.append("researcher")

        # ── Stage 3: Analyst ──────────────────────────────────────────────────
        analysis = await self._run_stage(
            "analyst", ANALYST["system"],
            (f"{prefix}Topic: {query}\n\n"
             f"All research collected:\n{context}\n\n"
             "Produce the structured analysis."),
            2000, progress_cb,
        )
        if analysis:
            context += f"\n\n=== STRATEGIC ANALYSIS ===\n{analysis}"
            stages_ok.append("analyst")
        else:
            stages_fail.append("analyst")

        # ── Stage 4: Writer ───────────────────────────────────────────────────
        report_text = await self._run_stage(
            "writer", WRITER["system"],
            (f"{prefix}Topic: {query}\n\n"
             f"All research and analysis:\n{context}\n\n"
             "Write the complete intelligence report."),
            4000, progress_cb,
        )
        if report_text:
            stages_ok.append("writer")
        else:
            stages_fail.append("writer")
            report_text = _fallback_report(query, context)

        elapsed = (datetime.utcnow() - t0).total_seconds()
        report_id = uuid.uuid4().hex[:8]

        return {
            "report_text":    report_text,
            "context":        context,
            "stages_ok":      stages_ok,
            "stages_failed":  stages_fail,
            "report_id":      report_id,
            "elapsed":        elapsed,
            "provider":       self.config.provider_label,
            "model":          self.config.model,
        }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fallback_report(query: str, context: str) -> str:
    """Minimal report when the writer stage fails."""
    return (
        f"# Research Report: {query}\n\n"
        "## Research Findings\n\n"
        + context[:3000]
    )
