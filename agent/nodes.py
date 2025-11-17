"""
LangGraph nodes for the agent workflow
"""
import json
from typing import Dict, Any

from .state import AgentState, ProjectPhase
from .llm import get_llm
from .tools import MCPTools
from .config import config


def plan_node(state: AgentState) -> AgentState:
    """
    Planning node - uses LLM to generate phase specifications.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with new phase plan
    """
    llm = get_llm(config.llm_provider)
    
    # Build context
    context = f"""
    Project: {state.project_name}
    Description: {state.project_description}
    Current Phase: {state.current_phase}
    Previous Phases: {len(state.phases)}
    Target Total Phases: {config.max_phases}
    Remaining Phases Needed: {config.max_phases - state.current_phase}
    """
    
    # Add PRP preferences if available
    if state.project_preferences:
        from agent.prp import PRPCollector
        prp_context = PRPCollector.preferences_to_prompt_context(state.project_preferences)
        context += f"\n\nProject Requirements and Preferences (PRP):\n{prp_context}\n"
    
    # Add brainstorm analysis if available (CRITICAL: Use brainstorm insights!)
    if state.brainstorm_data:
        brainstorm_summary = f"""
BRAINSTORM ANALYSIS (Use these insights for planning):
- Core Purpose: {state.brainstorm_data.get('project_understanding', {}).get('core_purpose', 'N/A')}
- Recommended Technologies: {', '.join(state.brainstorm_data.get('technical_analysis', {}).get('recommended_technologies', []))}
- Architecture Pattern: {state.brainstorm_data.get('technical_analysis', {}).get('architecture_pattern', 'N/A')}
- Main Challenges: {', '.join(state.brainstorm_data.get('technical_analysis', {}).get('main_challenges', []))}
- MVP Features: {', '.join(state.brainstorm_data.get('project_scope', {}).get('mvp_features', []))}
- Suggested Phases: {state.brainstorm_data.get('recommendations', {}).get('total_phases_suggested', 'N/A')}
- Phase Breakdown: {', '.join(state.brainstorm_data.get('recommendations', {}).get('phase_breakdown', []))}
- Security Considerations: {', '.join(state.brainstorm_data.get('best_practices', {}).get('security', []))}
- Testing Strategy: {state.brainstorm_data.get('best_practices', {}).get('testing_strategy', 'N/A')}
"""
        context += f"\n{brainstorm_summary}\n"
    
    if state.phases:
        last_phase = state.phases[-1]
        context += f"\nLast Phase: {last_phase.title} (Status: {last_phase.status})"
    
    # Prompt for phase planning
    prompt = f"""
    You are a software architect planning development phases.
    
    {context}
    
    IMPORTANT: We need to plan {config.max_phases} phases total. Currently at phase {state.current_phase + 1} of {config.max_phases}.
    Generate the next phase specification as JSON:
    {{
        "phase_number": {state.current_phase + 1},
        "title": "Phase Title",
        "specs": {{
            "files_to_create": ["list of files"],
            "tests_to_write": ["list of test files"],
            "dependencies": ["required packages"],
            "instructions": "Detailed instructions for implementation"
        }}
    }}
    
    Focus on TDD (Test-Driven Development) with security considerations.
    Return ONLY valid JSON, no other text.
    """
    
    # Get LLM response
    response = llm.invoke(prompt)
    
    # Parse JSON response with better error handling
    try:
        # Debug: ver o que o LLM retornou
        print(f"[DEBUG] LLM Response: {response.content[:500]}")
        
        # Tentar extrair JSON da resposta
        content = response.content.strip()
        
        # Se houver markdown code blocks, remover
        if content.startswith("```"):
            parts = content.split("```")
            # Procurar por bloco json
            for i, part in enumerate(parts):
                if part.strip().startswith("json"):
                    content = part[4:].strip()
                    break
                elif part.strip().startswith("{"):
                    content = part.strip()
                    break
            else:
                # Se não encontrou, pegar o primeiro bloco que não seja vazio
                content = next((p.strip() for p in parts[1:] if p.strip()), content)
        
        # Remover qualquer texto antes do primeiro {
        if "{" in content:
            content = content[content.index("{"):]
        # Remover qualquer texto depois do último }
        if "}" in content:
            content = content[:content.rindex("}") + 1]
        
        phase_data = json.loads(content)
        
        # Validar estrutura esperada
        if "phase_number" not in phase_data or "title" not in phase_data or "specs" not in phase_data:
            raise ValueError("Missing required fields in LLM response")
        
        new_phase = ProjectPhase(
            number=phase_data["phase_number"],
            title=phase_data["title"],
            specs=phase_data["specs"],
            status="planned"
        )
        state.phases.append(new_phase)
        state.current_phase = new_phase.number
        
        state.messages.append({
            "role": "assistant",
            "content": f"Planned phase {new_phase.number}: {new_phase.title}"
        })
        
        print(f"[DEBUG] Successfully parsed phase: {new_phase.title}")
        
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse LLM response as JSON: {e}\nResponse: {response.content[:200]}"
        print(f"[ERROR] {error_msg}")
        state.error = error_msg
        state.messages.append({
            "role": "system",
            "content": f"Error planning phase: {error_msg}"
        })
    except (KeyError, ValueError) as e:
        error_msg = f"Invalid phase data structure: {e}\nResponse: {response.content[:200]}"
        print(f"[ERROR] {error_msg}")
        state.error = error_msg
        state.messages.append({
            "role": "system",
            "content": f"Error planning phase: {error_msg}"
        })
    
    return state


