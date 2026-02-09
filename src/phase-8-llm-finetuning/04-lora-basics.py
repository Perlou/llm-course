"""
LoRA 原理与实现
===============

学习目标：
    1. 理解 LoRA 的核心原理
    2. 掌握 LoRA 的关键参数
    3. 学会使用 LoRA 微调

核心概念：
    - 低秩分解
    - 秩 (rank)
    - Alpha 缩放因子

环境要求：
    - pip install peft transformers torch
"""

import os
from dotenv import load_dotenv

load_dotenv()


def lora_principle():
    """LoRA 原理"""
    print("=" * 60)
    print("第一部分：LoRA 核心原理")
    print("=" * 60)

    print("""
    LoRA: Low-Rank Adaptation
    ─────────────────────────
    
    核心思想：不更新原始权重，而是学习一个低秩的增量矩阵
    
    
    传统微调 vs LoRA
    ────────────────
    
    传统全量微调:
    ┌─────────────────────────────────────────────────────────┐
    │                                                         │
    │   W' = W + ΔW                                          │
    │                                                         │
    │   ┌───────────────────┐                                │
    │   │        ΔW         │  ← 更新整个矩阵                 │
    │   │   (d × d 参数)     │     如 4096 × 4096 = 16M 参数  │
    │   └───────────────────┘                                │
    │                                                         │
    └─────────────────────────────────────────────────────────┘
    
    
    LoRA 微调:
    ┌─────────────────────────────────────────────────────────┐
    │                                                         │
    │   W' = W + BA                                          │
    │                                                         │
    │   ┌─────┐   ┌─────────────────┐                        │
    │   │  B  │ × │        A        │  ← 低秩分解             │
    │   │(d×r)│   │      (r×d)      │                        │
    │   └─────┘   └─────────────────┘                        │
    │                                                         │
    │   参数量: d×r + r×d = 2×d×r                            │
    │   如 r=8: 2 × 4096 × 8 = 65K 参数 (仅 0.4%)             │
    │                                                         │
    └─────────────────────────────────────────────────────────┘
    
    
    数学表示
    ────────
    
    原始前向传播:  h = Wx
    LoRA 前向传播: h = Wx + BAx = (W + BA)x
    
    其中:
    - W: 原始权重矩阵 (冻结)
    - B: 低秩矩阵 (d × r), 初始化为 0
    - A: 低秩矩阵 (r × d), 随机初始化
    - r: 秩 (rank), 通常 4-64
    """)


def lora_parameters():
    """LoRA 参数"""
    print("\n" + "=" * 60)
    print("第二部分：LoRA 关键参数")
    print("=" * 60)

    print("""
    关键参数
    ───────
    
    1. rank (r) - 秩
       ┌────────────────────────────────────────────────────┐
       │  r = 4   │  参数极少，效果可能不足                   │
       │  r = 8   │  常用默认值，平衡效果和效率               │
       │  r = 16  │  较好效果                                │
       │  r = 32  │  接近全量微调效果                        │
       │  r = 64+ │  参数较多，可能过拟合                     │
       └────────────────────────────────────────────────────┘
    
    2. lora_alpha (α) - 缩放因子
       实际缩放 = α / r
       
       常用设置:
       - alpha = rank (缩放 = 1)
       - alpha = 2 * rank (缩放 = 2)
    
    3. target_modules - 目标模块
       应用 LoRA 的层，常见选择:
       - q_proj, v_proj (注意力层)
       - q_proj, k_proj, v_proj, o_proj (全部注意力)
       - 所有线性层 (效果最好，参数最多)
    
    4. lora_dropout - Dropout 比例
       防止过拟合，通常 0.05-0.1
    
    
    参数量计算
    ─────────
    
    假设模型有 L 层，每层有 N 个目标模块，维度为 d:
    
    LoRA 参数量 = L × N × 2 × d × r
    
    示例 (7B 模型, 32 层, 4 个模块, d=4096, r=8):
    参数量 = 32 × 4 × 2 × 4096 × 8 = 8.4M (仅 0.12%)
    """)


def lora_code_example():
    """LoRA 代码示例"""
    print("\n" + "=" * 60)
    print("第三部分：LoRA 代码实现")
    print("=" * 60)

    print("""
    使用 PEFT 库实现 LoRA
    ───────────────────
    """)

    code_example = """
    from peft import LoraConfig, get_peft_model, TaskType
    from transformers import AutoModelForCausalLM, AutoTokenizer

    # 1. 加载基础模型
    model_name = "meta-llama/Llama-2-7b-hf"
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # 2. 配置 LoRA
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=8,                          # 秩
        lora_alpha=16,                # 缩放因子
        lora_dropout=0.05,            # Dropout
        target_modules=[              # 目标模块
            "q_proj",
            "k_proj", 
            "v_proj",
            "o_proj",
        ],
        bias="none",                  # 是否训练 bias
    )

    # 3. 创建 PEFT 模型
    peft_model = get_peft_model(model, lora_config)

    # 4. 查看可训练参数
    peft_model.print_trainable_parameters()
    # 输出: trainable params: 4,194,304 || all params: 6,742,609,920 || 0.06%

    # 5. 训练 (使用 Trainer 或手动训练)
    from transformers import TrainingArguments, Trainer

    training_args = TrainingArguments(
        output_dir="./lora_output",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        learning_rate=1e-4,
        fp16=True,
        logging_steps=10,
        save_steps=100,
    )

    trainer = Trainer(
        model=peft_model,
        args=training_args,
        train_dataset=train_dataset,
    )

    trainer.train()

    # 6. 保存 LoRA 权重
    peft_model.save_pretrained("./lora_weights")

    # 7. 加载 LoRA 权重
    from peft import PeftModel

    base_model = AutoModelForCausalLM.from_pretrained(model_name)
    peft_model = PeftModel.from_pretrained(base_model, "./lora_weights")

    # 8. 合并权重 (可选)
    merged_model = peft_model.merge_and_unload()
    merged_model.save_pretrained("./merged_model")
    """

    print(code_example)


