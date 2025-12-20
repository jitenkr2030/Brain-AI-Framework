#!/usr/bin/env python3
"""
Brain-Inspired AI Framework CLI
Command-line interface for the Brain-Inspired AI Framework.
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import aiohttp
import yaml
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown

console = Console()


class BrainAICLI:
    """Command-line interface for Brain-Inspired AI Framework"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
    
    async def health_check(self):
        """Check system health"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        console.print("✅ [green]System is healthy[/green]")
                        console.print(f"Brain initialized: {data.get('brain_initialized', False)}")
                        console.print(f"Database status: {data.get('database', {}).get('status', 'unknown')}")
                    else:
                        console.print(f"❌ [red]Health check failed: {response.status}[/red]")
        except Exception as e:
            console.print(f"❌ [red]Connection failed: {e}[/red]")
    
    async def process_input(self, data: Dict[str, Any], context: Optional[Dict[str, Any]] = None):
        """Process input through the brain system"""
        try:
            payload = {
                "data": data,
                "context": context or {},
                "reasoning_type": "analysis"
            }
            
            async with aiohttp.ClientSession() as session:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("Processing with brain AI...", total=None)
                    
                    async with session.post(f"{self.api_url}/process", json=payload) as response:
                        if response.status == 200:
                            result = await response.json()
                            progress.update(task, description="✅ Processing complete")
                            
                            # Display results
                            console.print("\n[bold blue]🧠 Brain AI Processing Results[/bold blue]")
                            
                            # Active memories
                            if result.get("active_memories"):
                                table = Table(title="Active Memories")
                                table.add_column("ID", style="cyan")
                                table.add_column("Pattern", style="green")
                                table.add_column("Strength", style="yellow")
                                table.add_column("Type", style="magenta")
                                
                                for memory in result["active_memories"][:5]:  # Show top 5
                                    table.add_row(
                                        memory.get("id", "N/A")[:8] + "...",
                                        memory.get("pattern_signature", "N/A")[:30],
                                        f"{memory.get('strength', 0):.2f}",
                                        memory.get("memory_type", "N/A")
                                    )
                                
                                console.print(table)
                            
                            # Reasoning result
                            if result.get("reasoning_result"):
                                console.print(f"\n[bold green]💭 Reasoning:[/bold green]")
                                console.print(result["reasoning_result"].get("result", "No reasoning result"))
                            
                            # Metadata
                            console.print(f"\n[dim]Memory count: {result.get('memory_count', 0)} | "
                                         f"Execution time: {result.get('execution_time', 0):.2f}s[/dim]")
                        
                        else:
                            error_text = await response.text()
                            console.print(f"❌ [red]Processing failed: {response.status}[/red]")
                            console.print(error_text)
        
        except Exception as e:
            console.print(f"❌ [red]Error: {e}[/red]")
    
    async def provide_feedback(self, memory_id: str, feedback_type: str, outcome: Dict[str, Any]):
        """Provide feedback to the brain system"""
        try:
            payload = {
                "memory_id": memory_id,
                "feedback_type": feedback_type,
                "outcome": outcome,
                "source": "cli"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_url}/feedback", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        console.print(f"✅ [green]Feedback processed for memory {memory_id}[/green]")
                        console.print(f"Learning update: {result.get('learning_update', {})}")
                    else:
                        console.print(f"❌ [red]Feedback failed: {response.status}[/red]")
        
        except Exception as e:
            console.print(f"❌ [red]Error: {e}[/red]")
    
    async def get_memories(self, limit: int = 10):
        """Get current memories"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/memories?limit={limit}") as response:
                    if response.status == 200:
                        data = await response.json()
                        memories = data.get("memories", [])
                        
                        console.print(f"\n[bold blue]🧠 Current Memories ({len(memories)} shown)[/bold blue]")
                        
                        table = Table()
                        table.add_column("ID", style="cyan")
                        table.add_column("Pattern", style="green")
                        table.add_column("Strength", style="yellow")
                        table.add_column("Type", style="magenta")
                        table.add_column("Access Count", style="blue")
                        
                        for memory in memories:
                            table.add_row(
                                memory.get("id", "N/A")[:8] + "...",
                                memory.get("pattern_signature", "N/A")[:30],
                                f"{memory.get('strength', 0):.2f}",
                                memory.get("memory_type", "N/A"),
                                str(memory.get("access_count", 0))
                            )
                        
                        console.print(table)
                        console.print(f"\n[dim]Total memories: {data.get('total', 0)}[/dim]")
                    
                    else:
                        console.print(f"❌ [red]Failed to get memories: {response.status}[/red]")
        
        except Exception as e:
            console.print(f"❌ [red]Error: {e}[/red]")
    
    async def get_system_status(self):
        """Get comprehensive system status"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/status") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # System status panel
                        status_panel = Panel(
                            f"[bold green]Status:[/bold green] {data.get('status', 'unknown')}\n"
                            f"[bold blue]Uptime:[/bold blue] {data.get('uptime', 0):.1f}s\n"
                            f"[bold yellow]Brain Initialized:[/bold yellow] {data.get('brain_system', {}).get('initialized', False)}",
                            title="🧠 System Status",
                            border_style="blue"
                        )
                        console.print(status_panel)
                        
                        # Brain system details
                        brain_stats = data.get('brain_system', {})
                        if brain_stats.get('initialized'):
                            console.print("\n[bold cyan]Brain System Statistics:[/bold cyan]")
                            
                            # Memory statistics
                            memory_stats = brain_stats.get('memory_stats', {})
                            if memory_stats:
                                memory_table = Table(title="Memory Store", show_header=False)
                                memory_table.add_column("Metric", style="yellow")
                                memory_table.add_column("Value", style="green")
                                
                                for key, value in memory_stats.items():
                                    if isinstance(value, (int, float, str)):
                                        memory_table.add_row(key.replace('_', ' ').title(), str(value))
                                
                                console.print(memory_table)
                            
                            # Learning statistics
                            learning_stats = brain_stats.get('learning_stats', {})
                            if learning_stats:
                                learning_table = Table(title="Learning Engine", show_header=False)
                                learning_table.add_column("Metric", style="yellow")
                                learning_table.add_column("Value", style="green")
                                
                                for key, value in learning_stats.items():
                                    if isinstance(value, (int, float, str)):
                                        learning_table.add_row(key.replace('_', ' ').title(), str(value))
                                
                                console.print(learning_table)
                        
                    else:
                        console.print(f"❌ [red]Failed to get status: {response.status}[/red]")
        
        except Exception as e:
            console.print(f"❌ [red]Error: {e}[/red]")
    
    async def explain_decision(self, decision: str, context: Optional[Dict[str, Any]] = None):
        """Explain a decision using the brain system"""
        try:
            payload = {
                "decision": decision,
                "context": context or {}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_url}/explain", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("success"):
                            explanation = result.get("explanation", {})
                            console.print(f"\n[bold blue]🎯 Decision Explanation[/bold blue]")
                            console.print(f"Decision: {decision}")
                            console.print(f"\n[green]Explanation:[/green]")
                            console.print(explanation.get("explanation", "No explanation available"))
                            console.print(f"\n[yellow]Confidence:[/yellow] {explanation.get('confidence', 0):.2f}")
                        else:
                            console.print(f"❌ [red]Explanation failed[/red]")
                    
                    else:
                        console.print(f"❌ [red]Explanation request failed: {response.status}[/red]")
        
        except Exception as e:
            console.print(f"❌ [red]Error: {e}[/red]")
    
    async def make_prediction(self, situation: Dict[str, Any], time_horizon: str = "near_term"):
        """Make a prediction using the brain system"""
        try:
            payload = {
                "situation": situation,
                "time_horizon": time_horizon
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_url}/predict", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("success"):
                            prediction = result.get("prediction", {})
                            console.print(f"\n[bold blue]🔮 Prediction[/bold blue]")
                            console.print(f"Time horizon: {time_horizon}")
                            console.print(f"\n[green]Prediction:[/green]")
                            console.print(prediction.get("prediction", "No prediction available"))
                            console.print(f"\n[yellow]Confidence:[/yellow] {prediction.get('confidence', 0):.2f}")
                            console.print(f"[dim]Based on {prediction.get('based_on_memories', 0)} memories[/dim]")
                        else:
                            console.print(f"❌ [red]Prediction failed[/red]")
                    
                    else:
                        console.print(f"❌ [red]Prediction request failed: {response.status}[/red]")
        
        except Exception as e:
            console.print(f"❌ [red]Error: {e}[/red]")
    
    async def create_plan(self, goal: str, constraints: Optional[List[str]] = None):
        """Create an action plan"""
        try:
            payload = {
                "goal": goal,
                "constraints": constraints or []
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_url}/plan", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("success"):
                            plan = result.get("plan", {})
                            console.print(f"\n[bold blue]📋 Action Plan[/bold blue]")
                            console.print(f"Goal: {goal}")
                            console.print(f"\n[green]Plan:[/green]")
                            
                            plan_text = plan.get("plan", "No plan available")
                            console.print(Markdown(plan_text))
                            
                            console.print(f"\n[yellow]Confidence:[/yellow] {plan.get('confidence', 0):.2f}")
                            if constraints:
                                console.print(f"[dim]Constraints: {', '.join(constraints)}[/dim]")
                        else:
                            console.print(f"❌ [red]Plan creation failed[/red]")
                    
                    else:
                        console.print(f"❌ [red]Plan request failed: {response.status}[/red]")
        
        except Exception as e:
            console.print(f"❌ [red]Error: {e}[/red]")
    
    async def run_test(self):
        """Run system test"""
        try:
            console.print("[bold yellow]🧪 Running Brain AI System Test...[/bold yellow]")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_url}/test") as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("success"):
                            console.print("✅ [green]System test completed successfully![/green]")
                            console.print(f"Test input: {result.get('test_input', {})}")
                            console.print(f"Processing result: {result.get('message', 'No message')}")
                        else:
                            console.print("❌ [red]System test failed[/red]")
                    else:
                        console.print(f"❌ [red]Test request failed: {response.status}[/red]")
        
        except Exception as e:
            console.print(f"❌ [red]Error: {e}[/red]")
    
    async def interactive_mode(self):
        """Start interactive mode"""
        console.print("[bold blue]🧠 Brain-Inspired AI Interactive Mode[/bold blue]")
        console.print("Type 'help' for commands, 'quit' to exit.\n")
        
        while True:
            try:
                user_input = Prompt.ask("\n[bold green]You[/bold green]").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    console.print("👋 Goodbye!")
                    break
                
                elif user_input.lower() == 'help':
                    self._show_interactive_help()
                
                elif user_input.lower() == 'status':
                    await self.get_system_status()
                
                elif user_input.lower() == 'memories':
                    await self.get_memories()
                
                elif user_input.lower() == 'test':
                    await self.run_test()
                
                else:
                    # Process as general input
                    await self.process_input({"user_input": user_input})
            
            except KeyboardInterrupt:
                console.print("\n👋 Goodbye!")
                break
            except Exception as e:
                console.print(f"❌ [red]Error: {e}[/red]")
    
    def _show_interactive_help(self):
        """Show interactive mode help"""
        help_text = """
