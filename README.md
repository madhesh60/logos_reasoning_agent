# LOGOS — Autonomous Research Intelligence Agent

LOGOS is a production-ready, multi-agent AI research pipeline designed to automate corporate competitive intelligence and market trend scanning. Powered by Microsoft Azure AI Foundry and utilizing reasoning models, the system decomposes complex topics, conducts web search grounding, scans near-term news, builds competitor profiles, performs risk assessments, and compiles comprehensive formal reports.

---

## Documentation Subdirectory

For detailed technical specifications, setup manuals, and architecture descriptions, refer to the following documents in the `docs/` folder:

*   **[Agent Design and Multi-Agent Architecture](docs/agent.md)**: Specifications of the 6-agent sequential pipeline, system prompts, A2A communication, and Human-in-the-Loop context integration.
*   **[Hackathon Alignment and Requirements Mapping](docs/hackathonAlignment.md)**: Clear alignment matrices demonstrating how the project satisfies the requirements for Battle #2, including Work IQ, Foundry IQ, and Fabric IQ layer emulation.
*   **[Developer Guide and Local Execution Manual](docs/developerGuide.md)**: Complete steps for cloning the repository, establishing virtual environments, configuring environment variables, running the CLI tools, launching the FastAPI server, and executing tests.
*   **[Microsoft Azure AI Foundry Usage Guide](docs/foundryUsage.md)**: Technical breakdown of Azure Project Client initialization, Responses API orchestration, Agents SDK Threads integration, and cloud-hosted container deployments.

---

## Features and Capabilities

*   **6-Agent LangGraph Pipeline**: Orchesrates specialized roles: Planner, Researcher, Industry News Scanner, Competitive Landscape Researcher, Analyst, and Writer.
*   **Persistent SQLite Memory**: Stores user profiles, preferences, research history, and entity mention metrics to personalize downstream model responses.
*   **Human-in-the-Loop (HITL) Clarification**: Dynamically generates targeted questions to refine the research scope before execution.
*   **Azure AI Foundry Integration**: Direct invocation of visual workflow-built agents via the Responses API and stateful assistants via the Agents SDK.
*   **Robust JSON Cleaning & Repair**: Utilities designed to strip model reasoning traces (`<think>...</think>`) and reconstruct malformed outputs.
*   **Dual Interface System**: Interactive command-line interface (CLI) for analysts and a FastAPI REST backend for system integrations.

---

## Installation

LOGOS can be installed locally via PyPI:

```bash
pip install logos-research
```

*Note: For active development and modifying source files, refer to the [Developer Setup Guide](docs/developerGuide.md).*

---

## Basic Usage

### Command Line Interface

```bash
# Start an interactive research REPL (recommended)
logos

# Run a single research query non-interactively
logos -q "What are the latest developments in NLP?"

# Execute a query bypassing cloud agents (local emulation mode)
logos --no-a2a -q "Summarize trends in fintech."

# Disable Human-in-the-Loop questions
logos --no-hitl -q "Analyze the cloud computing market."

# Diagnostic check for model endpoints
logos --model-test
```

### FastAPI Web Server

```bash
# Launch the local host API server
uvicorn main:app --reload --port 8000
```
Swagger interactive documentation is served at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## Technical Architecture

```
User Query ──► SQLite Memory Context Load ──► HITL Questioning ──► 6-Agent Cloud Orchestration
                                                                         │
                                                                   [ planner-agent ]
                                                                         │
                                                                 [ researcher-agent ]
                                                                         │
                                                             [ industry-news-scanner ]
                                                                         │
                                                               [ competitive-agent ]
                                                                         │
                                                                  [ analyst-agent ]
                                                                         │
                                                                   [ writer-agent ]
                                                                         │
                                                                         ▼
                                                                  Generated Report
```

---

## Proof of Execution and Traces

This section contains visual evidence of the running application, including CLI traces, container outputs, and Azure AI portal configurations.

### 1. Command-Line Interface Execution Trace
Below is a screenshot demonstrating the interactive setup process, Human-in-the-Loop question prompts, and final report rendering within the terminal interface:

![CLI Execution Trace](docs/images/cli_execution_trace.png)

### 2. Containerized Execution Logs
Below is the output log validating the container compilation and FastAPI server startup within a sandbox environment:

![Container Execution Logs](docs/images/container_execution_logs.png)

### 3. Azure AI Foundry Portal Configuration
Below is a dashboard capture showing the pre-deployed reasoning agent models and endpoints configured inside the Azure AI Foundry console:

![Azure AI Foundry Portal](docs/images/azure_foundry_portal.png)

---

## License

This project is licensed under the MIT License.
