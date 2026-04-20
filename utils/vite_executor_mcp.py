import os
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Vite Executor Suite")

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))

def get_ui_dir():
    """Lazily evaluates target directory and auto-links node_modules inside staging so npx succeeds."""
    staging_ui = os.path.join(project_root, ".staging", "ngs-variant-ui")
    if os.path.exists(staging_ui):
        base_node_modules = os.path.join(project_root, "ngs-variant-ui", "node_modules")
        staged_node_modules = os.path.join(staging_ui, "node_modules")
        
        # Link node_modules inside the staged UI folder to fix Vite dependencies
        if os.path.exists(base_node_modules) and not os.path.exists(staged_node_modules):
            try:
                os.symlink(base_node_modules, staged_node_modules)
            except Exception:
                pass
                
        return staging_ui
    return os.path.join(project_root, "ngs-variant-ui")

@mcp.tool()
def toggle_react_eval_mode(enable: bool = True) -> str:
    """
    Linked to skill: @vite-reactor-suite
    Injects or clears the `VITE_MOCK_AUTH=true` flag into the `ngs-variant-ui/.env.local` 
    file to dynamically unlock the DOM from Auth0 bounds for Headless testing.
    """
    env_local_path = os.path.join(project_root, "ngs-variant-ui", ".env.local")
    try:
        if enable:
            with open(env_local_path, "w") as f:
                f.write("VITE_MOCK_AUTH=true\n")
            return "[SUCCESS] VITE_MOCK_AUTH=true active. The React UI is now permanently unlocked for Headless Visual Evaluation."
        else:
            if os.path.exists(env_local_path):
                os.remove(env_local_path)
            return "[SUCCESS] `.env.local` cleared. The React UI has restored Auth0 JWKS Security."
    except Exception as e:
        return f"[ERROR] Failed to toggle React Eval Bound: {str(e)}"

@mcp.tool()
def build_vite_project() -> str:
    """
    Linked to skill: @vite-reactor-suite
    Executes 'npm run build' natively within the staging environment to verify
    structural integrity and basic syntactic compilation. 
    Use this to ensure the project bundles successfully before handing off to QA.
    """
    try:
        # We use --emptyOutDir to prevent build artifacts from bloating the airlock
        result = subprocess.run(["npm", "run", "build", "--", "--emptyOutDir"], cwd=get_ui_dir(), capture_output=True, text=True, timeout=300)
        output_limit = 2000
        output = result.stdout + "\n" + result.stderr
        if result.returncode == 0:
            return f"[SUCCESS] Vite Build Complete. Project bundled successfully.\n{output[-output_limit:]}"
        else:
            return f"[FAILED] Vite Build Errors:\n{output[-output_limit:]}"
    except Exception as e:
        return f"Error executing vite build: {str(e)}"

if __name__ == "__main__":
    mcp.run()
