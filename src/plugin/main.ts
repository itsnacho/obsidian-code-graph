import {
  FileSystemAdapter,
  Notice,
  Plugin,
  TFile,
} from "obsidian";
import { spawn } from "child_process";
import * as path from "path";
import * as fs from "fs";

import {
  CodeGraphPluginSettings,
  CodeGraphSettingTab,
  DEFAULT_SETTINGS,
} from "./settings";
import { ScanModal } from "./scanModal";

export default class CodeGraphPlugin extends Plugin {
  settings: CodeGraphPluginSettings;

  async onload() {
    await this.loadSettings();

    // Auto-detect engine path if not configured
    if (!this.settings.enginePath) {
      this.detectDefaultEnginePath();
    }

    // Ribbon Icon (Left sidebar)
    this.addRibbonIcon("network", "Scan Codebase (Code Graph)", () => {
      new ScanModal(this.app, this).open();
    });

    // Command Palette: Scan Codebase
    this.addCommand({
      id: "scan-codebase",
      name: "Scan Project and Generate Graph",
      callback: () => {
        new ScanModal(this.app, this).open();
      },
    });

    // Command Palette: Open Graph View Shortcut
    this.addCommand({
      id: "open-graph-view",
      name: "Open Graph View",
      callback: () => {
        // @ts-ignore
        this.app.commands.executeCommandById("graph:open");
      },
    });

    // Settings Tab
    this.addSettingTab(new CodeGraphSettingTab(this.app, this));
  }

  detectDefaultEnginePath() {
    // Look for the engine repo in common locations
    const possiblePaths = [
      __dirname,
      "C:\\Users\\Arnav Modi\\Documents\\vscode\\obsidian-code-graph",
      path.resolve(__dirname, "../../.."),
    ];

    for (const p of possiblePaths) {
      if (fs.existsSync(path.join(p, "src", "engine", "cli.py"))) {
        this.settings.enginePath = p;
        this.saveSettings();
        break;
      }
    }
  }

  async runEngine(targetPath: string, outputSubfolder: string): Promise<void> {
    if (!(this.app.vault.adapter instanceof FileSystemAdapter)) {
      new Notice("❌ Code Graph requires the desktop version of Obsidian.");
      return;
    }

    const vaultBasePath = this.app.vault.adapter.getBasePath();
    const outputFullPath = path.join(vaultBasePath, outputSubfolder);

    if (!this.settings.enginePath || !fs.existsSync(this.settings.enginePath)) {
      new Notice("❌ Engine Path not configured. Please set it in Code Graph plugin settings.");
      return;
    }

    const notice = new Notice("🕸️ Code Graph: Parsing codebase and building graph...", 0);

    try {
      const pythonExe = this.settings.pythonPath || (process.platform === "win32" ? "py" : "python3");
      const args: string[] = [];

      if (pythonExe === "py") {
        args.push("-3");
      }

      args.push("-m", "src.engine.cli", targetPath, "-o", outputFullPath);

      const processEnv = {
        ...process.env,
        PYTHONIOENCODING: "utf-8",
        PYTHONUNBUFFERED: "1",
      };

      const child = spawn(pythonExe, args, {
        cwd: this.settings.enginePath,
        env: processEnv,
        shell: false,
      });

      let stdoutData = "";
      let stderrData = "";

      child.stdout.on("data", (data) => {
        stdoutData += data.toString();
      });

      child.stderr.on("data", (data) => {
        stderrData += data.toString();
      });

      child.on("close", async (code) => {
        notice.hide();

        if (code === 0) {
          new Notice("✅ Code Graph generated successfully!", 5000);

          // Give Obsidian a brief moment to index the new files
          setTimeout(async () => {
            const overviewPath = `${outputSubfolder}/_Overview.md`;
            const file = this.app.vault.getAbstractFileByPath(overviewPath);
            if (file instanceof TFile) {
              const leaf = this.app.workspace.getLeaf(false);
              await leaf.openFile(file);
            }

            // Open graph view
            // @ts-ignore
            if (this.app.commands) {
              // @ts-ignore
              this.app.commands.executeCommandById("graph:open");
            }
          }, 600);
        } else {
          console.error("Code Graph error:", stderrData || stdoutData);
          const errDetail = (stderrData || stdoutData).trim();
          new Notice(`❌ Generation failed: ${errDetail || `exit code ${code}`}`, 10000);
        }
      });

      child.on("error", (err) => {
        notice.hide();
        console.error("Code Graph spawn error:", err);
        new Notice(`❌ Failed to spawn Python: ${err.message}`, 8000);
      });
    } catch (e: any) {
      notice.hide();
      new Notice(`❌ Unexpected error: ${e.message}`, 8000);
    }
  }

  async loadSettings() {
    this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
  }

  async saveSettings() {
    await this.saveData(this.settings);
  }
}
