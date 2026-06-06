#!/usr/bin/env python3
"""
Research-to-Report Multi-Agent Demo
====================================
Runs the full 4-agent pipeline (Planner → Researcher → Analyst → Writer)
with rich, coloured, step-by-step terminal output so you can watch every
agent reason in real time.

Uses:
  • phi-4-mini-reasoning  (fast, default)  OR
  • phi-4-reasoning       (deep, set AZURE_OPENAI_DEPLOYMENT=phi-4-reasoning in .env)

Run from the project root:
    python demo.py
    python demo.py --query "What are the risks of renewable energy in data centres?"
    python demo.py --query "..." --model phi-4-reasoning
    python demo.py --interactive
"""

import asyncio
import argparse
import json
import os
import sys
import textwrap
import time
from datetime import datetime
from pathlib import Path

# ── bootstrap path so 'src.*' imports work without install ──────────────────
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

# ── pretty-print helpers ────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
MAGENTA= "\033[95m"
BLUE   = "\033[94m"
RED    = "\033[91m"


def banner(text: str, color: str = CYAN) -> None:
    width = 70
    print()
    print(color + "═" * width + RESET)
    print(color + BOLD + f"  {text}" + RESET)
    print(color + "═" * width + RESET)


def step(icon: str, label: str, detail: str = "", color: str = BLUE) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{DIM}[{ts}]{RESET} {color}{BOLD}{icon} {label}{RESET}  {DIM}{detail}{RESET}")


def section(title: str) -> None:
    print()
    print(f"{YELLOW}{'─'*70}{RESET}")
    print(f"{YELLOW}{BOLD}  {title}{RESET}")
    print(f"{YELLOW}{'─'*70}{RESET}")


def indent(text: str, width: int = 4) -> str:
    prefix = " " * width
    return "\n".join(prefix + line for line in text.splitlines())


def print_plan(plan) -> None:
    section("📋  PLANNER  —  Task Decomposition")
    print(f"  {BOLD}Plan ID     :{RESET} {plan.plan_id}")
    print(f"  {BOLD}Intent      :{RESET} {plan.intent_summary}")
    print(f"  {BOLD}Tasks       :{RESET} {plan.total_tasks}")
    print(f"  {BOLD}Confidence  :{RESET} {plan.confidence_score:.0%}")
    print(f"  {BOLD}Est. time   :{RESET} {plan.estimated_total_time_seconds}s")
    print()
    print(f"  {MAGENTA}{BOLD}Sub-tasks:{RESET}")
    for t in plan.tasks:
        deps = f"  ← depends on {t.depends_on}" if t.depends_on else ""
        print(f"    [{t.task_id}] {BOLD}{t.task_type}{RESET} → {t.agent}{deps}")
        print(f"         {DIM}{t.description[:80]}...{RESET}" if len(t.description) > 80
              else f"         {DIM}{t.description}{RESET}")
    print()
    print(f"  {BOLD}Execution order:{RESET} {' → '.join(plan.execution_order)}")
    print(f"  {BOLD}Reasoning:{RESET}")
    print(indent(textwrap.fill(plan.reasoning, 64), 4))


def print_research(res) -> None:
    section("🔍  RESEARCHER  —  Web Search Results")
    print(f"  {BOLD}Timestamp       :{RESET} {res.timestamp}")
    print(f"  {BOLD}Total sources   :{RESET} {res.total_sources}")
    print(f"  {BOLD}High-confidence :{RESET} {len(res.high_confidence_sources)}")
    print(f"  {BOLD}Confidence score:{RESET} {res.confidence_score:.0%}")

    if res.high_confidence_sources:
        print()
        print(f"  {GREEN}{BOLD}Top Sources:{RESET}")
        for i, src in enumerate(res.high_confidence_sources[:5], 1):
            print(f"    {i}. {BOLD}{src.title}{RESET}")
            print(f"       {DIM}Source: {src.source_name}  |  Relevance: {src.relevance_score:.0%}  |  Authority: {src.authority_score:.0%}{RESET}")
            snippet = src.snippet[:120] + "..." if len(src.snippet) > 120 else src.snippet
            print(f"       {snippet}")

    if res.gaps_identified:
        print()
        print(f"  {YELLOW}{BOLD}Gaps Identified:{RESET}")
        for g in res.gaps_identified:
            print(f"    ⚠  {g}")


