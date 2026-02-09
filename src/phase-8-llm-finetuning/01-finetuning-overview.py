"""
微调方法概述
============

学习目标：
    1. 理解什么是 LLM 微调
    2. 掌握微调的类型和方法
    3. 了解微调的应用场景

核心概念：
    - 预训练 vs 微调
    - 全量微调 vs 参数高效微调
    - 指令微调与对齐

环境要求：
    - pip install transformers torch
"""

import os
from dotenv import load_dotenv

load_dotenv()


def finetuning_overview():
    """微调概述"""
    print("=" * 60)
    print("第一部分：什么是 LLM 微调")
    print("=" * 60)

    print("""
    LLM 训练流程
    ───────────
    
    ┌────────────┐    ┌────────────┐    ┌────────────┐
    │   预训练    │───▶│    微调     │───▶│    对齐    │
    │Pre-training│    │Fine-tuning │    │ Alignment  │
    └────────────┘    └────────────┘    └────────────┘
         │                 │                 │
         ▼                 ▼                 ▼
    海量无标注数据     领域/任务数据     人类偏好数据
    (TB级别)          (GB级别)          (MB级别)
    
    
    什么是微调？
    ──────────
    
    微调 (Fine-tuning) 是在预训练模型基础上，使用特定领域或任务的数据
    继续训练，使模型适应目标任务的过程。
    
    预训练：学习语言的通用知识
    微调：学习特定任务的专业知识
    
    
    为什么需要微调？
    ─────────────
    
    ✅ 领域适应：让模型理解专业术语（医疗、法律、金融）
    ✅ 任务优化：提升特定任务性能（问答、摘要、代码）
    ✅ 风格控制：调整输出风格（正式、幽默、简洁）
    ✅ 成本优化：小模型+微调 可能优于 大模型+提示工程
    ✅ 隐私保护：可在本地数据上训练，不泄露敏感信息
    """)


def finetuning_types():
    """微调类型"""
    print("\n" + "=" * 60)
    print("第二部分：微调类型")
    print("=" * 60)

    print("""
    微调方法分类
    ───────────
    
    ┌─────────────────────────────────────────────────────────┐
    │                    微调方法                              │
    ├─────────────────────────────────────────────────────────┤
    │                                                         │
    │   ┌─────────────────┐    ┌─────────────────────────┐   │
    │   │   全量微调       │    │    参数高效微调 (PEFT)   │   │
    │   │ Full Fine-tuning│    │                         │   │
    │   └─────────────────┘    │  ┌─────┐ ┌─────┐ ┌────┐│   │
    │          │               │  │ LoRA│ │Prefix│ │IA³ ││   │
    │          ▼               │  └─────┘ └─────┘ └────┘│   │
    │   更新所有参数           │  ┌─────┐ ┌───────────┐ │   │
    │   资源消耗大             │  │QLoRA│ │ Adapters  │ │   │
    │   效果最好               │  └─────┘ └───────────┘ │   │
    │                          └─────────────────────────┘   │
    │                                     │                   │
    │                                     ▼                   │
    │                            只更新少量参数               │
    │                            资源消耗小                   │
    │                            效果接近全量                  │
    └─────────────────────────────────────────────────────────┘
    
    
    1. 全量微调 (Full Fine-tuning)
       ────────────────────────
       - 更新模型所有参数
       - 需要大量 GPU 显存
       - 效果最好
       - 适用：资源充足，追求最佳效果
    
    2. 参数高效微调 (PEFT)
       ──────────────────
       - 只更新少量参数（0.1%-10%）
       - 显存需求大幅降低
       - 效果接近全量微调
       - 适用：资源有限，快速迭代
    
    3. 指令微调 (Instruction Tuning)
       ──────────────────────────
       - 使用指令格式的数据
       - 提升模型遵循指令能力
       - 适用：构建对话/助手模型
    
    4. 对齐训练 (Alignment)
       ────────────────────
       - RLHF：基于人类反馈的强化学习
       - DPO：直接偏好优化
       - 适用：让模型输出更符合人类期望
    """)


def finetuning_comparison():
    """微调方法对比"""
    print("\n" + "=" * 60)
    print("第三部分：微调方法对比")
    print("=" * 60)

    print("""
    方法对比
    ───────
    
    ┌─────────────┬─────────────┬─────────────┬─────────────┐
    │    方法     │  参数量     │   显存需求   │    效果     │
    ├─────────────┼─────────────┼─────────────┼─────────────┤
    │ 全量微调    │   100%      │   非常高    │    最好     │
    │ LoRA        │   0.1-1%    │   低        │    很好     │
    │ QLoRA       │   0.1-1%    │   最低      │    较好     │
    │ Prefix      │   0.1%      │   低        │    一般     │
    │ Prompt      │   <0.1%     │   最低      │    一般     │
    └─────────────┴─────────────┴─────────────┴─────────────┘
    
    
    选择建议
    ───────
    
    ┌─────────────────────────────────────────────────────────┐
    │                     选择决策树                          │
    │                                                         │
    │             ┌──────────────────┐                        │
    │             │ 有足够 GPU 资源？ │                        │
    │             └────────┬─────────┘                        │
    │                 ┌────┴────┐                             │
    │                是         否                             │
    │                 │          │                             │
    │                 ▼          ▼                             │
    │          ┌──────────┐ ┌──────────┐                      │
    │          │追求最佳效果│ │ 单卡训练？│                      │
    │          └────┬─────┘ └────┬─────┘                      │
    │            ┌──┴──┐     ┌───┴───┐                        │
    │           是    否    是      否                         │
    │            │     │     │       │                        │
    │            ▼     ▼     ▼       ▼                        │
    │        全量微调 LoRA  QLoRA  DeepSpeed                   │
    │                                +LoRA                    │
    └─────────────────────────────────────────────────────────┘
    """)


