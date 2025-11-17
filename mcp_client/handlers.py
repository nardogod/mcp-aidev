"""
MCP Protocol Handlers for Cursor integration
"""
import json
from typing import Dict, Any, Optional

from agent.main import run_agent
from agent.tools import MCPTools
from agent.config import config


class MCPHandler:
    """
    Handles MCP protocol requests from Cursor.
    Implements JSON-RPC 2.0 over stdio.
    """
    
    def __init__(self):
        """Initialize handler with MCP tools"""
        self.mcp_tools = MCPTools(config.mcp_server_url)
        self.initialized = False
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming MCP request.
        
        Args:
            request: JSON-RPC 2.0 request
            
        Returns:
            JSON-RPC 2.0 response
        """
        # Validate basic structure
        if "method" not in request:
            return self._error_response(
                request.get("id"),
                -32600,
                "Invalid Request: missing method"
            )
        
        method = request["method"]
        params = request.get("params", {})
        request_id = request.get("id")
        
        # Route to appropriate handler
        try:
            if method == "initialize":
                result = self._handle_initialize(params)
            elif method == "tools/list":
                result = self._handle_tools_list()
            elif method == "tools/call":
                result = self._handle_tools_call(params)
            elif method == "notifications/initialized":
                # Notification, no response needed
                return self._success_response(request_id, {})
            else:
                return self._error_response(
                    request_id,
                    -32601,
                    f"Method not found: {method}"
                )
            
            return self._success_response(request_id, result)
            
        except Exception as e:
            return self._error_response(
                request_id,
                -32603,
                f"Internal error: {str(e)}"
            )
    
    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request"""
        self.initialized = True
        
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "mcp-aidev",
                "version": "0.1.0"
            }
        }
    
    def _handle_tools_list(self) -> Dict[str, Any]:
        """List available tools"""
        tools = [
            {
                "name": "run_agent",
                "description": "Run the LangGraph agent to plan project phases. Creates project in MCP server and generates phase specifications using AI.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "Name of the project"
                        },
                        "project_description": {
                            "type": "string",
                            "description": "Description of what to build"
                        },
                        "max_phases": {
                            "type": "integer",
                            "description": "Maximum number of phases to plan (default: 3)",
                            "default": 3
                        }
                    },
                    "required": ["project_name"]
                }
            },
            {
                "name": "get_phase",
                "description": "Get phase specifications from MCP server for implementation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "UUID of the project"
                        },
                        "phase_number": {
                            "type": "integer",
                            "description": "Phase number to retrieve"
                        }
                    },
                    "required": ["project_id", "phase_number"]
                }
            },
            {
                "name": "list_projects",
                "description": "List all projects in MCP server",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "update_progress",
                "description": "Update phase progress after implementation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "UUID of the project"
                        },
                        "phase_number": {
                            "type": "integer",
                            "description": "Phase number to update"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["in_progress", "completed"],
                            "description": "New status"
                        },
                        "progress_data": {
                            "type": "object",
                            "description": "Optional progress information"
                        }
                    },
                    "required": ["project_id", "phase_number", "status"]
                }
            },
            {
                "name": "health_check",
                "description": "Check if MCP server is healthy",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_project_status",
                "description": "Get comprehensive project status including total phases, completed phases, in-progress phases, current phase, and progress percentage",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "UUID of the project"
                        }
                    },
                    "required": ["project_id"]
                }
            },
            {
                "name": "list_project_phases",
                "description": "List all phases for a project with their status (planned, in_progress, completed)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "UUID of the project"
                        }
                    },
                    "required": ["project_id"]
                }
            },
            {
                "name": "get_current_phase",
                "description": "Get the current phase (first non-completed phase) for a project. Returns None if all phases are completed.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "UUID of the project"
                        }
                    },
                    "required": ["project_id"]
                }
            },
            {
                "name": "execute_agent_command",
                "description": "Execute agent commands from any directory. Runs Python agent commands without needing to change directories.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "enum": ["agent", "server", "api"],
                            "description": "Command to execute: 'agent' (interactive), 'server' (MCP stdio), 'api' (web server)"
                        },
                        "project_name": {
                            "type": "string",
                            "description": "Project name (required if command is 'agent')"
                        },
                        "project_description": {
                            "type": "string",
                            "description": "Project description (optional)"
                        },
                        "max_phases": {
                            "type": "integer",
                            "description": "Maximum phases to plan (default: 3)"
                        }
                    },
                    "required": ["command"]
                }
            }
        ]
        
        return {"tools": tools}
    
    def _handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "run_agent":
            result = self._call_run_agent(arguments)
        elif tool_name == "get_phase":
            result = self._call_get_phase(arguments)
        elif tool_name == "list_projects":
            result = self._call_list_projects()
        elif tool_name == "update_progress":
            result = self._call_update_progress(arguments)
        elif tool_name == "health_check":
            result = self._call_health_check()
        elif tool_name == "get_project_status":
            result = self._call_get_project_status(arguments)
        elif tool_name == "list_project_phases":
            result = self._call_list_project_phases(arguments)
        elif tool_name == "get_current_phase":
            result = self._call_get_current_phase(arguments)
        elif tool_name == "execute_agent_command":
            result = self._call_execute_agent_command(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }
            ]
        }
    
    def _call_run_agent(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Call run_agent"""
        project_name = args["project_name"]
        project_description = args.get("project_description", "")
        max_phases = args.get("max_phases", 3)
        
        result = run_agent(project_name, project_description, max_phases)
        
        return {
            "project_id": result.project_id,
            "project_name": result.project_name,
            "phases_planned": len(result.phases),
            "phases": [
                {
                    "number": p.number,
                    "title": p.title,
                    "status": p.status
                }
                for p in result.phases
            ]
        }
    
    def _call_get_phase(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Call get_phase from MCP server"""
        return self.mcp_tools.get_phase(
            args["project_id"],
            args["phase_number"]
        )
    
    def _call_list_projects(self) -> Dict[str, Any]:
        """List all projects"""
        import requests
        response = requests.get(f"{config.mcp_server_url}/projects")
        return response.json()
    
    def _call_update_progress(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Update phase progress"""
        return self.mcp_tools.update_progress(
            args["project_id"],
            args["phase_number"],
            args["status"],
            args.get("progress_data", {})
        )
    
    def _call_health_check(self) -> Dict[str, Any]:
        """Check MCP server health"""
        is_healthy = self.mcp_tools.health_check()
        return {
            "healthy": is_healthy,
            "server_url": config.mcp_server_url
        }
    
    def _call_get_project_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive project status"""
        import requests
        project_id = args["project_id"]
        response = requests.post(
            f"{config.mcp_server_url}/mcp/execute",
            json={
                "tool": "get_project_status",
                "arguments": {"project_id": project_id}
            }
        )
        result = response.json()
        if result.get("success"):
            return result.get("data", {})
        else:
            raise ValueError(result.get("error", "Unknown error"))
    
    def _call_list_project_phases(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List all phases for a project"""
        import requests
        project_id = args["project_id"]
        response = requests.post(
            f"{config.mcp_server_url}/mcp/execute",
            json={
                "tool": "list_project_phases",
                "arguments": {"project_id": project_id}
            }
        )
        result = response.json()
        if result.get("success"):
            return result.get("data", {})
        else:
            raise ValueError(result.get("error", "Unknown error"))
    
    def _call_get_current_phase(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get current phase for a project"""
        import requests
        project_id = args["project_id"]
        response = requests.post(
            f"{config.mcp_server_url}/mcp/execute",
            json={
                "tool": "get_current_phase",
                "arguments": {"project_id": project_id}
            }
        )
        result = response.json()
        if result.get("success"):
            return result.get("data", {})
        else:
            raise ValueError(result.get("error", "Unknown error"))
    
    def _call_execute_agent_command(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent command from any directory"""
        import subprocess
        import os
        from pathlib import Path
        
        command = args["command"]
        mcp_dir = Path(__file__).parent.parent.resolve()
        
        # Encontra o script wrapper
        wrapper_script = mcp_dir / "mcp_agent.py"
        
        if command == "agent":
            project_name = args.get("project_name")
            if not project_name:
                return {
                    "success": False,
                    "error": "project_name is required for 'agent' command"
                }
            
            project_description = args.get("project_description", "")
            max_phases = args.get("max_phases", 3)
            
            # Executa diretamente via Python
            try:
                import sys
                sys.path.insert(0, str(mcp_dir))
                os.chdir(mcp_dir)
                os.environ["PYTHONPATH"] = str(mcp_dir)
                
                from agent.main import run_agent
                result = run_agent(project_name, project_description, max_phases)
                
                return {
                    "success": True,
                    "project_id": result.project_id,
                    "project_name": result.project_name,
                    "phases_planned": len(result.phases),
                    "message": f"Agent executed successfully. Project ID: {result.project_id}"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        
        elif command == "server":
            return {
                "success": False,
                "error": "Server command should be run directly: python -m mcp_client.server"
            }
        
        elif command == "api":
            return {
                "success": False,
                "error": "API server command should be run directly: uvicorn src.main:app --reload --port 8000"
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown command: {command}"
            }
    
    def _success_response(self, request_id: Any, result: Any) -> Dict[str, Any]:
        """Create success response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
    
    def _error_response(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }

