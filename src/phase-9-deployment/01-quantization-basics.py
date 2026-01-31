"""
模型量化基础
============

学习目标：
    1. 理解模型量化的原理和必要性
    2. 掌握常见量化方法（FP16、INT8、INT4）
    3. 学习使用 GPTQ、AWQ、GGUF 进行模型量化
    4. 评估量化对模型性能的影响

核心概念：
    - 量化：将高精度数值转换为低精度表示
    - 精度损失：量化带来的模型能力下降
    - 显存优化：量化后模型占用更少资源

前置知识：
    - Phase 8 的微调知识
    - 了解模型参数和推理基础

环境要求：
    - pip install transformers torch bitsandbytes accelerate
    - pip install auto-gptq autoawq  # 量化工具
"""

import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


# ==================== 第一部分：量化基础概念 ====================


def introduction():
    """
    模型量化介绍

    量化是将模型参数从高精度（如FP32）转换为低精度（如INT8、INT4）的技术。
    这可以显著减少模型大小和推理时的显存需求。
    """
    print("=" * 60)
    print("第一部分：模型量化概述")
    print("=" * 60)

    overview = """
    📌 什么是模型量化？

    量化是一种模型压缩技术，通过降低参数的数值精度来减少模型大小。

    ┌─────────────────────────────────────────────────────────┐
    │                    量化对比示例                          │
    ├───────────────┬───────────────┬─────────────────────────┤
    │    精度       │    每参数字节  │    7B模型大小           │
    ├───────────────┼───────────────┼─────────────────────────┤
    │    FP32      │    4 bytes    │    28 GB               │
    │    FP16      │    2 bytes    │    14 GB               │
    │    INT8      │    1 byte     │    7 GB                │
    │    INT4      │    0.5 bytes  │    3.5 GB              │
    └───────────────┴───────────────┴─────────────────────────┘

    🎯 量化的好处：
    1. 减少显存占用 - 让大模型能在消费级 GPU 上运行
    2. 加速推理 - 低精度计算更快（依赖硬件支持）
    3. 降低成本 - 使用更便宜的硬件部署

    ⚠️ 量化的代价：
    1. 精度损失 - 模型能力可能略有下降
    2. 量化耗时 - 某些方法需要校准数据
    3. 兼容性 - 需要特定库支持
    """
    print(overview)


# ==================== 第二部分：BitsAndBytes 动态量化 ====================


def bitsandbytes_quantization():
    """
    使用 BitsAndBytes 进行动态量化

    BitsAndBytes 是最简单的量化方案，只需加载时指定参数即可。
    """
    print("\n" + "=" * 60)
    print("第二部分：BitsAndBytes 动态量化")
    print("=" * 60)

    print("""
    📌 BitsAndBytes 特点：
    - 加载时量化，无需预处理
    - 支持 INT8 和 INT4（NF4）
    - 与 HuggingFace 无缝集成
    """)

    # INT8 量化配置
    print("\n1. INT8 量化配置：")
    print("-" * 40)

    int8_config = """
# INT8 量化配置
quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,              # 启用 8bit 量化
    llm_int8_threshold=6.0,         # 离群值阈值
    llm_int8_has_fp16_weight=False  # 是否保留 FP16 权重
)

# 加载量化模型
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2-1.5B-Instruct",
    quantization_config=quantization_config,
    device_map="auto"
)
"""
    print(int8_config)

    # INT4 (NF4) 量化配置
    print("\n2. INT4 (NF4) 量化配置：")
    print("-" * 40)

    int4_config = """
# INT4 量化配置（推荐使用 NF4）
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,                       # 启用 4bit 量化
    bnb_4bit_quant_type="nf4",               # 量化类型: nf4 或 fp4
    bnb_4bit_compute_dtype=torch.bfloat16,   # 计算时使用的精度
    bnb_4bit_use_double_quant=True           # 双量化进一步压缩
)

model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2-1.5B-Instruct",
    quantization_config=quantization_config,
    device_map="auto"
)
"""
    print(int4_config)

    # 实际演示加载
    print("\n3. 实际加载 INT4 量化模型：")
    print("-" * 40)

    # 检查是否有 GPU
    if not torch.cuda.is_available():
        print("⚠️ 未检测到 GPU，跳过实际加载演示")
        print("在有 GPU 的环境中，可以运行以下代码：")
        return

    try:
        # 创建量化配置
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )

        # 加载小模型演示
        model_name = "Qwen/Qwen2-0.5B-Instruct"
        print(f"加载模型: {model_name}")

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name, quantization_config=quantization_config, device_map="auto"
        )

        # 显示显存使用
        print(f"✅ 模型加载成功")
        print(f"显存使用: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")

        # 测试推理
        messages = [{"role": "user", "content": "你好，用一句话介绍自己"}]
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = tokenizer(text, return_tensors="pt").to(model.device)

        outputs = model.generate(**inputs, max_new_tokens=50)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"模型响应: {response}")

    except Exception as e:
        print(f"⚠️ 加载失败: {e}")
        print("请确保已安装必要的依赖和足够的显存")


