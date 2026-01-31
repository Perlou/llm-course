"""
文字转语音
==========

学习目标：
    1. 使用 OpenAI TTS API 生成语音
    2. 了解不同音色和参数设置
    3. 构建语音交互应用

核心概念：
    - TTS (Text-to-Speech)
    - 声音模型选择
    - 流式语音生成

环境要求：
    - pip install openai
"""

import os
from typing import Generator
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：TTS 概述 ====================


def introduction():
    """TTS 概述"""
    print("=" * 60)
    print("第一部分：文字转语音概述")
    print("=" * 60)

    print("""
    📌 OpenAI TTS 特点：
    ┌─────────────────────────────────────────────────────────┐
    │ • 6 种内置音色                                         │
    │ • 支持多语言（自动检测）                               │
    │ • 高质量音频输出                                       │
    │ • 支持实时流式输出                                     │
    │ • 多种音频格式                                         │
    └─────────────────────────────────────────────────────────┘

    📌 可用音色：
    ┌───────────┬───────────────────────────────────────────┐
    │ alloy     │ 中性、平衡                               │
    │ echo      │ 男性、深沉                               │
    │ fable     │ 英式、叙事感                             │
    │ onyx      │ 男性、低沉有力                           │
    │ nova      │ 女性、温暖友好                           │
    │ shimmer   │ 女性、清晰活泼                           │
    └───────────┴───────────────────────────────────────────┘

    📌 模型选择：
    - tts-1: 标准质量，低延迟
    - tts-1-hd: 高质量，稍高延迟
    """)


# ==================== 第二部分：基础使用 ====================


def basic_usage():
    """基础使用"""
    print("\n" + "=" * 60)
    print("第二部分：TTS 基础使用")
    print("=" * 60)

    code = '''
from openai import OpenAI
from pathlib import Path

client = OpenAI()

def text_to_speech(
    text: str,
    output_path: str,
    voice: str = "alloy",
    model: str = "tts-1"
) -> str:
    """文字转语音"""
    response = client.audio.speech.create(
        model=model,      # tts-1 或 tts-1-hd
        voice=voice,      # alloy, echo, fable, onyx, nova, shimmer
        input=text
    )

    # 保存音频文件
    response.stream_to_file(output_path)
    return output_path

# 使用示例
text_to_speech(
    text="你好，欢迎使用语音合成服务！",
    output_path="output.mp3",
    voice="nova"
)

# 高质量版本
text_to_speech(
    text="这是高质量语音输出。",
    output_path="hd_output.mp3",
    voice="alloy",
    model="tts-1-hd"
)
'''
    print(code)


# ==================== 第三部分：流式输出 ====================


def streaming_output():
    """流式输出"""
    print("\n" + "=" * 60)
    print("第三部分：流式语音输出")
    print("=" * 60)

    code = '''
def text_to_speech_streaming(
    text: str,
    output_path: str,
    voice: str = "alloy"
):
    """流式语音输出 - 边生成边播放"""
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
        response_format="mp3"
    )

    # 流式写入文件
    with open(output_path, "wb") as f:
        for chunk in response.iter_bytes(chunk_size=1024):
            f.write(chunk)

    return output_path

# 实时播放（需要 pygame 或类似库）
def stream_and_play(text: str, voice: str = "alloy"):
    """流式生成并实时播放"""
    import pygame
    import io

    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
    )

    # 使用 pygame 播放
    pygame.mixer.init()
    audio_data = io.BytesIO(response.content)
    pygame.mixer.music.load(audio_data)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
'''
    print(code)


# ==================== 第四部分：音频格式 ====================


def audio_formats():
    """音频格式"""
    print("\n" + "=" * 60)
    print("第四部分：音频格式选择")
    print("=" * 60)

    print("""
    📌 支持的格式：
    ┌─────────┬────────────────────────────────────────────┐
    │ mp3     │ 默认格式，通用性好                        │
    │ opus    │ 低延迟，适合实时应用                      │
    │ aac     │ 移动端兼容性好                            │
    │ flac    │ 无损格式，高质量                          │
    │ wav     │ 无压缩，编辑方便                          │
    │ pcm     │ 原始音频，无头信息                        │
    └─────────┴────────────────────────────────────────────┘
    """)

    code = '''
def text_to_speech_format(
    text: str,
    output_path: str,
    voice: str = "alloy",
    format: str = "mp3"
) -> str:
    """指定输出格式"""
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
        response_format=format  # mp3, opus, aac, flac, wav, pcm
    )

    response.stream_to_file(output_path)
    return output_path

# 不同场景使用不同格式
text_to_speech_format("实时对话", "realtime.opus", format="opus")
text_to_speech_format("高质量播客", "podcast.flac", format="flac")
'''
    print(code)


# ==================== 第五部分：完整语音交互 ====================


def voice_interaction():
    """完整语音交互"""
    print("\n" + "=" * 60)
    print("第五部分：完整语音交互系统")
    print("=" * 60)

    code = '''
class VoiceAssistant:
    """语音助手：语音输入 → LLM → 语音输出"""

    def __init__(self, voice: str = "nova"):
        self.client = OpenAI()
        self.voice = voice
        self.conversation = []

    def process(self, audio_input_path: str, audio_output_path: str) -> dict:
        """处理一轮对话"""
        # 1. 语音转文字
        with open(audio_input_path, "rb") as f:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        user_text = transcript.text

        # 2. 添加到对话历史
        self.conversation.append({"role": "user", "content": user_text})

        # 3. LLM 生成回复
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "你是一个友好的语音助手。回复简洁自然，适合语音播放。"},
                *self.conversation
            ]
        )
        assistant_text = response.choices[0].message.content

        # 4. 添加助手回复到历史
        self.conversation.append({"role": "assistant", "content": assistant_text})

        # 5. 文字转语音
        speech = self.client.audio.speech.create(
            model="tts-1",
            voice=self.voice,
            input=assistant_text
        )
        speech.stream_to_file(audio_output_path)

        return {
            "user_text": user_text,
            "assistant_text": assistant_text,
            "audio_path": audio_output_path
        }

# 使用示例
# assistant = VoiceAssistant(voice="nova")
# result = assistant.process("user_audio.mp3", "response.mp3")
'''
    print(code)


# ==================== 第六部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现多音色播客生成（不同角色用不同音色）
    练习 2：构建完整的语音对话机器人

    思考题：如何选择合适的音色？
    答案：
    - 客服场景：nova（友好）或 shimmer（清晰）
    - 有声书：fable（叙事感）
    - 新闻播报：onyx（沉稳）或 alloy（中性）
    - 助手对话：根据品牌调性选择
    """)


def main():
    introduction()
    basic_usage()
    streaming_output()
    audio_formats()
    voice_interaction()
    exercises()
    print("\n" + "=" * 60)
    print("🎉 Phase 11 课程完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
