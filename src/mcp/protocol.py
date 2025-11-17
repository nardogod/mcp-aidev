"""
MCP Protocol Handler for mcp-aidev

Handles request execution and response formatting
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from .tools import MCPTools
from services.project_service import ProjectService


class MCPProtocol:
    """
    Handles MCP protocol requests and responses.
    """
    
    def __init__(self, db: Session):
        """
        Initialize protocol handler.
        
        Args:
            db: Database session for operations
        """
        self.db = db
        self.tools = MCPTools()
        self.service = ProjectService(db)
    
    def list_tools(self) -> Dict[str, Any]:
        """
        List all available tools.
        
        Returns:
            Dictionary with tools list for MCP response
        """
        return {
            "tools": self.tools.get_all_tools()
        }
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with given arguments.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Dictionary of arguments for the tool
            
        Returns:
            Dictionary with success status and data or error
        """
        # Check if tool exists
        tool_def = self.tools.get_tool(tool_name)
        if not tool_def:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found"
            }
        
        # Validate required parameters
        validation_error = self._validate_arguments(tool_def, arguments)
        if validation_error:
            return {
                "success": False,
                "error": validation_error
            }
        
        # Execute the tool
        try:
            result = self._dispatch_tool(tool_name, arguments)
            return {
                "success": True,
                "data": result
            }
        except ValueError as e:
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}"
            }
    
    def _validate_arguments(self, tool_def: Dict[str, Any], arguments: Dict[str, Any]) -> Optional[str]:
        """
        Validate arguments against tool schema.
        
        Args:
            tool_def: Tool definition with schema
            arguments: Arguments to validate
            
        Returns:
            Error message string or None if valid
        """
        schema = tool_def["input_schema"]
        
        # Check required fields
        required = schema.get("required", [])
        for field in required:
            if field not in arguments:
                return f"Missing required parameter: {field}"
        
        # Basic type validation
        properties = schema.get("properties", {})
        for key, value in arguments.items():
            if key in properties:
                expected_type = properties[key].get("type")
                if not self._check_type(value, expected_type):
                    return f"Invalid type for '{key}': expected {expected_type}"
        
        return None
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """
        Check if value matches expected JSON Schema type.
        
        Args:
            value: Value to check
            expected_type: Expected JSON Schema type
            
        Returns:
            True if type matches, False otherwise
        """
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        if expected_type not in type_map:
            return True  # Unknown type, skip validation
        
        return isinstance(value, type_map[expected_type])
    
    def _dispatch_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatch tool execution to appropriate service method.
        
        Args:
            tool_name: Name of tool to execute
            arguments: Tool arguments
            
        Returns:
            Result from service method
        """
        if tool_name == "create_project":
            return self.service.create_project(
                name=arguments["name"],
                description=arguments.get("description")
            )
        
        elif tool_name == "save_phase":
            return self.service.save_phase(
                project_id=arguments["project_id"],
                phase_number=arguments["phase_number"],
                title=arguments["title"],
                specs=arguments["specs"]
            )
        
        elif tool_name == "get_phase":
            return self.service.get_phase(
                project_id=arguments["project_id"],
                phase_number=arguments["phase_number"]
            )
        
        elif tool_name == "update_progress":
            return self.service.update_progress(
                project_id=arguments["project_id"],
                phase_number=arguments["phase_number"],
                status=arguments["status"],
                progress_data=arguments.get("progress_data")
            )
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
