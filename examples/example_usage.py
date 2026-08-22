"""Example usage of the PRISMA Agents pipeline."""

import asyncio

from src.agents.orchestrator_langgraph import MainStateGraph
from src.agents.state import PRISMAState


async def run_example():
    """Run a small example of the PRISMA pipeline."""
    print("Initializing pipeline...")
    graph = MainStateGraph(total_target=5)
    app = graph.compile()
    
    initial_state = PRISMAState(
        project_id="example-001",
        query="hypertension AND mortality",
        max_results_per_source=5,
    )
    
    print("Starting execution (this will run the actual nodes)...")
    # For a real run, this will invoke LLMs and web requests.
    # final_state = app.invoke(initial_state)
    # print(final_state)
    print("Pipeline compilation successful. (Execution skipped in example script).")


if __name__ == "__main__":
    asyncio.run(run_example())
