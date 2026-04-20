import os
from google.adk.tools import FunctionTool
from .config import BASE_DIR

rag_tool = None
try:
    with open(os.path.join(BASE_DIR, ".agents", "memory", "vertex_rag_config.txt"), "r") as f:
        corpus_id = f.read().strip()
        import vertexai
        from vertexai.preview import rag
        
        project_id = os.environ.get("VERTEX_PROJECT_ID", "general-477613")
        location = os.environ.get("VERTEX_LOCATION", "us-west1")
        vertexai.init(project=project_id, location=location)

        def query_vertex_rag_corpus(query: str) -> str:
            """Queries the Vertex AI RAG Corpus for semantic code chunks and constraints."""
            response = rag.retrieval_query(
                rag_resources=[rag.RagResource(rag_corpus=corpus_id)],
                text=query,
                similarity_top_k=2,
            )
            return "".join([context.text for context in response.contexts])[:10000]

        rag_tool = FunctionTool(function=query_vertex_rag_corpus)
        print(f"[RAG Engine] Vertex AI Semantic Memory Initialized: {corpus_id}")
except Exception as e:
    print(f"[RAG Engine Bypass] Skipping RAG Tool initialization: {e}")
