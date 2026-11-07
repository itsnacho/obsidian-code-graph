"""
Obsidian Vault Generator.
Converts a DependencyGraph into a fully linked, interactive Obsidian vault
with frontmatter metadata, wiki-links, callouts, and preconfigured graph physics.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Set

from src.engine.graph import DependencyGraph, ModuleNode
from src.engine.parser import ClassInfo, FunctionInfo


class VaultGenerator:
    """Generates an Obsidian vault folder containing interconnected Markdown notes."""

    def __init__(self, graph: DependencyGraph, output_dir: Path, project_name: str = "Codebase"):
        self.graph = graph
        self.output_dir = output_dir.resolve()
        self.project_name = project_name
        self.cycles = graph.find_cycles()
        self.cycle_map: Dict[str, List[List[str]]] = {}
        for cycle in self.cycles:
            for mod in set(cycle):
                self.cycle_map.setdefault(mod, []).append(cycle)

    def generate(self) -> Path:
        """Executes full vault generation."""
        if self.output_dir.exists():
            # Clean previous generated notes but preserve any user files if needed
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Setup .obsidian configuration (Graph View styling & colors)
        self._write_obsidian_config()

        # 2. Write individual module notes
        for mod_name, node in self.graph.nodes.items():
            self._write_module_note(mod_name, node)

        # 3. Write Master Index / Overview note
        self._write_overview_note()

        return self.output_dir

    def _write_obsidian_config(self) -> None:
        """Writes preconfigured .obsidian settings for optimal graph physics and node colors."""
        dot_obsidian = self.output_dir / ".obsidian"
        dot_obsidian.mkdir(parents=True, exist_ok=True)

        app_config = {
            "useMarkdownLinks": False,
            "showLineNumber": True,
        }
        (dot_obsidian / "app.json").write_text(json.dumps(app_config, indent=2), encoding="utf-8")

        # Color groups for Obsidian Graph View:
        # Red (#e05252 = 14701138) for circular dependencies
        # Orange (#e67e22 = 15105570) for orphans
        # Purple/Indigo (#6c5ce7 = 7101671) for entry points
        # Teal (#00b894 = 47252) for standard modules
        graph_config = {
            "collapse-filter": False,
            "search": "",
            "local-search": "",
            "local-backend": "gephi",
            "local-forefront": True,
            "showTags": False,
            "showAttachments": False,
            "hideUnresolved": False,
            "showOrphans": True,
            "collapse-color-groups": False,
            "colorGroups": [
                {
                    "query": "tag:#status/circular-dependency",
                    "color": {"a": 1, "rgb": 14701138},
                },
                {
                    "query": "tag:#status/orphan",
                    "color": {"a": 1, "rgb": 15105570},
                },
                {
                    "query": "tag:#status/entrypoint",
                    "color": {"a": 1, "rgb": 7101671},
                },
                {
                    "query": "tag:#code/module",
                    "color": {"a": 1, "rgb": 47252},
                },
            ],
            "collapse-display": False,
            "showArrow": True,
            "textFadeMultiplier": 0,
            "nodeSizeMultiplier": 1.15,
            "lineSizeMultiplier": 1.1,
            "collapse-forces": False,
            "centerStrength": 0.45,
            "repulsionStrength": 12,
            "linkStrength": 1,
            "linkDistance": 220,
            "scale": 1,
        }
        (dot_obsidian / "graph.json").write_text(json.dumps(graph_config, indent=2), encoding="utf-8")

    def _write_module_note(self, mod_name: str, node: ModuleNode) -> None:
        """Generates a rich Markdown note for a single module."""
        is_circular = mod_name in self.cycle_map
        is_orphan = node.is_orphan
        is_entrypoint = node.in_degree == 0 and node.out_degree > 0

        # Tags
        tags = ["code/module"]
        if is_circular:
            tags.append("status/circular-dependency")
        if is_orphan:
            tags.append("status/orphan")
        if is_entrypoint:
            tags.append("status/entrypoint")

        # Frontmatter
        lines = [
            "---",
            "type: module",
            f"module: {mod_name}",
            f"file_path: {node.parsed.file_path.as_posix()}",
            f"total_loc: {node.parsed.total_loc}",
            f"code_loc: {node.parsed.code_loc}",
            f"classes_count: {len(node.parsed.classes)}",
            f"functions_count: {len(node.parsed.functions)}",
            f"in_degree: {node.in_degree}",
            f"out_degree: {node.out_degree}",
            "tags:",
        ]
        for tag in tags:
            lines.append(f"  - #{tag}")
        lines.append("---\n")

        # Title
        lines.append(f"# 📦 `{mod_name}`\n")

        # Docstring overview
        if node.parsed.docstring:
            lines.append(f"> [!ABSTRACT] Module Overview\n> {node.parsed.docstring.strip()}\n")
        else:
            lines.append(f"> *No module-level docstring provided.*\n")

        # Warnings / Diagnostics Callouts
        if is_circular:
            lines.append("> [!WARNING] Circular Dependency Detected")
            for cycle in self.cycle_map[mod_name]:
                cycle_str = " ➔ ".join([f"`{c}`" for c in cycle])
                lines.append(f"> • Loop: {cycle_str}")
            lines.append("")

        if is_orphan:
            lines.append(
                "> [!CAUTION] Orphan Module (Dead Code Candidate)\n"
                "> This module has 0 dependents and 0 internal dependencies. Nothing in this project references it.\n"
            )

        if is_entrypoint:
            lines.append(
                "> [!TIP] Architectural Entry Point\n"
                "> This module is at the top of the dependency hierarchy (0 internal dependents).\n"
            )

        # Internal Dependencies (Obsidian Wiki-Links!)
        lines.append("## 🔗 Dependencies (Imports)")
        if node.internal_dependencies:
            lines.append("These internal modules are directly imported by this file:\n")
            for dep in sorted(node.internal_dependencies):
                lines.append(f"- [[{dep}]]")
        else:
            lines.append("*None (No internal project dependencies)*")
        lines.append("")

        # Internal Dependents (Backlink targets)
        lines.append("## 📥 Dependents (Imported By)")
        if node.internal_dependents:
            lines.append("These internal modules depend on this file:\n")
            for dep in sorted(node.internal_dependents):
                lines.append(f"- [[{dep}]]")
        else:
            lines.append("*None (No other modules import this file)*")
        lines.append("")

        # External Dependencies
        if node.external_dependencies:
            lines.append("## 🌐 External Dependencies")
            for ext in sorted(node.external_dependencies):
                lines.append(f"- `{ext}`")
            lines.append("")

        # Code Structure: Classes
        if node.parsed.classes:
            lines.append("## 🏛️ Classes")
            for cls in node.parsed.classes:
                lines.append(f"### `class {cls.name}` *(Line {cls.lineno})*")
                if cls.docstring:
                    lines.append(f"> {cls.docstring.strip()}\n")
                if cls.methods:
                    lines.append("**Methods:**")
                    for m in cls.methods:
                        prefix = "async def" if m.is_async else "def"
                        args_str = ", ".join(m.args)
                        ret_str = f" -> {m.return_type}" if m.return_type else ""
                        doc_str = f" — *{m.docstring.strip().splitlines()[0]}*" if m.docstring else ""
                        lines.append(f"- `{prefix} {m.name}({args_str}){ret_str}`{doc_str}")
                lines.append("")

        # Code Structure: Functions
        if node.parsed.functions:
            lines.append("## ⚡ Functions")
            for fn in node.parsed.functions:
                prefix = "async def" if fn.is_async else "def"
                args_str = ", ".join(fn.args)
                ret_str = f" -> {fn.return_type}" if fn.return_type else ""
                doc_str = f"\n  > {fn.docstring.strip()}" if fn.docstring else ""
                lines.append(f"- `{prefix} {fn.name}({args_str}){ret_str}` *(Line {fn.lineno})*{doc_str}")
            lines.append("")

        # Footer backlink to overview
        lines.append("---\n*Part of the [[_Overview|Architecture Overview]]*")

        note_file = self.output_dir / f"{mod_name}.md"
        note_file.write_text("\n".join(lines), encoding="utf-8")

    def _write_overview_note(self) -> None:
        """Generates the master index note for the entire project vault."""
        total_modules = len(self.graph.nodes)
        total_loc = sum(node.parsed.total_loc for node in self.graph.nodes.values())
        total_code_loc = sum(node.parsed.code_loc for node in self.graph.nodes.values())
        total_classes = sum(len(node.parsed.classes) for node in self.graph.nodes.values())
        total_functions = sum(len(node.parsed.functions) for node in self.graph.nodes.values())

        orphans = self.graph.get_orphans()
        entry_points = self.graph.get_entry_points()
        hubs = self.graph.get_hubs(limit=8)

        lines = [
            "---",
            "type: overview",
            f"project: {self.project_name}",
            f"total_modules: {total_modules}",
            f"total_loc: {total_loc}",
            "tags:",
            "  - #code/overview",
            "---\n",
            f"# 🕸️ {self.project_name} — Architecture Overview\n",
            "> Generated automatically by **Obsidian Code Graph**.\n",
            "## 📊 High-Level Metrics",
            f"| Metric | Count |",
            f"| :--- | :--- |",
            f"| **Total Modules** | {total_modules} |",
            f"| **Lines of Code** | {total_code_loc} code lines ({total_loc} total) |",
            f"| **Classes** | {total_classes} |",
            f"| **Functions** | {total_functions} |",
            f"| **Circular Import Loops** | {len(self.cycles)} |",
            f"| **Orphan Modules** | {len(orphans)} |",
            "",
            "## 🧭 Navigation & Core Entry Points",
            "Modules at the top of the dependency hierarchy:",
        ]

        if entry_points:
            for ep in entry_points:
                lines.append(f"- [[{ep}]]")
        else:
            lines.append("*No distinct entry points detected.*")
        lines.append("")

        lines.append("## 🌟 Central Hub Modules")
        lines.append("Modules with the highest incoming dependencies (core backbone):")
        if hubs:
            for hub_name, count in hubs:
                lines.append(f"- [[{hub_name}]] — depended on by **{count}** other modules")
        else:
            lines.append("*No central hubs.*")
        lines.append("")

        if self.cycles:
            lines.append("## ⚠️ Circular Dependencies Report")
            lines.append("> [!WARNING] The following circular import loops were detected:")
            for idx, cycle in enumerate(self.cycles, 1):
                cycle_str = " ➔ ".join([f"[[{c}]]" for c in cycle])
                lines.append(f"> {idx}. {cycle_str}")
            lines.append("")

        if orphans:
            lines.append("## 👻 Orphan / Dead Code Modules")
            lines.append("Modules with 0 internal incoming and outgoing connections:")
            for orph in orphans:
                lines.append(f"- [[{orph}]]")
            lines.append("")

        lines.append("## 📚 Complete Module Directory")
        for mod_name in sorted(self.graph.nodes.keys()):
            node = self.graph.nodes[mod_name]
            meta = f"*(LOC: {node.parsed.code_loc}, In: {node.in_degree}, Out: {node.out_degree})*"
            lines.append(f"- [[{mod_name}]] {meta}")

        lines.append("")
        lines.append("---\n💡 **Tip:** Press **`Ctrl + G`** in Obsidian to open the interactive physics Graph View!")

        overview_file = self.output_dir / "_Overview.md"
        overview_file.write_text("\n".join(lines), encoding="utf-8")
