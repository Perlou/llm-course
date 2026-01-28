"""
数据集准备
==========

学习目标：
    1. 理解微调数据集的要求
    2. 掌握数据收集和清洗方法
    3. 学会数据格式转换

核心概念：
    - 数据质量 vs 数据量
    - 数据格式规范
    - 数据增强

环境要求：
    - pip install datasets pandas
"""

import os
import json
from typing import Dict, List, Any
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def data_requirements():
    """数据要求"""
    print("=" * 60)
    print("第一部分：微调数据要求")
    print("=" * 60)

    print("""
    数据质量 > 数据量
    ─────────────────
    
    ┌─────────────────────────────────────────────────────────┐
    │                    数据质量金字塔                        │
    │                                                         │
    │                      ┌───────┐                          │
    │                      │高质量 │ 专家标注                 │
    │                      │ 10%  │ 准确率 > 95%              │
    │                    ┌─┴───────┴─┐                        │
    │                    │  中质量   │ 众包标注               │
    │                    │   30%    │ 准确率 80-95%           │
    │                  ┌─┴───────────┴─┐                      │
    │                  │    低质量     │ 自动生成              │
    │                  │     60%      │ 需要过滤               │
    │                  └───────────────┘                      │
    └─────────────────────────────────────────────────────────┘
    
    
    数据量建议
    ─────────
    
    ┌────────────────┬───────────────┬─────────────────────┐
    │    任务类型    │   最小数据量   │     推荐数据量       │
    ├────────────────┼───────────────┼─────────────────────┤
    │ 简单分类       │    100        │    1,000 - 5,000    │
    │ 复杂分类       │    500        │    5,000 - 10,000   │
    │ 指令遵循       │   1,000       │    10,000 - 50,000  │
    │ 领域适应       │   5,000       │    50,000 - 100,000 │
    │ 对话能力       │  10,000       │    100,000+         │
    └────────────────┴───────────────┴─────────────────────┘
    """)


def data_formats():
    """数据格式"""
    print("\n" + "=" * 60)
    print("第二部分：常见数据格式")
    print("=" * 60)

    print("""
    1. 纯文本格式 (Continued Pre-training)
    ─────────────────────────────────────
    用于领域知识注入，无需标注
    
    示例：
    {
        "text": "人工智能（AI）是指由机器展示的智能..."
    }
    
    
    2. 指令格式 (Instruction Tuning)
    ────────────────────────────────
    用于训练模型遵循指令
    
    示例：
    {
        "instruction": "请将以下文本翻译成英文",
        "input": "今天天气真好",
        "output": "The weather is really nice today"
    }
    
    
    3. 对话格式 (Chat Format)
    ─────────────────────────
    用于训练对话模型
    
    示例：
    {
        "messages": [
            {"role": "system", "content": "你是一个有帮助的助手"},
            {"role": "user", "content": "什么是机器学习？"},
            {"role": "assistant", "content": "机器学习是..."}
        ]
    }
    
    
    4. 偏好对格式 (Preference Data)
    ───────────────────────────────
    用于 DPO/RLHF 训练
    
    示例：
    {
        "prompt": "请解释量子计算",
        "chosen": "量子计算利用量子力学原理...",
        "rejected": "量子计算就是很快的计算机..."
    }
    """)


def data_collection():
    """数据收集"""
    print("\n" + "=" * 60)
    print("第三部分：数据收集方法")
    print("=" * 60)

    print("""
    数据来源
    ───────
    
    1. 公开数据集
       - HuggingFace Datasets
       - Kaggle
       - 学术论文附带数据
    
    2. 企业内部数据
       - 客服对话记录
       - 文档知识库
       - 用户反馈
    
    3. 人工标注
       - 专家标注（质量高，成本高）
       - 众包标注（质量中，成本中）
    
    4. 合成数据
       - 使用 GPT-4 生成
       - 数据增强技术
    """)

    # 代码示例
    print("\n📌 数据收集代码示例：")

    code_example = """
    from datasets import load_dataset

    # 从 HuggingFace 加载公开数据集
    dataset = load_dataset("tatsu-lab/alpaca")

    # 从本地文件加载
    dataset = load_dataset("json", data_files="data.jsonl")

    # 从 CSV 加载
    dataset = load_dataset("csv", data_files="data.csv")

    # 使用 GPT-4 生成合成数据
    import openai

    def generate_training_sample(topic: str) -> dict:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "生成一个关于该主题的问答对"},
                {"role": "user", "content": f"主题: {topic}"}
            ]
        )
        # 解析并返回格式化的数据
        return parse_response(response)
    """

    print(code_example)


