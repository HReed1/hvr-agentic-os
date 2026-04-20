---
description: Enforces strict data-fetching, state-management, and React component constraints on the Autonomous Swarm for the frontend UI.
glob: "ngs-variant-ui/**/*.tsx, ngs-variant-ui/**/*.ts, ngs-variant-ui/vite.config.ts"
---

# UI Frontend Functional Governance

You are operating within a Vite + React + TypeScript single-page application. When inspecting or mutating `.tsx` or `.ts` resources within `ngs-variant-ui`, you **MUST** strictly adhere to the following guardrails to prevent introducing UI technical debt or structural anti-patterns:

1. **State Management & Caching**: You are strictly **forbidden** from constructing raw `useEffect()` loops mapped to `useState()` arrays for managing asynchronous backend telemetry payload fetches. You **must** utilize `@tanstack/react-query` (`useQuery`, `useMutation`) for all external API dependencies to ensure the Swarm natively inherits caching, automatic background refetching (poll loops), and request deduplication.

2. **Environment Variable Architecture**: Be acutely aware of Vite's bundler isolation. Do **not** attempt to request raw `process.env` properties. Any environment variables that need to be inherently accessible to the compiled React DOM must be prefixed with `VITE_` and consumed strictly via `import.meta.env.VITE_*`.

3. **Routing Integrity**: Structural pathways must remain cleanly decoupled. All physical URL transitions and protected endpoints must be wrapped and evaluated dynamically by `react-router-dom`. When generating new components that load secondary URLs, leverage `Link` and `NavLink` over native `<a>` anchor variants to prevent the unmounting of the global `Auth0Provider` context.

4. **Authorization Bounds**: Never build implicit authentication assumptions inside raw UI blocks. Any requests for secure information must gracefully capture failure states (e.g., `401 Unauthorized` or `403 Forbidden`) from the `FastAPI` instance and render visually distinct fallback error blocks instructing the user to re-authenticate or contact their local IAM administrator.

5. **Headless Visual Testing**: When performing internal visual regression testing (via Playwright or Browser Subagents), you MUST dynamically bypass the Auth0 JWT UI lock. Use `toggle_react_eval_mode(enable=True)` to set `VITE_MOCK_AUTH=true`. This signals Axios interceptors to manually drop `getAccessTokenSilently` and utilize the localized `X-Telemetry-Secret` payload natively, rendering the UI layout completely without requiring human Multi-Factor Authentication. Always call `toggle_react_eval_mode(enable=False)` after testing completes to restore Zero-Trust policies. Note that `getAccessTokenSilently()` throws when `VITE_MOCK_AUTH=true` with no real Auth0 session — any SSE connections or API calls that rely on a bearer token must implement a MOCK_AUTH fallback path to avoid silent failures.

6. **No Push-Through on Missing Imports**: If the Vite compiler, TypeScript diagnostics, or Vitest returns a `"Failed to resolve import"`, `"Cannot find module"`, or any `import-analysis` error, you are **forbidden** from continuing validation or treating the error as a code-level defect. The mandatory first action is `provision_ui_dependency` (see `vite-reactor-suite` SKILL.md). Missing modules produce cascading synthetic errors that make correct code appear broken — fixing the environment before testing is not optional. This is the QA Engineer's responsibility, not the Executor's.
