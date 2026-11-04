// GitHub Copilot CLI extension for the AI Engineering scaffold.
//
// Thin wrapper around the canonical bin/bootstrap_ai_engineering.sh (bundled as a
// synced copy under ../skills/bootstrap-ai-engineering/assets/). The script builds
// the skeleton and returns an LLM Ingest Prompt; Copilot then implements the four
// reference guides itself, exactly as any other harness would.
import { joinSession } from "@github/copilot-sdk/extension";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const execFileAsync = promisify(execFile);

// Self-locating path resolution (symlinks resolve to the real plugin location).
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BOOTSTRAP_SCRIPT = path.join(
  __dirname, "..", "skills", "bootstrap-ai-engineering", "assets", "bin", "bootstrap_ai_engineering.sh"
);

// The scaffold is a bash script: macOS/Linux natively, Windows via Git Bash or WSL.
const BASH_BIN = process.env.BASH_BIN || "bash";
const PYTHON_BIN = process.env.PYTHON_BIN || (process.platform === "win32" ? "python" : "python3");

const session = await joinSession({
  tools: [
    {
      name: "bootstrap_ai_engineering",
      description:
        "Bootstraps the AI Engineering scaffold (LLM Wiki, Drift Registry, Session Workflows, Elephant-Goldfish Verification) " +
        "into a project and returns an LLM Ingest Prompt. After calling this tool, implement the returned prompt's instructions yourself.",
      parameters: {
        type: "object",
        properties: {
          targetDir: { type: "string", description: "Project directory to scaffold (default: current directory)" },
          harness: {
            type: "string",
            description: "Agent harness(es), comma-separated: antigravity, claude, codex, copilot, or all (default: copilot)"
          },
          wikiDb: { type: "string", enum: ["none", "postgres"], description: "Wiki metadata index (default: none)" },
          dbUser: { type: "string", description: "Postgres user (only with wikiDb=postgres; default: $USER)" },
          dbName: { type: "string", description: "Postgres database (only with wikiDb=postgres; default: wiki)" },
          author: { type: "string", description: "Author name for retrospectives and wiki pages (default: git user.name)" }
        }
      },
      handler: async ({ targetDir = ".", harness = "copilot", wikiDb = "none", dbUser, dbName, author }) => {
        if (!fs.existsSync(BOOTSTRAP_SCRIPT)) {
          return `Error: bundled bootstrap script not found at ${BOOTSTRAP_SCRIPT}. Reinstall the plugin.`;
        }
        const args = [
          BOOTSTRAP_SCRIPT,
          "--target-dir", path.resolve(targetDir),
          "--harness", harness,
          "--wiki-db", wikiDb
        ];
        if (wikiDb === "postgres" && dbUser) args.push("--db-user", dbUser);
        if (wikiDb === "postgres" && dbName) args.push("--db-name", dbName);
        if (author) args.push("--author", author);

        try {
          const { stdout, stderr } = await execFileAsync(BASH_BIN, args);
          return `${stdout}\n${stderr}\n\nNext: implement the ingest prompt above in ${path.resolve(targetDir)} (do not ask the user to copy it).`;
        } catch (error) {
          return `Bootstrap failed: ${error.message}\n\nSTDOUT:\n${error.stdout || ""}\n\nSTDERR:\n${error.stderr || ""}`;
        }
      }
    },
    {
      name: "drift_check",
      description: "Runs scripts/drift_enforcer.py against docs/drift_registries/ in the current workspace.",
      parameters: {
        type: "object",
        properties: {
          stamp: {
            type: "boolean",
            description: "Pass true to stamp current baselines (only during session wrapup, with user approval)"
          }
        }
      },
      handler: async ({ stamp = false }) => {
        const scriptPath = path.join(process.cwd(), "scripts", "drift_enforcer.py");
        if (!fs.existsSync(scriptPath)) {
          return "Error: scripts/drift_enforcer.py not found in current directory. Run bootstrap_ai_engineering first.";
        }
        const cmdArgs = stamp ? [scriptPath, "--stamp"] : [scriptPath];
        try {
          const { stdout } = await execFileAsync(PYTHON_BIN, cmdArgs);
          return stdout || "(Drift check passed cleanly)";
        } catch (err) {
          return `Drift check failed:\n${err.stdout || err.message}\n${err.stderr || ""}`;
        }
      }
    }
  ],

  hooks: {
    // Git guardrails: remote mutations require explicit human approval.
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
            session.log(`Blocked restricted command by governance: ${cmd}`);
            return {
              allow: false,
              reason: "Blocked by Agent Governance: remote repository mutations (push, PR merge/close/delete) require explicit human approval."
            };
          }
        }
      }
      return { allow: true };
    }
  }
});
