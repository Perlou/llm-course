"""
ReAct Agent
===========

学习目标：
    1. 理解 ReAct 模式原理
    2. 掌握 Thought-Action-Observation 循环
    3. 实现基础 ReAct Agent

核心概念：
    - ReAct：Reasoning + Acting
    - Thought：推理思考
    - Action：执行操作
    - Observation：观察结果

前置知识：
    - 01-agent-fundamentals.py

环境要求：
    - pip install google-generativeai python-dotenv
"""

import os
import re
import json
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：ReAct 概述 ====================


def react_overview():
    """ReAct 模式概述"""
    print("=" * 60)
    print("第一部分：ReAct 模式概述")
    print("=" * 60)

    print("""
    什么是 ReAct？
    ─────────────
    
    ReAct = Reasoning + Acting（推理 + 行动）
    
    传统方法的问题：
    ┌──────────────────────┬──────────────────────┐
    │   纯推理 (CoT)        │   纯行动             │
    │                      │                      │
    │ 思考→思考→思考→输出    │ 输入→行动→输出        │
    │                      │                      │
    │ ❌ 无法获取新信息     │ ❌ 缺乏规划和反思     │
    │ ❌ 容易产生幻觉       │ ❌ 容易陷入错误循环   │
    └──────────────────────┴──────────────────────┘
    
    ReAct 解决方案：
    ───────────────
    
    ┌─────────────────────────────────────────────────┐
    │                                                 │
    │   Thought ──→ Action ──→ Observation            │
    │      ↑                        │                 │
    │      └────────────────────────┘                 │
    │                                                 │
    │   ✅ 推理与行动交织                              │
    │   ✅ 基于真实反馈调整策略                        │
    │   ✅ 可解释的决策过程                            │
    │                                                 │
    └─────────────────────────────────────────────────┘
    """)


# ==================== 第二部分：ReAct 执行流程 ====================


def react_flow():
    """ReAct 执行流程示例"""
    print("\n" + "=" * 60)
    print("第二部分：ReAct 执行流程")
    print("=" * 60)

    print("""
    问题: "苹果公司和微软的市值哪个更高？"
    
    【第一轮】
    ┌─────────────────────────────────────────────────────────┐
    │ Thought 1: 我需要先查询苹果公司的当前市值                  │
    └─────────────────────────────────────────────────────────┘
                               │
                               ▼
    ┌─────────────────────────────────────────────────────────┐
    │ Action 1: search("苹果公司当前市值 2024")                 │
    └─────────────────────────────────────────────────────────┘
                               │
                               ▼
    ┌─────────────────────────────────────────────────────────┐
    │ Observation 1: 苹果公司市值约为 2.9 万亿美元               │
    └─────────────────────────────────────────────────────────┘
    
    【第二轮】
    ┌─────────────────────────────────────────────────────────┐
    │ Thought 2: 我已知道苹果市值，现在需要查询微软的市值         │
    └─────────────────────────────────────────────────────────┘
                               │
                               ▼
    ┌─────────────────────────────────────────────────────────┐
    │ Action 2: search("微软公司当前市值 2024")                 │
    └─────────────────────────────────────────────────────────┘
                               │
                               ▼
    ┌─────────────────────────────────────────────────────────┐
    │ Observation 2: 微软公司市值约为 3.1 万亿美元               │
    └─────────────────────────────────────────────────────────┘
    
    【第三轮】
    ┌─────────────────────────────────────────────────────────┐
    │ Thought 3: 我现在有两家公司的市值数据，可以比较了          │
    │ 苹果: 2.9万亿, 微软: 3.1万亿，微软市值更高                 │
    └─────────────────────────────────────────────────────────┘
                               │
                               ▼
    ┌─────────────────────────────────────────────────────────┐
    │ Final Answer: 根据最新数据，微软市值(3.1万亿美元)高于      │
    │ 苹果市值(2.9万亿美元)，微软市值更高。                      │
    └─────────────────────────────────────────────────────────┘
    """)


