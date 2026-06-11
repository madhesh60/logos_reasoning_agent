# Before running the sample:
#    pip install azure-ai-projects>=2.1.0

import os
import sys
import time
import subprocess
import json
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.core.credentials import AccessToken
from dotenv import load_dotenv

# Fix Windows console encoding to support Unicode output
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Load env variables from .env
load_dotenv()

# Rich UI imports
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.markdown import Markdown
    from rich.status import Status
    from rich.prompt import Prompt
except ImportError:
    print("Error: The 'rich' library is required to run this CLI.")
    print("Please install it using: pip install rich")
    sys.exit(1)

console = Console()

class AzureCliTokenCredential:
    """
    Credential that invokes Azure CLI to fetch tokens.
    Necessary on Windows when DefaultAzureCredential fails due to Python subprocess
    limitations with .cmd file resolution.
    """
    def get_token(self, *scopes, **kwargs) -> AccessToken:
        resource = "https://management.core.windows.net"
        if scopes:
            scope = scopes[0]
            if scope.endswith("/.default"):
                resource = scope[:-9]
            else:
                resource = scope
        
        # Invoke az account get-access-token for the resource
        cmd = ["az.cmd", "account", "get-access-token", "--resource", resource]
        res = subprocess.run(" ".join(cmd), shell=True, capture_output=True, text=True, check=True)
        data = json.loads(res.stdout)
        
        expires_on = data.get("expiresOnTime")
        if expires_on is None:
            expires_str = data.get("expiresOn")
            if expires_str:
                try:
                    from datetime import datetime as dt_class
                    dt = dt_class.strptime(expires_str.split(".")[0], "%Y-%m-%d %H:%M:%S")
                    expires_on = int(dt.timestamp())
                except:
                    expires_on = int(time.time()) + 3600
            else:
                expires_on = int(time.time()) + 3600
        else:
            expires_on = int(expires_on)
            
        return AccessToken(data["accessToken"], expires_on)

NODE_MAP = {
    "planner_node": ("📋 Planner", "Decomposing query and planning research tasks"),
    "researcher_node": ("🔍 Researcher", "Executing web searches and gathering sources"),
    "news_node": ("📰 News Analyst", "Scanning recent news and market trends"),
    "analyst_node": ("🧠 Analyst", "Extracting insights and identifying risks"),
    "writer_node": ("📝 Writer", "Generating final report"),
}

def get_node_label(action_id: str) -> tuple[str, str]:
    action_id_lower = action_id.lower()
    for key, (label, desc) in NODE_MAP.items():
        if key in action_id_lower or key.replace("_node", "") in action_id_lower:
            return label, desc
    # Fallback
    formatted_name = action_id.replace("_", " ").title()
    return f"⚙️ {formatted_name}", f"Running {formatted_name}"

