"""
LangGraph workflow definition
"""
from langgraph.graph import StateGraph, END
from typing import Literal

from .state import AgentState
from .nodes import plan_node, execute_node, review_node
from .nodes_brainstorm import brainstorm_node


def should_continue(state: AgentState) -> Literal["plan", END]:
    """Router function to decide next node"""
    if state.error or not state.should_continue:
        return END
    return "plan"


def create_agent_graph():
    """
    Create the LangGraph workflow for the agent.
    
    The graph follows this flow (MCP STANDARD):
    1. Brainstorm: Complete analysis BEFORE planning (FIRST STEP!)
    2. Plan: Generate phase specs using LLM (uses brainstorm insights)
    3. Execute: Save phase to MCP server
    4. Review: Analyze results and decide next action
    5. Loop or End
    
    Returns:
        Compiled LangGraph workflow
    """
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("brainstorm", brainstorm_node)  # FIRST: Brainstorm
    workflow.add_node("plan", plan_node)
    workflow.add_node("execute", execute_node)
    workflow.add_node("review", review_node)
    
    # Set entry point to brainstorm (MCP standard)
    workflow.set_entry_point("brainstorm")
    
    # Add edges
    workflow.add_edge("brainstorm", "plan")  # Brainstorm -> Plan
    workflow.add_edge("plan", "execute")
    workflow.add_edge("execute", "review")
    
    # Add conditional edge from review
    workflow.add_conditional_edges(
        "review",
        should_continue,
        {
            "plan": "plan",
            END: END
        }
    )
    
    # Compile the graph
    app = workflow.compile()
    
    return app

