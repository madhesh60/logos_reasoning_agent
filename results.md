when i run the commands given by you i get these resulst or errors if its an error fix it

1)PS C:\Users\RAJ\Desktop\research-to-report-multi-agent> python run_agent.py --model-test        

════════════════════════════════════════════════════════════════════════                        
  Azure AI Foundry — Model Connection Test
════════════════════════════════════════════════════════════════════════                        
[10:57:52] 🔌 Connecting to endpoint:  https://reasoning-agent-hack2-resource.services.ai.azure.com/openai/v1
[10:57:52] 🤖 Using deployment   :  phi-4-mini-reasoning
[10:57:54] 📤 Sending test prompt …

── Model Response ──────────────────────────────────
<think>

Okay, I need to figure out the top three investment risks in the Indian EV market. Let me start by breaking down what I know about the EV market in India. First, India has been rapidly increasing its EV adoption, driven by government policies like FAME (Facilitating Mission Assets to Generate Equity) and targets for zero-emission vehicles by 2030. But despite this growth, there are risks involved.

First risk: Supply chain issues. EVs rely heavily on batteries, especially lithium-ion ones. China is a major player in battery production, and any disruptions there could affect India. Plus, raw material scarcity like lithium, cobalt, and nickel could drive up costs. Have I seen reports about supply chain bottlenecks in the past year? Yes, maybe due to COVID or geopolitical tensions.

Second, infrastructure.Robber electric vehicles might be a problem, but more importantly, charging infrastructure. If investors don't see enough chargers, it could limit EV usage. Also, India needs more charging stations, which requires investment. Maybe that's a risk for companies relying on high adoption rates.

Third, government policy changes. Policies can shift with political climates. For example, if a future government decides to roll back subsidies or change tax incentives, that could impact profitability. Also, there's the import duty on EVs; India has reduced it, but maybe further changes are possible. Regulatory risks are always a factor in emerging markets.

Wait, any other risks? Maybe competition. Local vs. foreign companies. There's tension about Chinese EV investments, so geopolitical Risks. Also, financing risks since EVs are more expensive, affecting consumer affordability. Secondly, maybe technology risks related to battery advancements. If a new battery tech emerges, companies with current tech might become obsolete.

But the top three are supply chain, infrastructure, and government policy. Let me check if these are supported by data. Supply chain was a big issue in 2023-24 with delays. Infrastructure lag compared to China. Government announcements have been proactive but also unpredictable. Yeah, that seems right. So the three risks are:

1. Supply chain vulnerabilities (batteries, raw materials)
2. Charging infrastructure development
3. Policy and regulatory changes

Alternatively, maybe consumer adoption risk due to higher upfront costs. But subsidies are helping, so maybe it's mitigated. Another angle: competition from established automakers entering the EV space. But I think the three I listed are the main ones. Let me confirm with examples. Tesla has been facing supply chain issues too. Local players like Tata Motors, Mahindra & Mahindra. So yes, the top three would be supply chain, infrastructure (both charging and manufacturing), and policy. Maybe I should prioritize them as 1, 2, 3. Alright, that seems solid.

</think>

**Step-by-Step Analysis:**

1. **Supply Chain Vulnerabilities**
   - **Key Factors**: Dependency on rare earth metals (lithium, nickel) and Chinese battery manufacturing.
   - **Evidence**: Global shortages, production delays (2023-24), and geopolitical tensions affecting Component Suppliers.
   - **Impact**: Cost volatility, production bottlenecks for companies like FCAC and MG Electronics.

2. **Charging Infrastructure Gaps**
   - **Key Factors**: Slow rollout of fast chargers, limited rural coverage.
   - **Evidence**: CEIC India reports show hesitancy in consumer adoption without reliable charging.
   - **Impact**: Operational delays for ride-hailing services (e.g., Ola, Uber) reliant on EVs. 

3. **Regulatory & Policy Uncertainty**
   - **Key Factors**: Ambiguity post-subsidy phases (FAME IV), geopolitical tensions over chip supplies.
   - **Evidence**: Sudden tax changes (e.g., EV import duties) and fluctuating incentives.      
   - **Impact**: Revenue instability for firms like HeroEV.

4. **Secondary Risks** (Competitor Advancements, Geopolitical Tensions)
   - Rising competition from local OEMs (Tata Motors) vs. restrictions on Chinese tech (e.g., Xuedong Hai Jinle controversy).

**Final Answer:**
The top 3 investment risks in the Indian EV market are:
- **Supply Chain Disruptions** (batteries/raw materials dependency).
- **Infrastructure Development Gaps
────────────────────────────────────────────────────
  ✓  Finish reason : length
  ✓  Total tokens  : 969
PS C:\Users\RAJ\Desktop\research-to-report-multi-agent> python quick_demo.py --only planner

────────────────────────────────────────────────────────────────
  Phi-4 Reasoning Multi-Agent — Quick Demo & Test Suite
────────────────────────────────────────────────────────────────
  →  Python  : 3.10.11
  →  Root    : C:\Users\RAJ\Desktop\research-to-report-multi-agent
  →  Time    : 2026-06-07 10:58:32

────────────────────────────────────────────────────────────────
  TEST 3 — Planner Agent (Task Decomposition)
────────────────────────────────────────────────────────────────
2026-06-07 10:58:41 [info     ] environment_loaded             env_file=.env
2026-06-07 10:58:41 [info     ] instantiating_chat_openai_for_foundry base_url=https://reasoning-agent-hack2-resource.services.ai.azure.com/openai/v1 model=phi-4-mini-reasoning temperature=0.3        
  →  Query: What are the main risks of investing in AI startups in India?
2026-06-07 10:58:41 [info     ] planner_decompose_task_start   query='What are the main risks of investing in AI startups in India?'
2026-06-07 11:00:10 [error    ] planner_json_parse_error       error='1 validation error for SubTask\nestimated_duration_seconds\n  Input should be a valid integer, got a number with a fractional part [type=int_from_float, input_value=1.5, input_type=float]\n    For further information visit https://errors.pydantic.dev/2.10/v/int_from_float' response="<think>\n\nOkay, I need to create a JSON plan for decomposing the query about the main risks of investing in AI startups in India. Let me start by understanding the user's intent. They want to know the "
  ✗  Planner error: Failed to parse planner response as JSON: 1 validation error for SubTask
estimated_duration_seconds
  Input should be a valid integer, got a number with a fractional part [type=int_from_float, input_value=1.5, input_type=float]
    For further information visit https://errors.pydantic.dev/2.10/v/int_from_float
