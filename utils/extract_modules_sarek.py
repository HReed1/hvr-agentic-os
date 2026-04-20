import os
import re

main_nf_path = '/Users/harrisonreed/Projects/ngs-variant-validator/src/pipelines/main.nf'
modules_dir = '/Users/harrisonreed/Projects/ngs-variant-validator/src/pipelines/modules/local'

with open(main_nf_path, 'r') as f:
    lines = f.readlines()

new_main = []
includes = []

processes = [
    "FETCH_DB_INPUTS", "SRA_TO_FASTQ", "SPLIT_FASTQ_BATCH", "ALIGN_READS",
    "MERGE_BAMS_REGIONAL", "GATHER_BAMS", "MARK_DUPLICATES", "CALCULATE_COVERAGE",
    "FAIL_FAST_QC", "INDEX_REFERENCE", "CALL_VARIANTS", "CALL_VARIANTS_VIRAL",
    "VIRAL_LINEAGE_ASSIGNMENT", "FILTER_BY_COVERAGE", "ANNOTATE_VARIANTS",
    "VALIDATE_VARIANTS", "GENERATE_JSON_REPORT", "GENERATE_JSON_REPORT_VIRAL",
    "PUBLISH_TELEMETRY"
]

in_process = False
current_process = None
brace_count = 0
process_lines = []

for line in lines:
    if not in_process:
        match = re.match(r'^process\s+([A-Z0-9_]+)\s*\{', line)
        if match:
            in_process = True
            current_process = match.group(1)
            brace_count = line.count('{') - line.count('}')
            process_lines = [line]
            includes.append(f"include {{ {current_process} }} from './modules/local/{current_process}.nf'\n")
        else:
            new_main.append(line)
    else:
        process_lines.append(line)
        brace_count += line.count('{') - line.count('}')
        if brace_count == 0:
            # End of process
            with open(os.path.join(modules_dir, f"{current_process}.nf"), 'w') as out_f:
                out_f.write("".join(process_lines))
            in_process = False
            current_process = None
            process_lines = []

insert_idx = 0
for i, line in enumerate(new_main):
    if "nextflow.enable.dsl=2" in line:
        insert_idx = i + 1
        break

new_main = new_main[:insert_idx] + ["\n// Modules\n"] + includes + ["\n"] + new_main[insert_idx:]

with open(main_nf_path, 'w') as f:
    f.writelines(new_main)
