"""
In-memory directed dependency graph for codebase architecture analysis.
Computes in-degree, out-degree, cycles, entry points, and orphan modules.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

from src.engine.parser import ParsedModule
from src.engine.resolver import ResolvedImport


@dataclass
class ModuleNode:
    """Represents a module node in the dependency graph."""
    module_name: str
    parsed: ParsedModule
    internal_dependencies: Set[str] = field(default_factory=set)  # Modules this node imports
    internal_dependents: Set[str] = field(default_factory=set)    # Modules that import this node
    external_dependencies: Set[str] = field(default_factory=set)  # 3rd-party or stdlib packages
    resolved_imports: List[ResolvedImport] = field(default_factory=list)

    @property
    def in_degree(self) -> int:
        """Number of modules that depend on this node."""
        return len(self.internal_dependents)

    @property
    def out_degree(self) -> int:
        """Number of internal modules this node depends on."""
        return len(self.internal_dependencies)

    @property
    def is_orphan(self) -> bool:
        """True if the module has 0 dependents and 0 internal dependencies (excluding package __init__ files)."""
        if self.parsed.is_package_init:
            return False
        return self.in_degree == 0 and self.out_degree == 0


class DependencyGraph:
    """Directed graph representing the architecture of the codebase."""

    def __init__(self):
        self.nodes: Dict[str, ModuleNode] = {}

    def add_module(self, parsed: ParsedModule, resolved_imports: List[ResolvedImport]) -> None:
        """Adds a module node and registers its imports."""
        node = ModuleNode(
            module_name=parsed.module_name,
            parsed=parsed,
            resolved_imports=resolved_imports,
        )

        for imp in resolved_imports:
            if imp.is_internal:
                # Avoid self-loops in dependencies set
                if imp.target_module != parsed.module_name:
                    node.internal_dependencies.add(imp.target_module)
            else:
                if imp.target_module:
                    node.external_dependencies.add(imp.target_module)

        self.nodes[parsed.module_name] = node

    def build_edges(self) -> None:
        """Computes reverse dependencies (dependents / in-edges) for all nodes."""
        for mod_name, node in self.nodes.items():
            for dep in node.internal_dependencies:
                if dep in self.nodes:
                    self.nodes[dep].internal_dependents.add(mod_name)

    def find_cycles(self) -> List[List[str]]:
        """
        Detects circular dependency cycles using Depth-First Search (DFS).
        Returns a list of cycle paths, e.g., [['auth.service', 'config', 'auth.service']].
        """
        visited: Set[str] = set()
        recursion_stack: List[str] = []
        in_stack: Set[str] = set()
        cycles: List[List[str]] = []
        seen_cycle_fingerprints: Set[frozenset] = set()

        def dfs(curr: str):
            visited.add(curr)
            recursion_stack.append(curr)
            in_stack.add(curr)

            node = self.nodes.get(curr)
            if node:
                for neighbor in sorted(node.internal_dependencies):
                    if neighbor not in self.nodes:
                        continue
                    if neighbor in in_stack:
                        # Cycle detected! Extract the cycle path from recursion_stack
                        cycle_start_idx = recursion_stack.index(neighbor)
                        cycle_path = recursion_stack[cycle_start_idx:] + [neighbor]
                        fingerprint = frozenset(cycle_path)
                        if fingerprint not in seen_cycle_fingerprints:
                            seen_cycle_fingerprints.add(fingerprint)
                            cycles.append(cycle_path)
                    elif neighbor not in visited:
                        dfs(neighbor)

            recursion_stack.pop()
            in_stack.remove(curr)

        for mod_name in sorted(self.nodes.keys()):
            if mod_name not in visited:
                dfs(mod_name)

        return cycles

    def get_orphans(self) -> List[str]:
        """Returns all modules with 0 dependents and 0 internal dependencies."""
        return sorted([name for name, node in self.nodes.items() if node.is_orphan])

    def get_entry_points(self) -> List[str]:
        """Returns modules with 0 dependents but >= 1 dependency (top of the dependency tree)."""
        return sorted([
            name for name, node in self.nodes.items()
            if node.in_degree == 0 and node.out_degree > 0
        ])

    def get_hubs(self, limit: int = 5) -> List[Tuple[str, int]]:
        """Returns the most heavily depended-upon modules (highest in-degree)."""
        sorted_nodes = sorted(
            self.nodes.items(),
            key=lambda item: item[1].in_degree,
            reverse=True,
        )
        return [(name, node.in_degree) for name, node in sorted_nodes[:limit] if node.in_degree > 0]
