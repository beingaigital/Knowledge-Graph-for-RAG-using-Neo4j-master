# RAG 图谱设计（v3）
节点：Stage/Industry/MarketType/CompanyType、PRGoal/Strategy/Tactic/Channel、CaseStudy/Persona/Metric/Trend
关系：CompanyType→PRGoal，PRGoal→Strategy，Strategy→Channel|Tactic|CaseStudy|Persona|Metric|Trend
示例 Cypher：
```
MERGE (g:PRGoal {name:$goal})
MERGE (s:Strategy {title:$title})
MERGE (g)-[:INCLUDES]->(s)
MERGE (c:Channel {name:$ch})
MERGE (s)-[:USES]->(c)
```
