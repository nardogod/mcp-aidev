"""
Tests for Phase 2: Database Layer

TDD - RED Phase: These tests should FAIL initially
"""

import pytest
from datetime import datetime
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.connection import get_db, init_db, clear_db
from database.models import Project, Phase
from services.project_service import ProjectService


@pytest.fixture
def db_session():
    """Provide a clean database session for each test"""
    init_db(":memory:")  # Use in-memory SQLite for tests
    db = next(get_db())
    yield db
    clear_db()


@pytest.fixture
def project_service(db_session):
    """Provide ProjectService instance"""
    return ProjectService(db_session)


class TestDatabaseConnection:
    """Test database connection and initialization"""
    
    def test_init_db_creates_tables(self):
        """Database initialization should create all tables"""
        init_db(":memory:")
        db = next(get_db())
        
        # Check tables exist by querying them
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        assert "projects" in tables
        assert "phases" in tables
    
    def test_get_db_returns_session(self):
        """get_db should return a valid database session"""
        init_db(":memory:")
        db = next(get_db())
        
        assert db is not None
        assert hasattr(db, "add")
        assert hasattr(db, "commit")
        assert hasattr(db, "query")


class TestProjectModel:
    """Test Project model CRUD operations"""
    
    def test_create_project(self, db_session):
        """Should create a new project"""
        project = Project(
            name="test-project",
            description="A test project"
        )
        db_session.add(project)
        db_session.commit()
        
        assert project.id is not None
        assert project.name == "test-project"
        assert project.status == "active"
        assert project.created_at is not None
    
    def test_project_has_uuid_id(self, db_session):
        """Project ID should be a valid UUID string"""
        project = Project(name="uuid-test")
        db_session.add(project)
        db_session.commit()
        
        assert isinstance(project.id, str)
        assert len(project.id) == 36  # UUID format
    
    def test_project_default_status(self, db_session):
        """Project should have 'active' as default status"""
        project = Project(name="status-test")
        db_session.add(project)
        db_session.commit()
        
        assert project.status == "active"
    
    def test_project_timestamps(self, db_session):
        """Project should have created_at and updated_at timestamps"""
        project = Project(name="timestamp-test")
        db_session.add(project)
        db_session.commit()
        
        assert isinstance(project.created_at, datetime)
        assert isinstance(project.updated_at, datetime)
    
    def test_read_project_by_id(self, db_session):
        """Should retrieve project by ID"""
        project = Project(name="read-test")
        db_session.add(project)
        db_session.commit()
        
        fetched = db_session.query(Project).filter_by(id=project.id).first()
        
        assert fetched is not None
        assert fetched.name == "read-test"
    
    def test_update_project(self, db_session):
        """Should update project fields"""
        project = Project(name="update-test")
        db_session.add(project)
        db_session.commit()
        
        project.name = "updated-name"
        project.status = "completed"
        db_session.commit()
        
        fetched = db_session.query(Project).filter_by(id=project.id).first()
        assert fetched.name == "updated-name"
        assert fetched.status == "completed"
    
    def test_delete_project(self, db_session):
        """Should delete project"""
        project = Project(name="delete-test")
        db_session.add(project)
        db_session.commit()
        project_id = project.id
        
        db_session.delete(project)
        db_session.commit()
        
        fetched = db_session.query(Project).filter_by(id=project_id).first()
        assert fetched is None


