"""
Directory and file scanner for Python projects.
Discovers all Python source files and calculates their module dot-notation.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set

DEFAULT_IGNORE_DIRS: Set[str] = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    ".env",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".eggs",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
    "site-packages",
}


@dataclass
class DiscoveredModule:
    """Represents a discovered Python file in the target project."""
    file_path: Path
    relative_path: Path
    module_name: str
    is_package_init: bool


class ProjectScanner:
    """Recursively scans a directory for Python source files."""

    def __init__(self, root_path: Path, ignore_dirs: Set[str] | None = None):
        self.root_path = root_path.resolve()
        self.ignore_dirs = ignore_dirs if ignore_dirs is not None else DEFAULT_IGNORE_DIRS

    def scan(self) -> Dict[str, DiscoveredModule]:
        """
        Scans the project directory and returns a dictionary mapping
        module_name -> DiscoveredModule.
        """
        modules: Dict[str, DiscoveredModule] = {}

        for path in self.root_path.rglob("*.py"):
            # Check if any parent directory is in ignore_dirs
            rel_parts = path.relative_to(self.root_path).parts
            if any(part in self.ignore_dirs for part in rel_parts[:-1]):
                continue

            rel_path = path.relative_to(self.root_path)
            module_name, is_init = self._compute_module_name(rel_path)

            discovered = DiscoveredModule(
                file_path=path,
                relative_path=rel_path,
                module_name=module_name,
                is_package_init=is_init,
            )
            modules[module_name] = discovered

        return modules

    def _compute_module_name(self, rel_path: Path) -> tuple[str, bool]:
        """
        Converts a relative path to Python module dot-notation.
        Examples:
            'auth/service.py' -> ('auth.service', False)
            'auth/__init__.py' -> ('auth', True)
            'main.py' -> ('main', False)
        """
        parts = list(rel_path.with_suffix("").parts)
        is_init = False

        if parts and parts[-1] == "__init__":
            is_init = True
            parts.pop()

        module_name = ".".join(parts)
        return module_name, is_init