Traceback (most recent call last):
  File "C:\Users\RAJ\Desktop\research-to-report-multi-agent\src\agents\planner.py", line 206, in decompose_task
    tasks = [SubTask(**task) for task in plan_data["tasks"]]
  File "C:\Users\RAJ\Desktop\research-to-report-multi-agent\src\agents\planner.py", line 206, in <listcomp>
    tasks = [SubTask(**task) for task in plan_data["tasks"]]
  File "C:\Users\RAJ\AppData\Local\Programs\Python\Python310\lib\site-packages\pydantic\main.py", line 214, in __init__
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
    For further information visit https://errors.pydantic.dev/2.10/v/int_from_float

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\RAJ\Desktop\research-to-report-multi-agent\quick_demo.py", line 106, in test_planner
    plan = await planner.decompose_task(q)
  File "C:\Users\RAJ\Desktop\research-to-report-multi-agent\src\agents\planner.py", line 232, in decompose_task
    raise ValueError(f"Failed to parse planner response as JSON: {e}")
ValueError: Failed to parse planner response as JSON: 1 validation error for SubTask
estimated_duration_seconds
  Input should be a valid integer, got a number with a fractional part [type=int_from_float, input_value=1.5, input_type=float]
    For further information visit https://errors.pydantic.dev/2.10/v/int_from_float

────────────────────────────────────────────────────────────────
  SUMMARY
────────────────────────────────────────────────────────────────
  ✗  planner      FAIL
Traceback (most recent call last):
  File "C:\Users\RAJ\Desktop\research-to-report-multi-agent\quick_demo.py", line 314, in <module>
    asyncio.run(main())
  File "C:\Users\RAJ\AppData\Local\Programs\Python\Python310\lib\asyncio\runners.py", line 44, in run
    return loop.run_until_complete(main)
  File "C:\Users\RAJ\AppData\Local\Programs\Python\Python310\lib\asyncio\base_events.py", line 649, in run_until_complete 
    return future.result()
  File "C:\Users\RAJ\Desktop\research-to-report-multi-agent\quick_demo.py", line 309, in main
    print(f"\n  {G if passed==total else Y}{BOLD}{passed}/{total} tests passed{R}\n")
NameError: name 'BOLD' is not defined
PS C:\Users\RAJ\Desktop\research-to-report-multi-agent>

2)PS C:\Users\RAJ\Desktop\research-to-report-multi-agent> python quick_demo.py --only researcher

────────────────────────────────────────────────────────────────
  Phi-4 Reasoning Multi-Agent — Quick Demo & Test Suite
────────────────────────────────────────────────────────────────
  →  Python  : 3.10.11
  →  Root    : C:\Users\RAJ\Desktop\research-to-report-multi-agent
  →  Time    : 2026-06-07 10:59:51

────────────────────────────────────────────────────────────────
  TEST 4 — Researcher Agent (Search + Rank)
────────────────────────────────────────────────────────────────
2026-06-07 10:59:58 [info     ] environment_loaded             env_file=.env
2026-06-07 10:59:58 [info     ] instantiating_chat_openai_for_foundry base_url=https://reasoning-agent-hack2-resource.services.ai.azure.com/openai/v1 model=phi-4-mini-reasoning temperature=0.4
2026-06-07 11:00:00 [info     ] mcp_web_search_initialized     server_url='https://reasoning-agent-hack2-resource.services.ai.azure.com/api/projects/reasoning-agent-hack2/toolboxes/reasoning-agent-web-search/mcp?api-version=v1' use_azure_toolbox=True
  →  Query: Top 3 investment risks in Indian EV market
2026-06-07 11:00:00 [info     ] researcher_search_start        max_results=8 query='Top 3 investment risks in Indian EV market'
2026-06-07 11:00:20 [info     ] azure_toolbox_search_start     project_endpoint=https://reasoning-agent-hack2-resource.services.ai.azure.com/api/projects/reasoning-agent-hack2 query=IndiaEVregulatorychallenges2023 toolbox=reasoning-agent-web-search
2026-06-07 11:00:20 [error    ] azure_toolbox_search_error_falling_back error="No module named 'langchain_azure_ai'" query=IndiaEVregulatorychallenges2023
2026-06-07 11:00:20 [info     ] azure_toolbox_search_start     project_endpoint=https://reasoning-agent-hack2-resource.services.ai.azure.com/api/projects/reasoning-agent-hack2 query=BatterySupplyChainRisksIndiaEV toolbox=reasoning-agent-web-search
2026-06-07 11:00:20 [error    ] azure_toolbox_search_error_falling_back error="No module named 'langchain_azure_ai'" query=BatterySupplyChainRisksIndiaEV
2026-06-07 11:00:20 [info     ] azure_toolbox_search_start     project_endpoint=https://reasoning-agent-hack2-resource.services.ai.azure.com/api/projects/reasoning-agent-hack2 query=EVMarketAdoptionBarriersIndia toolbox=reasoning-agent-web-search
2026-06-07 11:00:20 [error    ] azure_toolbox_search_error_falling_back error="No module named 'langchain_azure_ai'" query=EVMarketAdoptionBarriersIndia
2026-06-07 11:00:20 [info     ] azure_toolbox_search_start     project_endpoint=https://reasoning-agent-hack2-resource.ser2026-06-07 11:00:20 [info     ] azure_toolbox_search_start     project_endpoint=https://reasoning-agent-hack2-resource.services.ai.azure.com/api/projects/reasoning-agent-hack2 query=EVFinancingHurdlesIndia toolbox=reasoning-agent-web-search    
2026-06-07 11:00:20 [error    ] azure_toolbox_search_error_falling_back error="No module named 'langchain_azure_ai'" query=EVFinancingHurdlesIndia
2026-06-07 11:00:20 [info     ] researcher_search_complete     high_confidence_count=5 query='Top 3 investment risks in Indian EV market' total_results=5
  ✓  Total sources       : 5
  ✓  High-confidence     : 5
  ✓  Medium-confidence   : 0
  ✓  Confidence score    : 1.00

  Top sources:
    • Indiaevregulatorychallenges2023 - Reuters Analysis  [Reuters]
    • Batterysupplychainrisksindiaev - Reuters Analysis  [Reuters]
    • Evmarketadoptionbarriersindia - Reuters Analysis  [Reuters]

────────────────────────────────────────────────────────────────
  SUMMARY
────────────────────────────────────────────────────────────────
  ✓  researcher   PASS
Traceback (most recent call last):
  File "C:\Users\RAJ\Desktop\research-to-report-multi-agent\quick_demo.py", line 314, in <module>
    asyncio.run(main())
  File "C:\Users\RAJ\AppData\Local\Programs\Python\Python310\lib\asyncio\runners.py", line 44, in run
    return loop.run_until_complete(main)
2026-06-07 11:00:20 [info     ] azure_toolbox_search_start     project_endpoint=https://reasoning-agent-hack2-resource.services.ai.azure.com/api/projects/reasoning-agent-hack2 query=EVFinancingHurdlesIndia toolbox=reasoning-agent-web-search    
2026-06-07 11:00:20 [error    ] azure_toolbox_search_error_falling_back error="No module named 'langchain_azure_ai'" query=EVFinancingHurdlesIndia
2026-06-07 11:00:20 [info     ] researcher_search_complete     high_confidence_count=5 query='Top 3 investment risks in Indian EV market' total_results=5
  ✓  Total sources       : 5
  ✓  High-confidence     : 5
  ✓  Medium-confidence   : 0
  ✓  Confidence score    : 1.00

  Top sources:
    • Indiaevregulatorychallenges2023 - Reuters Analysis  [Reuters]
    • Batterysupplychainrisksindiaev - Reuters Analysis  [Reuters]
    • Evmarketadoptionbarriersindia - Reuters Analysis  [Reuters]

