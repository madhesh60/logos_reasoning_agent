# Agent Design and Multi-Agent Architecture

This document details the multi-agent architecture and design principles implemented in the LOGOS Autonomous Research Intelligence Agent.

---

## Architecture Overview

LOGOS uses a modular multi-agent system structured as a sequential pipeline. The architecture is designed to handle research tasks by decomposing, retrieving, scanning, profiling, analyzing, and synthesizing intelligence into a structured formal report.

The system is coordinated via a local orchestrator that interfaces with cloud-hosted agents on Microsoft Azure AI Foundry. It supports robust fallback mechanisms to local execution engines if a cloud-based agent becomes unavailable.

```
                  [ User Input Query ]
                           │
                           ▼
             [ SQLite Memory Context Load ]
                           │
                           ▼
          [ Human-in-the-Loop Clarification ] (2-3 Custom Questions)
                           │
                           ▼
             [ 6-Agent Execution Pipeline ]
                           │
  ┌────────────────────────┼────────────────────────┐
  ▼                        ▼                        ▼
Planner Agent       Researcher Agent     Industry News Scanner
(Decomposition)     (Web Grounding)      (Near-Term Signals)
  │                        │                        │
  └────────────────────────┼────────────────────────┘
                           │
                           ▼
             [ 6-Agent Execution Pipeline (Cont.) ]
                           │
  ┌────────────────────────┼────────────────────────┐
  ▼                        ▼                        ▼
Competitive Intel    Analyst Agent        Writer Agent
(Market Profiling)   (Risk Assessment)    (Report Drafting)
  │                        │                        │
  └────────────────────────┼────────────────────────┘
                           │
                           ▼
             [ SQLite Memory Context Sync ]
                           │
                           ▼
                 [ Generated Report ]
```

---

## The 6-Agent Pipeline

The core research pipeline consists of six specialized agents. Each agent inherits context accumulated by its predecessors, refining the overall analytical output.

### 1. Planner Agent (`planner-agent` | Version 9)
*   **Role**: Decomposes the user's research query into structured, sequential sub-tasks.
*   **Input**: User query and personalized profile context (name, role, domain).
*   **Process**: Evaluates the scope of the request, identifies critical topics of investigation, estimates execution durations, and specifies necessary tools (e.g., web search).
*   **Output**: A structured research plan containing a task execution path.

### 2. Researcher Agent (`researcher-agent` | Version 7)
*   **Role**: Gathers grounded factual intelligence from the web.
*   **Input**: Original query and the structured research plan.
*   **Process**: Invokes search queries using Model Context Protocol (MCP) search tools, scans relevant pages, and extracts key data points, figures, and direct source URLs.
*   **Output**: Grounded web research findings containing citations and verified links.

### 3. Industry News Scanner (`industry-news-trend-scanner` | Version 1)
*   **Role**: Analyzes recent developments, breaking press, and short-term trends.
*   **Input**: Current research context and query.
*   **Process**: Targets news engines and recent industry releases focusing on the last 3-6 months to capture market shifts not yet covered in traditional static reports.
*   **Output**: Chronological logs of trend signals, press summaries, and specific publication sources.

### 4. Competitive Landscape Researcher (`competitive-landscape-researcher` | Version 1)
*   **Role**: Maps the competitive landscape and identifies market structures.
*   **Input**: Query, accumulated research, and industry news logs.
*   **Process**: Extracts details on major competitors, their market share, core technologies, differentiation strategies, and strategic white-spaces.
*   **Output**: Competitive profiles and competitor positioning analysis.

### 5. Analyst Agent (`analyst-agent` | Version 4)
*   **Role**: Synthesizes facts, detects underlying patterns, and assesses risks.
*   **Input**: Raw research, news signals, and competitive profiles.
*   **Process**: Group findings into qualitative categories, evaluates the strength of evidence (Strong, Medium, Weak), detects market patterns, and computes risk scores based on probability and impact factors.
*   **Output**: Key findings, risk assessments with mitigation strategies, and an overall confidence score.

### 6. Writer Agent (`writer-agent` | Version 4)
*   **Role**: Drafts the final report in formal, structured markdown.
*   **Input**: Synthesized analysis findings, risk registers, and source links.
*   **Process**: Formats the final content using clean markdown sections (Executive Summary, Current Trends, Competitive Landscape, Opportunities & Risks, and Strategic Recommendations).
*   **Output**: The complete generated report object containing metadata, summaries, structured sections, conclusions, and citation reference lists.

---

## Agent-to-Agent (A2A) Protocol

The communication between agents follows a strict A2A pattern implemented over HTTP. When `enable_a2a` is active, the orchestrator routes sequential calls to the FastAPI endpoints.

*   **Service Integration**: The FastAPI application (`main.py`) acts as the API interface, exposing endpoints like `/ask` for the sequential pipeline and `/research` for parallelized execution.
*   **Configuration Parameters**: Controlled via `.env` options:
    *   `A2A_HOST`: Defines the binding host (default `0.0.0.0`).
    *   `A2A_PORT`: Port mapping for local deployment (default `8080`).
    *   `A2A_TIMEOUT`: Maximum execution limit in seconds before fallback (default `30`s).

---

## Human-in-the-Loop (HITL) Clarification

To prevent generic outputs and tailor the analysis to the user's actual needs, the orchestrator triggers an interactive HITL phase before initiating the multi-agent pipeline.

1.  **Question Generation**: A dedicated prompting routine generates up to three sharp, query-specific clarifying questions.
2.  **Context Mixing**: This process uses the local SQLite memory context (the user's profile details and previous search summary logs) to ensure questions target gaps in the current profile.
3.  **Interaction Loop**: The CLI prompts the user to input answers to each question. If the user hits enter without answering, the system skips that question and uses defaults.
4.  **Payload Injection**: The resulting question-answer pairs are structured into a `=== USER CLARIFICATIONS ===` block and prepended to all downstream agent system prompts, ensuring alignment across all 6 pipeline stages.
