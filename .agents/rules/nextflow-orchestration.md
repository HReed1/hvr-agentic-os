---
description: Applies Nextflow Internal Mechanics to prevent physical infrastructure collisions and asynchronous pipeline corruption.
glob: "*.nf, nextflow.config"
---

# Nextflow Orchestration Mechanics

When modifying Nextflow DAGs or AWS Batch mappings, enforce these axiomatic boundaries:

1. **The Asynchronous Array Trap**: Never use dumb aggregators like `samtools cat` to merge channels produced by `.groupTuple()`. Because chunks arrive asynchronously based on container completion times, dumb concatenators destroy biological coordinate geometry. Always use coordinate-aware binaries (`samtools merge`).
2. **The Staging Standoff**: Nextflow natively stages `path(file)` inputs in the `.command.work` JVM boundary. NEVER execute `ln -s ${file} file` inside the `script:` block, as this creates a fatal `Exit 1` circular symlink collision. Trust the Nextflow staging contract.
3. **DSL2 Optional Inputs**: Do not use `path(file, optional: true)`. Cast optional files as `val(file)` and use explicit bash existence checks (`if [ "${file}" != "null" ]...`) inside the execution block.
4. **AWS Batch Container Mapping**: Any new `process` label must be physically mapped to its target Docker URI in `nextflow.config` via the `withName:` directive. Failure to map results in an invalid AWS Batch job definition error.
5. **Cryptographic Caching Limits**: Nextflow evaluates a 128-bit MD5 checksum for caching. Modifying ANY character/string within a `script:` block strictly invalidates the cache for that discrete node and severely impacts all downstream dependent processes.
6. **StoreDir vs PublishDir**: `storeDir` acts as a hard physical cache mapping for external remote fetches (e.g. large S3 target refs) to protect against `-resume` network failures. `publishDir` is strictly structural for final end-state telemetry and reporting egress. Do not conflate the two.
7. **Hardware Acceleration Semantics**: Only NVIDIA Parabricks (`ALIGN_PARABRICKS`) and GPU Variant Callers (`CALL_VARIANTS`) require GPU queue routing. Standard sequence binaries (`BWA`, `Bowtie2`, `Minimap2`) are strictly CPU-bound and must map to CPU queues to prevent compute starvation.
8. **Telemetry Blackout Principle**: Nextflow pipeline wrappers utilizing `-with-weblog` have been deprecated in favor of native configuration files. Whenever altering pipeline topologies, you MUST ensure that `weblog { enabled = true }` is structurally defined inside `nextflow.config`. Failure to specify this natively drops all webhook M2M synchronization payloads silently.
