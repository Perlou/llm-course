"""
辩论式 Agent (Debate Agents)
============================

学习目标：
    1. 理解辩论式多 Agent 模式
    2. 实现正反方辩论系统
    3. 学会使用裁判 Agent 总结

核心概念：
    - 对抗性思考
    - 多角度分析
    - 共识达成

环境要求：
    - pip install openai python-dotenv
"""

import os
from dotenv import load_dotenv
from typing import Dict, List, Any
from dataclasses import dataclass

load_dotenv()


def debate_overview():
    """辩论模式概述"""
    print("=" * 60)
    print("第一部分：辩论式 Agent 概述")
    print("=" * 60)

    print("""
    辩论式 Agent 模式
    ─────────────────
    
    多个 Agent 从不同角度讨论问题，通过对抗性思考得出更好的结论。
    
         ┌─────────────────────────────────────┐
         │              Topic                   │
         └───────────────┬─────────────────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
         ┌─────────┐          ┌─────────┐
         │ Pro     │ ◄──────► │ Con     │
         │ 正方    │  辩论    │ 反方    │
         └────┬────┘          └────┬────┘
              │                    │
              └────────┬───────────┘
                       ▼
                 ┌──────────┐
                 │  Judge   │
                 │  裁判    │
                 └────┬─────┘
                      ▼
                 结论总结
    
    适用场景：
    ✅ 需要多角度分析的问题
    ✅ 决策制定和风险评估
    ✅ 创意发散和收敛
    ✅ 观点验证和批判性思考
    """)


def debate_implementation():
    """辩论系统实现"""
    print("\n" + "=" * 60)
    print("第二部分：辩论系统实现")
    print("=" * 60)

    @dataclass
    class Argument:
        """论点"""

        position: str  # pro/con
        content: str
        strength: int  # 1-10

    class DebateAgent:
        """辩论 Agent"""

        def __init__(self, name: str, position: str):
            self.name = name
            self.position = position  # "pro" or "con"
            self.arguments: List[Argument] = []

        def make_argument(self, topic: str, round_num: int) -> Argument:
            """提出论点"""
            if self.position == "pro":
                content = f"[{self.name}] 第{round_num}轮正方论点：支持{topic}，因为..."
            else:
                content = f"[{self.name}] 第{round_num}轮反方论点：反对{topic}，因为..."

            arg = Argument(self.position, content, round_num + 5)
            self.arguments.append(arg)
            return arg

        def rebut(self, opponent_arg: Argument) -> str:
            """反驳"""
            return (
                f"[{self.name}] 反驳：针对'{opponent_arg.content[:20]}...'，我认为..."
            )

    class JudgeAgent:
        """裁判 Agent"""

        def __init__(self):
            self.name = "Judge"

        def evaluate(self, pro_args: List[Argument], con_args: List[Argument]) -> Dict:
            """评估辩论"""
            pro_score = sum(a.strength for a in pro_args)
            con_score = sum(a.strength for a in con_args)

            return {
                "pro_score": pro_score,
                "con_score": con_score,
                "winner": "正方" if pro_score > con_score else "反方",
                "summary": f"经过评估，{('正方' if pro_score > con_score else '反方')}论点更具说服力",
            }

    class DebateSystem:
        """辩论系统"""

        def __init__(self, topic: str):
            self.topic = topic
            self.pro = DebateAgent("正方辩手", "pro")
            self.con = DebateAgent("反方辩手", "con")
            self.judge = JudgeAgent()

        def run_debate(self, rounds: int = 3) -> Dict:
            """运行辩论"""
            print(f"\n📢 辩题：{self.topic}")
            print("=" * 50)

            for r in range(1, rounds + 1):
                print(f"\n🔔 第 {r} 轮")
                print("-" * 40)

                pro_arg = self.pro.make_argument(self.topic, r)
                print(f"   {pro_arg.content}")

                con_arg = self.con.make_argument(self.topic, r)
                print(f"   {con_arg.content}")

                if r > 1:
                    print(f"   {self.pro.rebut(con_arg)}")
                    print(f"   {self.con.rebut(pro_arg)}")

            print("\n⚖️ 裁判评议")
            print("-" * 40)
            result = self.judge.evaluate(self.pro.arguments, self.con.arguments)
            print(f"   正方得分: {result['pro_score']}")
            print(f"   反方得分: {result['con_score']}")
            print(f"   🏆 获胜方: {result['winner']}")

            return result

    # 演示
    print("\n🚀 辩论演示：")
    debate = DebateSystem("人工智能是否应该有自主决策权")
    debate.run_debate(3)


