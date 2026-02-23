"""
倒数排序融合 (RRF) 引擎
负责将来自多个不同异构检索器的结果从不同量纲空间里归化聚合并统合在一起。
"""

from typing import List, Dict, Any

from config import config


class FusionEngine:
    def __init__(self):
        self.rrf_k = config.fusion_k

    def fuse(
        self, bm25_results: List[Dict[str, Any]], dense_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        利用经典的 RRF (Reciprocal Rank Fusion) 算法做混合合并: 最终得分 = 1 / (常数K + 局部排名Rank)
        入参的各个列表元素要求是携带 `document` (实体对象) 以及 `rank` (名次) 键值的字典。
        返回值则以倒数排序分数从高到低排列。
        """
        doc_scores: Dict[str, Dict[str, Any]] = {}

        # 归信第一路通道: BM25 (精准短文本匹配) 结果集
        for result in bm25_results:
            doc = result["document"]
            # 优先尝试使用具有父级约束溯源的原始文本标识
            doc_id = (
                doc.metadata.get("doc_id") or doc.metadata.get("parent_id") or id(doc)
            )

            if doc_id not in doc_scores:
                doc_scores[doc_id] = {"document": doc, "rrf_score": 0.0, "sources": []}

            rank = result["rank"]
            doc_scores[doc_id]["rrf_score"] += 1.0 / (self.rrf_k + rank)
            if "bm25" not in doc_scores[doc_id]["sources"]:
                doc_scores[doc_id]["sources"].append("bm25")

        # 归信第二路通道: Dense 向量语义模型特征召回结果集
        for result in dense_results:
            doc = result["document"]
            doc_id = (
                doc.metadata.get("doc_id") or doc.metadata.get("parent_id") or id(doc)
            )

            if doc_id not in doc_scores:
                doc_scores[doc_id] = {"document": doc, "rrf_score": 0.0, "sources": []}

            rank = result["rank"]
            doc_scores[doc_id]["rrf_score"] += 1.0 / (self.rrf_k + rank)
            if "dense" not in doc_scores[doc_id]["sources"]:
                doc_scores[doc_id]["sources"].append("dense")

        # 输出混合后的统合结果
        fused_results = list(doc_scores.values())
        fused_results.sort(key=lambda x: x["rrf_score"], reverse=True)

        # 打上终版的混合名次标签
        for rank, item in enumerate(fused_results, start=1):
            item["fusion_rank"] = rank

        return fused_results
