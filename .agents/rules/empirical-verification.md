# Empirical Verification Rule

When investigating system errors, paradoxes, or missing telemetry, Swarm Agents MUST NOT formulate architectural workarounds based on unverified symptom-matching or "Black Box" assumptions.

Before making codebase changes or proposing architectural mitigations to fix a suspected infrastructure bug, Agents MUST strictly adhere to the following empirical verification sequence:

1. **Physical Evidence First:** Agents must verify the actual physical state utilizing log outputs, raw database queries (e.g. SQLite), and filesystem states (identifying cached Git artifacts vs truly generated footprints).
2. **Never Guess:** If an environment boundary (like a Firewall or Sandbox) is suspected of stripping variables or blocking commands, Agents must read the structural execution bounds or raw source code of the infrastructure to unequivocally PROVE the behavior.
3. **Data Over Hypotheses:** Do not rely strictly on observed LLM behavior variations to diagnose system bounds. Agents must trace the full script pipeline and exact inputs/outputs (e.g., extracting literal pipe strings and bash parameters).

Architectural workarounds are strictly prohibited until the actual root mechanic of the failure has been physically verified.
