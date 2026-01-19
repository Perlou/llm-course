"""
流式响应处理
============

学习目标：
    1. 理解流式响应的优势
    2. 掌握 OpenAI 流式 API 的使用方法
    3. 学会处理流式响应的数据结构
    4. 实现流式输出的用户界面

核心概念：
    - Streaming：逐块返回响应，而非等待完整结果
    - Delta：每个流式块中的增量内容
    - 首字延迟（TTFT）：Time To First Token

前置知识：
    - 完成 01-openai-api-basics.py
    - 完成 02-openai-parameters.py

环境要求：
    - pip install openai python-dotenv
"""

import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


# ==================== 第一部分：流式 vs 非流式对比 ====================


def compare_streaming_modes():
    """对比流式和非流式响应"""
    print("=" * 60)
    print("第一部分：流式 vs 非流式对比")
    print("=" * 60)

    client = OpenAI()
    prompt = "写一首关于春天的四句诗"

    print("""
流式响应的优势：
┌─────────────────┬─────────────────────────────────────┐
│ 特点            │ 说明                                │
├─────────────────┼─────────────────────────────────────┤
│ 更快的首字响应  │ 用户立即看到输出开始                │
│ 更好的用户体验  │ 逐字输出更自然，像打字机效果        │
│ 节省等待时间    │ 无需等待完整响应                    │
│ 可提前终止      │ 可以在生成过程中取消                │
└─────────────────┴─────────────────────────────────────┘
    """)

    # 非流式调用
    print("📌 非流式调用（需要等待完整响应）：")
    print("-" * 40)

    start_time = time.time()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        stream=False,
    )
    end_time = time.time()

    print(f"回复: {response.choices[0].message.content}")
    print(f"⏱️ 总耗时: {end_time - start_time:.2f} 秒")

    # 流式调用
    print("\n📌 流式调用（逐字输出）：")
    print("-" * 40)

    start_time = time.time()
    first_token_time = None

    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    print("回复: ", end="", flush=True)
    for chunk in stream:
        if chunk.choices[0].delta.content:
            if first_token_time is None:
                first_token_time = time.time()
            print(chunk.choices[0].delta.content, end="", flush=True)

    print()  # 换行
    end_time = time.time()

    print(f"⏱️ 首字延迟 (TTFT): {first_token_time - start_time:.2f} 秒")
    print(f"⏱️ 总耗时: {end_time - start_time:.2f} 秒")
    print("\n💡 注意：流式模式下，用户第一时间就能看到输出开始！")


# ==================== 第二部分：流式响应数据结构 ====================


def examine_stream_structure():
    """详细查看流式响应的数据结构"""
    print("\n" + "=" * 60)
    print("第二部分：流式响应数据结构")
    print("=" * 60)

    client = OpenAI()

    print("""
流式响应的 chunk 结构：
- 每个 chunk 只包含增量内容 (delta)
- 第一个 chunk 包含 role 信息
- 最后一个 chunk 的 finish_reason 不为 None
    """)

    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "说3个数字"}],
        stream=True,
    )

    print("📦 各个 chunk 的内容：")
    print("-" * 40)

    chunk_count = 0
    for chunk in stream:
        chunk_count += 1
        delta = chunk.choices[0].delta
        finish_reason = chunk.choices[0].finish_reason

        # 格式化输出
        content_str = repr(delta.content) if delta.content else "None"
        role_str = delta.role if delta.role else "None"

        print(
            f"Chunk {chunk_count:2d}: role={role_str:10s} content={content_str:10s} finish_reason={finish_reason}"
        )

    print(f"\n📊 共收到 {chunk_count} 个 chunks")


# ==================== 第三部分：完整的流式处理函数 ====================