# ==================== 第三部分：ReAct Prompt 设计 ====================


def react_prompt_design():
    """ReAct Prompt 设计"""
    print("\n" + "=" * 60)
    print("第三部分：ReAct Prompt 设计")
    print("=" * 60)

    react_prompt = """
你是一个智能助手，使用 ReAct 方法解决问题。

可用的工具：
- search(query): 搜索互联网获取信息
- calculate(expression): 执行数学计算
- lookup(term): 在知识库中查找术语定义
- finish(answer): 给出最终答案

请严格按照以下格式回答：

Thought: [你的推理过程]
Action: [工具名称]
Action Input: [工具参数]

等待观察结果后继续推理，直到可以给出最终答案。
当你确定答案后，使用 finish 给出最终答案。

问题：{question}

{scratchpad}
"""

    print("📌 ReAct Prompt 模板：")
    print(react_prompt)

    print("""
    Prompt 设计要点：
    ─────────────────
    1. 明确列出可用工具及其功能
    2. 规定严格的输出格式
    3. 说明何时结束（finish）
    4. 保留历史推理过程（scratchpad）
    """)


# ==================== 第四部分：ReAct Agent 实现 ====================


def react_agent_implementation():
    """ReAct Agent 实现"""
    print("\n" + "=" * 60)
    print("第四部分：ReAct Agent 实现")
    print("=" * 60)

    class ReActAgent:
        """ReAct Agent 实现"""

        REACT_PROMPT = """你是一个智能助手，使用 ReAct 方法解决问题。

可用的工具：
- search(query): 搜索互联网获取信息
- calculate(expression): 执行数学计算
- finish(answer): 给出最终答案

请严格按照以下格式回答：

Thought: [你的推理过程]
Action: [工具名称]
Action Input: [工具参数]

当你确定答案后，使用 Action: finish 给出最终答案。

问题：{question}

{scratchpad}"""

        def __init__(self):
            self.tools = {
                "search": self._search,
                "calculate": self._calculate,
                "finish": self._finish,
            }
            self.scratchpad = ""

        def _search(self, query: str) -> str:
            """模拟搜索工具"""
            mock_data = {
                "苹果": "苹果公司(Apple Inc.)当前市值约为 2.9 万亿美元",
                "微软": "微软公司(Microsoft)当前市值约为 3.1 万亿美元",
                "北京天气": "北京今日天气：晴，气温 25°C，空气质量良好",
                "上海人口": "上海市常住人口约为 2400 万人",
            }
            for key, value in mock_data.items():
                if key in query:
                    return value
            return f"搜索 '{query}' 未找到相关结果"

        def _calculate(self, expression: str) -> str:
            """计算器工具"""
            try:
                # 安全计算，只允许数学运算
                result = eval(expression, {"__builtins__": {}})
                return f"计算结果: {result}"
            except Exception as e:
                return f"计算错误: {e}"

        def _finish(self, answer: str) -> str:
            """结束并返回答案"""
            return f"FINAL_ANSWER: {answer}"

        def parse_response(self, response: str) -> dict:
            """解析 LLM 响应"""
            # 提取 Thought
            thought_match = re.search(
                r"Thought:\s*(.+?)(?=\nAction:)", response, re.DOTALL
            )
            thought = thought_match.group(1).strip() if thought_match else ""

            # 提取 Action
            action_match = re.search(r"Action:\s*(\w+)", response)
            action = action_match.group(1) if action_match else "finish"

            # 提取 Action Input
            input_match = re.search(
                r"Action Input:\s*(.+?)(?=\n|$)", response, re.DOTALL
            )
            action_input = input_match.group(1).strip() if input_match else ""

            return {"thought": thought, "action": action, "action_input": action_input}

        def run(self, question: str, max_steps: int = 5) -> str:
            """运行 ReAct 循环"""
            self.scratchpad = ""

            for step in range(1, max_steps + 1):
                print(f"\n--- 第 {step} 轮 ---")

                # 模拟 LLM 响应 (简化演示)
                response = self._simulate_llm_response(question, step)

                # 解析响应
                parsed = self.parse_response(response)

                print(f"Thought: {parsed['thought']}")
                print(f"Action: {parsed['action']}")
                print(f"Action Input: {parsed['action_input']}")

                # 执行工具
                if parsed["action"] in self.tools:
                    observation = self.tools[parsed["action"]](parsed["action_input"])
                    print(f"Observation: {observation}")

                    # 检查是否完成
                    if observation.startswith("FINAL_ANSWER:"):
                        return observation.replace("FINAL_ANSWER: ", "")

                    # 更新 scratchpad
                    self.scratchpad += f"""
Thought: {parsed["thought"]}
Action: {parsed["action"]}
Action Input: {parsed["action_input"]}
Observation: {observation}
"""
                else:
                    print(f"未知工具: {parsed['action']}")

            return "达到最大步数，未能完成任务"

        def _simulate_llm_response(self, question: str, step: int) -> str:
            """模拟 LLM 响应（演示用）"""
            if "苹果" in question and "微软" in question:
                if step == 1:
                    return """Thought: 我需要先查询苹果公司的市值
Action: search
Action Input: 苹果公司市值"""
                elif step == 2:
                    return """Thought: 已知苹果市值，现在需要查询微软市值
Action: search
Action Input: 微软公司市值"""
                else:
                    return """Thought: 两家公司市值已知：苹果2.9万亿，微软3.1万亿，微软更高
Action: finish
Action Input: 根据查询结果，微软市值(3.1万亿美元)高于苹果市值(2.9万亿美元)"""

            elif "计算" in question:
                expr = re.search(r"[\d+\-*/\s]+", question)
                if expr:
                    return f"""Thought: 用户需要计算数学表达式
Action: calculate
Action Input: {expr.group().strip()}"""

            return """Thought: 我需要直接回答这个问题
Action: finish
Action Input: 请提供更具体的问题，以便我能够帮助您。"""

    # 演示
    agent = ReActAgent()

    print("📌 测试：市值比较问题")
    print("-" * 40)
    result = agent.run("苹果公司和微软的市值哪个更高？")
    print(f"\n✅ 最终答案: {result}")


