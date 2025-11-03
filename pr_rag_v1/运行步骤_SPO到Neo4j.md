# SPO三元组提取并上传到Neo4j的步骤

## 📋 前提条件

1. **确保环境变量已设置**：
   ```bash
   export OPENAI_API_KEY="你的API密钥"
   export NEO4J_URI="bolt://localhost:7687"
   export NEO4J_USERNAME="neo4j"
   export NEO4J_PASSWORD="你的密码"
   export NEO4J_DATABASE="neo4j"
   ```

2. **确保Neo4j数据库正在运行**

3. **数据已准备好**（已有chunks文件在 `data/chunks/` 目录下）

---

## 🚀 步骤1：使用Python交互式环境提取SPO三元组

在终端中运行：

```bash
cd /Users/biaowenhuang/Documents/Knowledge-Graph-for-RAG-using-Neo4j-master/pr_rag_v1
python3
```

然后在Python中执行：

```python
import os
import json
from pathlib import Path
from core.pr_spo_extractor import SPOTripleExtractor
from core.pr_kg_builder import KnowledgeGraphBuilder

# 设置API密钥
os.environ['OPENAI_API_KEY'] = '你的API密钥'

# 初始化SPO提取器（使用OpenAI）
extractor = SPOTripleExtractor(
    model_name="gpt-3.5-turbo",
    use_openrouter=False,
    temperature=0.0
)

# 初始化图谱构建器
kg_builder = KnowledgeGraphBuilder()

# 读取所有chunks文件
chunks_dir = Path("data/chunks")
chunk_files = list(chunks_dir.glob("*_chunks.json"))

print(f"找到 {len(chunk_files)} 个chunks文件")

all_triples = []

# 处理每个chunks文件
for chunk_file in chunk_files:
    print(f"\n处理文件: {chunk_file.name}")
    
    with open(chunk_file, 'r', encoding='utf-8') as f:
        chunks_data = json.load(f)
    
    for i, chunk in enumerate(chunks_data):
        chunk_text = chunk.get('text', '')
        if not chunk_text:
            continue
            
        print(f"  处理chunk {i+1}/{len(chunks_data)}...")
        
        # 提取SPO三元组
        result = extractor.extract_triples_from_text(
            chunk_text,
            chunk_size=150,
            overlap=30,
            verbose=False
        )
        
        # 归一化三元组
        normalized = extractor.normalize_triples(result['triples'])
        
        # 添加来源信息
        for triple in normalized:
            triple['source_file'] = chunk_file.name
            triple['chunk_id'] = chunk.get('chunkId', f"chunk_{i}")
        
        all_triples.extend(normalized)
        
        # 添加到图谱
        kg_builder.add_triples(normalized)
        
        print(f"    提取了 {len(normalized)} 个三元组")

print(f"\n✅ 总共提取了 {len(all_triples)} 个三元组")

# 保存三元组到文件（可选）
with open('data/spo_triples.json', 'w', encoding='utf-8') as f:
    json.dump(all_triples, f, ensure_ascii=False, indent=2)
print("✅ 三元组已保存到 data/spo_triples.json")

# 显示图谱统计
stats = kg_builder.get_statistics()
print(f"\n📊 图谱统计:")
print(f"  节点数: {stats['nodes']}")
print(f"  边数: {stats['edges']}")
```

---

## 🔗 步骤2：将SPO三元组上传到Neo4j

继续在Python中执行：

```python
from langchain_community.graphs import Neo4jGraph
from dotenv import load_dotenv
load_dotenv()

# 连接Neo4j
neo4j_uri = os.getenv('NEO4J_URI')
neo4j_user = os.getenv('NEO4J_USERNAME')
neo4j_pwd = os.getenv('NEO4J_PASSWORD')
neo4j_db = os.getenv('NEO4J_DATABASE') or 'neo4j'

graph = Neo4jGraph(
    url=neo4j_uri,
    username=neo4j_user,
    password=neo4j_pwd,
    database=neo4j_db
)

print("✅ Neo4j连接成功")

# 创建索引
print("\n🔧 创建索引...")
index_queries = [
    "CREATE INDEX IF NOT EXISTS FOR (n:Entity) ON (n.name)",
    "CREATE INDEX IF NOT EXISTS FOR (n:PR_Chunk) ON (n.chunk_id)",
    "CREATE INDEX IF NOT EXISTS FOR ()-[r:HAS_RELATION]-() ON (r.predicate)"
]

for query in index_queries:
    try:
        graph.query(query)
    except Exception as e:
        print(f"⚠️ 索引创建警告: {e}")

# 上传三元组
print(f"\n📤 开始上传 {len(all_triples)} 个三元组到Neo4j...")

success_count = 0
for i, triple in enumerate(all_triples, 1):
    subject = triple['subject']
    predicate = triple['predicate']
    obj = triple['object']
    chunk_id = triple.get('chunk_id', '')
    source_file = triple.get('source_file', '')
    
    try:
        # 创建实体节点和关系
        cypher = """
        MERGE (s:Entity {name: $subject})
        MERGE (o:Entity {name: $object})
        MERGE (s)-[r:HAS_RELATION {predicate: $predicate}]->(o)
        ON CREATE SET 
            r.created_at = timestamp(),
            r.source_file = $source_file,
            r.chunk_id = $chunk_id
        ON MATCH SET
            r.updated_at = timestamp()
        
        // 如果chunk_id存在，关联到chunk节点
        WITH s, o, r
        WHERE $chunk_id <> ''
        MERGE (chunk:PR_Chunk {chunk_id: $chunk_id})
        MERGE (chunk)-[:CONTAINS_ENTITY]->(s)
        MERGE (chunk)-[:CONTAINS_ENTITY]->(o)
        """
        
        graph.query(cypher, params={
            'subject': subject,
            'object': obj,
            'predicate': predicate,
            'chunk_id': chunk_id,
            'source_file': source_file
        })
        
        success_count += 1
        
        if i % 50 == 0:
            print(f"  进度: {i}/{len(all_triples)} ({i/len(all_triples)*100:.1f}%)")
            
    except Exception as e:
        print(f"⚠️ 上传三元组 {i} 失败: {e}")

print(f"\n✅ 成功上传 {success_count}/{len(all_triples)} 个三元组")

# 查询统计
stats_query = """
MATCH (n:Entity)
RETURN count(n) as entity_count
UNION ALL
MATCH ()-[r:HAS_RELATION]->()
RETURN count(r) as relation_count
"""
result = graph.query(stats_query)
print(f"\n📊 Neo4j统计:")
for row in result:
    if 'entity_count' in row:
        print(f"  实体节点: {row['entity_count']}")
    elif 'relation_count' in row:
        print(f"  关系数量: {row['relation_count']}")
```

