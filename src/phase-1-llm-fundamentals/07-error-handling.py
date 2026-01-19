"""
错误处理与重试机制
==================

学习目标：
    1. 了解 LLM API 常见错误类型
    2. 掌握错误处理的最佳实践
    3. 学会实现指数退避重试机制
    4. 使用 tenacity 库进行重试

核心概念：
    - API 错误类型：认证错误、速率限制、服务器错误等
    - 指数退避：每次重试等待时间翻倍
    - 幂等性：相同请求可以安全重试

前置知识：
    - 完成前面的 API 课程

环境要求：
    - pip install openai tenacity python-dotenv
"""

import os
import time
import random
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：常见错误类型 ====================


def error_types_introduction():
    """常见 API 错误类型介绍"""
    print("=" * 60)
    print("第一部分：常见错误类型")
    print("=" * 60)

    print("""
LLM API 常见错误：
┌────────────────────┬──────────┬────────────────────────────────┐
│ 错误类型           │ HTTP 码  │ 处理方式                       │
├────────────────────┼──────────┼────────────────────────────────┤
│ AuthenticationError│ 401      │ 检查 API Key                   │
│ PermissionDenied   │ 403      │ 检查账户权限                   │
│ RateLimitError     │ 429      │ 等待后重试                     │
│ ServerError        │ 500      │ 等待后重试                     │
│ ServiceUnavailable │ 503      │ 等待后重试                     │
│ Timeout            │ -        │ 增加超时时间或重试             │
│ ConnectionError    │ -        │ 检查网络或重试                 │
│ BadRequestError    │ 400      │ 检查请求参数                   │
│ ContentFilterError │ -        │ 修改输入内容                   │
└────────────────────┴──────────┴────────────────────────────────┘

可重试的错误：
✅ RateLimitError (429) - 等待后重试
✅ ServerError (500, 502, 503, 504) - 稍后重试
✅ Timeout - 可以重试
✅ ConnectionError - 可以重试

不可重试的错误：
❌ AuthenticationError (401) - 需要修复 API Key
❌ PermissionDenied (403) - 需要升级账户
❌ BadRequestError (400) - 需要修改请求参数
    """)


# ==================== 第二部分：基础错误处理 ====================


def basic_error_handling():
    """基础错误处理"""
    print("\n" + "=" * 60)
    print("第二部分：基础错误处理")
    print("=" * 60)

    from openai import (
        OpenAI,
        APIError,
        APIConnectionError,
        RateLimitError,
        AuthenticationError,
    )

    print("""
基础错误处理模板：
─────────────────────────────────────────────────────────────
from openai import (
    OpenAI,
    APIError,
    APIConnectionError,
    RateLimitError,
    AuthenticationError,
)

client = OpenAI()

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "你好"}]
    )
    print(response.choices[0].message.content)
    
except AuthenticationError:
    print("❌ API Key 无效，请检查配置")
    
except RateLimitError:
    print("⚠️ 达到速率限制，请稍后重试")
    
except APIConnectionError:
    print("⚠️ 网络连接失败，请检查网络")
    
except APIError as e:
    print(f"❌ API 错误: {e}")
─────────────────────────────────────────────────────────────
    """)

    # 实际演示
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ 未配置 OPENAI_API_KEY，跳过实际演示")
        return

    client = OpenAI()

    print("\n📝 实际测试（正常请求）：")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "说 OK"}],
            max_tokens=10,
        )
        print(f"   ✅ 成功: {response.choices[0].message.content}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")


# ==================== 第三部分：手动实现重试 ====================


def manual_retry_implementation():
    """手动实现重试机制"""
    print("\n" + "=" * 60)
    print("第三部分：手动实现重试机制")
    print("=" * 60)

    print("""
💡 指数退避重试策略：
   每次失败后，等待时间翻倍，加上随机抖动

等待时间 = min(base_delay * 2^attempt + random_jitter, max_delay)

示例：
   第1次失败 → 等待 1-2 秒
   第2次失败 → 等待 2-4 秒
   第3次失败 → 等待 4-8 秒
   第4次失败 → 等待 8-16 秒
    """)

    from openai import OpenAI, RateLimitError, APIError, APIConnectionError

    def call_with_retry(
        client,
        messages,
        model="gpt-3.5-turbo",
        max_retries=3,
        base_delay=1.0,
        max_delay=60.0,
    ):
        """带重试机制的 API 调用"""

        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                response = client.chat.completions.create(
                    model=model, messages=messages
                )
                return response

            except (RateLimitError, APIConnectionError) as e:
                last_exception = e

                if attempt == max_retries:
                    print(f"   ❌ 最终失败，已重试 {max_retries} 次")
                    raise

                # 计算等待时间（指数退避 + 随机抖动）
                delay = min(base_delay * (2**attempt), max_delay)
                jitter = random.uniform(0, delay * 0.1)
                wait_time = delay + jitter

                print(f"   ⚠️ 第 {attempt + 1} 次失败: {type(e).__name__}")
                print(f"   ⏳ 等待 {wait_time:.1f} 秒后重试...")
                time.sleep(wait_time)

            except APIError as e:
                # 服务器错误可以重试
                if hasattr(e, "status_code") and e.status_code >= 500:
                    last_exception = e
                    if attempt < max_retries:
                        delay = min(base_delay * (2**attempt), max_delay)
                        print(f"   ⚠️ 服务器错误 {e.status_code}，等待 {delay:.1f} 秒")
                        time.sleep(delay)
                        continue
                raise  # 其他 API 错误不重试

        raise last_exception

    # 演示代码（不实际运行，避免浪费 API 调用）
    print("""
使用示例：
─────────────────────────────────────────────────────────────
response = call_with_retry(
    client=client,
    messages=[{"role": "user", "content": "你好"}],
    max_retries=3,
    base_delay=1.0
)
print(response.choices[0].message.content)
─────────────────────────────────────────────────────────────
    """)


