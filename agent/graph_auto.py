"""
Automatic LangGraph workflow with implementation

This graph includes automatic code generation and file creation.
"""
from langgraph.graph import StateGraph, END
from typing import Literal

from .state import AgentState
from .nodes import plan_node, execute_node, review_node
from .nodes_auto import implement_node
from .nodes_brainstorm import brainstorm_node


def should_continue_auto(state: AgentState) -> Literal["plan", "implement", END]:
    """Router function for automatic workflow"""
    if state.error:
        return END
    
    if not state.should_continue:
        return END
    
    # Check if we have a phase that needs implementation
    if state.phases:
        last_phase = state.phases[-1]
        
        # If phase is saved but not implemented, implement it
        if last_phase.status == "saved":
            return "implement"
        
        # If phase is completed, plan next phase
        if last_phase.status == "completed":
            return "plan"
    
    # Default: plan next phase
    return "plan"


def create_auto_agent_graph():
    """
    Create the automatic LangGraph workflow with implementation.
    
    Flow (MCP STANDARD):
    1. Brainstorm: Complete analysis BEFORE planning (FIRST STEP!)
    2. Plan: Generate phase specs using LLM (uses brainstorm insights)
    3. Execute: Save phase to MCP server
    4. Implement: Actually create files and code
    5. Review: Analyze results and decide next action
    6. Loop or End
    
    Returns:
        Compiled LangGraph workflow with automatic implementation
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("brainstorm", brainstorm_node)  # FIRST: Brainstorm
    workflow.add_node("plan", plan_node)
    workflow.add_node("execute", execute_node)
    workflow.add_node("implement", implement_node)  # Automatic implementation
    workflow.add_node("review", review_node)
    
    # Set entry point to brainstorm (MCP standard)
    workflow.set_entry_point("brainstorm")
    
    # Add edges
    workflow.add_edge("brainstorm", "plan")  # Brainstorm -> Plan
    workflow.add_edge("plan", "execute")
    workflow.add_edge("execute", "implement")  # After saving, implement
    workflow.add_edge("implement", "review")
    
    # Add conditional edge from review
    workflow.add_conditional_edges(
        "review",
        should_continue_auto,
        {
            "plan": "plan",
            "implement": "implement",
            END: END
        }
    )
    
    # Compile the graph
    app = workflow.compile()
    
    return app