def execute_node(state: AgentState) -> AgentState:
    """
    Execution node - saves phase to MCP server.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state after saving to MCP
    """
    if not state.phases:
        state.error = "No phases to execute"
        return state
    
    mcp = MCPTools(config.mcp_server_url)
    
    # Create project if not exists
    if not state.project_id:
        result = mcp.create_project(
            state.project_name,
            state.project_description,
            state.project_preferences
        )
        if result["success"]:
            state.project_id = result["data"]["project_id"]
            state.messages.append({
                "role": "system",
                "content": f"Created project with ID: {state.project_id}"
            })
        else:
            state.error = f"Failed to create project: {result.get('error')}"
            return state
    
    # Save current phase
    current_phase = state.phases[-1]
    result = mcp.save_phase(
        state.project_id,
        current_phase.number,
        current_phase.title,
        current_phase.specs
    )
    
    if result["success"]:
        current_phase.status = "saved"
        state.messages.append({
            "role": "system",
            "content": f"Saved phase {current_phase.number} to MCP server"
        })
    else:
        state.error = f"Failed to save phase: {result.get('error')}"
    
    return state


def review_node(state: AgentState) -> AgentState:
    """
    Review node - analyzes completed phase and decides next action.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with review results
    """
    if not state.phases:
        state.should_continue = False
        return state
    
    llm = get_llm(config.llm_provider)
    
    current_phase = state.phases[-1]
    
    prompt = f"""
    Review the completed phase:
    
    Project: {state.project_name}
    Phase {current_phase.number}: {current_phase.title}
    Status: {current_phase.status}
    Specs: {json.dumps(current_phase.specs, indent=2)}
    
    IMPORTANT: We need to plan {config.max_phases} phases total.
    Currently completed: {state.current_phase} phases.
    Remaining phases needed: {config.max_phases - state.current_phase}
    
    Provide a brief review and indicate if we should continue to the next phase.
    You MUST continue if current_phase ({state.current_phase}) < max_phases ({config.max_phases}).
    Only stop if we have reached or exceeded max_phases ({config.max_phases}).
    
    Return JSON:
    {{
        "review": "Your review comments",
        "should_continue": true/false,
        "next_phase_focus": "What the next phase should focus on (if continuing)"
    }}
    
    Return ONLY valid JSON.
    """
    
    response = llm.invoke(prompt)
    
    try:
        review_data = json.loads(response.content)
        state.messages.append({
            "role": "assistant",
            "content": f"Review: {review_data.get('review', 'Phase reviewed')}"
        })
        
        # Decide if we should continue
        # PRIORITY: Always check max_phases first, ignore LLM decision if we haven't reached max
        if state.current_phase >= config.max_phases:
            state.should_continue = False
            state.messages.append({
                "role": "system",
                "content": f"Reached max phases limit ({config.max_phases}). Stopping."
            })
        else:
            # Only trust LLM decision if we haven't reached max_phases
            # But prioritize continuing if we're below max_phases
            llm_decision = review_data.get("should_continue", True)
            # Force continue if below max_phases, even if LLM says stop
            if state.current_phase < config.max_phases:
                state.should_continue = True
                if not llm_decision:
                    state.messages.append({
                        "role": "system",
                        "content": f"LLM suggested stopping, but we need {config.max_phases - state.current_phase} more phases. Continuing."
                    })
            else:
                state.should_continue = llm_decision
            
    except json.JSONDecodeError:
        state.messages.append({
            "role": "assistant",
            "content": f"Review completed for phase {current_phase.number}"
        })
        # Don't stop on JSON error if we haven't reached max_phases
        if state.current_phase >= config.max_phases:
            state.should_continue = False
        else:
            state.should_continue = True
            state.messages.append({
                "role": "system",
                "content": f"JSON parse error in review, but continuing to reach max_phases ({config.max_phases}). Current: {state.current_phase}"
            })
    
    return state


def router(state: AgentState) -> str:
    """
    Router function to decide next node based on state.
    
    Args:
        state: Current agent state
        
    Returns:
        Name of next node to execute
    """
    if state.error:
        return "end"
    
    if not state.should_continue:
        return "end"
    
    # If we have a planned phase that's not saved, execute it
    if state.phases and state.phases[-1].status == "planned":
        return "execute"
    
    # If last phase is saved, review it
    if state.phases and state.phases[-1].status == "saved":
        return "review"
    
    # Default: plan next phase
    return "plan"

