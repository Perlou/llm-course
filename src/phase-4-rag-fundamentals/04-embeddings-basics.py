"""
Embedding 模型
==============

学习目标：
    1. 理解 Embedding 的原理
    2. 掌握 Google Gemini Embedding 使用
    3. 了解其他 Embedding 选项

核心概念：
    - Embedding：将文本转换为向量
    - 向量相似度：余弦相似度
    - 语义搜索：基于向量的检索

前置知识：
    - 03-document-transformers.py

环境要求：
    - pip install langchain langchain-google-genai numpy python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：Embedding 概念 ====================


def embedding_concept():
    """Embedding 概念"""
    print("=" * 60)
    print("第一部分：Embedding 概念")
    print("=" * 60)

    print("""
    什么是 Embedding？
    ─────────────────
    
    Embedding 将文本转换为数值向量，使文本可以进行数学计算。
    
    "人工智能" → [0.12, -0.34, 0.56, ..., 0.78]  (1536维)
    
    向量特点：
    ─────────
    - 语义相似的文本，向量距离近
    - 可以用余弦相似度衡量相关性
    
    ┌─────────────────────────────────────────────┐
    │        "猫"  ●                              │
    │              ╲                              │
    │               ╲ 近                          │
    │                ●  "小猫"                    │
    │                                             │
    │        "汽车" ●─────────────● "飞机"         │
    │                     远                      │
    └─────────────────────────────────────────────┘
    """)


# ==================== 第二部分：Google Gemini Embedding ====================


def gemini_embedding():
    """Google Gemini Embedding"""
    print("\n" + "=" * 60)
    print("第二部分：Google Gemini Embedding")
    print("=" * 60)

    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

        # 单文本嵌入
        text = "人工智能正在改变世界"
        vector = embeddings.embed_query(text)

        print(f"📌 单文本嵌入：")
        print(f"  文本: {text}")
        print(f"  向量维度: {len(vector)}")
        print(f"  向量前5维: {vector[:5]}")

        # 批量嵌入
        texts = ["机器学习", "深度学习", "自然语言处理"]
        vectors = embeddings.embed_documents(texts)

        print(f"\n📌 批量嵌入：")
        print(f"  文本数: {len(texts)}")
        print(f"  向量数: {len(vectors)}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第三部分：向量相似度 ====================


def vector_similarity():
    """向量相似度计算"""
    print("\n" + "=" * 60)
    print("第三部分：向量相似度")
    print("=" * 60)

    try:
        import numpy as np
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

        # 计算相似度
        def cosine_similarity(v1, v2):
            return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

        texts = [
            "我喜欢吃苹果",
            "苹果是我最爱的水果",
            "今天天气真好",
        ]

        vectors = embeddings.embed_documents(texts)

        print("📌 相似度矩阵：")
        for i, t1 in enumerate(texts):
            for j, t2 in enumerate(texts):
                if i < j:
                    sim = cosine_similarity(vectors[i], vectors[j])
                    print(f"  '{t1[:10]}...' vs '{t2[:10]}...': {sim:.4f}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第四部分：语义搜索 ====================


def semantic_search():
    """语义搜索演示"""
    print("\n" + "=" * 60)
    print("第四部分：语义搜索")
    print("=" * 60)

    try:
        import numpy as np
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

        # 文档库
        documents = [
            "Python 是一种编程语言",
            "机器学习需要大量数据",
            "深度学习是人工智能的重要分支",
            "自然语言处理用于理解文本",
        ]

        # 查询
        query = "AI 技术"

        # 嵌入
        doc_vectors = embeddings.embed_documents(documents)
        query_vector = embeddings.embed_query(query)

        # 计算相似度
        def cosine_similarity(v1, v2):
            return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

        similarities = [cosine_similarity(query_vector, dv) for dv in doc_vectors]

        # 排序
        ranked = sorted(zip(documents, similarities), key=lambda x: x[1], reverse=True)

        print(f"📌 查询: '{query}'")
        print("\n搜索结果（按相似度排序）：")
        for doc, sim in ranked:
            print(f"  [{sim:.4f}] {doc}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第五部分：其他 Embedding 模型 ====================


def other_embeddings():
    """其他 Embedding 模型"""
    print("\n" + "=" * 60)
    print("第五部分：其他 Embedding 模型")
    print("=" * 60)

    print("""
    常用 Embedding 模型：
    
    | 模型               | 维度   | 特点                    |
    |-------------------|-------|------------------------|
    | Gemini embedding  | 768   | 免费，效果好             |
    | OpenAI ada-002    | 1536  | 效果好，付费             |
    | HuggingFace BGE   | 1024  | 开源，中文效果好          |
    | Sentence-BERT     | 768   | 开源，通用               |
    | Cohere            | 1024  | 付费，多语言             |
    
    使用 HuggingFace 模型示例：
    ─────────────────────────
    
    from langchain_community.embeddings import HuggingFaceEmbeddings
    
    # 使用 BGE 中文模型
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-zh"
    )
    
    vector = embeddings.embed_query("你好世界")
    """)


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：相似度实验
        测试同义词、反义词的向量相似度。

        ✅ 参考答案：
        ```python
        import numpy as np
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

        def cosine_similarity(v1, v2):
            return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

        # 同义词测试
        synonyms = [("高兴", "开心"), ("快速", "迅速"), ("美丽", "漂亮")]
        # 反义词测试
        antonyms = [("高兴", "悲伤"), ("快速", "缓慢"), ("美丽", "丑陋")]

        for word1, word2 in synonyms + antonyms:
            v1 = embeddings.embed_query(word1)
            v2 = embeddings.embed_query(word2)
            sim = cosine_similarity(v1, v2)
            print(f"{word1} vs {word2}: {sim:.4f}")
        # 同义词相似度通常 > 0.8，反义词相似度较低
        ```

    练习 2：多语言测试
        测试中英文相同含义文本的相似度。

        ✅ 参考答案：
        ```python
        pairs = [
            ("人工智能", "artificial intelligence"),
            ("我爱编程", "I love programming"),
            ("今天天气很好", "The weather is nice today"),
        ]

        for zh, en in pairs:
            v_zh = embeddings.embed_query(zh)
            v_en = embeddings.embed_query(en)
            sim = cosine_similarity(v_zh, v_en)
            print(f"{zh} vs {en}: {sim:.4f}")
        # 多语言模型通常能达到 0.7+ 的相似度
        ```

    练习 3：本地模型
        使用 HuggingFaceEmbeddings 运行本地模型。

        ✅ 参考答案：
        ```python
        from langchain_community.embeddings import HuggingFaceEmbeddings

        # 使用 BGE 中文模型
        local_embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-zh-v1.5",
            model_kwargs={"device": "cpu"},  # 或 "cuda"
            encode_kwargs={"normalize_embeddings": True}
        )

        text = "人工智能改变世界"
        vector = local_embeddings.embed_query(text)
        print(f"向量维度: {len(vector)}")
        ```

    思考题：
        1. Embedding 维度越高越好吗？
           
           ✅ 答案：
           - 不一定！需要权衡：
           - 高维度：表达能力强，但存储和计算成本高
           - 低维度：效率高，但可能损失信息
           - 768-1536 维是常见选择
           - 关键是模型训练质量，而非维度

        2. 不同领域的文本如何选择模型？
           
           ✅ 答案：
           - 通用文本：Gemini/OpenAI 通用模型
           - 中文文本：BGE-zh、M3E 等中文模型
           - 代码：CodeBERT、StarCoder 等
           - 医学/法律：领域专用模型
           - 建议：测试多个模型，选择效果最好的
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 Embedding 模型")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 GOOGLE_API_KEY")
        return

    try:
        embedding_concept()
        gemini_embedding()
        vector_similarity()
        semantic_search()
        other_embeddings()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：05-vector-stores-intro.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
