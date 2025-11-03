# -*- coding: utf-8 -*-
"""
MCP 工具占位服务：search_kb / suggest_campaign / render_assets
"""
import os, json, asyncio
from modelcontextprotocol import Server
from modelcontextprotocol.mcp import Tool, CallToolResult

async def main():
    server = Server("pr-mkt-agent-mcp-v3")

    @server.list_tools()
    async def list_tools():
        return [
            Tool(name="search_kb", description="检索知识库（占位）", input_schema={"type":"object","properties":{"query":{"type":"string"}},"required":["query"]}),
            Tool(name="suggest_campaign", description="策略草案生成（占位）", input_schema={"type":"object","properties":{"vars_json":{"type":"string"}},"required":["vars_json"]}),
            Tool(name="render_assets", description="产出结构（A/B/E）占位", input_schema={"type":"object","properties":{"vars_json":{"type":"string"}},"required":["vars_json"]}),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        if name == "search_kb":
            res = [{"text": f"占位检索：{arguments['query']}", "source": "chroma+graph"}]
            return CallToolResult(content=[{"type":"text","text":json.dumps(res,ensure_ascii=False)}])
        if name == "suggest_campaign":
            data = json.loads(arguments["vars_json"])
            res = {"idea": f"针对{data.get('industry')}与目标{data.get('goal')}的整合策划（占位）", "channels": ["小红书","抖音","知乎"], "kpis": ["曝光","互动","留资"]}
            return CallToolResult(content=[{"type":"text","text":json.dumps(res,ensure_ascii=False)}])
        if name == "render_assets":
            res = {"A":{"prompts":["主视觉","延展1","延展2"]},"B":{"shotlist":[{"id":1,"sec":6,"desc":"开场"}]},"E":{"titles":["标题1","标题2","标题3"]}}
            return CallToolResult(content=[{"type":"text","text":json.dumps(res,ensure_ascii=False)}])
        return CallToolResult(content=[{"type":"text","text":"unknown tool"}])

    await server.run_stdio()

if __name__ == "__main__":
    asyncio.run(main())
