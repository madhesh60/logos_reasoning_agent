"""
logos/cli.py — LOGOS command-line interface
============================================

Entry point: logos = "logos.cli:main"

After  pip install logos-research  →  run  logos

Features
--------
  - First-run setup wizard (provider, API key, model)
  - Persistent memory  (~/.logos/memory.db)
  - Human-in-the-loop clarifying questions before research
  - 4-stage research pipeline  (works with any OpenAI-compatible API)
  - Optional Azure AI Foundry 6-agent pipeline (for Foundry users)
  - Story-driven narrative CLI — no emojis, intelligence-briefing tone
"""

from __future__ import annotations

import asyncio
import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# ── Windows UTF-8 ─────────────────────────────────────────────────────────────
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Path setup (local dev: project root on sys.path) ─────────────────────────
_CLI_DIR = Path(__file__).resolve().parent
_ROOT    = _CLI_DIR.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# ── Load .env — CWD first, then ~/.logos/.env ─────────────────────────────────
from dotenv import load_dotenv
_LOGOS_HOME = Path.home() / ".logos"
_LOGOS_HOME.mkdir(parents=True, exist_ok=True)
load_dotenv(Path.cwd() / ".env", override=False)
load_dotenv(_LOGOS_HOME / ".env", override=False)

# ── Silence noisy loggers ─────────────────────────────────────────────────────
import warnings
warnings.filterwarnings("ignore")
import logging
for _log in ("httpx", "azure", "openai", "urllib3"):
    logging.getLogger(_log).setLevel(logging.ERROR)

# ── Rich ──────────────────────────────────────────────────────────────────────
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.rule import Rule
from rich import box

console = Console(highlight=False)

C_RULE   = "grey46"
C_TITLE  = "bold white"
C_DIM    = "grey46"
C_OK     = "green3"
C_WARN   = "yellow3"
C_ERR    = "red3"
C_LABEL  = "white"
C_ACCENT = "steel_blue1"
C_BORDER = "grey30"

# ── Imports ───────────────────────────────────────────────────────────────────
from logos.config   import Config, PROVIDERS
from logos.memory.store import MemoryStore
from logos.hitl.questioner import generate_questions
from logos.research.pipeline import ResearchPipeline, STAGES


# ── UI helpers ────────────────────────────────────────────────────────────────

def _rule(title: str = "") -> None:
    if title:
        console.print(Rule(f"[{C_DIM}]{title}[/]", style=C_RULE))
    else:
        console.print(Rule(style=C_RULE))

def _p(msg: str, indent: int = 2) -> None:
    console.print(" " * indent + msg)

def _blank() -> None:
    console.print()

def _ok(msg: str)   -> None: _p(f"[{C_OK}]{msg}[/]")
def _warn(msg: str) -> None: _p(f"[{C_WARN}]{msg}[/]")
def _err(msg: str)  -> None: _p(f"[{C_ERR}]{msg}[/]")
def _dim(msg: str)  -> None: _p(f"[{C_DIM}]{msg}[/]")

def _ask(prompt_text: str, password: bool = False) -> str:
    _blank()
    if password:
        import getpass
        console.print(f"  [{C_ACCENT}]{prompt_text}[/]", end="")
        try:
            return getpass.getpass("  ").strip()
        except Exception:
            return ""
    try:
        return console.input(f"  [{C_ACCENT}]{prompt_text}[/]  ").strip()
    except (KeyboardInterrupt, EOFError):
        raise


# ── Banner ────────────────────────────────────────────────────────────────────

def _banner() -> None:
    _blank()
    console.print(f"  [{C_TITLE}]L O G O S[/]   [{C_DIM}]— Autonomous Research Intelligence[/]")
    _p(f"[{C_DIM}]{'─' * 54}[/]")
    _blank()


# ── Setup wizard ──────────────────────────────────────────────────────────────

