# Microsoft Azure AI Foundry Usage and SDK Integration

This document outlines the architectural decisions and implementation patterns for integrating Microsoft Azure AI Foundry services, SDKs, and container deployment structures within the LOGOS Multi-Agent system.

---

## 1. Project Client Connection and Authentication

LOGOS connects to Azure AI Foundry resources using the **Azure AI Projects SDK** (`azure-ai-projects`). To align with enterprise security guidelines, the application avoids hardcoding access keys in the source files, relying on keyless authentication where possible.

### 1.1. Client Initialization
Connections are established using the `AIProjectClient` utility:
```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

client = AIProjectClient(
    endpoint=AZURE_PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(exclude_interactive_browser_credential=True)
)
```

### 1.2. Authentication Methods
*   **Local Development**: Evaluates active environment variables, developer credentials, or active Azure CLI logins (`az login`).
*   **Production Cloud Environments**: Resolves using a **Managed Identity (Entra ID)** assigned to the hosted agent service, ensuring secure connection to model deployments, search indexes, and vault assets.

---

## 2. API Selection: Responses API vs. Agents SDK

LOGOS adopts a hybrid integration approach based on the specific capabilities and execution patterns of each agent stage:

### 2.1. Responses API (Visual Workflow Integration)
The main multi-agent execution pipeline (Planner, Researcher, Industry News Scanner, Competitive Landscape, Analyst, and Writer) is coordinated using the **OpenAI Responses API** via the Foundry project endpoint:
*   **Rationale**: The Responses API allows calling cloud-configured agents by their registered name and version without the overhead of stateful thread tracking.
*   **Implementation**:
    ```python
    oc = client.get_openai_client()
    resp = oc.responses.create(
        input=[{"role": "user", "content": prompt}],
        extra_body={
            "agent_reference": {
                "name": agent_name,
                "version": agent_version,
                "type": "agent_reference"
            }
        }
    )
    return resp.output_text
    ```
*   **Benefits**: Stateless execution, low request latency, and direct compatibility with cloud-managed agent references.

### 2.2. Agents Thread and Run API (Stateful Conversational Flows)
For specialized competitive analysis requests (`POST /competitive`), the system utilizes the **Azure AI Agents SDK** Thread and Run interfaces:
*   **Rationale**: This agent is pre-deployed as a standalone assistant. Managing conversational state in the cloud via stateful Thread APIs is ideal for multi-turn discussions.
*   **Implementation**:
    ```python
    # 1. Initialize Thread
    thread = client.agents.create_thread()
    
    # 2. Post User Query Message
    client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=query,
    )
    
    # 3. Create and Process the Run
    run = client.agents.create_and_process_run(
        thread_id=thread.id,
        agent_id=agent_name,
    )
    
    # 4. Fetch Response Message Payload
    messages = client.agents.list_messages(thread_id=thread.id)
    ```

---

## 3. Reasoning Model Optimization

When calling reasoning models, responses include intermediate reasoning traces enclosed within `<think>...</think>` tags. To prevent these traces from corrupting downstream JSON parsing, LOGOS implements a custom parsing utility (`clean_and_parse_json` in `src/utils/config.py`):

1.  **Tag Extraction**: Scans response text using regular expressions to remove `<think>...</think>` blocks (handling both complete and unclosed blocks).
2.  **Markdown Cleaning**: Identifies and removes enclosing Markdown code blocks (e.g., ` ```json ... ``` `).
3.  **JSON Outermost Parsing**: Extracts the outermost JSON object (`{...}`) or array (`[...]`) bounds.
4.  **Parsing Recovery Loop**: If standard library `json.loads` fails, it applies a parsing recovery pass using the `json-repair` library to correct syntax errors, backslash escape sequences, and trailing commas.

---

## 4. Containerized Hosted Agent Service Deployment

LOGOS is ready to be packaged and deployed to the stateful **Hosted Agent Service** on Azure AI Foundry. The deployment uses the pre-configured Azure Container Registry named `reasoningagentregistry`.

### 4.1. Packaging and Docker Configurations
The `Dockerfile` in the root of the project packages the FastAPI REST server:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install -e .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 4.2. ACR Build and Push Commands
Execute the following commands to push the image to `reasoningagentregistry`:
```bash
# Authenticate against your Azure Container Registry
az acr login --name reasoningagentregistry

# Tag and build the local container image
docker build -t reasoningagentregistry.azurecr.io/logos-research-agent:latest .

# Push image to registry
docker push reasoningagentregistry.azurecr.io/logos-research-agent:latest
```

### 4.3. Cloud Provisioning and State Mapping
Once pushed:
1.  **Service Pull**: The Hosted Agent Service pulls the container image from `reasoningagentregistry.azurecr.io`.
2.  **Identities**: Attach an Entra ID Managed Identity to the provisioned container service to authorize calls to downstream model endpoints and MCP servers.
3.  **Persistent Volume Mounts**: To preserve session memory across container recycles, map the SQLite store file path (`~/.logos/memory.db`) to a persistent storage volume (e.g., Azure File Share).
4.  **Telemetry & Logging**: The FastAPI server logs structured JSON via `structlog`, which is piped directly to Azure Monitor and Application Insights.
