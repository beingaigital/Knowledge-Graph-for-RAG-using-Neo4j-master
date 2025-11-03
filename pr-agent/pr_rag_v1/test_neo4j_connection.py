#!/usr/bin/env python3
"""
Neo4j连接测试脚本
"""

from dotenv import load_dotenv
import os
import sys

# 加载环境变量
load_dotenv('.env', override=True)

def test_neo4j_connection():
    """测试Neo4j连接"""
    print("🔍 Neo4j连接测试")
    print("=" * 50)
    
    # 显示环境变量
    print("环境变量:")
    print(f"  NEO4J_URI: {os.getenv('NEO4J_URI')}")
    print(f"  NEO4J_USERNAME: {os.getenv('NEO4J_USERNAME')}")
    print(f"  NEO4J_DATABASE: {os.getenv('NEO4J_DATABASE')}")
    print(f"  NEO4J_PASSWORD: {'*' * len(os.getenv('NEO4J_PASSWORD', ''))}")
    print()
    
    # 测试不同的连接方法
    methods = [
        ("langchain_neo4j", "from langchain_neo4j import Neo4jGraph"),
        ("neo4j_driver", "from neo4j import GraphDatabase"),
        ("neo4j_community", "from langchain_community.graphs import Neo4jGraph")
    ]
    
    for method_name, import_statement in methods:
        print(f"测试方法: {method_name}")
        try:
            exec(import_statement)
            
            if method_name == "langchain_neo4j":
                from langchain_neo4j import Neo4jGraph
                graph = Neo4jGraph(
                    url=os.getenv('NEO4J_URI'),
                    username=os.getenv('NEO4J_USERNAME'),
                    password=os.getenv('NEO4J_PASSWORD'),
                    database=os.getenv('NEO4J_DATABASE')
                )
                result = graph.query('RETURN 1 as test')
                print(f"✅ {method_name} 连接成功!")
                print(f"   查询结果: {result}")
                
            elif method_name == "neo4j_driver":
                from neo4j import GraphDatabase
                driver = GraphDatabase.driver(
                    os.getenv('NEO4J_URI'),
                    auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD'))
                )
                with driver.session(database=os.getenv('NEO4J_DATABASE')) as session:
                    result = session.run('RETURN 1 as test')
                    record = result.single()
                    print(f"✅ {method_name} 连接成功!")
                    print(f"   查询结果: {record['test']}")
                driver.close()
                
            elif method_name == "neo4j_community":
                from langchain_community.graphs import Neo4jGraph
                graph = Neo4jGraph(
                    url=os.getenv('NEO4J_URI'),
                    username=os.getenv('NEO4J_USERNAME'),
                    password=os.getenv('NEO4J_PASSWORD'),
                    database=os.getenv('NEO4J_DATABASE')
                )
                result = graph.query('RETURN 1 as test')
                print(f"✅ {method_name} 连接成功!")
                print(f"   查询结果: {result}")
            
            return True
            
        except Exception as e:
            print(f"❌ {method_name} 连接失败: {e}")
            print()
    
    return False

if __name__ == "__main__":
    success = test_neo4j_connection()
    if success:
        print("🎉 至少有一种方法连接成功!")
    else:
        print("❌ 所有连接方法都失败了")
        sys.exit(1)
