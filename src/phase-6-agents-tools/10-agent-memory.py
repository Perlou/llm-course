"""
Agent 记忆管理
=============

学习目标：
    1. 理解 Agent 记忆系统架构
    2. 实现短期和长期记忆
    3. 掌握记忆检索和压缩

核心概念：
    - 短期记忆：当前对话历史
    - 长期记忆：向量化存储
    - 工作记忆：当前任务状态

前置知识：
    - Phase 4 RAG 基础

环境要求：
    - pip install openai python-dotenv chromadb
"""

import os
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：记忆系统架构 ====================


def memory_architecture():
    """记忆系统架构"""
    print("=" * 60)
    print("第一部分：记忆系统架构")
    print("=" * 60)

    print("""
    Agent 记忆系统
    ─────────────
    
    ┌─────────────────────────────────────────────────────┐
    │                    记忆系统                          │
    │                                                     │
    │  ┌────────────────────────────────────────────┐    │
    │  │              短期记忆                       │    │
    │  │  [消息1] → [消息2] → [消息3] → ...          │    │
    │  │  • 当前对话上下文                           │    │
    │  │  • 有容量限制（窗口大小）                    │    │
    │  └──────────────────┬─────────────────────────┘    │
    │                     │ 压缩/总结                      │
    │                     ▼                               │
    │  ┌────────────────────────────────────────────┐    │
    │  │              长期记忆                       │    │
    │  │  ┌─────────────────────────────────────┐  │    │
    │  │  │           向量数据库                 │  │    │
    │  │  │  [知识] [历史总结] [用户偏好]        │  │    │
    │  │  └─────────────────────────────────────┘  │    │
    │  └────────────────────────────────────────────┘    │
    │                                                     │
    │  ┌────────────────────────────────────────────┐    │
    │  │              工作记忆                       │    │
    │  │  • 当前任务状态                            │    │
    │  │  • 临时变量                                │    │
    │  └────────────────────────────────────────────┘    │
    │                                                     │
    └─────────────────────────────────────────────────────┘
    """)


# ==================== 第二部分：短期记忆 ====================


