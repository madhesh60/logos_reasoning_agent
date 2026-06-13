# Agent Architecture and Character Specifications

This document outlines the multi-agent system architecture and design principles of the LOGOS Autonomous Research Intelligence Agent.

---

## 1. Multi-Agent Character Design

LOGOS divides strategic research and competitive intelligence into six distinct analytical tasks. Each task is handled by a specialized agent character configured with appropriate model quotas and targeted instructions.

### 1.1. Planner Agent (`planner-agent` | Version 12)
*   **Persona**: Senior Research Coordinator / Methodical Planner.
*   **Role**: Decomposes the high-level business query into discrete, sequential sub-tasks. It estimates execution times and defines required tools.
*   **Model Recommendation**: `GPT o4 Mini`.
*   **Inputs**: User's raw research query and personalized user profile context.
*   **Process**: Evaluates the scope of the request, identifies critical topics of investigation, estimates execution durations, and specifies tools.
*   **Outputs**: A structured research plan containing a task execution path.

### 1.2. Researcher Agent (`researcher-agent` | Version 12)
*   **Persona**: Data Gathering Specialist / Web Fact Finder.
*   **Role**: Gathers grounded factual intelligence from the web.
*   **Model Recommendation**: `GPT o4 Mini`.
*   **Inputs**: Original query, user context, and the planner's structured research plan.
*   **Process**: Performs search operations using Model Context Protocol (MCP) search toolboxes to query live search indexes. It parses result summaries and extracts direct source URLs.
*   **Outputs**: Grounded web research findings containing citations and verified links.

### 1.3. Industry News Scanner (`industry-news-trend-scanner` | Version 5)
*   **Persona**: Real-Time Trend Analyst / News Reporter.
*   **Role**: Focuses on breaking developments, press releases, and near-term market trends.
*   **Model Recommendation**: `GPT-4.1 Mini`.
*   **Inputs**: Original query, user context, and accumulated web research findings.
*   **Process**: Targets news engines and recent industry releases focusing on the last 3-6 months to capture market shifts.
*   **Outputs**: A chronological log of recent news headlines, trend signals, and press summaries with specific publication sources.

### 1.4. Competitive Landscape Researcher (`competitive-landscape-researcher` | Version 2)
*   **Persona**: Competitive Intelligence Officer / SWOT Specialist.
*   **Role**: Maps industry competitors, assesses market share, and identifies strategic white-spaces.
*   **Model Recommendation**: `GPT-4.1 Mini`.
*   **Inputs**: Original query, user context, accumulated research findings, and trend signals.
*   **Process**: Identifies major competitors, their market share, core technologies, and product positioning.
*   **Outputs**: Competitor profiles, SWOT findings, and strategic positioning summaries.

### 1.5. Analyst Agent (`analyst-agent` | Version 4)
*   **Persona**: Risk Officer / Qualitative Synthesis Expert.
*   **Role**: Synthesizes facts, detects underlying patterns, and constructs risk assessments.
*   **Model Recommendation**: `GPT-4.1 Mini`.
*   **Inputs**: Accumulated research findings, news logs, and competitive profiles.
*   **Process**: Group findings into qualitative categories, evaluates the strength of evidence (Strong, Medium, Weak), detects market patterns, and computes risk scores based on probability-impact matrices.
*   **Outputs**: Key findings, risk assessments with mitigation strategies, and an overall confidence score.

### 1.6. Writer Agent (`writer-agent` | Version 4)
*   **Persona**: Executive Report Writer / Strategy Editor.
*   **Role**: Composes the final formal report using a standard corporate strategy template.
*   **Model Recommendation**: `GPT-4.1`.
*   **Inputs**: Structured key findings, risk registers, and resource links.
*   **Process**: Compiles all analytical results and formats the final markdown content.
*   **Outputs**: A generated report object containing metadata, executive summaries, structured sections, conclusions, and citation reference lists.

---

## 2. Context Grounding and Prompt Structure

To deliver personalized and contextually accurate research, LOGOS utilizes a multi-layered prompt injection protocol:

```
+-------------------------------------------------------------+
| System Instructions / System Prompt                         |
+-------------------------------------------------------------+
| === RESEARCH CONTEXT FROM MEMORY ===                        |
| Researcher: <Name> (<Role>)                                 |
| Organization: <Organization>                                |
| Primary Domain: <Domain>                                    |
| Recent research topics, tracked entities, and bookmarks... |
| === END CONTEXT ===                                         |
+-------------------------------------------------------------+
| === USER CLARIFICATIONS ===                                 |
| Q: [Clarifying Question 1]                                   |
| A: [User's Answer 1]                                        |
| Q: [Clarifying Question 2]                                   |
| A: [User's Answer 2]                                        |
| === END CLARIFICATIONS ===                                  |
+-------------------------------------------------------------+
| Task Context (Accumulated Stage Outputs)                    |
+-------------------------------------------------------------+
| User's Current Research Query                               |
+-------------------------------------------------------------+
```

