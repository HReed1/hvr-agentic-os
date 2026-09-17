# Ledger Reference Fixtures & Example Schemas

This directory contains populated reference ledgers demonstrating the full schema capabilities of Wonder's storage, project, and asset catalogs.

## Purpose
- **Schema & Referential Integrity Reference**: Showcases the complete set of required and optional fields across `drives_example.yaml`, `projects_example.yaml`, and `assets_example.yaml`.
- **Validation Testbed**: Unit test suites (`tests/test_ledgers.py`) and bootstrap verification (`scripts/verify_bootstrap.py`) validate complex foreign key relationships, 3-2-1 backup tier topologies, and pipeline phase mappings using these fixtures.
- **Production Isolation**: Ensures live working files in `/ledger/` remain strictly reflective of real physical inventory without confusion from synthetic demo productions.

## Files
- `drives_example.yaml`: Multi-tier storage setup (NVMe scratch, nearline RAID5, cold offsite archive, field shuttle) with benchmark specs, encryption, and mirror targets.
- `projects_example.yaml`: Video and photography projects with DaVinci Resolve Studio and Adobe Lightroom Classic pipelines.
- `assets_example.yaml`: Camera reels (.braw, .mov), raw photo shoots (.arw, .cr3), audio stems (.wav), proxies, and checksum manifests.
