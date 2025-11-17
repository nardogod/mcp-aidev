"""
Business logic layer for project and phase management.
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

from database.models import Project, Phase


class ProjectService:
    """
    Service class for managing projects and phases.
    """
    
    def __init__(self, db: Session):
        """
        Initialize service with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def create_project(self, name: str, description: str = None) -> Dict[str, Any]:
        """
        Create a new project.
        
        Args:
            name: Project name
            description: Optional project description
            
        Returns:
            Dictionary with project info and success message
        """
        project = Project(name=name, description=description)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        
        return {
            "project_id": project.id,
            "name": project.name,
            "description": project.description,
            "status": project.status,
            "created_at": project.created_at.isoformat(),
            "message": f"Project '{name}' created successfully"
        }
    
    def save_phase(
        self,
        project_id: str,
        phase_number: int,
        title: str,
        specs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Save phase specifications for a project.
        
        Args:
            project_id: UUID of the project
            phase_number: Phase number (1, 2, 3, etc.)
            title: Phase title
            specs: Dictionary containing phase specifications
            
        Returns:
            Dictionary with phase info and success message
        """
        # Verify project exists
        project = self.db.query(Project).filter_by(id=project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Check if phase already exists
        existing = self.db.query(Phase).filter_by(
            project_id=project_id,
            phase_number=phase_number
        ).first()
        
        if existing:
            # Update existing phase
            existing.title = title
            existing.specs = specs
            phase = existing
        else:
            # Create new phase
            phase = Phase(
                project_id=project_id,
                phase_number=phase_number,
                title=title,
                specs=specs
            )
            self.db.add(phase)
        
        self.db.commit()
        self.db.refresh(phase)
        
        return {
            "phase_id": phase.id,
            "project_id": phase.project_id,
            "phase_number": phase.phase_number,
            "title": phase.title,
            "status": phase.status,
            "message": f"Phase {phase_number} saved successfully"
        }
    
    def get_phase(self, project_id: str, phase_number: int) -> Dict[str, Any]:
        """
        Retrieve phase specifications.
        
        Args:
            project_id: UUID of the project
            phase_number: Phase number to retrieve
            
        Returns:
            Dictionary with complete phase information
            
        Raises:
            ValueError: If phase not found
        """
        phase = self.db.query(Phase).filter_by(
            project_id=project_id,
            phase_number=phase_number
        ).first()
        
        if not phase:
            raise ValueError(f"Phase {phase_number} not found for project {project_id}")
        
        return {
            "phase_id": phase.id,
            "project_id": phase.project_id,
            "phase_number": phase.phase_number,
            "title": phase.title,
            "specs": phase.specs,
            "status": phase.status,
            "progress_data": phase.progress_data,
            "created_at": phase.created_at.isoformat(),
            "updated_at": phase.updated_at.isoformat()
        }
    
    def update_progress(
        self,
        project_id: str,
        phase_number: int,
        status: str,
        progress_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update phase progress after implementation.
        
        Args:
            project_id: UUID of the project
            phase_number: Phase number to update
            status: New status (in_progress, completed)
            progress_data: Optional dictionary with progress information
            
        Returns:
            Dictionary with updated phase info
            
        Raises:
            ValueError: If phase not found
        """
        phase = self.db.query(Phase).filter_by(
            project_id=project_id,
            phase_number=phase_number
        ).first()
        
        if not phase:
            raise ValueError(f"Phase {phase_number} not found for project {project_id}")
        
        phase.status = status
        if progress_data:
            phase.progress_data = progress_data
        
        self.db.commit()
        self.db.refresh(phase)
        
        return {
            "phase_id": phase.id,
            "phase_number": phase.phase_number,
            "status": phase.status,
            "progress_data": phase.progress_data,
            "message": f"Phase {phase_number} progress updated to '{status}'"
        }
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all projects.
        
        Returns:
            List of project dictionaries
        """
        projects = self.db.query(Project).all()
        
        return [
            {
                "project_id": p.id,
                "name": p.name,
                "description": p.description,
                "status": p.status,
                "created_at": p.created_at.isoformat(),
                "phases_count": len(p.phases)
            }
            for p in projects
        ]
