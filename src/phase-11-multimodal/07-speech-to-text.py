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

📌 Gemini 迁移说明：
    Gemini SDK当前不提供语音识别功能。

    推荐替代方案：
    1. Google Cloud Speech-to-Text API（企业级，高准确度）
    2. SpeechRecognition库（免费，易用）
    3. faster-whisper（本地高性能）

    本文件保留教学价值，展示语音转文字的概念和应用场景。
    示例代码使用OpenAI Whisper API演示。
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

        ✅ 参考答案：
        ```python
        from openai import OpenAI
        from pydub import AudioSegment
        import os
        from typing import Dict
        
        class PodcastTranscriber:
            '''播客转写工具'''
            
            def __init__(self, api_key: str = None):
                self.client = OpenAI(api_key=api_key)
            
            def split_audio(
                self, 
                audio_path: str, 
                chunk_minutes: int = 10
            ) -> list:
                '''分割长音频'''
                audio = AudioSegment.from_file(audio_path)
                chunk_ms = chunk_minutes * 60 * 1000
                chunks = []
                
                for i in range(0, len(audio), chunk_ms):
                    chunk = audio[i:i + chunk_ms]
                    chunk_path = f"temp_chunk_{i // chunk_ms}.mp3"
                    chunk.export(chunk_path, format="mp3")
                    chunks.append(chunk_path)
                
                return chunks
            
            def transcribe_chunk(
                self, 
                audio_path: str,
                language: str = None
            ) -> Dict:
                '''转写单个片段'''
                with open(audio_path, "rb") as f:
                    response = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=f,
                        language=language,
                        response_format="verbose_json",
                        timestamp_granularities=["segment"]
                    )
                return response
            
            def transcribe_podcast(
                self, 
                audio_path: str,
                language: str = "zh",
                output_format: str = "text"
            ) -> Dict:
                '''转写完整播客'''
                # 分割音频
                chunks = self.split_audio(audio_path)
                
                full_text = []
                segments = []
                
                for i, chunk_path in enumerate(chunks):
                    result = self.transcribe_chunk(chunk_path, language)
                    full_text.append(result.text)
                    
                    # 调整时间戳偏移
                    offset = i * 10 * 60  # 每块10分钟
                    for seg in result.segments:
                        segments.append({
                            'start': seg.start + offset,
                            'end': seg.end + offset,
                            'text': seg.text
                        })
                    
                    # 清理临时文件
                    os.remove(chunk_path)
                
                return {
                    'text': ' '.join(full_text),
                    'segments': segments,
                    'duration': segments[-1]['end'] if segments else 0
                }
            
            def generate_summary(self, transcript: str) -> str:
                '''生成摘要'''
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{
                        "role": "user",
                        "content": f'''为这期播客生成摘要：

{transcript[:8000]}

请提供：
1. 主题概述（2-3句话）
2. 核心观点（3-5个要点）
3. 精彩片段（引用原文）
4. 推荐收听理由'''
                    }]
                )
                return response.choices[0].message.content
        
        # 使用示例
        # transcriber = PodcastTranscriber()
        # result = transcriber.transcribe_podcast("podcast.mp3")
        # summary = transcriber.generate_summary(result['text'])
        ```
    
    练习 2：构建多语言会议转写系统

        ✅ 参考答案：
        ```python
        class MultiLangMeetingTranscriber:
            '''多语言会议转写系统'''
            
            def __init__(self, api_key: str = None):
                self.client = OpenAI(api_key=api_key)
            
            def detect_language(self, audio_path: str) -> str:
                '''检测音频语言'''
                with open(audio_path, "rb") as f:
                    # Whisper 会返回检测到的语言
                    response = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=f,
                        response_format="verbose_json"
                    )
                return response.language
            
            def transcribe_meeting(
                self, 
                audio_path: str,
                target_language: str = "zh"
            ) -> Dict:
                '''转写会议并翻译'''
                # 1. 转写原文
                with open(audio_path, "rb") as f:
                    original = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=f,
                        response_format="verbose_json",
                        timestamp_granularities=["segment"]
                    )
                
                # 2. 如果不是目标语言，进行翻译
                translated_text = None
                if original.language != target_language:
                    response = self.client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{
                            "role": "user",
                            "content": f"将以下{original.language}文本翻译为{target_language}：\\n\\n{original.text}"
                        }]
                    )
                    translated_text = response.choices[0].message.content
                
                # 3. 提取会议信息
                analysis = self.analyze_meeting(original.text)
                
                return {
                    'original_language': original.language,
                    'original_text': original.text,
                    'translated_text': translated_text,
                    'segments': original.segments,
                    'analysis': analysis
                }
            
            def analyze_meeting(self, transcript: str) -> Dict:
                '''分析会议内容'''
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{
                        "role": "user",
                        "content": f'''分析这个会议记录，返回 JSON：

{transcript}

{{
    "summary": "会议摘要",
    "participants": ["发言人列表（如可识别）"],
    "key_decisions": ["关键决策"],
    "action_items": [
        {{"assignee": "负责人", "task": "任务", "deadline": "截止日期"}}
    ],
    "next_steps": ["下一步计划"]
}}'''
                    }]
                )
                
                import json
                return json.loads(response.choices[0].message.content)
        
        # 使用示例
        # transcriber = MultiLangMeetingTranscriber()
        # result = transcriber.transcribe_meeting("meeting.mp3", target_language="zh")
        # print(f"原语言: {result['original_language']}")
        ```

    思考题：如何提高语音识别的准确率？

        ✅ 答：
        1. 指定语言 - 提供 language 参数避免自动检测错误
        2. 音频预处理 - 降噪、增益、去除静音
        3. 高质量录音 - 使用好的麦克风，减少环境噪音
        4. 提供 prompt - 告知专业术语、人名等上下文
        5. 分段处理 - 长音频分割后分别处理
        6. 后处理校正 - 用 LLM 纠正常见错误和专业术语
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
