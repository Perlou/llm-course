"""
成本优化
========

学习目标：
    1. 理解 LLM 应用的成本构成
    2. 掌握 Token 优化技巧
    3. 实现成本监控和控制

核心概念：
    - Token 成本：输入/输出 token 定价
    - Caching：缓存复用
    - 模型选择：在质量和成本间平衡

环境要求：
    - pip install tiktoken openai
"""

import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：成本构成分析 ====================


def introduction():
    """成本构成分析"""
    print("=" * 60)
    print("第一部分：LLM 成本构成")
    print("=" * 60)

    print("""
    📌 LLM 应用成本构成：
    ┌─────────────────────────────────────────────────────────┐
    │  1. API 调用成本 (最大)                                 │
    │     - 输入 Token 费用                                   │
    │     - 输出 Token 费用（通常更贵）                       │
    │                                                         │
    │  2. 基础设施成本                                        │
    │     - 服务器/GPU 费用                                   │
    │     - 向量数据库                                        │
    │                                                         │
    │  3. 存储成本                                            │
    │     - 向量索引存储                                      │
    │     - 缓存存储                                          │
    └─────────────────────────────────────────────────────────┘

    📌 主流模型定价对比 ($/1M tokens)：
    ┌────────────────┬──────────┬──────────┬──────────────┐
    │     模型       │  输入    │   输出   │   性能/成本  │
    ├────────────────┼──────────┼──────────┼──────────────┤
    │ GPT-4o         │  $2.5    │  $10     │   中         │
    │ GPT-4o-mini    │  $0.15   │  $0.6    │   高         │
    │ Claude 3.5     │  $3      │  $15     │   中         │
    │ Claude 3 Haiku │  $0.25   │  $1.25   │   高         │
    └────────────────┴──────────┴──────────┴──────────────┘
    """)


# ==================== 第二部分：Token 优化 ====================


def token_optimization():
    """Token 优化"""
    print("\n" + "=" * 60)
    print("第二部分：Token 优化")
    print("=" * 60)

    code = '''
import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """计算文本的 token 数量"""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def estimate_cost(
    input_text: str,
    output_tokens: int,
    model: str = "gpt-4o"
) -> float:
    """估算 API 调用成本"""
    prices = {
        "gpt-4o": {"input": 2.5/1e6, "output": 10/1e6},
        "gpt-4o-mini": {"input": 0.15/1e6, "output": 0.6/1e6},
    }

    input_tokens = count_tokens(input_text, model)
    price = prices[model]

    cost = input_tokens * price["input"] + output_tokens * price["output"]
    return cost

# 优化示例：精简提示词
verbose_prompt = """
我想请你帮我完成一个任务。这个任务非常重要。
请你仔细阅读以下内容，然后给出你的回答。
在回答时，请确保......（冗长的说明）
"""

concise_prompt = """
任务：{task}
要求：简洁回答，2句话以内
"""

print(f"冗长版 tokens: {count_tokens(verbose_prompt)}")
print(f"精简版 tokens: {count_tokens(concise_prompt)}")
'''
    print(code)


# ==================== 第三部分：缓存策略 ====================


def caching_strategy():
    """缓存策略"""
    print("\n" + "=" * 60)
    print("第三部分：缓存策略")
    print("=" * 60)

    code = '''
import hashlib
import json
from functools import lru_cache

class LLMCache:
    """LLM 响应缓存"""

    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.local_cache = {}

    def _get_cache_key(self, prompt: str, model: str) -> str:
        """生成缓存键"""
        content = f"{model}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, prompt: str, model: str) -> str | None:
        """获取缓存"""
        key = self._get_cache_key(prompt, model)

        # 先查本地缓存
        if key in self.local_cache:
            return self.local_cache[key]

        # 再查 Redis
        if self.redis:
            cached = self.redis.get(key)
            if cached:
                return cached.decode()

        return None

    def set(self, prompt: str, model: str, response: str, ttl: int = 3600):
        """设置缓存"""
        key = self._get_cache_key(prompt, model)
        self.local_cache[key] = response

        if self.redis:
            self.redis.setex(key, ttl, response)

# 使用示例
cache = LLMCache()

def generate_with_cache(prompt: str, model: str = "gpt-4o"):
    # 检查缓存
    cached = cache.get(prompt, model)
    if cached:
        print("命中缓存，节省 API 调用")
        return cached

    # 调用 API
    response = client.chat.completions.create(...)

    # 存入缓存
    cache.set(prompt, model, response.choices[0].message.content)
    return response.choices[0].message.content
'''
    print(code)


# ==================== 第四部分：模型路由 ====================


def model_routing():
    """模型路由策略"""
    print("\n" + "=" * 60)
    print("第四部分：模型路由策略")
    print("=" * 60)

    code = '''
class SmartRouter:
    """智能模型路由器"""

    def __init__(self):
        self.models = {
            "simple": "gpt-4o-mini",    # 简单任务
            "complex": "gpt-4o",         # 复杂任务
            "creative": "gpt-4o",        # 创意任务
        }

    def classify_task(self, prompt: str) -> str:
        """分类任务复杂度"""
        # 简单规则判断
        if len(prompt) < 100 and "简单" in prompt:
            return "simple"
        elif any(w in prompt for w in ["代码", "分析", "推理", "复杂"]):
            return "complex"
        else:
            return "simple"

    def route(self, prompt: str) -> str:
        """路由到合适的模型"""
        task_type = self.classify_task(prompt)
        return self.models[task_type]

# 使用
router = SmartRouter()

def smart_generate(prompt: str):
    model = router.route(prompt)
    print(f"使用模型: {model}")
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response
'''
    print(code)


# ==================== 第五部分：成本监控 ====================


def cost_monitoring():
    """成本监控"""
    print("\n" + "=" * 60)
    print("第五部分：成本监控")
    print("=" * 60)

    code = '''
class CostTracker:
    """成本追踪器"""

    def __init__(self):
        self.usage_log = []
        self.total_cost = 0

    def log_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        user_id: str = None
    ):
        """记录使用量"""
        cost = self._calculate_cost(model, input_tokens, output_tokens)

        self.usage_log.append({
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
            "user_id": user_id
        })

        self.total_cost += cost
        return cost

    def get_daily_report(self) -> dict:
        """获取日报"""
        today = datetime.now().date()
        today_logs = [
            log for log in self.usage_log
            if log["timestamp"].startswith(str(today))
        ]

        return {
            "date": str(today),
            "total_requests": len(today_logs),
            "total_tokens": sum(l["input_tokens"] + l["output_tokens"] for l in today_logs),
            "total_cost": sum(l["cost"] for l in today_logs),
            "by_model": self._group_by_model(today_logs)
        }

    def check_budget(self, budget: float) -> bool:
        """检查是否超预算"""
        if self.total_cost >= budget:
            print(f"⚠️ 已达到预算上限: ${budget}")
            return False
        return True
'''
    print(code)


# ==================== 第六部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现一个带缓存的 LLM 调用函数
    练习 2：设计一个基于任务复杂度的模型路由策略

    思考题：如何在质量和成本之间找到平衡？
    答案：1. 根据任务重要性选择模型
          2. 利用缓存减少重复调用
          3. 优化提示词减少 token
          4. 监控成本设置预算告警
    """)


def main():
    introduction()
    token_optimization()
    caching_strategy()
    model_routing()
    cost_monitoring()
    exercises()
    print("\n" + "=" * 60)
    print("🎉 Phase 10 课程完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
