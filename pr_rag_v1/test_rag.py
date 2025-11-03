#!/usr/bin/env python3
"""
简单的增强RAG查询测试
"""

import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('.env', override=True)

# 添加路径
sys.path.append('core')

def test_simple_query():
    """简单查询测试"""
    print("🔍 增强RAG查询测试")
    print("=" * 60)
    
    try:
        # 直接导入模块
        from pr_enhanced_rag import EnhancedPRRAGSystem
        
        print("🚀 初始化增强RAG系统...")
        rag_system = EnhancedPRRAGSystem()
        print("✅ RAG系统初始化成功")
        print()
        
        # 测试问题
        test_questions = [
            "奥迪有哪些营销策略？",
            "一汽丰田的电商营销方案是什么？",
            "华与华超级符号案例有哪些？"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"🤔 测试问题 {i}: {question}")
            print("-" * 50)
            
            try:
                # 使用GraphRAG查询
                print("📊 使用GraphRAG查询...")
                answer = rag_system.query(question, use_graph=True)
                print(f"🤖 GraphRAG回答:\n{answer}")
                print()
                
            except Exception as e:
                print(f"❌ GraphRAG查询失败: {e}")
                print()
            
            print("=" * 60)
            print()
        
        print("🎉 增强RAG查询测试完成！")
        
    except Exception as e:
        print(f"❌ RAG系统初始化失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_query()

