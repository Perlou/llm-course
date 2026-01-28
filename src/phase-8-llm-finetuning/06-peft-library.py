"""
PEFT 库使用
===========

学习目标：
    1. 掌握 PEFT 库的使用
    2. 了解多种 PEFT 方法
    3. 学会保存和加载 PEFT 模型

核心概念：
    - PEFT (Parameter-Efficient Fine-Tuning)
    - Adapters
    - Prefix Tuning

环境要求：
    - pip install peft transformers
"""

import os
from dotenv import load_dotenv

load_dotenv()


def peft_overview():
    """PEFT 概述"""
    print("=" * 60)
    print("第一部分：PEFT 库概述")
    print("=" * 60)

    print("""
    PEFT: Parameter-Efficient Fine-Tuning
    ─────────────────────────────────────
    
    HuggingFace 开发的统一 PEFT 框架，支持多种方法。
    
    
    支持的方法
    ─────────
    
    ┌─────────────────────────────────────────────────────────┐
    │                    PEFT 方法                             │
    ├─────────────────────────────────────────────────────────┤
    │                                                         │
    │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
    │   │  LoRA   │  │ AdaLoRA │  │  IA³    │  │Prefix   │   │
    │   └─────────┘  └─────────┘  └─────────┘  │Tuning   │   │
    │                                          └─────────┘   │
    │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
    │   │ Prompt  │  │  P-     │  │ (IA)³   │  │LoHa/    │   │
    │   │ Tuning  │  │ Tuning  │  │         │  │LoKR     │   │
    │   └─────────┘  └─────────┘  └─────────┘  └─────────┘   │
    │                                                         │
    └─────────────────────────────────────────────────────────┘
    
    
    方法对比
    ───────
    
    ┌─────────────┬────────────┬────────────┬────────────┐
    │    方法     │  参数效率   │    效果    │   复杂度   │
    ├─────────────┼────────────┼────────────┼────────────┤
    │   LoRA      │   高       │    好      │    低      │
    │   AdaLoRA   │   更高     │    好      │    中      │
    │   IA³       │   最高     │    一般    │    低      │
    │   Prefix    │   高       │    一般    │    中      │
    │   Prompt    │   最高     │    一般    │    低      │
    └─────────────┴────────────┴────────────┴────────────┘
    """)


def lora_adapter():
    """LoRA Adapter"""
    print("\n" + "=" * 60)
    print("第二部分：LoRA Adapter")
    print("=" * 60)

    code_example = """
    from peft import LoraConfig, get_peft_model, TaskType
    from transformers import AutoModelForCausalLM

    # 加载模型
    model = AutoModelForCausalLM.from_pretrained("model_name")

    # LoRA 配置
    config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=8,
        lora_alpha=16,
        lora_dropout=0.1,
        target_modules=["q_proj", "v_proj"],
    )

    # 应用 LoRA
    peft_model = get_peft_model(model, config)
    """

    print("📌 LoRA 配置示例：")
    print(code_example)


def other_methods():
    """其他 PEFT 方法"""
    print("\n" + "=" * 60)
    print("第三部分：其他 PEFT 方法")
    print("=" * 60)

    print("""
    1. Prefix Tuning
    ────────────────
    在每层添加可训练的前缀向量
    """)

    prefix_code = """
    from peft import PrefixTuningConfig

    config = PrefixTuningConfig(
        task_type="CAUSAL_LM",
        num_virtual_tokens=20,  # 前缀长度
        prefix_projection=True,
    )
    """
    print(prefix_code)

    print("""
    2. Prompt Tuning
    ────────────────
    只在输入嵌入层添加可训练的软提示
    """)

    prompt_code = """
    from peft import PromptTuningConfig

    config = PromptTuningConfig(
        task_type="CAUSAL_LM",
        num_virtual_tokens=8,
        prompt_tuning_init="TEXT",      # 初始化方式
        prompt_tuning_init_text="分类这段文本的情感：",
    )
    """
    print(prompt_code)

    print("""
    3. IA³ (Infused Adapter by Inhibiting and Amplifying)
    ──────────────────────────────────────────────────────
    通过学习缩放向量调整激活值
    """)

    ia3_code = """
    from peft import IA3Config

    config = IA3Config(
        task_type="CAUSAL_LM",
        target_modules=["k_proj", "v_proj", "down_proj"],
        feedforward_modules=["down_proj"],
    )
    """
    print(ia3_code)


