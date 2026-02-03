"""
MediMind - RAG 问答服务

基于检索增强生成的健康问答服务。
"""

from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass

from src.core.retriever import Retriever, RetrievalResult, get_retriever
from src.core.llm_engine import get_llm_engine, BaseLLMEngine
from src.core.prompts import (
    HEALTH_QA_SYSTEM_PROMPT,
    HEALTH_QA_USER_PROMPT,
    MEDICAL_DISCLAIMER,
    EMERGENCY_ALERT,
)
from src.utils import get_settings, log, generate_id


@dataclass
class Source:
    """来源引用"""
    title: str
    source: str
    score: float


@dataclass 
class RAGResponse:
    """RAG 响应"""
    answer: str
    sources: List[Source]
    is_emergency: bool
    conversation_id: str
    disclaimer: str = MEDICAL_DISCLAIMER


class RAGService:
    """RAG 问答服务"""

    def __init__(
        self,
        retriever: Retriever = None,
        llm_engine: BaseLLMEngine = None,
    ):
        self._retriever = retriever
        self._llm_engine = llm_engine
        
        # 紧急症状关键词
        self.emergency_keywords = [
            "胸痛", "胸闷", "呼吸困难", "喘不上气",
            "剧烈头痛", "突然头痛", "意识模糊", "昏迷",
            "大量出血", "吐血", "便血", "咯血",
            "心悸", "心跳骤停", "休克",
            "抽搐", "癫痫发作", "高烧不退",
            "中毒", "过敏性休克", "窒息",
            "严重外伤", "骨折", "脱臼",
        ]

    @property
    def retriever(self) -> Retriever:
        if self._retriever is None:
            self._retriever = get_retriever()
        return self._retriever

    @property
    def llm_engine(self) -> BaseLLMEngine:
        if self._llm_engine is None:
            self._llm_engine = get_llm_engine()
        return self._llm_engine

    def _check_emergency(self, query: str) -> bool:
        """检查是否为紧急情况"""
        for keyword in self.emergency_keywords:
            if keyword in query:
                return True
        return False

    def _build_context(self, results: List[RetrievalResult]) -> str:
        """构建上下文"""
        if not results:
            return "未找到相关参考资料。"
        
        context_parts = []
        for i, result in enumerate(results, 1):
            title = result.doc_title or "未知来源"
            context_parts.append(f"### 参考资料 {i}: {title}\n{result.content}\n")
        
        return "\n".join(context_parts)

    def _extract_sources(self, results: List[RetrievalResult]) -> List[Source]:
        """提取来源信息"""
        sources = []
        seen_titles = set()
        
        for result in results:
            title = result.doc_title or "未知来源"
            if title not in seen_titles:
                sources.append(Source(
                    title=title,
                    source=result.source,
                    score=result.score,
                ))
                seen_titles.add(title)
        
        return sources

    def query(
        self,
        question: str,
        conversation_id: str = None,
    ) -> RAGResponse:
        """
        健康问答查询
        
        Args:
            question: 用户问题
            conversation_id: 对话 ID
            
        Returns:
            RAG 响应
        """
        conversation_id = conversation_id or generate_id("conv_")
        
        # 检查紧急情况
        is_emergency = self._check_emergency(question)
        
        # 检索相关文档
        log.info(f"开始检索: {question[:50]}...")
        results = self.retriever.retrieve_for_health_qa(question)
        log.info(f"检索到 {len(results)} 个相关文档")
        
        # 构建上下文
        context = self._build_context(results)
        
        # 构建 prompt
        user_prompt = HEALTH_QA_USER_PROMPT.format(
            query=question,
            context=context,
        )
        
        # 生成回答
        log.info("调用 LLM 生成回答...")
        answer = self.llm_engine.generate(
            prompt=user_prompt,
            system_prompt=HEALTH_QA_SYSTEM_PROMPT,
        )
        
        # 如果是紧急情况，在回答前添加紧急提醒
        if is_emergency:
            answer = EMERGENCY_ALERT + "\n\n" + answer
        
        # 提取来源
        sources = self._extract_sources(results)
        
        return RAGResponse(
            answer=answer,
            sources=sources,
            is_emergency=is_emergency,
            conversation_id=conversation_id,
        )

    async def query_stream(
        self,
        question: str,
        conversation_id: str = None,
    ) -> AsyncGenerator[str, None]:
        """
        流式健康问答查询
        
        Args:
            question: 用户问题
            conversation_id: 对话 ID
            
        Yields:
            回答文本片段
        """
        # 检查紧急情况
        is_emergency = self._check_emergency(question)
        
        # 如果是紧急情况，先输出紧急提醒
        if is_emergency:
            yield EMERGENCY_ALERT + "\n\n"
        
        # 检索相关文档
        results = self.retriever.retrieve_for_health_qa(question)
        
        # 构建上下文和 prompt
        context = self._build_context(results)
        user_prompt = HEALTH_QA_USER_PROMPT.format(
            query=question,
            context=context,
        )
        
        # 流式生成回答
        async for chunk in self.llm_engine.generate_stream(
            prompt=user_prompt,
            system_prompt=HEALTH_QA_SYSTEM_PROMPT,
        ):
            yield chunk
        
        # 输出免责声明
        yield MEDICAL_DISCLAIMER


# 单例
_rag_service = None


def get_rag_service() -> RAGService:
    """获取 RAG 服务单例"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
