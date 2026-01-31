"""
语音转文字
==========

学习目标：
    1. 使用 Whisper API 进行语音转文字
    2. 处理不同格式的音频文件
    3. 实现实时语音转写

核心概念：
    - ASR (Automatic Speech Recognition)
    - Whisper：OpenAI 的语音识别模型
    - 音频预处理

环境要求：
    - pip install openai pydub
    - 需要 ffmpeg（音频处理）
"""

import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：语音识别概述 ====================


def introduction():
    """语音识别概述"""
    print("=" * 60)
    print("第一部分：语音识别概述")
    print("=" * 60)

    print("""
    📌 Whisper 模型特点：
    ┌─────────────────────────────────────────────────────────┐
    │ • 多语言支持：100+ 种语言                              │
    │ • 自动检测语言                                          │
    │ • 支持翻译（非英语 → 英语）                            │
    │ • 支持时间戳                                            │
    │ • 可处理噪音和口音                                      │
    └─────────────────────────────────────────────────────────┘

    📌 支持的音频格式：
    - mp3, mp4, mpeg, mpga, m4a, wav, webm

    📌 API 选项：
    ┌───────────────┬─────────────────────────────────────┐
    │ transcriptions│ 语音转文字（保持原语言）             │
    │ translations  │ 语音翻译为英语                       │
    └───────────────┴─────────────────────────────────────┘
    """)


# ==================== 第二部分：基础使用 ====================


def basic_usage():
    """基础使用"""
    print("\n" + "=" * 60)
    print("第二部分：Whisper API 基础使用")
    print("=" * 60)

    code = '''
from openai import OpenAI

client = OpenAI()

def transcribe_audio(audio_path: str, language: str = None) -> str:
    """语音转文字"""
    with open(audio_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language,  # 可选，如 "zh", "en"
            response_format="text"  # text, json, srt, vtt
        )

    return response

def transcribe_with_timestamps(audio_path: str) -> dict:
    """带时间戳的转写"""
    with open(audio_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json",
            timestamp_granularities=["word", "segment"]
        )

    return response

# 使用示例
# text = transcribe_audio("meeting.mp3", language="zh")
# result = transcribe_with_timestamps("interview.wav")
'''
    print(code)


# ==================== 第三部分：语音翻译 ====================


def translation():
    """语音翻译"""
    print("\n" + "=" * 60)
    print("第三部分：语音翻译为英语")
    print("=" * 60)

    code = '''
def translate_audio(audio_path: str) -> str:
    """将非英语语音翻译为英语文本"""
    with open(audio_path, "rb") as audio_file:
        response = client.audio.translations.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )

    return response

# 中文语音 → 英文文本
# english_text = translate_audio("chinese_audio.mp3")
'''
    print(code)


# ==================== 第四部分：音频预处理 ====================


def audio_preprocessing():
    """音频预处理"""
    print("\n" + "=" * 60)
    print("第四部分：音频预处理")
    print("=" * 60)

    code = '''
from pydub import AudioSegment
import math

def convert_audio(input_path: str, output_path: str, format: str = "mp3"):
    """转换音频格式"""
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format=format)
    return output_path

def split_audio(audio_path: str, chunk_duration_ms: int = 60000) -> list:
    """
    分割长音频
    Whisper 限制：最大 25MB
    建议：按分钟分割
    """
    audio = AudioSegment.from_file(audio_path)
    duration = len(audio)
    chunks = []

    for i in range(0, duration, chunk_duration_ms):
        chunk = audio[i:i + chunk_duration_ms]
        chunk_path = f"chunk_{i // chunk_duration_ms}.mp3"
        chunk.export(chunk_path, format="mp3")
        chunks.append(chunk_path)

    return chunks

def transcribe_long_audio(audio_path: str) -> str:
    """转写长音频"""
    # 分割音频
    chunks = split_audio(audio_path, chunk_duration_ms=60000)

    # 依次转写
    full_text = []
    for chunk_path in chunks:
        text = transcribe_audio(chunk_path)
        full_text.append(text)
        os.remove(chunk_path)  # 清理临时文件

    return " ".join(full_text)
'''
    print(code)


# ==================== 第五部分：与 LLM 集成 ====================


def llm_integration():
    """与 LLM 集成"""
    print("\n" + "=" * 60)
    print("第五部分：语音 + LLM 集成")
    print("=" * 60)

    code = '''
def voice_chat(audio_path: str, system_prompt: str = "") -> str:
    """语音对话：语音输入 → LLM 处理 → 文本回复"""
    # 1. 语音转文字
    user_text = transcribe_audio(audio_path, language="zh")

    # 2. LLM 处理
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_text})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    return {
        "user_text": user_text,
        "assistant_text": response.choices[0].message.content
    }

def meeting_assistant(audio_path: str) -> dict:
    """会议助手：转写 + 摘要 + 待办"""
    # 1. 转写
    transcript = transcribe_audio(audio_path)

    # 2. LLM 分析
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": f"""分析以下会议记录：

{transcript}

请提供：
1. 会议摘要（3-5句话）
2. 关键决策
3. 待办事项（明确的 action items）
4. 下一步计划"""
            }
        ]
    )

    return {
        "transcript": transcript,
        "analysis": response.choices[0].message.content
    }
'''
    print(code)


# ==================== 第六部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现一个播客转写工具
    练习 2：构建多语言会议转写系统

    思考题：如何提高语音识别的准确率？
    答案：
    1. 提供语言参数，避免自动检测
    2. 音频预处理（降噪、增益）
    3. 使用高质量麦克风录制
    4. 提供 prompt 引导（专业术语等）
    """)


def main():
    introduction()
    basic_usage()
    translation()
    audio_preprocessing()
    llm_integration()
    exercises()
    print("\n课程完成！下一步：08-text-to-speech.py")


if __name__ == "__main__":
    main()
