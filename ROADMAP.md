# 4-Day Sprint Roadmap

## 📅 Day 1: Python AST Import Parser & Linker (~2.5 hrs)
- [x] Set up directory scanner using `pathlib.Path.rglob("*.py")`
- [x] Implement AST visitor using `ast.parse()` to extract:
  - `import x`
  - `from y import z`
  - Relative imports (`from . import a`, `from ..b import c`)
- [x] Map internal project imports vs external 3rd-party packages (e.g., standard library vs pip packages)
- [x] Build in-memory directed graph of files and dependencies: `{ "module": [dependencies...] }`
- [x] Run test on sample project to verify extracted links, cycle detection, and dead code detection

## 📅 Day 2: Vault Generator & Cycle Detection (~3 hrs)
- [x] Implement cycle detection algorithm (Depth-First Search) to catch circular imports
- [x] Generate Markdown note templates:
  - Frontmatter metadata (`type: module`, `imports_count`, `complexity`)
  - Obsidian wiki-links: `[[imported_module]]`
  - Class and function definitions table/list with docstrings
  - Callout warning box for circular dependencies (`> [!WARNING] Circular Dependency Detected`)
- [x] Output generated notes into an `.obsidian` vault structure
- [x] **Milestone 1:** Open folder in Obsidian Desktop and verify that the native Graph View renders all nodes and physics connections!

## 📅 Day 3: Obsidian TypeScript Plugin Wrapper (~3 hrs)
- [x] Initialize Obsidian plugin boilerplate (`manifest.json`, `package.json`, `main.ts`)
- [x] Add Command Palette entry: `Code Graph: Analyze Current Project`
- [x] Add Sidebar ribbon icon (network graph icon)
- [x] Implement folder picker / settings input for Python path and repository path
- [x] Spawn Python engine in background via Node's `child_process.execFile`
- [x] Display native Obsidian notices (`new Notice("Generating codebase graph...")`, `new Notice("Graph ready!")`)
- [x] Auto-trigger vault refresh once notes are written

## 📅 Day 4: Testing, Demo & GitHub Showcase (~2 hrs)
- [x] Test end-to-end on sample project and engine repos
- [x] Verify Obsidian force-directed graph view with color-coded node clusters
- [x] Write rich GitHub README with installation instructions, architecture diagrams, and usage guides
- [x] Publish repository to `https://github.com/itsnacho/obsidian-code-graph`