def model_management():
    """模型管理"""
    print("\n" + "=" * 60)
    print("第四部分：模型保存与加载")
    print("=" * 60)

    print("""
    保存和加载 PEFT 模型
    ───────────────────
    """)

    code_example = """
    from peft import PeftModel, PeftConfig
    from transformers import AutoModelForCausalLM

    # ============ 保存 ============

    # 1. 只保存 adapter 权重 (推荐)
    peft_model.save_pretrained("./adapter_weights")
    # 保存的文件:
    # - adapter_config.json
    # - adapter_model.safetensors

    # 2. 合并后保存完整模型
    merged_model = peft_model.merge_and_unload()
    merged_model.save_pretrained("./merged_model")


    # ============ 加载 ============

    # 1. 加载 adapter
    base_model = AutoModelForCausalLM.from_pretrained("base_model_name")
    peft_model = PeftModel.from_pretrained(base_model, "./adapter_weights")

    # 2. 查看 adapter 配置
    config = PeftConfig.from_pretrained("./adapter_weights")
    print(config)

    # 3. 禁用 adapter (使用原始模型)
    with peft_model.disable_adapter():
        output = peft_model.generate(...)

    # 4. 多 adapter 管理
    peft_model.load_adapter("./adapter2", adapter_name="task2")
    peft_model.set_adapter("task2")  # 切换 adapter
    """

    print(code_example)


def multi_adapter():
    """多 Adapter"""
    print("\n" + "=" * 60)
    print("第五部分：多 Adapter 管理")
    print("=" * 60)

    print("""
    多任务 Adapter
    ─────────────
    
    ┌─────────────────────────────────────────────────────────┐
    │                   Base Model (冻结)                      │
    │                                                         │
    │   ┌─────────┐   ┌─────────┐   ┌─────────┐              │
    │   │Adapter A│   │Adapter B│   │Adapter C│              │
    │   │ 翻译    │   │ 摘要    │   │ 问答    │              │
    │   └─────────┘   └─────────┘   └─────────┘              │
    │        │             │             │                    │
    │        └─────────────┴─────────────┘                    │
    │                      │                                  │
    │              推理时动态切换                               │
    └─────────────────────────────────────────────────────────┘
    """)

    multi_code = """
    # 训练多个 adapter
    model.add_adapter(lora_config, adapter_name="translate")
    model.add_adapter(lora_config, adapter_name="summarize")

    # 切换 adapter
    model.set_adapter("translate")
    output1 = model.generate(...)

    model.set_adapter("summarize")
    output2 = model.generate(...)

    # 合并多个 adapter
    model.add_weighted_adapter(
        adapters=["translate", "summarize"],
        weights=[0.5, 0.5],
        adapter_name="combined",
    )
    """
    print(multi_code)


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：对比实验
        比较 LoRA, Prefix Tuning, IA³ 效果
    
    练习 2：多 Adapter
        为不同任务训练多个 adapter
    
    练习 3：Adapter 合并
        实验不同权重的 adapter 合并
    
    思考题：
    ────────
    1. 如何选择适合任务的 PEFT 方法？
    2. 多 Adapter 的应用场景？
    """)


def main():
    print("📦 PEFT 库使用")
    print("=" * 60)
    peft_overview()
    lora_adapter()
    other_methods()
    model_management()
    multi_adapter()
    exercises()
    print("\n✅ 课程完成！下一步：07-supervised-finetuning.py")


if __name__ == "__main__":
    main()
