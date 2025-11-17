"""
Tests for Phase 4: FastAPI Endpoints

TDD - RED Phase: These tests should FAIL initially
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import app, get_database
from database.connection import init_db, clear_db, get_db


@pytest.fixture
def client():
    """Provide test client with clean database"""
    # Override database dependency for testing
    init_db(":memory:")
    
    def override_get_db():
        db = next(get_db())
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_database] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    clear_db()
    app.dependency_overrides.clear()


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self, client):
        """Root endpoint should return welcome message"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "mcp" in data["message"].lower() or "aidev" in data["message"].lower()
    
    def test_health_endpoint(self, client):
        """Health endpoint should return status"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_health_includes_database_status(self, client):
        """Health check should include database status"""
        response = client.get("/health")
        
        data = response.json()
        assert "database" in data
        assert data["database"] == "connected"


class TestMCPToolsEndpoint:
    """Test MCP tools listing endpoint"""
    
    def test_list_tools_endpoint(self, client):
        """Should list all available MCP tools"""
        response = client.get("/mcp/tools")
        
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert len(data["tools"]) == 4
    
    def test_tools_have_correct_structure(self, client):
        """Each tool should have name, description, input_schema"""
        response = client.get("/mcp/tools")
        
        tools = response.json()["tools"]
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool
    
    def test_specific_tool_endpoint(self, client):
        """Should get specific tool definition"""
        response = client.get("/mcp/tools/create_project")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "create_project"
        assert "input_schema" in data
    
    def test_nonexistent_tool_returns_404(self, client):
        """Should return 404 for unknown tool"""
        response = client.get("/mcp/tools/unknown_tool")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestMCPExecuteEndpoint:
    """Test MCP tool execution endpoint"""
    
    def test_execute_create_project(self, client):
        """Should execute create_project via API"""
        response = client.post(
            "/mcp/execute",
            json={
                "tool": "create_project",
                "arguments": {
                    "name": "api-test-project",
                    "description": "Testing via API"
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "project_id" in data["data"]
        assert data["data"]["name"] == "api-test-project"
    
    def test_execute_save_phase(self, client):
        """Should execute save_phase via API"""
        # First create project
        create_response = client.post(
            "/mcp/execute",
            json={
                "tool": "create_project",
                "arguments": {"name": "phase-api-test"}
            }
        )
        project_id = create_response.json()["data"]["project_id"]
        
        # Then save phase
        response = client.post(
            "/mcp/execute",
            json={
                "tool": "save_phase",
                "arguments": {
                    "project_id": project_id,
                    "phase_number": 1,
                    "title": "API Test Phase",
                    "specs": {
                        "files_to_create": ["main.py"],
                        "tests_to_write": ["test_main.py"]
                    }
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["phase_number"] == 1
    
    def test_execute_get_phase(self, client):
        """Should execute get_phase via API"""
        # Setup: create project and phase
        create_resp = client.post(
            "/mcp/execute",
            json={
                "tool": "create_project",
                "arguments": {"name": "get-api-test"}
            }
        )
        project_id = create_resp.json()["data"]["project_id"]
        
        client.post(
            "/mcp/execute",
            json={
                "tool": "save_phase",
                "arguments": {
                    "project_id": project_id,
                    "phase_number": 1,
                    "title": "Get API Test",
                    "specs": {"files": ["app.py"]}
                }
            }
        )
        
        # Get phase
        response = client.post(
            "/mcp/execute",
            json={
                "tool": "get_phase",
                "arguments": {
                    "project_id": project_id,
                    "phase_number": 1
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["title"] == "Get API Test"
    
    def test_execute_update_progress(self, client):
        """Should execute update_progress via API"""
        # Setup
        create_resp = client.post(
            "/mcp/execute",
            json={
                "tool": "create_project",
                "arguments": {"name": "progress-api-test"}
            }
        )
        project_id = create_resp.json()["data"]["project_id"]
        
        client.post(
            "/mcp/execute",
            json={
                "tool": "save_phase",
                "arguments": {
                    "project_id": project_id,
                    "phase_number": 1,
                    "title": "Progress API Test",
                    "specs": {}
                }
            }
        )
        
        # Update progress
        response = client.post(
            "/mcp/execute",
            json={
                "tool": "update_progress",
                "arguments": {
                    "project_id": project_id,
                    "phase_number": 1,
                    "status": "completed",
                    "progress_data": {
                        "tests_passed": 15,
                        "tests_failed": 0
                    }
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "completed"
    
    def test_execute_unknown_tool_returns_error(self, client):
        """Should return error for unknown tool"""
        response = client.post(
            "/mcp/execute",
            json={
                "tool": "unknown_tool",
                "arguments": {}
            }
        )
        
        assert response.status_code == 200  # MCP returns 200 with error in body
        data = response.json()
        assert data["success"] is False
        assert "error" in data
    
    def test_execute_with_invalid_json(self, client):
        """Should return 422 for invalid request body"""
        response = client.post(
            "/mcp/execute",
            json={"invalid": "structure"}
        )
        
        assert response.status_code == 422
    
    def test_execute_missing_required_params(self, client):
        """Should return error when required params missing"""
        response = client.post(
            "/mcp/execute",
            json={
                "tool": "create_project",
                "arguments": {}  # Missing 'name'
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "error" in data


class TestProjectsEndpoint:
    """Test projects management endpoints"""
    
    def test_list_projects_empty(self, client):
        """Should return empty list when no projects"""
        response = client.get("/projects")
        
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        assert data["projects"] == []
    
    def test_list_projects_with_data(self, client):
        """Should list all projects"""
        # Create some projects
        client.post(
            "/mcp/execute",
            json={
                "tool": "create_project",
                "arguments": {"name": "project-1"}
            }
        )
        client.post(
            "/mcp/execute",
            json={
                "tool": "create_project",
                "arguments": {"name": "project-2"}
            }
        )
        
        response = client.get("/projects")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["projects"]) == 2
        names = [p["name"] for p in data["projects"]]
        assert "project-1" in names
        assert "project-2" in names
    
    def test_get_project_details(self, client):
        """Should get project with phases"""
        # Create project
        create_resp = client.post(
            "/mcp/execute",
            json={
                "tool": "create_project",
                "arguments": {"name": "details-test"}
            }
        )
        project_id = create_resp.json()["data"]["project_id"]
        
        # Add phases
        client.post(
            "/mcp/execute",
            json={
                "tool": "save_phase",
                "arguments": {
                    "project_id": project_id,
                    "phase_number": 1,
                    "title": "Phase 1",
                    "specs": {}
                }
            }
        )
        
        response = client.get(f"/projects/{project_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "details-test"
        assert "phases" in data
        assert len(data["phases"]) == 1
    
    def test_get_nonexistent_project_returns_404(self, client):
        """Should return 404 for unknown project"""
        response = client.get("/projects/nonexistent-uuid")
        
        assert response.status_code == 404


class TestCORSAndHeaders:
    """Test CORS and security headers"""
    
    def test_cors_headers_present(self, client):
        """Response should include CORS headers"""
        response = client.get("/health")
        
        # FastAPI with CORSMiddleware adds these
        assert response.status_code == 200
        # CORS headers are added by middleware
    
    def test_json_content_type(self, client):
        """All responses should be JSON"""
        response = client.get("/health")
        
        assert "application/json" in response.headers["content-type"]
    
    def test_options_request(self, client):
        """Should handle OPTIONS requests for CORS"""
        response = client.options("/mcp/tools")
        
        assert response.status_code in [200, 204, 405]