async def run_setup(cfg: Config, *, force: bool = False) -> None:
    """
    Interactive setup wizard. Runs on first install or `logos setup`.
    Saves provider, API key, and model to ~/.logos/config.json.
    """
    _rule("Setup")
    _blank()

    if not force and cfg.is_configured():
        _p(f"[{C_LABEL}]LOGOS is already configured.[/]")
        _dim(f"Provider : {cfg.provider_label}")
        _dim(f"Model    : {cfg.model}")
        _blank()
        change = _ask("Reconfigure?  [y/N]  >")
        if change.lower() not in ("y", "yes"):
            return

    _blank()
    _p(f"[{C_LABEL}]Choose your AI provider.[/]")
    _blank()

    provider_keys = list(PROVIDERS.keys())
    for i, (key, info) in enumerate(PROVIDERS.items(), 1):
        label    = info["label"]
        advanced = "  (advanced)" if info.get("advanced") else ""
        _p(f"  [{C_DIM}]{i}[/]  {label}{advanced}")

    _blank()
    choice_raw = _ask("Provider  [1-6]  >")
    try:
        idx = int(choice_raw) - 1
        if not (0 <= idx < len(provider_keys)):
            raise ValueError
        provider_key = provider_keys[idx]
    except ValueError:
        _err("Invalid choice. Defaulting to OpenAI.")
        provider_key = "openai"

    prov = PROVIDERS[provider_key]
    cfg.set("provider", provider_key)
    _blank()

    # API key
    if provider_key == "ollama":
        cfg.set("api_key", "ollama")
        _ok("Ollama selected. No API key needed.")
    elif provider_key == "foundry":
        _dim("Azure AI Foundry requires two endpoint URLs.")
        ep = _ask("Azure project endpoint  >")
        cfg.set("azure_project_endpoint", ep)
        cfg.set("api_key", "foundry")
    else:
        hint = prov.get("key_hint", "Your API key")
        _p(f"[{C_DIM}]Get your key from the provider dashboard.[/]")
        key = _ask(f"API key  ({hint})  >", password=True)
        cfg.set("api_key", key)

        if prov.get("needs_endpoint") and provider_key == "azure":
            ep = _ask("Azure endpoint  (https://your-resource.openai.azure.com)  >")
            cfg.set("azure_endpoint", ep)

    # Model
    models = prov.get("models", [])
    default_model = prov.get("default_model", "")
    if models and provider_key != "foundry":
        _blank()
        _p(f"[{C_LABEL}]Choose a model.[/]")
        for i, m in enumerate(models, 1):
            tag = "  (default)" if m == default_model else ""
            _p(f"  [{C_DIM}]{i}[/]  {m}{tag}")
        m_choice = _ask(f"Model  [1-{len(models)}  or type name]  (Enter = {default_model})  >")
        if not m_choice:
            cfg.set("model", default_model)
        else:
            try:
                mi = int(m_choice) - 1
                cfg.set("model", models[mi] if 0 <= mi < len(models) else default_model)
            except ValueError:
                cfg.set("model", m_choice)  # allow custom model name

    cfg.save()
    _blank()
    _ok(f"Setup complete.  Provider: {cfg.provider_label}  |  Model: {cfg.model}")
    _blank()


# ── First-time user profile ───────────────────────────────────────────────────

async def _user_profile_setup(memory: MemoryStore) -> None:
    _blank()
    _p(f"[{C_LABEL}]Before your first investigation, a few quick questions.[/]")
    _dim("These help LOGOS personalise every report. Press Enter to skip any.")
    _blank()

    name   = _ask("Your name  >")
    role   = _ask("Role or function  (e.g. founder, analyst, researcher)  >")
    org    = _ask("Organization or project  >")
    domain = _ask("Primary domain of research  (e.g. AI, fintech, biotech)  >")

    _blank()
    _p(f"[{C_LABEL}]Preferred report depth:[/]")
    _dim("  1   Concise — executive-level summaries")
    _dim("  2   Detailed — full analysis with evidence")
    depth_raw = _ask("Choice  [1/2]  >")
    depth = "concise" if depth_raw.strip() == "1" else "detailed"

    kwargs: dict[str, str] = {"depth_preference": depth}
    if name:   kwargs["name"]         = name
    if role:   kwargs["role"]         = role
    if org:    kwargs["organization"] = org
    if domain: kwargs["domain"]       = domain

    memory.set_profile(**kwargs)
    _blank()
    _ok("Profile saved. LOGOS will personalise every report to your context.")
    _blank()
    _rule()


# ── Session greeting ──────────────────────────────────────────────────────────