class TestPhaseModel:
    """Test Phase model CRUD operations"""
    
    def test_create_phase(self, db_session):
        """Should create a phase linked to project"""
        project = Project(name="phase-test")
        db_session.add(project)
        db_session.commit()
        
        phase = Phase(
            project_id=project.id,
            phase_number=1,
            title="Setup Initial",
            specs={"files_to_create": ["main.py"], "tests": ["test_main.py"]}
        )
        db_session.add(phase)
        db_session.commit()
        
        assert phase.id is not None
        assert phase.project_id == project.id
        assert phase.phase_number == 1
        assert phase.status == "planned"
    
    def test_phase_specs_is_json(self, db_session):
        """Phase specs should store and retrieve JSON correctly"""
        project = Project(name="json-test")
        db_session.add(project)
        db_session.commit()
        
        specs = {
            "files_to_create": ["src/main.py", "tests/test_main.py"],
            "dependencies": ["fastapi", "pytest"],
            "instructions": "Setup basic structure"
        }
        
        phase = Phase(
            project_id=project.id,
            phase_number=1,
            title="JSON Test",
            specs=specs
        )
        db_session.add(phase)
        db_session.commit()
        
        fetched = db_session.query(Phase).filter_by(id=phase.id).first()
        assert fetched.specs == specs
        assert fetched.specs["files_to_create"] == ["src/main.py", "tests/test_main.py"]
    
    def test_phase_default_status(self, db_session):
        """Phase should have 'planned' as default status"""
        project = Project(name="status-test")
        db_session.add(project)
        db_session.commit()
        
        phase = Phase(
            project_id=project.id,
            phase_number=1,
            title="Status Test",
            specs={}
        )
        db_session.add(phase)
        db_session.commit()
        
        assert phase.status == "planned"
    
    def test_phase_progress_data_nullable(self, db_session):
        """Phase progress_data should be nullable"""
        project = Project(name="nullable-test")
        db_session.add(project)
        db_session.commit()
        
        phase = Phase(
            project_id=project.id,
            phase_number=1,
            title="Nullable Test",
            specs={}
        )
        db_session.add(phase)
        db_session.commit()
        
        assert phase.progress_data is None
    
    def test_update_phase_progress(self, db_session):
        """Should update phase progress data"""
        project = Project(name="progress-test")
        db_session.add(project)
        db_session.commit()
        
        phase = Phase(
            project_id=project.id,
            phase_number=1,
            title="Progress Test",
            specs={}
        )
        db_session.add(phase)
        db_session.commit()
        
        progress = {
            "files_created": ["main.py"],
            "tests_passed": 5,
            "tests_failed": 0
        }
        phase.progress_data = progress
        phase.status = "completed"
        db_session.commit()
        
        fetched = db_session.query(Phase).filter_by(id=phase.id).first()
        assert fetched.progress_data == progress
        assert fetched.status == "completed"
    
    def test_project_phases_relationship(self, db_session):
        """Project should have phases relationship"""
        project = Project(name="relationship-test")
        db_session.add(project)
        db_session.commit()
        
        phase1 = Phase(project_id=project.id, phase_number=1, title="Phase 1", specs={})
        phase2 = Phase(project_id=project.id, phase_number=2, title="Phase 2", specs={})
        db_session.add_all([phase1, phase2])
        db_session.commit()
        
        # Refresh to load relationships
        db_session.refresh(project)
        
        assert len(project.phases) == 2
        assert project.phases[0].title in ["Phase 1", "Phase 2"]


class TestProjectService:
    """Test ProjectService business logic"""
    
    def test_create_project_service(self, project_service):
        """Service should create project and return dict"""
        result = project_service.create_project(
            name="service-test",
            description="Testing service layer"
        )
        
        assert "project_id" in result
        assert result["name"] == "service-test"
        assert result["status"] == "active"
        assert "message" in result
    
    def test_save_phase_service(self, project_service):
        """Service should save phase specs"""
        project = project_service.create_project(name="phase-service")
        
        specs = {
            "files_to_create": ["app.py"],
            "tests_to_write": ["test_app.py"],
            "dependencies": ["flask"],
            "instructions": "Create Flask app"
        }
        
        result = project_service.save_phase(
            project_id=project["project_id"],
            phase_number=1,
            title="Setup Flask",
            specs=specs
        )
        
        assert "phase_id" in result
        assert result["phase_number"] == 1
        assert result["status"] == "planned"
    
    def test_get_phase_service(self, project_service):
        """Service should retrieve phase with specs"""
        project = project_service.create_project(name="get-phase-test")
        specs = {"files": ["main.py"], "tests": ["test_main.py"]}
        
        project_service.save_phase(
            project_id=project["project_id"],
            phase_number=1,
            title="Get Test",
            specs=specs
        )
        
        result = project_service.get_phase(
            project_id=project["project_id"],
            phase_number=1
        )
        
        assert result["title"] == "Get Test"
        assert result["specs"] == specs
        assert result["status"] == "planned"
    
    def test_update_progress_service(self, project_service):
        """Service should update phase progress"""
        project = project_service.create_project(name="update-progress")
        project_service.save_phase(
            project_id=project["project_id"],
            phase_number=1,
            title="Update Test",
            specs={}
        )
        
        progress_data = {
            "files_created": ["main.py", "test_main.py"],
            "tests_passed": 10,
            "tests_failed": 0,
            "notes": "All tests passing"
        }
        
        result = project_service.update_progress(
            project_id=project["project_id"],
            phase_number=1,
            status="completed",
            progress_data=progress_data
        )
        
        assert result["status"] == "completed"
        assert "message" in result
    
    def test_get_nonexistent_phase_raises_error(self, project_service):
        """Should raise error when phase doesn't exist"""
        project = project_service.create_project(name="error-test")
        
        with pytest.raises(ValueError):
            project_service.get_phase(
                project_id=project["project_id"],
                phase_number=99
            )
    
    def test_list_projects_service(self, project_service):
        """Service should list all projects"""
        project_service.create_project(name="list-test-1")
        project_service.create_project(name="list-test-2")
        
        projects = project_service.list_projects()
        
        assert len(projects) >= 2
        names = [p["name"] for p in projects]
        assert "list-test-1" in names
        assert "list-test-2" in names