1.  **System Instructions**: Injects the agent persona, format requirements, and tool instructions.
2.  **Research Context from Memory**: Derived from SQLite database lookups. Grounded in the user's saved profile and historical search behavior.
3.  **User Clarifications**: Gathered via the Human-in-the-Loop (HITL) prompt phase before the pipeline runs, answering query-specific clarifying questions.
4.  **Task Context**: Accumulated outputs passed from predecessor agents in the sequential pipeline.

---

## 3. Short-Term Context and Long-Term Memory (SQLite Schema)

LOGOS utilizes a persistent local SQLite database (`memory.db`) stored at `~/.logos/memory.db`. This database serves as the foundation for the user's short-term context and long-term memory:

```
                      +-------------------+
                      |   user_profile    |
                      +-------------------+
                      | key (PK)          |
                      | value             |
                      | updated_at        |
                      +---------+---------+
                                |
                                |
                      +---------v---------+
                      |      queries      |
                      +---------+---------+
                      | id (PK)           |
                      | query             |
                      | summary           |
                      | topics (JSON)     |
                      | entities (JSON)   |
                      | path_used         |
                      | created_at        |
                      +----+---------+----+
                           |         |
            +--------------+         +--------------+
            |                                       |
  +---------v---------+                   +---------v---------+
  | tracked_entities  |                   |     insights      |
  +-------------------+                   +-------------------+
  | id (PK)           |                   | id (PK)           |
  | name (UNIQUE)     |                   | query_id (FK)     |
  | entity_type       |                   | text              |
  | mention_count     |                   | created_at        |
  | last_seen         |                   +-------------------+
  +-------------------+
```

### 3.1. User Profile Table (`user_profile`)
Tracks user preferences and organizational details:
*   `key`: Key name (e.g., `name`, `role`, `organization`, `domain`, `depth_preference`).
*   `value`: Field value.
*   `updated_at`: ISO timestamp of the last update.

### 3.2. Query History Table (`queries`)
Logs historical search sessions and reports:
*   `id`: Primary key (autoincrement).
*   `query`: Raw user query.
*   `summary`: A short excerpt or summary of the executive summary.
*   `topics`: JSON list of extracted topics.
*   `entities`: JSON list of tracked entities mentioned.
*   `path_used`: Orchestration path (e.g., `foundry_6agent` or `local_fallback`).
*   `created_at`: ISO timestamp.

### 3.3. Tracked Entities Table (`tracked_entities`)
Calculates entity mention frequencies over time:
*   `id`: Primary key (autoincrement).
*   `name`: Name of the company, competitor, or technology (unique).
*   `entity_type`: Category classification.
*   `mention_count`: Aggregated count of entity mentions across all sessions.
*   `last_seen`: Timestamp of the most recent query mentioning this entity.

### 3.4. Insights Bookmarks Table (`insights`)
Allows manual bookmarking of key strategic findings:
*   `id`: Primary key (autoincrement).
*   `query_id`: Foreign key referencing `queries(id)`.
*   `text`: Bookmarked finding text.
*   `created_at`: ISO timestamp.

---

## 4. End-to-End Orchestration Workflow

When a query is executed, the orchestrator triggers the following sequential pipeline:

```
[Step 1: Init]              Load environment config and open local SQLite connection.
                                   │
[Step 2: Profile context]   Query SQLite `user_profile` to build memory context string.
                                   │
[Step 3: HITL Verification] Run the questioner agent to generate query-specific questions.
                            Collect user answers and compile the user clarifications block.
                                   │
[Step 4: Pipeline Execution]
   ├── Planner:             Decompose query -> plan.
   ├── Researcher:          Call MCP (Tavily/Bing) tools -> extract URLs.
   ├── Trend-Scanner:       News search -> extract near-term signals.
   ├── Competitive-Intel:   Competitor profiles -> positioning analysis.
   ├── Analyst:             Perform qualitative analysis -> compile risk matrix.
   └── Writer:              Draft formal report -> parse into GeneratedReport object.
                                   │
[Step 5: Output Sync]       Render report sections to console and save report.md file.
                                   │
[Step 6: Memory Update]     Extract topics and entities. Upsert tracked entities table.
                            Offer user option to bookmark specific findings in insights table.
```

---

## 5. Agent Skills and Capabilities

To control tool-calling permissions and logic, agent capabilities are guided by **Model Context Protocol (MCP)** tool declarations.

*   **Custom Prompting Templates (`Skill.md`)**: Agents refer to structured prompt instructions to determine when to call tools (e.g., prioritizing `bing_web_search` or `tavily_search` when resolving current-event questions).
*   **Tool Binding**: The Researcher and News Scanner agents bind the `bing_web_search` tool through HTTP JSON-RPC to the MCP server.
*   **Stateful Run Validation**: The Game Master and Competitive Landscape agents use persistent assistant structures with access to file storage resources and code execution dependencies where appropriate.
