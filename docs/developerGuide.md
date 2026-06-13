# Developer Setup Guide and Execution Manual

This document provides technical instructions for configuring the development environment, initializing local configurations, executing the command-line interface, launching the web API, and running tests.

---

## 1. System Requirements

Before beginning the installation, ensure your host environment meets the following specifications:
*   **Operating System**: Windows 10/11, macOS, or Linux.
*   **Python**: Version 3.10 or higher.
*   **Git**: Required for repository management.
*   **Access Credentials**: An active Azure subscription with access to Azure AI Foundry model deployments (specifically `phi-4-mini-reasoning`, `gpt-4o-mini`, or `gpt-4o`).

---

## 2. Installation and Environment Setup

### 2.1. Clone the Repository
```bash
git clone https://github.com/madhesh60/logos_reasoning_agent.git
cd logos_reasoning_agent
```

### 2.2. Create a Virtual Environment
To isolate project dependencies, create and activate a Python virtual environment:

*   **Windows (PowerShell)**:
    ```powershell
    python -m venv .venv
    .venv\Scripts\activate
    ```
*   **macOS / Linux**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

### 2.3. Install Dependencies
Install the package in editable developer mode alongside development packages:
```bash
# Install the core package
pip install -e .

# Install development and testing dependencies
pip install -e .[dev]
```
*(Alternatively, you can use `uv` for faster dependency installation: `uv pip install -e .[dev]`)*

---

## 3. Environment Variables Configuration

Copy the template environment configuration file to `.env`:
```bash
cp .env.example .env
```

Configure the following variables in the `.env` file to authorize model and MCP calls:

```ini
# ── AZURE OPENAI CONNECTION CONFIGURATION ──────────────────────────────────
# Base endpoint for Azure OpenAI service
AZURE_OPENAI_ENDPOINT=https://your-resource.services.ai.azure.com/openai/v1
# API key to authenticate model calls
AZURE_OPENAI_API_KEY=your-api-key-here
# Deployment name of the target reasoning model
AZURE_OPENAI_DEPLOYMENT=phi-4-mini-reasoning
# API version mapping
AZURE_OPENAI_API_VERSION=2024-02-01

# ── AZURE AI PROJECT ENDPOINT ──────────────────────────────────────────────
# Endpoint for your Azure AI Foundry project
AZURE_PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project-name
# Default toolbox name for web search
AZURE_TOOLBOX_NAME=reasoning-agent-web-search
# Default toolbox version
AZURE_TOOLBOX_VERSION=1

# ── MODEL CONTEXT PROTOCOL (MCP) ROUTER ────────────────────────────────────
# URL of the MCP server hosting Tavily Web Search and Azure Web Search
MCP_SERVER_URL=https://mcp.ai.azure.com

# ── PRE-DEPLOYED AZURE AI ASSISTANTS ───────────────────────────────────────
# Agent ID mapping for stateful competitive landscape researcher
AZURE_EXISTING_AGENT_ID=competitive-landscape-researcher:1

# ── LOCAL NETWORKING CONFIGURATION ──────────────────────────────────────────
# Network interface binding
A2A_HOST=0.0.0.0
# API port mapping
A2A_PORT=8080
# Timeout threshold in seconds
A2A_TIMEOUT=30
```

> [!WARNING]
> Never commit `.env` files or hardcoded credentials to public or private source control repositories.

---

## 4. Execution Interfaces

### 4.1. Command Line Interface (CLI)

The CLI is registered as a console script. Ensure your virtual environment is active before running commands:

*   **Interactive REPL Shell**:
    Guides you through name/role profile setup, loads memory database signals, and launches the chat loop:
    ```bash
    logos
    ```
*   **Single-Shot Investigation**:
    Submit a research query directly. The final report will print to the console and save to a markdown file in the current directory:
    ```bash
    logos -q "Evaluate the investment risks of the Indian EV charging sector."
    ```
*   **Bypass Cloud Agents (Local Emulation Mode)**:
    Runs the research process locally using configured LangChain fallback models:
    ```bash
    logos --no-a2a -q "Research current trends in edge computing."
    ```
*   **Diagnostics Check**:
    Ping the Azure OpenAI endpoint to verify credentials and liveness:
    ```bash
    logos --model-test
    ```

### 4.2. FastAPI REST Web Server

Start the local FastAPI server to expose endpoints for external integrations:
```bash
uvicorn main:app --reload --port 8080
```
Once initialized, open your browser to access the documentation interfaces:
*   **Swagger UI (Interactive Docs)**: [http://localhost:8080/docs](http://localhost:8080/docs)
*   **ReDoc (Static Specifications)**: [http://localhost:8080/redoc](http://localhost:8080/redoc)

---

## 5. Docker Container Build and Execution

To build and run the LOGOS web api container locally:

### 5.1. Build the Docker Image
```bash
docker build -t reasoningagentregistry.azurecr.io/logos-research-agent:latest .
```

### 5.2. Run the Container
```bash
docker run -d -p 8080:8080 --env-file .env reasoningagentregistry.azurecr.io/logos-research-agent:latest
```

---

## 6. Running the Test Suite

The test suite contains unit and integration tests using mock clients to validate agent reasoning logic, JSON cleaning wrappers, and A2A routing:

```bash
# Execute the test suite
pytest tests/test_agents.py -v

# Run tests and output coverage stats
pytest --cov=src --cov=logos tests/
```
