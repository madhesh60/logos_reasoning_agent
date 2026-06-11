# Before running the sample:
#    pip install azure-ai-projects>=2.1.0

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

endpoint = "https://reasoning-agent-hack2-resource.services.ai.azure.com/api/projects/reasoning-agent-hack2"

project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

my_agent = "competitive-landscape-researcher"
my_version = "2"

openai_client = project_client.get_openai_client()

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    from dotenv import load_dotenv
    from pathlib import Path

    # Load environment variables from .env
    root_dir = Path(__file__).resolve().parent.parent.parent
    load_dotenv(root_dir / ".env")

    # Check if a query is provided via command line arguments
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        # Prompt the user for input
        query = input(f"Enter query for {my_agent} (version {my_version}): ").strip()
        if not query:
            query = "Tell me what you can help with."

    print(f"\nSending query to {my_agent} (version {my_version}): '{query}'...")

    import time
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            response = openai_client.responses.create(
                input=[{"role": "user", "content": query}],
                extra_body={"agent_reference": {"name": my_agent, "version": my_version, "type": "agent_reference"}},
            )
            break
        except Exception as e:
            if "429" in str(e) or "RateLimitError" in str(e) or "rate limit" in str(e).lower():
                if attempt < max_retries:
                    wait_time = attempt * 10
                    print(f"\nRate limit exceeded (429). Retrying in {wait_time} seconds (Attempt {attempt}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    print(f"\nFailed after {max_retries} attempts due to RateLimitError.")
                    raise e
            else:
                raise e

    print("\n" + "=" * 60)
    print("AGENT RESPONSE")
    print("=" * 60)
    print(response.output_text)
    print("=" * 60 + "\n")

# Backward-compatible imports for other files
from src.agents import CompetitiveLandscapeAgent, CompetitiveAnalysisResult