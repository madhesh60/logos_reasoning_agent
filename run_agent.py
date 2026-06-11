#!/usr/bin/env python3
"""
run_agent.py — Phi-4 · Azure Foundry Multi-Agent Research Terminal
===================================================================
  python run_agent.py                          # interactive mode
  python run_agent.py -q "NLP trends 2025"    # single query
  python run_agent.py --model-test             # verify model connection
  python run_agent.py --search-test            # verify web search
"""

import asyncio
import argparse
import sys
import os
import time
from pathlib import Path
from datetime import datetime

# ── Windows UTF-8 console ─────────────────────────────────────────────────────
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

# ── Suppress noise ────────────────────────────────────────────────────────────
os.environ["LANGGRAPH_STRICT_MSGPACK"] = "true"
import warnings; warnings.filterwarnings("ignore")

from src.utils.logging import configure_logging
configure_logging(log_level="WARNING", json_format=False)
import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("azure").setLevel(logging.WARNING)

# ── Rich UI ───────────────────────────────────────────────────────────────────
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.status import Status
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table
from rich.columns import Columns
from rich import box

console = Console(highlight=True)

# ── Brand colours ─────────────────────────────────────────────────────────────
BRAND   = "deep_sky_blue1"
ACCENT  = "medium_purple1"
SUCCESS = "bright_green"
WARN    = "yellow"
DANGER  = "bright_red"
DIM     = "grey58"

def _banner():
    console.print()
    console.print(Panel.fit(
        Text.assemble(
            (" ◈ ", ACCENT),
            ("FOUNDRY RESEARCH INTELLIGENCE", f"bold {BRAND}"),
            (" ◈", ACCENT),
            ("\n", ""),
            ("  Phi-4 · Azure AI Foundry · Multi-Agent Pipeline  ", DIM),
        ),
        border_style=BRAND,
        padding=(0, 3),
    ))
    console.print()

def ok(msg):   console.print(f"  [{SUCCESS}]✔[/]  {msg}")
def warn(msg): console.print(f"  [{WARN}]⚠[/]  {msg}")
def fail(msg): console.print(f"  [{DANGER}]✘[/]  {msg}")
def info(msg): console.print(f"  [{DIM}]›[/]  {msg}")

PIPELINE_STAGES = [
    ("🧠 Planner",               "Decomposing your query into research tasks"),
    ("🔍 Researcher",            "Fetching latest data from the web"),
    ("📰 Industry-News Scanner", "Scanning real-time industry signals"),
    ("⚔  Competitive Intel",     "Mapping competitive landscape"),
    ("📊 Analyst",               "Extracting insights and risk factors"),
    ("✍  Writer",                "Generating the structured report"),
]

# ── Args ─────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(
        description="Foundry Research Intelligence — Multi-Agent Report Generator",
    )
    p.add_argument("-q", "--query",       help="Research query")
    p.add_argument("-m", "--model",       default=None, help="Override LLM deployment")
    p.add_argument("--model-test",        action="store_true")
    p.add_argument("--search-test",       action="store_true")
    p.add_argument("--no-a2a",            action="store_true",
                   help="Skip Foundry agents, use local Phi-4 only")
    return p.parse_args()

# ── Model test ────────────────────────────────────────────────────────────────
async def run_model_test(model_override=None):
    console.print(Rule(f"[{BRAND}]Model Connection Test", style=BRAND))
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    api_key  = os.environ.get("AZURE_OPENAI_API_KEY", "")
    deploy   = model_override or os.environ.get("AZURE_OPENAI_DEPLOYMENT", "phi-4-mini-reasoning")

    info(f"Endpoint  : {endpoint[:60]}…")
    info(f"Deployment: {deploy}")

    from openai import OpenAI
    client = OpenAI(base_url=endpoint.rstrip("/"), api_key=api_key)
    with console.status(f"[{BRAND}]Pinging model…", spinner="aesthetic"):
        try:
            r = client.chat.completions.create(
                model=deploy,
                messages=[{"role":"user","content":"Reply with one sentence about AI in 2025."}],
                max_tokens=120,
            )
            text = r.choices[0].message.content or "(no content)"
            console.print(Panel(text, title="Model Reply", border_style=SUCCESS))
            ok(f"Tokens used: {r.usage.total_tokens if r.usage else 'N/A'}")
            return True
        except Exception as e:
            fail(str(e)); return False

