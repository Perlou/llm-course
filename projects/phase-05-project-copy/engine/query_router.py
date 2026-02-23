"""
核心查询路由与理解引擎
负责查询语句的处理，利用大模型理解意图。
包含先进的 HyDE (假设性文档嵌入) 策略以及长难句的查询分解。
"""

from typing import List, Dict, Any
import google.generativeai as genai

from config import config


class QueryRouter:
    """基于大模型的高级意图识别处理器。"""

    DECOMPOSITION_PROMPT = """你是一个专业的长难句查询理解引擎。
用户的提问可能比较复杂或者宽泛，请将其拆解为 1-3 个独立、明确的核心搜索子查询。
如果原查询很简单，只需返回原查询即可。

用户查询: {query}

要求：
1. 提取最关键的实体和动作
2. 每个子查询必须能独立完整地查询出一个特定方面的信息
3. 每个子查询占一行，不要有任何编号序列或者补充废话

子查询列表："""

    HYDE_PROMPT = """你是一个专业的内网知识服务系统专家。请根据用户的提问，**尝试假想**并直接写出一段能够完美回应该问题的文档段落。
我们不需要这个答案的内容具有绝对的真实性，但这段假想文字必须**包含该话题或领域下极其专业的术语、核心的动词与常见语境表达**。
因为我们稍后会拿着你写的这篇“假想文章”的向量，去真实的知识库里大海捞针地做相似性检索。

用户查询: {query}

请直接输出你的假想标准文档段落（字数尽量控制在 100 字左右，不要废话）："""

    def __init__(self):
        genai.configure(api_key=config.google_api_key)
        self.model = genai.GenerativeModel(config.llm_model)

    def decompose(self, query: str) -> List[str]:
        """将复杂的单一提问解构为多个更聚焦的信息点。"""
        try:
            response = self.model.generate_content(
                self.DECOMPOSITION_PROMPT.format(query=query),
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                ),
            )
            queries = [q.strip() for q in response.text.split("\n") if q.strip()]
            return queries if queries else [query]
        except Exception as e:
            print(f"查询意图分解过程发生异常: {e}")
            return [query]

    def generate_hyde(self, query: str) -> str:
        """生成 HyDE (假设性目标文档)，为向量检索锚定语义空间。"""
        try:
            response = self.model.generate_content(
                self.HYDE_PROMPT.format(query=query),
                generation_config=genai.GenerationConfig(
                    temperature=0.7,  # 适当开大幻想概率有助于包含更多隐性关联词
                ),
            )
            return response.text.strip()
        except Exception as e:
            print(f"生成假想回答 (HyDE) 失败: {e}")
            return query

    def process(
        self, query: str, use_hyde: bool = True, use_decomposition: bool = False
    ) -> Dict[str, Any]:
        """
        核心编排逻辑：
        use_hyde: 非常有助于增强向量密集型匹配的召回率。
        use_decomposition: 对 BM25 特征匹配以及大段描述性提问非常友好。
        """
        result = {
            "original_query": query,
            "vector_search_queries": [query],  # 输送给稠密向量匹配通道的内容
            "bm25_search_queries": [query],  # 输送给基于关键词的传统通道
        }

        if use_hyde:
            hyde_doc = self.generate_hyde(query)
            # HyDE 所产出的长段假想文档更贴合模型嵌入特性
            result["vector_search_queries"].append(hyde_doc)

        if use_decomposition:
            sub_queries = self.decompose(query)
            # 只有在大模型给出超过一句有用拆解时，才合并词法检索目标
            if len(sub_queries) > 1:
                result["bm25_search_queries"].extend(sub_queries)

        return result