────────────────────────────────────────────────────────────────
  SUMMARY
────────────────────────────────────────────────────────────────
  ✓  researcher   PASS
Traceback (most recent call last):
  File "C:\Users\RAJ\Desktop\research-to-report-multi-agent\quick_demo.py", line 314, in <module>
    asyncio.run(main())
  File "C:\Users\RAJ\AppData\Local\Programs\Python\Python310\lib\asyncio\runners.py", line 44, in run
    return loop.run_until_complete(main)
  File "C:\Users\RAJ\AppData\Local\Programs\Python\Python310\lib\asyncio\base_events.py", line 649, in run_until_complete 
  ✓  Confidence score    : 1.00

  Top sources:
    • Indiaevregulatorychallenges2023 - Reuters Analysis  [Reuters]
    • Batterysupplychainrisksindiaev - Reuters Analysis  [Reuters]
    • Evmarketadoptionbarriersindia - Reuters Analysis  [Reuters]

────────────────────────────────────────────────────────────────
  SUMMARY
────────────────────────────────────────────────────────────────
  ✓  researcher   PASS
Traceback (most recent call last):
  File "C:\Users\RAJ\Desktop\research-to-report-multi-agent\quick_demo.py", line 314, in <module>
    asyncio.run(main())
  File "C:\Users\RAJ\AppData\Local\Programs\Python\Python310\lib\asyncio\runners.py", line 44, in run
    return loop.run_until_complete(main)
  File "C:\Users\RAJ\Desktop\research-to-report-multi-agent\quick_demo.py", line 314, in <module>
    asyncio.run(main())
  File "C:\Users\RAJ\AppData\Local\Programs\Python\Python310\lib\asyncio\runners.py", line 44, in run
    return loop.run_until_complete(main)
    return loop.run_until_complete(main)
  File "C:\Users\RAJ\AppData\Local\Programs\Python\Python310\lib\asyncio\base_events.py", line 649, in run_until_complete 
    return future.result()
  File "C:\Users\RAJ\Desktop\research-to-report-multi-agent\quick_demo.py", line 309, in main
    print(f"\n  {G if passed==total else Y}{BOLD}{passed}/{total} tests passed{R}\n")
NameError: name 'BOLD' is not defined
PS C:\Users\RAJ\Desktop\research-to-report-multi-agent>

3)python quick_demo.py --only writer  

────────────────────────────────────────────────────────────────
  Phi-4 Reasoning Multi-Agent — Quick Demo & Test Suite
────────────────────────────────────────────────────────────────
  →  Python  : 3.10.11
  →  Root    : C:\Users\RAJ\Desktop\research-to-report-multi-agent
  →  Time    : 2026-06-07 11:00:09

────────────────────────────────────────────────────────────────
2026-06-07 11:00:16 [info     ] instantiating_chat_openai_for_foundry base_url=https://reasoning-agent-hack2-resource.services.ai.azure.com/openai/v1 model=phi-4-mini-reasoning temperature=0.4
  →  Generating report for: What are the top 3 investment risks in the Indian EV market?…
2026-06-07 11:00:17 [info     ] writer_generate_report_start   analysis_results_type=dict format=json query='What are the top 3 investment risks in the Indian '
2026-06-07 11:02:15 [info     ] writer_generate_report_complete recommendations=3 report_id=report_20260607_053215 sections=8
  ✓  Report ID    : report_20260607_053215
  ✓  Sections     : 8
  ✓  Conclusions  : 2
  ✓  Confidence   : 0.82

  Executive Summary (preview):
  The Indian EV market, driven by rapid government initiatives and a push for self-reliance, faces significant investment risks. Top risks include regulatory policy shifts, which threaten long-ter
m retu…                                                                                                                                                                                             
────────────────────────────────────────────────────────────────
  SUMMARY
────────────────────────────────────────────────────────────────
  ✓  writer       PASS
Traceback (most recent call last):
  File "C:\Users\RAJ\Desktop\research-to-report-multi-agent\quick_demo.py", line 314, in <module>
    asyncio.run(main())
  File "C:\Users\RAJ\AppData\Local\Programs\Python\Python310\lib\asyncio\runners.py", line 44, in run
    return loop.run_until_complete(main)
2026-06-07 11:00:16 [info     ] instantiating_chat_openai_for_foundry base_url=https://reasoning-agent-hack2-resource.services.ai.azure.com/openai/v1 model=phi-4-mini-reasoning temperature=0.4
  →  Generating report for: What are the top 3 investment risks in the Indian EV market?…
2026-06-07 11:00:17 [info     ] writer_generate_report_start   analysis_results_type=dict format=json query='What are the top 3 investment risks in the Indian '
2026-06-07 11:02:15 [info     ] writer_generate_report_complete recommendations=3 report_id=report_20260607_053215 sections=8
  ✓  Report ID    : report_20260607_053215

4)PS C:\Users\RAJ\Desktop\research-to-report-multi-agent> python run_agent.py                 

════════════════════════════════════════════════════════════════════════
  Research-to-Report — Interactive Mode  (Phi-4 Reasoning)
════════════════════════════════════════════════════════════════════════
  Type your research question and press Enter.
  Commands: exit | model-test | search-test

Query> explain why india is a diverse country

════════════════════════════════════════════════════════════════════════
  Research-to-Report Multi-Agent  ·  Phi-4 Reasoning
════════════════════════════════════════════════════════════════════════
  →  Query : explain why india is a diverse country
