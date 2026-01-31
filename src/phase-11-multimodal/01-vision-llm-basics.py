"""
视觉 LLM 基础
============

学习目标：
    1. 理解多模态 LLM 的概念和发展
    2. 掌握视觉语言模型的核心架构
    3. 了解主流多模态模型

核心概念：
    - 模态 (Modality)：信息的不同形式
    - Vision Encoder：视觉编码器
    - 模态对齐：将视觉特征映射到语言空间

环境要求：
    - pip install transformers torch pillow
"""


# ==================== 第一部分：什么是多模态 ====================


def introduction():
    """什么是多模态"""
    print("=" * 60)
    print("第一部分：什么是多模态")
    print("=" * 60)

    print("""
    📌 模态 (Modality) 的类型：
    ┌─────────────────────────────────────────────────────────┐
    │  📝 文本 (Text)      - 文章、对话、代码               │
    │  🖼️  图像 (Image)     - 照片、图表、截图               │
    │  🎵 音频 (Audio)     - 语音、音乐、环境音             │
    │  🎬 视频 (Video)     - 影片、动画、实时流             │
    │  📊 结构化数据       - 表格、图谱、数据库             │
    └─────────────────────────────────────────────────────────┘

    📌 单模态 vs 多模态：
    ┌────────────────────────────────────────────────────────┐
    │ 单模态 LLM:                                           │
    │   文本 → LLM → 文本                                   │
    │                                                        │
    │ 多模态 LLM:                                           │
    │   文本 ──┐                                            │
    │   图像 ──┼──→ MLLM → 文本/图像...                    │
    │   音频 ──┘                                            │
    └────────────────────────────────────────────────────────┘

    📌 为什么需要多模态？
    - 信息完整性：直接理解图像、视频内容
    - 交互自然性：支持语音、图片等自然交互
    - 任务覆盖：图文问答、视频理解等
    """)


# ==================== 第二部分：核心架构 ====================


def architecture():
    """核心架构"""
    print("\n" + "=" * 60)
    print("第二部分：多模态 LLM 核心架构")
    print("=" * 60)

    print("""
    📌 通用架构：
    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │  输入    │    │ 模态编码 │    │  对齐/   │    │   LLM    │
    │  模态    │───►│ Encoders │───►│  融合层  │───►│ Backbone │
    └──────────┘    └──────────┘    └──────────┘    └──────────┘

    📌 视觉编码器 (Vision Encoder)：
    ┌─────────────┬────────────┬───────────────────┐
    │   编码器    │   来源     │       特点        │
    ├─────────────┼────────────┼───────────────────┤
    │ ViT         │ Google     │ 标准 Transformer  │
    │ CLIP-ViT    │ OpenAI     │ 图文对齐预训练    │
    │ SigLIP      │ Google     │ Sigmoid 损失改进  │
    │ DINOv2      │ Meta       │ 自监督强特征      │
    └─────────────┴────────────┴───────────────────┘

    📌 模态对齐方法：
    1. 线性投影 (LLaVA) - 简单高效
    2. MLP 投影器 (LLaVA-1.5) - 两层 MLP
    3. Q-Former (BLIP-2) - 压缩视觉 token
    4. Cross-Attention (Flamingo) - 深度融合
    """)


# ==================== 第三部分：主流模型介绍 ====================


def models_overview():
    """主流模型介绍"""
    print("\n" + "=" * 60)
    print("第三部分：主流多模态模型")
    print("=" * 60)

    print("""
    📌 闭源模型：
    ┌─────────────┬───────────────────────────────────────┐
    │ GPT-4o      │ OpenAI，原生多模态，实时语音交互     │
    │ Claude 3.5  │ Anthropic，强文档/图表理解           │
    │ Gemini 2.0  │ Google，全模态，100万+ tokens        │
    └─────────────┴───────────────────────────────────────┘

    📌 开源模型：
    ┌─────────────┬───────────────────────────────────────┐
    │ LLaVA       │ 视觉指令微调，简单高效               │
    │ Qwen2-VL    │ 阿里，动态分辨率，中文优化           │
    │ InternVL2   │ 书生，强视觉编码器，多规模           │
    └─────────────┴───────────────────────────────────────┘

    📌 能力对比 (2024.12)：
    ┌───────────┬───────┬───────┬───────┬───────┐
    │   模型    │ 图像QA │  OCR  │ 图表  │ 视频  │
    ├───────────┼───────┼───────┼───────┼───────┤
    │ GPT-4o    │ ★★★★★│ ★★★★★│ ★★★★★│ ★★★☆ │
    │ Claude3.5 │ ★★★★★│ ★★★★★│ ★★★★★│ ★★☆  │
    │ Qwen2-VL  │ ★★★★☆│ ★★★★★│ ★★★★☆│ ★★★★☆│
    └───────────┴───────┴───────┴───────┴───────┘
    """)


# ==================== 第四部分：代码示例 ====================


def code_example():
    """代码示例"""
    print("\n" + "=" * 60)
    print("第四部分：代码示例")
    print("=" * 60)

    code = """
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from PIL import Image
import torch

# 加载模型
model_name = "Qwen/Qwen2-VL-7B-Instruct"
model = Qwen2VLForConditionalGeneration.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
processor = AutoProcessor.from_pretrained(model_name)

# 准备输入
image = Image.open("example.jpg")
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": "描述这张图片的内容"}
        ]
    }
]

# 处理输入
text = processor.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True
)
inputs = processor(
    text=[text],
    images=[image],
    return_tensors="pt"
).to(model.device)

# 生成输出
generated_ids = model.generate(**inputs, max_new_tokens=512)
output = processor.batch_decode(
    generated_ids[:, inputs.input_ids.shape[1]:],
    skip_special_tokens=True
)[0]

print(output)
"""
    print(code)


# ==================== 第五部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：使用 Qwen2-VL 或 LLaVA 加载一个多模态模型
    练习 2：输入一张图片，让模型描述图片内容

    思考题：为什么视觉编码器通常是预训练冻结的？
    答案：视觉编码器（如 CLIP-ViT）已通过大规模数据预训练，
          具有很强的图像表示能力。冻结它可以：
          1. 减少训练成本
          2. 保留已学到的视觉知识
          3. 只需训练对齐层和 LLM
    """)


def main():
    introduction()
    architecture()
    models_overview()
    code_example()
    exercises()
    print("\n课程完成！下一步：02-gpt4-vision.py")


if __name__ == "__main__":
    main()