def print_analysis(analysis) -> None:
    section("🧠  ANALYST  —  Reasoning & Insight Extraction")
    print(f"  {BOLD}Analysis ID     :{RESET} {analysis.analysis_id}")
    print(f"  {BOLD}Overall conf.   :{RESET} {analysis.overall_confidence:.0%}")
    print(f"  {BOLD}Sources analysed:{RESET} {analysis.data_sources_analyzed}")

    if analysis.reasoning_chain:
        print()
        print(f"  {CYAN}{BOLD}Reasoning Chain:{RESET}")
        for i, step_text in enumerate(analysis.reasoning_chain, 1):
            print(f"    Step {i}: {step_text}")

    if analysis.key_findings:
        print()
        print(f"  {GREEN}{BOLD}Key Findings:{RESET}")
        for f in analysis.key_findings:
            conf_bar = "█" * int(f.confidence * 10) + "░" * (10 - int(f.confidence * 10))
            print(f"    [{f.category.upper()}] {BOLD}{f.statement}{RESET}")
            print(f"       Confidence: {conf_bar} {f.confidence:.0%}  |  Evidence strength: {f.evidence_strength}")

    if analysis.risks_identified:
        print()
        print(f"  {RED}{BOLD}Risks Identified:{RESET}")
        for r in analysis.risks_identified:
            level_color = RED if r.level.value in ("critical", "high") else YELLOW
            print(f"    {level_color}{BOLD}[{r.level.value.upper()}]{RESET} {r.title}")
            print(f"       Risk score: {r.risk_score:.2f}  (P={r.probability:.0%} × I={r.impact:.0%})")
            print(f"       {DIM}{r.description[:100]}...{RESET}" if len(r.description) > 100
                  else f"       {DIM}{r.description}{RESET}")
            if r.mitigation:
                print(f"       Mitigation: {r.mitigation[0]}")

    if analysis.patterns_detected:
        print()
        print(f"  {MAGENTA}{BOLD}Patterns Detected:{RESET}")
        for p in analysis.patterns_detected:
            print(f"    • {p}")


def print_report(report) -> None:
    section("📄  WRITER  —  Final Research Report")
    print(f"  {BOLD}Report ID  :{RESET} {report.metadata.report_id}")
    print(f"  {BOLD}Title      :{RESET} {report.metadata.title}")
    print(f"  {BOLD}Created    :{RESET} {report.metadata.created_at}")
    print(f"  {BOLD}Confidence :{RESET} {report.metadata.confidence_score:.0%}")
    print(f"  {BOLD}Data srcs  :{RESET} {report.metadata.data_sources}")
    print(f"  {BOLD}Agents used:{RESET} {', '.join(report.metadata.agents_used)}")

    print()
    print(f"  {CYAN}{BOLD}Executive Summary:{RESET}")
    wrapped = textwrap.fill(report.executive_summary, 64)
    print(indent(wrapped, 4))

    if report.sections:
        print()
        print(f"  {BOLD}Sections:{RESET}")
        for s in report.sections:
            print(f"    [{s.section_id}] {BOLD}{s.title}{RESET}")
            preview = s.content[:120].replace("\n", " ")
            print(f"         {DIM}{preview}...{RESET}")

    if report.conclusions:
        print()
        print(f"  {GREEN}{BOLD}Conclusions:{RESET}")
        for i, c in enumerate(report.conclusions, 1):
            print(f"    {i}. {c}")

    if report.recommendations:
        print()
        print(f"  {MAGENTA}{BOLD}Recommendations:{RESET}")
        for i, r in enumerate(report.recommendations, 1):
            print(f"    {i}. {r}")

    if report.citations:
        print()
        print(f"  {DIM}References: {len(report.citations)} sources cited{RESET}")


# ── Core async runner ────────────────────────────────────────────────────────