2026-06-07 11:01:29 [info     ] environment_loaded             env_file=.env
[11:01:29] 📋 PLANNER       — breaking query into sub-tasks …  
2026-06-07 11:01:30 [info     ] instantiating_chat_openai_for_foundry base_url=https://reasoning-agent-hack2-resource.services.ai.azure.com/openai/v1 model=phi-4-mini-reasoning temperature=0.3
2026-06-07 11:01:30 [info     ] instantiating_chat_openai_for_foundry base_url=https://reasoning-agent-hack2-resource.services.ai.azure.com/openai/v1 model=phi-4-mini-reasoning temperature=0.4
2026-06-07 11:01:30 [info     ] a2a_client_initialized         endpoint=http://localhost:8080/planner timeout=30
2026-06-07 11:01:30 [info     ] a2a_client_initialized         endpoint=http://localhost:8080/researcher timeout=30       
2026-06-07 11:01:30 [info     ] a2a_client_initialized         endpoint=http://localhost:8080/analyst timeout=30
2026-06-07 11:01:30 [info     ] a2a_client_initialized         endpoint=http://localhost:8080/writer timeout=30
2026-06-07 11:01:30 [info     ] a2a_clients_initialized        agents=['planner', 'researcher', 'analyst', 'writer']      
2026-06-07 11:01:30 [info     ] research_workflow_initialized  enable_a2a=True enable_mcp=True max_retries=2
2026-06-07 11:01:30 [info     ] workflow_execute_start         query='explain why india is a diverse country'
2026-06-07 11:01:30 [info     ] workflow_plan_node_start       query='explain why india is a diverse country'
2026-06-07 11:01:30 [info     ] a2a_planner_decompose_task_start
2026-06-07 11:01:30 [info     ] a2a_call_agent                 correlation_id=msg_20260607053130574559 endpoint=http://localhost:8080/planner method=decompose_task
2026-06-07 11:01:32 [error    ] a2a_http_error                 attempt=1 error='All connection attempts failed'
2026-06-07 11:01:35 [error    ] a2a_http_error                 attempt=2 error='All connection attempts failed'
2026-06-07 11:01:37 [error    ] a2a_http_error                 attempt=3 error='All connection attempts failed'
2026-06-07 11:01:37 [warning  ] a2a_planner_decompose_task_failed error={'code': 'HTTP_ERROR', 'message': 'All connection attempts failed'}
2026-06-07 11:01:37 [info     ] planner_decompose_task_start   query='explain why india is a diverse country'
2026-06-07 11:04:38 [info     ] planner_decompose_task_complete confidence=0.95 plan_id=plan_001 task_count=6
2026-06-07 11:04:38 [info     ] workflow_validate_plan_start   plan_id=plan_001
2026-06-07 11:04:38 [info     ] a2a_planner_validate_plan_start
2026-06-07 11:04:38 [info     ] a2a_call_agent                 correlation_id=msg_20260607053438451917 endpoint=http://localhost:8080/planner method=validate_plan
2026-06-07 11:04:40 [error    ] a2a_http_error                 attempt=1 error='All connection attempts failed'
2026-06-07 11:04:43 [error    ] a2a_http_error                 attempt=2 error='All connection attempts failed'
2026-06-07 11:04:45 [error    ] a2a_http_error                 attempt=3 error='All connection attempts failed'
2026-06-07 11:04:45 [warning  ] a2a_planner_validate_plan_failed error={'code': 'HTTP_ERROR', 'message': 'All connection attempts failed'}
2026-06-07 11:04:45 [info     ] planner_validate_plan_start    plan_id=plan_001
2026-06-07 11:04:45 [info     ] planner_validate_plan_complete is_valid=True issue_count=0 plan_id=plan_001 warning_count=0
2026-06-07 11:04:45 [info     ] workflow_research_node_start   plan_id=plan_001
2026-06-07 11:04:45 [info     ] a2a_researcher_search_start   
2026-06-07 11:04:45 [info     ] a2a_call_agent                 correlation_id=msg_20260607053445373013 endpoint=http://localhost:8080/researcher method=search
2026-06-07 11:04:47 [error    ] a2a_http_error                 attempt=1 error='All connection attempts failed'
2026-06-07 11:04:49 [error    ] a2a_http_error                 attempt=2 error='All connection attempts failed'
2026-06-07 11:04:52 [error    ] a2a_http_error                 attempt=3 error='All connection attempts failed'
2026-06-07 11:04:52 [warning  ] a2a_researcher_search_failed   error={'code': 'HTTP_ERROR', 'message': 'All connection attempts failed'}
2026-06-07 11:04:52 [info     ] researcher_search_start        max_results=10 query='explain why india is a diverse country'
2026-06-07 11:05:08 [info     ] azure_toolbox_search_start     project_endpoint=https://reasoning-agent-hack2-resource.services.ai.azure.com/api/projects/reasoning-agent-hack2 query="India's linguistic diversity: regional language di" toolbox=reasoning-agent-web-search
2026-06-07 11:05:08 [error    ] azure_toolbox_search_error_falling_back error="No module named 'langchain_azure_ai'" query="India's linguistic diversity: regional language di"
2026-06-07 11:05:08 [info     ] azure_toolbox_search_start     project_endpoint=https://reasoning-agent-hack2-resource.services.ai.azure.com/api/projects/reasoning-agent-hack2 query='Religious demographics of India by state' toolbox=reasoning-agent-web-search
2026-06-07 11:05:08 [error    ] azure_toolbox_search_error_falling_back error="No module named 'langchain_azure_ai'" query='Religious demographics of India by state'
2026-06-07 11:05:08 [info     ] azure_toolbox_search_start     project_endpoint=https://reasoning-agent-hack2-resource.services.ai.azure.com/api/projects/reasoning-agent-hack2 query="Ethnic diversity in India's Northeast region" toolbox=reasoning-agent-web-search
2026-06-07 11:05:08 [error    ] azure_toolbox_search_error_falling_back error="No module named 'langchain_azure_ai'" query="Ethnic diversity in India's Northeast region"
2026-06-07 11:05:08 [info     ] azure_toolbox_search_start     project_endpoint=https://reasoning-agent-hack2-resource.services.ai.azure.com/api/projects/reasoning-agent-hack2 query='Cultural festivals and traditions across Indian st' toolbox=reasoning-agent-web-search
2026-06-07 11:05:08 [error    ] azure_toolbox_search_error_falling_back error="No module named 'langchain_azure_ai'" query='Cultural festivals and traditions across Indian st'
2026-06-07 11:05:08 [info     ] azure_toolbox_search_start     project_endpoint=https://reasoning-agent-hack2-resource.services.ai.azure.com/api/projects/reasoning-agent-hack2 query='Geographical landscapes: mountains, deserts, and c' toolbox=reasoning-agent-web-search
2026-06-07 11:05:08 [error    ] azure_toolbox_search_error_falling_back error="No module named 'langchain_azure_ai'" query='Geographical landscapes: mountains, deserts, and c'
2026-06-07 11:05:08 [info     ] researcher_search_complete     high_confidence_count=10 query='explain why india is a diverse country' total_results=10
2026-06-07 11:05:08 [info     ] workflow_analyze_node_start    query='explain why india is a diverse country'
2026-06-07 11:05:08 [info     ] a2a_analyst_analyze_start     
2026-06-07 11:05:08 [info     ] a2a_call_agent                 correlation_id=msg_20260607053508661088 endpoint=http://localhost:8080/analyst method=analyze
2026-06-07 11:05:10 [error    ] a2a_http_error                 attempt=1 error='All connection attempts failed'
2026-06-07 11:05:13 [error    ] a2a_http_error                 attempt=2 error='All connection attempts failed'
gent-web-search
2026-06-07 11:05:08 [error    ] azure_toolbox_search_error_falling_back error="No module named 'langchain_azure_ai'" query='Religious demographics of India by state'
2026-06-07 11:05:08 [info     ] azure_toolbox_search_start     project_endpoint=https://reasoning-agent-hack2-resource.services.ai.azure.com/api/projects/reasoning-agent-hack2 query="Ethnic diversity in India's Northeast region" toolbox=reasoning-agent-web-search
2026-06-07 11:05:08 [error    ] azure_toolbox_search_error_falling_back error="No module named 'langchain_azure_ai'" query="Ethnic diversity in India's Northeast region"
2026-06-07 11:05:08 [info     ] azure_toolbox_search_start     project_endpoint=https://reasoning-agent-hack2-resource.services.ai.azure.com/api/projects/reasoning-agent-hack2 query='Cultural festivals and traditions across Indian st' toolbox=reasoning-agent-web-search
2026-06-07 11:05:08 [error    ] azure_toolbox_search_error_falling_back error="No module named 'langchain_azure_ai'" query='Cultural festivals and traditions across Indian st'
2026-06-07 11:05:08 [info     ] azure_toolbox_search_start     project_endpoint=https://reasoning-agent-hack2-resource.services.ai.azure.com/api/projects/reasoning-agent-hack2 query='Geographical landscapes: mountains, deserts, and c' toolbox=reasoning-agent-web-search
2026-06-07 11:05:08 [error    ] azure_toolbox_search_error_falling_back error="No module named 'langchain_azure_ai'" query='Geographical landscapes: mountains, deserts, and c'
2026-06-07 11:05:08 [info     ] researcher_search_complete     high_confidence_count=10 query='explain why india is a diverse country' total_results=10
2026-06-07 11:05:08 [info     ] workflow_analyze_node_start    query='explain why india is a diverse country'
2026-06-07 11:05:08 [info     ] a2a_analyst_analyze_start     
2026-06-07 11:05:08 [info     ] a2a_call_agent                 correlation_id=msg_20260607053508661088 endpoint=http://localhost:8080/analyst method=analyze
2026-06-07 11:05:10 [error    ] a2a_http_error                 attempt=1 error='All connection attempts failed'
2026-06-07 11:05:13 [error    ] a2a_http_error                 attempt=2 error='All connection attempts failed'
easoning-agent-web-search
2026-06-07 11:05:08 [error    ] azure_toolbox_search_error_falling_back error="No module named 'langchain_azure_ai'" query='Cultural festivals and traditions across Indian st'
2026-06-07 11:05:08 [info     ] azure_toolbox_search_start     project_endpoint=https://reasoning-agent-hack2-resource.services.ai.azure.com/api/projects/reasoning-agent-hack2 query='Geographical landscapes: mountains, deserts, and c' toolbox=reasoning-agent-web-search
2026-06-07 11:05:08 [error    ] azure_toolbox_search_error_falling_back error="No module named 'langchain_azure_ai'" query='Geographical landscapes: mountains, deserts, and c'
2026-06-07 11:05:08 [info     ] researcher_search_complete     high_confidence_count=10 query='explain why india is a diverse country' total_results=10
2026-06-07 11:05:08 [info     ] workflow_analyze_node_start    query='explain why india is a diverse country'
2026-06-07 11:05:08 [info     ] a2a_analyst_analyze_start     
2026-06-07 11:05:08 [info     ] a2a_call_agent                 correlation_id=msg_20260607053508661088 endpoint=http://localhost:8080/analyst method=analyze
2026-06-07 11:05:10 [error    ] a2a_http_error                 attempt=1 error='All connection attempts failed'
2026-06-07 11:05:13 [error    ] a2a_http_error                 attempt=2 error='All connection attempts failed'
2026-06-07 11:05:08 [info     ] a2a_call_agent                 correlation_id=msg_20260607053508661088 endpoint=http://localhost:8080/analyst method=analyze
2026-06-07 11:05:10 [error    ] a2a_http_error                 attempt=1 error='All connection attempts failed'
2026-06-07 11:05:13 [error    ] a2a_http_error                 attempt=2 error='All connection attempts failed'
2026-06-07 11:05:13 [error    ] a2a_http_error                 attempt=2 error='All connection attempts failed'
2026-06-07 11:05:15 [error    ] a2a_http_error                 attempt=3 error='All connection attempts failed'
2026-06-07 11:05:15 [warning  ] a2a_analyst_analyze_failed     error={'code': 'HTTP_ERROR', 'message': 'All connection attempts failed'}
2026-06-07 11:05:15 [info     ] analyst_analyze_start          query='explain why india is a diverse country' research_data_type=dict













