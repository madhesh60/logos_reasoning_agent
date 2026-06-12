# Developer Guide and Local Execution Manual

This document provides instructions on how to set up the developer environment, install dependencies, configure credentials, and run the LOGOS Autonomous Research Intelligence Agent locally.

---

## Prerequisites

Before setting up the project, ensure your environment meets the following requirements:

*   **Python**: Version 3.10 or higher.
*   **Git**: Required for repository cloning and version control.
*   **Package Manager**: `pip` (or `uv` for faster dependency resolution).
*   **Azure Account**: Active Azure subscription with access to Azure AI Foundry models (specifically `phi-4-mini-reasoning`).

---

## 1. Cloning & Installation

Clone the repository and set up a virtual environment:

### Step 1: Clone the Repository
```bash
git clone https://github.com/madhesh60/logos_reasoning_agent.git
cd logos_reasoning_agent
```

### Step 2: Create a Python Virtual Environment
*   **Windows**:
    ```powershell
    python -m venv .venv
    .venv\Scripts\activate
    ```
*   **macOS / Linux**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

### Step 3: Install Dependencies
Install the package and its dependencies in editable developer mode:
```bash
pip install -e .
```
For testing and development tools, install the optional dependencies:
```bash
pip install -e .[dev]
```

---

## 2. Environment Configuration

Copy the example environment file to `.env` in the root of the project:
```bash
cp .env.example .env
```

Open `.env` and fill in the required parameters:

```ini
# Azure OpenAI/Foundry model credentials
AZURE_OPENAI_ENDPOINT=https://your-resource.services.ai.azure.com/openai/v1
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=phi-4-mini-reasoning
AZURE_OPENAI_API_VERSION=2024-02-01

# Azure AI Project endpoint (required for MCP web search and competitive agent)
AZURE_PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project-name

# Pre-deployed Competitive agent ID
AZURE_EXISTING_AGENT_ID=competitive-landscape-researcher:1
```

*Note: Never commit your `.env` file or credentials to source control. A default `.gitignore` is configured to prevent this.*

---

## 3. Running the CLI Agent

The CLI is registered as a console script. You can run the command `logos` directly in your terminal once your virtual environment is active.

### Interactive Mode (REPL)
Guides you through initial profile setup, memory summaries, and interactive conversations:
```bash
logos
```

### Single-Shot Query
Execute a search and report generation request directly without entering the interactive shell:
```bash
logos -q "What are the top 3 investment risks in the Indian EV market?"
```

### Local Emulation Fallback Mode
Bypass A2A connections and cloud agent orchestration. Runs the pipeline using local LLM models:
```bash
logos --no-a2a -q "Research recent developments in fusion energy."
```

### Skip Clarifying Questions
Disable the Human-in-the-Loop question prompts and run the query directly:
```bash
logos --no-hitl -q "Summarize the current state of NLP."
```

### Connection Diagnostics
Verify connection endpoints and API credentials against the Azure OpenAI deployment:
```bash
logos --model-test
```

---

## 4. Running the FastAPI Local Server

You can run the FastAPI web server to expose REST endpoints for programmatic integrations.

### Start the Server
```bash
uvicorn main:app --reload --port 8000
```

Once started, the API is available locally:
*   **API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Alternate Docs (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
*   **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

### Available Web Endpoints

*   `POST /ask`: Runs the 6-agent research pipeline sequentially (Planner → Researcher → Analyst → Writer).
*   `POST /competitive`: Directly calls the pre-deployed competitive intelligence agent hosted on Azure AI Foundry.
*   `POST /research`: The flagship hackathon endpoint. Triggers the local 6-agent pipeline and the competitive agent in parallel, returning a combined report.

---

## 5. Running the Test Suite

The test suite validates agent logic, schemas, and pipeline orchestration using mock clients.

Run all tests using pytest:
```bash
pytest tests/test_agents.py -v
```
To calculate test coverage:
```bash
pytest --cov=src --cov=logos tests/
```
