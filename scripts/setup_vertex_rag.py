import os
import vertexai
from google.cloud import aiplatform

def initialize_vertex_rag_corpus(project_id=os.environ.get("VERTEX_PROJECT_ID", "your-project-id-here"), location="us-west1", corpus_display_name=os.environ.get("VERTEX_RAG_CORPUS_NAME", "my_adk_rag_corpus")):
    print(f"Initializing Vertex AI Context in {project_id} ({location})...")
    vertexai.init(project=project_id, location=location)
    
    # Check if a corpus already exists (simplistic check, we'll try to retrieve or create)
    from vertexai.preview import rag
    
    # List corpora
    corpora = rag.list_corpora()
    for c in corpora:
        if c.display_name == corpus_display_name:
            print(f"RAG Corpus already exists: {c.name}")
            return c.name
            
    print(f"Creating new RAG Corpus: {corpus_display_name}...")
    # Create the corpus
    corpus = rag.create_corpus(display_name=corpus_display_name, timeout=1800)
    print(f"Successfully provisioned RAG Corpus: {corpus.name}")
    return corpus.name

if __name__ == "__main__":
    corpus_name = initialize_vertex_rag_corpus()
    # Save the corpus_name to a local config so the MCP servers can easily access it
    os.makedirs(".agents/memory", exist_ok=True)
    with open(".agents/memory/vertex_rag_config.txt", "w") as f:
        f.write(corpus_name)
    print(f"Saved Corpus ID to .agents/memory/vertex_rag_config.txt")
