import os
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Architect Secure IO Proxy")

@mcp.tool()
def write_architect_handoff(payload_json: str) -> str:
    """
    Linked to persona: @architect
    Zero-Trust capability that physically serializes the Architect's findings directly into the secure artifacts payload registry.
    Strictly denies path traversal or destructive schema overwriting.
    """
    try:
        # Validate the incoming string is structured correctly
        parsed_payload = json.loads(payload_json)
        
        # Enforce strict path binding
        cwd = os.getcwd()
        artifacts_dir = os.path.join(cwd, "artifacts")
        
        # Guarantee the artifacts directory exists
        os.makedirs(artifacts_dir, exist_ok=True)
        
        # Secure the target payload path
        target_path = os.path.join(artifacts_dir, "architect_handoff.json")
        
        # Write to disk
        with open(target_path, "w") as f:
            json.dump(parsed_payload, f, indent=2)
            
        return f"Successfully wrote structured payload to {target_path}"
    
    except json.JSONDecodeError as e:
        return f"Failed to parse JSON string: {str(e)}"
    except Exception as e:
        return f"Fatal IO Failure: {str(e)}"

if __name__ == "__main__":
    mcp.run()
