#!/usr/bin/env python3
"""
Demonstration of AI Fallback System
Shows how the system automatically switches from Gemini to Groq when needed
"""

import asyncio
import sys
from rich.console import Console
from rich.panel import Panel
from config.config import Config
from src.orchestrator import Orchestrator

console = Console()


def print_status():
    """Print current configuration status"""
    console.print("\n" + "="*60, style="bold cyan")
    console.print("  🔄 AI Fallback System Status", style="bold cyan")
    console.print("="*60 + "\n", style="bold cyan")

    # Gemini status
    gemini_status = "✓ Configured" if Config.GEMINI_API_KEY else "✗ Not Set"
    gemini_color = "green" if Config.GEMINI_API_KEY else "red"
    console.print(f"[{gemini_color}]Gemini (Primary):      {gemini_status}[/{gemini_color}]")

    # Groq status
    groq_status = "✓ Configured" if Config.GROQ_API_KEY else "✗ Not Set"
    groq_color = "green" if Config.GROQ_API_KEY else "yellow"
    console.print(f"[{groq_color}]Groq (Fallback #1):    {groq_status}[/{groq_color}]")

    # OpenRouter status
    or_status = "✓ Configured" if Config.OPENROUTER_API_KEY else "✗ Not Set"
    or_color = "green" if Config.OPENROUTER_API_KEY else "dim"
    console.print(f"[{or_color}]OpenRouter (Fallback #2): {or_status}[/{or_color}]")

    console.print()


async def demo_normal_operation():
    """Demo 1: Normal operation with Gemini"""
    console.print("[bold yellow]📋 Demo 1: Normal Operation[/bold yellow]\n")

    try:
        orchestrator = Orchestrator()
        console.print(f"[cyan]Primary AI: {orchestrator.ai_name}[/cyan]\n")

        query = "What is machine learning in one sentence?"
        console.print(f"[dim]Query:[/dim] {query}\n")

        response = await orchestrator.process_query(query)

        console.print(f"\n[green]✓ Success![/green]")
        console.print(f"[dim]AI Used: {orchestrator.ai_name}[/dim]")
        console.print(f"\n[cyan]Response:[/cyan]")
        console.print(Panel(response[:300] + "..." if len(response) > 300 else response))

        return True
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return False


async def demo_fallback_simulation():
    """Demo 2: Simulate Gemini failure to show Groq fallback"""
    console.print("\n[bold yellow]📋 Demo 2: Fallback Simulation[/bold yellow]\n")

    if not Config.GROQ_API_KEY:
        console.print("[yellow]⚠️  Groq API key not configured - cannot demo fallback[/yellow]")
        console.print("\n[cyan]To enable fallback:[/cyan]")
        console.print("  1. Get free key from: https://console.groq.com/keys")
        console.print("  2. Add to .env: GROQ_API_KEY=your_key_here")
        console.print("  3. Re-run this demo\n")
        return False

    console.print("[dim]Simulating Gemini failure...[/dim]\n")

    try:
        orchestrator = Orchestrator()

        # Simulate Gemini failure by forcing it to fail
        class FailingAI:
            async def analyze_query(self, *args, **kwargs):
                raise Exception("Simulated Gemini API failure")

            async def synthesize_response(self, *args, **kwargs):
                raise Exception("Simulated Gemini API failure")

            async def answer_directly(self, *args, **kwargs):
                raise Exception("Simulated Gemini API failure")

        # Replace Gemini with failing version
        if orchestrator.ai_models and orchestrator.ai_models[0][0] == "Gemini":
            orchestrator.ai_models[0] = ("Gemini", FailingAI())

        query = "What is artificial intelligence?"
        console.print(f"[dim]Query:[/dim] {query}\n")

        response = await orchestrator.process_query(query)

        console.print(f"\n[green]✓ Fallback successful![/green]")
        console.print(f"[green]Switched to: {orchestrator.ai_name}[/green]")
        console.print(f"\n[cyan]Response:[/cyan]")
        console.print(Panel(response[:300] + "..." if len(response) > 300 else response))

        return True
    except Exception as e:
        console.print(f"[red]✗ Fallback failed: {e}[/red]")
        return False


async def demo_query_types():
    """Demo 3: Different query types"""
    console.print("\n[bold yellow]📋 Demo 3: Handling Different Query Types[/bold yellow]\n")

    try:
        orchestrator = Orchestrator()

        queries = [
            ("Knowledge", "What is NDVI?"),
            ("Weather", "What's the weather in London?"),
            ("Recent Info", "What are the latest farming techniques?"),
        ]

        for query_type, query in queries:
            console.print(f"\n[cyan]Testing: {query_type}[/cyan]")
            console.print(f"[dim]Query: {query}[/dim]\n")

            response = await orchestrator.process_query(query)

            console.print(f"[green]✓ AI: {orchestrator.ai_name}[/green]")
            console.print(f"[dim]{response[:150]}...[/dim]\n")

        return True
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return False


async def main():
    """Run all demos"""
    console.clear()

    # Print banner
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           🔄  AI Fallback System Demo  🤖                 ║
║                                                           ║
║      Demonstrating Automatic Gemini → Groq Fallback      ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")

    print_status()

    # Check if we have at least one AI configured
    if not (Config.GEMINI_API_KEY or Config.GROQ_API_KEY or Config.OPENROUTER_API_KEY):
        console.print("[red]❌ No AI models configured![/red]")
        console.print("[yellow]Please add at least one API key to .env file[/yellow]\n")
        sys.exit(1)

    # Run demos
    console.print("[bold cyan]Running Demos...[/bold cyan]\n")
    console.print("-" * 60 + "\n")

    await demo_normal_operation()

    console.print("\n" + "-" * 60 + "\n")

    await demo_fallback_simulation()

    console.print("\n" + "-" * 60 + "\n")

    # Summary
    console.print("\n[bold green]✅ Demo Complete![/bold green]\n")

    if not Config.GROQ_API_KEY:
        console.print("[yellow]💡 Next Step: Add Groq API for automatic fallback[/yellow]")
        console.print("   See setup_groq_guide.md for instructions\n")
    else:
        console.print("[green]✓ Full fallback system is active![/green]\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]\n")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Demo error: {e}[/red]\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