def _greet(memory: MemoryStore, cfg: Config) -> None:
    profile    = memory.get_user_profile()
    recent     = memory.get_recent_queries(3)
    total      = memory.total_query_count()
    session_no = memory.session_number()
    entities   = memory.get_tracked_entities(4)
    now_str    = datetime.now().strftime("%A, %d %B %Y  |  %H:%M")
    name       = profile.get("name", "")

    session_line = f"Session {session_no}  |  {now_str}"
    if name:
        session_line += f"  |  Welcome back, {name}"
    session_line += f"  |  {cfg.provider_label}  /  {cfg.model}"

    _p(f"[{C_DIM}]{session_line}[/]")
    _blank()

    if total > 0:
        _dim(f"Your research history spans {total} {'query' if total == 1 else 'queries'}.")
        if entities:
            top = ", ".join(e["name"] for e in entities[:3])
            _dim(f"Frequently investigated: {top}.")
        if recent:
            _dim(f"Last query: \"{recent[0]['query'][:70]}\".")

    _blank()


# ── Human-in-the-loop ─────────────────────────────────────────────────────────

async def _run_hitl(query: str, memory: MemoryStore, cfg: Config) -> str:
    _blank()
    _rule("Investigation received")
    _blank()
    _p(f"[{C_LABEL}]Before the research begins, a few clarifying questions.[/]")
    _dim("Your answers will shape the depth and direction of the report.")
    _blank()

    memory_ctx = memory.build_context_string() if not memory.is_first_run() else ""

    with console.status(f"  [{C_DIM}]Preparing questions...[/]", spinner="line", spinner_style=C_DIM):
        questions = await generate_questions(query, memory_ctx, cfg=cfg)

    if not questions:
        return ""

    qa_pairs: list[str] = []
    for i, q_text in enumerate(questions, 1):
        _rule(f"Question {i} of {len(questions)}")
        _blank()
        _p(f"[{C_LABEL}]{q_text}[/]")
        try:
            ans = _ask(">")
        except (KeyboardInterrupt, EOFError):
            ans = ""
        if ans:
            qa_pairs.append(f"Q: {q_text}\nA: {ans}")
        else:
            _dim("(skipped)")

    _blank()
    _rule()
    _blank()
    _dim("Understood. Dispatching the research team now.")
    _blank()

    if not qa_pairs:
        return ""
    return "=== USER CLARIFICATIONS ===\n" + "\n\n".join(qa_pairs) + "\n=== END CLARIFICATIONS ==="


# ── Pipeline status live display ──────────────────────────────────────────────

_STAGE_STATUS: dict[str, str] = {}
_STAGE_LOCK = asyncio.Lock()

_ALL_STAGES_DEF = [
    ("planner",    "Decomposing the query into a research framework"),
    ("researcher", "Conducting deep research across sources"),
    ("analyst",    "Synthesising findings and assessing risk"),
    ("writer",     "Composing the structured report"),
    # Foundry extras (shown only when Foundry pipeline is active)
    ("industry_news", "Scanning real-time industry signals"),
    ("competitive",   "Mapping the competitive landscape"),
]

def _render_pipeline_panel(active_stages: list[tuple[str, str]]) -> str:
    lines = []
    for sid, sdesc in active_stages:
        st = _STAGE_STATUS.get(sid, "waiting")
        if st == "running":
            icon = f"[{C_ACCENT}]>[/]"
            col  = C_LABEL
        elif st == "done":
            icon = f"[{C_OK}].[/]"
            col  = C_DIM
        elif st == "failed":
            icon = f"[{C_WARN}]![/]"
            col  = C_WARN
        else:
            icon = f"[{C_DIM}]-[/]"
            col  = C_DIM
        lines.append(f"  {icon}  [{col}]{sdesc}[/]")
    return "\n".join(lines)


# ── Execute a research query ──────────────────────────────────────────────────

