---
title: "Storage Audit: {{drive_id}} ({{volume_name}})"
date: {{date}}
category: ledger
tags:
  - storage
  - audit
  - hardware
drive_id: "{{drive_id}}"
volume_name: "{{volume_name}}"
sources:
  - "[[ledger/drives]]"
---

# Storage Audit: {{drive_id}} (`{{volume_name}}`)

> **Audit Date:** {{date}}  
> **Volume Mount:** `/Volumes/{{volume_name}}`  
> **Capacity:** 0.0 TB  
> **Filesystem:** APFS / exFAT  

---

## 1. Safety Checklist Passed
- [x] **Zero-Mutation Invariant**: No files moved, renamed, or modified on physical volume.
- [x] **Zero-Byte-Shift / Non-Hydration Invariant**: No temporary files or log records written to volume.

---

## 2. Directory Taxonomy & Discovered Content
```text
/Volumes/{{volume_name}}/
└── ...
```

---

## 3. Discovered Projects & Footprints
| Project Key | Directory | Detected Footprint | Registered in Ledger |
|---|---|---|---|
| PRJ-001 | `/...` | 0.0 GB | Yes |
