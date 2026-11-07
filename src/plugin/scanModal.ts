import { App, Modal, Setting, Notice } from "obsidian";
import type CodeGraphPlugin from "./main";

export class ScanModal extends Modal {
  plugin: CodeGraphPlugin;
  targetDir: string;
  outputFolder: string;

  constructor(app: App, plugin: CodeGraphPlugin) {
    super(app);
    this.plugin = plugin;
    this.targetDir = this.plugin.settings.defaultTargetDir;
    this.outputFolder = this.plugin.settings.outputFolder || "CodeGraph";
  }

  onOpen() {
    const { contentEl } = this;
    contentEl.empty();

    contentEl.createEl("h2", { text: "🕸️ Obsidian Code Graph: Analyze Codebase" });
    contentEl.createEl("p", {
      text: "Enter the path of the Python project you want to reverse-engineer into an interactive knowledge graph.",
    });

    new Setting(contentEl)
      .setName("Project Directory")
      .setDesc("Absolute path to the Python repository on your computer.")
      .addText((text) =>
        text
          .setPlaceholder("C:\\path\\to\\my-codebase")
          .setValue(this.targetDir)
          .onChange((value) => {
            this.targetDir = value.trim();
          })
      );

    new Setting(contentEl)
      .setName("Vault Destination Folder")
      .setDesc("Folder name inside this vault where the linked notes will be written.")
      .addText((text) =>
        text
          .setPlaceholder("CodeGraph")
          .setValue(this.outputFolder)
          .onChange((value) => {
            this.outputFolder = value.trim() || "CodeGraph";
          })
      );

    new Setting(contentEl)
      .addButton((btn) =>
        btn
          .setButtonText("Scan & Generate Graph")
          .setCta()
          .onClick(async () => {
            if (!this.targetDir) {
              new Notice("❌ Please enter a valid project directory path.");
              return;
            }
            this.close();
            await this.plugin.runEngine(this.targetDir, this.outputFolder);
          })
      )
      .addButton((btn) =>
        btn.setButtonText("Cancel").onClick(() => {
          this.close();
        })
      );
  }

  onClose() {
    const { contentEl } = this;
    contentEl.empty();
  }
}