2026-06-07 11:05:15 [error    ] a2a_http_error                 attempt=3 error='All connection attempts failed'
2026-06-07 11:05:15 [warning  ] a2a_analyst_analyze_failed     error={'code': 'HTTP_ERROR', 'message': 'All connection attempts failed'}
2026-06-07 11:05:15 [info     ] analyst_analyze_start          query='explain why india is a diverse country' research_data_type=dict





2026-06-07 11:05:15 [error    ] a2a_http_error                 attempt=3 error='All connection attempts failed'
2026-06-07 11:05:15 [warning  ] a2a_analyst_analyze_failed     error={'code': 'HTTP_ERROR', 'message': 'All connection attempts failed'}
2026-06-07 11:05:15 [error    ] a2a_http_error                 attempt=3 error='All connection attempts failed'
2026-06-07 11:05:15 [warning  ] a2a_analyst_analyze_failed     error={'code': 'HTTP_ERROR', 'message': 'All connection attempts failed'}
2026-06-07 11:05:15 [info     ] analyst_analyze_start          query='explain why india is a diverse country' research_data_type=dict
2026-06-07 11:06:45 [error    ] analyst_json_parse_error       error='Invalid \\escape: line 34 column 43 (char 1583)'
2026-06-07 11:06:45 [info     ] workflow_write_report_start    query='explain why india is a diverse country'
2026-06-07 11:06:45 [info     ] a2a_writer_generate_report_start
2026-06-07 11:06:45 [info     ] a2a_call_agent                 correlation_id=msg_20260607053645566104 endpoint=http://localhost:8080/writer method=generate_report
2026-06-07 11:06:47 [error    ] a2a_http_error                 attempt=1 error='All connection attempts failed'
2026-06-07 11:06:50 [error    ] a2a_http_error                 attempt=2 error='All connection attempts failed'
2026-06-07 11:06:52 [error    ] a2a_http_error                 attempt=3 error='All connection attempts failed'
2026-06-07 11:06:52 [warning  ] a2a_writer_generate_report_failed error={'code': 'HTTP_ERROR', 'message': 'All connection attempts failed'}
ndia is a diverse country'
2026-06-07 11:07:32 [error    ] writer_json_parse_error        error="Expecting ',' delimiter: line 11 column 44 (char 1177)"
2026-06-07 11:07:32 [info     ] writer_generate_report_complete recommendations=1 report_id=report_20260607_053732 sections=3
2026-06-07 11:07:32 [info     ] workflow_execute_complete      completed_tasks=4 confidence=0.2 status=completed

