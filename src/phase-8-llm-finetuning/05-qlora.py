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

        ✅ 参考答案：
        13B 参数模型使用 QLoRA (4-bit):
        
        基础模型 (4-bit): 13B × 0.5 bytes = 6.5 GB
        LoRA 参数 (FP16): ~26M × 2 bytes = 0.05 GB
        梯度 (仅 LoRA): ~0.05 GB
        优化器状态: ~0.2 GB
        激活值/缓存: ~2 GB
        
        总计: ~9-10 GB
        
        对比 LoRA (FP16): 13B × 2 bytes = 26 GB + 额外 ≈ 35 GB
        节省: 约 70% 显存
    
    练习 2：配置对比
        比较 NF4 和 FP4 量化效果

        ✅ 参考答案：
        ```python
        import torch
        from transformers import BitsAndBytesConfig
        
        # NF4 配置
        nf4_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",  # NormalFloat
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
        
        # FP4 配置  
        fp4_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="fp4",  # Float Point
            bnb_4bit_compute_dtype=torch.bfloat16,
        )
        
        # 对比结果（典型）:
        # NF4: 困惑度 ↑0.1-0.3, 更适合 Transformer 权重分布
        # FP4: 困惑度 ↑0.3-0.5, 通用性较好
        # 结论: NF4 通常略优于 FP4
        ```
    
    练习 3：推理优化
        将 QLoRA 模型导出用于推理

        ✅ 参考答案：
        ```python
        from peft import PeftModel
        from transformers import AutoModelForCausalLM
        import torch
        
        # 1. 加载训练好的 QLoRA 模型
        base_model = AutoModelForCausalLM.from_pretrained(
            "base_model_name",
            torch_dtype=torch.float16,  # 反量化为 FP16
            device_map="auto",
        )
        model = PeftModel.from_pretrained(base_model, "./qlora_adapter")
        
        # 2. 合并 LoRA 权重
        merged_model = model.merge_and_unload()
        
        # 3. 保存为标准格式
        merged_model.save_pretrained("./merged_model")
        tokenizer.save_pretrained("./merged_model")
        
        # 4. 可选：重新量化用于推理
        # 使用 llama.cpp, GPTQ, AWQ 等工具
        # 例如: python quantize.py ./merged_model --bits 4
        ```
    
    思考题：
    ────────
    1. 什么情况下应该用 QLoRA 而不是 LoRA？

       ✅ 答：
       - GPU 显存有限（< 16GB）时
       - 训练更大模型（13B+）时
       - 成本敏感的场景
       - 快速原型验证
       
       使用 LoRA 的情况：
       - 追求最佳效果
       - 有足够显存
       - 需要频繁推理（量化有损）

    2. 量化精度和任务难度的关系？

       ✅ 答：
       - 简单任务（分类、命名实体）：4-bit 足够
       - 中等任务（问答、摘要）：4-bit 通常可接受
       - 复杂任务（数学推理、代码）：可能需要 8-bit 或更高
       - 创意生成：量化影响相对较小
       
       建议：先用 4-bit 尝试，效果不佳再提升精度
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
