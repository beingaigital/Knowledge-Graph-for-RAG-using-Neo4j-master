#!/usr/bin/env python3
"""
SPO知识图谱系统演示
展示如何使用集成的SPO三元组提取和知识图谱构建功能
"""

import os
import sys

# 添加core目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

from core.pr_integrated_kg_system import IntegratedKGSystem
from core.pr_entity_extractor import EntityRelationshipExtractor


def demo_spo_extraction():
    """演示SPO三元组提取"""
    print("=" * 70)
    print("🧪 演示1: SPO三元组提取")
    print("=" * 70)
    
    test_text = """
    华与华与雅诗兰黛合作推出品牌升级活动，在微信、微博等社交媒体平台进行推广。
    小米公司与华为在智能手机市场展开激烈竞争，双方都投入大量资源进行品牌建设。
    奥迪品牌通过数字化营销策略，在抖音、小红书等平台开展用户运营活动。
    一汽丰田在2021年度推出了数字营销电商策略，重点布局新能源市场。
    """
    
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ 跳过此演示：需要API密钥才能运行SPO提取")
        return None
    
    try:
        # 使用集成的SPO系统（使用OpenAI而不是OpenRouter）
        system = IntegratedKGSystem(
            use_openrouter=False,
            model_name="gpt-3.5-turbo"  # 使用OpenAI支持的模型
        )
        
        result = system.process_text(
            test_text,
            chunk_size=50,
            overlap=10,
            verbose=True
        )
        
        print(f"\n✅ 提取结果:")
        print(f"   归一化三元组数: {result['normalized_triples_count']}")
        print(f"   图谱节点数: {result['graph_stats']['nodes']}")
        print(f"   图谱边数: {result['graph_stats']['edges']}")
        
        # 显示部分三元组
        if system.normalized_triples:
            print(f"\n📋 前5个三元组:")
            for i, triple in enumerate(system.normalized_triples[:5], 1):
                print(f"   {i}. {triple['subject']} --[{triple['predicate']}]--> {triple['object']}")
        
        return system
    
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def demo_entity_extractor_with_spo():
    """演示使用SPO的实体提取器"""
    print("\n" + "=" * 70)
    print("🧪 演示2: 实体提取器（带SPO支持）")
    print("=" * 70)
    
    test_text = """
    华与华与雅诗兰黛合作推出品牌升级活动，在微信、微博等社交媒体平台进行推广。
    小米公司与华为在智能手机市场展开激烈竞争。
    """
    
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ 跳过SPO提取演示：需要API密钥")
        print("📋 仅演示传统方法:")
        try:
            extractor = EntityRelationshipExtractor(use_spo_extractor=False)
            entities = extractor.extract_entities_from_text(test_text)
            relationships = extractor.extract_relationships_from_text(test_text, entities)
            print(f"   实体数: {sum(len(v) for v in entities.values())}")
            print(f"   关系数: {len(relationships)}")
        except Exception as e:
            print(f"   传统方法也失败: {e}")
        return
    
    try:
        # 使用SPO提取器（使用OpenAI）
        extractor = EntityRelationshipExtractor(
            use_spo_extractor=True,
            spo_config={
                'model_name': 'gpt-3.5-turbo',  # 使用OpenAI模型
                'use_openrouter': False  # 使用OpenAI API
            }
        )
        
        # 提取SPO三元组
        spo_result = extractor.extract_spo_triples_from_text(
            test_text,
            chunk_size=50,
            overlap=10,
            verbose=True
        )
        
        print(f"\n✅ SPO提取结果:")
        print(f"   原始三元组数: {len(spo_result['triples'])}")
        print(f"   归一化三元组数: {len(spo_result['normalized_triples'])}")
        print(f"   成功块数: {spo_result['successful_chunks']}")
        
        # 显示归一化三元组
        if spo_result['normalized_triples']:
            print(f"\n📋 归一化三元组（前5个）:")
            for i, triple in enumerate(spo_result['normalized_triples'][:5], 1):
                print(f"   {i}. {triple['subject']} --[{triple['predicate']}]--> {triple['object']}")
        
        # 测试传统方法
        print(f"\n📋 使用传统方法:")
        entities = extractor.extract_entities_from_text(test_text)
        relationships = extractor.extract_relationships_from_text(test_text, entities)
        
        print(f"   实体数: {sum(len(v) for v in entities.values())}")
        print(f"   关系数: {len(relationships)}")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()


def demo_kg_query():
    """演示图谱查询"""
    print("\n" + "=" * 70)
    print("🧪 演示3: 知识图谱查询（RAG）")
    print("=" * 70)
    
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ 跳过此演示：需要API密钥才能运行图谱RAG查询")
        return
    
    test_text = """
    玛丽·居里，原名玛丽亚·斯克沃多夫斯卡，出生于波兰华沙，是一位开创性的物理学家和化学家。
    她与丈夫皮埃尔·居里一起发现了元素钋和镭。
    玛丽·居里是第一位获得诺贝尔奖的女性，也是唯一一位在两个不同科学领域获得诺贝尔奖的人。
    她于1903年与皮埃尔·居里和亨利·贝克勒尔一起获得诺贝尔物理学奖。
    她于1911年因对镭和钋的研究获得诺贝尔化学奖。
    玛丽·居里有两个女儿：伊雷娜和夏娃。
    玛丽·居里于1867年11月7日出生，于1934年去世。
    """
    
    try:
        system = IntegratedKGSystem(
            use_openrouter=False,
            model_name="gpt-3.5-turbo"  # 使用OpenAI支持的模型
        )
        system.process_text(test_text, chunk_size=80, overlap=15, verbose=False)
        
        questions = [
            "玛丽·居里在哪两个领域获得了诺贝尔奖？",
            "玛丽·居里的丈夫是谁？",
            "玛丽·居里发现了哪些元素？"
        ]
        
        for q in questions:
            print(f"\n❓ 问题: {q}")
            answer = system.query(q, verbose=False)
            print(f"✅ 回答: {answer}")
            print("-" * 70)
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    print("\n🚀 SPO知识图谱系统完整演示")
    print("=" * 70)
    print("\n提示: 请确保设置了以下环境变量:")
    print("  - OPENROUTER_API_KEY 或 OPENAI_API_KEY")
    print("=" * 70)
    
    # 检查API密钥
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n⚠️ 警告: 未检测到API密钥")
        print("   请设置 OPENROUTER_API_KEY 或 OPENAI_API_KEY 环境变量")
        print("   例如: export OPENROUTER_API_KEY='your-api-key'")
        print("\n   演示将继续运行，但会跳过需要API的功能")
    
    # 运行演示
    try:
        # 演示1: SPO提取
        system = demo_spo_extraction()
        
        # 演示2: 实体提取器
        demo_entity_extractor_with_spo()
        
        # 演示3: 图谱查询（如果系统可用）
        if system:
            demo_kg_query()
        
        print("\n" + "=" * 70)
        print("✅ 所有演示完成！")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断演示")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