def llm_debate():
    """使用 LLM 的辩论系统"""
    print("\n" + "=" * 60)
    print("第三部分：使用 LLM 的辩论系统")
    print("=" * 60)

    print("""
    LLM 辩论代码示例：
    
    class LLMDebateAgent:
        def __init__(self, client, position: str):
            self.client = client
            self.position = position
            self.persona = "支持者" if position == "pro" else "反对者"

        async def argue(self, topic: str, history: List) -> str:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"你是{topic}的{self.persona}，请提出有力论点。"},
                    {"role": "user", "content": f"辩题：{topic}\\n历史：{history}"}
                ]
            )
            return response.choices[0].message.content

    class LLMJudge:
        async def evaluate(self, topic: str, debate_log: List) -> str:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "你是公正的辩论裁判，请总结双方观点并给出结论。"},
                    {"role": "user", "content": f"辩题：{topic}\\n辩论记录：{debate_log}"}
                ]
            )
            return response.choices[0].message.content
    """)


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：添加多方辩论 - 支持3+个立场

        ✅ 参考答案：
        ```python
        class MultiPartyDebate:
            def __init__(self, llm, positions: list):
                self.llm = llm
                self.positions = positions  # ["支持", "反对", "中立"]
            
            def debate(self, topic: str, rounds: int = 2):
                history = []
                
                for round_num in range(rounds):
                    for position in self.positions:
                        prompt = f'''
                        话题：{topic}
                        你的立场：{position}
                        历史辩论：{history[-6:]}  # 只看最近几轮
                        
                        请从你的立场发表观点，回应之前的论点：
                        '''
                        argument = self.llm.invoke(prompt).content
                        history.append({"position": position, "argument": argument})
                
                return history
        ```

    练习 2：实现观众投票 - 每轮后观众评分

        ✅ 参考答案：
        ```python
        class DebateWithVoting:
            def __init__(self, llm, num_judges: int = 3):
                self.llm = llm
                self.num_judges = num_judges
            
            def evaluate_round(self, pro_arg: str, con_arg: str):
                votes = {"pro": 0, "con": 0}
                
                for i in range(self.num_judges):
                    prompt = f'''
                    作为评委 {i+1}，评估以下辩论：
                    正方：{pro_arg}
                    反方：{con_arg}
                    
                    谁更有说服力？回答 "pro" 或 "con"：
                    '''
                    vote = self.llm.invoke(prompt).content.strip().lower()
                    if "pro" in vote:
                        votes["pro"] += 1
                    else:
                        votes["con"] += 1
                
                return votes
        ```

    练习 3：使用 LangGraph 实现辩论流程

        ✅ 参考答案：
        ```python
        from langgraph.graph import StateGraph, END

        class DebateState(TypedDict):
            topic: str
            round: int
            max_rounds: int
            pro_arguments: list
            con_arguments: list
            verdict: str

        def pro_speak(state):
            # 正方发言
            return {"pro_arguments": state["pro_arguments"] + [pro_arg]}

        def con_speak(state):
            # 反方发言
            return {"con_arguments": state["con_arguments"] + [con_arg]}

        def check_continue(state):
            if state["round"] >= state["max_rounds"]:
                return "judge"
            return "pro"

        graph = StateGraph(DebateState)
        graph.add_node("pro", pro_speak)
        graph.add_node("con", con_speak)
        graph.add_node("judge", judge_debate)
        graph.add_edge("pro", "con")
        graph.add_conditional_edges("con", check_continue)
        graph.add_edge("judge", END)
        ```
    
    思考题：
    1. 如何确保 AI 辩论的公平性？

       ✅ 答：使用相同的 LLM，随机化发言顺序，
       提供均等的信息和 token 限制，多评委机制。

    2. 辩论结果如何用于实际决策？

       ✅ 答：提取各方核心论点和证据，量化论点强度，
       识别共识和分歧，为决策者提供多角度参考。
    """)


def main():
    print("⚔️ 辩论式 Agent")
    print("=" * 60)
    debate_overview()
    debate_implementation()
    llm_debate()
    exercises()
    print("\n✅ 课程完成！下一步：07-agent-workflows.py")


if __name__ == "__main__":
    main()
