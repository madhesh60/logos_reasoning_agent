# Before running the sample:
#    pip install azure-ai-projects>=2.1.0

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

endpoint = "https://reasoning-agent-hack2-resource.services.ai.azure.com/api/projects/reasoning-agent-hack2"

project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

my_agent = "planner-agent"
my_version = "9"

openai_client = project_client.get_openai_client()

response = openai_client.responses.create(
    input=[{"role": "user", "content": "Recent trends in AI." }],
    extra_body={"agent_reference": {"name": my_agent, "version": my_version, "type": "agent_reference"}},
)

print(f"Response output: {response.output_text}")

# Backward-compatible imports for other files
from src.agents import PlannerAgent, ResearchPlan, SubTask, TaskType