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
