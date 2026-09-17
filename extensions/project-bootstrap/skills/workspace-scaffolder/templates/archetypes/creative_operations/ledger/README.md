# {{project_name}} — Master Ledgers

This directory contains master entity ledgers tracking physical/cloud storage endpoints, projects, and media assets.

## Clean Zero-State Invariant

All live production ledgers initialize in a clean zero-state (`status: pre_audit_uninitialized`) with empty entity dictionaries.
- Do NOT populate live files with synthetic demonstration records.
- For schema testing and demonstration examples, see `templates/examples/`.
- Populating live ledgers occurs strictly through live storage discovery audits (`scripts/audit_storage.py` or interactive sessions).
