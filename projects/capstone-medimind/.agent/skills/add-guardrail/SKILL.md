---
name: add-guardrail
description: 为 MediMind 添加安全护栏规则（医疗合规）
---

# 添加安全护栏技能

此技能用于为 MediMind 健康助手项目添加和配置安全护栏规则，确保医疗合规。

## 核心文件位置

```
src/core/guardrails.py          # 护栏实现
configs/guardrails.yaml          # 护栏规则配置
src/api/middleware/guardrail.py  # API 中间件
```

## 安全护栏架构

```
用户输入 ──▶ 输入检查器 ──▶ 业务处理 ──▶ 输出检查器 ──▶ 用户
                │                              │
                ▼                              ▼
           紧急情况检测                    诊断语言过滤
           危险意图拦截                    免责声明注入
```

## 护栏规则配置

### configs/guardrails.yaml

```yaml
# 安全护栏配置

input_guardrail:
  # 危险意图关键词（直接拒绝）
  dangerous_patterns:
    - "如何自杀"
    - "如何自残"
    - "如何堕胎"
    - "帮我诊断"
    - "告诉我得了什么病"
    - "开个处方"
    - "怎么买处方药"
    - "哪里可以买到.*处方"

  # 紧急症状关键词（提醒就医）
  emergency_patterns:
    - "胸口剧烈疼痛"
    - "心脏.*疼"
    - "呼吸困难"
    - "无法呼吸"
    - "意识模糊"
    - "意识不清"
    - "大出血"
    - "出血不止"
    - "昏迷"
    - "心跳停止"
    - "抽搐"
    - "剧烈头痛"

output_guardrail:
  # 禁止出现的诊断性语言
  diagnostic_patterns:
    - "您患有"
    - "您得了"
    - "确诊为"
    - "诊断为"
    - "需要服用.*药"
    - "建议您用.*治疗"
    - "处方"

  # 必须包含的免责声明
  disclaimer: "⚕️ 以上信息仅供参考，如有健康问题请咨询专业医生。"

  # 紧急情况提醒
  emergency_alert: "⚠️ 如果您正在经历紧急症状，请立即拨打 120 急救电话！"
```

## 护栏实现

### src/core/guardrails.py

```python
"""
MediMind - 安全护栏模块
"""

import re
from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path
import yaml

from src.utils import log


@dataclass
class GuardrailResult:
    """护栏检查结果"""
    passed: bool
    action: str = "PASS"  # PASS, BLOCK, EMERGENCY_ALERT, REWRITE
    message: Optional[str] = None
    content: Optional[str] = None
    is_emergency: bool = False


class Guardrail:
    """安全护栏"""

    def __init__(self, config_path: str = "configs/guardrails.yaml"):
        self.config = self._load_config(config_path)
        self._compile_patterns()

    def _load_config(self, path: str) -> dict:
        """加载配置"""
        config_file = Path(path)
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {}

    def _compile_patterns(self):
        """编译正则表达式"""
        input_config = self.config.get("input_guardrail", {})
        output_config = self.config.get("output_guardrail", {})

        self.dangerous_patterns = [
            re.compile(p) for p in input_config.get("dangerous_patterns", [])
        ]
        self.emergency_patterns = [
            re.compile(p) for p in input_config.get("emergency_patterns", [])
        ]
        self.diagnostic_patterns = [
            re.compile(p) for p in output_config.get("diagnostic_patterns", [])
        ]

        self.disclaimer = output_config.get(
            "disclaimer",
            "⚕️ 以上信息仅供参考，如有健康问题请咨询专业医生。"
        )
        self.emergency_alert = output_config.get(
            "emergency_alert",
            "⚠️ 如果您正在经历紧急症状，请立即拨打 120 急救电话！"
        )

    def check_input(self, query: str) -> GuardrailResult:
        """检查用户输入"""
        # 1. 检测危险意图
        for pattern in self.dangerous_patterns:
            if pattern.search(query):
                log.warning(f"检测到危险意图: {query[:50]}...")
                return GuardrailResult(
                    passed=False,
                    action="BLOCK",
                    message="抱歉，这个问题我无法回答。如有健康问题，建议您咨询专业医生。",
                )

        # 2. 检测紧急情况
        for pattern in self.emergency_patterns:
            if pattern.search(query):
                log.warning(f"检测到紧急症状: {query[:50]}...")
                return GuardrailResult(
                    passed=True,
                    action="EMERGENCY_ALERT",
                    message=self.emergency_alert,
                    is_emergency=True,
                )

        return GuardrailResult(passed=True)

    def check_output(self, response: str) -> GuardrailResult:
        """检查模型输出"""
        # 1. 检测诊断性语言
        needs_rewrite = False
        for pattern in self.diagnostic_patterns:
            if pattern.search(response):
                log.warning(f"检测到诊断性语言，需要改写")
                needs_rewrite = True
                response = self._make_advisory(response, pattern)

        # 2. 确保包含免责声明
        if self.disclaimer not in response:
            response = response.rstrip() + "\n\n" + self.disclaimer

        return GuardrailResult(
            passed=not needs_rewrite,
            action="REWRITE" if needs_rewrite else "PASS",
            content=response,
        )

    def _make_advisory(self, text: str, pattern: re.Pattern) -> str:
        """将诊断性语言改写为建议性语言"""
        replacements = {
            r"您患有": "您可能存在",
            r"您得了": "您可能存在",
            r"确诊为": "可能与...有关",
            r"诊断为": "可能与...有关",
            r"需要服用(.*)药": "可咨询医生是否需要使用\\1药物",
            r"建议您用(.*)治疗": "建议咨询医生了解\\1治疗方案",
        }
        for old, new in replacements.items():
            text = re.sub(old, new, text)
        return text


# 单例
_guardrail: Optional[Guardrail] = None

def get_guardrail() -> Guardrail:
    """获取护栏实例"""
    global _guardrail
    if _guardrail is None:
        _guardrail = Guardrail()
    return _guardrail
```

