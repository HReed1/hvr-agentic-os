import os
import re

main_nf_path = '/Users/harrisonreed/Projects/ngs-variant-validator/src/pipelines/main.nf'
workflows_dir = '/Users/harrisonreed/Projects/ngs-variant-validator/src/pipelines/workflows'

with open(main_nf_path, 'r') as f:
    content = f.read()

# Extract all include statements from main.nf
include_lines = []
for line in content.splitlines():
    if line.startswith("include {") and "./modules/" in line:
        include_lines.append(line.replace("./modules/", "../modules/"))

all_includes_str = "\n".join(include_lines) + "\n\n"

# Extract workflow VIRAL_ORCHESTRATION { ... }
start_viral = content.find("workflow VIRAL_ORCHESTRATION {")
end_viral = content.find("\n}", start_viral) + 2
viral_workflow = content[start_viral:end_viral]

with open(os.path.join(workflows_dir, 'viral.nf'), 'w') as f:
    f.write(all_includes_str + viral_workflow)

# Extract workflow SOMATIC_ORCHESTRATION { ... }
start_somatic = content.find("workflow SOMATIC_ORCHESTRATION {")
end_somatic = content.find("\n}", start_somatic) + 2
somatic_workflow = content[start_somatic:end_somatic]

with open(os.path.join(workflows_dir, 'somatic.nf'), 'w') as f:
    f.write(all_includes_str + somatic_workflow)

# Replace in main.nf
new_content = content[:start_viral] + content[end_somatic:]

# Fix main.nf includes
new_includes = """// Workflow Includes
include { VIRAL_ORCHESTRATION } from './workflows/viral.nf'
include { SOMATIC_ORCHESTRATION } from './workflows/somatic.nf'
"""

# Put new includes before the main workflow block
main_start = new_content.find("// Workflow Execution")
new_content = new_content[:main_start] + new_includes + "\n" + new_content[main_start:]

with open(main_nf_path, 'w') as f:
    f.write(new_content)
