import asyncio
import os

import httpx
from azure.identity import DefaultAzureCredential
from a2a.client import A2ACardResolver, ClientConfig, create_client
from a2a.helpers import new_text_message
from a2a.types.a2a_pb2 import Role, SendMessageRequest

endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT", "https://reasoning-agent-hack2-resource.services.ai.azure.com/api/projects/reasoning-agent-hack2")
agent_name = "industry-news-trend-scanner"

# Full A2A base URL for this agent
A2A_BASE_URL = f"{endpoint}/agents/{agent_name}/endpoint/protocols/a2a"
AGENT_CARD_PATH = "agentCard/v0.3"


async def main():
    credential = DefaultAzureCredential()
    token = credential.get_token("https://ai.azure.com/.default").token

    async with httpx.AsyncClient(
        headers={"Authorization": f"Bearer {token}"},
        timeout=httpx.Timeout(120.0),
    ) as httpx_client:
        # Resolve the agent card
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=A2A_BASE_URL,
            agent_card_path=AGENT_CARD_PATH,
        )
        agent_card = await resolver.get_agent_card()

        # Create a non-streaming A2A client
        config = ClientConfig(streaming=False, httpx_client=httpx_client)
        client = await create_client(agent=agent_card, client_config=config)

        # Send a message to the agent
        message = new_text_message("Hello, what can you do?", role=Role.ROLE_USER)
        request = SendMessageRequest(message=message)

        async for response in client.send_message(request):
            print(response)

        await client.close()


if __name__ == "__main__":
    asyncio.run(main())