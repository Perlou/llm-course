"""
文档转换
========

学习目标：
    1. 理解文档转换的场景
    2. 掌握元数据处理
    3. 学会文档过滤和清洗

核心概念：
    - Document Transformers：文档转换器
    - 元数据增强：添加/修改元数据
    - 内容清洗：去除噪声

前置知识：
    - 02-text-splitters.py

环境要求：
    - pip install langchain langchain-community
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：文档转换概述 ====================


def transformer_overview():
    """文档转换概述"""
    print("=" * 60)
    print("第一部分：文档转换概述")
    print("=" * 60)

    print("""
    文档转换的应用场景：
    ────────────────────
    
    1. 元数据增强
       - 添加来源、时间戳
       - 计算文档统计信息
    
    2. 内容清洗
       - 去除多余空白
       - 过滤无关内容
    
    3. 格式转换
       - HTML 转纯文本
       - 提取表格数据
    
    4. 去重
       - 删除重复文档
       - 合并相似内容
    
    转换流程：
    
    ┌────────┐    ┌────────────┐    ┌────────┐
    │ 原始Doc │ ─▶ │ Transformer │ ─▶ │ 转换Doc │
    └────────┘    └────────────┘    └────────┘
    """)


# ==================== 第二部分：元数据处理 ====================


def metadata_handling():
    """元数据处理"""
    print("\n" + "=" * 60)
    print("第二部分：元数据处理")
    print("=" * 60)

    from langchain_core.documents import Document
    from datetime import datetime

    # 原始文档
    docs = [
        Document(
            page_content="Python 是一种编程语言", metadata={"source": "file1.txt"}
        ),
        Document(page_content="机器学习需要大量数据", metadata={"source": "file2.txt"}),
    ]

    # 添加元数据
    def add_metadata(docs):
        """添加额外元数据"""
        for doc in docs:
            doc.metadata["processed_at"] = datetime.now().isoformat()
            doc.metadata["char_count"] = len(doc.page_content)
            doc.metadata["word_count"] = len(doc.page_content.split())
        return docs

    enriched_docs = add_metadata(docs)

    print("📌 元数据增强后：")
    for doc in enriched_docs:
        print(f"  内容: {doc.page_content[:30]}...")
        print(f"  元数据: {doc.metadata}\n")


# ==================== 第三部分：内容清洗 ====================


def content_cleaning():
    """内容清洗"""
    print("\n" + "=" * 60)
    print("第三部分：内容清洗")
    print("=" * 60)

    from langchain_core.documents import Document
    import re

    def clean_document(doc: Document) -> Document:
        """清洗文档内容"""
        content = doc.page_content

        # 移除多余空白
        content = re.sub(r"\s+", " ", content)

        # 移除特殊字符
        content = re.sub(r"[^\w\s\u4e00-\u9fff.,!?，。！？]", "", content)

        # 去除首尾空白
        content = content.strip()

        return Document(
            page_content=content, metadata={**doc.metadata, "cleaned": True}
        )

    # 测试
    dirty_doc = Document(
        page_content="  这是   一段\n\n\n  很乱的   文本!!!@#$%  ",
        metadata={"source": "test.txt"},
    )

    clean_doc = clean_document(dirty_doc)

    print("📌 清洗前后对比：")
    print(f"  原始: '{dirty_doc.page_content}'")
    print(f"  清洗后: '{clean_doc.page_content}'")


# ==================== 第四部分：文档过滤 ====================


def document_filtering():
    """文档过滤"""
    print("\n" + "=" * 60)
    print("第四部分：文档过滤")
    print("=" * 60)

    from langchain_core.documents import Document

    docs = [
        Document(
            page_content="这是一段有意义的长文本，包含很多有用的信息。",
            metadata={"type": "article"},
        ),
        Document(page_content="短", metadata={"type": "fragment"}),
        Document(
            page_content="这是一段广告内容，购买请联系...", metadata={"type": "ad"}
        ),
        Document(
            page_content="技术文档：Python 函数定义使用 def 关键字。",
            metadata={"type": "doc"},
        ),
    ]

    def filter_documents(docs, min_length=10, exclude_types=None):
        """过滤文档"""
        exclude_types = exclude_types or []
        filtered = []

        for doc in docs:
            # 长度过滤
            if len(doc.page_content) < min_length:
                continue

            # 类型过滤
            if doc.metadata.get("type") in exclude_types:
                continue

            filtered.append(doc)

        return filtered

    filtered = filter_documents(docs, min_length=10, exclude_types=["ad"])

    print("📌 过滤结果：")
    print(f"  原始文档数: {len(docs)}")
    print(f"  过滤后: {len(filtered)}")
    for doc in filtered:
        print(f"    - [{doc.metadata['type']}] {doc.page_content[:30]}...")


# ==================== 第五部分：文档去重 ====================


def document_deduplication():
    """文档去重"""
    print("\n" + "=" * 60)
    print("第五部分：文档去重")
    print("=" * 60)

    from langchain_core.documents import Document
    import hashlib

    def deduplicate_docs(docs):
        """基于内容哈希去重"""
        seen = set()
        unique = []

        for doc in docs:
            # 计算内容哈希
            content_hash = hashlib.md5(doc.page_content.encode()).hexdigest()

            if content_hash not in seen:
                seen.add(content_hash)
                unique.append(doc)

        return unique

    docs = [
        Document(page_content="人工智能正在改变世界"),
        Document(page_content="机器学习是 AI 的分支"),
        Document(page_content="人工智能正在改变世界"),  # 重复
        Document(page_content="深度学习很重要"),
    ]

    unique_docs = deduplicate_docs(docs)

    print("📌 去重结果：")
    print(f"  原始: {len(docs)} 篇")
    print(f"  去重后: {len(unique_docs)} 篇")


# ==================== 第六部分：完整转换管道 ====================


def transformation_pipeline():
    """完整转换管道"""
    print("\n" + "=" * 60)
    print("第六部分：完整转换管道")
    print("=" * 60)

    from langchain_core.documents import Document
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    import re

    def create_pipeline():
        """创建文档处理管道"""

        def clean(docs):
            for doc in docs:
                doc.page_content = re.sub(r"\s+", " ", doc.page_content).strip()
            return docs

        def filter_short(docs, min_len=20):
            return [d for d in docs if len(d.page_content) >= min_len]

        def add_metadata(docs):
            for i, doc in enumerate(docs):
                doc.metadata["chunk_id"] = i
                doc.metadata["length"] = len(doc.page_content)
            return docs

        return clean, filter_short, add_metadata

    # 使用管道
    raw_docs = [
        Document(page_content="  这是    一段长文本  ", metadata={}),
        Document(page_content="短", metadata={}),
    ]

    clean, filter_short, add_meta = create_pipeline()

    result = add_meta(filter_short(clean(raw_docs)))

    print("📌 管道处理结果：")
    for doc in result:
        print(f"  内容: {doc.page_content}")
        print(f"  元数据: {doc.metadata}")


# ==================== 第七部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：自定义清洗器
        实现一个移除 URL 和 Email 的清洗函数。

    练习 2：语言检测过滤
        过滤掉非中文的文档。

    练习 3：相似度去重
        使用编辑距离或向量相似度进行模糊去重。

    思考题：
        1. 过度清洗会有什么问题？
        2. 如何保留重要的格式信息？
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 文档转换")
    print("=" * 60)

    try:
        transformer_overview()
        metadata_handling()
        content_cleaning()
        document_filtering()
        document_deduplication()
        transformation_pipeline()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：04-embeddings-basics.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
