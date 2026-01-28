"""
指令数据集构建
==============

学习目标：
    1. 理解指令微调数据格式
    2. 掌握指令数据集构建方法
    3. 学会使用 GPT 生成数据

核心概念：
    - 指令格式
    - Self-Instruct
    - 数据多样性

环境要求：
    - pip install openai datasets
"""

import os
import json
from typing import Dict, List
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def instruction_format():
    """指令格式"""
    print("=" * 60)
    print("第一部分：指令格式详解")
    print("=" * 60)

    print("""
    Alpaca 格式
    ───────────
    
    {
        "instruction": "任务描述/指令",
        "input": "可选的输入上下文",
        "output": "期望的输出"
    }
    
    ┌─────────────────────────────────────────────────────────┐
    │ instruction: 翻译以下中文句子为英文                       │
    ├─────────────────────────────────────────────────────────┤  
    │ input: 今天是个好天气                                     │
    ├─────────────────────────────────────────────────────────┤
    │ output: Today is a nice day                              │
    └─────────────────────────────────────────────────────────┘
    
    
    ShareGPT 格式
    ─────────────
    
    {
        "conversations": [
            {"from": "human", "value": "用户问题"},
            {"from": "gpt", "value": "助手回答"},
            {"from": "human", "value": "追问"},
            {"from": "gpt", "value": "继续回答"}
        ]
    }
    
    
    OpenAI 格式
    ───────────
    
    {
        "messages": [
            {"role": "system", "content": "系统提示"},
            {"role": "user", "content": "用户消息"},
            {"role": "assistant", "content": "助手回复"}
        ]
    }
    """)


def instruction_templates():
    """指令模板"""
    print("\n" + "=" * 60)
    print("第二部分：指令模板")
    print("=" * 60)

    # 定义模板
    templates = {
        "qa": {
            "instruction": "请回答以下问题",
            "example": {"input": "什么是人工智能？", "output": "人工智能是..."},
        },
        "summarize": {
            "instruction": "请总结以下文本的主要内容",
            "example": {"input": "一段长文本...", "output": "文本摘要..."},
        },
        "translate": {
            "instruction": "请将以下{src_lang}文本翻译成{tgt_lang}",
            "example": {"input": "Hello world", "output": "你好世界"},
        },
        "classify": {
            "instruction": "判断以下文本的情感倾向（正面/负面/中性）",
            "example": {"input": "这个产品太棒了", "output": "正面"},
        },
        "rewrite": {
            "instruction": "请将以下文本改写为更正式的语气",
            "example": {"input": "这东西真不错", "output": "该产品具有优秀的品质"},
        },
        "code": {
            "instruction": "编写一个Python函数实现以下功能",
            "example": {
                "input": "计算列表平均值",
                "output": "def avg(l): return sum(l)/len(l)",
            },
        },
    }

    print("\n📌 常用指令模板：")
    for name, template in templates.items():
        print(f"\n   {name}:")
        print(f"      指令: {template['instruction']}")
        print(f"      示例: {template['example']}")


def self_instruct():
    """Self-Instruct 方法"""
    print("\n" + "=" * 60)
    print("第三部分：Self-Instruct 方法")
    print("=" * 60)

    print("""
    Self-Instruct 流程
    ──────────────────
    
    使用 LLM 自动生成指令数据
    
    ┌─────────────────────────────────────────────────────────┐
    │                  Self-Instruct 流程                      │
    │                                                         │
    │   ┌───────────┐                                        │
    │   │ 种子指令   │ ← 人工编写 175 条种子                   │
    │   │ Seed Tasks│                                        │
    │   └─────┬─────┘                                        │
    │         │                                               │
    │         ▼                                               │
    │   ┌───────────┐    ┌───────────┐                       │
    │   │ 生成新指令 │───▶│ 过滤去重   │                       │
    │   │ LLM 生成  │    │ 质量控制   │                       │
    │   └───────────┘    └─────┬─────┘                       │
    │         ▲                │                              │
    │         │                ▼                              │
    │         │          ┌───────────┐                       │
    │         └──────────│ 生成回答   │                       │
    │                    │ LLM 生成  │                       │
    │                    └─────┬─────┘                       │
    │                          │                              │
    │                          ▼                              │
    │                    ┌───────────┐                       │
    │                    │ 数据集    │ → 52K 指令             │
    │                    └───────────┘                       │
    └─────────────────────────────────────────────────────────┘
    """)

    print("\n📌 Self-Instruct 代码示例：")

    code_example = '''
    from openai import OpenAI

    client = OpenAI()

    def generate_instructions(seed_tasks: List[str], num_generate: int = 10) -> List[str]:
        """使用 LLM 生成新指令"""
        prompt = f"""以下是一些任务指令的示例：

{chr(10).join(f'{i+1}. {task}' for i, task in enumerate(seed_tasks[:5]))}

请生成 {num_generate} 个新的、多样化的任务指令。
要求：
- 指令要清晰具体
- 涵盖不同的任务类型
- 避免重复"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        # 解析生成的指令
        return parse_instructions(response.choices[0].message.content)

    def generate_response(instruction: str, input_text: str = "") -> str:
        """为指令生成回答"""
        prompt = f"指令: {instruction}"
        if input_text:
            prompt += f"\\n输入: {input_text}"
        prompt += "\\n\\n请提供高质量的回答："

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content
    '''

    print(code_example)


