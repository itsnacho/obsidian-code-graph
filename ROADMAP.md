# 4-Day Sprint Roadmap

## 📅 Day 1: Python AST Import Parser & Linker (~2.5 hrs)
- [ ] Set up directory scanner using `pathlib.Path.rglob("*.py")`
- [ ] Implement AST visitor using `ast.parse()` to extract:
  - `import x`
  - `from y import z`
  - Relative imports (`from . import a`, `from ..b import c`)
- [ ] Map internal project imports vs external 3rd-party packages (e.g., standard library vs pip packages)
- [ ] Build in-memory directed graph of files and dependencies: `{ "module": [dependencies...] }`
- [ ] Run test on existing Python project (`exml` or `itsnacho`) to verify extracted links

## 📅 Day 2: Vault Generator & Cycle Detection (~3 hrs)
- [ ] Implement cycle detection algorithm (Depth-First Search) to catch circular imports
- [ ] Generate Markdown note templates:
  - Frontmatter metadata (`type: module`, `imports_count`, `complexity`)
  - Obsidian wiki-links: `[[imported_module]]`
  - Class and function definitions table/list with docstrings
  - Callout warning box for circular dependencies (`> [!WARNING] Circular Dependency Detected`)
- [ ] Output generated notes into an `.obsidian` vault structure
- [ ] **Milestone 1:** Open folder in Obsidian Desktop and verify that the native Graph View renders all nodes and physics connections!

## 📅 Day 3: Obsidian TypeScript Plugin Wrapper (~3 hrs)
- [ ] Initialize Obsidian plugin boilerplate (`manifest.json`, `package.json`, `main.ts`)
- [ ] Add Command Palette entry: `Code Graph: Analyze Current Project`
- [ ] Add Sidebar ribbon icon (network graph icon)
- [ ] Implement folder picker / settings input for Python path and repository path
- [ ] Spawn Python engine in background via Node's `child_process.execFile`
- [ ] Display native Obsidian notices (`new Notice("Generating codebase graph...")`, `new Notice("Graph ready!")`)
- [ ] Auto-trigger vault refresh once notes are written

## 📅 Day 4: Testing, Demo & GitHub Showcase (~2 hrs)
- [ ] Test end-to-end on 2 different open-source Python repos
- [ ] Record a 5–10 second demo GIF showing:
  - Clicking the button in Obsidian
  - Opening the native Graph View and watching nodes bounce and cluster
- [ ] Write rich GitHub README with installation instructions, screenshots, and architecture diagrams
- [ ] Publish repository to `https://github.com/itsnacho/obsidian-code-graph`
- [ ] Feature the project in [`itsnacho/itsnacho`](https://github.com/itsnacho/itsnacho) profile README
