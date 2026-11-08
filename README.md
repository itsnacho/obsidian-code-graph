# Obsidian Code Graph

> Turn any Python codebase into an interactive, physics-driven knowledge graph inside Obsidian.

[![GitHub](https://img.shields.io/badge/author-itsnacho-blue.svg)](https://github.com/itsnacho)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-yellow.svg)](https://www.python.org/)

**Obsidian Code Graph** reverse-engineers any Python project using Abstract Syntax Trees (AST) and generates a fully linked Obsidian vault. Every module becomes a note, imports become `[[wiki-links]]`, and circular dependencies or dead code are automatically flagged.

---

## Features

- **Zero Manual Linking:** Automatically maps imports and relative paths into native Obsidian `[[wiki-links]]`.
- **Circular Dependency Detection:** Runs DFS across the dependency graph to catch circular import loops.
- **Dead Code Finder:** Identifies orphan files with zero incoming references.
- **Force-Directed Graph:** Comes with tuned physics, directional arrows, and color-coded node groups (red for cycles, orange for orphans, purple for entrypoints).

---

## Quickstart (Obsidian Plugin)

Clone or copy this repository directly into your vault's plugins folder:

```bash
git clone https://github.com/itsnacho/obsidian-code-graph.git "<path-to-vault>/.obsidian/plugins/obsidian-code-graph"
```

1. Open Obsidian $\rightarrow$ **Settings** $\rightarrow$ **Community plugins** $\rightarrow$ Enable **Obsidian Code Graph**.
2. Click the **network icon** on the left ribbon (or press `Ctrl + P` $\rightarrow$ *"Scan Project and Generate Graph"*).
3. Enter the path to your Python project and click **Scan**.

---

## Standalone CLI

You can also run the engine directly from your terminal without opening Obsidian:

```bash
# Print diagnostic report in terminal
py -3 -m src.engine.cli "path/to/project"

# Generate a ready-to-open Obsidian vault
py -3 -m src.engine.cli "path/to/project" -o my_code_vault
```

---

## How It Works

1. **AST Engine (`src/engine/`):** Scans `.py` files and uses Python's standard `ast` module to extract imports, classes, and functions without running any code.
2. **Graph Analysis:** Builds a directed graph to calculate dependencies, detect cycles, and spot orphan modules.
3. **Vault Generator:** Generates Markdown notes with docstrings, method outlines, and Obsidian graph presets.
4. **Plugin Wrapper (`src/plugin/`):** TypeScript bridge that triggers scans in the background and auto-refreshes your vault.

---

## License

MIT — built by [itsnacho](https://github.com/itsnacho).
