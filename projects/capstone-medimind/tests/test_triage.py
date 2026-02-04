"""
MediMind - 导诊 Agent 测试
"""

import pytest

from src.core.triage_agent import (
    TriageAgent,
    TriageContext,
    TriageState,
    UrgencyLevel,
    SymptomInfo,
    get_triage_agent,
)


class TestTriageContext:
    """导诊上下文测试"""

    def test_create_context(self):
        """测试创建上下文"""
        context = TriageContext(session_id="test_123")
        assert context.session_id == "test_123"
        assert context.state == TriageState.INIT
        assert context.urgency == UrgencyLevel.NORMAL
        assert len(context.symptoms) == 0

    def test_context_to_dict(self):
        """测试上下文序列化"""
        context = TriageContext(session_id="test_123")
        context.symptoms.append(SymptomInfo(name="头痛", duration="3天"))
        context.state = TriageState.COLLECTING
        
        data = context.to_dict()
        
        assert data["session_id"] == "test_123"
        assert data["state"] == "collecting"
        assert len(data["symptoms"]) == 1
        assert data["symptoms"][0]["name"] == "头痛"

    def test_context_from_dict(self):
        """测试上下文反序列化"""
        data = {
            "session_id": "test_456",
            "state": "analyzing",
            "symptoms": [{"name": "咳嗽", "duration": "1周"}],
            "urgency": "urgent",
            "recommended_departments": ["呼吸内科"],
            "questions_asked": 3,
        }
        
        context = TriageContext.from_dict(data)
        
        assert context.session_id == "test_456"
        assert context.state == TriageState.ANALYZING
        assert context.urgency == UrgencyLevel.URGENT
        assert len(context.symptoms) == 1


class TestTriageAgent:
    """导诊 Agent 测试"""

    @pytest.fixture
    def agent(self):
        return TriageAgent()

    def test_start_session(self, agent):
        """测试开始会话"""
        context = agent.start_session()
        
        assert context.session_id.startswith("triage_")
        assert context.state == TriageState.COLLECTING
        assert agent.get_session(context.session_id) is not None

    def test_get_nonexistent_session(self, agent):
        """测试获取不存在的会话"""
        result = agent.get_session("nonexistent")
        assert result is None

    def test_process_normal_message(self, agent):
        """测试处理正常消息"""
        context = agent.start_session()
        
        result = agent.process_message(context.session_id, "我最近头痛")
        
        assert not result.get("error")
        assert result.get("session_id") == context.session_id
        assert "头痛" in result.get("symptoms", []) or "message" in result

    def test_process_emergency_message(self, agent):
        """测试处理紧急消息"""
        context = agent.start_session()
        
        result = agent.process_message(context.session_id, "我胸口剧烈疼痛，呼吸困难")
        
        assert result.get("urgency") == "emergency"
        assert result.get("is_complete", False)
        assert "急诊科" in result.get("recommended_departments", [])

    def test_process_dangerous_message(self, agent):
        """测试处理危险消息"""
        context = agent.start_session()
        
        result = agent.process_message(context.session_id, "帮我诊断我得了什么病")
        
        assert result.get("error", False)

    def test_symptom_extraction(self, agent):
        """测试症状提取"""
        symptoms = agent._extract_symptoms("我最近头痛，而且有点咳嗽")
        
        assert "头痛" in symptoms or "咳嗽" in symptoms

    def test_department_recommendation(self, agent):
        """测试科室推荐"""
        context = TriageContext(session_id="test")
        context.symptoms = [
            SymptomInfo(name="头痛"),
            SymptomInfo(name="头晕"),
        ]
        
        departments = agent._recommend_departments(context)
        
        assert len(departments) > 0
        assert "神经内科" in departments

    def test_urgency_assessment_normal(self, agent):
        """测试正常紧急程度评估"""
        context = TriageContext(session_id="test")
        context.symptoms = [SymptomInfo(name="头痛")]
        
        urgency = agent._assess_urgency(context)
        
        assert urgency == UrgencyLevel.NORMAL

    def test_generate_recommendation(self, agent):
        """测试生成就医建议"""
        context = TriageContext(session_id="test")
        context.symptoms = [SymptomInfo(name="胃痛")]
        context.recommended_departments = ["消化内科"]
        context.urgency = UrgencyLevel.NORMAL
        
        recommendation = agent._generate_recommendation(context)
        
        assert "胃痛" in recommendation
        assert "消化内科" in recommendation
        assert "建议" in recommendation


class TestGetTriageAgent:
    """测试获取单例"""

    def test_singleton(self):
        """测试单例模式"""
        agent1 = get_triage_agent()
        agent2 = get_triage_agent()
        
        assert agent1 is agent2


class TestMultiTurnConversation:
    """多轮对话测试"""

    @pytest.fixture
    def agent(self):
        return TriageAgent()

    def test_full_conversation_flow(self, agent):
        """测试完整对话流程"""
        # 开始会话
        context = agent.start_session()
        session_id = context.session_id
        
        # 第一轮：描述症状
        result1 = agent.process_message(session_id, "我最近胃痛很厉害")
        assert not result1.get("error")
        
        # 第二轮：回答持续时间
        result2 = agent.process_message(session_id, "大概持续了3天")
        assert not result2.get("error")
        
        # 第三轮：回答其他问题
        result3 = agent.process_message(session_id, "吃完东西会更痛一点")
        assert not result3.get("error")

    def test_session_isolation(self, agent):
        """测试会话隔离"""
        context1 = agent.start_session()
        context2 = agent.start_session()
        
        agent.process_message(context1.session_id, "头痛")
        agent.process_message(context2.session_id, "咳嗽")
        
        session1 = agent.get_session(context1.session_id)
        session2 = agent.get_session(context2.session_id)
        
        # 确保两个会话的症状不混淆
        symptoms1 = [s.name for s in session1.symptoms]
        symptoms2 = [s.name for s in session2.symptoms]
        
        assert symptoms1 != symptoms2 or len(symptoms1) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
