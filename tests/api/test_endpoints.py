"""Tests for FastAPI endpoints."""

from fastapi.testclient import TestClient

from src.api.server import app

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_run_project():
    """Test starting a project pipeline."""
    response = client.post(
        "/api/v1/projects/run",
        json={"query": "test query", "max_results": 10},
    )
    assert response.status_code == 200
    data = response.json()
    assert "project_id" in data
    assert data["status"] == "pending"


def test_get_project_status():
    """Test getting a project status."""
    project_id = "test-project-123"
    response = client.get(f"/api/v1/projects/{project_id}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == project_id
    assert data["status"] == "in_progress"


def test_export_endpoints():
    """Test export endpoints."""
    project_id = "test-project-123"
    
    response_md = client.get(f"/api/v1/projects/{project_id}/export/markdown")
    assert response_md.status_code == 200
    
    response_json = client.get(f"/api/v1/projects/{project_id}/export/json")
    assert response_json.status_code == 200
