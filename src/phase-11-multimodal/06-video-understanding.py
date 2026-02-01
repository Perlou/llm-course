"""
视频理解
========

学习目标：
    1. 了解视频理解的方法和挑战
    2. 使用多模态 LLM 分析视频内容
    3. 实现视频摘要和问答

核心概念：
    - 帧采样：从视频中提取关键帧
    - 时序理解：理解视频的时间顺序
    - 视频问答：基于视频内容回答问题

环境要求：
    - pip install google-generativeai pillow opencv-python

📌 Gemini 迁移说明：
    本文件展示视频理解的核心概念（通过帧提取+图像分析）。
    示例代码使用OpenAI API演示，Gemini等价实现参考02-gpt4-vision.py顶部说明。
"""

import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：视频理解概述 ====================


def introduction():
    """视频理解概述"""
    print("=" * 60)
    print("第一部分：视频理解概述")
    print("=" * 60)

    print("""
    📌 视频理解的挑战：
    ┌─────────────────────────────────────────────────────────┐
    │ 1. 数据量大：1分钟视频 = 1800帧 (30fps)               │
    │ 2. 时序依赖：需要理解帧之间的关系                      │
    │ 3. 计算成本：处理大量帧消耗资源                        │
    │ 4. 上下文长度：Token 限制                              │
    └─────────────────────────────────────────────────────────┘

    📌 常用方法：
    ┌─────────────────┬─────────────────────────────────────┐
    │ 关键帧采样      │ 均匀或智能选取代表性帧              │
    │ 场景分割       │ 按场景变化分段处理                   │
    │ 视频摘要       │ 生成视频内容概述                     │
    │ 视频问答       │ 基于视频回答问题                     │
    │ 原生视频模型   │ Gemini 2.0 等支持直接输入视频       │
    └─────────────────┴─────────────────────────────────────┘

    📌 支持视频的模型：
    - Gemini 2.0：原生视频理解
    - Qwen2-VL：支持视频输入
    - GPT-4o：通过帧采样分析
    """)


# ==================== 第二部分：帧采样 ====================


def frame_sampling():
    """帧采样"""
    print("\n" + "=" * 60)
    print("第二部分：视频帧采样")
    print("=" * 60)

    code = '''
import cv2
import base64
from PIL import Image
import io

def extract_frames(video_path: str, num_frames: int = 10) -> list:
    """从视频中均匀采样帧"""
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps

    print(f"视频信息: {total_frames}帧, {fps}fps, {duration:.1f}秒")

    # 均匀采样
    frame_indices = [int(i * total_frames / num_frames) for i in range(num_frames)]

    frames = []
    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            # BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append({
                "frame_idx": idx,
                "timestamp": idx / fps,
                "image": Image.fromarray(frame_rgb)
            })

    cap.release()
    return frames

def frames_to_base64(frames: list) -> list:
    """将帧转换为 base64"""
    base64_frames = []
    for frame in frames:
        buffer = io.BytesIO()
        frame["image"].save(buffer, format="JPEG", quality=85)
        b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        base64_frames.append({
            "timestamp": frame["timestamp"],
            "base64": b64
        })
    return base64_frames
'''
    print(code)


# ==================== 第三部分：视频分析 ====================


def video_analysis():
    """视频分析"""
    print("\n" + "=" * 60)
    print("第三部分：视频内容分析")
    print("=" * 60)

    code = '''
from openai import OpenAI

client = OpenAI()

def analyze_video(video_path: str, num_frames: int = 8) -> str:
    """分析视频内容"""
    # 提取帧
    frames = extract_frames(video_path, num_frames)
    base64_frames = frames_to_base64(frames)

    # 构建请求
    content = [{
        "type": "text",
        "text": """这是一个视频的关键帧序列，请分析视频内容：

1. 视频主题：这个视频在讲什么？
2. 场景描述：主要场景和环境
3. 关键事件：按时间顺序列出发生的事情
4. 人物/物体：主要出现的人物或物体
5. 整体摘要：用2-3句话总结视频

帧序列（按时间顺序）："""
    }]

    for i, frame in enumerate(base64_frames):
        content.append({"type": "text", "text": f"\\n帧 {i+1} (时间: {frame['timestamp']:.1f}秒):"})
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{frame['base64']}"
            }
        })

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": content}],
        max_tokens=1500
    )

    return response.choices[0].message.content
'''
    print(code)


# ==================== 第四部分：视频问答 ====================


def video_qa():
    """视频问答"""
    print("\n" + "=" * 60)
    print("第四部分：视频问答")
    print("=" * 60)

    code = '''
def video_question_answer(
    video_path: str,
    question: str,
    num_frames: int = 8
) -> str:
    """基于视频回答问题"""
    frames = extract_frames(video_path, num_frames)
    base64_frames = frames_to_base64(frames)

    content = [{
        "type": "text",
        "text": f"""这是一个视频的关键帧序列。请根据视频内容回答问题。

问题：{question}

帧序列："""
    }]

    for i, frame in enumerate(base64_frames):
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{frame['base64']}"
            }
        })

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": content}],
        max_tokens=800
    )

    return response.choices[0].message.content

# 使用示例
# answer = video_question_answer("demo.mp4", "视频中有多少人？")
'''
    print(code)


# ==================== 第五部分：使用 Gemini ====================


def gemini_video():
    """使用 Gemini 原生视频理解"""
    print("\n" + "=" * 60)
    print("第五部分：Gemini 原生视频理解")
    print("=" * 60)

    code = '''
import google.generativeai as genai
import time

# 配置 API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def analyze_video_gemini(video_path: str, prompt: str) -> str:
    """使用 Gemini 分析视频（原生支持）"""
    # 上传视频文件
    video_file = genai.upload_file(path=video_path)

    # 等待处理完成
    while video_file.state.name == "PROCESSING":
        print("处理中...")
        time.sleep(5)
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
        raise ValueError("视频处理失败")

    # 调用模型
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(
        [video_file, prompt],
        generation_config={"max_output_tokens": 2000}
    )

    return response.text

# 使用示例
# result = analyze_video_gemini("video.mp4", "总结这个视频的内容")
'''
    print(code)


# ==================== 第六部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现智能帧采样（基于场景变化）
    练习 2：构建视频内容审核系统

    思考题：帧采样数量如何选择？
    答案：
    - 短视频（<1分钟）：6-10帧
    - 中等视频（1-5分钟）：10-16帧
    - 长视频：按场景分段，每段采样
    - 快速变化场景：增加采样密度
    - 静态场景：可减少采样
    """)


def main():
    introduction()
    frame_sampling()
    video_analysis()
    video_qa()
    gemini_video()
    exercises()
    print("\n课程完成！下一步：07-speech-to-text.py")


if __name__ == "__main__":
    main()