async def execute_query(
    query:       str,
    memory:      MemoryStore,
    cfg:         Config,
    skip_hitl:   bool = False,
    use_foundry: bool = False,
) -> None:

    memory_ctx = memory.build_context_string() if not memory.is_first_run() else ""
    clarifications = ""

    if not skip_hitl:
        try:
            clarifications = await _run_hitl(query, memory, cfg)
        except (KeyboardInterrupt, EOFError):
            _blank()
            _dim("Clarifications skipped.")
    else:
        _blank()

    # ── Choose pipeline ───────────────────────────────────────────────────────
    if use_foundry or cfg.provider == "foundry":
        result = await _run_foundry_pipeline(query, memory_ctx, clarifications)
    else:
        result = await _run_standard_pipeline(query, memory_ctx, clarifications, cfg)

    # ── Render ────────────────────────────────────────────────────────────────
    report_text = result.get("report_text", "")
    elapsed     = result.get("elapsed", 0)
    report_id   = result.get("report_id", "unknown")
    stages_ok   = result.get("stages_ok", [])

    if not report_text:
        _err("The research pipeline did not return a report.")
        _warn("Check your API key and network connection.")
        return

    _blank()
    _rule("Report")
    _blank()
    _p(
        f"[{C_DIM}]Generated in[/] [{C_LABEL}]{elapsed:.1f}s[/]   "
        f"[{C_DIM}]Stages completed[/] [{C_LABEL}]{len(stages_ok)}[/]   "
        f"[{C_DIM}]ID[/] [{C_DIM}]{report_id}[/]"
    )
    _blank()

    console.print(Panel(
        Markdown(report_text),
        border_style=C_BORDER,
        padding=(0, 2),
    ))
    _blank()

    # Save file
    fname = _save_report_file(query, report_text, report_id)
    _dim(f"Report saved: {fname.name}")

    # Save to memory
    query_id = await _save_to_memory(query, report_text, memory, result)

    # Offer bookmark
    await _offer_bookmark(query_id, memory)


# ── Standard pipeline runner ──────────────────────────────────────────────────

async def _run_standard_pipeline(
    query: str,
    memory_ctx: str,
    clarifications: str,
    cfg: Config,
) -> dict:
    pipeline = ResearchPipeline(cfg)

    stages_for_display = [("planner","Planning"), ("researcher","Researching"),
                          ("analyst","Analysing"), ("writer","Writing")]

    status_lines = {sid: "waiting" for sid, _ in stages_for_display}

    with console.status(f"  [{C_DIM}]Research in progress...[/]", spinner="line", spinner_style=C_DIM) as sp:
        async def progress_cb(stage_id: str, status: str) -> None:
            status_lines[stage_id] = status
            labels = {"planner":"Planning","researcher":"Researching",
                      "analyst":"Analysing","writer":"Writing"}
            running = next((labels[s] for s, st in status_lines.items() if st == "running"), "Running")
            sp.update(f"  [{C_DIM}]{running}...[/]")

        result = await pipeline.execute(
            query,
            memory_context=memory_ctx,
            user_clarifications=clarifications,
            progress_cb=progress_cb,
        )

    return result


# ── Foundry pipeline runner ───────────────────────────────────────────────────

async def _run_foundry_pipeline(
    query: str,
    memory_ctx: str,
    clarifications: str,
) -> dict:
    try:
        from src.orchestration.research_workflow import ResearchWorkflow
    except ImportError:
        _err("Azure AI Foundry pipeline is not available in this installation.")
        _warn("Run 'logos setup' and select a different provider.")
        return {}

    workflow = ResearchWorkflow(enable_a2a=True, max_retries=1)
    t0 = time.time()

    with console.status(f"  [{C_DIM}]Foundry 6-agent pipeline running...[/]", spinner="line", spinner_style=C_DIM):
        raw = await workflow.execute(
            query,
            memory_context=memory_ctx,
            user_clarifications=clarifications,
        )

    elapsed = time.time() - t0
    report  = raw.get("report")
    if not report:
        return {}

    # Flatten Foundry report object to standard dict
    report_text = _flatten_foundry_report(report)
    return {
        "report_text":   report_text,
        "stages_ok":     raw.get("stages_ok", []),
        "stages_failed": raw.get("stages_failed", []),
        "report_id":     getattr(report.metadata, "report_id", "foundry"),
        "elapsed":       elapsed,
    }


def _flatten_foundry_report(report) -> str:
    """Convert a GeneratedReport object to a markdown string."""
    parts: list[str] = []
    title = getattr(report.metadata, "title", "Research Report")
    parts.append(f"# {title}\n")
    if report.executive_summary:
        parts.append(f"## Executive Summary\n\n{report.executive_summary}\n")
    for sec in report.sections:
        if sec.title and sec.content:
            parts.append(f"## {sec.title}\n\n{sec.content}\n")
    if report.conclusions:
        parts.append("## Conclusions\n\n" + "\n".join(f"- {c}" for c in report.conclusions))
    if report.recommendations:
        parts.append("## Recommendations\n\n" + "\n".join(
            f"{i}. {r}" for i, r in enumerate(report.recommendations, 1)
        ))
    if report.citations:
        parts.append("## Resources\n\n" + "\n".join(
            f"- [{c.get('title','Source')}]({c.get('url','#')})"
            for c in report.citations[:12]
        ))
    return "\n".join(parts)


