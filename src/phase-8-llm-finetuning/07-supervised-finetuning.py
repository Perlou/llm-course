"""
监督微调 (SFT)
==============

学习目标：
    1. 理解 SFT 的原理
    2. 使用 TRL 进行 SFT
    3. 掌握 SFT 最佳实践

核心概念：
    - Supervised Fine-Tuning
    - SFTTrainer
    - Chat Template

环境要求：
    - pip install trl transformers peft
"""

import os
from dotenv import load_dotenv

load_dotenv()


def sft_overview():
    """SFT 概述"""
    print("=" * 60)
    print("第一部分：SFT 概述")
    print("=" * 60)

    print("""
    Supervised Fine-Tuning (SFT)
    ────────────────────────────
    
    使用标注的指令-回答对进行有监督微调，是训练对话模型的核心步骤。
    
    
    训练流程
    ───────
    
    ┌─────────────────────────────────────────────────────────┐
    │                    SFT 训练流程                          │
    │                                                         │
    │   ┌─────────┐    ┌─────────┐    ┌─────────┐            │
    │   │  预训练  │───▶│   SFT   │───▶│  对齐   │            │
    │   │  模型   │    │  训练   │    │ (可选)  │            │
    │   └─────────┘    └────┬────┘    └─────────┘            │
    │                       │                                 │
    │                       ▼                                 │
    │              ┌─────────────────┐                        │
    │              │  Instruction    │                        │
    │              │    Dataset      │                        │
    │              │ ┌─────────────┐ │                        │
    │              │ │ 指令 + 回答  │ │                        │
    │              │ └─────────────┘ │                        │
    │              └─────────────────┘                        │
    │                                                         │
    └─────────────────────────────────────────────────────────┘
    
    
    SFT 的目标
    ─────────
    
    最大化 P(回答 | 指令)
    
    即：让模型学会根据指令生成符合期望的回答
    """)


def chat_template():
    """Chat Template"""
    print("\n" + "=" * 60)
    print("第二部分：Chat Template")
    print("=" * 60)

    print("""
    聊天模板
    ───────
    
    不同模型有不同的对话格式，需要正确应用模板。
    
    
    常见格式
    ───────
    
    1. Llama 2 格式:
    ┌─────────────────────────────────────────────────────────┐
    │ <s>[INST] <<SYS>>                                       │
    │ 你是一个有帮助的助手。                                    │
    │ <</SYS>>                                                 │
    │                                                         │
    │ 你好！ [/INST] 你好！有什么可以帮助你的吗？ </s>           │
    └─────────────────────────────────────────────────────────┘
    
    2. ChatML 格式:
    ┌─────────────────────────────────────────────────────────┐
    │ <|im_start|>system                                      │
    │ 你是一个有帮助的助手。<|im_end|>                          │
    │ <|im_start|>user                                        │
    │ 你好！<|im_end|>                                         │
    │ <|im_start|>assistant                                   │
    │ 你好！有什么可以帮助你的吗？<|im_end|>                     │
    └─────────────────────────────────────────────────────────┘
    
    3. Alpaca 格式:
    ┌─────────────────────────────────────────────────────────┐
    │ ### Instruction:                                        │
    │ {instruction}                                           │
    │                                                         │
    │ ### Input:                                              │
    │ {input}                                                 │
    │                                                         │
    │ ### Response:                                           │
    │ {output}                                                │
    └─────────────────────────────────────────────────────────┘
    """)


def sft_with_trl():
    """使用 TRL 进行 SFT"""
    print("\n" + "=" * 60)
    print("第三部分：使用 TRL 进行 SFT")
    print("=" * 60)

    print("""
    TRL (Transformer Reinforcement Learning)
    ─────────────────────────────────────────
    
    HuggingFace 的训练库，简化 SFT 和对齐训练。
    """)

    code_example = '''
    from trl import SFTTrainer, SFTConfig
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from datasets import load_dataset
    from peft import LoraConfig

    # 1. 加载模型和分词器
    model_name = "meta-llama/Llama-2-7b-hf"
    model = AutoModelForCausalLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token

    # 2. 加载数据集
    dataset = load_dataset("tatsu-lab/alpaca", split="train")

    # 3. 数据格式化函数
    def formatting_prompts_func(examples):
        output_texts = []
        for i in range(len(examples["instruction"])):
            instruction = examples["instruction"][i]
            input_text = examples["input"][i]
            output = examples["output"][i]
            
            if input_text:
                text = f"""### Instruction:
{instruction}

### Input:
{input_text}

### Response:
{output}"""
            else:
                text = f"""### Instruction:
{instruction}

### Response:
{output}"""
            
            output_texts.append(text)
        return output_texts

    # 4. LoRA 配置 (可选)
    peft_config = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        target_modules=["q_proj", "v_proj"],
    )

    # 5. 训练配置
    training_args = SFTConfig(
        output_dir="./sft_output",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=10,
        save_steps=100,
        max_seq_length=512,
    )

    # 6. 创建 SFTTrainer
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        formatting_func=formatting_prompts_func,
        tokenizer=tokenizer,
        peft_config=peft_config,
    )

    # 7. 开始训练
    trainer.train()

    # 8. 保存模型
    trainer.save_model("./sft_model")
    '''

    print(code_example)


def sft_tips():
    """SFT 技巧"""
    print("\n" + "=" * 60)
    print("第四部分：SFT 最佳实践")
    print("=" * 60)

    print("""
    最佳实践
    ───────
    
    1. 数据准备
       - 确保数据格式正确
       - 注意 EOS token 的添加
       - 只对回答部分计算 loss
    
    2. 训练参数
       - 学习率: 1e-4 到 3e-4
       - 轮数: 通常 1-3 轮
       - 批次大小: 根据显存调整
    
    3. 模板选择
       - 使用模型原生模板
       - 或使用通用模板如 ChatML
    
    4. 数据质量
       - 质量 > 数量
       - 多样性很重要
       - 清洗低质量样本
    
    
    常见问题
    ───────
    
    Q: 模型不遵循指令怎么办？
    A: - 增加数据量和多样性
       - 检查模板格式
       - 增加训练轮数
    
    Q: 模型回复太长/太短？
    A: - 调整数据中的回复长度分布
       - 使用长度控制token
    
    Q: 模型忘记预训练知识？
    A: - 降低学习率
       - 减少训练轮数
       - 混入预训练数据
    """)


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现 SFT
        使用 TRL 训练一个简单的问答模型
    
    练习 2：模板设计
        设计一个适合你任务的对话模板
    
    练习 3：数据增强
        扩展训练数据的多样性
    
    思考题：
    ────────
    1. 如何评估 SFT 的效果？
    2. SFT 和 RLHF 的关系？
    """)


def main():
    print("📚 监督微调 (SFT)")
    print("=" * 60)
    sft_overview()
    chat_template()
    sft_with_trl()
    sft_tips()
    exercises()
    print("\n✅ 课程完成！下一步：08-dpo-training.py")


if __name__ == "__main__":
    main()
