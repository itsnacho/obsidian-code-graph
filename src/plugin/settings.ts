import { App, PluginSettingTab, Setting } from "obsidian";
import type CodeGraphPlugin from "./main";

export interface CodeGraphPluginSettings {
  pythonPath: string;
  enginePath: string;
  defaultTargetDir: string;
  outputFolder: string;
}

export const DEFAULT_SETTINGS: CodeGraphPluginSettings = {
  pythonPath: process.platform === "win32" ? "py" : "python3",
  enginePath: "",
  defaultTargetDir: "",
  outputFolder: "CodeGraph",
};

export class CodeGraphSettingTab extends PluginSettingTab {
  plugin: CodeGraphPlugin;

  constructor(app: App, plugin: CodeGraphPlugin) {
    super(app, plugin);
    this.plugin = plugin;
  }

  display(): void {
    const { containerEl } = this;
    containerEl.empty();

    containerEl.createEl("h2", { text: "🕸️ Obsidian Code Graph Settings" });

    new Setting(containerEl)
      .setName("Python Command or Path")
      .setDesc("The Python 3.10+ executable used to run the AST engine (e.g. 'py', 'python3', or full path).")
      .addText((text) =>
        text
          .setPlaceholder("py or python3")
          .setValue(this.plugin.settings.pythonPath)
          .onChange(async (value) => {
            this.plugin.settings.pythonPath = value.trim();
            await this.plugin.saveSettings();
          })
      );

    new Setting(containerEl)
      .setName("Engine Repository Path")
      .setDesc("Absolute path to the obsidian-code-graph repository root containing the 'src/engine' folder.")
      .addText((text) =>
        text
          .setPlaceholder("C:\\path\\to\\obsidian-code-graph")
          .setValue(this.plugin.settings.enginePath)
          .onChange(async (value) => {
            this.plugin.settings.enginePath = value.trim();
            await this.plugin.saveSettings();
          })
      );

    new Setting(containerEl)
      .setName("Default Target Codebase Path")
      .setDesc("Optional default directory of the Python project you want to scan.")
      .addText((text) =>
        text
          .setPlaceholder("C:\\path\\to\\my-python-project")
          .setValue(this.plugin.settings.defaultTargetDir)
          .onChange(async (value) => {
            this.plugin.settings.defaultTargetDir = value.trim();
            await this.plugin.saveSettings();
          })
      );

    new Setting(containerEl)
      .setName("Output Folder Name")
      .setDesc("Folder inside this Obsidian vault where notes and diagrams will be generated.")
      .addText((text) =>
        text
          .setPlaceholder("CodeGraph")
          .setValue(this.plugin.settings.outputFolder)
          .onChange(async (value) => {
            this.plugin.settings.outputFolder = value.trim() || "CodeGraph";
            await this.plugin.saveSettings();
          })
      );
  }
}
