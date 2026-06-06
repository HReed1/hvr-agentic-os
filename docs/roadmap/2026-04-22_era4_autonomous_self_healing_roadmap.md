# Era 4 Roadmap: Autonomous Infrastructure Self-Healing

## The Paradox of the "Black Box" Test Runner
In standard iterative execution (Era 3), agentic swarms depend entirely on the `stdout` of test runners (like Pytest) to determine logical correctness. This creates a dangerous **Cognitive Gap**:

1. If application logic fails, Pytest provides a clear Traceback (e.g., `AssertionError`, `KeyError`). The Swarm can effortlessly parse this and mutate the code to fix the logic.
2. If the *infrastructure* fails (e.g., Uvicorn latency binding to port 8000, zombie processes consuming sockets, or CI/CD memory limits), Pytest simply crashes with generic network errors like `net::ERR_CONNECTION_REFUSED`. 

Because the Swarm cannot dynamically "see" the infrastructure failure, it incorrectly assumes its application logic is flawed. This triggers an **iteration death-loop** where the Swarm continually mutates perfectly healthy application code to fix a hidden infrastructure bug.

To break this loop and achieve genuine zero-shot autonomy without human intervention, we must architect three interconnected capabilities into the `hvr-agentic-os` framework:

---

## Pillar 1: The Diagnostic MCP Wrapper (Giving the Swarm "Eyes")

**Objective:** Expose native host-level observability tooling to the `qa_engineer` node so it can physically interrogate the operating system when test runners crash ambiguously.

### Technical Implementation:
We will engineer a `diagnostics_mcp.py` integration exposing highly restricted, read-only bash primitives to the QA Engineer. 

*   **`tail_background_process(process_name: str, tail_lines: int = 50)`**
    *   **Mechanism:** Pytest often swallows the `stderr` of subprocesses. By allowing the QA Engineer to tail the literal Uvicorn or Nextflow log buffers remotely, it can instantly see `"SyntaxError in line 52"` or `"Uvicorn running on http://127.0.0.1:8000"` rather than guessing why the runner died.
*   **`audit_network_sockets(port: int)`**
    *   **Mechanism:** Executes a sanitized `lsof -i :<port>` or `netstat`. If Playwright crashes due to port bindings, the QA Engineer queries the OS to verify if (A) the port is free and the server never started, or (B) a rogue zombie process from a previous test is holding the socket hostage.
*   **Security Constraint:** These tools are explicitly read-only to prevent the Swarm from accidentally mutating host system configs outside the `.staging` sandbox.

---

## Pillar 2: Multi-Model "Rubber Duck" Escalation (Hierarchical Cascading)

**Objective:** Implement a hierarchical intelligence graph that utilizes cost-efficient models for standard bulk-engineering, but automatically cascades execution up to high-reasoning frontier models when structural paradoxes are encountered.

### Technical Implementation:
Currently, the Swarm loops using `gemini-3.1-flash`. Flash is incredibly fast but struggles with zero-shot spatial infrastructure reasoning. We will update `agent_app/agents.py` to support dynamic conditional nodes:

*   **The Paradox Trigger:** We inject a state counter into the `qa_engineer` payload. If the QA Engineer returns `PASS: False` for three consecutive epochs without resolving the specific test, the ADK `SequentialAgent` halts the standard loop.
*   **The Senior Architect Gateway:** The ADK router natively yields control up to the `senior_architect` node—a specialized agent powered by `gemini-3.1-pro`.
*   **Execution:** Pro receives the entire dense context of the three failures. Given its higher reasoning threshold, it can mathematically parse that the issue is Infrastructure/Latency based. It implements safety loops, resolves the environment barrier, and yields control **back down** to the Flash loop to finish the execution.

---

## Pillar 3: Anti-Pattern Knowledge Graphs (RAG)

**Objective:** Prevent repetitive hallucination death-loops by ensuring the Swarm possesses a permanent, searchable memory of historical testing and infrastructure quirks specific to our codebase.

### Technical Implementation:
We will physically map semantic memory into the QA Engineer's lifecycle to intercept errors before it writes a single line of bad code.

*   **The Anti-Pattern Database:** We establish a dedicated `docs/anti-patterns/` directory. Each markdown file rigorously documents a known systemic quirk (e.g., `asgi_playwright_latency.md`, `sqlalchemy_asyncpg_teardowns.md`).
*   **ADK RAG Integration:** We inject the ADK's native `rag_tool` into the `qa_engineer` dictionary. 
*   **Prompt Engineering:** We update the Crucible prompt: *"Upon receiving an unhandled Exception or generic network trace, you MUST execute a RAG query against the Anti-Pattern database using the exception signature before mutating any backend code."*
*   **Result:** The moment Flash encounters `ERR_CONNECTION_REFUSED`, it queries the Knowledge Graph, reads the exact Pytest polling loop requirement, and fixes the test without touching the application logic.
