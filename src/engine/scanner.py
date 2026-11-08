"""
File crawler for Python projects.
Walks a folder, grabs all .py files, and turns file paths into Python module names.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set

# Directories we definitely don't want to parse
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
    """Recursively crawls a project tree looking for Python files."""

    def __init__(self, root_path: Path, ignore_dirs: Set[str] | None = None):
        self.root_path = root_path.resolve()
        self.ignore_dirs = ignore_dirs if ignore_dirs is not None else DEFAULT_IGNORE_DIRS

    def scan(self) -> Dict[str, DiscoveredModule]:
        """Walks the directory and returns { module_name: DiscoveredModule }."""
        modules: Dict[str, DiscoveredModule] = {}

        for path in self.root_path.rglob("*.py"):
            # Skip ignored directories (like venv, .git, etc.)
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
        Turn relative path into dot-notation:
          'auth/service.py' -> ('auth.service', False)
          'auth/__init__.py' -> ('auth', True)
        """
        parts = list(rel_path.with_suffix("").parts)
        is_init = False

        if parts and parts[-1] == "__init__":
            is_init = True
            parts.pop()

        module_name = ".".join(parts)
        return module_name, is_init
