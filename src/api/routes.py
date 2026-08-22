"""API Routes for the PRISMA pipeline."""

import uuid
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Path
from pydantic import BaseModel

from src.agents.orchestrator_langgraph import MainStateGraph
from src.agents.state import PRISMAState
# Mocking a DB interaction for the project status in this example.
# You would integrate with src.db.async_session here.

router = APIRouter(tags=["Projects"])


class RunProjectRequest(BaseModel):
    query: str
    max_results: int = 50


class ProjectResponse(BaseModel):
    project_id: str
    status: str
    message: str


def run_pipeline_task(project_id: str, query: str, max_results: int):
    """Background task to run the LangGraph pipeline."""
    print(f"[BACKGROUND TASK] Starting pipeline for {project_id}")
    graph = MainStateGraph(total_target=max_results)
    app_run = graph.compile()

    initial_state = PRISMAState(
        project_id=project_id,
        query=query,
        max_results_per_source=max_results,
    )

    try:
        # In a real scenario with DB, we would update DB to "running" here
        final_state = app_run.invoke(initial_state)
        # And update DB to "completed" here, saving artifacts
        print(f"[BACKGROUND TASK] Pipeline {project_id} completed successfully.")
    except Exception as e:
        print(f"[BACKGROUND TASK] Pipeline {project_id} failed: {e}")
        # Update DB to "error" here


@router.post("/projects/run", response_model=ProjectResponse)
async def run_project(request: RunProjectRequest, background_tasks: BackgroundTasks):
    """
    Start the PRISMA pipeline asynchronously.
    Returns a project ID that can be used to poll the status.
    """
    project_id = str(uuid.uuid4())
    
    # Normally, you would insert a new Project into PostgreSQL here.
    
    background_tasks.add_task(
        run_pipeline_task, 
        project_id=project_id, 
        query=request.query, 
        max_results=request.max_results
    )
    
    return ProjectResponse(
        project_id=project_id,
        status="pending",
        message="Pipeline execution started in the background."
    )


@router.get("/projects/{project_id}/status")
async def get_project_status(project_id: str = Path(..., title="The ID of the project")):
    """
    Get the current status of a project.
    """
    # Here you would query the PostgreSQL DB for the Phase/Project status.
    # For now, returning a mock response.
    return {
        "project_id": project_id,
        "status": "in_progress",
        "details": "Database integration is required to fetch real-time status."
    }


@router.get("/projects/{project_id}/export/markdown")
async def export_markdown(project_id: str = Path(...)):
    """
    Export the synthesis output as a Markdown file.
    """
    # Fetch from SynthesisOutput table in DB
    return {"message": "Export functionality requires DB integration for artifact retrieval."}


@router.get("/projects/{project_id}/export/json")
async def export_json(project_id: str = Path(...)):
    """
    Export the synthesis output as JSON.
    """
    # Fetch from SynthesisOutput table in DB
    return {"message": "Export functionality requires DB integration for artifact retrieval."}
