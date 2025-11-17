"""
MCP Server integration tools
"""
import requests
from typing import Dict, Any, Optional


class MCPTools:
    """
    Tools for interacting with MCP Server (Render).
    Wraps HTTP calls to the MCP API.
    """
    
    def __init__(self, server_url: str = "https://mcp-aidev.onrender.com"):
        """
        Initialize MCP tools.
        
        Args:
            server_url: Base URL of the MCP server
        """
        self.server_url = server_url.rstrip("/")
    
    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool on the MCP server.
        
        Args:
            tool_name: Name of the MCP tool
            arguments: Tool arguments
            
        Returns:
            MCP server response
        """
        url = f"{self.server_url}/mcp/execute"
        payload = {
            "tool": tool_name,
            "arguments": arguments
        }
        
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        return response.json()
    
    def create_project(self, name: str, description: str = "", preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a new project in MCP.
        
        Args:
            name: Project name
            description: Project description
            preferences: Optional PRP preferences
            
        Returns:
            Response with project_id
        """
        args = {"name": name, "description": description}
        if preferences:
            args["preferences"] = preferences
        return self._execute_tool("create_project", args)
    
    def save_phase(
        self,
        project_id: str,
        phase_number: int,
        title: str,
        specs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save phase specifications to MCP.
        
        Args:
            project_id: UUID of the project
            phase_number: Phase number
            title: Phase title
            specs: Phase specifications
            
        Returns:
            Response with phase_id
        """
        return self._execute_tool(
            "save_phase",
            {
                "project_id": project_id,
                "phase_number": phase_number,
                "title": title,
                "specs": specs
            }
        )
    
    def get_phase(self, project_id: str, phase_number: int) -> Dict[str, Any]:
        """
        Get phase specifications from MCP.
        
        Args:
            project_id: UUID of the project
            phase_number: Phase number to retrieve
            
        Returns:
            Phase specifications
        """
        return self._execute_tool(
            "get_phase",
            {"project_id": project_id, "phase_number": phase_number}
        )
    
    def update_progress(
        self,
        project_id: str,
        phase_number: int,
        status: str,
        progress_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update phase progress in MCP.
        
        Args:
            project_id: UUID of the project
            phase_number: Phase number
            status: New status (in_progress, completed)
            progress_data: Optional progress information
            
        Returns:
            Updated phase info
        """
        args = {
            "project_id": project_id,
            "phase_number": phase_number,
            "status": status
        }
        if progress_data:
            args["progress_data"] = progress_data
        
        return self._execute_tool("update_progress", args)
    
    def health_check(self) -> bool:
        """
        Check if MCP server is healthy.
        
        Returns:
            True if server is healthy
        """
        try:
            response = requests.get(f"{self.server_url}/health", timeout=10)
            return response.status_code == 200
        except Exception:
            return False

