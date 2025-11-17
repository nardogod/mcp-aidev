"""Tests for project structure (FASE 1)."""

import os
from pathlib import Path


def test_project_structure_exists():
    """Test that all required directories exist."""
    base_path = Path(__file__).parent.parent
    
    required_dirs = [
        "src",
        "src/mcp",
        "src/database",
        "src/services",
        "tests",
        "docs",
    ]
    
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        assert full_path.exists(), f"Directory {dir_path} does not exist"
        assert full_path.is_dir(), f"{dir_path} is not a directory"


def test_requirements_installed():
    """Test that requirements.txt exists."""
    base_path = Path(__file__).parent.parent
    requirements_file = base_path / "requirements.txt"
    
    assert requirements_file.exists(), "requirements.txt does not exist"
    assert requirements_file.is_file(), "requirements.txt is not a file"
    
    # Check that file has content
    content = requirements_file.read_text()
    assert len(content) > 0, "requirements.txt is empty"
    assert "fastapi" in content.lower(), "fastapi not found in requirements.txt"
    assert "sqlalchemy" in content.lower(), "sqlalchemy not found in requirements.txt"

