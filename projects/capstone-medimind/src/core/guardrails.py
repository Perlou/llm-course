"""
MediMind - 安全护栏模块

实现医疗内容的输入安全检查、输出合规检查和自动改写功能。
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import yaml

from src.utils import get_settings, log


class RiskLevel(Enum):
    """风险等级"""
    SAFE = "safe"           # 安全
    CAUTION = "caution"     # 需注意
    WARNING = "warning"     # 警告
    CRITICAL = "critical"   # 危险
    EMERGENCY = "emergency" # 紧急


@dataclass
class GuardrailResult:
    """护栏检查结果"""
    passed: bool
    risk_level: RiskLevel
    message: Optional[str] = None
    matched_patterns: List[str] = None
    modified_content: Optional[str] = None
    
    def __post_init__(self):
        if self.matched_patterns is None:
            self.matched_patterns = []


class GuardrailConfig:
    """护栏配置加载器"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._load_config()
    
    def _load_config(self):
        """加载护栏配置"""
        config_path = Path(__file__).parent.parent.parent / "configs" / "guardrails.yaml"
        
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f)
                log.info("护栏配置加载完成")
        else:
            log.warning(f"护栏配置文件不存在: {config_path}")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> dict:
        """默认配置"""
        return {
            "input_guardrail": {
                "dangerous_patterns": [],
                "emergency_patterns": [],
            },
            "output_guardrail": {
                "diagnostic_patterns": [],
                "disclaimer": "⚕️ 以上信息仅供参考。",
                "emergency_alert": "⚠️ 请拨打120急救电话。",
            },
            "sensitive_topics": {
                "medical_advice": [],
                "mental_health": [],
                "extra_disclaimer": "",
            },
        }
    
    @property
    def input_guardrail(self) -> dict:
        return self._config.get("input_guardrail", {})
    
    @property
    def output_guardrail(self) -> dict:
        return self._config.get("output_guardrail", {})
    
    @property
    def sensitive_topics(self) -> dict:
        return self._config.get("sensitive_topics", {})


class InputGuardrail:
    """输入安全检查"""
    
    def __init__(self, config: GuardrailConfig = None):
        self.config = config or GuardrailConfig()
        self._compile_patterns()
    
    def _compile_patterns(self):
        """编译正则表达式"""
        input_config = self.config.input_guardrail
        
        self.dangerous_patterns = [
            re.compile(p, re.IGNORECASE)
            for p in input_config.get("dangerous_patterns", [])
        ]
        
        self.emergency_patterns = [
            re.compile(p, re.IGNORECASE)
            for p in input_config.get("emergency_patterns", [])
        ]
    
    def check(self, text: str) -> GuardrailResult:
        """
        检查输入文本的安全性
        
        Args:
            text: 用户输入文本
            
        Returns:
            检查结果
        """
        # 检查危险意图
        dangerous_matches = self._find_matches(text, self.dangerous_patterns)
        if dangerous_matches:
            return GuardrailResult(
                passed=False,
                risk_level=RiskLevel.CRITICAL,
                message="检测到可能有害的请求，无法处理。请咨询专业医生。",
                matched_patterns=dangerous_matches,
            )
        
        # 检查紧急情况
        emergency_matches = self._find_matches(text, self.emergency_patterns)
        if emergency_matches:
            return GuardrailResult(
                passed=True,  # 仍然处理，但标记为紧急
                risk_level=RiskLevel.EMERGENCY,
                message="检测到可能的紧急医疗状况。",
                matched_patterns=emergency_matches,
            )
        
        # 安全通过
        return GuardrailResult(
            passed=True,
            risk_level=RiskLevel.SAFE,
        )
    
    def _find_matches(self, text: str, patterns: List[re.Pattern]) -> List[str]:
        """查找匹配的模式"""
        matches = []
        for pattern in patterns:
            if pattern.search(text):
                matches.append(pattern.pattern)
        return matches
    
    def is_emergency(self, text: str) -> bool:
        """检查是否为紧急情况"""
        result = self.check(text)
        return result.risk_level == RiskLevel.EMERGENCY


