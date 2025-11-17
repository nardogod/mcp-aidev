"""
MCP Tool Definitions for mcp-aidev

Defines the schema for each tool following MCP specification
"""

from typing import Dict, Any, List, Optional


class MCPTools:
    """
    Defines MCP tool schemas for the orchestrator.
    """
    
    def __init__(self):
        """Initialize tool definitions"""
        self._tools = self._define_tools()
    
    def _define_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        Define all available MCP tools with their schemas.
        
        Returns:
            Dictionary mapping tool names to their definitions
        """
        return {
            "create_project": {
                "name": "create_project",
                "description": "Creates a new project in MCP orchestrator for tracking development phases",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Unique name for the project"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description of the project"
                        },
                        "preferences": {
                            "type": "object",
                            "description": "Optional PRP (Product Requirements Planning) preferences for the project"
                        }
                    },
                    "required": ["name"]
                }
            },
            "save_phase": {
                "name": "save_phase",
                "description": "Saves phase specifications for a project, including files to create, tests, and instructions",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "UUID of the project"
                        },
                        "phase_number": {
                            "type": "integer",
                            "description": "Phase number (1, 2, 3, etc.)"
                        },
                        "title": {
                            "type": "string",
                            "description": "Title of the phase"
                        },
                        "specs": {
                            "type": "object",
                            "description": "Phase specifications including files, tests, dependencies",
                            "properties": {
                                "files_to_create": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "tests_to_write": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "dependencies": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "instructions": {
                                    "type": "string"
                                }
                            }
                        }
                    },
                    "required": ["project_id", "phase_number", "title", "specs"]
                }
            },
            "get_phase": {
                "name": "get_phase",
                "description": "Retrieves phase specifications for implementation in Cursor",
                "input_schema": {
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
            "update_progress": {
                "name": "update_progress",
                "description": "Updates phase progress after implementation, including test results and status",
                "input_schema": {
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
                            "description": "New status of the phase"
                        },
                        "progress_data": {
                            "type": "object",
                            "description": "Progress information from implementation",
                            "properties": {
                                "files_created": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "tests_passed": {
                                    "type": "integer"
                                },
                                "tests_failed": {
                                    "type": "integer"
                                },
                                "notes": {
                                    "type": "string"
                                }
                            }
                        }
                    },
                    "required": ["project_id", "phase_number", "status"]
                }
            },
            "get_project_status": {
                "name": "get_project_status",
                "description": "Get comprehensive project status including total phases, completed phases, in-progress phases, current phase, and progress percentage",
                "input_schema": {
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
            "list_project_phases": {
                "name": "list_project_phases",
                "description": "List all phases for a project with their status (planned, in_progress, completed)",
                "input_schema": {
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
            "get_current_phase": {
                "name": "get_current_phase",
                "description": "Get the current phase (first non-completed phase) for a project. Returns None if all phases are completed.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "UUID of the project"
                        }
                    },
                    "required": ["project_id"]
                }
            }
        }
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """
        Get all tool definitions as a list.
        
        Returns:
            List of tool definition dictionaries
        """
        return list(self._tools.values())
    
    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific tool definition by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool definition or None if not found
        """
        return self._tools.get(name)
    
    def get_tool_names(self) -> List[str]:
        """
        Get list of all tool names.
        
        Returns:
            List of tool name strings
        """
        return list(self._tools.keys())
