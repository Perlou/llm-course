"""
核心打分模型模块(Rerank)
取代了阶段 05 中使用原先造价大且响应慢死板大语言模型作为审核打分的设定。
采取 `Sentence-Transformers` 底导所挂靠的 Cross-Encoder 模型来实现以极高性能速度给段落进行相似打分，保证第一页推荐质量最优。
"""

from typing import List, Dict, Any
from sentence_transformers import CrossEncoder
import torch

from config import config


class LocalReranker:
    """基于本地显卡或核心运算器的交叉打分重排序通道库。"""

    def __init__(self):
        print(
            f"正在准备调用系统底层资源与部署挂载在重排模块上所请求指定的模型: {config.reranker_model}..."
        )
        # 智能化适配苹果系统自有的 M 系列硅片 MPS 加速架构。或者常规英伟达系 CUDA ，甚至是最纯粹基础兜底 CPU 演算
        device = (
            "mps"
            if torch.backends.mps.is_available()
            else ("cuda" if torch.cuda.is_available() else "cpu")
        )
        self.model = CrossEncoder(
            config.reranker_model,
            max_length=512,
            default_activation_function=torch.nn.Sigmoid(),
            device=device,
        )
        print(f"高级语义重排序(Cross-Encoder)装载准备完毕。正在使用 {device} 跑推理。")

    def rerank(
        self, query: str, results: List[Dict[str, Any]], top_n: int = None
    ) -> List[Dict[str, Any]]:
        """
        开始进入二次打分精确修正。
        传入的 `results` 变量，是指带有 `document` 原始文档文本片段内容的包裹字字典集合阵列组合
        """
        if top_n is None:
            top_n = config.rerank_top_n

        if not results:
            return []

        # 整理成 (用户问词, 内容原文被评估候选对象片段) 将这对 CP 成排地放入评估预处理数列
        pairs = []
        for result in results:
            doc = result["document"]
            pairs.append([query, doc.page_content])

        # 让 AI 预见相关联值
        # 它被挂钩给出的输出阈值是一个强行的 S 曲线激活数，故此这个区间只能框限落在极弱到强（0至1 之间）。
        scores = self.model.predict(pairs).tolist()

        # 最后组装拼贴这些数值并按照其最终分从左到右去粗取精列出来给人类阅读。
        for i, result in enumerate(results):
            result["cross_encoder_score"] = scores[i]

        # 依照它自身的交叉评估强分数从大到小的正经地排队归纳入集。
        results.sort(key=lambda x: x["cross_encoder_score"], reverse=True)

        # 给这些名列前茅留下的种子选手正式佩上最后被筛选出来的荣誉勋章排位标签数字序号标识。
        for rank, item in enumerate(results, start=1):
            item["final_rank"] = rank

        return results[:top_n]
