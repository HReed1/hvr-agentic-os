# Project Bootstrapper — GitHub Copilot CLI Extension

> **Zero-Dependency, Enterprise-Safe Project Bootstrapping & Local Cadence Engine for GitHub Copilot CLI.**

This extension brings the complete HvR Informatics agentic scaffolding suite directly into GitHub Copilot CLI across **Windows (PowerShell)**, **macOS**, and **Linux**.

---

## 🌟 Capabilities

1. **Enterprise-Safe Workspace Bootstrapping (`bootstrap_project`)**:
   - Generates Obsidian-compatible vaults (mode 0755, BOM-free JSONs).
   - Provisions **Local SQLite Cadence Goal Engine** (`.cadence/cadence.db`).
   - Provisions **Local SQLite Wiki Database** (`.wiki/wiki.db`).
   - Generates domain governance constitutions (`copilot-instructions.md`, prompt templates).
   - Asserts **9-Layer Bootstrap Certification** (`scripts/verify_bootstrap.py`).
2. **Cadence Goal Engine Tool (`cadence_cli`)**:
   - Enables Copilot to list active goals, create milestones, advance sprint states, and record Saturday syncs entirely within local SQLite.
3. **Universal Drift Enforcer Tool (`drift_check`)**:
   - Runs symbol-level and AST verification against `docs/drift_registries/`.
4. **Wiki Knowledge Base Sync (`sync_wiki`)**:
   - Re-exports Markdown pages and synchronizes the local SQLite database.
5. **Active Context Injection Hook (`onSessionStart`)**:
   - Automatically detects if the current workspace has `.cadence/cadence.db` and injects active sprint goals directly into the Copilot session prompt!
6. **Enterprise Git Guardrail Hook (`onPreToolUse`)**:
   - Intercepts shell execution tools and blocks unauthorized `git push` or `gh pr merge/close/delete` commands, preventing accidental corporate remote mutations.

---

## 🔒 Enterprise & Zero-Cloud Guarantees

- **100% Local Storage:** Uses Python standard library `sqlite3` for Cadence and Wiki databases. No Firestore, no PostgreSQL server, no external API tokens.
- **Zero NPM Dependencies:** GitHub Copilot CLI automatically resolves `@github/copilot-sdk/extension`.
- **Zero Administrative Privileges on Windows:** The installer uses native **NTFS Directory Junctions**, allowing unprivileged standard corporate accounts to install and run without IT elevation.

---

## 🚀 Quick Start & Installation

### Option A: Windows (PowerShell)

1. Clone `hvr-agentic-os` to your local drive (e.g. `C:\Users\<user>\tools\hvr-agentic-os`):
   ```powershell
   git clone https://github.com/HReed1/hvr-agentic-os.git "$HOME\tools\hvr-agentic-os"
   ```

2. Run the PowerShell installer:
   ```powershell
   cd "$HOME\tools\hvr-agentic-os\extensions\project-bootstrap"
   powershell -ExecutionPolicy Bypass -File .\install.ps1
   ```

3. Launch Copilot CLI in any repository:
   ```powershell
   cd "$HOME\Projects\my-work-repo"
   copilot
   ```

---

### Option B: macOS / Linux (Bash / Zsh)

1. Clone `hvr-agentic-os`:
   ```bash
   git clone https://github.com/HReed1/hvr-agentic-os.git "$HOME/.local/share/hvr-agentic-os"
   ```

2. Run the Bash installer:
   ```bash
   cd "$HOME/.local/share/hvr-agentic-os/extensions/project-bootstrap"
   ./install.sh
   ```

3. Launch Copilot CLI in any directory:
   ```bash
   cd ~/Projects/my-project
   copilot
   ```

---

## 💬 Example Prompt Interactions with Copilot

Once installed, Copilot has native tool access. You can prompt naturally:

### Bootstrapping a New Service
> *"Bootstrap a new project in `./services/payment-processor` named 'Payment Processor' using the software_engineering archetype. We need an API service with webhook ingestion and database models."*

Copilot will invoke `bootstrap_project`, scaffolding all 9 layers with local SQLite and `.github/copilot-instructions.md`.

### Reviewing Today's Sprint Goals
> *"What are my active Cadence goals for today?"*

Copilot will execute `cadence_cli` with subcommand `list` to inspect `.cadence/cadence.db`.

### Checking Drift & Contracts
> *"Run a drift check to make sure my recent edits didn't break any registered contracts."*

Copilot will execute `drift_check` against `docs/drift_registries/`.

---

## 📂 Extension Directory Anatomy

```text
extensions/project-bootstrap/
├── extension.mjs          # Copilot CLI entry point (Node.js ESM)
├── install.ps1            # Windows PowerShell installer (NTFS Junctions)
├── install.sh             # macOS/Linux symlink installer
├── README.md              # Documentation
├── plugin.json            # Antigravity plugin manifest
└── skills/                # Scaffolding sub-skills & templates
    ├── project-bootstrapper/
    │   ├── bootstrap.py   # Master orchestrator CLI
    │   └── SKILL.md
    ├── cadence-scaffolder/
    ├── drift-registry-scaffolder/
    ├── governance-architect/
    ├── harness-scaffolder/
    ├── session-rituals-scaffolder/
    ├── wiki-db-scaffolder/
    └── workspace-scaffolder/
```