[bold cyan]Available Commands:[/bold cyan]

[yellow]status[/yellow] - Show system status
[yellow]memories[/yellow] - List current memories
[yellow]test[/yellow] - Run system test
[yellow]help[/yellow] - Show this help
[yellow]quit[/yellow] - Exit interactive mode

[bold cyan]Usage:[/bold cyan]
- Simply type anything to process it through the brain AI
- The system will encode, retrieve memories, and reason about your input
- You'll see active memories and reasoning results
        """
        console.print(Panel(help_text, title="❓ Help", border_style="cyan"))
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(config_path, 'r') as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    return yaml.safe_load(f)
                elif config_path.endswith('.json'):
                    return json.load(f)
                else:
                    raise ValueError("Config file must be .yaml, .yml, or .json")
        except Exception as e:
            console.print(f"❌ [red]Error loading config: {e}[/red]")
            return {}


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="🧠 Brain-Inspired AI Framework CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  brain-ai health                    # Check system health
  brain-ai process '{"text": "hello"}'  # Process input
  brain-ai memories --limit 20       # List memories
  brain-ai interactive               # Interactive mode
  brain-ai status                    # System status
  brain-ai test                      # Run system test
        """
    )
    
    parser.add_argument(
        "--url", 
        default="http://localhost:8000",
        help="Base URL for Brain AI API (default: http://localhost:8000)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Health check command
    health_parser = subparsers.add_parser("health", help="Check system health")
    
    # Process command
    process_parser = subparsers.add_parser("process", help="Process input through brain AI")
    process_parser.add_argument("data", help="Input data (JSON string or file)")
    process_parser.add_argument("--context", help="Context data (JSON string or file)")
    process_parser.add_argument("--file", help="Read input from file")
    
    # Feedback command
    feedback_parser = subparsers.add_parser("feedback", help="Provide feedback")
    feedback_parser.add_argument("memory_id", help="Memory ID")
    feedback_parser.add_argument("feedback_type", help="Feedback type (positive, negative, neutral)")
    feedback_parser.add_argument("--outcome", help="Outcome data (JSON)")
    
    # Memories command
    memories_parser = subparsers.add_parser("memories", help="List memories")
    memories_parser.add_argument("--limit", type=int, default=10, help="Number of memories to show")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Get system status")
    
    # Explain command
    explain_parser = subparsers.add_parser("explain", help="Explain a decision")
    explain_parser.add_argument("decision", help="Decision to explain")
    explain_parser.add_argument("--context", help="Context data (JSON)")
    
    # Predict command
    predict_parser = subparsers.add_parser("predict", help="Make a prediction")
    predict_parser.add_argument("situation", help="Situation description (JSON or file)")
    predict_parser.add_argument("--horizon", default="near_term", help="Time horizon")
    
    # Plan command
    plan_parser = subparsers.add_parser("plan", help="Create action plan")
    plan_parser.add_argument("goal", help="Goal to achieve")
    plan_parser.add_argument("--constraints", nargs="*", help="Constraints")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run system test")
    
    # Interactive command
    interactive_parser = subparsers.add_parser("interactive", help="Start interactive mode")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = BrainAICLI(args.url)
    
    try:
        if args.command == "health":
            await cli.health_check()
        
        elif args.command == "process":
            # Load input data
            if args.file:
                with open(args.file, 'r') as f:
                    data = json.load(f)
            else:
                data = json.loads(args.data)
            
            # Load context if provided
            context = None
            if args.context:
                context = json.loads(args.context)
            
            await cli.process_input(data, context)
        
        elif args.command == "feedback":
            outcome = {}
            if args.outcome:
                outcome = json.loads(args.outcome)
            
            await cli.provide_feedback(args.memory_id, args.feedback_type, outcome)
        
        elif args.command == "memories":
            await cli.get_memories(args.limit)
        
        elif args.command == "status":
            await cli.get_system_status()
        
        elif args.command == "explain":
            context = None
            if args.context:
                context = json.loads(args.context)
            
            await cli.explain_decision(args.decision, context)
        
        elif args.command == "predict":
            if Path(args.situation).exists():
                with open(args.situation, 'r') as f:
                    situation = json.load(f)
            else:
                situation = json.loads(args.situation)
            
            await cli.make_prediction(situation, args.horizon)
        
        elif args.command == "plan":
            await cli.create_plan(args.goal, args.constraints)
        
        elif args.command == "test":
            await cli.run_test()
        
        elif args.command == "interactive":
            await cli.interactive_mode()
    
    except json.JSONDecodeError as e:
        console.print(f"❌ [red]Invalid JSON: {e}[/red]")
    except FileNotFoundError as e:
        console.print(f"❌ [red]File not found: {e}[/red]")
    except Exception as e:
        console.print(f"❌ [red]Unexpected error: {e}[/red]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n👋 Goodbye!")
    except Exception as e:
        console.print(f"❌ [red]Fatal error: {e}[/red]")
        sys.exit(1)