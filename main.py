#!/usr/bin/env python3
"""
Gemini Regional Agent - Terminal Chatbot
A conversational AI assistant with real-time capabilities
"""

import asyncio
import sys
from rich.console import Console
from config.config import validate_config
from src.orchestrator import Orchestrator

console = Console()


def display_banner():
    """Display welcome banner"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              ✨  Multi-AI Agent System  🤖                ║
║                                                           ║
║         Your AI Assistant with Real-Time Data             ║
║                                                           ║
║    Data Sources: Web Search • Weather • Agriculture       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")
    console.print("Powered by Gemini AI with automatic fallback to Groq/OpenRouter\n", style="dim")


def display_help():
    """Display help information"""
    console.print("\n[bold yellow]💬 Chat with AI - Example Conversations:[/bold yellow]\n")

    console.print("[bold cyan]Weather Questions (Any Location):[/bold cyan]")
    console.print("[dim]  You:[/dim] [white]What's the weather like in London right now?[/white]")
    console.print("[dim]  You:[/dim] [white]Will it rain in Tokyo this week?[/white]")
    console.print("[dim]  You:[/dim] [white]What's the temperature in New York?[/white]")

    console.print("\n[bold cyan]Agriculture & Farming (Global):[/bold cyan]")
    console.print("[dim]  You:[/dim] [white]What crops should I plant in spring?[/white]")
    console.print("[dim]  You:[/dim] [white]Tell me about soil preparation for maize[/white]")
    console.print("[dim]  You:[/dim] [white]What are drought-resistant crops?[/white]")

    console.print("\n[bold cyan]Current Events & Research:[/bold cyan]")
    console.print("[dim]  You:[/dim] [white]What are the latest farming techniques in 2025?[/white]")
    console.print("[dim]  You:[/dim] [white]Tell me about recent AI developments[/white]")
    console.print("[dim]  You:[/dim] [white]What's the latest news on climate change?[/white]")

    console.print("\n[bold cyan]General Knowledge:[/bold cyan]")
    console.print("[dim]  You:[/dim] [white]What is NDVI and why is it important?[/white]")
    console.print("[dim]  You:[/dim] [white]Explain crop rotation benefits[/white]")
    console.print("[dim]  You:[/dim] [white]How does satellite imagery help farmers?[/white]")

    console.print("\n[bold cyan]Code Generation:[/bold cyan]")
    console.print("[dim]  You:[/dim] [white]Generate a PyQGIS script for satellite processing[/white]")
    console.print("[dim]  You:[/dim] [white]I need a script to calculate NDVI from Landsat[/white]")

    console.print("\n[bold cyan]🔧 System Commands:[/bold cyan]")
    console.print("[cyan]  help[/cyan]  - Show this help menu")
    console.print("[cyan]  clear[/cyan] - Clear the screen")
    console.print("[cyan]  exit[/cyan]  - Exit the chat")

    console.print("\n[yellow]✨ How It Works:[/yellow]")
    console.print("[dim]  • I analyze your question[/dim]")
    console.print("[dim]  • I fetch real-time data when needed (web, weather, agriculture)[/dim]")
    console.print("[dim]  • I synthesize everything into a clear answer[/dim]")
    console.print("[dim]  • Just ask naturally - I handle the rest![/dim]\n")


async def main():
    """Main application loop"""
    # Validate configuration
    validate_config()

    # Initialize orchestrator
    orchestrator = Orchestrator()

    # Display welcome banner
    display_banner()
    console.print(f"[white]👋 Hi! I'm your multi-AI assistant with real-time capabilities.[/white]")
    console.print(f"[dim]Using: {orchestrator.ai_name} (with automatic fallback to ensure reliability)[/dim]")
    console.print("[dim]I can search the web, check weather anywhere in the world, and provide insights.[/dim]")
    console.print("[dim]Just chat with me naturally - I'll fetch any data I need automatically![/dim]\n")
    console.print("[yellow]💡 Tip:[/yellow] [dim]Type 'help' for examples, 'exit' to quit.[/dim]\n")

    # Main chat loop
    while True:
        try:
            # Get user input
            user_input = console.input("[cyan]You:[/cyan] ").strip()

            # Skip empty input
            if not user_input:
                continue

            # Handle special commands
            if user_input.lower() in ['exit', 'quit']:
                console.print("\n[yellow]👋 Goodbye! Have a great day![/yellow]\n")
                break

            if user_input.lower() == 'help':
                display_help()
                continue

            if user_input.lower() in ['clear', 'cls']:
                console.clear()
                display_banner()
                continue

            # Process the query with Gemini
            response = await orchestrator.process_query(user_input)

            # Display Gemini's response
            console.print("\n[bold cyan]✨ AI:[/bold cyan]\n")
            console.print(response)
            console.print()

        except EOFError:
            # Handle EOF (when stdin is closed or Ctrl+D is pressed)
            console.print("\n\n[yellow]👋 Goodbye! (EOF detected)[/yellow]\n")
            break
        except KeyboardInterrupt:
            console.print("\n\n[yellow]👋 Goodbye![/yellow]\n")
            break
        except Exception as e:
            console.print(f"\n[red]❌ Sorry, I encountered an error: {e}[/red]\n")
            if '--debug' in sys.argv:
                console.print_exception()
            # Don't break on general exceptions, allow retry
            continue


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye![/yellow]\n")
        sys.exit(0)
