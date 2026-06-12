# Microsoft Azure AI Foundry Usage and SDK Integration

This document outlines the design decisions and technical implementations for leveraging Microsoft Azure AI Foundry services, endpoints, and SDK capabilities within the LOGOS system.

---

## 1. Project Client Initialization

LOGOS connects to Azure AI Foundry using the **Azure AI Projects SDK** (`azure-ai-projects`). The client is initialized using environment parameters that connect to the project's workspace endpoint.

*   **Code Reference**: In `src/orchestration/research_workflow.py` and `main.py`, connections are established using:
    ```python
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential

    client = AIProjectClient(
        endpoint=AZURE_PROJECT_ENDPOINT,
        credential=DefaultAzureCredential()
    )
    ```
*   **Security Compliance**: Local development utilizes the `DefaultAzureCredential` which checks active environmental tokens, CLI logins (`az login`), or managed credentials. No access keys are hardcoded in the codebase, in alignment with Microsoft's security guidelines.

---

## 2. API Selection: Responses API vs. Agents SDK

LOGOS adopts a hybrid integration approach based on the specific capabilities and performance requirements of each agent stage:

### Responses API (Main Pipeline)
The main 6-agent research pipeline (Planner, Researcher, Industry News, Competitive, Analyst, and Writer) is orchestrated using the **OpenAI Responses API** via the Foundry project endpoint.
*   **Rationale**: The Responses API is compatible with visual workflow-configured agents built inside the Azure AI Foundry Portal. Using this client allows the system to invoke agents by their registered name and version without managing stateful threads for each hop.
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
*   **Benefits**: Minimal request overhead, low execution latency, and direct compatibility with cloud-managed agent references.

### Agents Thread and Run API (Competitive Landscape Endpoint)
For the specialized competitive-landscape-researcher endpoint (`POST /competitive`), the system utilizes the stateful **Azure AI Agents SDK** Thread and Run interfaces.
*   **Rationale**: This agent is pre-deployed as a standalone assistant. The stateful Thread API allows conversational persistence, separating query context into discrete threads managed in the cloud.
*   **Implementation**:
    ```python
    # 1. Initialize thread
    thread = client.agents.create_thread()
    
    # 2. Post user message
    client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=query,
    )
    
    # 3. Create and process the run
    run = client.agents.create_and_process_run(
        thread_id=thread.id,
        agent_id=agent_name,
    )
    
    # 4. Fetch response messages
    messages = client.agents.list_messages(thread_id=thread.id)
    ```

---

## 3. Model Optimization: Phi-4-mini-reasoning

LOGOS is configured to use reasoning models (e.g., `phi-4-mini-reasoning`) deployed on Azure AI Foundry:

*   **Reasoning Block Parsing**: Reasoning models output thoughts inside `<think>...</think>` tags before returning their final text. These blocks can consume thousands of tokens, which can interfere with downstream JSON parsing.
*   **Clean and Repair Engine**: A custom utility `clean_and_parse_json` in `src/utils/config.py` is implemented to handle these responses:
    1.  Strips `<think>...</think>` tags using regular expressions (handling both complete and unclosed blocks).
    2.  Removes Markdown code blocks (e.g., ` ```json ... ``` `).
    3.  Extracts the outermost JSON object (`{...}`) or array (`[...]`).
    4.  Corrects backslash escape sequences and trailing commas.
    5.  Applies a parsing recovery loop using the `json-repair` library if the JSON is truncated.

---

## 4. Cloud Deployment (Hosted Agent Service)

To deploy the LOGOS FastAPI backend and orchestrator to the **Azure AI Foundry Hosted Agent Service**, the codebase is prepared with:

*   **Dockerfile**: Uses a slim Python 3.10 base image, installs system requirements, copies source folders (`src/`, `logos/`), and launches the FastAPI application using `uvicorn`.
*   **State Persistence**: The local SQLite database can be mapped to an Azure File Share or persistent volume mount within the Azure Container Registry deployment context to maintain long-term memory across sessions.
*   **Observability Integration**: JSON log formats are standard (`LOG_FORMAT=json`), making it compatible with Azure Monitor, Application Insights, and log collection facilities in Azure Container Instances.
