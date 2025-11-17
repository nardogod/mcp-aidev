"""
Brainstorm Node for LangGraph

This node performs a complete brainstorm/analysis of the project
BEFORE starting to plan phases. This is the standard MCP approach.
"""
import json
from typing import Dict, Any

from .state import AgentState
from .llm import get_llm
from .config import config


def brainstorm_node(state: AgentState) -> AgentState:
    """
    Brainstorm node - performs complete analysis of the project BEFORE planning.
    
    This is the FIRST step in the MCP workflow:
    1. Brainstorm: Complete analysis and understanding
    2. Plan: Generate phase specifications
    3. Execute: Save to MCP
    4. Implement: Create code
    5. Review: Analyze results
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with brainstorm analysis
    """
    llm = get_llm(config.llm_provider)
    
    # Build comprehensive context for brainstorm
    context = f"""
Project Name: {state.project_name}
Project Description: {state.project_description}
"""
    
    # Add PRP preferences if available
    if state.project_preferences:
        from agent.prp import PRPCollector
        prp_context = PRPCollector.preferences_to_prompt_context(state.project_preferences)
        context += f"\n\nProject Requirements and Preferences (PRP):\n{prp_context}\n"
    
    # Comprehensive brainstorm prompt
    prompt = f"""
You are an expert software architect performing a COMPLETE BRAINSTORM and ANALYSIS of a new project.

{context}

Perform a comprehensive brainstorm analysis covering:

1. **Project Understanding**
   - What is the core purpose of this project?
   - What problems does it solve?
   - Who are the target users?
   - What are the key features needed?

2. **Technical Analysis**
   - What technologies are most suitable?
   - What architecture patterns fit best?
   - What are the main technical challenges?
   - What dependencies and integrations are needed?

3. **Project Scope**
   - What is in scope vs out of scope?
   - What are the MVP (Minimum Viable Product) features?
   - What can be deferred to future versions?
   - What are the success criteria?

4. **Risk Assessment**
   - What are the main risks?
   - What are potential blockers?
   - What assumptions are being made?
   - What needs validation?

5. **Development Strategy**
   - How should this project be structured?
   - What are logical development phases?
   - What should be built first?
   - What dependencies exist between components?

6. **Best Practices**
   - What security considerations are needed?
   - What testing strategy should be used?
   - What documentation is needed?
   - What deployment considerations exist?

Return your analysis as JSON:
{{
    "project_understanding": {{
        "core_purpose": "What this project does",
        "problems_solved": ["list of problems"],
        "target_users": ["list of users"],
        "key_features": ["list of features"]
    }},
    "technical_analysis": {{
        "recommended_technologies": ["list of technologies"],
        "architecture_pattern": "recommended pattern",
        "main_challenges": ["list of challenges"],
        "dependencies": ["list of dependencies"],
        "integrations": ["list of integrations"]
    }},
    "project_scope": {{
        "in_scope": ["what's included"],
        "out_of_scope": ["what's excluded"],
        "mvp_features": ["MVP features"],
        "future_features": ["future versions"],
        "success_criteria": ["how to measure success"]
    }},
    "risk_assessment": {{
        "main_risks": ["list of risks"],
        "potential_blockers": ["list of blockers"],
        "assumptions": ["list of assumptions"],
        "validation_needed": ["what needs validation"]
    }},
    "development_strategy": {{
        "project_structure": "how to organize",
        "logical_phases": ["list of phase concepts"],
        "build_order": "what to build first",
        "dependencies": "what depends on what"
    }},
    "best_practices": {{
        "security": ["security considerations"],
        "testing_strategy": "testing approach",
        "documentation": "documentation needs",
        "deployment": "deployment considerations"
    }},
    "recommendations": {{
        "total_phases_suggested": <number>,
        "phase_breakdown": ["high-level phase descriptions"],
        "priority_features": ["most important features"],
        "technical_decisions": ["key technical decisions"]
    }}
}}

Return ONLY valid JSON, no other text.
"""
    
    # Get LLM response
    response = llm.invoke(prompt)
    
    # Parse JSON response
    try:
        content = response.content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```"):
            parts = content.split("```")
            for part in parts:
                if part.strip().startswith("json"):
                    content = part[4:].strip()
                    break
                elif part.strip().startswith("{"):
                    content = part.strip()
                    break
            else:
                content = next((p.strip() for p in parts[1:] if p.strip()), content)
        
        # Extract JSON
        if "{" in content:
            content = content[content.index("{"):]
        if "}" in content:
            content = content[:content.rindex("}") + 1]
        
        brainstorm_data = json.loads(content)
        
        # Store brainstorm in state
        if not hasattr(state, 'brainstorm_data'):
            state.brainstorm_data = {}
        state.brainstorm_data = brainstorm_data
        
        # Add to messages
        state.messages.append({
            "role": "assistant",
            "content": f"Brainstorm completed. Analysis suggests {brainstorm_data.get('recommendations', {}).get('total_phases_suggested', 'unknown')} phases."
        })
        
        print("\n" + "=" * 70)
        print("BRAINSTORM COMPLETO - ANALISE DO PROJETO")
        print("=" * 70)
        print(f"\nProposito Principal: {brainstorm_data.get('project_understanding', {}).get('core_purpose', 'N/A')}")
        print(f"\nTecnologias Recomendadas: {', '.join(brainstorm_data.get('technical_analysis', {}).get('recommended_technologies', []))}")
        print(f"\nPadrao de Arquitetura: {brainstorm_data.get('technical_analysis', {}).get('architecture_pattern', 'N/A')}")
        print(f"\nFases Sugeridas: {brainstorm_data.get('recommendations', {}).get('total_phases_suggested', 'N/A')}")
        print(f"\nPrincipais Riscos: {len(brainstorm_data.get('risk_assessment', {}).get('main_risks', []))} identificados")
        print("=" * 70)
        print()
        
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse brainstorm response as JSON: {e}\nResponse: {response.content[:200]}"
        print(f"[ERROR] {error_msg}")
        state.error = error_msg
        state.messages.append({
            "role": "system",
            "content": f"Error in brainstorm: {error_msg}"
        })
    except Exception as e:
        error_msg = f"Brainstorm failed: {str(e)}"
        print(f"[ERROR] {error_msg}")
        state.error = error_msg
        state.messages.append({
            "role": "system",
            "content": error_msg
        })
    
    return state

