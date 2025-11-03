# 公关营销方案智能体（Graph RAG + MCP 版）

本项目为“公关营销方案智能体”的**新版实现**，在你之前的一版基础上做了整体重构：

- **RAG 实现**：`LlamaIndex + Chroma + Neo4j`（Graph RAG）。默认使用本地/免费向量模型（`BAAI/bge-m3`），降低 Token 成本。
- **大模型选择**：通过 **LiteLLM** 适配 `DeepSeek / 通义千问(Qwen) / OpenAI` 等主流 API，使用统一接口；避免被单一厂商锁定。
- **输出六大产出**：
  - A 平面类（自动生成 A3/300dpi JPG 占位图 + 提交给文生图工具的 Prompt brief）
  - B 企业宣传视频脚本及 AIGC 分镜（Shotlist + 配音字幕文案）
  - C 公关营销策划案（自动导出 Word/PPT，包含 SWOT/PEST、策略矩阵、媒体投放、甘特图、预算饼图）
  - D 爆款短视频脚本及 AIGC 成片（15s/30s/60-180s 的分镜脚本）
  - E 小红书爆款笔记（标题 + 正文 + 配图提示）
  - F 危机公关应对方案（Word/PPT 格式，含时间线、响应机制、甘特图）
- **MCP 工具服务器**：提供一个最小可跑的 **MCP 协议占位服务**（`mcp_tools_server.py`），可被支持 MCP 的客户端（如一些 IDE/Agent 框架）调用，暴露：
  - `search_kb`：按主题查询向量库+图谱
  - `suggest_campaign`：基于 RAG + LLM 生成策略草案
  - `render_assets`：生成平面/视频/小红书/危机方案等结构化产出

> 运行环境：**Python 3.11.13**（务必固定版本）。

---

## 一、快速开始

1. 创建虚拟环境，固定 Python 版本：

```bash
pyenv local 3.11.13   # 或使用 conda/mamba 安装 3.11
python -m venv .venv311
source .venv311/bin/activate
```

2. 安装依赖：

```bash
python3.11 -m venv .venv311
source .venv311/bin/activate
python -V   # 此处应显示 3.11.13
pip install -U pip setuptools wheel
pip install -r requirements.txt
pip check
```

3. 填写配置：

- 复制 `config.example.yaml` 为 `config.yaml`
- 复制 `.env.example` 为 `.env`，填好你的 API Key / Neo4j 连接信息。

4. 构建知识库（RAG 图谱 + 向量库）：

```bash
python rag_pipeline.py --data_dir ./data   --persist_dir ./vector_store/chroma_db   --neo4j_uri bolt://localhost:7687   --neo4j_user neo4j   --neo4j_password your_password
```

5. 运行智能体（生成六类产出）：

```bash
python pr_marketing_agent_v2.py   --enterprise_name "吉利远程新能源商用车"   --enterprise_stage "中小微企业"   --industry "商用汽车"   --market_type "ToB"   --pr_goal "品牌认知"   --pr_cycle "半年"   --pr_budget "¥150万"   --innovation "适度创新"   --outputs A,B,C,D,E,F
```

输出会写入 `./outputs/YYYYMMDD_HHMMSS/`。

6. 启动 MCP 工具服务器（可选）：

```bash
python mcp_tools_server.py
```

---

## 二、与上一版的改进对照

- 引入 **LiteLLM** 统一多家大模型调用，默认优先 DeepSeek/Qwen；OpenAI 作为后备。
- 向量模型默认 **本地免费**（`BAAI/bge-m3`），节约成本。
- 加强 **Graph RAG**：Neo4j 图谱节点扩展到 Strategy/Tactic/Channel/CaseStudy/Persona/Metric/Trend 等，详见 `rag_db_design.md`。
- 输出模块模板化、结构化，**对接 AIGC 工具更方便**（分镜 JSON + 配音文本 + Midjourney/SDXL 提示）。
- 所有脚本都兼容 `Chroma 0.4.x` 的 `collection`/`chroma_collection` 参数差异。

---

## 三、目录结构

```
.
├── pr_marketing_agent_v2.py      # 新版智能体主程序（CLI）
├── rag_pipeline.py               # 资料入库（向量 + 图谱）
├── mcp_tools_server.py           # MCP 工具占位服务
├── rag_db_design.md              # RAG 图谱设计文档
├── ARCHITECTURE_DESIGN.md        # 架构设计文档（详）
├── README.md
├── requirements.txt
├── config.example.yaml
├── .env.example
└── outputs/                      # 运行后自动生成
```

---

## 四、常见问题

- **Q**：LlamaIndex 是否必须用 OpenAI？  
  **A**：不用。本版通过 **LiteLLM** 走统一接口，`provider=model` 即可切换 DeepSeek/Qwen/OpenAI。嵌入用本地 `bge-m3`。

- **Q**：Chroma 的不同小版本参数不一致？  
  **A**：代码里做了兼容封装（尝试 `chroma_collection` -> 回退 `collection`）。

- **Q**：Python 3.13 不支持？  
  **A**：建议固定 **3.11.13**（依赖更稳）。

- **Q**：能否直接连 Canva/Kimi PPT？  
  **A**：MCP 提供占位工具，你可以在 `mcp_tools_server.py` 里补充 OAuth/SDK 调用。

---

## 五、许可证

本仓库默认以 **MIT** 许可开源，按需二次开发即可。
