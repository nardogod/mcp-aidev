"""
Agent state management for LangGraph
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass
class ProjectPhase:
    """Represents a development phase"""
    number: int
    title: str
    specs: Dict[str, Any]
    status: str = "planned"  # planned, saved, in_progress, completed
    progress_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AgentState:
    """
    State object for the LangGraph agent.
    Tracks project info, phases, and conversation history.
    """
    # Project info
    project_name: str
    project_description: str = ""
    project_id: Optional[str] = None
    project_preferences: Optional[Dict[str, Any]] = None  # PRP: Project preferences
    
    # Phase tracking
    current_phase: int = 0
    phases: List[ProjectPhase] = field(default_factory=list)
    
    # Conversation history
    messages: List[Dict[str, str]] = field(default_factory=list)
    
    # Agent control
    should_continue: bool = True
    error: Optional[str] = None
    
    # Brainstorm data (PRP analysis)
    brainstorm_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize state to dictionary"""
        return {
            "project_name": self.project_name,
            "project_description": self.project_description,
            "project_id": self.project_id,
            "project_preferences": self.project_preferences,
            "current_phase": self.current_phase,
            "phases": [p.to_dict() for p in self.phases],
            "messages": self.messages,
            "should_continue": self.should_continue,
            "error": self.error,
            "brainstorm_data": self.brainstorm_data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentState":
        """Create state from dictionary"""
        phases_data = data.get("phases", [])
        phases = []
        for p in phases_data:
            if isinstance(p, ProjectPhase):
                phases.append(p)
            elif isinstance(p, dict):
                phases.append(ProjectPhase(**p))
            else:
                # Try to convert
                phases.append(ProjectPhase(**dict(p)))
        return cls(
            project_name=data["project_name"],
            project_description=data.get("project_description", ""),
            project_id=data.get("project_id"),
            project_preferences=data.get("project_preferences"),
            current_phase=data.get("current_phase", 0),
            phases=phases,
            messages=data.get("messages", []),
            should_continue=data.get("should_continue", True),
            error=data.get("error"),
            brainstorm_data=data.get("brainstorm_data")
        )