def short_term_memory():
    """短期记忆"""
    print("\n" + "=" * 60)
    print("第二部分：短期记忆")
    print("=" * 60)

    class ShortTermMemory:
        """短期记忆实现"""

        def __init__(self, max_messages: int = 10):
            self.messages: List[Dict] = []
            self.max_messages = max_messages

        def add(self, role: str, content: str):
            """添加消息"""
            self.messages.append(
                {
                    "role": role,
                    "content": content,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # 保持窗口大小
            if len(self.messages) > self.max_messages:
                self._compress()

        def _compress(self):
            """压缩旧消息"""
            # 保留最新的一半消息
            keep = self.max_messages // 2
            old = self.messages[:-keep]

            # 简化：取摘要（实际应用中用 LLM 总结）
            summary = f"[摘要: {len(old)} 条历史消息]"

            self.messages = [{"role": "system", "content": summary}] + self.messages[
                -keep:
            ]

            print(f"  ⚠️ 压缩了 {len(old)} 条消息")

        def get_messages(self) -> List[Dict]:
            """获取消息列表"""
            return [{"role": m["role"], "content": m["content"]} for m in self.messages]

        def clear(self):
            """清空记忆"""
            self.messages = []

    # 演示
    memory = ShortTermMemory(max_messages=5)

    print("📌 短期记忆演示：")
    for i in range(7):
        memory.add("user", f"消息 {i + 1}")
        print(f"  添加消息 {i + 1}，当前消息数: {len(memory.messages)}")


# ==================== 第三部分：长期记忆 ====================


def long_term_memory():
    """长期记忆"""
    print("\n" + "=" * 60)
    print("第三部分：长期记忆")
    print("=" * 60)

    class LongTermMemory:
        """长期记忆（简化版）"""

        def __init__(self):
            self.memories: List[Dict] = []

        def store(self, content: str, metadata: Dict = None):
            """存储记忆"""
            self.memories.append(
                {
                    "content": content,
                    "metadata": metadata or {},
                    "timestamp": datetime.now().isoformat(),
                }
            )

        def search(self, query: str, top_k: int = 3) -> List[str]:
            """搜索记忆（简化：关键词匹配）"""
            results = []
            query_words = set(query.lower().split())

            for mem in self.memories:
                content_words = set(mem["content"].lower().split())
                if query_words & content_words:
                    results.append(mem["content"])

            return results[:top_k]

    memory = LongTermMemory()

    # 存储一些记忆
    memory.store("用户喜欢使用 Python 编程")
    memory.store("上次对话讨论了 AI Agent 技术")
    memory.store("用户是一名软件工程师")

    print("📌 长期记忆演示：")
    print(f"  存储了 {len(memory.memories)} 条记忆")

    results = memory.search("Python 技术")
    print(f"  搜索 'Python 技术': {results}")


# ==================== 第四部分：工作记忆 ====================


def working_memory():
    """工作记忆"""
    print("\n" + "=" * 60)
    print("第四部分：工作记忆")
    print("=" * 60)

    class WorkingMemory:
        """工作记忆"""

        def __init__(self):
            self.state: Dict[str, Any] = {}
            self.task_context: Dict = {}

        def set(self, key: str, value: Any):
            """设置变量"""
            self.state[key] = value

        def get(self, key: str, default=None) -> Any:
            """获取变量"""
            return self.state.get(key, default)

        def set_task(self, task: str, steps: List[str]):
            """设置当前任务"""
            self.task_context = {
                "task": task,
                "steps": steps,
                "current_step": 0,
                "completed": [],
            }

        def next_step(self) -> str:
            """获取下一步"""
            idx = self.task_context["current_step"]
            if idx < len(self.task_context["steps"]):
                return self.task_context["steps"][idx]
            return None

        def complete_step(self):
            """完成当前步骤"""
            step = self.next_step()
            if step:
                self.task_context["completed"].append(step)
                self.task_context["current_step"] += 1

    memory = WorkingMemory()

    print("📌 工作记忆演示：")
    memory.set("user_name", "张三")
    memory.set_task("撰写报告", ["收集资料", "整理大纲", "撰写内容"])

    print(f"  用户: {memory.get('user_name')}")
    print(f"  当前任务: {memory.task_context['task']}")
    print(f"  下一步: {memory.next_step()}")

    memory.complete_step()
    print(f"  完成后下一步: {memory.next_step()}")


# ==================== 第五部分：统一记忆系统 ====================


def unified_memory():
    """统一记忆系统"""
    print("\n" + "=" * 60)
    print("第五部分：统一记忆系统")
    print("=" * 60)

    class AgentMemory:
        """Agent 统一记忆系统"""

        def __init__(self):
            self.short_term: List[Dict] = []
            self.long_term: List[Dict] = []
            self.working: Dict = {}

        def add_message(self, role: str, content: str):
            """添加对话消息"""
            self.short_term.append({"role": role, "content": content})

        def save_to_long_term(self, content: str):
            """保存到长期记忆"""
            self.long_term.append({"content": content})

        def recall(self, query: str) -> str:
            """回忆相关信息"""
            # 从长期记忆中检索
            for mem in self.long_term:
                if query.lower() in mem["content"].lower():
                    return mem["content"]
            return ""

        def get_context(self) -> str:
            """获取当前上下文"""
            context = ""

            # 添加相关长期记忆
            if self.long_term:
                context += "相关信息：\n"
                for mem in self.long_term[-3:]:
                    context += f"- {mem['content']}\n"

            # 添加最近对话
            context += "\n最近对话：\n"
            for msg in self.short_term[-5:]:
                context += f"{msg['role']}: {msg['content']}\n"

            return context

    memory = AgentMemory()
    memory.save_to_long_term("用户偏好：简洁的回复风格")
    memory.add_message("user", "你好")
    memory.add_message("assistant", "你好！有什么可以帮助你的？")

    print("📌 统一记忆上下文：")
    print(memory.get_context())


# ==================== 第六部分：练习 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现 LLM 摘要压缩
        用 LLM 总结旧消息而非简单截断

        ✅ 参考答案：
        ```python
        class SummarizingMemory:
            def __init__(self, llm, max_messages: int = 10):
                self.llm = llm
                self.max_messages = max_messages
                self.messages = []
                self.summary = ""

            def add_message(self, role: str, content: str):
                self.messages.append({"role": role, "content": content})
                
                if len(self.messages) > self.max_messages:
                    self.compress()

            def compress(self):
                '''压缩旧消息为摘要'''
                old_messages = self.messages[:5]
                text = "\\n".join([f"{m['role']}: {m['content']}" for m in old_messages])
                
                prompt = f'''
                总结以下对话的关键信息（一句话）：
                {text}
                '''
                new_summary = self.llm.invoke(prompt).content
                
                # 合并摘要
                self.summary = f"{self.summary}\\n{new_summary}".strip()
                self.messages = self.messages[5:]

            def get_context(self):
                return f"历史摘要：{self.summary}\\n\\n最近对话：{self.messages}"
        ```
    
    练习 2：集成向量数据库
        使用 ChromaDB 实现语义搜索

        ✅ 参考答案：
        ```python
        from langchain_chroma import Chroma
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        class SemanticMemory:
            def __init__(self):
                self.embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
                self.vectorstore = Chroma(embedding_function=self.embeddings)
                self.memory_id = 0

            def add_memory(self, content: str, metadata: dict = None):
                '''添加记忆到向量库'''
                self.vectorstore.add_texts(
                    texts=[content],
                    metadatas=[{"id": self.memory_id, **(metadata or {})}]
                )
                self.memory_id += 1

            def search(self, query: str, k: int = 3):
                '''语义搜索相关记忆'''
                results = self.vectorstore.similarity_search(query, k=k)
                return [doc.page_content for doc in results]

            def get_relevant_context(self, query: str):
                '''获取与当前查询相关的上下文'''
                memories = self.search(query)
                return "\\n".join(memories)
        ```
    
    思考题：
        如何平衡记忆容量和检索效率？
        答：分层存储，热数据在内存，冷数据在向量库

        ✅ 详细答案：
        - 分层架构：
          * L1（内存）：最近 5-10 条消息
          * L2（向量库）：语义索引的历史记忆
          * L3（数据库）：完整历史存档
        
        - 优化策略：
          * 定期压缩和摘要
          * 基于重要性过滤
          * 惰性加载长期记忆
          * 设置合理的 TTL
    """)


def main():
    print("🧠 Agent 记忆管理")
    print("=" * 60)

    memory_architecture()
    short_term_memory()
    long_term_memory()
    working_memory()
    unified_memory()
    exercises()

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：11-mcp-introduction.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