class OutputGuardrail:
    """输出合规检查"""
    
    def __init__(self, config: GuardrailConfig = None):
        self.config = config or GuardrailConfig()
        self._compile_patterns()
    
    def _compile_patterns(self):
        """编译正则表达式"""
        output_config = self.config.output_guardrail
        
        self.diagnostic_patterns = [
            re.compile(p, re.IGNORECASE)
            for p in output_config.get("diagnostic_patterns", [])
        ]
        
        self.disclaimer = output_config.get(
            "disclaimer",
            "⚕️ 以上信息仅供参考。"
        )
        
        self.emergency_alert = output_config.get(
            "emergency_alert",
            "⚠️ 请拨打120急救电话。"
        )
    
    def check(self, text: str) -> GuardrailResult:
        """
        检查输出文本的合规性
        
        Args:
            text: AI 输出文本
            
        Returns:
            检查结果
        """
        diagnostic_matches = self._find_matches(text, self.diagnostic_patterns)
        
        if diagnostic_matches:
            return GuardrailResult(
                passed=False,
                risk_level=RiskLevel.WARNING,
                message="输出包含诊断性语言，需要改写。",
                matched_patterns=diagnostic_matches,
            )
        
        return GuardrailResult(
            passed=True,
            risk_level=RiskLevel.SAFE,
        )
    
    def _find_matches(self, text: str, patterns: List[re.Pattern]) -> List[str]:
        """查找匹配的模式"""
        matches = []
        for pattern in patterns:
            if pattern.search(text):
                matches.append(pattern.pattern)
        return matches
    
    def rewrite(self, text: str) -> str:
        """
        改写诊断性语言为建议性语言
        
        Args:
            text: 原始输出文本
            
        Returns:
            改写后的文本
        """
        rewrites = {
            r"您患有": "您可能存在",
            r"您得了": "您的症状可能与以下情况相关",
            r"确诊为": "初步判断可能是",
            r"诊断为": "这可能提示",
            r"您的病是": "您的情况可能与以下因素有关",
            r"需要服用(.+?)药": r"可以咨询医生是否适合使用\1药",
            r"必须服用": "建议在医生指导下考虑使用",
            r"建议您用(.+?)治疗": r"您可以咨询医生关于\1的治疗方案",
        }
        
        modified = text
        for pattern, replacement in rewrites.items():
            modified = re.sub(pattern, replacement, modified)
        
        return modified
    
    def add_disclaimer(self, text: str, is_emergency: bool = False) -> str:
        """
        添加免责声明
        
        Args:
            text: 输出文本
            is_emergency: 是否为紧急情况
            
        Returns:
            添加声明后的文本
        """
        # 检查是否已有免责声明
        if "仅供参考" in text or "请咨询" in text:
            return text
        
        result = text
        
        # 紧急情况添加紧急提醒
        if is_emergency:
            result = f"{self.emergency_alert}\n\n{result}"
        
        # 添加免责声明
        result = f"{result}\n\n{self.disclaimer}"
        
        return result
    
    def process(self, text: str, is_emergency: bool = False) -> Tuple[str, GuardrailResult]:
        """
        处理输出文本（检查+改写+添加声明）
        
        Args:
            text: 原始输出
            is_emergency: 是否为紧急情况
            
        Returns:
            (处理后的文本, 检查结果)
        """
        check_result = self.check(text)
        
        # 如果有诊断性语言，进行改写
        processed_text = text
        if not check_result.passed:
            processed_text = self.rewrite(text)
            log.info(f"输出已改写，匹配模式: {check_result.matched_patterns}")
        
        # 添加免责声明
        processed_text = self.add_disclaimer(processed_text, is_emergency)
        
        return processed_text, check_result


class SensitiveTopicHandler:
    """敏感话题处理"""
    
    def __init__(self, config: GuardrailConfig = None):
        self.config = config or GuardrailConfig()
        self._compile_patterns()
    
    def _compile_patterns(self):
        """编译正则表达式"""
        topics = self.config.sensitive_topics
        
        self.medical_advice_patterns = [
            re.compile(p, re.IGNORECASE)
            for p in topics.get("medical_advice", [])
        ]
        
        self.mental_health_patterns = [
            re.compile(p, re.IGNORECASE)
            for p in topics.get("mental_health", [])
        ]
        
        self.extra_disclaimer = topics.get("extra_disclaimer", "")
    
    def detect_topics(self, text: str) -> Dict[str, bool]:
        """
        检测敏感话题
        
        Args:
            text: 输入文本
            
        Returns:
            话题检测结果
        """
        return {
            "medical_advice": any(p.search(text) for p in self.medical_advice_patterns),
            "mental_health": any(p.search(text) for p in self.mental_health_patterns),
        }
    
    def get_extra_disclaimer(self, topics: Dict[str, bool]) -> Optional[str]:
        """获取额外免责声明"""
        if topics.get("mental_health"):
            return self.extra_disclaimer
        return None


class Guardrails:
    """统一护栏接口"""
    
    def __init__(self):
        self.config = GuardrailConfig()
        self.input_guard = InputGuardrail(self.config)
        self.output_guard = OutputGuardrail(self.config)
        self.topic_handler = SensitiveTopicHandler(self.config)
    
    def check_input(self, text: str) -> GuardrailResult:
        """检查输入"""
        return self.input_guard.check(text)
    
    def check_output(self, text: str) -> GuardrailResult:
        """检查输出"""
        return self.output_guard.check(text)
    
    def process_output(self, text: str, is_emergency: bool = False) -> str:
        """处理输出（改写+添加声明）"""
        processed, _ = self.output_guard.process(text, is_emergency)
        return processed
    
    def is_emergency(self, text: str) -> bool:
        """检查是否为紧急情况"""
        return self.input_guard.is_emergency(text)
    
    def detect_sensitive_topics(self, text: str) -> Dict[str, bool]:
        """检测敏感话题"""
        return self.topic_handler.detect_topics(text)


# 单例
_guardrails: Guardrails = None


def get_guardrails() -> Guardrails:
    """获取护栏单例"""
    global _guardrails
    if _guardrails is None:
        _guardrails = Guardrails()
    return _guardrails