def data_cleaning():
    """数据清洗"""
    print("\n" + "=" * 60)
    print("第四部分：数据清洗")
    print("=" * 60)

    class DataCleaner:
        """数据清洗器"""

        def __init__(self):
            self.stats = {"total": 0, "removed": 0, "cleaned": 0}

        def clean(self, samples: List[Dict]) -> List[Dict]:
            """清洗数据"""
            cleaned = []
            for sample in samples:
                self.stats["total"] += 1

                # 1. 去除空样本
                if not sample.get("text") and not sample.get("output"):
                    self.stats["removed"] += 1
                    continue

                # 2. 去除过短样本
                text = sample.get("text") or sample.get("output", "")
                if len(text) < 10:
                    self.stats["removed"] += 1
                    continue

                # 3. 去除重复
                # 4. 规范化文本
                sample = self._normalize(sample)

                cleaned.append(sample)
                self.stats["cleaned"] += 1

            return cleaned

        def _normalize(self, sample: Dict) -> Dict:
            """文本规范化"""
            for key in ["text", "input", "output", "instruction"]:
                if key in sample and sample[key]:
                    # 去除多余空白
                    sample[key] = " ".join(sample[key].split())
            return sample

        def report(self):
            """打印统计"""
            print(f"   总样本: {self.stats['total']}")
            print(f"   保留: {self.stats['cleaned']}")
            print(f"   移除: {self.stats['removed']}")

    # 演示
    print("\n📌 数据清洗演示：")

    cleaner = DataCleaner()
    samples = [
        {"text": "这是一个有效的样本，包含足够的文本内容。"},
        {"text": ""},  # 空样本
        {"text": "太短"},  # 过短
        {"text": "这是   另一个   有效   的样本，需要规范化空白。"},
    ]

    cleaned = cleaner.clean(samples)
    cleaner.report()
    print(f"   清洗后样本数: {len(cleaned)}")


def format_conversion():
    """格式转换"""
    print("\n" + "=" * 60)
    print("第五部分：格式转换")
    print("=" * 60)

    def convert_to_alpaca(raw_data: List[Dict]) -> List[Dict]:
        """转换为 Alpaca 格式"""
        converted = []
        for item in raw_data:
            converted.append(
                {
                    "instruction": item.get("question", ""),
                    "input": item.get("context", ""),
                    "output": item.get("answer", ""),
                }
            )
        return converted

    def convert_to_chat(raw_data: List[Dict]) -> List[Dict]:
        """转换为对话格式"""
        converted = []
        for item in raw_data:
            converted.append(
                {
                    "messages": [
                        {"role": "user", "content": item.get("question", "")},
                        {"role": "assistant", "content": item.get("answer", "")},
                    ]
                }
            )
        return converted

    # 演示
    print("\n📌 格式转换演示：")

    raw_data = [
        {"question": "什么是机器学习？", "answer": "机器学习是AI的一个分支..."},
        {"question": "Python有什么特点？", "answer": "Python简洁易读..."},
    ]

    alpaca_format = convert_to_alpaca(raw_data)
    chat_format = convert_to_chat(raw_data)

    print("\n   原始格式:")
    print(f"   {raw_data[0]}")

    print("\n   Alpaca 格式:")
    print(f"   {alpaca_format[0]}")

    print("\n   Chat 格式:")
    print(f"   {chat_format[0]}")


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：准备一个小型数据集
        收集 100 条问答对，转换为 Alpaca 格式
    
    练习 2：实现去重
        基于文本相似度进行数据去重
    
    练习 3：数据增强
        使用同义词替换增强数据
    
    思考题：
    ────────
    1. 如何判断数据质量是否足够？
    2. 合成数据有什么潜在问题？
    """)


def main():
    print("📊 数据集准备")
    print("=" * 60)
    data_requirements()
    data_formats()
    data_collection()
    data_cleaning()
    format_conversion()
    exercises()
    print("\n✅ 课程完成！下一步：03-instruction-dataset.py")


if __name__ == "__main__":
    main()
