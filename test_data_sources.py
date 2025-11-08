#!/usr/bin/env python3
"""Test all data sources to ensure they work correctly"""

import asyncio
from rich.console import Console
from rich.table import Table
from src.integrations.web_search import WebSearchIntegration
from src.integrations.regional_data import RegionalDataIntegration

console = Console()


async def test_web_search():
    """Test web search (DuckDuckGo)"""
    console.print("\n[bold yellow]Test 1: Web Search (DuckDuckGo)[/bold yellow]")
    console.print("Testing real-time web search capabilities...\n")

    try:
        web_search = WebSearchIntegration()
        result = await web_search.search("latest AI developments 2025", ["artificial intelligence", "2025"])

        if result['success']:
            console.print("[green]✓ Web search working![/green]")
            if result.get('mock'):
                console.print("[yellow]  ⚠️  Using mock results (duckduckgo-search may not be installed)[/yellow]")
            else:
                console.print(f"  • Query: {result['query']}")
                console.print(f"  • Found {len(result['results'].get('sources', []))} sources")
                if result['results'].get('sources'):
                    console.print(f"  • Top result: {result['results']['sources'][0]['title'][:60]}...")
            return True
        else:
            console.print("[red]✗ Web search failed[/red]")
            return False
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return False


async def test_weather_data():
    """Test weather data retrieval"""
    console.print("\n[bold yellow]Test 2: Weather Data (Open-Meteo)[/bold yellow]")
    console.print("Testing global weather data retrieval...\n")

    test_locations = ["London", "Tokyo", "New York"]
    results = []

    for location in test_locations:
        try:
            regional = RegionalDataIntegration()
            result = await regional.get_weather_data(location)

            if result['success']:
                console.print(f"[green]✓ {location}:[/green] {result['current']['temperature']}°C, {result['current']['description']}")
                results.append(True)
            else:
                console.print(f"[red]✗ {location}: {result.get('error', 'Unknown error')}[/red]")
                results.append(False)
        except Exception as e:
            console.print(f"[red]✗ {location}: {e}[/red]")
            results.append(False)

    success_rate = sum(results) / len(results) * 100
    console.print(f"\n[cyan]Success rate: {success_rate:.0f}%[/cyan]")
    return success_rate > 50


async def test_agricultural_data():
    """Test agricultural data"""
    console.print("\n[bold yellow]Test 3: Agricultural Data[/bold yellow]")
    console.print("Testing agricultural insights...\n")

    try:
        regional = RegionalDataIntegration()
        result = await regional.get_agricultural_data("California", "wheat")

        if result['success']:
            console.print("[green]✓ Agricultural data working![/green]")
            if result.get('mock'):
                console.print("[yellow]  ⚠️  Using mock data (Agriculture API not configured)[/yellow]")
            console.print(f"  • Location: {result['location']}")
            console.print(f"  • Data keys: {', '.join(result['data'].keys())}")
            return True
        else:
            console.print("[red]✗ Agricultural data failed[/red]")
            return False
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return False


async def test_soil_data():
    """Test soil data"""
    console.print("\n[bold yellow]Test 4: Soil Data[/bold yellow]")
    console.print("Testing soil information retrieval...\n")

    try:
        regional = RegionalDataIntegration()
        result = await regional.get_soil_data("TestRegion")

        if result['success']:
            console.print("[green]✓ Soil data working![/green]")
            if result.get('mock'):
                console.print("[yellow]  ⚠️  Using mock data (Real soil API not configured)[/yellow]")
            console.print(f"  • Soil type: {result['data']['soilType']}")
            console.print(f"  • pH: {result['data']['pH']}")
            return True
        else:
            console.print("[red]✗ Soil data failed[/red]")
            return False
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return False


async def test_global_locations():
    """Test weather for various global locations"""
    console.print("\n[bold yellow]Test 5: Global Location Support[/bold yellow]")
    console.print("Testing weather data for diverse global locations...\n")

    test_locations = [
        "Paris", "Sydney", "Mumbai", "Cairo", "São Paulo",
        "Moscow", "Cape Town", "Seoul", "Mexico City", "Dubai"
    ]

    regional = RegionalDataIntegration()
    table = Table(title="Global Weather Test Results")
    table.add_column("Location", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Temperature", style="yellow")
    table.add_column("Conditions", style="blue")

    success_count = 0
    for location in test_locations:
        try:
            result = await regional.get_weather_data(location)
            if result['success']:
                status = "✓"
                temp = f"{result['current']['temperature']}°C"
                conditions = result['current']['description']
                success_count += 1
            else:
                status = "✗"
                temp = "N/A"
                conditions = "Failed"
        except Exception as e:
            status = "✗"
            temp = "N/A"
            conditions = str(e)[:30]

        table.add_row(location, status, temp, conditions)

    console.print(table)
    console.print(f"\n[cyan]Successfully retrieved weather for {success_count}/{len(test_locations)} locations[/cyan]")
    return success_count >= len(test_locations) * 0.7  # 70% success rate


async def main():
    """Run all tests"""
    console.print("\n" + "="*60, style="bold cyan")
    console.print("  🧪 Data Source Integration Tests", style="bold cyan")
    console.print("="*60 + "\n", style="bold cyan")

    results = {}

    # Run all tests
    results["Web Search"] = await test_web_search()
    results["Weather Data"] = await test_weather_data()
    results["Agricultural Data"] = await test_agricultural_data()
    results["Soil Data"] = await test_soil_data()
    results["Global Locations"] = await test_global_locations()

    # Print summary
    console.print("\n" + "="*60, style="bold cyan")
    console.print("  📊 Test Summary", style="bold cyan")
    console.print("="*60 + "\n", style="bold cyan")

    table = Table(show_header=True)
    table.add_column("Test", style="cyan")
    table.add_column("Result", style="green")

    for test_name, result in results.items():
        status = "[green]✓ PASSED[/green]" if result else "[red]✗ FAILED[/red]"
        table.add_row(test_name, status)

    console.print(table)

    # Overall status
    passed = sum(results.values())
    total = len(results)
    console.print(f"\n[bold]Overall: {passed}/{total} tests passed[/bold]")

    if passed == total:
        console.print("[green]✅ All data sources working perfectly![/green]")
    elif passed >= total * 0.7:
        console.print("[yellow]⚠️  Most data sources working. Some issues detected.[/yellow]")
    else:
        console.print("[red]❌ Multiple data sources failing. Check configuration.[/red]")

    console.print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Tests interrupted by user[/yellow]\n")
    except Exception as e:
        console.print(f"\n[red]Test error: {e}[/red]\n")
        import traceback
        traceback.print_exc()