def stream_with_full_handling():
    """带完整处理的流式函数"""
    print("\n" + "=" * 60)
    print("第三部分：完整的流式处理函数")
    print("=" * 60)

    client = OpenAI()

    print("下面是一个生产级的流式处理函数示例：\n")

    def stream_chat(messages, on_token=None, on_complete=None):
        """
        流式聊天函数

        Args:
            messages: 消息列表
            on_token: 每收到一个 token 时的回调函数
            on_complete: 完成时的回调函数

        Returns:
            完整的回复内容
        """
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=messages, stream=True
        )

        collected_content = []

        for chunk in stream:
            delta = chunk.choices[0].delta
            finish_reason = chunk.choices[0].finish_reason

            if delta.content:
                collected_content.append(delta.content)
                if on_token:
                    on_token(delta.content)

            if finish_reason == "stop":
                full_content = "".join(collected_content)
                if on_complete:
                    on_complete(full_content)
                return full_content

        return "".join(collected_content)

    # 使用示例
    print("📝 使用示例：")
    print("-" * 40)

    def print_token(token):
        print(token, end="", flush=True)

    def on_done(full_text):
        print(f"\n\n✅ 完成！共 {len(full_text)} 个字符")

    print("回复: ", end="")
    result = stream_chat(
        messages=[{"role": "user", "content": "用一句话解释什么是机器学习"}],
        on_token=print_token,
        on_complete=on_done,
    )


# ==================== 第四部分：异步流式处理 ====================


def async_streaming_intro():
    """异步流式处理介绍（仅展示概念）"""
    print("\n" + "=" * 60)
    print("第四部分：异步流式处理（概念介绍）")
    print("=" * 60)

    print("""
在 Web 应用中，通常使用异步流式处理：

┌─────────────────────────────────────────────────────────────┐
│ # 异步流式示例 (FastAPI + SSE)                              │
├─────────────────────────────────────────────────────────────┤
│ from fastapi import FastAPI                                 │
│ from fastapi.responses import StreamingResponse             │
│ from openai import AsyncOpenAI                              │
│                                                             │
│ app = FastAPI()                                             │
│ client = AsyncOpenAI()                                      │
│                                                             │
│ @app.post("/chat/stream")                                   │
│ async def chat_stream(message: str):                        │
│     async def generate():                                   │
│         stream = await client.chat.completions.create(      │
│             model="gpt-3.5-turbo",                          │
│             messages=[{"role": "user", "content": message}],│
│             stream=True                                     │
│         )                                                   │
│         async for chunk in stream:                          │
│             if chunk.choices[0].delta.content:              │
│                 yield chunk.choices[0].delta.content        │
│                                                             │
│     return StreamingResponse(generate())                    │
└─────────────────────────────────────────────────────────────┘

💡 关键点：
1. 使用 AsyncOpenAI 客户端
2. 使用 async for 遍历流
3. 使用 yield 生成 SSE (Server-Sent Events)
4. 前端使用 EventSource 或 fetch 接收流
    """)


# ==================== 第五部分：模拟打字机效果 ====================


def typewriter_effect():
    """实现打字机效果"""
    print("\n" + "=" * 60)
    print("第五部分：模拟打字机效果")
    print("=" * 60)

    client = OpenAI()

    print("📝 打字机效果演示：")
    print("-" * 40)
    print()

    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "你是一个讲故事的人，用简短有趣的方式讲故事。",
            },
            {"role": "user", "content": "讲一个关于一只勇敢的小猫的50字小故事"},
        ],
        stream=True,
    )

    # 添加少量延迟增强打字机效果
    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            for char in content:
                print(char, end="", flush=True)
                time.sleep(0.02)  # 每个字符延迟 20ms

    print("\n")


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    exercises_text = """
练习 1：测量首字延迟
    修改 compare_streaming_modes() 函数，
    记录并对比不同提示词长度下的首字延迟 (TTFT)。

练习 2：实现流式聊天机器人
    基于 stream_with_full_handling() 中的 stream_chat 函数，
    实现一个交互式的命令行聊天机器人。

练习 3：统计流式 Token
    在流式输出时，实时显示已生成的 token 数量。
    提示：可以简单地统计收到的 chunk 数。

练习 4（进阶）：实现中断功能
    实现一个可以通过键盘中断（Ctrl+C）来停止生成的流式对话。

思考题：
    1. 流式输出时，API 是如何知道何时结束的？
    2. 流式模式是否会影响 token 计费？
    3. 在什么情况下，非流式可能比流式更合适？
    """
    print(exercises_text)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 流式响应处理")
    print("=" * 60)
    print("⚠️ 注意：本课程会多次调用 API，预估消耗约 1000-2000 tokens")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 请先配置 OPENAI_API_KEY 环境变量")
        return

    try:
        compare_streaming_modes()
        examine_stream_structure()
        stream_with_full_handling()
        async_streaming_intro()
        typewriter_effect()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！")
    print("下一步：04-anthropic-claude.py（Claude API 使用）")
    print("=" * 60)


if __name__ == "__main__":
    main()
