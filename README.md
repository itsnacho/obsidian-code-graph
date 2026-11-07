# 🕸️ Obsidian Code Graph

> Turn any Python codebase into an interactive, physics-driven knowledge graph inside Obsidian.

[![GitHub](https://img.shields.io/badge/author-itsnacho-blue.svg)](https://github.com/itsnacho)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-yellow.svg)](https://www.python.org/)
[![Obsidian Plugin](https://img.shields.io/badge/obsidian-plugin-purple.svg)](https://obsidian.md)

Reading an unfamiliar codebase through a flat file tree in VS Code is rough. You can't easily see how modules connect, which files act as central hubs, where circular import bugs are hiding, or which abandoned files are floating around as dead code.

**Obsidian Code Graph** bridges that gap. It reverse-engineers any Python project using Abstract Syntax Trees (AST) and generates a complete Obsidian vault where every file becomes a Markdown note, every import becomes an Obsidian `[[wiki-link]]`, and Obsidian's native physics engine clusters your code into an architectural galaxy.

---

## ✨ Features

- ⚡ **Zero Manual Linking:** Automatically parses `import x`, `from y import z`, and relative imports (`from . import a`, `from ..b import c`) using Python's C-level `ast` module.
- 🔴 **Circular Dependency Detection:** Runs Depth-First Search (DFS) across the dependency graph to catch circular import loops before they cause runtime bugs, highlighting them with red badges.
- 👻 **Dead Code / Orphan Finder:** Flags files with zero incoming references so you can safely identify unused code for deletion.
- 🎨 **Tuned Graph View Preset:** Drops an auto-configured `.obsidian/graph.json` with tuned gravity, link distance, directional arrows, and color-coded node groups:
  - 🔴 **Red:** Circular dependency loops
  - 🟠 **Orange:** Orphan / dead code candidates
  - 🟣 **Purple:** Core entry points (e.g. `main`, `cli`)
  - 🟢 **Teal:** Standard modules
- 🔌 **Dual Mode:** Use it as a **1-click Obsidian Plugin** right inside the app, or as a **Standalone CLI** from your terminal.

---

## 🏗️ Architecture

```
                      ┌─────────────────────────────────┐
                      │    Target Python Repository     │
                      └────────────────┬────────────────┘
                                       │
                                       ▼
                      ┌─────────────────────────────────┐
                      │    Python AST Engine (Core)     │
                      │  * scanner.py  (file crawler)   │
                      │  * parser.py   (AST visitor)    │
                      │  * resolver.py (relative paths) │
                      │  * graph.py    (DFS cycle check)│
                      └────────────────┬────────────────┘
                                       │
                                       ▼
                      ┌─────────────────────────────────┐
                      │    Vault Generator              │
                      │  * Formatted .md with [[links]] │
                      │  * Method & class outlines      │
                      │  * .obsidian/graph.json colors  │
                      └────────────────┬────────────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
      ┌───────────────────────────┐         ┌───────────────────────────┐
      │     Standalone CLI        │         │   Obsidian Plugin (TS)    │
      │  Run directly in terminal │         │  1-click sidebar button   │
      └───────────────────────────┘         └───────────────────────────┘
```

---

## 🔌 Method 1: Using the Obsidian Plugin (Recommended)

You can run Code Graph directly inside Obsidian with a single click.

### Step 1: Build the plugin
Make sure you have Node.js installed, then build the plugin bundle:

```bash
cd src/plugin
npm install
npm run build
```
This generates `src/plugin/main.js` and `manifest.json`.

### Step 2: Install into your Obsidian Vault
Copy the plugin folder into your vault's plugin directory:

```bash
# On Windows (PowerShell):
New-Item -ItemType Directory -Force -Path "C:\path\to\your-vault\.obsidian\plugins\obsidian-code-graph"
Copy-Item "src\plugin\manifest.json" "C:\path\to\your-vault\.obsidian\plugins\obsidian-code-graph\"
Copy-Item "src\plugin\main.js" "C:\path\to\your-vault\.obsidian\plugins\obsidian-code-graph\"
```

### Step 3: Enable the plugin in Obsidian
1. Open Obsidian and open your vault.
2. Go to **Settings** (`Ctrl + ,`) $\rightarrow$ **Community plugins**.
3. Toggle on **Turn on community plugins**.
4. Scroll down to **Installed plugins** and switch on **Obsidian Code Graph**.

### Step 4: Scan and graph any codebase!
1. Click the new **network graph icon** on Obsidian's left ribbon (or hit `Ctrl + P` and search for `Scan Project and Generate Graph`).
2. Enter the path to any Python project on your machine.
3. Click **Scan & Generate Graph**.
4. In under a second, the plugin will index the codebase, open the project overview note, and launch the interactive graph view!

---

## 💻 Method 2: Using the Standalone CLI

If you prefer the terminal or want to run it without opening the plugin, the Python engine works standalone:

### Quick Scan (Terminal Report Only)
To inspect a codebase and see metrics, hubs, orphans, and cycle reports printed right in your terminal:

```bash
# Windows
py -3 -m src.engine.cli "C:\path\to\target-codebase"

# macOS / Linux
python3 -m src.engine.cli "/path/to/target-codebase"
```

### Generate a Vault from CLI
Add the `-o` flag to spit out a ready-to-open Obsidian vault:

```bash
py -3 -m src.engine.cli "C:\path\to\target-codebase" -o my_code_vault
```

Then in Obsidian, click **Open folder as vault**, choose `my_code_vault`, and hit **`Ctrl + G`**!

---

## 📋 What a Generated Note Looks Like

Every Python module gets its own dedicated documentation card:

```markdown
---
type: module
module: auth.service
file_path: auth/service.py
code_loc: 48
classes_count: 1
tags:
  - #code/module
  - #status/circular-dependency
---

# 📦 `auth.service`

> [!ABSTRACT] Module Overview
> Coordinates user login, session token issuance, and password verification.

> [!WARNING] Circular Dependency Detected
> • Loop: `auth.service` ➔ `database` ➔ `auth.service`

## 🔗 Dependencies (Imports)
- [[auth.crypto]]
- [[config]]
- [[database]]

## 📥 Dependents (Imported By)
- [[database]]
- [[main]]

## 🏛️ Classes
### `class AuthService` (Line 10)
> Core authentication coordinator.
- `def register(self, username: str, password: str) -> bool`
- `def login(self, username: str, password: str) -> bool`
```

---

## ⚙️ Plugin Configuration

Open **Settings $\rightarrow$ Obsidian Code Graph** to adjust:
- **Python Command or Path:** defaults to `py` (Windows) or `python3` (Mac/Linux).
- **Engine Repository Path:** path to the `obsidian-code-graph` root if installed in an external vault.
- **Default Target Codebase:** pre-fills your preferred repo path so you don't have to retype it.
- **Output Folder Name:** subfolder inside the vault where notes will be written (default: `CodeGraph`).

---

## 🛠️ Project Structure

```
obsidian-code-graph/
├── src/
│   ├── engine/                # Python Core
│   │   ├── scanner.py         # File discovery & module naming
│   │   ├── parser.py          # AST visitor (imports, classes, functions)
│   │   ├── resolver.py        # Import resolution & stdlib filter
│   │   ├── graph.py           # Dependency graph & DFS cycle detector
│   │   ├── vault_generator.py # Markdown generator & .obsidian configs
│   │   └── cli.py             # CLI runner & diagnostics printer
│   └── plugin/                # Obsidian TypeScript Plugin
│       ├── main.ts            # Plugin lifecycle & Python runner
│       ├── settings.ts        # In-app settings tab
│       ├── scanModal.ts       # Pop-up prompt modal
│       ├── esbuild.config.mjs # Production bundler
│       └── manifest.json      # Obsidian plugin metadata
├── tests/
│   └── sample_project/        # Test suite with intentional cycles & orphans
└── README.md
```

---

## 📄 License

MIT License — built by [itsnacho](https://github.com/itsnacho). Feel free to fork, customize, or contribute!
