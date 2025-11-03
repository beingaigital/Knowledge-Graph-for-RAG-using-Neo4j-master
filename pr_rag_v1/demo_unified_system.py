#!/usr/bin/env python3
"""
统一公关传播智能体系统演示脚本
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('.env', override=True)

def test_unified_system():
    """测试统一系统"""
    print("🤖 统一公关传播智能体系统演示")
    print("=" * 60)
    
    try:
        # 导入统一系统
        from unified_pr_system import UnifiedPRSystem
        
        # 初始化系统
        print("🚀 初始化统一系统...")
        system = UnifiedPRSystem("unified_config.yaml")
        print("✅ 系统初始化成功")
        
        # 测试1: 知识查询
        print("\n📊 测试1: 知识查询")
        print("-" * 30)
        query1 = "小米汽车应该如何做好用户运营？"
        print(f"查询: {query1}")
        
        result1 = system.unified_query(query1, "knowledge_query")
        if "error" not in result1:
            print(f"回答: {result1['result'][:300]}...")
        else:
            print(f"错误: {result1['error']}")
        
        # 测试2: 实体分析
        print("\n🔬 测试2: 实体分析")
        print("-" * 30)
        query2 = "小米汽车与华为汽车在智能驾驶领域展开竞争，双方都在加大研发投入"
        print(f"分析文本: {query2}")
        
        result2 = system.unified_query(query2, "entity_analysis")
        if "error" not in result2:
            print(f"分析结果: {result2['result']}")
        else:
            print(f"错误: {result2['error']}")
        
        # 测试3: 方案生成
        print("\n📋 测试3: 方案生成")
        print("-" * 30)
        enterprise_info = {
            "enterprise_name": "小米汽车",
            "enterprise_stage": "大型企业",
            "industry": "汽车",
            "market_type": "ToC",
            "pr_goal": "品牌认知",
            "pr_cycle": "6个月",
            "pr_budget": "500万",
            "innovation": "适度创新"
        }
        
        print(f"企业信息: {enterprise_info['enterprise_name']} - {enterprise_info['industry']}")
        print("生成方案类型: A(图形创意), B(视频脚本), C(活动策划)")
        
        result3 = system.generate_pr_plan(enterprise_info, ["A", "B", "C"])
        if "error" not in result3:
            print("✅ 方案生成成功")
            for plan_type, content in result3.items():
                print(f"\n{plan_type} 方案预览:")
                print(f"{content[:200]}...")
        else:
            print(f"错误: {result3['error']}")
        
        # 测试4: 自动模式查询
        print("\n🎯 测试4: 自动模式查询")
        print("-" * 30)
        queries = [
            "AI变革对品牌传播有什么影响？",
            "请为小米汽车生成一个品牌推广方案",
            "分析这个案例中的品牌关系：小米与华为的竞争"
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\n查询{i}: {query}")
            result = system.unified_query(query, "auto")
            print(f"识别模式: {result['mode']}")
            if "error" not in result:
                if isinstance(result['result'], str):
                    print(f"结果: {result['result'][:150]}...")
                else:
                    print(f"结果: {result['result']}")
            else:
                print(f"错误: {result['error']}")
        
        print("\n🎉 演示完成！")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'system' in locals():
            system.close()

def show_system_capabilities():
    """显示系统能力"""
    print("\n📋 统一系统能力概览:")
    print("=" * 40)
    
    capabilities = {
        "知识查询": [
            "基于Neo4j知识图谱的语义查询",
            "基于向量数据库的相似性搜索",
            "实体关系推理和路径查询",
            "多模态知识融合"
        ],
        "方案生成": [
            "A - 图形创意Brief（平面广告/包装/IP周边）",
            "B - 视频脚本（企业宣传片分镜）",
            "C - 活动策划（完整营销方案）",
            "D - 短视频脚本（15s-180s多格式）",
            "E - 小红书笔记（爆款内容）",
            "F - 危机公关方案（应对策略）"
        ],
        "实体分析": [
            "品牌识别和属性提取",
            "企业关系分析",
            "活动策略识别",
            "媒体渠道分析",
            "KPI指标提取"
        ],
        "文档导出": [
            "Word文档生成",
            "PPT演示文稿",
            "图片占位符",
            "Markdown格式",
            "JSON数据导出"
        ]
    }
    
    for category, features in capabilities.items():
        print(f"\n🔹 {category}:")
        for feature in features:
            print(f"  • {feature}")

if __name__ == "__main__":
    show_system_capabilities()
    test_unified_system()