# ── Memory helpers ────────────────────────────────────────────────────────────

async def _save_to_memory(
    query: str,
    report_text: str,
    memory: MemoryStore,
    result: dict,
) -> int:
    import re
    entities = list(dict.fromkeys(
        re.findall(r"\b[A-Z][a-zA-Z]{3,}(?:\s[A-Z][a-zA-Z]{2,})*\b", report_text)
    ))[:10]

    qid = memory.save_query(
        query    = query,
        summary  = report_text[:300],
        topics   = result.get("stages_ok", []),
        entities = entities,
    )
    for e in entities[:6]:
        memory.track_entity(e)
    return qid


async def _offer_bookmark(query_id: int, memory: MemoryStore) -> None:
    _blank()
    _rule("Memory")
    _blank()
    _p(f"[{C_LABEL}]Report saved to memory.[/]")
    _dim("Bookmark a key finding for your long-term record, or press Enter to skip.")
    try:
        insight = _ask("Bookmark  >")
    except (KeyboardInterrupt, EOFError):
        insight = ""
    if insight:
        memory.save_insight(query_id, insight)
        _ok("Saved.")
    else:
        _dim("Nothing bookmarked.")
    _blank()


def _save_report_file(query: str, report_text: str, report_id: str) -> Path:
    slug  = query[:40].lower().replace(" ", "_").replace("/", "").replace("\\", "")
    fname = Path.cwd() / f"report_{slug}_{report_id}.md"
    fname.write_text(report_text, encoding="utf-8")
    return fname


# ── Memory display commands ───────────────────────────────────────────────────

def cmd_memory(memory: MemoryStore) -> None:
    _blank()
    _rule("Memory")
    _blank()
    profile  = memory.get_user_profile()
    recent   = memory.get_recent_queries(5)
    entities = memory.get_tracked_entities(8)

    if profile:
        for k, v in profile.items():
            _p(f"[{C_DIM}]{k:<22}[/] {v}")
        _blank()
    if recent:
        _p(f"[{C_LABEL}]Recent investigations:[/]")
        for q in recent:
            ts = q["created_at"][:10]
            _dim(f"  {ts}  {q['query'][:70]}")
        _blank()
    if entities:
        _p(f"[{C_LABEL}]Frequently researched:[/]")
        for e in entities:
            _dim(f"  {e['name']:<30} mentioned {e['count']}x")
        _blank()
    if not profile and not recent:
        _dim("No memory stored yet.")
    _blank()


def cmd_insights(memory: MemoryStore) -> None:
    _blank()
    _rule("Bookmarked Insights")
    _blank()
    insights = memory.get_recent_insights(10)
    if insights:
        for i, ins in enumerate(insights, 1):
            _p(f"[{C_DIM}]{i}.[/]  {ins}")
            _blank()
    else:
        _dim("No insights bookmarked yet.")
    _blank()


# ── Model connection test ─────────────────────────────────────────────────────

async def cmd_model_test(cfg: Config) -> None:
    _banner()
    _rule("Connection Test")
    _blank()
    _dim(f"Provider : {cfg.provider_label}")
    _dim(f"Model    : {cfg.model}")
    _blank()

    with console.status(f"  [{C_DIM}]Pinging model...[/]", spinner="line", spinner_style=C_DIM):
        try:
            client = cfg.build_openai_client()
            r = client.chat.completions.create(
                model=cfg.model,
                messages=[{"role": "user", "content": "In one sentence, describe the state of AI in 2025."}],
                max_tokens=80,
            )
            text = r.choices[0].message.content or "(no content)"
            _ok("Model responded.")
            _blank()
            console.print(Panel(text, border_style=C_BORDER, padding=(0, 2)))
        except Exception as exc:
            _err(f"Connection failed: {exc}")
    _blank()


# ── Help ──────────────────────────────────────────────────────────────────────

def _print_help() -> None:
    _blank()
    _p(f"[{C_LABEL}]Commands:[/]")
    _dim("  Any text          Run a full research investigation")
    _dim("  setup             Reconfigure your AI provider")
    _dim("  memory            View your research history and profile")
    _dim("  insights          View bookmarked findings")
    _dim("  profile           Update your personal profile")
    _dim("  clear memory      Wipe all stored memory")
    _dim("  exit / quit       End the session")
    _blank()