## 添加新规则

### 1. 添加危险意图关键词

在 `configs/guardrails.yaml` 的 `dangerous_patterns` 添加：

```yaml
dangerous_patterns:
  - "新的危险关键词"
```

### 2. 添加紧急症状

```yaml
emergency_patterns:
  - "新的紧急症状"
```

### 3. 添加禁止的诊断语言

```yaml
diagnostic_patterns:
  - "新的诊断性表达"
```

## 测试护栏

```python
# tests/test_guardrails.py

import pytest
from src.core.guardrails import Guardrail

class TestGuardrails:
    @pytest.fixture
    def guardrail(self):
        return Guardrail()

    def test_block_dangerous_input(self, guardrail):
        result = guardrail.check_input("帮我诊断一下")
        assert not result.passed
        assert result.action == "BLOCK"

    def test_emergency_detection(self, guardrail):
        result = guardrail.check_input("我胸口剧烈疼痛")
        assert result.passed
        assert result.is_emergency
        assert result.action == "EMERGENCY_ALERT"

    def test_normal_query(self, guardrail):
        result = guardrail.check_input("高血压应该注意什么？")
        assert result.passed
        assert not result.is_emergency

    def test_output_disclaimer(self, guardrail):
        result = guardrail.check_output("这是健康建议")
        assert "仅供参考" in result.content

    def test_rewrite_diagnostic_language(self, guardrail):
        result = guardrail.check_output("您患有高血压")
        assert "您患有" not in result.content
        assert "可能" in result.content or "可能存在" in result.content
```

## 在 API 中使用

```python
from src.api.dependencies import get_guardrail
from src.core.guardrails import Guardrail

@router.post("/chat")
async def chat(
    request: ChatRequest,
    guardrail: Guardrail = Depends(get_guardrail),
):
    # 输入检查
    input_check = guardrail.check_input(request.query)

    if not input_check.passed:
        return ChatResponse(
            answer=input_check.message,
            emergency=False,
        )

    if input_check.is_emergency:
        # 返回紧急提醒 + 正常回答
        ...

    # 输出检查
    output_check = guardrail.check_output(response)
    final_response = output_check.content

    return ChatResponse(answer=final_response)
```

## 注意事项

1. **覆盖率**：确保覆盖常见危险场景
2. **误判率**：避免过于敏感导致正常问题被拦截
3. **日志记录**：记录所有拦截和改写操作
4. **持续更新**：根据用户反馈持续完善规则
5. **多语言**：考虑中英文混合输入