# ── Search test ───────────────────────────────────────────────────────────────
async def run_search_test():
    console.print(Rule(f"[{ACCENT}]Web Search Test", style=ACCENT))
    from src.mcp_tools.web_search import MCPWebSearchTool
    tool = MCPWebSearchTool(
        azure_project_endpoint=os.getenv("AZURE_PROJECT_ENDPOINT"),
        azure_toolbox_name=os.getenv("AZURE_TOOLBOX_NAME","reasoning-agent-web-search"),
        azure_toolbox_version=os.getenv("AZURE_TOOLBOX_VERSION","1"),
        azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    )
    q = "Top NLP breakthroughs 2025"
    info(f"Searching: {q}")
    with console.status(f"[{ACCENT}]Searching the web…", spinner="aesthetic"):
        resp = await tool.search(q, max_results=4)
    for i, r in enumerate(resp.results, 1):
        console.print(f"\n  [{BRAND}]{i}. {r.title}[/]")
        console.print(f"     [{DIM}]{r.url}[/]")
        console.print(f"     {r.snippet[:120]}…")
    await tool.close()

# ── Animated pipeline stages display ─────────────────────────────────────────
def _show_pipeline_running():
    """Show the 6-agent pipeline as a live progress list."""
    table = Table(box=None, show_header=False, padding=(0,1))
    table.add_column(justify="right", style=DIM, no_wrap=True)
    table.add_column(style="bold")
    table.add_column(style=DIM)
    for i, (name, desc) in enumerate(PIPELINE_STAGES):
        table.add_row(f"{i+1}.", name, desc)
    console.print(Panel(
        table,
        title=f"[{BRAND}]Active Pipeline[/]",
        border_style=BRAND,
        padding=(0, 1),
    ))

# ── Report printer ────────────────────────────────────────────────────────────
def _print_report(report, query: str, elapsed: float, path: str):
    """Render the GeneratedReport beautifully in the terminal."""

    console.print()
    console.print(Rule(f"[{SUCCESS}]  RESEARCH REPORT  ", style=SUCCESS))
    console.print()

    # ── Header stats bar ──────────────────────────────────────────────────────
    stats = Table(box=box.SIMPLE, show_header=False, padding=(0,2))
    stats.add_column(style=f"bold {BRAND}", no_wrap=True)
    stats.add_column(style="white")
    conf = report.metadata.confidence_score
    conf_color = SUCCESS if conf >= 0.8 else (WARN if conf >= 0.6 else DANGER)
    stats.add_row("⏱  Generated in", f"{elapsed:.1f}s")
    stats.add_row("🔀  Path",         path.replace("_", " ").title())
    stats.add_row("📊  Confidence",   f"[{conf_color}]{conf:.0%}[/]")
    stats.add_row("🆔  Report ID",    report.metadata.report_id)
    console.print(Panel(stats, border_style=DIM, padding=(0,1)))
    console.print()

    # ── Title & executive summary ─────────────────────────────────────────────
    title = report.metadata.title or query
    console.print(Panel(
        Markdown(f"# {title}\n\n{report.executive_summary}"),
        border_style=BRAND, padding=(1, 2),
        title=f"[bold {BRAND}]Executive Summary[/]",
    ))
    console.print()

    # ── Main sections ─────────────────────────────────────────────────────────
    for sec in report.sections:
        if sec.content and sec.title:
            console.print(Panel(
                Markdown(sec.content),
                title=f"[bold {ACCENT}]{sec.title}[/]",
                border_style=ACCENT,
                padding=(0, 2),
            ))
            console.print()

    # ── Conclusions ───────────────────────────────────────────────────────────
    if report.conclusions:
        md = "\n".join(f"- {c}" for c in report.conclusions)
        console.print(Panel(
            Markdown(md),
            title=f"[bold {SUCCESS}]Key Conclusions[/]",
            border_style=SUCCESS,
            padding=(0, 2),
        ))
        console.print()

    # ── Recommendations ───────────────────────────────────────────────────────
    if report.recommendations:
        md = "\n".join(f"{i}. {r}" for i, r in enumerate(report.recommendations, 1))
        console.print(Panel(
            Markdown(md),
            title=f"[bold {WARN}]Strategic Recommendations[/]",
            border_style=WARN,
            padding=(0, 2),
        ))
        console.print()

    # ── Citations / Resources ─────────────────────────────────────────────────
    if report.citations:
        ref_md = "\n".join(
            f"- [{c.get('title','Link')}]({c.get('url','#')})  — *{c.get('source','')}*"
            for c in report.citations[:8]
        )
        console.print(Panel(
            Markdown(ref_md),
            title=f"[bold {DIM}]Resources & References[/]",
            border_style=DIM,
            padding=(0, 2),
        ))
        console.print()

    # ── Save ──────────────────────────────────────────────────────────────────
    _save_report(report, query)

