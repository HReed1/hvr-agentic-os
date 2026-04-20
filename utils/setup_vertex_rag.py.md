# Setup Vertex RAG Corpus (`setup_vertex_rag.py`)

## Overview
A backend infrastructure python script tasked with provisioning or reconnecting the local agent memory graph to a designated Google Cloud Vertex AI Retrieval Augmented Generation (RAG) corpus.

## Functionality
- **Authentication**: Initializes the Vertex connection dynamically pointing to `project="general-477613"` residing in `us-west1`.
- **Search and Resolve**: Iterates over existing RAG corpora in the user's GCP environment, seeking the specific `ngs_variant_validator_rag` namespace.
- **Provisioning**: Automatically creates the RAG corpus if it does not yet exist on the server.
- **Memory Linking**: Persistently saves the resulting Corpus ID binding natively into `.agents/memory/vertex_rag_config.txt`, ensuring standard MCP servers can map their vector ingestion operations dynamically to this context.
