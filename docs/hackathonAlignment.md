# Hackathon Alignment and Requirements Mapping

This document maps the design, architecture, and implementation of the LOGOS Autonomous Research Intelligence Agent to the official requirements of the **Microsoft Agent League Hackathon: Battle #2 - Reasoning Agents with Microsoft Foundry**.

---

## 1. Challenge & Scenario Alignment

LOGOS implements a multi-agent system designed for **Enterprise Intelligence and Research Automation**. The scenario addresses the need for organizations to conduct deep, context-aware competitive research, scanner trends, and generate comprehensive research reports using reasoning models.

The system mirrors the structure of a professional research division by dividing responsibilities among six agents, ensuring specialization, deep analytical decomposition, and high-fidelity output.

---

## 2. Microsoft IQ Layer Integration

The hackathon requires integrating at least one Microsoft IQ intelligence layer. LOGOS integrates concepts and patterns representing all three layers, grounded in local databases and cloud APIs:

### Work IQ
*   **Definition**: Understanding the user's work context, collaboration patterns, and organizational focus.
*   **LOGOS Implementation**:
    *   Implemented via the persistent SQLite profile storage (`~/.logos/memory.db`).
    *   During initialization, LOGOS records the user's name, role, organization, research domain, and preferred depth of analysis.
    *   These signals are combined with real-time feedback gathered during the Human-in-the-Loop (HITL) phase (clarifying focus areas and timeline constraints).
    *   The resulting context is injected into agent prompts, ensuring the generated report aligns with the user's organizational role.

### Foundry IQ
*   **Definition**: Grounding agents in external knowledge bases, web search, and data sources with proper citations.
*   **LOGOS Implementation**:
    *   Integrates search capabilities using the Microsoft Agent Framework and custom Model Context Protocol (MCP) search toolboxes.
    *   The Researcher Agent fetches live search indices, and the Industry News Scanner targets recent press.
    *   The system enforces reference-aware generation: the Writer Agent lists actual source links and URLs in a dedicated "Resources & References" section, verifying the output is grounded.

### Fabric IQ
*   **Definition**: A semantic foundation mapping structured relationships between business entities, patterns, and historical signals.
*   **LOGOS Implementation**:
    *   Implemented through the semantic schema in the SQLite database.
    *   LOGOS extracts and correlates research sessions, tracking entity metrics (such as mention counts for frequently researched companies or technologies).
    *   Users can bookmark key analytical insights (`insights` table), linking them back to specific search sessions.
    *   This semantic memory builds an ontology of the user's research focus over time, which is queried to enrich subsequent prompts.

---

## 3. Data Hygiene and Synthetic Data Compliance

In strict compliance with the hackathon rules regarding security and privacy, LOGOS enforces the following guardrails:

*   **No PII or Customer Data**: The system is designed to analyze general industry trends and public competitive landscapes. No customer records, personal data, or private credentials are sent to the model endpoints.
*   **Synthetic/Demo Seeding**: When executing first-time setup or mock runs, the database populates with synthetic profiles and generic search queries (e.g., standard tech sectors).
*   **Credentials Separation**: Credentials, API keys, and endpoints are kept entirely out of source control. They are loaded at runtime from a local `.env` file, which is blacklisted in `.gitignore`.

---

## 4. Production-Ready Deployment Story

LOGOS is built to transition from local prototype to cloud-scale deployment using **Hosted Agents in Foundry Agent Service**:

*   **Containerization**: The codebase includes a `Dockerfile` and `docker-compose.yml` configured to build a lightweight, production-ready container image running the FastAPI web server.
*   **Foundry Agent Service Compatibility**:
    *   The web server exposes endpoints (`/ask`, `/research`, `/competitive`) that allow other enterprise workflows to query the agent network.
    *   In a hosted cloud environment, the local SQLite database can be mapped to persistent storage volumes, preserving session memory.
    *   Managed Identities (Entra ID) are recommended to call downstream Azure OpenAI and search services, eliminating the need to package hardcoded secrets in the container.

---

## 5. Telemetry, Observability, and Evaluation

LOGOS integrates tools to evaluate system behavior and measure performance:

*   **Structured Logging**: Utilizes `structlog` to output JSON logs mapping agent transitions, execution states, and error handling.
*   **Confidence Metrics**: The Analyst and Writer agents compute confidence scores (representing data quality and source consistency) which are returned in the API responses and report metadata.
*   **Performance Profiling**: The orchestrator tracks elapsed execution times for each agent stage, assisting in performance optimization.
*   **Automated Verification**: The test suite in `tests/test_agents.py` verifies core agent logic and LangGraph orchestration paths using mock LLMs, providing a stable foundation for CI/CD pipelines.
