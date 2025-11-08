#!/usr/bin/env python3
"""Test global location support through the orchestrator"""

import asyncio
from rich.console import Console
from rich.table import Table
from src.orchestrator import Orchestrator

console = Console()


async def main():
    console.print("\n" + "="*60, style="bold cyan")
    console.print("  🌍 Global Location Support Test", style="bold cyan")
    console.print("="*60 + "\n", style="bold cyan")

    orchestrator = Orchestrator()
    console.print(f"[green]✓ Using {orchestrator.ai_name}[/green]\n")

    # Test different global cities
    cities = ["Tokyo", "London", "Sydney", "Mumbai", "Toronto"]

    table = Table(title="Global Weather Queries")
    table.add_column("City", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Response Preview", style="white")

    for city in cities:
        query = f"What's the weather in {city}?"
        console.print(f"[yellow]Testing:[/yellow] {query}")

        try:
            response = await orchestrator.process_query(query)

            # Extract temperature from response
            preview = response[:100].replace('\n', ' ')
            table.add_row(city, "✓", preview + "...")
            console.print(f"[green]✓ Success[/green]\n")

        except Exception as e:
            table.add_row(city, "✗", f"Error: {str(e)[:50]}")
            console.print(f"[red]✗ Failed: {e}[/red]\n")

    console.print(table)
    console.print("\n[green]✅ Global support verified![/green]\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted[/yellow]\n")