def _save_report(report, query: str):
    try:
        slug  = query[:40].lower().replace(" ", "_").replace("/","")
        fname = ROOT / f"report_{slug}_{report.metadata.report_id}.md"
        lines = [
            f"# {report.metadata.title or query}",
            f"\n**Confidence:** {report.metadata.confidence_score:.0%}  "
            f"| **Generated:** {report.metadata.generated_at}  "
            f"| **ID:** `{report.metadata.report_id}`\n",
            "---\n",
            "## Executive Summary\n",
            report.executive_summary, "\n",
        ]
        for sec in report.sections:
            lines += [f"\n## {sec.title}\n", sec.content, "\n"]
        if report.conclusions:
            lines += ["\n## Conclusions\n"] + [f"- {c}\n" for c in report.conclusions]
        if report.recommendations:
            lines += ["\n## Recommendations\n"] + [f"{i}. {r}\n" for i, r in enumerate(report.recommendations, 1)]
        if report.citations:
            lines += ["\n## Resources\n"] + [
                f"- [{c.get('title','Link')}]({c.get('url','#')})\n"
                for c in report.citations[:10]
            ]
        fname.write_text("\n".join(lines), encoding="utf-8")
        ok(f"Report saved → {fname.name}")
    except Exception as e:
        warn(f"Could not save: {e}")

# ── Execute one query ─────────────────────────────────────────────────────────
async def execute_query(query: str, model_override=None, enable_a2a: bool = True):
    from src.utils.config import load_environment
    load_environment()

    if model_override:
        os.environ["AZURE_OPENAI_DEPLOYMENT"] = model_override

    from src.orchestration.research_workflow import ResearchWorkflow
    workflow = ResearchWorkflow(enable_a2a=enable_a2a, max_retries=1)

    console.print()
    console.print(Panel(
        f"[bold]{query}[/]",
        title=f"[{BRAND}]Research Query[/]",
        border_style=BRAND, padding=(0, 2),
    ))
    console.print()

    _show_pipeline_running()
    console.print()

    t_start = time.time()
    with console.status(
        f"[{BRAND}]Calling Foundry Writer Agent — generating your report…[/]",
        spinner="aesthetic",
        spinner_style=BRAND,
    ):
        result = await workflow.execute(query)

    elapsed = time.time() - t_start

    report = result.get("report")
    if report and report.executive_summary:
        ok(f"Workflow complete in {elapsed:.1f}s  ·  path: {result.get('path_used','?')}")
        _print_report(report, query, elapsed, result.get("path_used","?"))
    else:
        fail("No report generated. Check logs.")
        if result.get("error"):
            warn(result["error"])

# ── Interactive REPL ──────────────────────────────────────────────────────────
async def interactive_mode(model_override=None, enable_a2a: bool = True):
    _banner()

    console.print(Panel(
        Text.assemble(
            (f"  {'Command':<18}  Description\n", f"bold {BRAND}"),
            (f"  {'─'*18}  {'─'*40}\n", DIM),
            (f"  {'<your question>':<18}  ", ""),     ("Run full research pipeline\n", ""),
            (f"  {'model-test':<18}  ", ""),          ("Verify model connection\n", ""),
            (f"  {'search-test':<18}  ", ""),         ("Verify web search\n", ""),
            (f"  {'exit / quit':<18}  ", ""),         ("Exit the terminal", ""),
        ),
        title=f"[{ACCENT}]Commands[/]",
        border_style=ACCENT,
        padding=(0, 2),
    ))
    console.print()

    while True:
        try:
            query = Prompt.ask(f"\n  [{BRAND}]>[/]")
        except (KeyboardInterrupt, EOFError):
            console.print(f"\n  [{DIM}]Goodbye ◈[/]\n"); break

        query = query.strip()
        if not query:
            continue
        if query.lower() in ("exit", "quit", "q", "bye"):
            console.print(f"\n  [{DIM}]Goodbye ◈[/]\n"); break
        if query.lower() == "model-test":
            await run_model_test(model_override); continue
        if query.lower() == "search-test":
            await run_search_test(); continue

        try:
            await execute_query(query, model_override, enable_a2a=enable_a2a)
        except Exception as exc:
            fail(f"Pipeline error: {exc}")

# ── Entry ─────────────────────────────────────────────────────────────────────
async def main():
    args = parse_args()

    if args.model_test:
        await run_model_test(args.model); sys.exit(0)
    if args.search_test:
        await run_search_test(); sys.exit(0)

    enable_a2a = not args.no_a2a

    if args.query:
        _banner()
        await execute_query(args.query, args.model, enable_a2a=enable_a2a)
    else:
        await interactive_mode(args.model, enable_a2a=enable_a2a)

if __name__ == "__main__":
    asyncio.run(main())
