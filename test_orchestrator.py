#!/usr/bin/env python3
"""Test the orchestrator with real queries"""

import asyncio
from rich.console import Console
from src.orchestrator import Orchestrator

console = Console()


async def test_query(orchestrator, query_type, query):
    """Test a single query"""
    console.print(f"\n[bold cyan]Test: {query_type}[/bold cyan]")
    console.print(f"[dim]Query: {query}[/dim]\n")

    try:
        response = await orchestrator.process_query(query)
        console.print(f"\n[green]✓ Success![/green]")
        console.print(f"[cyan]Response preview:[/cyan]")
        console.print(f"{response[:300]}...\n" if len(response) > 300 else f"{response}\n")
        return True
    except Exception as e:
        console.print(f"[red]✗ Failed: {e}[/red]\n")
        return False


async def main():
    console.print("\n" + "="*60, style="bold cyan")
    console.print("  🧪 Full Orchestrator Test", style="bold cyan")
    console.print("="*60 + "\n", style="bold cyan")

    # Initialize orchestrator
    orchestrator = Orchestrator()
    console.print(f"[green]✓ Using {orchestrator.ai_name}[/green]\n")

    results = {}

    # Test 1: Simple knowledge query (no external data)
    results["Knowledge Query"] = await test_query(
        orchestrator,
        "Simple Knowledge Query",
        "What is crop rotation?"
    )

    # Test 2: Weather query (requires location data)
    results["Weather Query"] = await test_query(
        orchestrator,
        "Weather Data Query",
        "What's the weather in Paris right now?"
    )

    # Test 3: Current events query (requires web search)
    results["Web Search Query"] = await test_query(
        orchestrator,
        "Current Events Query",
        "What are the latest AI developments in 2025?"
    )

    # Summary
    console.print("="*60, style="bold cyan")
    console.print("  📊 Test Results", style="bold cyan")
    console.print("="*60 + "\n", style="bold cyan")

    for test_name, result in results.items():
        status = "[green]✓ PASSED[/green]" if result else "[red]✗ FAILED[/red]"
        console.print(f"{test_name}: {status}")

    passed = sum(results.values())
    total = len(results)
    console.print(f"\n[bold]{passed}/{total} tests passed[/bold]\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Tests interrupted[/yellow]\n")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]\n")
        import traceback
        traceback.print_exc()