def lora_tips():
    """LoRA 使用技巧"""
    print("\n" + "=" * 60)
    print("第四部分：LoRA 使用技巧")
    print("=" * 60)

    print("""
    最佳实践
    ───────
    
    1. Rank 选择
       - 简单任务: r=4-8
       - 复杂任务: r=16-32
       - 不确定时: 从 r=8 开始尝试
    
    2. 目标模块选择
       - 最小: q_proj, v_proj
       - 推荐: q_proj, k_proj, v_proj, o_proj
       - 全面: 所有线性层
    
    3. 学习率
       - 通常比全量微调高: 1e-4 到 3e-4
       - 可以使用学习率调度器
    
    4. 训练轮数
       - 通常 1-3 轮即可
       - 监控验证集 loss，防止过拟合
    
    
    常见问题
    ───────
    
    Q: LoRA 效果不如全量微调怎么办？
    A: - 增加 rank
       - 增加目标模块
       - 增加训练数据
       - 调整学习率
    
    Q: 训练不稳定怎么办？
    A: - 降低学习率
       - 增加 warmup
       - 使用梯度裁剪
    
    Q: 多个 LoRA 如何组合？
    A: - 分别训练，推理时切换
       - 使用 LoRA 合并技术
    """)


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：参数计算
        计算 13B 模型使用 LoRA (r=16) 的参数量

        ✅ 参考答案：
        13B 模型通常有 40 层，每层 4 个注意力投影矩阵
        假设隐藏维度 d = 5120
        
        LoRA 参数量 = 层数 × 目标模块数 × 2 × d × r
                    = 40 × 4 × 2 × 5120 × 16
                    = 26,214,400 参数
                    ≈ 26M 参数
        
        占比 = 26M / 13B = 0.2%
    
    练习 2：配置优化
        设计一个 LoRA 配置，权衡效果和训练速度

        ✅ 参考答案：
        ```python
        from peft import LoraConfig
        
        # 平衡配置
        balanced_config = LoraConfig(
            r=8,                          # 中等秩
            lora_alpha=16,                # alpha = 2*r
            lora_dropout=0.05,            # 轻微 dropout
            target_modules=[
                "q_proj", "v_proj",       # 只训练 Q 和 V
            ],
            bias="none",
        )
        
        # 效果优先配置
        quality_config = LoraConfig(
            r=32,
            lora_alpha=64,
            lora_dropout=0.1,
            target_modules=[
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj",
            ],
        )
        
        # 速度优先配置
        speed_config = LoraConfig(
            r=4,
            lora_alpha=8,
            lora_dropout=0,
            target_modules=["q_proj", "v_proj"],
        )
        ```
    
    练习 3：实验对比
        比较不同 rank 值的训练效果

        ✅ 参考答案：
        ```python
        def compare_ranks(base_model, dataset, ranks=[4, 8, 16, 32]):
            results = {}
            
            for r in ranks:
                config = LoraConfig(r=r, lora_alpha=r*2, ...)
                model = get_peft_model(base_model, config)
                
                # 训练
                trainer = Trainer(model=model, ...)
                trainer.train()
                
                # 评估
                eval_result = trainer.evaluate()
                results[f"rank_{r}"] = {
                    "params": model.num_parameters(only_trainable=True),
                    "loss": eval_result["eval_loss"],
                    "accuracy": eval_result["eval_accuracy"],
                }
            
            return results
        
        # 典型结果模式:
        # rank_4:  params=2.1M, loss=2.1, accuracy=78%
        # rank_8:  params=4.2M, loss=1.8, accuracy=82%
        # rank_16: params=8.4M, loss=1.6, accuracy=85%
        # rank_32: params=16.8M, loss=1.5, accuracy=86%
        ```
    
    思考题：
    ────────
    1. 为什么 LoRA 选择在注意力层应用？

       ✅ 答：
       - 注意力层参数量最大，对输出影响最显著
       - 研究表明注意力权重的增量是低秩的
       - Q/K/V 投影直接影响模型的"关注"内容
       - 相比 FFN 层，注意力层更易于适应新任务

    2. LoRA 的局限性是什么？

       ✅ 答：
       - 对极复杂任务可能不如全量微调
       - 需要选择合适的 rank 和目标模块
       - 不同任务可能需要不同配置
       - 多个 LoRA 同时使用可能冲突
       - 对预训练阶段的知识注入效果有限
    """)


def main():
    print("🔧 LoRA 原理与实现")
    print("=" * 60)
    lora_principle()
    lora_parameters()
    lora_code_example()
    lora_tips()
    exercises()
    print("\n✅ 课程完成！下一步：05-qlora.py")


if __name__ == "__main__":
    main()
