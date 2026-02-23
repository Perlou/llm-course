"""
全管线编排调度(Orchestrator Pipeline)中心枢纽系统。
它对业务隐藏内部细节，对外作为一个独立的统制类把：抽取录入、知识节点、搜索策略判断、匹配引擎、交叉对敲重排序 这些小弟完美缝合成一套顺畅完整的生态流。
"""

import time
from typing import Dict, Any

from engine.ingestion import DocumentIngestor
from engine.indexer import DocumentIndexer
from engine.query_router import QueryRouter
from engine.fusion import FusionEngine
from retrievers.bm25 import BM25Retriever
from retrievers.dense import DenseRetriever
from reranker.cross_encoder import LocalReranker


class SearchPipeline:
    def __init__(self):
        print("正在从零启动配置并加载 V2 现代混合倒查架构引擎底盘...")
        self.ingestor = DocumentIngestor()
        self.indexer = DocumentIndexer()
        self.router = QueryRouter()
        self.fusion = FusionEngine()

        self.bm25 = BM25Retriever()
        self.dense = DenseRetriever()

        # 加载比较具有分量感压迫体积大小的交叉排列评估模型系统（如果是第一次跑没有被映射装载进系统内容 VRAM ，通常这里会耗损阻断住将近3-10秒去等待冷车启动）
        self.reranker = LocalReranker()

    def initialize_index(self, directory: str):
        """进入对一整个路径区域档案下属所有材料集中提取并且搭建大宇宙关联世界状态体系。"""
        print(f"正在从目录群 {directory} 内大规模扫除吃下未结构乱卷知识档案库语料...")
        data = self.ingestor.ingest(directory)

        parents = data["parents"]
        children = data["children"]

        if not parents:
            print("提示: 系统成功走完了一编流程但它发觉库房目前没有可喂用数据。")
            return

        self.indexer.index(parents, children)
        # 用精细版的子女切割短碎文字在内存内部中就地修造属于 BM25 特性的树形关联库
        self.bm25.build_index(children)
        print("所有底子准备打基建完成。\n")

    def search(self, raw_query: str) -> Dict[str, Any]:
        """犹如魔法一样的将最简单的一句土味人类文字输入，推向庞大精密的各个机器内部引擎进行流水过滤最终挤出完美提炼结论的执行函数旅途"""
        stats = {}
        start_time = time.time()

        # 1. 探索路由及发散: 子询问结构强迫抽丝剥茧分析与假想文档衍生预演的 HyDE
        t0 = time.time()
        routing_res = self.router.process(raw_query)
        bm25_queries = routing_res["bm25_search_queries"]
        dense_queries = routing_res["vector_search_queries"]
        stats["routing_time_ms"] = (time.time() - t0) * 1000

        # 2. 从两个截然物理与数学上不同位面同时兵分两路并发检索 (因为属于原生轻度脚本级代码暂且采用轮询模仿异步但如果日后大兵团高压重写肯定上协程 Asyncio 等手段 )
        t0 = time.time()
        all_bm25_results = []
        for q in bm25_queries:
            all_bm25_results.extend(self.bm25.search(q))

        all_dense_results = []
        for q in dense_queries:
            all_dense_results.extend(self.dense.search(q))
        stats["retrieval_time_ms"] = (time.time() - t0) * 1000
        stats["raw_bm25_hits"] = len(all_bm25_results)
        stats["raw_dense_hits"] = len(all_dense_results)

        # 3. 将这两个大杂烩派别打捞上来的名存粗算依据分数与相互位次通过强硬冷冰数学法则捏揉融合 RRF
        t0 = time.time()
        fused_candidates = self.fusion.fuse(all_bm25_results, all_dense_results)
        stats["fusion_time_ms"] = (time.time() - t0) * 1000
        stats["unique_fused_candidates"] = len(fused_candidates)

        # 4. 把这种名场面初步角逐产生的种子选手再全送去受尽苛求地拿放大审验与问题重叠咬合度，即高精度 Cross-Encoder 反向淘汰降维剔骨 Reranking 重制赛
        t0 = time.time()
        final_results = self.reranker.rerank(raw_query, fused_candidates)
        stats["rerank_time_ms"] = (time.time() - t0) * 1000

        # 5. 回馈上下文重注灌输
        # 这可谓是破局解法里最神来之笔的一个动作。因为它治愈了 RAG 由于切的越碎(更精准但丧失灵魂环境脉络)而生成大白痴症的这个天然绝痛绝症。带回去源材料老家(长文本)
        for res in final_results:
            doc = res["document"]
            parent_id = doc.metadata.get("parent_id")
            if parent_id:
                parent_doc = self.indexer.get_parent(parent_id)
                if parent_doc:
                    # 我们即刻展示这具有海量线索和旁证逻辑佐证包裹着精华的段子,同时也绝不丢失原本短切用来匹配最高得分那最精准的那一抹小灵魂闪光点核心证据
                    res["parent_context"] = parent_doc.page_content
                    res["document"] = parent_doc

        stats["total_latency_ms"] = (time.time() - start_time) * 1000

        return {"results": final_results, "stats": stats, "routing_info": routing_res}