# ==================== 第三部分：GPTQ 离线量化 ====================


def gptq_quantization():
    """
    GPTQ 离线量化方法

    GPTQ 是一种高质量的离线量化方法，需要校准数据。
    """
    print("\n" + "=" * 60)
    print("第三部分：GPTQ 离线量化")
    print("=" * 60)

    print("""
    📌 GPTQ 特点：
    - 逐层量化 + 误差补偿
    - 需要校准数据集
    - 量化质量高
    - 量化后可直接加载，推理快
    """)

    # GPTQ 量化流程
    print("\n1. GPTQ 量化流程：")
    print("-" * 40)

    gptq_code = """
from transformers import AutoModelForCausalLM, AutoTokenizer, GPTQConfig

# 1. 准备校准数据
calibration_data = [
    "这是一段用于校准的文本...",
    "量化需要代表性的数据...",
    # 通常需要 128-512 条样本
]

# 2. 配置 GPTQ 参数
gptq_config = GPTQConfig(
    bits=4,                    # 量化位数: 4 或 8
    group_size=128,            # 分组大小，越小精度越高
    dataset=calibration_data,  # 校准数据
    desc_act=True,             # 激活值降序处理
)

# 3. 加载并量化模型
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2-7B-Instruct",
    quantization_config=gptq_config,
    device_map="auto"
)

# 4. 保存量化后的模型
model.save_pretrained("./qwen2-7b-gptq-4bit")
tokenizer.save_pretrained("./qwen2-7b-gptq-4bit")
"""
    print(gptq_code)

    # 加载 GPTQ 量化模型
    print("\n2. 加载已量化的 GPTQ 模型：")
    print("-" * 40)

    load_gptq = """
from transformers import AutoModelForCausalLM, AutoTokenizer

# 直接加载已量化的模型
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2-7B-Instruct-GPTQ-Int4",  # HuggingFace 上的量化版本
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(
    "Qwen/Qwen2-7B-Instruct-GPTQ-Int4"
)
"""
    print(load_gptq)


# ==================== 第四部分：AWQ 量化 ====================


def awq_quantization():
    """
    AWQ（Activation-aware Weight Quantization）量化

    AWQ 通过保护重要权重来减少量化误差。
    """
    print("\n" + "=" * 60)
    print("第四部分：AWQ 量化")
    print("=" * 60)

    print("""
    📌 AWQ vs GPTQ：
    ┌────────────┬──────────────────┬──────────────────┐
    │    特性    │       AWQ        │       GPTQ       │
    ├────────────┼──────────────────┼──────────────────┤
    │   原理     │ 保护重要权重     │ 逐层量化+补偿    │
    │   精度     │ 略好             │ 良好             │
    │   速度     │ 稍快             │ 良好             │
    │   推理     │ 需要 AutoAWQ     │ 需要 AutoGPTQ    │
    └────────────┴──────────────────┴──────────────────┘
    """)

    # AWQ 量化流程
    print("\n1. AWQ 量化流程：")
    print("-" * 40)

    awq_code = """
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer

# 1. 加载原始模型
model_path = "Qwen/Qwen2-7B-Instruct"
quant_path = "./qwen2-7b-awq-4bit"

model = AutoAWQForCausalLM.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)

# 2. 配置量化参数
quant_config = {
    "w_bit": 4,              # 权重量化位数
    "q_group_size": 128,     # 量化分组大小
    "zero_point": True,      # 零点量化
    "version": "GEMM"        # 计算后端版本
}

# 3. 执行量化
model.quantize(
    tokenizer,
    quant_config=quant_config,
    calib_data="pileval"     # 使用内置校准数据集
)

# 4. 保存量化模型
model.save_quantized(quant_path)
tokenizer.save_pretrained(quant_path)
"""
    print(awq_code)

    # 加载 AWQ 模型
    print("\n2. 加载 AWQ 量化模型：")
    print("-" * 40)

    load_awq = """
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer

# 加载量化后的模型
model = AutoAWQForCausalLM.from_quantized(
    "Qwen/Qwen2-7B-Instruct-AWQ",
    fuse_layers=True  # 融合层以加速推理
)
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-7B-Instruct-AWQ")
"""
    print(load_awq)


