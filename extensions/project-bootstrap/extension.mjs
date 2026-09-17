import { joinSession } from "@github/copilot-sdk/extension";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const execFileAsync = promisify(execFile);

// Self-locating path resolution (works regardless of where hvr-agentic-os is cloned)
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BOOTSTRAP_SCRIPT = path.join(__dirname, "skills", "project-bootstrapper", "bootstrap.py");

// Cross-platform Python executable resolution (Windows uses 'python', Unix uses 'python3')
const PYTHON_BIN = process.env.PYTHON_BIN || (process.platform === "win32" ? "python" : "python3");

const session = await joinSession({
  tools: [
    {
      name: "bootstrap_project",
      description: "Bootstraps a new repository workspace with Obsidian vault, local SQLite Cadence goal engine, local SQLite wiki DB, and 9-layer governance.",
      parameters: {
        type: "object",
        properties: {
          name: {
            type: "string",
            description: "Project name (e.g., 'Payment Gateway Service')"
          },
          targetDir: {
            type: "string",
            description: "Target directory path for the new repository"
          },
          archetype: {
            type: "string",
            enum: ["software_engineering", "agentic_os", "creative_operations", "data_platform", "minimal_research"],
            description: "Domain archetype"
          },
          taskPrompt: {
            type: "string",
            description: "Description of what this project builds or manages"
          },
          flavor: {
            type: "string",
            enum: ["copilot", "antigravity", "universal"],
            description: "Agent flavor (default: copilot)"
          }
        },
        required: ["name", "targetDir", "archetype", "taskPrompt"]
      },
      handler: async ({ name, targetDir, archetype, taskPrompt, flavor = "copilot" }) => {
        const resolvedTarget = path.resolve(targetDir);
        const args = [
          BOOTSTRAP_SCRIPT,
          "--name", name,
          "--target-dir", resolvedTarget,
          "--archetype", archetype,
          "--flavor", flavor,
          "--cadence-backend", "sqlite",
          "--wiki-backend", "sqlite",
          "--task-prompt", taskPrompt,
          "--verbose"
        ];

        try {
          const { stdout, stderr } = await execFileAsync(PYTHON_BIN, args);
          return `Bootstrap completed successfully at ${resolvedTarget}.\n\nOutput:\n${stdout}\n${stderr}`;
        } catch (error) {
          return `Bootstrap failed: ${error.message}\n\nSTDOUT:\n${error.stdout || ""}\n\nSTDERR:\n${error.stderr || ""}`;
        }
      }
    },
    {
      name: "cadence_cli",
      description: "Interacts with the local SQLite Cadence goal engine in the current workspace (list, create, complete, defer, advance, week-plan, saturday-sync).",
      parameters: {
        type: "object",
        properties: {
          subcommand: {
            type: "string",
            enum: ["list", "create", "complete", "defer", "advance", "week-plan", "saturday-sync"],
            description: "Cadence command to run"
          },
          args: {
            type: "array",
            items: { type: "string" },
            description: "Additional arguments to pass to the cadence CLI"
          }
        },
        required: ["subcommand"]
      },
      handler: async ({ subcommand, args = [] }) => {
        const scriptPath = path.join(process.cwd(), "scripts", "cadence.py");
        if (!fs.existsSync(scriptPath)) {
          return "Error: scripts/cadence.py not found in current directory. Is this a bootstrapped workspace?";
        }
        try {
          const { stdout } = await execFileAsync(PYTHON_BIN, [scriptPath, subcommand, ...args]);
          return stdout || "(Command completed with no output)";
        } catch (err) {
          return `Cadence execution error: ${err.message}\nSTDOUT: ${err.stdout || ""}\nSTDERR: ${err.stderr || ""}`;
        }
      }
    },
    {
      name: "drift_check",
      description: "Runs the drift enforcer against docs/drift_registries/ to verify AST and commit baselines.",
      parameters: {
        type: "object",
        properties: {
          stamp: {
            type: "boolean",
            description: "Pass true to stamp current baselines into registries (use only during wrapup with user approval)"
          }
        }
      },
      handler: async ({ stamp = false }) => {
        const scriptPath = path.join(process.cwd(), "scripts", "drift_enforcer.py");
        if (!fs.existsSync(scriptPath)) {
          return "Error: scripts/drift_enforcer.py not found in current directory.";
        }
        const cmdArgs = stamp ? [scriptPath, "--stamp"] : [scriptPath];
        try {
          const { stdout } = await execFileAsync(PYTHON_BIN, cmdArgs);
          return stdout || "(Drift check passed cleanly)";
        } catch (err) {
          return `Drift check failed:\n${err.stdout || err.message}\n${err.stderr || ""}`;
        }
      }
    },
    {
      name: "sync_wiki",
      description: "Re-exports markdown wiki pages and synchronizes the local SQLite wiki database (.wiki/wiki.db).",
      parameters: {
        type: "object",
        properties: {}
      },
      handler: async () => {
        const exportScript = path.join(process.cwd(), "scripts", "export_wiki.py");
        const syncScript = path.join(process.cwd(), "scripts", "sync_wiki_db.py");

        if (!fs.existsSync(exportScript) || !fs.existsSync(syncScript)) {
          return "Error: scripts/export_wiki.py or scripts/sync_wiki_db.py not found in current directory.";
        }

        try {
          const exportResult = await execFileAsync(PYTHON_BIN, [exportScript]);
          const syncResult = await execFileAsync(PYTHON_BIN, [syncScript]);
          return `Wiki sync successful.\nExport output:\n${exportResult.stdout}\nSync output:\n${syncResult.stdout}`;
        } catch (err) {
          return `Wiki sync failed: ${err.message}\nSTDOUT: ${err.stdout || ""}\nSTDERR: ${err.stderr || ""}`;
        }
      }
    },
    {
      name: "verify_workspace",
      description: "Executes the comprehensive 9-layer verification harness asserting workspace structural, DB, and governance integrity.",
      parameters: {
        type: "object",
        properties: {}
      },
      handler: async () => {
        const verifyScript = path.join(process.cwd(), "scripts", "verify_bootstrap.py");
        if (!fs.existsSync(verifyScript)) {
          return "Error: scripts/verify_bootstrap.py not found in current directory.";
        }
        try {
          const { stdout } = await execFileAsync(PYTHON_BIN, [verifyScript, "--verbose"]);
          return `Verification passed:\n${stdout}`;
        } catch (err) {
          return `Verification failed:\n${err.stdout || err.message}\n${err.stderr || ""}`;
        }
      }
    }
  ],

  hooks: {
    // 1. Automatic Context Injection: Ground Copilot on startup with active Cadence goals
    onSessionStart: async () => {
      const cadenceDb = path.join(process.cwd(), ".cadence", "cadence.db");
      if (fs.existsSync(cadenceDb)) {
        try {
          const scriptPath = path.join(process.cwd(), "scripts", "cadence.py");
          const { stdout } = await execFileAsync(PYTHON_BIN, [scriptPath, "list", "--active-only"]);
          if (stdout && stdout.trim().length > 0) {
            session.log("Injecting active Cadence sprint goals into session context.");
            return {
              contextNotes: [
                `[Cadence Active Goals]:\n${stdout}`
              ]
            };
          }
        } catch (e) {
          session.log(`Cadence goal injection check: ${e.message}`);
        }
      }
    },

    // 2. Security Firewall: Intercept shell tools to enforce enterprise git guardrails
    onPreToolUse: async ({ toolName, toolArgs }) => {
      if (toolName === "bash" || toolName === "execute_command" || toolName === "powershell") {
        const cmd = toolArgs?.command || toolArgs?.cmd || "";
        const forbiddenPatterns = [
          /\bgit\s+push\b/i,
          /\bgh\s+pr\s+(merge|close|delete)\b/i,
          /\bgh\s+repo\s+delete\b/i
        ];

        for (const pattern of forbiddenPatterns) {
          if (pattern.test(cmd)) {
            session.log(`Blocked restricted command by governance constitution: ${cmd}`);
            return {
              allow: false,
              reason: "Blocked by Agent Governance: Remote repository mutations (push, PR merge/close/delete) require explicit human approval."
            };
          }
        }
      }
      return { allow: true };
    }
  }
});
