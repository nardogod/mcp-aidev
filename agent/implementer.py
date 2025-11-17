"""
Automatic Phase Implementation Module

This module implements automatic code generation and file creation
based on phase specifications.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .llm import get_llm
from .config import config


@dataclass
class ImplementationResult:
    """Result of phase implementation"""
    success: bool
    files_created: List[str]
    files_updated: List[str]
    tests_passed: int = 0
    tests_failed: int = 0
    errors: List[str] = None
    notes: str = ""

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class PhaseImplementer:
    """
    Automatically implements a phase by:
    1. Reading phase specifications
    2. Generating code using LLM
    3. Creating/updating files
    4. Running tests
    5. Validating implementation
    """
    
    def __init__(self, project_path: str = None, llm_provider: str = None):
        """
        Initialize the implementer.
        
        Args:
            project_path: Base path for the project (defaults to current directory)
            llm_provider: LLM provider to use (defaults to config)
        """
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.llm_provider = llm_provider or config.llm_provider
        self.llm = get_llm(self.llm_provider, temperature=0.3)  # Lower temp for code generation
        
    def implement_phase(
        self,
        phase_specs: Dict[str, Any],
        project_name: str,
        project_description: str = "",
        previous_phases: List[Dict[str, Any]] = None
    ) -> ImplementationResult:
        """
        Implement a phase automatically.
        
        Args:
            phase_specs: Phase specifications from MCP
            project_name: Name of the project
            project_description: Project description
            previous_phases: List of previously completed phases
            
        Returns:
            ImplementationResult with details of what was created
        """
        result = ImplementationResult(success=False, files_created=[], files_updated=[])
        
        try:
            # Build context for LLM
            context = self._build_context(
                phase_specs, project_name, project_description, previous_phases
            )
            
            # TDD APPROACH: Test-Driven Development
            # 1. RED: Write tests first (they should fail)
            # 2. GREEN: Write minimal code to make tests pass
            # 3. REFACTOR: Improve code quality
            
            files_to_create = phase_specs.get("specs", {}).get("files_to_create", [])
            files_to_update = phase_specs.get("specs", {}).get("files_to_update", [])
            tests_to_write = phase_specs.get("specs", {}).get("tests_to_write", [])
            
            # Install dependencies first (needed for tests)
            dependencies = phase_specs.get("specs", {}).get("dependencies", [])
            if dependencies:
                self._install_dependencies(dependencies)
            
            # STEP 1: RED - Write tests FIRST (TDD)
            if tests_to_write:
                print("\n[TDD] RED Phase: Writing tests first...")
                for test_file in tests_to_write:
                    test_result = self._create_test_file(test_file, context, phase_specs, files_to_create)
                    if test_result["success"]:
                        result.files_created.append(test_file)
                        print(f"  ✅ Test created: {test_file}")
                    else:
                        result.errors.append(f"Failed to create test {test_file}: {test_result.get('error')}")
                
                # Run tests - they should FAIL (RED phase)
                print("\n[TDD] Running tests (expected to FAIL in RED phase)...")
                test_result_red = self._run_tests(tests_to_write)
                print(f"  Tests failed (as expected): {test_result_red.get('failed', 0)}")
            
            # STEP 2: GREEN - Write minimal code to make tests pass
            print("\n[TDD] GREEN Phase: Writing code to make tests pass...")
            
            # Separate test files from source files
            source_files = [f for f in files_to_create if not any(t in f for t in tests_to_write)]
            
            # Create source files (implementation)
            for file_path in source_files:
                file_result = self._create_file(file_path, context, phase_specs)
                if file_result["success"]:
                    result.files_created.append(file_path)
                    print(f"  ✅ Code created: {file_path}")
                else:
                    result.errors.append(f"Failed to create {file_path}: {file_result.get('error')}")
            
            # Update existing files
            for file_path in files_to_update:
                file_result = self._update_file(file_path, context, phase_specs)
                if file_result["success"]:
                    result.files_updated.append(file_path)
                    print(f"  ✅ Code updated: {file_path}")
                else:
                    result.errors.append(f"Failed to update {file_path}: {file_result.get('error')}")
            
            # STEP 3: Run tests again - they should PASS now (GREEN phase)
            if tests_to_write:
                print("\n[TDD] GREEN Phase: Running tests (should PASS now)...")
                test_result_green = self._run_tests(tests_to_write)
                result.tests_passed = test_result_green.get("passed", 0)
                result.tests_failed = test_result_green.get("failed", 0)
                
                if result.tests_passed > 0:
                    print(f"  ✅ Tests passing: {result.tests_passed}")
                if result.tests_failed > 0:
                    print(f"  ⚠️  Tests still failing: {result.tests_failed}")
                    result.errors.append(f"{result.tests_failed} test(s) still failing after implementation")
            
            # STEP 4: REFACTOR (optional - could be done in next phase)
            # For now, we mark as complete if tests pass
            
            # Mark as successful if no critical errors
            result.success = len(result.errors) == 0
            
            if result.success:
                result.notes = f"Successfully implemented phase {phase_specs.get('phase_number', '?')}"
            else:
                result.notes = f"Implementation completed with {len(result.errors)} errors"
                
        except Exception as e:
            result.errors.append(f"Implementation failed: {str(e)}")
            result.success = False
            
        return result
    
    def _build_context(
        self,
        phase_specs: Dict[str, Any],
        project_name: str,
        project_description: str,
        previous_phases: List[Dict[str, Any]]
    ) -> str:
        """Build context string for LLM"""
        context = f"""