# ==================== 第五部分：GGUF 格式（llama.cpp） ====================


def gguf_quantization():
    """
    GGUF 格式量化（用于 llama.cpp）

    GGUF 是 llama.cpp 使用的量化格式，支持 CPU 推理。
    """
    print("\n" + "=" * 60)
    print("第五部分：GGUF 格式量化")
    print("=" * 60)

    print("""
    📌 GGUF 特点：
    - llama.cpp 原生格式
    - 支持 CPU 推理
    - 多种量化级别可选
    - 适合边缘设备部署
    """)

    # 量化级别说明
    print("\n1. GGUF 量化级别：")
    print("-" * 40)

    print("""
    ┌─────────────┬──────────────────┬──────────────────┐
    │   量化级别   │    模型大小比例   │    精度损失      │
    ├─────────────┼──────────────────┼──────────────────┤
    │    Q2_K     │    ~28%          │    较大          │
    │    Q3_K_M   │    ~35%          │    中等          │
    │    Q4_K_M   │    ~45%          │    小            │
    │    Q5_K_M   │    ~55%          │    很小          │
    │    Q6_K     │    ~65%          │    极小          │
    │    Q8_0     │    ~85%          │    几乎无        │
    └─────────────┴──────────────────┴──────────────────┘

    推荐选择：
    - 质量优先：Q5_K_M 或 Q6_K
    - 平衡方案：Q4_K_M（最常用）
    - 极限压缩：Q3_K_M
    """)

    # 转换流程
    print("\n2. 转换为 GGUF 格式：")
    print("-" * 40)

    gguf_code = """
# 使用 llama.cpp 的转换脚本

# 1. 克隆 llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp

# 2. 安装依赖
pip install -r requirements.txt

# 3. 转换 HuggingFace 模型为 GGUF
python convert_hf_to_gguf.py \\
    /path/to/Qwen2-7B-Instruct \\
    --outfile qwen2-7b.gguf \\
    --outtype f16

# 4. 量化
./llama-quantize \\
    qwen2-7b.gguf \\
    qwen2-7b-q4_k_m.gguf \\
    q4_k_m
"""
    print(gguf_code)

    # 使用 GGUF 模型
    print("\n3. 使用 GGUF 模型（通过 llama-cpp-python）：")
    print("-" * 40)

    use_gguf = """
from llama_cpp import Llama

# 加载 GGUF 模型
llm = Llama(
    model_path="./qwen2-7b-q4_k_m.gguf",
    n_ctx=4096,           # 上下文长度
    n_gpu_layers=35,      # GPU 层数（0 表示纯 CPU）
    n_threads=8           # CPU 线程数
)

# 推理
output = llm(
    "请介绍一下量化技术：",
    max_tokens=256,
    temperature=0.7
)

print(output["choices"][0]["text"])
"""
    print(use_gguf)


# ==================== 第六部分：量化评估与对比 ====================