# ==================== 第四部分：使用 Tenacity 库 ====================


def tenacity_usage():
    """使用 Tenacity 库进行重试"""
    print("\n" + "=" * 60)
    print("第四部分：使用 Tenacity 库")
    print("=" * 60)

    print("""
💡 Tenacity 是 Python 最流行的重试库
   提供丰富的重试策略配置

安装：pip install tenacity
    """)

    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception_type,
        before_sleep_log,
    )
    import logging

    print("""
Tenacity 常用配置：
┌──────────────────────────┬────────────────────────────────────┐
│ 配置                     │ 说明                               │
├──────────────────────────┼────────────────────────────────────┤
│ stop_after_attempt(n)    │ 最多重试 n 次                      │
│ stop_after_delay(s)      │ 总共最多等待 s 秒                  │
│ wait_exponential(...)    │ 指数退避等待                       │
│ wait_random(min, max)    │ 随机等待                           │
│ retry_if_exception_type  │ 只对特定异常重试                   │
│ before_sleep_log         │ 重试前记录日志                     │
└──────────────────────────┴────────────────────────────────────┘
    """)

    print("""
推荐配置示例：
─────────────────────────────────────────────────────────────
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from openai import RateLimitError, APIConnectionError

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
)
def call_llm(client, messages):
    return client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

# 使用
response = call_llm(client, [{"role": "user", "content": "你好"}])
─────────────────────────────────────────────────────────────
    """)

    # 实际演示
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ 未配置 OPENAI_API_KEY，跳过实际演示")
        return

    from openai import OpenAI, RateLimitError, APIConnectionError

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
    )
    def call_llm_with_retry(client, messages):
        return client.chat.completions.create(
            model="gpt-3.5-turbo", messages=messages, max_tokens=20
        )

    print("\n📝 使用 Tenacity 实际测试：")
    try:
        client = OpenAI()
        response = call_llm_with_retry(
            client, [{"role": "user", "content": "说 Hello"}]
        )
        print(f"   ✅ 成功: {response.choices[0].message.content}")
    except Exception as e:
        print(f"   ❌ 最终失败: {e}")


# ==================== 第五部分：生产级错误处理 ====================


def production_error_handling():
    """生产级错误处理模式"""
    print("\n" + "=" * 60)
    print("第五部分：生产级错误处理模式")
    print("=" * 60)

    print("""
生产环境最佳实践：
─────────────────────────────────────────────────────────────
import logging
from typing import Optional
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log,
)
from openai import (
    OpenAI,
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
)

logger = logging.getLogger(__name__)

class LLMService:
    '''生产级 LLM 服务封装'''
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type((
            RateLimitError,
            APIConnectionError,
            APITimeoutError,
        )),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.DEBUG),
    )
    def chat(
        self,
        messages: list,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        timeout: float = 30.0,
    ) -> str:
        '''发送聊天请求'''
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )
        return response.choices[0].message.content
    
    def safe_chat(
        self,
        messages: list,
        **kwargs
    ) -> tuple[str, Optional[Exception]]:
        '''安全调用，返回结果和错误'''
        try:
            result = self.chat(messages, **kwargs)
            return result, None
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            return "", e

# 使用示例
service = LLMService()

# 方式1：可能抛出异常
try:
    result = service.chat([{"role": "user", "content": "你好"}])
except Exception as e:
    print(f"失败: {e}")

# 方式2：安全调用
result, error = service.safe_chat([{"role": "user", "content": "你好"}])
if error:
    # 处理错误（如返回默认回复）
    result = "抱歉，服务暂时不可用"
─────────────────────────────────────────────────────────────
    """)


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    exercises_text = """
练习 1：自定义重试策略
    创建一个重试函数，满足：
    - 最多重试 5 次
    - 指数退避，初始 2 秒，最大 30 秒
    - 只对 RateLimitError 和网络错误重试
    - 每次重试打印日志

练习 2：故障转移
    实现一个函数，当 OpenAI 调用失败时，
    自动切换到 Ollama 本地模型。

练习 3：熔断器模式
    实现一个简单的熔断器：
    - 连续失败 5 次后，暂停调用 60 秒
    - 60 秒后尝试恢复

练习 4：监控和告警
    记录每次 API 调用的结果（成功/失败），
    当错误率超过 10% 时打印告警。

思考题：
    1. 为什么 429 错误需要等待而不是立即重试？
    2. 如何判断一个请求是否"幂等"，可以安全重试？
    3. 在什么情况下应该放弃重试，直接返回错误？
    """
    print(exercises_text)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 错误处理与重试机制")
    print("=" * 60)
    print("💡 本课程介绍 LLM API 的错误处理最佳实践")
    print("=" * 60)

    try:
        error_types_introduction()
        basic_error_handling()
        manual_retry_implementation()
        tenacity_usage()
        production_error_handling()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！")
    print("下一步：08-rate-limiting.py（速率限制与并发控制）")
    print("=" * 60)


if __name__ == "__main__":
    main()
