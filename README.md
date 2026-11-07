# 🕸️ Obsidian Code Graph

> Turn any codebase into an interactive, physics-driven knowledge graph inside Obsidian.

[![GitHub](https://img.shields.io/badge/Author-itsnacho-blue.svg)](https://github.com/itsnacho)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-yellow.svg)](https://www.python.org/)

**Obsidian Code Graph** parses any software project using Abstract Syntax Trees (AST) and generates a fully interconnected Obsidian vault. Every module becomes a note, every import becomes an Obsidian `[[wiki-link]]`, and circular dependencies are automatically flagged.

---

## ✨ Features
- 🚀 **Zero Manual Linking:** Automatically maps code files into connected Markdown notes.
- 🔴 **Circular Dependency Detection:** Highlights toxic dependency loops before they cause runtime bugs.
- 👻 **Orphan Code Finder:** Detects dead or unreferenced modules floating with zero incoming imports.
- 🔌 **Obsidian Native Integration:** Works directly with Obsidian's built-in Graph View, Canvas, and search.

---

## 🏗️ Architecture
- `src/engine/`: Python-based AST parser, dependency analyzer, and vault generator.
- `src/plugin/`: Lightweight TypeScript Obsidian plugin wrapper.

---

## 🚀 Quickstart
*(In development - Day 1 Sprint)*
