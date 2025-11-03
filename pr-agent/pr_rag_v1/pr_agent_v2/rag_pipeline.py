# -*- coding: utf-8 -*-
"""
资料入库：LlamaIndex 0.11.x + Chroma 0.4.x + Neo4j 5.x
- 读取 data_dir 文档 → chunk/嵌入 → Chroma
- 简易三元组抽取 → Neo4j（Strategy-USES->Channel）
"""
import os, argparse, re
from typing import List, Dict, Any
from llama_index.core import SimpleDirectoryReader, StorageContext
from llama_index.core import VectorStoreIndex, StorageContext, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
from neo4j import GraphDatabase

def get_storage_context_with_chroma(persist_dir: str = "./chroma_db", collection_name: str = "pr_agent"):
    """Return (storage_context, used_chroma: bool). Falls back to in-memory if ChromaVectorStore is unavailable."""
    try:
        if ChromaVectorStore is None:
            raise ImportError("ChromaVectorStore plugin not installed")
        import chromadb  # ensure chromadb present
        client = chromadb.PersistentClient(path=persist_dir)
        collection = client.get_or_create_collection(collection_name)
        vs = ChromaVectorStore(chroma_collection=collection)
        return StorageContext.from_defaults(vector_store=vs), True
    except Exception as e:
        print(f"[WARN] Chroma unavailable or failed ({e}); falling back to in-memory vector store.")
        return StorageContext.from_defaults(), False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_dir", required=True)
    ap.add_argument("--persist_dir", required=True)
    ap.add_argument("--neo4j_uri", required=True)
    ap.add_argument("--neo4j_user", required=True)
    ap.add_argument("--neo4j_password", required=True)
    args = ap.parse_args()

    os.makedirs(args.persist_dir, exist_ok=True)
    client = chromadb.PersistentClient(path=args.persist_dir)
    coll = client.get_or_create_collection("pr_kb_v3")
    try:
        vector_store = ChromaVectorStore(chroma_collection=coll)
    except TypeError:
        vector_store = ChromaVectorStore(collection=coll)

    # 定义一个缓存文件夹的路径
    cache_dir = "./model_cache/Users/biaowenhuang/Documents/vsc/projet/pr_agent_v2/model_cache"
    # 确保这个文件夹存在
    os.makedirs(cache_dir, exist_ok=True)
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3", cache_folder=cache_dir)
    storage_context, _ = get_storage_context_with_chroma(persist_dir=config.get('vector_store', {}).get('persist_dir', './chroma_db'), collection_name=config.get('vector_store', {}).get('collection', 'pr_agent'))

    print("📚 正在读取资料...")
    docs = SimpleDirectoryReader(input_dir=args.data_dir, recursive=True).load_data()
    print(f"读取到文档：{len(docs)}")

    print("🧠 正在写入向量库...")
    VectorStoreIndex.from_documents(docs, storage_context=storage_context, embed_model=embed_model, show_progress=True)

    # 轻量三元组抽取（示例）
    full_text = "\n\n".join([getattr(d, 'text', '') for d in docs])[:60000]
    triples = []
    pattern = re.compile(r"(策略|Strategy)[:：]?\s*([^\n；;,.，。 ]+).{0,12}?(使用|用|uses)\s*([^\n；;,.，。 ]+)", re.I)
    for m in pattern.finditer(full_text):
        head = m.group(2).strip(); tail = m.group(4).strip()
        if head and tail:
            triples.append((head, "USES", tail))
    triples = triples[:20]
    print(f"🔗 三元组抽取：{len(triples)}")

    # 写入 Neo4j
    driver = GraphDatabase.driver(args.neo4j_uri, auth=(args.neo4j_user, args.neo4j_password))
    with driver.session() as s:
        for h, _, t in triples:
            s.run("""
            MERGE (st:Strategy {title:$h})
            MERGE (ch:Channel  {name:$t})
            MERGE (st)-[r:USES]->(ch)
            ON CREATE SET r.weight=0.6, r.updated_at=timestamp()
            ON MATCH  SET r.weight=0.6, r.updated_at=timestamp()
            """, h=h, t=t)
    driver.close()

    print("✅ 入库完成")

if __name__ == "__main__":
    main()
