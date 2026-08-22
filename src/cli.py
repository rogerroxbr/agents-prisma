import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from src.agents.orchestrator_langgraph import MainStateGraph
from src.agents.state import PRISMAState

app = typer.Typer(help="Agents-Prisma CLI: Multi-agent system for systematic reviews")
console = Console()


@app.command()
def run(
    query: str = typer.Option(..., "--query", "-q", help="Search query for scientific databases"),
    max_results: int = typer.Option(50, "--max-results", "-m", help="Maximum number of results to fetch per database"),
):
    """
    Run the full PRISMA systematic review pipeline.
    """
    console.print(f"[bold green]Starting PRISMA Pipeline[/bold green]")
    console.print(f"Query: [cyan]{query}[/cyan]")
    console.print(f"Max Results per source: [cyan]{max_results}[/cyan]")

    graph = MainStateGraph(total_target=max_results)
    app_run = graph.compile()

    initial_state = PRISMAState(
        project_id="cli-run-001",
        query=query,
        max_results_per_source=max_results,
    )

    console.print("[yellow]Running pipeline... this might take a while.[/yellow]")
    
    # Run the graph synchronously
    try:
        final_state = app_run.invoke(initial_state)
        
        console.print("[bold green]Pipeline completed successfully![/bold green]")
        
        ident = final_state.get("identification", {})
        screen = final_state.get("screening", {})
        read = final_state.get("eligibility", {})
        
        console.print("\n=== Summary ===")
        if ident:
            console.print(f"Total articles found: {getattr(ident, 'total_found', 'N/A')}")
        if screen:
            console.print(f"Articles included after screening: {getattr(screen, 'included_count', 'N/A')}")
        if read:
            console.print(f"Articles passing full-text read: {len(getattr(read, 'extracted_data', []))}")
            
        console.print("\nCheck the [cyan]outputs/reports/[/cyan] directory for the final markdown and JSON reports.")
            
    except Exception as e:
        console.print(f"[bold red]Pipeline failed with error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def status(project_id: str = typer.Option(..., "--project-id", "-p", help="Project ID to check")):
    """
    Check the status of a project. (Note: Currently requires database setup for persistence to work fully).
    """
    console.print(f"Checking status for project: [cyan]{project_id}[/cyan]")
    console.print("[yellow]Note: Full state persistence is required to track status of async runs. The API uses PostgreSQL for this.[/yellow]")


if __name__ == "__main__":
    app()
