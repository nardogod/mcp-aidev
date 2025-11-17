"""
Tests for Phase 3: MCP Protocol Implementation

TDD - RED Phase: These tests should FAIL initially
"""

import pytest
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp.tools import MCPTools
from mcp.protocol import MCPProtocol
from database.connection import init_db, get_db, clear_db


@pytest.fixture
def mcp_tools():
    """Provide MCPTools instance"""
    return MCPTools()


@pytest.fixture
def mcp_protocol():
    """Provide MCPProtocol instance with database"""
    init_db(":memory:")
    db = next(get_db())
    yield MCPProtocol(db)
    clear_db()


class TestMCPToolDefinitions:
    """Test MCP tool schema definitions"""
    
    def test_get_all_tools_returns_list(self, mcp_tools):
        """Should return list of tool definitions"""
        tools = mcp_tools.get_all_tools()
        
        assert isinstance(tools, list)
        assert len(tools) == 4  # create_project, save_phase, get_phase, update_progress
    
    def test_tool_has_required_fields(self, mcp_tools):
        """Each tool should have name, description, input_schema"""
        tools = mcp_tools.get_all_tools()
        
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool
            assert isinstance(tool["name"], str)
            assert isinstance(tool["description"], str)
            assert isinstance(tool["input_schema"], dict)
    
    def test_create_project_tool_schema(self, mcp_tools):
        """create_project tool should have correct schema"""
        tool = mcp_tools.get_tool("create_project")
        
        assert tool is not None
        assert tool["name"] == "create_project"
        assert "project" in tool["description"].lower()
        
        schema = tool["input_schema"]
        assert schema["type"] == "object"
        assert "name" in schema["properties"]
        assert "description" in schema["properties"]
        assert "name" in schema["required"]
    
    def test_save_phase_tool_schema(self, mcp_tools):
        """save_phase tool should have correct schema"""
        tool = mcp_tools.get_tool("save_phase")
        
        assert tool is not None
        assert tool["name"] == "save_phase"
        
        schema = tool["input_schema"]
        assert "project_id" in schema["properties"]
        assert "phase_number" in schema["properties"]
        assert "title" in schema["properties"]
        assert "specs" in schema["properties"]
        assert schema["properties"]["specs"]["type"] == "object"
    
    def test_get_phase_tool_schema(self, mcp_tools):
        """get_phase tool should have correct schema"""
        tool = mcp_tools.get_tool("get_phase")
        
        assert tool is not None
        assert tool["name"] == "get_phase"
        
        schema = tool["input_schema"]
        assert "project_id" in schema["properties"]
        assert "phase_number" in schema["properties"]
        assert set(schema["required"]) == {"project_id", "phase_number"}
    
    def test_update_progress_tool_schema(self, mcp_tools):
        """update_progress tool should have correct schema"""
        tool = mcp_tools.get_tool("update_progress")
        
        assert tool is not None
        assert tool["name"] == "update_progress"
        
        schema = tool["input_schema"]
        assert "project_id" in schema["properties"]
        assert "phase_number" in schema["properties"]
        assert "status" in schema["properties"]
        assert "progress_data" in schema["properties"]
    
    def test_get_nonexistent_tool_returns_none(self, mcp_tools):
        """Should return None for unknown tool"""
        tool = mcp_tools.get_tool("nonexistent_tool")
        assert tool is None
    
    def test_tool_schemas_are_valid_json_schema(self, mcp_tools):
        """All tool schemas should be valid JSON Schema format"""
        tools = mcp_tools.get_all_tools()
        
        for tool in tools:
            schema = tool["input_schema"]
            # Basic JSON Schema validation
            assert "type" in schema
            assert schema["type"] == "object"
            assert "properties" in schema
            assert isinstance(schema["properties"], dict)


