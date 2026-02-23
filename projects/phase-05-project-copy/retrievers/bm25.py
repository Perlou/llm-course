"""
BM25 词法检索器
通过使用中文 NLP 分词引擎 Jieba 对短文本进行处理，基于内置的 rank_bm25 模型进行高速精确命中的关键词短语匹配。
"""

from typing import List, Dict, Any
import jieba
from rank_bm25 import BM25Okapi
from langchain_core.documents import Document

from config import config


class BM25Retriever:
    """基于 BM25 Okapi 的传统关键词匹配重度检索器。"""

    def __init__(self):
        self.bm25: BM25Okapi = None
        self.corpus_docs: List[Document] = []

    def _tokenize(self, text: str) -> List[str]:
        """对文本进行专门为中文环境考量的分词重整 (针对全角字符不敏感)。"""
        # (提示：如果业务场景足够垂直，可选择在其中配置自己的特有虚词和停用词典库以获得完美准确率)
        return list(jieba.cut_for_search(text))

    def build_index(self, documents: List[Document]):
        """接受一个分切过后的文档组 (Child chunks)，并对这些语料数据进行倒排与分词统计和索引构建。"""
        self.corpus_docs = documents
        tokenized_corpus = [self._tokenize(doc.page_content) for doc in documents]
        self.bm25 = BM25Okapi(tokenized_corpus)
        print(
            f"BM25 关键词本地索引池已顺利完成建库，现囊括 {len(documents)} 个精确短文本子切片。"
        )

    def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        全量执行 BM25 高精准匹配寻找。
        返回的格式为 List[Dict]，内含: {"document": 文档对象, "score": float 型权重, "rank": 排名整型值}
        """
        if top_k is None:
            top_k = config.bm25_top_k

        if self.bm25 is None or not self.corpus_docs:
            print("BM25 模型尚未构建索引结构树或是空白数据库集。")
            return []

        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)

        # 将无价值的结果(小于等于零)直接丢弃
        scored_docs = [(score, i) for i, score in enumerate(scores) if score > 0]
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        results = []
        for rank, (score, i) in enumerate(scored_docs[:top_k], 1):
            results.append(
                {
                    "document": self.corpus_docs[i],
                    "score": score,
                    "rank": rank,
                    "source": "bm25",
                }
            )

        return results