════════════════════════════════════════════════════════════════════════
  WORKFLOW RESULTS
════════════════════════════════════════════════════════════════════════
  ✓  Status          : completed
  ✓  Processing time : 361.5 s
  ✓  Confidence      : 20%

  Completed stages:
  ✓  plan
  ✓  research
  ✓  analyze
  ✓  write_report

════════════════════════════════════════════════════════════════════════
  📄  Research Report: explain why india is a diverse country...
════════════════════════════════════════════════════════════════════════

Executive Summary:
This report analyzes the research query and provides key findings based on available data.

Report Sections:

  ▶ Introduction
    This report analyzes the research query and provides key findings based on available data.

  ▶ Key Findings
    The research has identified several important findings related to the query. Detailed analysis is provided in the sections below.

  ▶ Conclusions
    1. Analysis completed with available data.

Key Conclusions:
  1. Analysis completed with available data.

Recommendations:
  1. Further research may provide additional insights.

Sources Referenced:
  • India'S Linguistic Diversity: Regional Language Distribution — Reuters
    https://www.reuters.com/article/1
  • Religious Demographics Of India By State - Reuters Analysis — Reuters
    https://www.reuters.com/article/1
  • Ethnic Diversity In India'S Northeast Region - Reuters Analy — Reuters
    https://www.reuters.com/article/1
  • Cultural Festivals And Traditions Across Indian States - Reu — Reuters
    https://www.reuters.com/article/1
  • Geographical Landscapes: Mountains, Deserts, And Coasts In I — Reuters
    https://www.reuters.com/article/1


  ▶ Introduction
    This report analyzes the research query and provides key findings based on available data.

  ▶ Key Findings
    The research has identified several important findings related to the query. Detailed analysis is provided in the sections below.

  ▶ Conclusions
    1. Analysis completed with available data.

Key Conclusions:
  1. Analysis completed with available data.

Recommendations:
  1. Further research may provide additional insights.

Sources Referenced:
  • India'S Linguistic Diversity: Regional Language Distribution — Reuters
    https://www.reuters.com/article/1
  • Religious Demographics Of India By State - Reuters Analysis — Reuters
    https://www.reuters.com/article/1
  • Ethnic Diversity In India'S Northeast Region - Reuters Analy — Reuters
    https://www.reuters.com/article/1
  • Cultural Festivals And Traditions Across Indian States - Reu — Reuters
    https://www.reuters.com/article/1
  • Geographical Landscapes: Mountains, Deserts, And Coasts In I — Reuters
    https://www.reuters.com/article/1

    1. Analysis completed with available data.

Key Conclusions:
  1. Analysis completed with available data.

Recommendations:
  1. Further research may provide additional insights.

Sources Referenced:
  • India'S Linguistic Diversity: Regional Language Distribution — Reuters
    https://www.reuters.com/article/1
  • Religious Demographics Of India By State - Reuters Analysis — Reuters
    https://www.reuters.com/article/1
  • Ethnic Diversity In India'S Northeast Region - Reuters Analy — Reuters
    https://www.reuters.com/article/1
  • Cultural Festivals And Traditions Across Indian States - Reu — Reuters
    https://www.reuters.com/article/1
  • Geographical Landscapes: Mountains, Deserts, And Coasts In I — Reuters
    https://www.reuters.com/article/1

    https://www.reuters.com/article/1
  • Cultural Festivals And Traditions Across Indian States - Reu — Reuters
    https://www.reuters.com/article/1
  • Geographical Landscapes: Mountains, Deserts, And Coasts In I — Reuters
    https://www.reuters.com/article/1


Report ID: report_20260607_053732  |  Generated: 2026-06-07T05:37:32

  ✓  Report saved → report_report_20260607_053732.md
Query>


5)python run_agent.py --query "Analyze AI startup risks in India" --model phi-4-reasoning
PS C:\Users\RAJ\Desktop\research-to-report-multi-agent> python run_agent.py --query "Analyze AI startup risks in India" --model phi-4-reasoning

════════════════════════════════════════════════════════════════════════
  Research-to-Report Multi-Agent  ·  Phi-4 Reasoning
════════════════════════════════════════════════════════════════════════
  →  Query : Analyze AI startup risks in India
  →  Model : phi-4-reasoning
2026-06-07 11:02:13 [info     ] environment_loaded             env_file=.env
[11:02:13] 📋 PLANNER       — breaking query into sub-tasks …  
2026-06-07 11:02:14 [info     ] instantiating_chat_openai_for_foundry base_url=https://reasoning-agent-hack2-resource.services.ai.azure.com/openai/v1 model=phi-4-reasoning temperature=0.3
2026-06-07 11:02:14 [info     ] instantiating_chat_openai_for_foundry base_url=https://reasoning-agent-hack2-resource.services.ai.azure.com/openai/v1 model=phi-4-reasoning temperature=0.4
2026-06-07 11:02:14 [info     ] a2a_client_initialized         endpoint=http://localhost:8080/planner timeout=30
2026-06-07 11:02:14 [info     ] a2a_client_initialized         endpoint=http://localhost:8080/researcher timeout=30       
2026-06-07 11:02:14 [info     ] a2a_client_initialized         endpoint=http://localhost:8080/analyst timeout=30
2026-06-07 11:02:14 [info     ] a2a_client_initialized         endpoint=http://localhost:8080/writer timeout=30
2026-06-07 11:02:14 [info     ] a2a_clients_initialized        agents=['planner', 'researcher', 'analyst', 'writer']      
2026-06-07 11:02:14 [info     ] research_workflow_initialized  enable_a2a=True enable_mcp=True max_retries=2
2026-06-07 11:02:14 [info     ] workflow_execute_start         query='Analyze AI startup risks in India'
2026-06-07 11:02:14 [info     ] workflow_plan_node_start       query='Analyze AI startup risks in India'
2026-06-07 11:02:14 [info     ] a2a_planner_decompose_task_start
2026-06-07 11:02:14 [info     ] a2a_call_agent                 correlation_id=msg_20260607053214442477 endpoint=http://localhost:8080/planner method=decompose_task
2026-06-07 11:02:16 [error    ] a2a_http_error                 attempt=1 error='All connection attempts failed'
2026-06-07 11:02:14 [info     ] instantiating_chat_openai_for_foundry base_url=https://reasoning-agent-hack2-resource.services.ai.azure.com/openai/v1 model=phi-4-reasoning temperature=0.3
2026-06-07 11:02:14 [info     ] instantiating_chat_openai_for_foundry base_url=https://reasoning-agent-hack2-resource.services.ai.azure.com/openai/v1 model=phi-4-reasoning temperature=0.4
2026-06-07 11:02:14 [info     ] a2a_client_initialized         endpoint=http://localhost:8080/planner timeout=30
2026-06-07 11:02:14 [info     ] a2a_client_initialized         endpoint=http://localhost:8080/researcher timeout=30       
2026-06-07 11:02:14 [info     ] a2a_client_initialized         endpoint=http://localhost:8080/analyst timeout=30
2026-06-07 11:02:14 [info     ] a2a_client_initialized         endpoint=http://localhost:8080/writer timeout=30
2026-06-07 11:02:14 [info     ] a2a_clients_initialized        agents=['planner', 'researcher', 'analyst', 'writer']      
2026-06-07 11:02:14 [info     ] research_workflow_initialized  enable_a2a=True enable_mcp=True max_retries=2
2026-06-07 11:02:14 [info     ] workflow_execute_start         query='Analyze AI startup risks in India'
2026-06-07 11:02:14 [info     ] workflow_plan_node_start       query='Analyze AI startup risks in India'
2026-06-07 11:02:14 [info     ] a2a_planner_decompose_task_start
2026-06-07 11:02:14 [info     ] a2a_call_agent                 correlation_id=msg_20260607053214442477 endpoint=http://localhost:8080/planner method=decompose_task
2026-06-07 11:02:16 [error    ] a2a_http_error                 attempt=1 error='All connection attempts failed'
2026-06-07 11:02:19 [error    ] a2a_http_error                 attempt=2 error='All connection attempts failed'
2026-06-07 11:02:21 [error    ] a2a_http_error                 attempt=3 error='All connection attempts failed'
2026-06-07 11:02:21 [warning  ] a2a_planner_decompose_task_failed error={'code': 'HTTP_ERROR', 'message': 'All connection attempts failed'}
2026-06-07 11:02:21 [info     ] planner_decompose_task_start   query='Analyze AI startup risks in India'





