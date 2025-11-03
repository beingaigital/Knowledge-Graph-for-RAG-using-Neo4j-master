#!/usr/bin/env python3
"""
增强的公关传播实体和关系提取器
基于LLM的智能实体识别和关系提取
"""

import json
import re
from typing import Dict, List, Any, Tuple
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
from pr_enhanced_schema import PRKnowledgeGraphSchema

class EntityRelationshipExtractor:
    """实体和关系提取器"""
    
    def __init__(self):
        self.schema = PRKnowledgeGraphSchema()
        try:
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.1,
                max_tokens=2000
            )
        except Exception as e:
            print(f"⚠️ LLM初始化失败，将使用规则提取: {e}")
            self.llm = None
        
        # 实体提取提示模板
        self.entity_extraction_prompt = PromptTemplate(
            input_variables=["text"],
            template="""
你是一个专业的公关传播分析师。请从以下文本中提取所有相关的实体信息。

文本内容：
{text}

请按照以下格式提取实体：

品牌 (Brand):
- 品牌名称: [品牌名]
- 行业: [行业类型]
- 品牌定位: [定位描述]

企业 (Company):
- 企业名称: [企业名]
- 行业: [行业类型]
- 企业类型: [类型描述]

公关公司 (Agency):
- 公司名称: [公司名]
- 专业领域: [专业领域]
- 服务范围: [服务范围]

传播活动 (Campaign):
- 活动名称: [活动名]
- 活动类型: [类型]
- 核心信息: [核心信息]

媒体渠道 (Media):
- 媒体名称: [媒体名]
- 媒体类型: [类型]
- 覆盖范围: [覆盖范围]

传播策略 (Strategy):
- 策略类型: [类型]
- 目标受众: [受众]
- 核心信息: [信息]

请确保提取的信息准确且完整。
"""
        )
        
        # 关系提取提示模板
        self.relationship_extraction_prompt = PromptTemplate(
            input_variables=["text", "entities"],
            template="""
你是一个专业的公关传播分析师。基于以下文本和已提取的实体，请识别实体之间的关系。

文本内容：
{text}

已提取的实体：
{entities}

请识别以下类型的关系：

1. 品牌合作关系 (BRAND_COLLABORATION):
   - 品牌联名、合作推出产品等

2. 商业合作关系 (COLLABORATES_WITH):
   - 企业间的商业合作、战略合作等

3. 竞争关系 (COMPETES_WITH):
   - 品牌或企业间的竞争关系

4. 媒体投放关系 (MEDIA_PLACEMENT):
   - 品牌在媒体平台的投放、推广等

5. 隶属关系 (BELONGS_TO):
   - 品牌隶属于某个企业或集团

6. 活动发起关系 (LAUNCHES_CAMPAIGN):
   - 品牌或企业发起的传播活动

7. 策略使用关系 (USES_STRATEGY):
   - 活动使用的传播策略

8. 内容创建关系 (CREATES_CONTENT):
   - 品牌或活动创建的内容

请按照以下格式输出关系：
关系类型: [关系类型]
主体: [主体实体]
客体: [客体实体]
关系描述: [关系描述]
置信度: [0-1之间的数值]

请确保关系识别准确且符合公关传播的实际情况。
"""
        )

    def extract_entities_from_text(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """从文本中提取实体"""
        if self.llm is None:
            # 直接使用规则提取
            return self._rule_based_entity_extraction(text)
            
        try:
            prompt = self.entity_extraction_prompt.format(text=text)
            response = self.llm.invoke(prompt)
            
            # 解析LLM响应
            entities = self._parse_entity_response(response.content)
            return entities
            
        except Exception as e:
            print(f"实体提取失败: {e}")
            # 回退到规则提取
            return self._rule_based_entity_extraction(text)

    def extract_relationships_from_text(self, text: str, entities: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """从文本中提取关系"""
        if self.llm is None:
            # 直接使用规则提取
            return self._rule_based_relationship_extraction(text)
            
        try:
            entities_str = json.dumps(entities, ensure_ascii=False, indent=2)
            prompt = self.relationship_extraction_prompt.format(text=text, entities=entities_str)
            response = self.llm.invoke(prompt)
            
            # 解析LLM响应
            relationships = self._parse_relationship_response(response.content)
            return relationships
            
        except Exception as e:
            print(f"关系提取失败: {e}")
            # 回退到规则提取
            return self._rule_based_relationship_extraction(text)

    def _parse_entity_response(self, response: str) -> Dict[str, List[Dict[str, Any]]]:
        """解析实体提取响应"""
        entities = {
            'brands': [],
            'companies': [],
            'agencies': [],
            'campaigns': [],
            'media': [],
            'strategies': []
        }
        
        lines = response.split('\n')
        current_type = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 识别实体类型
            if '品牌 (Brand):' in line:
                current_type = 'brands'
            elif '企业 (Company):' in line:
                current_type = 'companies'
            elif '公关公司 (Agency):' in line:
                current_type = 'agencies'
            elif '传播活动 (Campaign):' in line:
                current_type = 'campaigns'
            elif '媒体渠道 (Media):' in line:
                current_type = 'media'
            elif '传播策略 (Strategy):' in line:
                current_type = 'strategies'
            
            # 提取实体信息
            elif current_type and ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().replace('-', '').strip()
                value = value.strip()
                
                if value and value != '[待填写]':
                    # 查找是否已存在该实体
                    existing_entity = None
                    for entity in entities[current_type]:
                        if entity.get('name') == value:
                            existing_entity = entity
                            break
                    
                    if existing_entity:
                        existing_entity[key] = value
                    else:
                        entities[current_type].append({'name': value, key: value})
        
        return entities

    def _parse_relationship_response(self, response: str) -> List[Dict[str, Any]]:
        """解析关系提取响应"""
        relationships = []
        
        lines = response.split('\n')
        current_relationship = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_relationship:
                    relationships.append(current_relationship)
                    current_relationship = {}
                continue
            
            if '关系类型:' in line:
                if current_relationship:
                    relationships.append(current_relationship)
                current_relationship = {'type': line.split(':', 1)[1].strip()}
            elif '主体:' in line:
                current_relationship['from'] = line.split(':', 1)[1].strip()
            elif '客体:' in line:
                current_relationship['to'] = line.split(':', 1)[1].strip()
            elif '关系描述:' in line:
                current_relationship['description'] = line.split(':', 1)[1].strip()
            elif '置信度:' in line:
                try:
                    current_relationship['confidence'] = float(line.split(':', 1)[1].strip())
                except:
                    current_relationship['confidence'] = 0.5
        
        if current_relationship:
            relationships.append(current_relationship)
        
        return relationships

    def _rule_based_entity_extraction(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """基于规则的实体提取（回退方案）"""
        return self.schema.extract_entities(text)

    def _rule_based_relationship_extraction(self, text: str) -> List[Dict[str, Any]]:
        """基于规则的关系提取（回退方案）"""
        return self.schema.extract_relationships(text)

    def process_chunk(self, chunk_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理单个chunk，提取实体和关系"""
        text = chunk_data.get('text', '')
        
        # 提取实体
        entities = self.extract_entities_from_text(text)
        
        # 提取关系
        relationships = self.extract_relationships_from_text(text, entities)
        
        return {
            'chunk_id': chunk_data.get('chunkId'),
            'text': text,
            'entities': entities,
            'relationships': relationships,
            'source': chunk_data.get('source', ''),
            'metadata': {
                'content_type': chunk_data.get('content_type', 'general'),
                'industry': chunk_data.get('industry', 'unknown'),
                'brand_mentioned': chunk_data.get('brand_mentioned', [])
            }
        }

def test_extractor():
    """测试提取器功能"""
    extractor = EntityRelationshipExtractor()
    
    test_text = """
    华与华与雅诗兰黛合作推出品牌升级活动，在微信、微博等社交媒体平台进行推广。
    小米公司与华为在智能手机市场展开激烈竞争，双方都投入大量资源进行品牌建设。
    奥迪品牌通过数字化营销策略，在抖音、小红书等平台开展用户运营活动。
    """
    
    print("测试文本:")
    print(test_text)
    print("\n" + "="*60)
    
    # 提取实体
    entities = extractor.extract_entities_from_text(test_text)
    print("提取的实体:")
    print(json.dumps(entities, ensure_ascii=False, indent=2))
    
    # 提取关系
    relationships = extractor.extract_relationships_from_text(test_text, entities)
    print("\n提取的关系:")
    print(json.dumps(relationships, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    test_extractor()
