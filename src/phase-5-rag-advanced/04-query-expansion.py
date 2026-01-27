"""
查询扩展
========

学习目标：
    1. 理解查询扩展的作用
    2. 掌握同义词扩展和 LLM 扩展
    3. 学会实现查询改写

核心概念：
    - Query Expansion：扩展原始查询
    - Query Rewriting：改写查询语句
    - Multi-Query：生成多个查询变体

前置知识：
    - 03-parent-document-retriever.py

环境要求：
    - pip install langchain langchain-openai python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：查询扩展概念 ====================


def query_expansion_concept():
    """查询扩展概念"""
    print("=" * 60)
    print("第一部分：查询扩展概念")
    print("=" * 60)

    print("""
    为什么需要查询扩展？
    ────────────────────
    
    用户查询往往：
    - 表述不完整
    - 使用模糊术语
    - 缺少同义词
    
    示例：
    ─────
    原始查询：「如何减肥」
    
    扩展后：
    - 如何减肥
    - 体重管理方法
    - 健康瘦身技巧
    - 减重饮食计划
    - 运动减脂方案
    
    ┌─────────────────────────────────────────────────┐
    │                 原始查询                         │
    │           "如何写好代码"                         │
    │                   │                             │
    │                   ▼                             │
    │  ┌─────────────────────────────────────────┐   │
    │  │           查询扩展模块                    │   │
    │  │  • 同义词扩展                            │   │
    │  │  • LLM 生成变体                          │   │
    │  │  • 历史查询补充                          │   │
    │  └─────────────────────────────────────────┘   │
    │                   │                             │
    │                   ▼                             │
    │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐         │
    │  │写好  │ │代码  │ │编程  │ │开发  │         │
    │  │代码  │ │规范  │ │最佳  │ │技巧  │         │
    │  └──────┘ └──────┘ │实践  │ └──────┘         │
    │                    └──────┘                    │
    └─────────────────────────────────────────────────┘
    """)


# ==================== 第二部分：同义词扩展 ====================


def synonym_expansion():
    """同义词扩展"""
    print("\n" + "=" * 60)
    print("第二部分：同义词扩展")
    print("=" * 60)

    # 简单的同义词表
    synonyms = {
        "编程": ["编码", "写代码", "程序设计"],
        "机器学习": ["ML", "机器智能", "统计学习"],
        "人工智能": ["AI", "智能系统", "人工智慧"],
        "数据库": ["DB", "数据存储", "数据仓库"],
    }

    def expand_query(query: str, syn_dict: dict) -> list:
        """使用同义词扩展查询"""
        expanded = [query]
        for term, syns in syn_dict.items():
            if term in query:
                for syn in syns:
                    expanded.append(query.replace(term, syn))
        return expanded

    query = "机器学习入门教程"
    expanded = expand_query(query, synonyms)

    print(f"📌 原始查询: '{query}'")
    print("\n扩展结果：")
    for q in expanded:
        print(f"  - {q}")


# ==================== 第三部分：LLM 查询扩展 ====================


def llm_query_expansion():
    """LLM 查询扩展"""
    print("\n" + "=" * 60)
    print("第三部分：LLM 查询扩展")
    print("=" * 60)

    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        llm = ChatOpenAI(model="gpt-3.5-turbo")

        prompt = ChatPromptTemplate.from_template("""
你是一个查询扩展专家。给定用户的原始查询，请生成 3-5 个语义相近但表述不同的查询变体。
这些变体应该能帮助检索到更多相关文档。

原始查询: {query}

请直接列出查询变体，每行一个:""")

        chain = prompt | llm | StrOutputParser()

        query = "Python 异步编程"
        variants = chain.invoke({"query": query})

        print(f"📌 原始查询: '{query}'")
        print("\nLLM 生成的变体：")
        for line in variants.strip().split("\n"):
            if line.strip():
                print(f"  {line.strip()}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第四部分：查询改写 ====================


def query_rewriting():
    """查询改写"""
    print("\n" + "=" * 60)
    print("第四部分：查询改写")
    print("=" * 60)

    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate

        llm = ChatOpenAI(model="gpt-3.5-turbo")

        # 对话历史改写
        history_rewrite_prompt = ChatPromptTemplate.from_template("""
根据对话历史，将用户的后续问题改写为独立的完整问题。

对话历史:
{history}

用户问题: {question}

独立问题:""")

        history = """
用户: Python 有哪些 Web 框架？
助手: Python 常见的 Web 框架有 Django、Flask、FastAPI 等。
"""
        question = "它们有什么区别？"

        chain = history_rewrite_prompt | llm
        result = chain.invoke({"history": history, "question": question})

        print(f"📌 对话改写示例：")
        print(f"  原始问题: {question}")
        print(f"  改写后: {result.content}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第五部分：Step-Back Prompting ====================


def step_back_prompting():
    """Step-Back Prompting"""
    print("\n" + "=" * 60)
    print("第五部分：Step-Back Prompting")
    print("=" * 60)

    print("""
    Step-Back 策略：
    ────────────────
    对于具体问题，先「退一步」问更抽象的问题
    
    示例：
    ─────
    具体问题：「iPhone 15 的电池容量是多少？」
    
    Step-Back：「智能手机的电池技术有哪些？」
    
    这样可以获取更多背景知识
    """)

    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate

        llm = ChatOpenAI(model="gpt-3.5-turbo")

        step_back_prompt = ChatPromptTemplate.from_template("""
给定一个具体问题，请生成一个更抽象、更基础的问题。
这个问题的答案能提供回答原问题所需的背景知识。

具体问题: {question}

抽象问题:""")

        question = "GPT-4 的上下文窗口是多少？"
        chain = step_back_prompt | llm
        result = chain.invoke({"question": question})

        print(f"📌 Step-Back 示例：")
        print(f"  具体问题: {question}")
        print(f"  抽象问题: {result.content}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第六部分：集成实现 ====================


def integrated_expansion():
    """集成实现"""
    print("\n" + "=" * 60)
    print("第六部分：集成查询扩展器")
    print("=" * 60)

    code_example = '''
class QueryExpander:
    """综合查询扩展器"""
    
    def __init__(self, llm, synonyms=None):
        self.llm = llm
        self.synonyms = synonyms or {}
    
    def expand(self, query: str, method: str = "all") -> list:
        """扩展查询"""
        queries = [query]
        
        if method in ["synonym", "all"]:
            queries.extend(self._synonym_expand(query))
        
        if method in ["llm", "all"]:
            queries.extend(self._llm_expand(query))
        
        return list(set(queries))
    
    def _synonym_expand(self, query):
        expanded = []
        for term, syns in self.synonyms.items():
            if term in query:
                expanded.extend(query.replace(term, s) for s in syns)
        return expanded
    
    def _llm_expand(self, query):
        prompt = f"生成3个与'{query}'语义相近的查询变体..."
        response = self.llm.predict(prompt)
        return [q.strip() for q in response.split("\\n") if q.strip()]
'''
    print("📌 综合扩展器示例：")
    print(code_example)


# ==================== 第七部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：构建同义词库
        为你的领域构建一个同义词库。

    练习 2：对比扩展效果
        对比扩展前后检索召回率的变化。

    练习 3：动态扩展
        根据初次检索结果动态决定是否扩展。

    思考题：
        1. 扩展太多会有什么问题？
        2. 如何控制扩展的质量？
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 查询扩展")
    print("=" * 60)

    try:
        query_expansion_concept()
        synonym_expansion()
        llm_query_expansion()
        query_rewriting()
        step_back_prompting()
        integrated_expansion()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：05-multi-query-retrieval.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
