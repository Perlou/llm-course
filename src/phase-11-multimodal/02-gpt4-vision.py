"""
GPT-4V 使用
==========

学习目标：
    1. 掌握 GPT-4V/GPT-4o 的 API 使用
    2. 了解图像输入的格式和限制
    3. 实现多图对话和高级用法

核心概念：
    - base64 编码：图像传输格式
    - 图像 URL：远程图像引用
    - 多图输入：同时分析多张图片

环境要求：
    - pip install openai pillow
    - 需要 OpenAI API Key

⚠️ 成本提醒：GPT-4o 视觉调用按图像大小和 token 计费
"""

import os
import base64
from typing import List
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：基础使用 ====================


def basic_usage():
    """基础使用"""
    print("=" * 60)
    print("第一部分：GPT-4V 基础使用")
    print("=" * 60)

    code = '''
from openai import OpenAI
import base64

client = OpenAI()

# 方法1：使用 base64 编码图像
def encode_image(image_path: str) -> str:
    """将图像编码为 base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

image_base64 = encode_image("example.jpg")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "这张图片里有什么？"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ]
        }
    ],
    max_tokens=500
)

print(response.choices[0].message.content)

# 方法2：使用图像 URL
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "描述这张图片"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://example.com/image.jpg"
                    }
                }
            ]
        }
    ]
)
'''
    print(code)


# ==================== 第二部分：图像质量设置 ====================


def image_quality():
    """图像质量设置"""
    print("\n" + "=" * 60)
    print("第二部分：图像质量设置")
    print("=" * 60)

    print("""
    📌 detail 参数：
    ┌───────────┬────────────────────────────────────────┐
    │ low       │ 低分辨率，512×512，固定 85 tokens     │
    │ high      │ 高分辨率，细节模式，更多 tokens       │
    │ auto      │ 自动选择（默认）                      │
    └───────────┴────────────────────────────────────────┘
    """)

    code = """
# 低分辨率模式 - 快速、低成本
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "这是什么？"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}",
                        "detail": "low"  # 低分辨率
                    }
                }
            ]
        }
    ]
)

# 高分辨率模式 - 适合细节分析
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "阅读图片中的文字"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}",
                        "detail": "high"  # 高分辨率
                    }
                }
            ]
        }
    ]
)
"""
    print(code)


# ==================== 第三部分：多图输入 ====================


def multiple_images():
    """多图输入"""
    print("\n" + "=" * 60)
    print("第三部分：多图输入")
    print("=" * 60)

    code = '''
def compare_images(image_paths: list, question: str):
    """比较多张图片"""
    content = [{"type": "text", "text": question}]

    for path in image_paths:
        image_base64 = encode_image(path)
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_base64}"
            }
        })

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": content}],
        max_tokens=1000
    )

    return response.choices[0].message.content

# 使用示例
result = compare_images(
    ["before.jpg", "after.jpg"],
    "比较这两张图片的区别"
)
print(result)
'''
    print(code)


# ==================== 第四部分：实用场景 ====================


def practical_examples():
    """实用场景"""
    print("\n" + "=" * 60)
    print("第四部分：实用场景示例")
    print("=" * 60)

    print("""
    📌 场景1：图片 OCR
    """)

    ocr_code = '''
def image_ocr(image_path: str) -> str:
    """从图片中提取文字"""
    image_base64 = encode_image(image_path)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "请识别并提取这张图片中的所有文字，保持原有格式。"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ],
        max_tokens=2000
    )

    return response.choices[0].message.content
'''
    print(ocr_code)

    print("""
    📌 场景2：图表分析
    """)

    chart_code = '''
def analyze_chart(image_path: str) -> str:
    """分析图表内容"""
    image_base64 = encode_image(image_path)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """分析这张图表，请提供：
1. 图表类型
2. 主要数据点
3. 趋势分析
4. 关键洞察"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ],
        max_tokens=1500
    )

    return response.choices[0].message.content
'''
    print(chart_code)


# ==================== 第五部分：最佳实践 ====================


def best_practices():
    """最佳实践"""
    print("\n" + "=" * 60)
    print("第五部分：最佳实践")
    print("=" * 60)

    print("""
    📌 图像优化：
    ┌─────────────────────────────────────────────────────────┐
    │ 1. 压缩大图以减少成本                                  │
    │ 2. 简单任务用 detail="low"                             │
    │ 3. OCR/细节任务用 detail="high"                        │
    └─────────────────────────────────────────────────────────┘

    📌 Prompt 技巧：
    ┌─────────────────────────────────────────────────────────┐
    │ 1. 明确指出要分析图片的哪些方面                        │
    │ 2. 要求结构化输出（JSON、列表等）                      │
    │ 3. 多图时明确指出"第一张"、"第二张"                   │
    └─────────────────────────────────────────────────────────┘

    📌 成本控制：
    ┌───────────────────────────────────────────────────────┐
    │ • 预处理：压缩图片到合理分辨率                        │
    │ • 批处理：合并相关图片请求                            │
    │ • 缓存：缓存重复图片的分析结果                        │
    └───────────────────────────────────────────────────────┘

    📌 GPT-4o Token 计算：
    - low: 固定 85 tokens
    - high: 基础 85 + 每个 512×512 块 170 tokens
    """)


# ==================== 第六部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现一个图片描述函数
    练习 2：实现一个多图比较分析

    思考题：什么时候用 low，什么时候用 high？
    答案：
    - low: 简单识别、快速分类、低成本场景
    - high: OCR、图表分析、细节识别、文档理解
    """)


def main():
    basic_usage()
    image_quality()
    multiple_images()
    practical_examples()
    best_practices()
    exercises()
    print("\n课程完成！下一步：03-image-understanding.py")


if __name__ == "__main__":
    main()