Project: {project_name}
Description: {project_description}

Current Phase: {phase_specs.get('phase_number', '?')} - {phase_specs.get('title', 'Unknown')}
Instructions: {phase_specs.get('specs', {}).get('instructions', 'No specific instructions')}
"""
        
        if previous_phases:
            context += "\nPrevious Phases:\n"
            for phase in previous_phases[-3:]:  # Last 3 phases for context
                context += f"  - Phase {phase.get('phase_number')}: {phase.get('title')}\n"
        
        return context
    
    def _create_test_file(self, test_file_path: str, context: str, phase_specs: Dict[str, Any], source_files: List[str]) -> Dict[str, Any]:
        """
        Create a test file following TDD principles.
        
        In TDD, tests are written FIRST before implementation.
        Tests should define the expected behavior and fail initially.
        
        Args:
            test_file_path: Path to the test file
            context: Context for test generation
            phase_specs: Phase specifications
            source_files: List of source files that will be tested
            
        Returns:
            Dict with success status
        """
        try:
            full_path = self.project_path / test_file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if full_path.exists():
                return {
                    "success": False,
                    "error": f"Test file {test_file_path} already exists"
                }
            
            # Generate test code using LLM
            prompt = f"""
{context}

You are following TDD (Test-Driven Development) methodology.

TDD RED Phase: Write tests FIRST before implementation.

You need to create the test file: {test_file_path}

Source files that will be tested: {source_files}
Files to create: {phase_specs.get('specs', {}).get('files_to_create', [])}
Instructions: {phase_specs.get('specs', {}).get('instructions', '')}

Generate comprehensive test code for {test_file_path} that:
1. Tests the expected behavior BEFORE implementation exists
2. Tests should FAIL initially (RED phase) because code doesn't exist yet
3. Define clear test cases covering all requirements
4. Use appropriate testing framework (pytest for Python, jest for JS, etc.)
5. Include edge cases and error handling tests
6. Follow TDD best practices

IMPORTANT:
- Write tests that define WHAT the code should do, not HOW
- Tests should be independent and isolated
- Include setup/teardown if needed
- Return ONLY the test code, no markdown, no explanations