async def run_pipeline(query: str) -> dict:
    """
    Run the full Planner → Researcher → Analyst → Writer pipeline
    with step-by-step console output.
    """
    banner(f"Research-to-Report  |  Phi-4 Reasoning Agent")
    print(f"\n  {BOLD}Query:{RESET} {query}\n")

    from src.utils.config import load_environment
    load_environment()

    # ── 1. PLANNER ─────────────────────────────────────────────────────────
    step("🗂 ", "Planner", "Decomposing query into subtasks…", BLUE)
    t0 = time.time()

    from src.agents.planner import PlannerAgent
    planner = PlannerAgent()
    plan = await planner.decompose_task(query)
    elapsed = time.time() - t0

    step("✅", "Planner complete", f"{plan.total_tasks} tasks  |  {elapsed:.1f}s", GREEN)
    print_plan(plan)

    # Validate plan
    step("🔎", "Validating plan…", "", DIM)
    validation = await planner.validate_plan(plan)
    if validation["is_valid"]:
        step("✅", "Plan valid", f"can_proceed={validation['can_proceed']}", GREEN)
    else:
        step("⚠ ", "Plan warnings", str(validation.get("warnings", [])), YELLOW)

    # ── 2. RESEARCHER ───────────────────────────────────────────────────────
    step("🔍", "Researcher", "Searching web via Azure MCP toolbox…", CYAN)
    t0 = time.time()

    from src.agents.researcher import ResearcherAgent
    researcher = ResearcherAgent()
    research_results = await researcher.search(query, max_results=10)
    elapsed = time.time() - t0

    step("✅", "Research complete",
         f"{research_results.total_sources} sources  |  {elapsed:.1f}s", GREEN)
    print_research(research_results)

    # ── 3. ANALYST ──────────────────────────────────────────────────────────
    step("🧠", "Analyst", "Extracting insights & reasoning…", MAGENTA)
    t0 = time.time()

    research_data = {
        "sources": [
            {
                "title": r.title,
                "snippet": r.snippet,
                "source_name": r.source_name,
                "url": r.url,
                "relevance_score": r.relevance_score,
            }
            for r in (research_results.high_confidence_sources
                      + research_results.medium_confidence_sources)
        ],
        "search_results": research_results.sources_used,
    }

    from src.agents.analyst import AnalystAgent
    analyst = AnalystAgent()
    analysis = await analyst.analyze(query, research_data)
    elapsed = time.time() - t0

    step("✅", "Analysis complete",
         f"{len(analysis.key_findings)} findings  |  {len(analysis.risks_identified)} risks  |  {elapsed:.1f}s", GREEN)
    print_analysis(analysis)

    # ── 4. WRITER ───────────────────────────────────────────────────────────
    step("📝", "Writer", "Generating structured report…", YELLOW)
    t0 = time.time()

    analysis_data = {
        "key_findings": [
            {
                "insight_id": f.insight_id,
                "category": f.category,
                "statement": f.statement,
                "confidence": f.confidence,
                "evidence": f.evidence,
                "evidence_strength": f.evidence_strength.value,
                "caveats": f.caveats,
                "source_count": f.source_count,
            }
            for f in analysis.key_findings
        ],
        "risks_identified": [
            {
                "risk_id": r.risk_id,
                "title": r.title,
                "description": r.description,
                "level": r.level.value,
                "probability": r.probability,
                "impact": r.impact,
                "risk_score": r.risk_score,
                "factors": r.factors,
                "mitigation": r.mitigation,
                "evidence": r.evidence,
                "confidence": r.confidence,
            }
            for r in analysis.risks_identified
        ],
        "patterns_detected": analysis.patterns_detected,
        "reasoning_chain": analysis.reasoning_chain,
        "overall_confidence": analysis.overall_confidence,
        "data_sources_analyzed": analysis.data_sources_analyzed,
        "sources": research_data["sources"],
    }

    from src.agents.writer import WriterAgent, ReportFormat
    writer = WriterAgent()
    report = await writer.generate_report(query, analysis_data)
    elapsed = time.time() - t0

    step("✅", "Report complete",
         f"{len(report.sections)} sections  |  {elapsed:.1f}s", GREEN)
    print_report(report)

    # ── FINAL SUMMARY ────────────────────────────────────────────────────────
    banner("Pipeline Complete  🎉", GREEN)
    print(f"  {BOLD}Query     :{RESET} {query}")
    print(f"  {BOLD}Plan ID   :{RESET} {plan.plan_id}")
    print(f"  {BOLD}Report ID :{RESET} {report.metadata.report_id}")
    print(f"  {BOLD}Confidence:{RESET} {report.metadata.confidence_score:.0%}")
    print()

    # Save Markdown to disk
    md_path = ROOT / f"output_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    md_text = await writer.format_output(report, ReportFormat.MARKDOWN)
    md_path.write_text(md_text, encoding="utf-8")
    print(f"  📁  Markdown saved → {md_path.name}")
    print()

    return {
        "plan": plan.model_dump(),
        "research": {
            "total_sources": research_results.total_sources,
            "confidence": research_results.confidence_score,
        },
        "analysis": {
            "findings": len(analysis.key_findings),
            "risks": len(analysis.risks_identified),
            "confidence": analysis.overall_confidence,
        },
        "report": {
            "id": report.metadata.report_id,
            "title": report.metadata.title,
            "confidence": report.metadata.confidence_score,
            "markdown_file": str(md_path),
        },
    }


# ── CLI ──────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description="Research-to-Report Multi-Agent Demo (Azure AI Foundry + Phi-4)"
    )
    p.add_argument(
        "--query", "-q",
        default="What are the top 3 investment risks in the Indian EV market?",
        help="Research question to process (default: EV market risks)",
    )
    p.add_argument(
        "--model", "-m",
        choices=["phi-4-mini-reasoning", "phi-4-reasoning"],
        help="Override the model deployment (overrides .env)",
    )
    p.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive loop (type queries one by one)",
    )
    return p.parse_args()


async def interactive_loop():
    banner("Interactive Mode — Phi-4 Reasoning Agent")
    print("  Type a research question and press Enter.")
    print("  Type 'exit' or Ctrl-C to quit.\n")
    while True:
        try:
            q = input(f"{CYAN}Query>{RESET} ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
        if not q:
            continue
        if q.lower() in ("exit", "quit", "q"):
            print("Goodbye!")
            break
        await run_pipeline(q)


async def main_async(args):
    if args.model:
        os.environ["AZURE_OPENAI_DEPLOYMENT"] = args.model
        print(f"{DIM}[demo] Overriding model to: {args.model}{RESET}")

    if args.interactive:
        await interactive_loop()
    else:
        result = await run_pipeline(args.query)
        # Also dump JSON summary
        summary_path = ROOT / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        summary_path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
        print(f"  📁  JSON summary saved → {summary_path.name}\n")


def main():
    args = parse_args()
    try:
        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        print("\nInterrupted. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
