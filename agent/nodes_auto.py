"""
Automatic Implementation Node for LangGraph

This node actually implements phases by creating files and code.
"""
import json
from typing import Dict, Any

from .state import AgentState
from .implementer import PhaseImplementer, ImplementationResult
from .tools import MCPTools
from .config import config


def implement_node(state: AgentState) -> AgentState:
    """
    Implementation node - actually creates files and implements the phase.
    
    This is different from execute_node which only saves to MCP.
    This node actually generates code and creates files.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state after implementation
    """
    if not state.phases:
        state.error = "No phases to implement"
        return state
    
    current_phase = state.phases[-1]
    
    # Skip if already implemented
    if current_phase.status == "completed":
        state.messages.append({
            "role": "system",
            "content": f"Phase {current_phase.number} already completed, skipping implementation"
        })
        return state
    
    # Get phase specs from MCP if not in state
    phase_specs = None
    if state.project_id:
        mcp = MCPTools(config.mcp_server_url)
        phase_result = mcp.get_phase(state.project_id, current_phase.number)
        
        if phase_result.get("success"):
            phase_specs = phase_result.get("data", {})
        else:
            # Use state phase specs as fallback
            phase_specs = {
                "phase_number": current_phase.number,
                "title": current_phase.title,
                "specs": current_phase.specs
            }
    else:
        # Use state phase specs
        phase_specs = {
            "phase_number": current_phase.number,
            "title": current_phase.title,
            "specs": current_phase.specs
        }
    
    # Get previous phases for context
    previous_phases = []
    if state.project_id:
        mcp = MCPTools(config.mcp_server_url)
        phases_result = mcp.list_project_phases(state.project_id)
        if phases_result.get("success"):
            all_phases = phases_result.get("data", {}).get("phases", [])
            previous_phases = [
                p for p in all_phases 
                if p.get("phase_number", 0) < current_phase.number
                and p.get("status") == "completed"
            ]
    
    # Initialize implementer
    implementer = PhaseImplementer(
        project_path=config.project_base_path,
        llm_provider=config.llm_provider
    )
    
    # Implement the phase
    print(f"\n{'='*60}")
    print(f"IMPLEMENTING PHASE {current_phase.number}: {current_phase.title}")
    print(f"{'='*60}\n")
    
    result: ImplementationResult = implementer.implement_phase(
        phase_specs=phase_specs,
        project_name=state.project_name,
        project_description=state.project_description,
        previous_phases=previous_phases
    )
    
    # Update state based on result
    if result.success:
        current_phase.status = "completed"
        
        # Update progress in MCP
        if state.project_id:
            mcp = MCPTools(config.mcp_server_url)
            progress_data = {
                "files_created": result.files_created,
                "files_updated": result.files_updated,
                "tests_passed": result.tests_passed,
                "tests_failed": result.tests_failed,
                "notes": result.notes
            }
            
            mcp.update_progress(
                state.project_id,
                current_phase.number,
                "completed",
                progress_data
            )
        
        state.messages.append({
            "role": "system",
            "content": f"Phase {current_phase.number} implemented successfully. "
                      f"Created {len(result.files_created)} files, "
                      f"updated {len(result.files_updated)} files. "
                      f"Tests: {result.tests_passed} passed, {result.tests_failed} failed."
        })
        
        print(f"\n✅ Phase {current_phase.number} implemented successfully!")
        print(f"   Files created: {len(result.files_created)}")
        print(f"   Files updated: {len(result.files_updated)}")
        if result.tests_passed > 0 or result.tests_failed > 0:
            print(f"   Tests: {result.tests_passed} passed, {result.tests_failed} failed")
        
    else:
        current_phase.status = "failed"
        error_msg = f"Implementation failed: {', '.join(result.errors)}"
        state.error = error_msg
        
        state.messages.append({
            "role": "system",
            "content": error_msg
        })
        
        print(f"\n❌ Phase {current_phase.number} implementation failed!")
        for error in result.errors:
            print(f"   Error: {error}")
    
    return state