# ==================== 第五部分：使用 OpenAI 的 ReAct Agent ====================


def openai_react_agent():
    """使用 OpenAI 的 ReAct Agent"""
    print("\n" + "=" * 60)
    print("第五部分：Gemini ReAct Agent（代码示例）")
    print("=" * 60)

    code_example = '''
from google.generativeai import GenerativeModel
import google.generativeai as genai

class GeminiReActAgent:
    """使用 Gemini 的 ReAct Agent"""
    
    SYSTEM_PROMPT = """你是一个使用 ReAct 方法的智能助手。

可用工具：
- search(query): 搜索信息
- calculate(expression): 数学计算  
- finish(answer): 给出最终答案

严格按照以下格式回答：
Thought: [推理过程]
Action: [工具名]
Action Input: [参数]"""

    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.tools = {
            "search": self.search,
            "calculate": self.calculate,
        }
        
    def search(self, query: str) -> str:
        # 实际应用中调用搜索 API
        return f"搜索结果：{query} 的相关信息..."
        
    def calculate(self, expr: str) -> str:
        return str(eval(expr, {"__builtins__": {}}))
    
    def run(self, question: str, max_steps: int = 5) -> str:
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"问题：{question}"}
        ]
        
        for _ in range(max_steps):
            # 调用 LLM
            chat = self.model.start_chat(history=[])
            response = chat.send_message(
                "\n".join([m["content"] for m in messages])
            )
            
            content = response.text
            parsed = self.parse_response(content)
            
            if parsed["action"] == "finish":
                return parsed["action_input"]
            
            # 执行工具
            observation = self.tools[parsed["action"]](
                parsed["action_input"]
            )
            
            # 将结果加入对话
            messages.append({
                "role": "assistant", 
                "content": content
            })
            messages.append({
                "role": "user",
                "content": f"Observation: {observation}"
            })
        
        return "未能完成任务"
'''

    print("📌 完整 Gemini ReAct Agent 实现：")
    print(code_example)


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：添加新工具
        为 ReAct Agent 添加一个 lookup 工具，用于查询术语定义。

        ✅ 参考答案：
        ```python
        DEFINITIONS = {
            "ReAct": "Reasoning + Acting，结合推理和行动的Agent框架",
            "LLM": "Large Language Model，大型语言模型",
            "RAG": "Retrieval-Augmented Generation，检索增强生成",
            "Agent": "能够自主决策和执行的智能代理",
        }

        def lookup(term: str) -> str:
            '''查询术语定义'''
            term = term.strip().upper()
            if term in DEFINITIONS:
                return f"{term}: {DEFINITIONS[term]}"
            return f"未找到 '{term}' 的定义"

        # 注册到工具列表
        tools = {
            "search": search,
            "calculator": calculator,
            "lookup": lookup,  # 新增
        }
        ```
    
    练习 2：改进解析
        改进 parse_response 函数，使其能处理更多边界情况。

        ✅ 参考答案：
        ```python
        import re

        def parse_response_improved(response: str) -> dict:
            '''改进的响应解析，处理更多边界情况'''
            result = {
                "thought": None,
                "action": None,
                "action_input": None,
                "final_answer": None,
            }
            
            # 使用正则表达式更鲁棒地提取
            thought_match = re.search(r'Thought:\\s*(.+?)(?=Action:|Final Answer:|$)', response, re.DOTALL)
            action_match = re.search(r'Action:\\s*(.+?)(?=Action Input:|$)', response, re.DOTALL)
            input_match = re.search(r'Action Input:\\s*(.+?)(?=Thought:|Observation:|$)', response, re.DOTALL)
            answer_match = re.search(r'Final Answer:\\s*(.+?)$', response, re.DOTALL)
            
            if thought_match:
                result["thought"] = thought_match.group(1).strip()
            if action_match:
                result["action"] = action_match.group(1).strip()
            if input_match:
                result["action_input"] = input_match.group(1).strip()
            if answer_match:
                result["final_answer"] = answer_match.group(1).strip()
            
            return result
        ```
    
    练习 3：集成真实 API
        将模拟的 search 工具替换为真实的搜索 API（如 Serper）。

        ✅ 参考答案：
        ```python
        import os
        import requests

        def search_with_serper(query: str) -> str:
            '''使用 Serper API 进行真实搜索'''
            api_key = os.getenv("SERPER_API_KEY")
            
            response = requests.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": api_key},
                json={"q": query}
            )
            
            if response.status_code == 200:
                results = response.json()
                # 提取前3个结果
                snippets = []
                for item in results.get("organic", [])[:3]:
                    snippets.append(f"- {item.get('snippet', '')}")
                return "\\n".join(snippets)
            
            return f"搜索失败: {response.status_code}"
        ```
    
    思考题：
    ────────
    1. ReAct 相比纯 Chain-of-Thought 有什么优势？
       答：ReAct 可以获取外部信息，基于真实反馈调整推理，
       减少幻觉，过程可追溯可解释。
    
    2. 如果 Agent 进入死循环，如何检测和处理？
       答：设置最大步数限制；检测重复的 Thought 或 Action；
       如果连续多步没有新信息，强制结束。
    
    3. 多个工具如何选择？
       答：在 Prompt 中详细描述每个工具的用途，让 LLM 根据
       任务需求选择；也可以通过 Fine-tuning 提升工具选择能力。
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🔄 ReAct Agent")
    print("=" * 60)

    react_overview()
    react_flow()
    react_prompt_design()
    react_agent_implementation()
    openai_react_agent()
    exercises()

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：03-agent-types.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
