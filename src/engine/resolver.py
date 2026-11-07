"""
Import Resolver for Python codebases.
Resolves relative imports and differentiates internal project modules from external/stdlib packages.
"""

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

from src.engine.parser import ImportInfo
from src.engine.scanner import DiscoveredModule

# sys.stdlib_module_names is available in Python 3.10+
STDLIB_MODULES: Set[str] = set(getattr(sys, "stdlib_module_names", frozenset()))


@dataclass
class ResolvedImport:
    """Represents a fully resolved import edge."""
    raw_statement: str
    target_module: str            # e.g., 'auth.crypto' or 'fastapi'
    target_symbol: Optional[str]   # e.g., 'hash_pwd' if imported directly
    is_internal: bool             # True if it points to a file within the project
    is_stdlib: bool               # True if part of Python standard library
    lineno: int


class ImportResolver:
    """Resolves raw AST imports against the project's discovered module map."""

    def __init__(self, discovered_modules: Dict[str, DiscoveredModule]):
        self.discovered_modules = discovered_modules
        self.known_module_names = set(discovered_modules.keys())

    def resolve_module_imports(
        self, current_module: str, raw_imports: List[ImportInfo]
    ) -> List[ResolvedImport]:
        """Resolves all imports for a given module."""
        resolved: List[ResolvedImport] = []

        for imp in raw_imports:
            target = self._resolve_target_name(current_module, imp)
            is_internal, internal_mod, symbol = self._match_internal(current_module, target, imp.imported_name)

            # Determine if it's stdlib
            root_pkg = target.split(".")[0] if target else ""
            is_stdlib = root_pkg in STDLIB_MODULES

            if is_internal and internal_mod:
                resolved.append(
                    ResolvedImport(
                        raw_statement=self._format_raw(imp),
                        target_module=internal_mod,
                        target_symbol=symbol,
                        is_internal=True,
                        is_stdlib=False,
                        lineno=imp.lineno,
                    )
                )
            else:
                resolved.append(
                    ResolvedImport(
                        raw_statement=self._format_raw(imp),
                        target_module=target or root_pkg,
                        target_symbol=imp.imported_name,
                        is_internal=False,
                        is_stdlib=is_stdlib,
                        lineno=imp.lineno,
                    )
                )

        return resolved

    def _resolve_target_name(self, current_module: str, imp: ImportInfo) -> str:
        """Handles relative import levels (., .., ...) to get absolute module notation."""
        if imp.level == 0:
            return imp.module

        # Relative import: determine parent package parts
        parts = current_module.split(".")
        current_disc = self.discovered_modules.get(current_module)

        # If current file is not an __init__.py, its package is parts[:-1]
        if current_disc and not current_disc.is_package_init:
            pkg_parts = parts[:-1]
        else:
            pkg_parts = parts

        # Each level backs up one directory: level 1 is current dir, level 2 is parent, etc.
        backtrack = imp.level - 1
        if backtrack > 0:
            pkg_parts = pkg_parts[:-backtrack] if backtrack <= len(pkg_parts) else []

        if imp.module:
            combined = pkg_parts + imp.module.split(".")
        else:
            combined = pkg_parts

        return ".".join(combined)

    def _match_internal(
        self, current_module: str, target_module: str, imported_name: Optional[str]
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Checks if the target_module or target_module.imported_name matches a file in the project.
        Checks exact matches, sibling/subpackage matches, and common src/ root prefixes.
        Returns: (is_internal, resolved_module_name, imported_symbol)
        """
        if not target_module and not imported_name:
            return False, None, None

        # Build list of potential module name candidates
        candidates = []
        if target_module:
            candidates.append(target_module)

        # Current package context
        parts = current_module.split(".")
        current_disc = self.discovered_modules.get(current_module)
        pkg_parts = parts if (current_disc and current_disc.is_package_init) else parts[:-1]

        # Sibling candidates (e.g., imported 'config' from within 'tests.sample_project.main')
        if pkg_parts:
            pkg_prefix = ".".join(pkg_parts)
            if target_module:
                candidates.append(f"{pkg_prefix}.{target_module}")
            if imported_name and not target_module:
                candidates.append(f"{pkg_prefix}.{imported_name}")

        # Check 'src.' prefix variations if applicable
        if target_module:
            if not target_module.startswith("src.") and f"src.{target_module}" in self.known_module_names:
                candidates.append(f"src.{target_module}")
            elif target_module.startswith("src."):
                candidates.append(target_module[4:])

        for cand in candidates:
            # Check 1: direct candidate match
            if cand in self.known_module_names:
                return True, cand, imported_name

            # Check 2: candidate might be a package, and imported_name is a submodule file
            if imported_name:
                submodule_cand = f"{cand}.{imported_name}"
                if submodule_cand in self.known_module_names:
                    return True, submodule_cand, None

        return False, None, imported_name

    def _format_raw(self, imp: ImportInfo) -> str:
        dots = "." * imp.level
        if imp.imported_name:
            return f"from {dots}{imp.module} import {imp.imported_name}"
        return f"import {dots}{imp.module}"
