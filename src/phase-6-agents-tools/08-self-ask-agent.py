"""
自问自答 Agent
=============

学习目标：
    1. 理解 Self-Ask 模式原理
    2. 掌握子问题分解技术
    3. 实现 Self-Ask Agent

核心概念：
    - Follow-up Question：判断是否需要子问题
    - Intermediate Answer：中间答案
    - Final Answer：最终答案

前置知识：
    - 03-agent-types.py

环境要求：
    - pip install openai python-dotenv
"""

import os
from typing import List, Tuple
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：Self-Ask 概述 ====================


def self_ask_overview():
    """Self-Ask 概述"""
    print("=" * 60)
    print("第一部分：Self-Ask 模式概述")
    print("=" * 60)

    print("""
    Self-Ask 模式
    ─────────────
    
    通过自问自答，层层分解复杂问题：
    
    原始问题: "马斯克和贝索斯谁更有钱？"
                │
                ▼
    ┌─────────────────────────────────────┐
    │ Follow-up: 需要问子问题吗？ → 是     │
    └─────────────────────────────────────┘
                │
                ▼
    ┌─────────────────────────────────────┐
    │ Sub-Q 1: 马斯克的净资产是多少？       │
    │ Intermediate Answer: 约2000亿美元   │
    └─────────────────────────────────────┘
                │
                ▼
    ┌─────────────────────────────────────┐
    │ Sub-Q 2: 贝索斯的净资产是多少？       │
    │ Intermediate Answer: 约1500亿美元   │
    └─────────────────────────────────────┘
                │
                ▼
    ┌─────────────────────────────────────┐
    │ Follow-up: 需要更多子问题吗？ → 否    │
    └─────────────────────────────────────┘
                │
                ▼
    ┌─────────────────────────────────────┐
    │ Final Answer: 马斯克(2000亿)更有钱    │
    └─────────────────────────────────────┘
    
    适用场景：
    ✅ 多跳推理问题
    ✅ 比较类问题
    ✅ 需要组合多个独立信息
    """)


# ==================== 第二部分：Prompt 设计 ====================


def prompt_design():
    """Prompt 设计"""
    print("\n" + "=" * 60)
    print("第二部分：Self-Ask Prompt 设计")
    print("=" * 60)

    prompt = """
你是一个使用 Self-Ask 方法回答问题的助手。

回答问题时，请按以下格式：

Question: [原始问题]
Are follow-up questions needed here: [Yes/No]
Follow-up: [子问题]（如果需要）
Intermediate answer: [子问题答案]
...（重复直到不需要更多子问题）
So the final answer is: [最终答案]

示例：
Question: 贝多芬出生时莫扎特多大？
Are follow-up questions needed here: Yes
Follow-up: 贝多芬什么时候出生？
Intermediate answer: 1770年
Follow-up: 莫扎特什么时候出生？
Intermediate answer: 1756年
Are follow-up questions needed here: No
So the final answer is: 1770-1756=14，莫扎特14岁
"""

    print(prompt)


# ==================== 第三部分：Self-Ask Agent 实现 ====================


def self_ask_implementation():
    """Self-Ask Agent 实现"""
    print("\n" + "=" * 60)
    print("第三部分：Self-Ask Agent 实现")
    print("=" * 60)

    class SelfAskAgent:
        """Self-Ask Agent"""

        def __init__(self):
            # 模拟知识库
            self.knowledge = {
                "马斯克净资产": "约 2000 亿美元",
                "贝索斯净资产": "约 1500 亿美元",
                "苹果市值": "约 2.9 万亿美元",
                "微软市值": "约 3.1 万亿美元",
                "贝多芬出生": "1770年",
                "莫扎特出生": "1756年",
            }

        def need_followup(self, question: str, answers: List[str]) -> bool:
            """判断是否需要子问题"""
            # 比较类问题需要至少两个信息
            compare_words = ["谁", "哪个", "比较", "更"]
            if any(w in question for w in compare_words):
                return len(answers) < 2
            return False

        def generate_subquestion(self, question: str, step: int) -> str:
            """生成子问题"""
            if "马斯克" in question and "贝索斯" in question:
                if step == 1:
                    return "马斯克的净资产是多少？"
                elif step == 2:
                    return "贝索斯的净资产是多少？"

            if "贝多芬" in question and "莫扎特" in question:
                if step == 1:
                    return "贝多芬什么时候出生？"
                elif step == 2:
                    return "莫扎特什么时候出生？"

            return None

        def search(self, query: str) -> str:
            """搜索答案"""
            for key, value in self.knowledge.items():
                if key.replace("净资产", "").replace("出生", "") in query:
                    return value
            return "未找到相关信息"

        def synthesize(self, question: str, answers: List[Tuple[str, str]]) -> str:
            """综合答案"""
            if "马斯克" in question and "贝索斯" in question:
                return "马斯克(约2000亿美元)比贝索斯(约1500亿美元)更有钱"
            if "贝多芬" in question and "莫扎特" in question:
                return "贝多芬出生时(1770年)，莫扎特14岁(生于1756年)"
            return str(answers)

        def run(self, question: str) -> str:
            """运行 Self-Ask 循环"""
            print(f"Question: {question}")

            answers = []
            step = 0

            while self.need_followup(question, [a for _, a in answers]):
                step += 1

                # 生成子问题
                subq = self.generate_subquestion(question, step)
                if not subq:
                    break

                print(f"\nAre follow-up questions needed here: Yes")
                print(f"Follow-up: {subq}")

                # 搜索答案
                answer = self.search(subq)
                print(f"Intermediate answer: {answer}")

                answers.append((subq, answer))

                if step > 5:  # 防止无限循环
                    break

            print(f"\nAre follow-up questions needed here: No")
            final = self.synthesize(question, answers)
            print(f"So the final answer is: {final}")

            return final

    # 演示
    agent = SelfAskAgent()

    print("📌 测试 1：")
    print("-" * 40)
    agent.run("马斯克和贝索斯谁更有钱？")

    print("\n📌 测试 2：")
    print("-" * 40)
    agent.run("贝多芬出生时莫扎特多大？")


