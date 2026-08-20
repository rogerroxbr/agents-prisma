"""Main entry point for PRISMA pipeline."""

from src.agents.orchestrator import OrchestratorAgent


def main() -> None:
    """Run the PRISMA systematic review pipeline."""
    # Create orchestrator agent
    agent = OrchestratorAgent()

    # Run pipeline with sample parameters
    results = agent.run_pipeline(
        project_id=1, query="diabetes AND complications", max_results=50
    )

    print("\n=== Pipeline Results ===")
    print(f"Project ID: {results['project_id']}")
    print(f"Query: {results['query']}")
    print(f"Total articles found: {results['total_found']}")
    print(f"Articles screened: {results['screened_count']}")
    print(f"Included articles: {results['included_count']}")
    print("\nSynthesis output:")
    print(results["synthesis"])


if __name__ == "__main__":
    main()
