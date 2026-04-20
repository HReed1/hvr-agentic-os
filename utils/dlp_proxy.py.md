# DLP Proxy (`dlp_proxy.py`)

## Overview
A lightweight Data Loss Prevention (DLP) utility focused on securely scrubbing protected genomic information and critical infrastructure bindings (UUIDs) from text prior to logging or returning payloads across Zero-Trust boundaries.

## Key Functions

### `redact_genomic_phi(content: str, redact_uuids: bool = True)`
- **Genomic Redaction**: Aggressively searches string content for biological sequences (strings of 20+ `A`, `T`, `C`, `G` characters) and structurally defined VCF variant coordinates (e.g., `chr1:12345-67890`), securely swapping them with a safe `<REDACTED_PHI>` tag.
- **Infrastructure Redaction**: Iterates using standard UUID Regex (`8-4-4-4-12` hex structure) to strip IDs linking to AWS, Terraform configurations, or internal Auth0 mappings. Crucial for ensuring the AI agent does not mistakenly broadcast sensitive environment parameters into general context logs.
