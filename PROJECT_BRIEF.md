# Obsidian Code Graph (Hybrid Plugin)

## 📌 Project Overview
**Obsidian Code Graph** is a hybrid Obsidian plugin and developer tool that transforms any codebase into an interactive, physics-driven knowledge graph inside Obsidian.

Instead of manually creating and linking notes, the Python core uses **Abstract Syntax Trees (AST)** to automatically reverse-engineer codebases:
- Converts every module/file into an interconnected Markdown note with real Obsidian `[[wiki-links]]`.
- Identifies **circular dependencies** and highlights them with warning badges.
- Detects **dead/orphan code** with zero incoming dependencies.
- Surfaces code metrics, complexity scores, and class/function outlines with docstrings.
- Wrapped in a lightweight **TypeScript Obsidian Plugin** allowing developers to click a single button inside Obsidian to scan and visualize any project.

---

## 🛠️ Tech Stack & Architecture

```
                    ┌───────────────────────────────┐
                    │     Obsidian App UI (TS)      │
                    │   Sidebar Button / Command    │
                    └───────────────┬───────────────┘
                                    │ (triggers child_process)
                                    ▼
                    ┌───────────────────────────────┐
                    │    Python Core Engine (AST)   │
                    │  * File Scanner & AST Parser  │
                    │  * Dependency Graph Builder   │
                    │  * Cycle Detection (DFS)      │
                    └───────────────┬───────────────┘
                                    │ (generates linked notes)
                                    ▼
                    ┌───────────────────────────────┐
                    │     Obsidian Vault Output     │
                    │   * Markdown with [[links]]   │
                    │   * Tags (#entrypoint, etc.)  │
                    │   * Native Graph View renders │
                    └───────────────────────────────┘
```

- **Core Engine (Python 3.10+):** `ast`, `pathlib`, `json`, `os`
- **Plugin Wrapper (TypeScript):** Obsidian Plugin API, Node.js `child_process`
- **Visuals:** Obsidian's native force-directed Graph View + Obsidian Canvas

---

## 👤 Developer Context
- **GitHub Username:** [itsnacho](https://github.com/itsnacho)
- **Target Timeline:** 3–4 day sprint (~2.5–3 hours/day)
- **Goal:** Build an impressive, highly practical open-source project featured on GitHub profile README.