---

## 🎯 或者使用更简单的方法：修改现有上传脚本

如果你想一次性完成，可以：

**方法1：直接在终端运行Python脚本**

创建一个临时脚本 `temp_upload_spo.py`：

```python
#!/usr/bin/env python3
import os
import json
from pathlib import Path
from core.pr_spo_extractor import SPOTripleExtractor
from langchain_community.graphs import Neo4jGraph
from dotenv import load_dotenv

load_dotenv()

# 设置API密钥
os.environ['OPENAI_API_KEY'] = '你的API密钥'

# 初始化
extractor = SPOTripleExtractor(model_name="gpt-3.5-turbo", use_openrouter=False)
graph = Neo4jGraph(
    url=os.getenv('NEO4J_URI'),
    username=os.getenv('NEO4J_USERNAME'),
    password=os.getenv('NEO4J_PASSWORD'),
    database=os.getenv('NEO4J_DATABASE') or 'neo4j'
)

# 处理所有chunks文件
chunks_dir = Path("data/chunks")
all_triples = []

for chunk_file in chunks_dir.glob("*_chunks.json"):
    print(f"处理: {chunk_file.name}")
    with open(chunk_file, 'r', encoding='utf-8') as f:
        chunks_data = json.load(f)
    
    for chunk in chunks_data:
        text = chunk.get('text', '')
        if text:
            result = extractor.extract_triples_from_text(text, verbose=False)
            normalized = extractor.normalize_triples(result['triples'])
            all_triples.extend(normalized)

# 上传到Neo4j
for triple in all_triples:
    graph.query("""
    MERGE (s:Entity {name: $s})
    MERGE (o:Entity {name: $o})
    MERGE (s)-[r:HAS_RELATION {predicate: $p}]->(o)
    """, params={'s': triple['subject'], 'o': triple['object'], 'p': triple['predicate']})

print(f"✅ 完成！上传了 {len(all_triples)} 个三元组")
```

然后运行：
```bash
python3 temp_upload_spo.py
```

---

## ⚡ 快速命令（如果数据量不大）

如果你只想快速测试，可以用这个一行式命令：

```bash
python3 -c "
import os, json
from pathlib import Path
from core.pr_spo_extractor import SPOTripleExtractor
os.environ['OPENAI_API_KEY'] = '你的API密钥'
extractor = SPOTripleExtractor(model_name='gpt-3.5-turbo', use_openrouter=False)
chunks_file = Path('data/chunks/2025内容营销重点策略与案例_chunks.json')
with open(chunks_file) as f:
    data = json.load(f)
for chunk in data[:3]:  # 只处理前3个
    result = extractor.extract_triples_from_text(chunk['text'], verbose=False)
    print(f'提取了 {len(result[\"triples\"])} 个三元组')
"
```

---

## 📝 注意事项

1. **API调用费用**：SPO提取需要调用OpenAI API，会产生费用
2. **处理时间**：大量chunks需要较长时间
3. **建议分批处理**：可以先处理1-2个文件测试，确认无误后再处理全部
4. **Neo4j连接**：确保Neo4j数据库正在运行

---

## 🎉 完成后的验证

上传完成后，可以在Neo4j Browser中查询：

```cypher
// 查看所有实体
MATCH (n:Entity) RETURN n LIMIT 100

// 查看关系
MATCH ()-[r:HAS_RELATION]->() RETURN r LIMIT 50

// 统计
MATCH (n:Entity) RETURN count(n) as entities
MATCH ()-[r:HAS_RELATION]->() RETURN count(r) as relations
```


