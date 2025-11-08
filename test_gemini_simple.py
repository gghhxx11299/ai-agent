#!/usr/bin/env python3
"""Quick test to verify Gemini is working"""

import asyncio
from src.integrations.gemini import GeminiIntegration
from rich.console import Console

console = Console()

async def test_gemini():
    console.print("\n[bold cyan]Testing Gemini Configuration[/bold cyan]\n")

    try:
        gemini = GeminiIntegration()
        console.print("[green]✓ Gemini initialized successfully[/green]")

        # Test simple query
        console.print("\n[yellow]Testing simple query...[/yellow]")
        response = await gemini.answer_directly("What is NDVI in one sentence?")

        console.print("[green]✓ Gemini is working![/green]")
        console.print(f"\n[cyan]Response:[/cyan] {response}\n")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]\n")

if __name__ == "__main__":
    asyncio.run(test_gemini())