def quantization_evaluation():
    """
    量化模型评估和对比
    """
    print("\n" + "=" * 60)
    print("第六部分：量化评估与对比")
    print("=" * 60)

    # 评估维度
    print("\n1. 评估维度：")
    print("-" * 40)

    print("""
    量化模型评估需要从多个维度进行：

    📊 性能评估
    - 困惑度（Perplexity）：越低越好
    - 基准测试：MMLU、C-Eval 等
    - 任务准确率：特定任务的表现

    ⚡ 效率评估
    - 显存占用
    - 推理速度（tokens/s）
    - 首 Token 延迟（TTFT）

    💡 实用性评估
    - 生成质量主观评估
    - A/B 测试对比
    """)

    # 评估代码
    print("\n2. 困惑度评估示例：")
    print("-" * 40)

    eval_code = """
import torch
from tqdm import tqdm
from datasets import load_dataset

def evaluate_perplexity(model, tokenizer, dataset, max_samples=100):
    '''评估模型困惑度'''
    model.eval()
    total_loss = 0
    total_tokens = 0

    for sample in tqdm(dataset[:max_samples]):
        inputs = tokenizer(
            sample["text"],
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(model.device)

        with torch.no_grad():
            outputs = model(**inputs, labels=inputs["input_ids"])
            loss = outputs.loss

        total_loss += loss.item() * inputs["input_ids"].size(1)
        total_tokens += inputs["input_ids"].size(1)

    perplexity = torch.exp(torch.tensor(total_loss / total_tokens))
    return perplexity.item()

# 使用
dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")
ppl = evaluate_perplexity(model, tokenizer, dataset)
print(f"困惑度: {ppl:.2f}")
"""
    print(eval_code)

    # 量化方法对比
    print("\n3. 量化方法选择指南：")
    print("-" * 40)

    print("""
    ┌────────────────────────────────────────────────────────────┐
    │                    量化方法选择决策树                       │
    └────────────────────────────────────────────────────────────┘

                        精度要求高？
                            │
              ┌─────是──────┴──────否─────┐
              ↓                           ↓
           FP16/INT8                   INT4量化
              │                           │
              │                 ┌─────────┴─────────┐
              │                 ↓                   ↓
              │              GPU部署             CPU部署
              │              AWQ/GPTQ              GGUF
              ↓                 ↓                   ↓
         显存充足时          显存受限时          边缘设备

    具体推荐：
    - 服务器 GPU 充足 → FP16 或 INT8（简单快速）
    - 显存受限 → AWQ/GPTQ 4bit（质量与效率平衡）
    - CPU/边缘设备 → GGUF Q4_K_M
    - 需要快速部署 → BitsAndBytes 动态量化
    """)


# ==================== 第七部分：练习与思考 ====================


def exercises():
    """练习与思考"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    exercises_text = """
    📝 练习 1：对比不同量化方法的显存占用
    -------------------------
    使用同一个模型，分别用 FP16、INT8、INT4 加载，
    比较不同精度下的显存占用和推理速度。

    参考答案：
    ```python
    import torch
    from transformers import AutoModelForCausalLM, BitsAndBytesConfig

    model_name = "Qwen/Qwen2-1.5B-Instruct"
    results = []

    # FP16
    torch.cuda.empty_cache()
    model_fp16 = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.float16, device_map="auto"
    )
    results.append(("FP16", torch.cuda.memory_allocated() / 1024**3))
    del model_fp16

    # INT8
    torch.cuda.empty_cache()
    model_int8 = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=BitsAndBytesConfig(load_in_8bit=True),
        device_map="auto"
    )
    results.append(("INT8", torch.cuda.memory_allocated() / 1024**3))
    del model_int8

    # INT4
    torch.cuda.empty_cache()
    model_int4 = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=BitsAndBytesConfig(load_in_4bit=True),
        device_map="auto"
    )
    results.append(("INT4", torch.cuda.memory_allocated() / 1024**3))

    for name, mem in results:
        print(f"{name}: {mem:.2f} GB")
    ```

    📝 练习 2：评估量化对生成质量的影响
    -------------------------
    准备一组测试问题，分别用原始模型和量化模型生成回答，
    人工评估生成质量的差异。

    思考题：
    - Q: 什么情况下量化损失可以接受？
    - A: 当任务不需要极高精度时（如闲聊、简单问答），
         或者资源限制必须使用量化时。对于需要精确计算
         或专业领域的任务，建议谨慎评估量化影响。

    - Q: 如何在量化后恢复部分精度损失？
    - A: 可以考虑：
         1. 使用更高的量化位数（如 Q5 代替 Q4）
         2. 使用 QLoRA 进行量化后微调
         3. 选择更好的量化方法（如 AWQ 通常比 GPTQ 略好）
    """
    print(exercises_text)


# ==================== 主函数 ====================


def main():
    """主函数 - 按顺序执行所有部分"""
    introduction()
    bitsandbytes_quantization()
    gptq_quantization()
    awq_quantization()
    gguf_quantization()
    quantization_evaluation()
    exercises()

    print("\n" + "=" * 60)
    print("课程完成！下一步：02-vllm-deployment.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