Test code for {test_file_path}:
"""
            
            response = self.llm.invoke(prompt)
            test_code = self._extract_code(response.content, test_file_path)
            
            # Write test file
            full_path.write_text(test_code, encoding='utf-8')
            
            return {"success": True, "file_path": str(full_path)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_file(self, file_path: str, context: str, phase_specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new file with generated code.
        
        Args:
            file_path: Relative path to the file
            context: Context for code generation
            phase_specs: Phase specifications
            
        Returns:
            Dict with success status and optional error message
        """
        try:
            full_path = self.project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file already exists
            if full_path.exists():
                return {
                    "success": False,
                    "error": f"File {file_path} already exists. Use update_file instead."
                }
            
            # Generate code using LLM - TDD GREEN phase
            tests_to_write = phase_specs.get('specs', {}).get('tests_to_write', [])
            
            # Check if tests exist (TDD approach)
            test_context = ""
            if tests_to_write:
                # Read test files to understand what needs to be implemented
                test_contents = []
                for test_file in tests_to_write:
                    test_path = self.project_path / test_file
                    if test_path.exists():
                        test_contents.append(f"Test file {test_file}:\n{test_path.read_text(encoding='utf-8')[:1000]}")
                
                if test_contents:
                    test_context = "\n\nEXISTING TESTS (TDD GREEN Phase - make these pass):\n" + "\n".join(test_contents)
            
            prompt = f"""
{context}

TDD GREEN Phase: Write minimal code to make existing tests pass.

You need to create the file: {file_path}

Files to create: {phase_specs.get('specs', {}).get('files_to_create', [])}
Tests to write: {phase_specs.get('specs', {}).get('tests_to_write', [])}
Dependencies: {phase_specs.get('specs', {}).get('dependencies', [])}
{test_context}

Generate the code for {file_path} following these instructions:
{phase_specs.get('specs', {}).get('instructions', 'Implement according to best practices')}

IMPORTANT (TDD GREEN Phase):
- Write MINIMAL code to make existing tests pass
- Focus on making tests green, not perfect code
- If tests exist, read them and implement what they expect
- Include proper error handling
- Add comments where necessary
- Follow language-specific best practices
- Return ONLY the code, no markdown, no explanations

Code for {file_path}:
"""
            
            response = self.llm.invoke(prompt)
            code = self._extract_code(response.content, file_path)
            
            # Write file
            full_path.write_text(code, encoding='utf-8')
            
            return {"success": True, "file_path": str(full_path)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _update_file(self, file_path: str, context: str, phase_specs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing file.
        
        Args:
            file_path: Relative path to the file
            context: Context for code generation
            phase_specs: Phase specifications
            
        Returns:
            Dict with success status
        """
        try:
            full_path = self.project_path / file_path
            
            if not full_path.exists():
                return {
                    "success": False,
                    "error": f"File {file_path} does not exist. Use create_file instead."
                }
            
            # Read existing content
            existing_content = full_path.read_text(encoding='utf-8')
            
            # Generate updated code
            prompt = f"""
{context}

You need to update the file: {file_path}

Current file content:
```
{existing_content[:2000]}  # Limit to avoid token limits
```

Instructions for update:
{phase_specs.get('specs', {}).get('instructions', 'Update according to requirements')}

Generate the complete updated code for {file_path}. Include all existing functionality plus the new changes.

IMPORTANT:
- Preserve existing functionality
- Add new features as specified
- Maintain code quality
- Return ONLY the complete updated code, no markdown

Updated code for {file_path}:
"""
            
            response = self.llm.invoke(prompt)
            updated_code = self._extract_code(response.content, file_path)
            
            # Write updated file
            full_path.write_text(updated_code, encoding='utf-8')
            
            return {"success": True, "file_path": str(full_path)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _extract_code(self, content: str, file_path: str) -> str:
        """Extract code from LLM response, removing markdown if present"""
        content = content.strip()
        
        # Remove markdown code blocks
        if content.startswith("```"):
            parts = content.split("```")
            for part in parts:
                if part.strip() and not part.strip().startswith(("python", "javascript", "typescript", "json", "html", "css")):
                    return part.strip()
            # If all parts are language tags, get the last one
            if parts:
                return parts[-1].strip()
        
        # Remove any leading/trailing text before/after code
        lines = content.split('\n')
        code_lines = []
        in_code = False
        
        for line in lines:
            if line.strip().startswith(('def ', 'class ', 'import ', 'from ', '<', 'function', 'const ', 'let ', 'var ')):
                in_code = True
            if in_code or not line.strip().startswith(('#', '//', '<!--')):
                code_lines.append(line)
        
        return '\n'.join(code_lines) if code_lines else content
    
    def _install_dependencies(self, dependencies: List[str]) -> Dict[str, Any]:
        """Install project dependencies"""
        try:
            import subprocess
            
            # Check if requirements.txt exists
            requirements_file = self.project_path / "requirements.txt"
            
            if requirements_file.exists():
                # Read existing dependencies
                existing = set(requirements_file.read_text().splitlines())
            else:
                existing = set()
            
            # Add new dependencies
            new_deps = set(dependencies) - existing
            if new_deps:
                with open(requirements_file, 'a', encoding='utf-8') as f:
                    for dep in new_deps:
                        f.write(f"{dep}\n")
                
                # Install using pip
                subprocess.run(
                    ["pip", "install"] + list(new_deps),
                    cwd=self.project_path,
                    check=True,
                    capture_output=True
                )
            
            return {"success": True, "installed": list(new_deps)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _run_tests(self, test_files: List[str]) -> Dict[str, Any]:
        """Run tests and return results"""
        try:
            import subprocess
            
            passed = 0
            failed = 0
            
            for test_file in test_files:
                test_path = self.project_path / test_file
                if not test_path.exists():
                    failed += 1
                    continue
                
                # Try pytest first, then unittest, then node test
                try:
                    result = subprocess.run(
                        ["pytest", str(test_path)],
                        cwd=self.project_path,
                        capture_output=True,
                        timeout=30
                    )
                    if result.returncode == 0:
                        passed += 1
                    else:
                        failed += 1
                except:
                    try:
                        result = subprocess.run(
                            ["python", "-m", "unittest", str(test_path)],
                            cwd=self.project_path,
                            capture_output=True,
                            timeout=30
                        )
                        if result.returncode == 0:
                            passed += 1
                        else:
                            failed += 1
                    except:
                        failed += 1
            
            return {"passed": passed, "failed": failed}
            
        except Exception as e:
            return {"passed": 0, "failed": len(test_files), "error": str(e)}