def application_scenarios():
    """应用场景"""
    print("\n" + "=" * 60)
    print("第四部分：微调应用场景")
    print("=" * 60)

    print("""
    常见应用场景
    ───────────
    
    1. 领域专家模型
       - 医疗助手：理解医学术语，提供健康建议
       - 法律顾问：解读法律条款，提供法律意见
       - 金融分析：分析财报，预测市场趋势
    
    2. 企业私有助手
       - 客服机器人：基于企业知识库回答问题
       - 内部问答：理解企业文档和流程
       - 代码助手：理解企业代码规范
    
    3. 特定任务优化
       - 文本分类：情感分析、意图识别
       - 信息抽取：命名实体识别、关系抽取
       - 文本生成：摘要、翻译、创作
    
    4. 风格/人设定制
       - 角色扮演：特定人物的说话风格
       - 品牌声音：符合品牌调性的回复
       - 教学风格：适合特定受众的讲解
    
    
    何时选择微调 vs 提示工程？
    ─────────────────────────
    
    选择提示工程：
    - 需求变化快
    - 数据量小（< 100 条）
    - 资源限制大
    
    选择微调：
    - 需求相对稳定
    - 有足够数据（> 1000 条）
    - 需要更好的性能
    - 需要降低推理成本
    """)


def simple_example():
    """简单示例"""
    print("\n" + "=" * 60)
    print("第五部分：微调代码示例")
    print("=" * 60)

    print("""
    使用 Transformers 微调的基本流程
    ─────────────────────────────
    """)

    code_example = """
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        TrainingArguments,
        Trainer
    )
    from datasets import load_dataset

    # 1. 加载模型和分词器
    model_name = "meta-llama/Llama-2-7b-hf"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # 2. 准备数据集
    dataset = load_dataset("your_dataset")

    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=512,
            padding="max_length"
        )

    tokenized_dataset = dataset.map(tokenize_function, batched=True)

    # 3. 配置训练参数
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        learning_rate=2e-5,
        save_steps=500,
        logging_steps=100,
    )

    # 4. 创建 Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["validation"],
    )

    # 5. 开始训练
    trainer.train()

    # 6. 保存模型
    trainer.save_model("./finetuned_model")
    """

    print(code_example)


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：分析场景
        给定以下场景，判断应该使用什么方法：
        - 构建法律咨询助手
        - 临时添加新产品知识
        - 在消费级 GPU 上训练

        ✅ 参考答案：
        - 构建法律咨询助手 → 微调 (LoRA/QLoRA)
          理由：需要深入理解法律术语、需求稳定、有足够数据
          
        - 临时添加新产品知识 → 提示工程 + RAG
          理由：需求变化快、知识需要频繁更新、成本低
          
        - 在消费级 GPU 上训练 → QLoRA
          理由：显存需求低（~6GB for 7B）、效果接近 LoRA
    
    练习 2：资源估算
        对于 7B 参数模型：
        - 全量微调需要多少显存？
        - LoRA 微调需要多少显存？

        ✅ 参考答案：
        7B 参数 = 7 × 10^9 参数
        
        全量微调 FP16:
        - 模型权重: 7B × 2 bytes = 14 GB
        - 梯度: 14 GB
        - 优化器状态 (Adam): 14 GB × 2 = 28 GB
        - 激活值: ~20-40 GB
        - 总计: ~80-100 GB
        
        LoRA 微调 (r=8):
        - 基础模型 FP16: 14 GB
        - LoRA 参数: ~8.4M × 2 bytes ≈ 0.017 GB
        - 梯度+优化器 (仅 LoRA): ~0.1 GB
        - 总计: ~16-20 GB
    
    思考题：
    ────────
    1. 微调是否总是比提示工程效果好？

       ✅ 答：不一定。数据质量、数据量、任务复杂度都会影响结果。
       具体来说：
       - 数据量 < 100 条：提示工程可能更好
       - 任务简单明确：提示工程足够
       - 需要深度领域知识：微调更好
       - 需要风格/格式控制：微调更好
    
    2. 微调后的模型会"忘记"原有知识吗？

       ✅ 答：可能会发生灾难性遗忘，缓解方法：
       - 降低学习率
       - 减少训练轮数
       - 混入预训练数据 (约 5-10%)
       - 使用 LoRA 等参数高效方法
       - 使用正则化技术
    """)


def main():
    print("📚 微调方法概述")
    print("=" * 60)
    finetuning_overview()
    finetuning_types()
    finetuning_comparison()
    application_scenarios()
    simple_example()
    exercises()
    print("\n✅ 课程完成！下一步：02-dataset-preparation.py")


if __name__ == "__main__":
    main()
