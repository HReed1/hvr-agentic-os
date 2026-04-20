---
trigger: always_on
description: Enforces Zero-Trust authorization schemas and optimal SQLAlchemy object mapping for backend handlers.
---

# FastAPI Zero-Trust & DB Directives

1. **Zero-Trust Token Dependency**: Every operational FastAPI endpoint must mandate architectural authentication by injecting `Depends(verify_token)` into its signature block. (Note: Infrastructure endpoints like `/health` are explicitly exempt from this constraint). Do not leak PHI inside raw responses. Query against `FrontendPatient.patient_hash`, never `patient_id`.
2. **Deep Eager Loading (SQLAlchemy)**: When returning heavy relational endpoints (e.g., fetching a `Sample` with its associated `runs`), you MUST use `.options(selectinload(...))` for the child elements. This structurally protects the API from `N+1` query degradation.