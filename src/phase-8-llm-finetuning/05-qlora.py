"""
QLoRA 量化微调
==============

学习目标：
    1. 理解量化的基本概念
    2. 掌握 QLoRA 的工作原理
    3. 使用 QLoRA 进行微调

核心概念：
    - 量化 (Quantization)
    - 4-bit 精度
    - NF4 数据类型

环境要求：
    - pip install bitsandbytes peft transformers
"""

import os
from dotenv import load_dotenv

load_dotenv()


def quantization_basics():
    """量化基础"""
    print("=" * 60)
    print("第一部分：量化基础")
    print("=" * 60)

    print("""
    什么是量化？
    ───────────
    
    将高精度数值（如 FP32）转换为低精度（如 INT8/INT4），以减少显存占用。
    
    ┌─────────────────────────────────────────────────────────┐
    │                    精度对比                              │
    ├─────────────────────────────────────────────────────────┤
    │                                                         │
    │   FP32 (32位):  ████████████████████████████████        │
    │   FP16 (16位):  ████████████████                        │
    │   INT8 (8位):   ████████                                │
    │   INT4 (4位):   ████                                    │
    │                                                         │
    └─────────────────────────────────────────────────────────┘
    
    
    7B 模型显存需求
    ───────────────
    
    ┌────────────┬────────────┬────────────────┐
    │   精度     │  显存需求   │    适用场景     │
    ├────────────┼────────────┼────────────────┤
    │   FP32     │   28 GB    │   研究/调试     │
    │   FP16     │   14 GB    │   常规训练      │
    │   INT8     │   7 GB     │   推理优化      │
    │   INT4     │   3.5 GB   │   资源受限      │
    └────────────┴────────────┴────────────────┘
    
    
    量化方法
    ───────
    
    1. 训练后量化 (PTQ)
       - 训练完成后量化
       - 可能损失精度
    
    2. 量化感知训练 (QAT)
       - 训练时模拟量化
       - 精度损失小
    
    3. 混合精度
       - 关键层用高精度
       - 其他层用低精度
    """)


def qlora_principle():
    """QLoRA 原理"""
    print("\n" + "=" * 60)
    print("第二部分：QLoRA 原理")
    print("=" * 60)

    print("""
    QLoRA = 量化 + LoRA
    ──────────────────
    
    核心创新:
    1. 4-bit NormalFloat (NF4) 量化
    2. 双重量化 (Double Quantization)
    3. 分页优化器 (Paged Optimizers)
    
    
    QLoRA 架构
    ─────────
    
    ┌─────────────────────────────────────────────────────────┐
    │                      QLoRA                               │
    │                                                         │
    │   ┌─────────────────────────────────────────────────┐   │
    │   │           Base Model (4-bit 量化, 冻结)           │   │
    │   │                                                   │   │
    │   │   ┌────────────────────────────────────────────┐ │   │
    │   │   │  Weight (NF4)  ──dequant──▶  FP16          │ │   │
    │   │   └────────────────────────────────────────────┘ │   │
    │   └─────────────────────────────────────────────────┘   │
    │                           +                              │
    │   ┌─────────────────────────────────────────────────┐   │
    │   │           LoRA Adapters (BF16, 可训练)            │   │
    │   │                                                   │   │
    │   │   ┌─────┐     ┌─────┐                            │   │
    │   │   │  B  │  ×  │  A  │  (正常精度)                 │   │
    │   │   └─────┘     └─────┘                            │   │
    │   └─────────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────────┘
    
    
    NF4 量化
    ────────
    
    NormalFloat 4-bit: 专为正态分布的神经网络权重设计
    - 比 INT4 更适合 Transformer 权重分布
    - 信息损失更小
    
    
    双重量化
    ───────
    
    量化过程中的缩放因子也进行量化:
    - 每 64 个参数共享一个缩放因子
    - 缩放因子从 FP32 量化到 8-bit
    - 进一步减少显存
    """)


def qlora_code():
    """QLoRA 代码"""
    print("\n" + "=" * 60)
    print("第三部分：QLoRA 代码实现")
    print("=" * 60)

    print("""
    使用 QLoRA 微调
    ───────────────
    """)

    code_example = """
    import torch
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        TrainingArguments,
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

    # 1. 配置 4-bit 量化
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,                    # 使用 4-bit 加载
        bnb_4bit_quant_type="nf4",            # NF4 量化类型
        bnb_4bit_compute_dtype=torch.bfloat16,# 计算精度
        bnb_4bit_use_double_quant=True,       # 双重量化
    )

    # 2. 加载量化模型
    model = AutoModelForCausalLM.from_pretrained(
        "meta-llama/Llama-2-7b-hf",
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )

    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

    # 3. 准备模型用于 k-bit 训练
    model = prepare_model_for_kbit_training(model)

    # 4. 配置 LoRA
    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )

    # 5. 应用 LoRA
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    # 输出: trainable params: 6,553,600 || all params: 3,500,544,000 || 0.19%

    # 6. 训练
    training_args = TrainingArguments(
        output_dir="./qlora_output",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=10,
        optim="paged_adamw_32bit",  # 分页优化器
    )
    """

    print(code_example)


def qlora_tips():
    """QLoRA 技巧"""
    print("\n" + "=" * 60)
    print("第四部分：QLoRA 使用技巧")
    print("=" * 60)

    print("""
    显存对比
    ───────
    
    以 7B 模型为例:
    
    ┌─────────────────┬────────────┬─────────────────┐
    │     方法        │   显存     │    GPU 要求      │
    ├─────────────────┼────────────┼─────────────────┤
    │ 全量微调 FP16   │  ~100 GB   │   多卡 A100      │
    │ LoRA FP16       │  ~16 GB    │   单卡 A100/3090 │
    │ QLoRA 4-bit     │  ~6 GB     │   单卡 3080 可行 │
    └─────────────────┴────────────┴─────────────────┘
    
    
    最佳实践
    ───────
    
    1. 量化类型选择
       - 优先使用 NF4
       - FP4 作为备选
    
    2. 计算精度
       - BF16 (推荐，如果硬件支持)
       - FP16 (兼容性好)
    
    3. 优化器选择
       - paged_adamw_32bit (显存友好)
       - paged_adamw_8bit (更省显存)
    
    4. 批次大小
       - 使用梯度累积来模拟大批次
       - per_device_batch_size=1-4
       - gradient_accumulation_steps=8-16
    
    
    常见问题
    ───────
    
    Q: 量化后推理速度会变慢吗？
    A: 通常会稍慢，因为需要反量化。
       但可以使用专门的量化推理引擎加速。
    
    Q: 量化会损失多少精度？
    A: NF4 + LoRA 通常损失很小，
       在很多任务上接近全量微调效果。
    
    Q: QLoRA 和 LoRA 结果可以合并吗？
    A: 可以，但需要先反量化基础模型，
       再合并 LoRA 权重。
    """)


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：显存计算
        计算 13B 模型使用 QLoRA 需要多少显存
    
    练习 2：配置对比
        比较 NF4 和 FP4 量化效果
    
    练习 3：推理优化
        将 QLoRA 模型导出用于推理
    
    思考题：
    ────────
    1. 什么情况下应该用 QLoRA 而不是 LoRA？
    2. 量化精度和任务难度的关系？
    """)


def main():
    print("⚡ QLoRA 量化微调")
    print("=" * 60)
    quantization_basics()
    qlora_principle()
    qlora_code()
    qlora_tips()
    exercises()
    print("\n✅ 课程完成！下一步：06-peft-library.py")


if __name__ == "__main__":
    main()