# ── Interactive REPL ──────────────────────────────────────────────────────────

async def interactive_mode(
    cfg:           Config,
    memory:        MemoryStore,
    skip_hitl:     bool = False,
    use_foundry:   bool = False,
) -> None:
    _banner()

    if memory.is_first_run():
        await _user_profile_setup(memory)
    else:
        _greet(memory, cfg)

    _p(f"[{C_DIM}]State your investigation.  Type 'help' for commands,  'exit' to leave.[/]")
    _blank()

    while True:
        try:
            query = _ask(">")
        except (KeyboardInterrupt, EOFError):
            _blank()
            _dim("Session closed.")
            _blank()
            break

        if not query:
            continue

        low = query.lower().strip()

        if low in ("exit", "quit", "q"):
            _blank()
            _dim("Session closed.")
            _blank()
            break
        elif low == "help":
            _print_help()
        elif low == "memory":
            cmd_memory(memory)
        elif low == "insights":
            cmd_insights(memory)
        elif low == "profile":
            await _user_profile_setup(memory)
        elif low == "setup":
            await run_setup(cfg, force=True)
        elif low == "clear memory":
            _blank()
            confirm = _ask("Type 'confirm' to erase all memory  >")
            if confirm.lower() == "confirm":
                memory.db_path.unlink(missing_ok=True)
                memory.initialize()
                _ok("Memory cleared.")
            else:
                _dim("Cancelled.")
            _blank()
        else:
            try:
                await execute_query(
                    query, memory, cfg,
                    skip_hitl=skip_hitl,
                    use_foundry=use_foundry,
                )
            except KeyboardInterrupt:
                _blank()
                _warn("Investigation interrupted.")
                _blank()
            except Exception as exc:
                _err(f"Pipeline error: {exc}")
                _blank()

    memory.close()


# ── Argument parsing ──────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="logos",
        description="LOGOS — Autonomous Research Intelligence Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  logos                              interactive session\n"
            "  logos -q 'NLP trends 2025'         single query\n"
            "  logos setup                        configure provider\n"
            "  logos --no-hitl -q 'your query'   skip clarifying questions\n"
            "  logos --model-test                 test API connection\n"
        ),
    )
    p.add_argument("command",        nargs="?",       help="Command: setup, memory, insights")
    p.add_argument("-q", "--query",  default=None,    help="Run a single query non-interactively")
    p.add_argument("--no-hitl",      action="store_true", help="Skip clarifying questions")
    p.add_argument("--foundry",      action="store_true", help="Use Azure AI Foundry 6-agent pipeline")
    p.add_argument("--model-test",   action="store_true", help="Test model connection and exit")
    p.add_argument("--memory-path",  default=None,    help="Custom path for memory database")
    return p.parse_args()


# ── Entry point ───────────────────────────────────────────────────────────────

async def async_main() -> None:
    args   = parse_args()
    cfg    = Config()
    memory = MemoryStore(db_path=args.memory_path)
    memory.initialize()

    # ── Subcommands ───────────────────────────────────────────────────────────
    if args.command == "setup":
        _banner()
        await run_setup(cfg, force=True)
        return

    if args.command == "memory":
        _banner()
        cmd_memory(memory)
        return

    if args.command == "insights":
        _banner()
        cmd_insights(memory)
        return

    if args.model_test:
        await cmd_model_test(cfg)
        return

    # ── First-run: must configure a provider ─────────────────────────────────
    if not cfg.is_configured():
        _banner()
        _p(f"[{C_LABEL}]LOGOS is not configured yet.[/]")
        _blank()
        await run_setup(cfg)
        if not cfg.is_configured():
            _err("Setup incomplete. Run 'logos setup' to configure.")
            return

    # ── Single-query mode ─────────────────────────────────────────────────────
    if args.query:
        _banner()
        if memory.is_first_run():
            _dim("First session. Run 'logos' interactively to set up your profile.")
            _blank()
        else:
            _greet(memory, cfg)
        await execute_query(
            args.query, memory, cfg,
            skip_hitl=args.no_hitl,
            use_foundry=args.foundry,
        )
        memory.close()
        return

    # ── Interactive mode ──────────────────────────────────────────────────────
    await interactive_mode(
        cfg, memory,
        skip_hitl=args.no_hitl,
        use_foundry=args.foundry,
    )


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