class TestMCPProtocolExecution:
    """Test MCP protocol request execution"""
    
    def test_execute_create_project(self, mcp_protocol):
        """Should execute create_project tool"""
        result = mcp_protocol.execute_tool(
            "create_project",
            {"name": "test-project", "description": "Test"}
        )
        
        assert result["success"] is True
        assert "project_id" in result["data"]
        assert result["data"]["name"] == "test-project"
    
    def test_execute_save_phase(self, mcp_protocol):
        """Should execute save_phase tool"""
        # First create project
        project_result = mcp_protocol.execute_tool(
            "create_project",
            {"name": "phase-test"}
        )
        project_id = project_result["data"]["project_id"]
        
        # Then save phase
        result = mcp_protocol.execute_tool(
            "save_phase",
            {
                "project_id": project_id,
                "phase_number": 1,
                "title": "Setup",
                "specs": {"files": ["main.py"]}
            }
        )
        
        assert result["success"] is True
        assert result["data"]["phase_number"] == 1
        assert result["data"]["status"] == "planned"
    
    def test_execute_get_phase(self, mcp_protocol):
        """Should execute get_phase tool"""
        # Setup: create project and phase
        project_result = mcp_protocol.execute_tool(
            "create_project",
            {"name": "get-test"}
        )
        project_id = project_result["data"]["project_id"]
        
        mcp_protocol.execute_tool(
            "save_phase",
            {
                "project_id": project_id,
                "phase_number": 1,
                "title": "Get Test",
                "specs": {"files": ["app.py"], "tests": ["test_app.py"]}
            }
        )
        
        # Execute get_phase
        result = mcp_protocol.execute_tool(
            "get_phase",
            {"project_id": project_id, "phase_number": 1}
        )
        
        assert result["success"] is True
        assert result["data"]["title"] == "Get Test"
        assert result["data"]["specs"]["files"] == ["app.py"]
    
    def test_execute_update_progress(self, mcp_protocol):
        """Should execute update_progress tool"""
        # Setup
        project_result = mcp_protocol.execute_tool(
            "create_project",
            {"name": "progress-test"}
        )
        project_id = project_result["data"]["project_id"]
        
        mcp_protocol.execute_tool(
            "save_phase",
            {
                "project_id": project_id,
                "phase_number": 1,
                "title": "Progress Test",
                "specs": {}
            }
        )
        
        # Execute update_progress
        result = mcp_protocol.execute_tool(
            "update_progress",
            {
                "project_id": project_id,
                "phase_number": 1,
                "status": "completed",
                "progress_data": {"tests_passed": 10}
            }
        )
        
        assert result["success"] is True
        assert result["data"]["status"] == "completed"
    
    def test_execute_unknown_tool_returns_error(self, mcp_protocol):
        """Should return error for unknown tool"""
        result = mcp_protocol.execute_tool(
            "unknown_tool",
            {"param": "value"}
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "unknown" in result["error"].lower() or "not found" in result["error"].lower()
    
    def test_execute_with_missing_required_params(self, mcp_protocol):
        """Should return error when required params missing"""
        result = mcp_protocol.execute_tool(
            "create_project",
            {}  # Missing required 'name'
        )
        
        assert result["success"] is False
        assert "error" in result
    
    def test_execute_get_phase_not_found(self, mcp_protocol):
        """Should return error when phase not found"""
        project_result = mcp_protocol.execute_tool(
            "create_project",
            {"name": "not-found-test"}
        )
        project_id = project_result["data"]["project_id"]
        
        result = mcp_protocol.execute_tool(
            "get_phase",
            {"project_id": project_id, "phase_number": 99}
        )
        
        assert result["success"] is False
        assert "error" in result


class TestMCPRequestResponse:
    """Test MCP request/response formatting"""
    
    def test_format_tool_list_response(self, mcp_protocol):
        """Should format tool list for MCP response"""
        response = mcp_protocol.list_tools()
        
        assert "tools" in response
        assert isinstance(response["tools"], list)
        assert len(response["tools"]) == 4
    
    def test_format_success_response(self, mcp_protocol):
        """Success response should have correct structure"""
        result = mcp_protocol.execute_tool(
            "create_project",
            {"name": "format-test"}
        )
        
        assert "success" in result
        assert "data" in result
        assert result["success"] is True
    
    def test_format_error_response(self, mcp_protocol):
        """Error response should have correct structure"""
        result = mcp_protocol.execute_tool(
            "create_project",
            {}  # Missing name
        )
        
        assert "success" in result
        assert "error" in result
        assert result["success"] is False
        assert isinstance(result["error"], str)
    
    def test_validate_input_against_schema(self, mcp_protocol):
        """Should validate input matches tool schema"""
        # Valid input
        valid_result = mcp_protocol.execute_tool(
            "create_project",
            {"name": "valid", "description": "test"}
        )
        assert valid_result["success"] is True
        
        # Invalid input (wrong type)
        invalid_result = mcp_protocol.execute_tool(
            "save_phase",
            {
                "project_id": "123",
                "phase_number": "not-a-number",  # Should be int
                "title": "Test",
                "specs": {}
            }
        )
        assert invalid_result["success"] is False
