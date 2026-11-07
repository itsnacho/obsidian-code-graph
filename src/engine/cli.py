"""
Command-Line Interface for Obsidian Code Graph Engine.
Scans a target Python project, extracts architecture, and outputs a diagnostic summary.
"""

import argparse
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.engine.graph import DependencyGraph
from src.engine.parser import SourceParser
from src.engine.resolver import ImportResolver
from src.engine.scanner import ProjectScanner


def analyze_codebase(target_path: Path) -> DependencyGraph:
    """End-to-end analysis pipeline for a Python project."""
    scanner = ProjectScanner(target_path)
    discovered = scanner.scan()

    resolver = ImportResolver(discovered)
    graph = DependencyGraph()

    for mod_name, disc in discovered.items():
        parsed = SourceParser.parse_file(disc.file_path, mod_name, is_package_init=disc.is_package_init)
        resolved_imports = resolver.resolve_module_imports(mod_name, parsed.imports)
        graph.add_module(parsed, resolved_imports)

    graph.build_edges()
    return graph


def print_summary(graph: DependencyGraph, target_path: Path) -> None:
    """Prints a formatted terminal summary of the codebase analysis."""
    total_modules = len(graph.nodes)
    total_loc = sum(node.parsed.total_loc for node in graph.nodes.values())
    total_code_loc = sum(node.parsed.code_loc for node in graph.nodes.values())
    total_classes = sum(len(node.parsed.classes) for node in graph.nodes.values())
    total_functions = sum(len(node.parsed.functions) for node in graph.nodes.values())

    cycles = graph.find_cycles()
    orphans = graph.get_orphans()
    entry_points = graph.get_entry_points()
    hubs = graph.get_hubs()

    print("\n" + "=" * 60)
    print(f"🕸️  OBSIDIAN CODE GRAPH — ARCHITECTURE REPORT")
    print(f"📁 Target: {target_path.resolve()}")
    print("=" * 60)

    print("\n📊 Project Metrics:")
    print(f"  • Modules Analyzed:  {total_modules}")
    print(f"  • Total Lines:       {total_loc} ({total_code_loc} code lines)")
    print(f"  • Classes Found:     {total_classes}")
    print(f"  • Functions Found:   {total_functions}")

    print("\n🏛️  Architecture Structure:")
    if entry_points:
        print(f"  • Entry Points ({len(entry_points)}): {', '.join(entry_points)}")
    else:
        print("  • Entry Points: None detected")

    if hubs:
        hub_strs = [f"{name} ({count} imports)" for name, count in hubs]
        print(f"  • Core Hub Modules: {', '.join(hub_strs)}")
    else:
        print("  • Core Hub Modules: None")

    print("\n⚠️  Diagnostic Checks:")
    if cycles:
        print(f"  🔴 CIRCULAR DEPENDENCIES DETECTED ({len(cycles)} loop{'s' if len(cycles) > 1 else ''}):")
        for idx, cycle in enumerate(cycles, 1):
            cycle_str = " -> ".join(cycle)
            print(f"     [{idx}] {cycle_str}")
    else:
        print("  ✅ No circular dependencies found!")

    if orphans:
        print(f"  👻 ORPHAN / DEAD CODE MODULES ({len(orphans)}):")
        for orphan in orphans:
            print(f"     • {orphan}")
    else:
        print("  ✅ No orphan modules found!")

    print("\n📦 Module Dependency Breakdown:")
    for mod_name, node in sorted(graph.nodes.items()):
        internal_deps = sorted(node.internal_dependencies)
        external_deps = sorted(node.external_dependencies)
        status_flags = []
        if node.is_orphan:
            status_flags.append("[ORPHAN]")
        if any(mod_name in c for c in cycles):
            status_flags.append("[CIRCULAR]")

        flag_str = " " + " ".join(status_flags) if status_flags else ""
        print(f"\n  • {mod_name}{flag_str}")
        print(f"    LOC: {node.parsed.code_loc} | Classes: {len(node.parsed.classes)} | Funcs: {len(node.parsed.functions)}")
        if internal_deps:
            print(f"    Imports (Internal): {', '.join(internal_deps)}")
        if external_deps:
            print(f"    Imports (External): {', '.join(external_deps)}")
        if node.internal_dependents:
            print(f"    Imported By:        {', '.join(sorted(node.internal_dependents))}")

    print("\n" + "=" * 60 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Obsidian Code Graph Engine")
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Path to Python codebase to analyze (default: current directory)",
    )
    args = parser.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Path '{target_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    graph = analyze_codebase(target_path)
    print_summary(graph, target_path)


if __name__ == "__main__":
    main()
