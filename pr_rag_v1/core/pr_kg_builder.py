#!/usr/bin/env python3
"""
知识图谱构建器
使用NetworkX在内存中构建和管理知识图谱
"""

import networkx as nx
from typing import List, Dict, Any, Set, Optional
import json


class KnowledgeGraphBuilder:
    """使用NetworkX构建知识图谱"""
    
    def __init__(self):
        """初始化空的有向图"""
        self.graph = nx.DiGraph()
        self.triples_count = 0
        self.nodes_count = 0
        self.edges_count = 0
    
    def add_triples(self, triples: List[Dict[str, Any]]) -> int:
        """
        添加三元组到图谱
        
        Args:
            triples: 三元组列表，每个三元组包含subject、predicate、object
            
        Returns:
            添加的边数
        """
        added_count = 0
        
        for triple in triples:
            subject = triple.get('subject')
            predicate = triple.get('predicate')
            obj = triple.get('object')
            
            if subject and predicate and obj:
                # NetworkX会自动添加节点（如果不存在）
                # 添加边，使用predicate作为label属性
                self.graph.add_edge(
                    subject,
                    obj,
                    label=predicate,
                    **{k: v for k, v in triple.items() if k not in ['subject', 'predicate', 'object']}
                )
                added_count += 1
        
        self.triples_count += added_count
        self.edges_count = self.graph.number_of_edges()
        self.nodes_count = self.graph.number_of_nodes()
        
        return added_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取图谱统计信息"""
        stats = {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'triples_added': self.triples_count,
            'density': 0.0,
            'is_connected': False,
            'components': 0
        }
        
        if stats['nodes'] > 0:
            try:
                stats['density'] = nx.density(self.graph)
                stats['is_connected'] = nx.is_weakly_connected(self.graph)
                stats['components'] = nx.number_weakly_connected_components(self.graph)
            except Exception as e:
                pass  # 忽略计算错误
        
        return stats
    
    def get_subgraph_by_entities(
        self,
        entities: Set[str],
        max_depth: int = 1
    ) -> nx.DiGraph:
        """
        根据实体集合提取子图
        
        Args:
            entities: 实体名称集合
            max_depth: 最大遍历深度
            
        Returns:
            子图
        """
        relevant_nodes = set(entities)
        
        # 根据深度扩展相关节点
        for depth in range(max_depth):
            new_nodes = set()
            for u, v in self.graph.edges():
                if u in relevant_nodes:
                    new_nodes.add(v)
                if v in relevant_nodes:
                    new_nodes.add(u)
            relevant_nodes.update(new_nodes)
        
        return self.graph.subgraph(relevant_nodes)
    
    def find_related_entities(
        self,
        entity: str,
        max_hops: int = 2
    ) -> List[Dict[str, Any]]:
        """
        查找与给定实体相关的实体
        
        Args:
            entity: 实体名称
            max_hops: 最大跳数
            
        Returns:
            相关实体列表，包含路径信息
        """
        if entity not in self.graph:
            return []
        
        related = []
        visited = set([entity])
        
        # BFS遍历
        current_level = [entity]
        
        for hop in range(max_hops):
            next_level = []
            for node in current_level:
                # 前向和后向邻居
                neighbors = list(self.graph.successors(node)) + list(self.graph.predecessors(node))
                
                for neighbor in neighbors:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        next_level.append(neighbor)
                        
                        # 获取关系信息
                        edges = []
                        if self.graph.has_edge(node, neighbor):
                            edge_data = self.graph[node][neighbor]
                            edges.append({
                                'direction': 'out',
                                'label': edge_data.get('label', ''),
                                'data': {k: v for k, v in edge_data.items() if k != 'label'}
                            })
                        if self.graph.has_edge(neighbor, node):
                            edge_data = self.graph[neighbor][node]
                            edges.append({
                                'direction': 'in',
                                'label': edge_data.get('label', ''),
                                'data': {k: v for k, v in edge_data.items() if k != 'label'}
                            })
                        
                        related.append({
                            'entity': neighbor,
                            'hops': hop + 1,
                            'source': node,
                            'relationships': edges
                        })
            
            current_level = next_level
            if not current_level:
                break
        
        return related
    
    def get_triples_for_context(
        self,
        entities: Set[str],
        max_edges: int = 50
    ) -> List[str]:
        """
        获取用于构建上下文的 triples（文本形式）
        
        Args:
            entities: 相关实体集合
            max_edges: 最大边数
            
        Returns:
            三元组文本列表
        """
        subgraph = self.get_subgraph_by_entities(entities, max_depth=2)
        
        triples_text = []
        count = 0
        
        for u, v, data in subgraph.edges(data=True):
            if count >= max_edges:
                break
            predicate = data.get('label', '')
            triples_text.append(f"{u} {predicate} {v}.")
            count += 1
        
        return triples_text
    
    def get_node_with_highest_degree(self, top_k: int = 10) -> List[Dict[str, Any]]:
        """获取度最高的节点（最重要的实体）"""
        degrees = dict(self.graph.degree())
        sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                'entity': node,
                'degree': degree,
                'in_degree': self.graph.in_degree(node),
                'out_degree': self.graph.out_degree(node)
            }
            for node, degree in sorted_nodes[:top_k]
        ]
    
    def export_to_dict(self) -> Dict[str, Any]:
        """导出为字典格式"""
        nodes = []
        edges = []
        
        for node in self.graph.nodes():
            nodes.append({
                'id': str(node),
                'label': str(node),
                'in_degree': self.graph.in_degree(node),
                'out_degree': self.graph.out_degree(node)
            })
        
        for u, v, data in self.graph.edges(data=True):
            edges.append({
                'source': str(u),
                'target': str(v),
                'label': data.get('label', ''),
                'data': {k: v for k, v in data.items() if k != 'label'}
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'statistics': self.get_statistics()
        }
    
    def export_to_json(self, filepath: str):
        """导出为JSON文件"""
        data = self.export_to_dict()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def clear(self):
        """清空图谱"""
        self.graph.clear()
        self.triples_count = 0
        self.nodes_count = 0
        self.edges_count = 0


def test_kg_builder():
    """测试知识图谱构建器"""
    print("🧪 测试知识图谱构建器")
    print("=" * 60)
    
    # 创建测试三元组
    test_triples = [
        {'subject': 'marie curie', 'predicate': 'discovered', 'object': 'radium', 'chunk': 1},
        {'subject': 'marie curie', 'predicate': 'won', 'object': 'nobel prize in physics', 'chunk': 1},
        {'subject': 'marie curie', 'predicate': 'married', 'object': 'pierre curie', 'chunk': 2},
        {'subject': 'pierre curie', 'predicate': 'was born in', 'object': 'paris', 'chunk': 2},
        {'subject': 'radium', 'predicate': 'is element', 'object': 'radioactive material', 'chunk': 1},
    ]
    
    # 构建图谱
    kg_builder = KnowledgeGraphBuilder()
    added = kg_builder.add_triples(test_triples)
    print(f"✅ 添加了 {added} 条边")
    
    # 统计信息
    stats = kg_builder.get_statistics()
    print(f"\n📊 图谱统计:")
    print(f"   节点数: {stats['nodes']}")
    print(f"   边数: {stats['edges']}")
    print(f"   密度: {stats['density']:.4f}")
    print(f"   连通: {stats['is_connected']}")
    print(f"   组件数: {stats['components']}")
    
    # 查找相关实体
    print(f"\n🔍 查找与'marie curie'相关的实体:")
    related = kg_builder.find_related_entities('marie curie', max_hops=2)
    for rel in related[:5]:
        print(f"   {rel['entity']} (距离: {rel['hops']}, 来源: {rel['source']})")
    
    # 获取上下文
    print(f"\n📝 获取上下文三元组:")
    context = kg_builder.get_triples_for_context({'marie curie'}, max_edges=10)
    for triple in context[:5]:
        print(f"   {triple}")
    
    # 导出
    export_data = kg_builder.export_to_dict()
    print(f"\n💾 导出数据包含 {len(export_data['nodes'])} 个节点和 {len(export_data['edges'])} 条边")
    
    return kg_builder


if __name__ == "__main__":
    test_kg_builder()