2026-06-07 11:02:14 [info     ] instantiating_chat_openai_for_foundry base_url=https://reasoning-agent-hack2-resource.services.ai.azure.com/openai/v1 model=phi-4-reasoning temperature=0.3
2026-06-07 11:02:14 [info     ] instantiating_chat_openai_for_foundry base_url=https://reasoning-agent-hack2-resource.services.ai.azure.com/openai/v1 model=phi-4-reasoning temperature=0.4
2026-06-07 11:02:14 [info     ] a2a_client_initialized         endpoint=http://localhost:8080/planner timeout=30
2026-06-07 11:02:14 [info     ] a2a_client_initialized         endpoint=http://localhost:8080/researcher timeout=30       
2026-06-07 11:02:14 [info     ] a2a_client_initialized         endpoint=http://localhost:8080/analyst timeout=30
2026-06-07 11:02:14 [info     ] a2a_client_initialized         endpoint=http://localhost:8080/writer timeout=30
2026-06-07 11:02:14 [info     ] a2a_clients_initialized        agents=['planner', 'researcher', 'analyst', 'writer']      
2026-06-07 11:02:14 [info     ] research_workflow_initialized  enable_a2a=True enable_mcp=True max_retries=2
2026-06-07 11:02:14 [info     ] workflow_execute_start         query='Analyze AI startup risks in India'
2026-06-07 11:02:14 [info     ] workflow_plan_node_start       query='Analyze AI startup risks in India'
2026-06-07 11:02:14 [info     ] a2a_planner_decompose_task_start
2026-06-07 11:02:14 [info     ] a2a_call_agent                 correlation_id=msg_20260607053214442477 endpoint=http://localhost:8080/planner method=decompose_task
2026-06-07 11:02:16 [error    ] a2a_http_error                 attempt=1 error='All connection attempts failed'
2026-06-07 11:02:14 [info     ] a2a_planner_decompose_task_start
2026-06-07 11:02:14 [info     ] a2a_call_agent                 correlation_id=msg_20260607053214442477 endpoint=http://localhost:8080/planner method=decompose_task
2026-06-07 11:02:16 [error    ] a2a_http_error                 attempt=1 error='All connection attempts failed'
2026-06-07 11:02:16 [error    ] a2a_http_error                 attempt=1 error='All connection attempts failed'
2026-06-07 11:02:19 [error    ] a2a_http_error                 attempt=2 error='All connection attempts failed'
2026-06-07 11:02:21 [error    ] a2a_http_error                 attempt=3 error='All connection attempts failed'
2026-06-07 11:02:21 [warning  ] a2a_planner_decompose_task_failed error={'code': 'HTTP_ERROR', 'message': 'All connection attempts failed'}
2026-06-07 11:02:21 [info     ] planner_decompose_task_start   query='Analyze AI startup risks in India'













2026-06-07 11:02:19 [error    ] a2a_http_error                 attempt=2 error='All connection attempts failed'
2026-06-07 11:02:21 [error    ] a2a_http_error                 attempt=3 error='All connection attempts failed'
2026-06-07 11:02:21 [warning  ] a2a_planner_decompose_task_failed error={'code': 'HTTP_ERROR', 'message': 'All connection attempts failed'}
2026-06-07 11:02:21 [info     ] planner_decompose_task_start   query='Analyze AI startup risks in India'





2026-06-07 11:02:19 [error    ] a2a_http_error                 attempt=2 error='All connection attempts failed'
2026-06-07 11:02:21 [error    ] a2a_http_error                 attempt=3 error='All connection attempts failed'
2026-06-07 11:02:21 [warning  ] a2a_planner_decompose_task_failed error={'code': 'HTTP_ERROR', 'message': 'All connection 2026-06-07 11:02:19 [error    ] a2a_http_error                 attempt=2 e
rror='All connection attempts failed'                                                                                                                                                               2026-06-07 11:02:21 [error    ] a2a_http_error                 attempt=3 error='All connection attempts failed'
2026-06-07 11:02:21 [warning  ] a2a_planner_decompose_task_failed error={'code': 'HTTP_ERROR', 'message': 'All connection attempts failed'}
2026-06-07 11:02:19 [error    ] a2a_http_error                 attempt=2 error='All connection attempts failed'
2026-06-07 11:02:21 [error    ] a2a_http_error                 attempt=3 error='All connection attempts failed'
2026-06-07 11:02:21 [warning  ] a2a_planner_decompose_task_failed error={'code': 'HTTP_ERROR', 'message': 'All connection attempts failed'}
2026-06-07 11:02:21 [info     ] planner_decompose_task_start   query='Analyze AI startup risks in India'
























2026-06-07 11:02:19 [error    ] a2a_http_error                 attempt=2 error='All connection attempts failed'
2026-06-07 11:02:21 [error    ] a2a_http_error                 attempt=3 error='All connection attempts failed'
2026-06-07 11:02:21 [warning  ] a2a_planner_decompose_task_failed error={'code': 'HTTP_ERROR', 'message': 'All connection attempts failed'}
2026-06-07 11:02:21 [info     ] planner_decompose_task_start   query='Analyze AI startup risks in India'















2026-06-07 11:02:21 [info     ] planner_decompose_task_start   query='Analyze AI startup risks in India'



























2026-06-07 11:02:21 [info     ] planner_decompose_task_start   query='Analyze AI startup risks in India'



















2026-06-07 11:02:21 [info     ] planner_decompose_task_start   query='Analyze AI startup risks in India'





2026-06-07 11:02:21 [info     ] planner_decompose_task_start   query='Analyze AI startup risks in India'
2026-06-07 11:02:21 [info     ] planner_decompose_task_start   query='Analyze AI startup risks in India'
2026-06-07 11:08:24 [error    ] planning_failed                error='Request timed out.'
2026-06-07 11:08:24 [info     ] workflow_execute_complete      completed_tasks=0 confidence=0 status=completed_with_errors

════════════════════════════════════════════════════════════════════════
  WORKFLOW RESULTS
════════════════════════════════════════════════════════════════════════
  ✓  Status          : completed_with_errors
  ✓  Processing time : 370.1 s

  Errors encountered:
  ⚠  {'node': 'validate_plan', 'error': 'No plan available'}
  ✗  No report generated — check errors above

6)python run_agent.py --query "Renewable energy in India" --stream
PS C:\Users\RAJ\Desktop\research-to-report-multi-agent> python run_agent.py --query "Renewable energy in India" --stream

