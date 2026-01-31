"""
安全护栏
========

学习目标：
    1. 理解 LLM 安全威胁类型
    2. 实现输入/输出安全检查
    3. 配置访问控制和审计

核心概念：
    - Prompt 注入：恶意指令攻击
    - 内容过滤：有害内容检测
    - PII 保护：个人信息防泄露

环境要求：
    - pip install guardrails-ai  # 可选
"""

import re
from typing import List, Dict
from dataclasses import dataclass


# ==================== 第一部分：安全威胁概述 ====================


def introduction():
    """安全威胁概述"""
    print("=" * 60)
    print("第一部分：安全威胁概述")
    print("=" * 60)

    print("""
    📌 LLM 安全威胁全景：
    ┌─────────────────────────────────────────────────────────┐
    │  输入威胁                     输出风险                  │
    │  ┌─────────────────┐         ┌─────────────────┐       │
    │  │ • Prompt注入    │         │ • 有害内容      │       │
    │  │ • 越狱攻击      │         │ • 隐私泄露      │       │
    │  │ • 恶意指令      │         │ • 虚假信息      │       │
    │  │ • 敏感信息探测  │         │ • 偏见歧视      │       │
    │  └─────────────────┘         └─────────────────┘       │
    │                                                         │
    │  系统威胁                     合规要求                  │
    │  ┌─────────────────┐         ┌─────────────────┐       │
    │  │ • DDoS攻击      │         │ • 数据保护法规  │       │
    │  │ • 资源耗尽      │         │ • 内容审核要求  │       │
    │  │ • 模型窃取      │         │ • 审计追溯      │       │
    │  └─────────────────┘         └─────────────────┘       │
    └─────────────────────────────────────────────────────────┘

    📌 多层防护体系：
    请求 → [网关层] → [输入过滤] → [模型推理] → [输出审核] → 响应
              ↓            ↓            ↓            ↓
          认证鉴权      注入检测     监控告警      敏感过滤
          速率限制      长度限制     资源隔离      合规审计
    """)


# ==================== 第二部分：输入安全检查 ====================


def input_guard():
    """输入安全检查"""
    print("\n" + "=" * 60)
    print("第二部分：输入安全检查")
    print("=" * 60)

    code = '''
import re
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class GuardResult:
    passed: bool
    reason: str = ""

class InputGuard:
    """输入安全护栏"""

    def __init__(self):
        # Prompt 注入模式
        self.injection_patterns = [
            r"ignore.*previous.*instructions",
            r"disregard.*above",
            r"you are now",
            r"new instructions:",
            r"forget everything",
        ]

        # 敏感词列表
        self.sensitive_words = ["暴力", "毒品", ...]

    def check(self, text: str) -> GuardResult:
        """执行所有检查"""
        checks = [
            self._check_length(text),
            self._check_injection(text),
            self._check_sensitive(text),
        ]
        for result in checks:
            if not result.passed:
                return result
        return GuardResult(passed=True)

    def _check_length(self, text: str, max_len=8192) -> GuardResult:
        if len(text) > max_len:
            return GuardResult(False, f"输入过长: {len(text)}")
        return GuardResult(True)

    def _check_injection(self, text: str) -> GuardResult:
        for pattern in self.injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return GuardResult(False, "检测到注入攻击")
        return GuardResult(True)

    def _check_sensitive(self, text: str) -> GuardResult:
        for word in self.sensitive_words:
            if word in text:
                return GuardResult(False, f"包含敏感词: {word}")
        return GuardResult(True)

# 使用
guard = InputGuard()
result = guard.check(user_input)
if not result.passed:
    return {"error": result.reason}
'''
    print(code)


# ==================== 第三部分：输出安全审核 ====================


def output_guard():
    """输出安全审核"""
    print("\n" + "=" * 60)
    print("第三部分：输出安全审核")
    print("=" * 60)

    code = '''
class OutputGuard:
    """输出安全护栏"""

    def __init__(self):
        # PII 模式
        self.pii_patterns = {
            'phone': r'1[3-9]\d{9}',
            'id_card': r'\d{17}[\dXx]',
            'email': r'\S+@\S+\.\S+',
            'bank_card': r'\d{16,19}',
        }

    def check(self, output: str) -> GuardResult:
        checks = [
            self._check_pii(output),
            self._check_harmful(output),
        ]
        for result in checks:
            if not result.passed:
                return result
        return GuardResult(True)

    def _check_pii(self, text: str) -> GuardResult:
        """检测个人敏感信息"""
        for name, pattern in self.pii_patterns.items():
            if re.search(pattern, text):
                return GuardResult(False, f"检测到 PII: {name}")
        return GuardResult(True)

    def _check_harmful(self, text: str) -> GuardResult:
        """检测有害内容（可接入第三方 API）"""
        # 简单关键词检测或调用内容审核 API
        harmful_words = [...]
        for word in harmful_words:
            if word in text:
                return GuardResult(False, "检测到有害内容")
        return GuardResult(True)

    def mask_pii(self, text: str) -> str:
        """脱敏处理"""
        for name, pattern in self.pii_patterns.items():
            text = re.sub(pattern, f"[{name.upper()}_MASKED]", text)
        return text
'''
    print(code)


# ==================== 第四部分：访问控制配置 ====================


def access_control():
    """访问控制"""
    print("\n" + "=" * 60)
    print("第四部分：访问控制配置")
    print("=" * 60)

    print("""
    📌 安全配置清单：
    ┌────────────────┬──────────────┬──────────────┐
    │    防护措施    │    配置项    │    推荐值    │
    ├────────────────┼──────────────┼──────────────┤
    │    速率限制    │ 每用户 QPS   │   10-50      │
    │    输入限制    │ 最大 Token   │   4096-8192  │
    │    输出限制    │ 最大 Token   │   2048-4096  │
    │    超时控制    │ 请求超时     │   60-120s    │
    │    并发限制    │ 每用户并发   │   2-5        │
    └────────────────┴──────────────┴──────────────┘

    # API Key 管理
    class APIKeyManager:
        def validate(self, key: str) -> bool:
            # 验证 API Key
            pass

        def get_rate_limit(self, key: str) -> int:
            # 获取对应的速率限制
            pass

        def log_usage(self, key: str, tokens: int):
            # 记录使用量
            pass
    """)


# ==================== 第五部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现完整的输入/输出安全护栏
    练习 2：集成第三方内容审核 API

    思考题：如何平衡安全性和用户体验？
    答案：1. 分级审核（严格/宽松模式）
          2. 误报时提供申诉机制
          3. 对敏感内容脱敏而非直接拒绝
    """)


def main():
    introduction()
    input_guard()
    output_guard()
    access_control()
    exercises()
    print("\n" + "=" * 60)
    print("🎉 Phase 9 课程完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