def data_diversity():
    """数据多样性"""
    print("\n" + "=" * 60)
    print("第四部分：确保数据多样性")
    print("=" * 60)

    print("""
    多样性维度
    ─────────
    
    1. 任务类型多样性
       ┌─────────────────────────────────────────────────┐
       │  问答  │  翻译  │  摘要  │  分类  │  生成  │  ... │
       └─────────────────────────────────────────────────┘
    
    2. 输入长度多样性
       - 短句（< 50 字）
       - 中等（50-200 字）
       - 长文（> 200 字）
    
    3. 领域多样性
       - 科技、医疗、法律、金融、教育...
    
    4. 难度多样性
       - 简单：直接回答
       - 中等：需要推理
       - 困难：多步骤推理
    
    5. 输出格式多样性
       - 文本、列表、表格、代码、JSON...
    """)

    @dataclass
    class DiversityAnalyzer:
        """多样性分析器"""

        def analyze(self, samples: List[Dict]) -> Dict:
            """分析数据集多样性"""
            stats = {
                "total": len(samples),
                "avg_instruction_len": 0,
                "avg_output_len": 0,
                "task_types": set(),
                "unique_ratio": 0,
            }

            inst_lens = []
            out_lens = []
            unique_insts = set()

            for s in samples:
                inst = s.get("instruction", "")
                out = s.get("output", "")
                inst_lens.append(len(inst))
                out_lens.append(len(out))
                unique_insts.add(inst)

            stats["avg_instruction_len"] = (
                sum(inst_lens) / len(inst_lens) if inst_lens else 0
            )
            stats["avg_output_len"] = sum(out_lens) / len(out_lens) if out_lens else 0
            stats["unique_ratio"] = len(unique_insts) / len(samples) if samples else 0

            return stats

    # 演示
    print("\n📌 多样性分析演示：")

    samples = [
        {"instruction": "翻译这段话", "output": "Translation..."},
        {"instruction": "总结这篇文章", "output": "Summary..."},
        {"instruction": "写一首诗", "output": "Poem..."},
    ]

    analyzer = DiversityAnalyzer()
    stats = analyzer.analyze(samples)
    print(f"   样本数: {stats['total']}")
    print(f"   唯一率: {stats['unique_ratio']:.2%}")


def practical_example():
    """实践示例"""
    print("\n" + "=" * 60)
    print("第五部分：构建指令数据集实践")
    print("=" * 60)

    def build_instruction_dataset(
        topics: List[str], samples_per_topic: int = 5
    ) -> List[Dict]:
        """构建指令数据集"""
        dataset = []

        task_templates = [
            ("解释什么是{topic}", ""),
            ("{topic}有哪些应用场景？", ""),
            ("请用简单的语言介绍{topic}", ""),
            ("{topic}的优缺点是什么？", ""),
            ("如何学习{topic}？", ""),
        ]

        for topic in topics:
            for template, input_text in task_templates[:samples_per_topic]:
                instruction = template.format(topic=topic)
                dataset.append(
                    {
                        "instruction": instruction,
                        "input": input_text,
                        "output": f"[关于{topic}的回答]",  # 实际应用中需要生成
                    }
                )

        return dataset

    # 演示
    print("\n📌 构建数据集演示：")

    topics = ["机器学习", "深度学习", "自然语言处理"]
    dataset = build_instruction_dataset(topics, samples_per_topic=3)

    print(f"   生成样本数: {len(dataset)}")
    print(f"\n   示例样本:")
    for sample in dataset[:3]:
        print(f"      - {sample['instruction']}")


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：构建领域数据集
        为特定领域（如客服）构建 100 条指令数据
    
    练习 2：数据增强
        对现有指令进行改写增强
    
    练习 3：质量评估
        设计指令数据质量评估标准
    
    思考题：
    ────────
    1. 如何平衡数据量和质量？
    2. 合成数据的局限性是什么？
    """)


def main():
    print("📝 指令数据集构建")
    print("=" * 60)
    instruction_format()
    instruction_templates()
    self_instruct()
    data_diversity()
    practical_example()
    exercises()
    print("\n✅ 课程完成！下一步：04-lora-basics.py")


if __name__ == "__main__":
    main()
