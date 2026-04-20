#!/bin/bash
set -e

echo "================================================="
echo "[BOOTSTRAP] Initializing Agentic OS Memory Paths..."
echo "================================================="

# 1. Director Context Source of Truth
mkdir -p docs/director_context
if [ ! -f docs/director_context/README.md ]; then
    echo "# Architectural Source of Truth" > docs/director_context/README.md
    echo "This directory is intentionally exposed to the ADK Director via the 'list_docs' tool. Add your explicit API schemas, database bounds, and infrastructure specifications here so the Swarm has a comparative baseline to identify architectural drift." >> docs/director_context/README.md
    echo "Created docs/director_context/README.md"
else
    echo "Skipped: docs/director_context/README.md already exists."
fi

# 2. Retrospectives and Evals Paths
mkdir -p docs/evals/retrospectives
mkdir -p docs/retrospectives
echo "Created evaluation and retrospective directories."

# 3. Agents Memory Logic & State
mkdir -p .agents/memory
if [ ! -f .agents/memory/executor_handoff.md ]; then
    echo "# Ephemeral State Ledger" > .agents/memory/executor_handoff.md
    echo "The Executor is mandated to natively read this file between sandbox mutations to combat ephemeral amnesia. Append learned anti-patterns here." >> .agents/memory/executor_handoff.md
    echo "Created .agents/memory/executor_handoff.md"
else
    echo "Skipped: .agents/memory/executor_handoff.md already exists."
fi

if [ ! -f .agents/memory/vertex_rag_config.txt ]; then
    echo "YOUR_GCP_CORPUS_ID_HERE" > .agents/memory/vertex_rag_config.txt
    echo "Created .agents/memory/vertex_rag_config.txt (Update securely with your Vertex Context ID)"
else
    echo "Skipped: .agents/memory/vertex_rag_config.txt already exists."
fi

# 4. Artifacts Exchange State Route
mkdir -p artifacts
echo "Created artifacts/ handoff directory."

# 5. Staging Airlock
mkdir -p .staging
echo "Created .staging/ temporary Executor containment directory."

# 6. Minimal Nextflow Orchestration Backbone
if [ ! -f main.nf ]; then
    cat << 'EOF' > main.nf
#!/usr/bin/env nextflow

nextflow.enable.dsl=2

process HELLO_WORLD {
    echo true
    script:
    """
    echo "Agentic OS Orchestration Pipeline Successfully Initialized."
    """
}

workflow {
    HELLO_WORLD()
}
EOF
    echo "Created baseline main.nf orchestration script."
else
    echo "Skipped: main.nf orchestration script already exists."
fi

if [ ! -f nextflow.config ]; then
    cat << 'EOF' > nextflow.config
manifest {
    name = 'HVR Agentic OS Defaults'
    description = 'Standard execution environment bound by Zero-Trust parameters.'
}

profiles {
    local {
        process.executor = 'local'
        docker.enabled = true
    }
    awsbatch {
        process.executor = 'awsbatch'
        process.queue = 'agent-os-compute-queue'
        aws.region = 'us-east-1'
        aws.batch.cliPath = '/home/ec2-user/miniconda/bin/aws'
    }
}
EOF
    echo "Created baseline nextflow.config with local and AWS Batch profiles."
else
    echo "Skipped: nextflow.config already exists."
fi

# 7. Terraform AWS Boundary Baseline
mkdir -p infrastructure/aws
if [ ! -f infrastructure/aws/main.tf ]; then
    cat << 'EOF' > infrastructure/aws/main.tf
provider "aws" {
    region = "us-east-1"
}

# Baseline Launch Template constraint for the Architect to inspect
resource "aws_launch_template" "compute_node" {
    name = "agent-os-compute-node"
    instance_type = "m5.large"
}
EOF
    echo "Created baseline infrastructure/aws/main.tf for Architectural Audits."
else
    echo "Skipped: infrastructure/aws/main.tf already exists."
fi

# 8. Testing Matrix Baseline
mkdir -p tests
if [ ! -f tests/test_baseline.py ]; then
    cat << 'EOF' > tests/test_baseline.py
def test_system_baseline():
    """Baseline test to prevent pytest from exiting with exit code 5 (no tests collected)."""
    assert True
EOF
    echo "Created tests/test_baseline.py for systemic Pytest verification."
else
    echo "Skipped: tests/test_baseline.py already exists."
fi

echo "================================================="
echo "[SUCCESS] Zero-Trust Operating System Bootstrapped."
echo "You may now configure your .env file and wake up the Swarm."
