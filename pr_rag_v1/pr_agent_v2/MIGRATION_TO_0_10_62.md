
# Migration notes for LlamaIndex 0.10.62 + Chroma 0.5.5 + HF Embeddings

This bundle was adapted to run with:
- llama-index-core==0.10.62
- llama-index-embeddings-huggingface==0.2.2
- chromadb==0.5.5
- sentence-transformers==2.6.1
- transformers==4.41.2
- tokenizers==0.19.1

## What changed

1. **Imports normalized**
   - `from llama_index import ...` → `from llama_index.core import ...`
   - Explicitly import `VectorStoreIndex`, `SimpleDirectoryReader`, `StorageContext`, `Settings` when referenced.

2. **HuggingFace embeddings**
   - Use `from llama_index.embeddings.huggingface import HuggingFaceEmbedding`.
   - Pass `model_name=` explicitly.

3. **Chroma integration guard + fallback**
   - We try to import `ChromaVectorStore` from `llama_index.vector_stores.chroma`.
   - If it's not available (plugin not installed), we **fallback to in-memory** vector store and print a warning.
   - Helper: `get_storage_context_with_chroma(persist_dir, collection_name)` returns `(storage_context, used_chroma)`.

4. **Requirements pinned**
   - See `requirements.txt` for the exact versions.
   - Optionally install `llama-index-vector-stores-chroma` if you want the native integration; not required to run.

## Quickstart

```bash
pip install -r requirements.txt
python rag_pipeline.py --config config.example.yaml
python pr_marketing_agent_v3.py --config config.example.yaml
```
