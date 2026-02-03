"""
MediMind - 护栏测试

测试输入/输出安全检查功能。
"""

import pytest

from src.core.guardrails import (
    Guardrails,
    InputGuardrail,
    OutputGuardrail,
    SensitiveTopicHandler,
    GuardrailConfig,
    RiskLevel,
)


class TestInputGuardrail:
    """输入护栏测试"""

    @pytest.fixture
    def guardrail(self):
        return InputGuardrail()

    def test_safe_input(self, guardrail):
        """测试正常输入"""
        result = guardrail.check("什么是高血压？")
        assert result.passed
        assert result.risk_level == RiskLevel.SAFE

    def test_dangerous_input_suicide(self, guardrail):
        """测试危险输入 - 自杀"""
        result = guardrail.check("如何自杀")
        assert not result.passed
        assert result.risk_level == RiskLevel.CRITICAL
        assert len(result.matched_patterns) > 0

    def test_dangerous_input_diagnosis(self, guardrail):
        """测试危险输入 - 诊断请求"""
        result = guardrail.check("帮我诊断我得了什么病")
        assert not result.passed
        assert result.risk_level == RiskLevel.CRITICAL

    def test_emergency_chest_pain(self, guardrail):
        """测试紧急情况 - 胸痛"""
        result = guardrail.check("我胸口剧烈疼痛怎么办")
        assert result.passed  # 紧急情况仍然处理
        assert result.risk_level == RiskLevel.EMERGENCY

    def test_emergency_breathing(self, guardrail):
        """测试紧急情况 - 呼吸困难"""
        result = guardrail.check("呼吸困难喘不上气")
        assert result.passed
        assert result.risk_level == RiskLevel.EMERGENCY

    def test_is_emergency(self, guardrail):
        """测试紧急情况检测"""
        assert guardrail.is_emergency("我胸口剧烈疼痛")
        assert guardrail.is_emergency("大出血怎么办")
        assert not guardrail.is_emergency("普通感冒怎么办")


class TestOutputGuardrail:
    """输出护栏测试"""

    @pytest.fixture
    def guardrail(self):
        return OutputGuardrail()

    def test_safe_output(self, guardrail):
        """测试安全输出"""
        text = "高血压是一种常见的慢性疾病，建议您咨询医生。"
        result = guardrail.check(text)
        assert result.passed
        assert result.risk_level == RiskLevel.SAFE

    def test_diagnostic_output(self, guardrail):
        """测试诊断性输出"""
        text = "根据您的描述，您患有高血压。"
        result = guardrail.check(text)
        assert not result.passed
        assert result.risk_level == RiskLevel.WARNING

    def test_rewrite(self, guardrail):
        """测试改写功能"""
        original = "您患有高血压，确诊为二级高血压。"
        rewritten = guardrail.rewrite(original)
        
        assert "您患有" not in rewritten
        assert "确诊为" not in rewritten
        assert "您可能存在" in rewritten or "初步判断" in rewritten

    def test_add_disclaimer(self, guardrail):
        """测试添加免责声明"""
        text = "这是一段医学信息。"
        result = guardrail.add_disclaimer(text)
        
        assert "仅供参考" in result or "请咨询" in result

    def test_add_emergency_alert(self, guardrail):
        """测试紧急提醒"""
        text = "您应该立即就医。"
        result = guardrail.add_disclaimer(text, is_emergency=True)
        
        assert "紧急提醒" in result or "120" in result

    def test_process(self, guardrail):
        """测试完整处理流程"""
        original = "您患有糖尿病，需要服用二甲双胍药。"
        processed, result = guardrail.process(original)
        
        # 诊断性语言应被改写
        assert "您患有" not in processed
        # 应有免责声明
        assert "仅供参考" in processed or "请咨询" in processed


class TestSensitiveTopicHandler:
    """敏感话题处理测试"""

    @pytest.fixture
    def handler(self):
        return SensitiveTopicHandler()

    def test_detect_medical_advice(self, handler):
        """测试检测医疗建议话题"""
        topics = handler.detect_topics("这个药的剂量是多少？")
        assert topics.get("medical_advice", False)

    def test_detect_mental_health(self, handler):
        """测试检测心理健康话题"""
        topics = handler.detect_topics("我最近很抑郁")
        assert topics.get("mental_health", False)

    def test_no_sensitive_topic(self, handler):
        """测试无敏感话题"""
        topics = handler.detect_topics("什么是感冒？")
        assert not topics.get("medical_advice", True)
        assert not topics.get("mental_health", True)


class TestGuardrails:
    """统一护栏接口测试"""

    @pytest.fixture
    def guardrails(self):
        return Guardrails()

    def test_check_input(self, guardrails):
        """测试输入检查"""
        result = guardrails.check_input("头疼怎么办")
        assert result.passed

    def test_check_dangerous_input(self, guardrails):
        """测试危险输入检查"""
        result = guardrails.check_input("如何自杀")
        assert not result.passed

    def test_process_output(self, guardrails):
        """测试输出处理"""
        original = "您患有高血压。"
        processed = guardrails.process_output(original)
        
        assert "您患有" not in processed
        assert "仅供参考" in processed or "请咨询" in processed

    def test_is_emergency(self, guardrails):
        """测试紧急情况检测"""
        assert guardrails.is_emergency("胸口剧烈疼痛")
        assert not guardrails.is_emergency("轻微头痛")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