════════════════════════════════════════════════════════════════════════
  Research Agent — Streaming Mode
════════════════════════════════════════════════════════════════════════
  →  Query: Renewable energy in India
2026-06-07 11:02:26 [info     ] environment_loaded             env_file=.env
2026-06-07 11:02:26 [info     ] instantiating_chat_openai_for_foundry base_url=https://reasoning-agent-hack2-resource.services.ai.azure.com/openai/v1 model=phi-4-mini-reasoning temperature=0.3
2026-06-07 11:02:27 [info     ] instantiating_chat_openai_for_foundry base_url=https://reasoning-agent-hack2-resource.services.ai.azure.com/openai/v1 model=phi-4-mini-reasoning temperature=0.4
2026-06-07 11:02:27 [info     ] mcp_web_search_initialized     server_url='https://reasoning-agent-hack2-resource.services.ai.azure.com/api/projects/reasoning-agent-hack2/toolboxes/reasoning-agent
-web-search/mcp?api-version=v1' use_azure_toolbox=True                                                                                                                                              2026-06-07 11:02:27 [info     ] instantiating_chat_openai_for_foundry base_url=https://reasoning-agent-hack2-resource.services.ai.azure.com/openai/v1 model=phi-4-mini-reasoning temperature=0.3
2026-06-07 11:02:27 [info     ] instantiating_chat_openai_for_foundry base_url=https://reasoning-agent-hack2-resource.services.ai.azure.com/openai/v1 model=phi-4-mini-reasoning temperature=0.4
2026-06-07 11:02:27 [info     ] a2a_client_initialized         endpoint=http://localhost:8080/planner timeout=30
2026-06-07 11:02:27 [info     ] a2a_client_initialized         endpoint=http://localhost:8080/researcher timeout=30
2026-06-07 11:02:27 [info     ] a2a_client_initialized         endpoint=http://localhost:8080/analyst timeout=30
2026-06-07 11:02:27 [info     ] a2a_client_initialized         endpoint=http://localhost:8080/writer timeout=30
903 endpoint=http://localhost:8080/planner method=decompose_task
2026-06-07 11:02:29 [error    ] a2a_http_error                 attempt=1 error='All connection attempts failed'
2026-06-07 11:02:32 [error    ] a2a_http_error                 attempt=2 error='All connection attempts failed'
2026-06-07 11:02:34 [error    ] a2a_http_error                 attempt=3 error='All connection attempts failed'
2026-06-07 11:02:34 [warning  ] a2a_planner_decompose_task_failed error={'code': 'HTTP_ERROR', 'message': 'All connection attempts failed'}
2026-06-07 11:02:34 [info     ] planner_decompose_task_start   query='Renewable energy in India'
2026-06-07 11:03:38 [info     ] planner_decompose_task_complete confidence=0.95 plan_id=plan_001 task_count=7
  ✓  Planner Agent done
[11:03:38] ✅ Validator       — checking plan quality …
2026-06-07 11:03:38 [info     ] workflow_validate_plan_start   plan_id=plan_001
2026-06-07 11:03:38 [info     ] a2a_planner_validate_plan_start
2026-06-07 11:03:38 [info     ] a2a_call_agent                 correlation_id=msg_20260607053338314145 endpoint=http://localhost:8080/planner method=validate_plan
2026-06-07 11:03:40 [error    ] a2a_http_error                 attempt=1 error='All connection attempts failed'
2026-06-07 11:03:42 [error    ] a2a_http_error                 attempt=2 error='All connection attempts failed'
2026-06-07 11:03:45 [error    ] a2a_http_error                 attempt=3 error='All connection attempts failed'
2026-06-07 11:03:45 [warning  ] a2a_planner_validate_plan_failed error={'code': 'HTTP_ERROR', 'message': 'All connection attempts failed'}
2026-06-07 11:03:45 [info     ] planner_validate_plan_start    plan_id=plan_001
2026-06-07 11:03:45 [info     ] planner_validate_plan_complete is_valid=True issue_count=0 plan_id=plan_001 warning_count=903 endpoint=http://localhost:8080/planner method=decompose_task
2026-06-07 11:02:29 [error    ] a2a_http_error                 attempt=1 error='All connection attempts failed'
2026-06-07 11:02:32 [error    ] a2a_http_error                 attempt=2 error='All connection attempts failed'
2026-06-07 11:02:34 [error    ] a2a_http_error                 attempt=3 error='All connection attempts failed'
2026-06-07 11:02:34 [warning  ] a2a_planner_decompose_task_failed error={'code': 'HTTP_ERROR', 'message': 'All connection attempts failed'}
2026-06-07 11:02:34 [info     ] planner_decompose_task_start   query='Renewable energy in India'
2026-06-07 11:03:38 [info     ] planner_decompose_task_complete confidence=0.95 plan_id=plan_001 task_count=7
  ✓  Planner Agent done
[11:03:38] ✅ Validator       — checking plan quality …
2026-06-07 11:03:38 [info     ] workflow_validate_plan_start   plan_id=plan_001
2026-06-07 11:03:38 [info     ] a2a_planner_validate_plan_start

PS C:\Users\RAJ\Desktop\research-to-report-multi-agent>

1
  ✓  Validator done
[11:03:45] 🔍 Researcher Agent — executing web searches …
  ✗  {'node': 'research', 'error': 'No plan available'}
  ⚠  No report in final state
PS C:\Users\RAJ\Desktop\research-to-report-multi-agent>
  ✓  Validator done
[11:03:45] 🔍 Researcher Agent — executing web searches …
1
  ✓  Validator done
[11:03:45] 🔍 Researcher Agent — executing web searches …
  ✗  {'node': 'research', 'error': 'No plan available'}
1
  ✓  Validator done
[11:03:45] 🔍 Researcher Agent — executing web searches …
  ✗  {'node': 'research', 'error': 'No plan available'}
  ⚠  No report in final state