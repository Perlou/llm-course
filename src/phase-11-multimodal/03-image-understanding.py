"""
图像理解
========

学习目标：
    1. 掌握图像理解的常见任务类型
    2. 实现图像描述、问答、分类等功能
    3. 处理复杂的图像分析场景

核心概念：
    - 图像描述 (Image Captioning)
    - 视觉问答 (VQA)
    - 物体识别与定位

环境要求：
    - pip install google-generativeai pillow

📌 Gemini 迁移说明：
    本文件展示图像理解任务的核心概念。
    示例代码使用OpenAI API演示，Gemini等价实现参考02-gpt4-vision.py顶部说明。
"""

import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：图像理解任务类型 ====================


def task_types():
    """图像理解任务类型"""
    print("=" * 60)
    print("第一部分：图像理解任务类型")
    print("=" * 60)

    print("""
    📌 常见任务：
    ┌────────────────┬───────────────────────────────────────┐
    │ 图像描述       │ 生成图像的自然语言描述               │
    │ 视觉问答 (VQA) │ 根据图像回答问题                     │
    │ 物体识别       │ 识别图像中的物体                     │
    │ 场景理解       │ 理解图像的整体场景和上下文           │
    │ 文字识别 (OCR) │ 提取图像中的文字                     │
    │ 图表分析       │ 理解和解释图表数据                   │
    │ 空间关系       │ 理解物体间的位置关系                 │
    └────────────────┴───────────────────────────────────────┘

    📌 任务难度：
    简单：图像分类、简单描述
    中等：VQA、物体计数、OCR
    困难：复杂推理、多图对比、空间关系
    """)


# ==================== 第二部分：图像描述 ====================


def image_captioning():
    """图像描述"""
    print("\n" + "=" * 60)
    print("第二部分：图像描述")
    print("=" * 60)

    code = '''
from openai import OpenAI
import base64

client = OpenAI()

def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def describe_image(image_path: str, style: str = "detailed") -> str:
    """生成图像描述"""
    image_base64 = encode_image(image_path)

    prompts = {
        "brief": "用一句话描述这张图片。",
        "detailed": "请详细描述这张图片的内容，包括主要元素、场景和氛围。",
        "creative": "用富有想象力的语言描述这张图片，像讲故事一样。",
        "technical": "从技术角度分析这张图片的构图、光线和色彩。"
    }

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompts.get(style, prompts["detailed"])},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                    }
                ]
            }
        ],
        max_tokens=500
    )

    return response.choices[0].message.content

# 使用示例
# desc = describe_image("photo.jpg", style="detailed")
'''
    print(code)


# ==================== 第三部分：视觉问答 ====================


def visual_qa():
    """视觉问答"""
    print("\n" + "=" * 60)
    print("第三部分：视觉问答 (VQA)")
    print("=" * 60)

    code = '''
def visual_question_answer(image_path: str, question: str) -> str:
    """视觉问答"""
    image_base64 = encode_image(image_path)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                    }
                ]
            }
        ],
        max_tokens=500
    )

    return response.choices[0].message.content

# 常见问题类型示例
questions = [
    "图片中有多少人？",           # 计数
    "图片中的人在做什么？",       # 动作识别
    "这是在哪里拍摄的？",         # 场景理解
    "图片中最突出的颜色是什么？", # 视觉属性
    "这张图片给人什么感觉？",     # 情感分析
]
'''
    print(code)


# ==================== 第四部分：物体识别与分析 ====================


def object_analysis():
    """物体识别与分析"""
    print("\n" + "=" * 60)
    print("第四部分：物体识别与分析")
    print("=" * 60)

    code = '''
def identify_objects(image_path: str) -> dict:
    """识别图像中的物体"""
    image_base64 = encode_image(image_path)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """分析图片中的物体，返回 JSON 格式：
{
    "objects": [
        {"name": "物体名称", "count": 数量, "position": "位置描述"}
    ],
    "main_subject": "主要主题",
    "scene": "场景类型"
}"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                    }
                ]
            }
        ],
        max_tokens=800
    )

    import json
    return json.loads(response.choices[0].message.content)

def analyze_spatial_relations(image_path: str) -> str:
    """分析空间关系"""
    image_base64 = encode_image(image_path)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "描述图片中各元素之间的空间位置关系（如：上下、左右、前后等）。"
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                    }
                ]
            }
        ]
    )

    return response.choices[0].message.content
'''
    print(code)


# ==================== 第五部分：多图分析 ====================


def multi_image_analysis():
    """多图分析"""
    print("\n" + "=" * 60)
    print("第五部分：多图分析")
    print("=" * 60)

    code = '''
def compare_images(images: list, aspect: str = "general") -> str:
    """比较多张图片"""
    content = []

    prompts = {
        "general": "比较这些图片的异同点。",
        "style": "比较这些图片的风格差异。",
        "content": "描述这些图片内容上的关联和区别。",
        "timeline": "如果这些图片是按时间顺序的，描述发生了什么变化。"
    }

    content.append({"type": "text", "text": prompts.get(aspect, prompts["general"])})

    for i, img_path in enumerate(images):
        image_base64 = encode_image(img_path)
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
        })

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": content}],
        max_tokens=1000
    )

    return response.choices[0].message.content

# 使用示例：对比产品照片
# result = compare_images(["product_v1.jpg", "product_v2.jpg"], aspect="content")
'''
    print(code)


# ==================== 第六部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现一个图片内容审核函数
    练习 2：实现商品图片自动分类

    思考题：多模态 LLM 在图像理解上有什么局限？
    答案：
    1. 精确计数困难（人多时容易出错）
    2. 空间定位不够精确（无法输出坐标）
    3. 小物体识别能力有限
    4. 可能产生视觉幻觉
    """)


def main():
    task_types()
    image_captioning()
    visual_qa()
    object_analysis()
    multi_image_analysis()
    exercises()
    print("\n课程完成！下一步：04-document-ocr.py")


if __name__ == "__main__":
    main()
