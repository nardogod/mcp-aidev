"""
SQLAlchemy models for MCP-AIDev
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


def generate_uuid() -> str:
    """Generate a UUID string for primary keys"""
    return str(uuid.uuid4())


class Project(Base):
    """
    Project model - represents a development project being orchestrated.
    """
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active")
    preferences = Column(JSON, nullable=True)  # PRP: Project preferences and requirements
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship to phases
    phases = relationship("Phase", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, status={self.status})>"


class Phase(Base):
    """
    Phase model - represents a development phase within a project.
    """
    __tablename__ = "phases"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    phase_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    specs = Column(JSON, nullable=False)  # Specifications for this phase
    status = Column(String(50), default="planned")  # planned, in_progress, completed
    progress_data = Column(JSON, nullable=True)  # Progress info from implementation
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship to project
    project = relationship("Project", back_populates="phases")
    
    def __repr__(self):
        return f"<Phase(id={self.id}, project_id={self.project_id}, number={self.phase_number}, title={self.title})>"
