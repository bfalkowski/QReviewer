"""Review standards, guidelines, and context management."""

import json
import os
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class ReviewStandard:
    """A review standard with rules and guidelines."""
    name: str
    description: str
    version: str
    rules: List[Dict[str, Any]]
    severity_weights: Dict[str, float]
    categories: List[str]
    metadata: Dict[str, Any]


@dataclass
class ReviewContext:
    """Context information for a code review."""
    project_name: str
    project_description: str
    team_preferences: Dict[str, Any]
    business_context: str
    dependencies: List[str]
    previous_reviews: List[Dict[str, Any]]
    custom_rules: List[Dict[str, Any]]
    compliance_requirements: List[str]


class StandardsManager:
    """Manages review standards and context."""
    
    def __init__(self, standards_dir: str = "standards"):
        self.standards_dir = Path(standards_dir)
        self.standards_dir.mkdir(exist_ok=True)
        self.standards: Dict[str, ReviewStandard] = {}
        self._load_standards()
    
    def _load_standards(self):
        """Load all available standards."""
        for file_path in self.standards_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    standard = ReviewStandard(**data)
                    self.standards[standard.name] = standard
            except Exception as e:
                print(f"Warning: Could not load standard {file_path}: {e}")
    
    def get_standard(self, name: str) -> Optional[ReviewStandard]:
        """Get a specific standard by name."""
        return self.standards.get(name)
    
    def list_standards(self) -> List[str]:
        """List all available standard names."""
        return list(self.standards.keys())
    
    def create_standard(self, standard: ReviewStandard) -> bool:
        """Create a new standard."""
        try:
            file_path = self.standards_dir / f"{standard.name}.json"
            with open(file_path, 'w') as f:
                json.dump(asdict(standard), f, indent=2)
            self.standards[standard.name] = standard
            return True
        except Exception as e:
            print(f"Error creating standard: {e}")
            return False
    
    def get_context_from_files(self, project_path: str) -> ReviewContext:
        """Extract review context from project files."""
        project_path = Path(project_path)
        
        context = ReviewContext(
            project_name=project_path.name,
            project_description="",
            team_preferences={},
            business_context="",
            dependencies=[],
            previous_reviews=[],
            custom_rules=[],
            compliance_requirements=[]
        )
        
        # Try to read README
        readme_files = ["README.md", "README.txt", "README.rst"]
        for readme in readme_files:
            readme_path = project_path / readme
            if readme_path.exists():
                try:
                    with open(readme_path, 'r') as f:
                        context.project_description = f.read()[:1000]  # First 1000 chars
                    break
                except:
                    pass
        
        # Try to read contributing guidelines
        contributing_files = ["CONTRIBUTING.md", ".github/CONTRIBUTING.md"]
        for contrib in contributing_files:
            contrib_path = project_path / contrib
            if contrib_path.exists():
                try:
                    with open(contrib_path, 'r') as f:
                        content = f.read()
                        context.team_preferences["contributing_guidelines"] = content[:1000]
                    break
                except:
                    pass
        
        # Try to read requirements/dependencies
        req_files = ["requirements.txt", "pyproject.toml", "package.json"]
        for req_file in req_files:
            req_path = project_path / req_file
            if req_path.exists():
                try:
                    with open(req_path, 'r') as f:
                        context.dependencies.append(f"{req_file}: {f.read()[:500]}")
                except:
                    pass
        
        return context


# Pre-built standards
DEFAULT_STANDARDS = {
    "security": ReviewStandard(
        name="security",
        description="Security-focused code review standards",
        version="1.0.0",
        rules=[
            {
                "id": "SEC001",
                "category": "authentication",
                "pattern": r"(password|secret|token|key)\s*=\s*['\"][^'\"]+['\"]",
                "message": "Hardcoded credentials detected - use environment variables",
                "severity": "critical",
                "suggestion": "Replace with: os.getenv('SECRET_NAME')"
            },
            {
                "id": "SEC002", 
                "category": "injection",
                "pattern": r"eval\s*\(",
                "message": "eval() usage detected - potential code injection risk",
                "severity": "critical",
                "suggestion": "Use safer alternatives like ast.literal_eval() or json.loads()"
            },
            {
                "id": "SEC003",
                "category": "input_validation",
                "pattern": r"\.format\(.*\+.*\)",
                "message": "String concatenation in format() - potential injection",
                "severity": "major",
                "suggestion": "Use f-strings or proper escaping"
            }
        ],
        severity_weights={"critical": 3.0, "major": 2.0, "minor": 1.0},
        categories=["authentication", "injection", "input_validation", "crypto"],
        metadata={"framework": "general", "language": "python"}
    ),
    
    "python_style": ReviewStandard(
        name="python_style",
        description="Python style and best practices",
        version="1.0.0",
        rules=[
            {
                "id": "STY001",
                "category": "naming",
                "pattern": r"def [a-z][a-z0-9_]*\(",
                "message": "Function name should be snake_case",
                "severity": "minor",
                "suggestion": "Rename function to use snake_case: def my_function():"
            },
            {
                "id": "STY002",
                "category": "imports",
                "pattern": r"import \*",
                "message": "Wildcard imports can cause namespace pollution",
                "severity": "major",
                "suggestion": "Import only what you need: from module import specific_function"
            },
            {
                "id": "STY003",
                "category": "type_hints",
                "pattern": r"def [^(]+\([^)]*\):",
                "message": "Missing return type annotation",
                "severity": "minor",
                "suggestion": "Add return type: def function() -> ReturnType:"
            }
        ],
        severity_weights={"critical": 1.0, "major": 1.5, "minor": 1.0},
        categories=["naming", "imports", "type_hints", "formatting"],
        metadata={"framework": "pep8", "language": "python"}
    ),
    
    "performance": ReviewStandard(
        name="performance",
        description="Performance optimization guidelines",
        version="1.0.0",
        rules=[
            {
                "id": "PERF001",
                "category": "loops",
                "pattern": r"for.*in.*range\(len\(",
                "message": "Inefficient loop pattern - use enumerate()",
                "severity": "minor",
                "suggestion": "Replace with: for i, item in enumerate(items):"
            },
            {
                "id": "PERF002",
                "category": "data_structures",
                "pattern": r"\.append\(\)\s*in\s*loop",
                "message": "List appending in loop - consider list comprehension",
                "severity": "minor",
                "suggestion": "Use: [f(x) for x in items] instead of loop + append"
            }
        ],
        severity_weights={"critical": 2.0, "major": 1.5, "minor": 1.0},
        categories=["loops", "data_structures", "algorithms"],
        metadata={"framework": "general", "language": "python"}
    )
}


def create_default_standards(standards_dir: str = "standards") -> StandardsManager:
    """Create and save default standards."""
    manager = StandardsManager(standards_dir)
    
    for standard in DEFAULT_STANDARDS.values():
        manager.create_standard(standard)
    
    return manager


def load_project_context(project_path: str, standards: List[str] = None) -> Dict[str, Any]:
    """Load comprehensive project context for reviews."""
    manager = StandardsManager()
    
    # Get project context
    context = manager.get_context_from_files(project_path)
    
    # Get requested standards
    selected_standards = {}
    if standards:
        for std_name in standards:
            if std_name in manager.standards:
                selected_standards[std_name] = manager.standards[std_name]
    else:
        # Use all standards
        selected_standards = manager.standards
    
    return {
        "project_context": asdict(context),
        "standards": {name: asdict(std) for name, std in selected_standards.items()},
        "available_standards": manager.list_standards()
    }
