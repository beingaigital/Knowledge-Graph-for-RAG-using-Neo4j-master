#!/usr/bin/env python3
"""
增强RAG查询演示脚本
"""

import sys
import os
sys.path.append('core')

from pr_enhanced_rag import EnhancedPRRAGSystem

def demo_enhanced_rag():
    """演示增强RAG查询功能"""
    print("🔍 增强RAG查询演示")
    print("=" * 60)
    
    try:
        # 初始化RAG系统
        print("🚀 初始化增强RAG系统...")
        rag_system = EnhancedPRRAGSystem()
        print("✅ RAG系统初始化成功")
        print()
        
        # 测试问题列表
        test_questions = [
            "奥迪有哪些营销策略？",
            "一汽丰田的电商营销方案是什么？",
            "华与华超级符号案例有哪些？",
            "AI在营销中的应用有哪些？",
            "vivo品牌的内容表达策略是什么？"
        ]
        
        print("📝 测试问题列表:")
        for i, question in enumerate(test_questions, 1):
            print(f"  {i}. {question}")
        print()
        
        # 逐个测试问题
        for i, question in enumerate(test_questions, 1):
            print(f"🔍 测试问题 {i}: {question}")
            print("-" * 50)
            
            try:
                # 使用GraphRAG查询
                print("📊 使用GraphRAG查询...")
                answer = rag_system.query(question, use_graph=True)
                print(f"🤖 GraphRAG回答:\n{answer}")
                print()
                
                # 使用VectorRAG查询
                print("🔍 使用VectorRAG查询...")
                answer = rag_system.query(question, use_graph=False)
                print(f"🤖 VectorRAG回答:\n{answer}")
                print()
                
            except Exception as e:
                print(f"❌ 查询失败: {e}")
                print()
            
            print("=" * 60)
            print()
        
        print("🎉 增强RAG查询演示完成！")
        
    except Exception as e:
        print(f"❌ RAG系统初始化失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_enhanced_rag()

