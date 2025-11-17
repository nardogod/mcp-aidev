"""
Additional MCP Tools for Automatic Execution

These tools enable fully automatic project execution.
"""
from typing import Dict, Any, List, Optional


def get_execute_phase_tool() -> Dict[str, Any]:
    """
    Tool for automatically executing/implementing a phase.
    
    This tool reads phase specifications and actually implements them
    by creating files and generating code.
    """
    return {
        "name": "execute_phase",
        "description": "Automatically implement a phase by creating files and generating code based on phase specifications. This actually creates the code files, not just saves the plan.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "UUID of the project"
                },
                "phase_number": {
                    "type": "integer",
                    "description": "Phase number to implement"
                },
                "project_path": {
                    "type": "string",
                    "description": "Base path where project files should be created (optional, defaults to ./projects/{project_name})"
                }
            },
            "required": ["project_id", "phase_number"]
        }
    }


def get_execute_all_phases_tool() -> Dict[str, Any]:
    """
    Tool for executing all phases of a project automatically.
    """
    return {
        "name": "execute_all_phases",
        "description": "Automatically implement all phases of a project sequentially, from start to finish, without human interaction.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "UUID of the project"
                },
                "project_path": {
                    "type": "string",
                    "description": "Base path where project files should be created (optional)"
                },
                "start_from_phase": {
                    "type": "integer",
                    "description": "Phase number to start from (defaults to 1)"
                }
            },
            "required": ["project_id"]
        }
    }


def get_auto_plan_and_execute_tool() -> Dict[str, Any]:
    """
    Tool for planning and executing a complete project automatically.
    """
    return {
        "name": "auto_plan_and_execute",
        "description": "Plan a new project and automatically implement all phases from start to finish, completely automatically without human interaction.",
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
                    "description": "Maximum number of phases to plan (defaults to 3)"
                },
                "project_path": {
                    "type": "string",
                    "description": "Base path where project files should be created (optional)"
                }
            },
            "required": ["project_name", "project_description"]
        }
    }