def execute_foundry_workflow(query: str):
    endpoint = "https://reasoning-agent-hack2-resource.services.ai.azure.com/api/projects/reasoning-agent-hack2"
    credential = AzureCliTokenCredential()
    
    console.print(f"\n[bold green]Query:[/] {query}\n")
    
    with console.status("[bold cyan]Connecting to AI Project Client...[/]", spinner="dots") as status:
        try:
            project_client = AIProjectClient(
                endpoint=endpoint,
                credential=credential,
            )
        except Exception as e:
            status.stop()
            console.print(f"[bold red]✗ Failed to connect to AI Project Client:[/] {e}")
            return
            
        with project_client:
            workflow = {
                "name": "investment-research-workflow",
                "version": "5",
            }
            
            try:
                openai_client = project_client.get_openai_client()
                status.update("[bold cyan]Creating conversation on Azure...[/]")
                conversation = openai_client.conversations.create()
                status.update(f"[bold cyan]Submitting query to Foundry (id: {conversation.id[:10]}...)...[/]")
                
                stream = openai_client.responses.create(
                    conversation=conversation.id,
                    extra_body={"agent_reference": {"name": workflow["name"], "version": workflow["version"], "type": "agent_reference"}},
                    input=query,
                    stream=True,
                    metadata={"x-ms-debug-mode-enabled": "1"},
                )
            except Exception as e:
                status.stop()
                console.print(f"[bold red]✗ Initialization failed:[/] {e}")
                return

            current_actor = None
            accumulated_text = ""
            writer_stream_started = False
            
            for event in stream:
                event_type = getattr(event, "type", "")
                
                if event_type == "response.output_item.added" and hasattr(event, "item"):
                    item = event.item
                    if item.type == "workflow_action":
                        action_id = getattr(item, "action_id", "")
                        current_actor = action_id
                        label, desc = get_node_label(action_id)
                        status.update(f"[bold cyan]Running {label}: {desc}...[/]")
                        
                elif event_type == "response.output_item.done" and hasattr(event, "item"):
                    item = event.item
                    if item.type == "workflow_action":
                        action_id = getattr(item, "action_id", "")
                        label, _ = get_node_label(action_id)
                        console.print(f"  [bold green]✓[/] {label} completed successfully.")
                        if action_id == current_actor:
                            current_actor = None
                            
                elif event_type == "response.output_text.delta":
                    delta = getattr(event, "delta", "")
                    if delta:
                        accumulated_text += delta
                        # Stream the writer node's text in real-time
                        if (current_actor and "writer" in current_actor.lower()) or writer_stream_started:
                            if not writer_stream_started:
                                writer_stream_started = True
                                status.stop()
                                console.print("\n[bold green]Streaming Report Output:[/]")
                            print(delta, end="", flush=True)
                            
                elif event_type == "response.failed":
                    status.stop()
                    console.print(f"\n[bold red]✗ Response failed.[/]")
                    if hasattr(event, "response") and getattr(event.response, "error", None):
                        console.print(f"[bold red]Details:[/] {event.response.error.message}")
            
            # Ensure status spinner is stopped before final rendering
            status.stop()
            
            # Clean up conversation in background
            status.update("[bold yellow]Cleaning up conversation...[/]")
            try:
                openai_client.conversations.delete(conversation_id=conversation.id)
            except Exception as e:
                console.print(f"[dim yellow]Warning: Conversation deletion failed: {e}[/]")
            status.stop()
            
            if accumulated_text:
                console.print("\n")
                console.print(Panel(
                    Markdown(accumulated_text),
                    title="[bold green]Final Research Report[/]",
                    border_style="green",
                    padding=(1, 2)
                ))
                
                # Save markdown to file
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    fname = f"report_foundry_{timestamp}.md"
                    with open(fname, "w", encoding="utf-8") as f:
                        f.write(accumulated_text)
                    console.print(f"  [bold green]✓[/] Report saved to [bold cyan]{fname}[/]")
                except Exception as e:
                    console.print(f"  [bold yellow]⚠[/] Could not save report file: {e}")
            else:
                console.print("\n[bold yellow]No report content returned from Foundry workflow.[/]")

def main():
    console.print(Panel(
        Text("Azure AI Foundry Multi-Agent System", style="bold white", justify="center"),
        subtitle="Foundry Workflow CLI Runner",
        border_style="cyan"
    ))
    
    if len(sys.argv) > 1:
        query = sys.argv[1]
        execute_foundry_workflow(query)
    else:
        # Interactive mode
        console.print("[dim]Type your research question, or 'exit' / 'quit' to exit.[/]")
        while True:
            try:
                query = Prompt.ask("\n[bold cyan]Research Question[/]")
                query = query.strip()
            except (KeyboardInterrupt, EOFError):
                console.print("\n[dim]Goodbye![/]")
                break
                
            if not query:
                continue
            if query.lower() in ("exit", "quit", "q"):
                console.print("[dim]Goodbye![/]")
                break
                
            try:
                execute_foundry_workflow(query)
            except Exception as e:
                console.print(f"[bold red]✗ Pipeline error:[/] {e}")

if __name__ == "__main__":
    main()