# ==================== 第四部分：与 ReAct 对比 ====================


def compare_with_react():
    """与 ReAct 对比"""
    print("\n" + "=" * 60)
    print("第四部分：Self-Ask vs ReAct")
    print("=" * 60)

    print("""
    Self-Ask vs ReAct
    ─────────────────
    
    │ 特点       │ Self-Ask        │ ReAct           │
    ├────────────┼─────────────────┼─────────────────┤
    │ 推理方式   │ 子问题分解       │ 思考-行动-观察   │
    │ 适用问题   │ 多跳、比较类     │ 通用             │
    │ 工具使用   │ 主要是搜索       │ 多种工具         │
    │ 可解释性   │ 高              │ 高               │
    │ 复杂度     │ 较低            │ 中等             │
    
    选择建议：
    ─────────
    • 比较两个实体 → Self-Ask
    • 需要多步推理，信息独立 → Self-Ask  
    • 需要多种工具配合 → ReAct
    • 复杂交互任务 → ReAct
    """)


# ==================== 第五部分：练习 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：扩展知识库
        添加更多实体信息，支持更多问题类型

        ✅ 参考答案：
        ```python
        KNOWLEDGE_BASE = {
            "人物": {
                "爱因斯坦": {"出生": "1879年", "国籍": "德国/美国", "成就": "相对论"},
                "牛顿": {"出生": "1643年", "国籍": "英国", "成就": "万有引力"},
            },
            "概念": {
                "机器学习": {"类型": "AI子领域", "应用": "图像识别、NLP"},
                "深度学习": {"类型": "机器学习子领域", "基础": "神经网络"},
            },
            "时间": {
                "Python发布": "1991年",
                "互联网诞生": "1969年",
            }
        }

        def search_knowledge(query: str) -> str:
            for category, items in KNOWLEDGE_BASE.items():
                for entity, info in items.items():
                    if entity in query:
                        return f"{entity}: {info}"
            return "未找到相关信息"
        ```
    
    练习 2：集成真实搜索
        将 search 方法改为调用真实搜索 API

        ✅ 参考答案：
        ```python
        import requests
        import os

        def real_search(query: str) -> str:
            '''调用 DuckDuckGo Instant Answer API'''
            response = requests.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                abstract = data.get("AbstractText", "")
                if abstract:
                    return abstract[:500]
                
                # 尝试获取相关主题
                topics = data.get("RelatedTopics", [])
                if topics:
                    return topics[0].get("Text", "未找到信息")
            
            return "搜索失败"
        ```
    
    练习 3：改进子问题生成
        使用 LLM 动态生成子问题

        ✅ 参考答案：
        ```python
        class LLMSelfAskAgent:
            def __init__(self, llm, search_tool):
                self.llm = llm
                self.search = search_tool

            def generate_sub_questions(self, question: str, context: str) -> list:
                '''用 LLM 生成子问题'''
                prompt = f'''
                主问题：{question}
                已知信息：{context}
                
                如果需要更多信息才能回答主问题，列出 1-2 个子问题。
                如果可以回答，返回"无需子问题"。
                
                格式：
                - 子问题1
                - 子问题2
                '''
                response = self.llm.invoke(prompt).content
                
                if "无需子问题" in response:
                    return []
                
                # 解析子问题
                questions = []
                for line in response.split("\\n"):
                    if line.strip().startswith("-"):
                        questions.append(line.strip()[1:].strip())
                return questions
        ```
    
    思考题：
        Self-Ask 有什么局限性？
        答：主要依赖搜索工具，不适合需要复杂操作的任务；子问题分解可能不够智能

        ✅ 详细答案：
        - 单一工具依赖：只用搜索，无法执行计算、操作
        - 分解质量依赖 LLM：可能生成无关子问题
        - 深度限制：多层嵌套子问题难以处理
        - 适用场景：知识检索类问题
    """)


def main():
    print("❓ 自问自答 Agent")
    print("=" * 60)

    self_ask_overview()
    prompt_design()
    self_ask_implementation()
    compare_with_react()
    exercises()

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：09-tool-router.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
