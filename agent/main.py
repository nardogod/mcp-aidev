"""
Main entry point for the LangGraph Agent
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.state import AgentState
from agent.graph import create_agent_graph
from agent.config import config
from agent.tools import MCPTools


def run_agent(
    project_name: str,
    project_description: str = "",
    max_phases: int = None
) -> AgentState:
    """
    Run the LangGraph agent to plan and save project phases.
    
    Args:
        project_name: Name of the project
        project_description: Description of what to build
        max_phases: Maximum number of phases to plan (optional)
        
    Returns:
        Final agent state with all planned phases
        
    Example:
        result = run_agent(
            "wpp-bot",
            "WhatsApp bot with automatic responses and TDD security"
        )
        print(f"Project ID: {result.project_id}")
        print(f"Phases planned: {len(result.phases)}")
    """
    # Update config if max_phases provided
    if max_phases:
        config.max_phases = max_phases
    
    # Validate config
    config.validate()
    
    # Check MCP server health
    mcp = MCPTools(config.mcp_server_url)
    if not mcp.health_check():
        print(f"Warning: MCP server at {config.mcp_server_url} is not responding")
    
    # Create initial state
    initial_state = AgentState(
        project_name=project_name,
        project_description=project_description
    )
    
    # Create and run the graph
    graph = create_agent_graph()
    
    print(f"Starting agent for project: {project_name}")
    print(f"Using LLM provider: {config.llm_provider}")
    print(f"MCP Server: {config.mcp_server_url}")
    print("-" * 50)
    
    # Run the agent
    result = graph.invoke(initial_state)
    
    # LangGraph returns dict, convert back to AgentState if needed
    if isinstance(result, dict):
        final_state = AgentState.from_dict(result)
    else:
        final_state = result
    
    # Print summary
    print("-" * 50)
    print(f"Agent completed!")
    print(f"Project ID: {final_state.project_id}")
    print(f"Phases planned: {len(final_state.phases)}")
    
    for phase in final_state.phases:
        print(f"  Phase {phase.number}: {phase.title} [{phase.status}]")
    
    if final_state.error:
        print(f"Error: {final_state.error}")
    
    return final_state


def interactive_agent():
    """
    Interactive mode for the agent.
    """
    print("=" * 50)
    print("MCP-AIDev LangGraph Agent")
    print("=" * 50)
    
    project_name = input("Project name: ").strip()
    if not project_name:
        print("Project name is required")
        return
    
    project_description = input("Project description: ").strip()
    
    max_phases_input = input("Max phases (default 3): ").strip()
    max_phases = int(max_phases_input) if max_phases_input else 3
    
    print("\n")
    result = run_agent(project_name, project_description, max_phases)
    
    return result


if __name__ == "__main__":
    interactive_agent()

