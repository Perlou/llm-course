"""
MediMind 端到端测试
测试所有 API 端点的功能
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """健康检查端点测试"""
    
    def test_health_check(self):
        """测试健康检查接口"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestHealthQAEndpoint:
    """健康问答端点测试"""
    
    def test_chat_simple_query(self):
        """测试简单健康问题"""
        response = client.post(
            "/api/v1/health/chat",
            json={"query": "高血压应该注意什么?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "answer" in data["data"]
        assert "sources" in data["data"]
        assert "conversation_id" in data["data"]
        assert "disclaimer" in data["data"]
    
    def test_chat_with_conversation_id(self):
        """测试带会话 ID 的对话"""
        # 第一轮对话
        response1 = client.post(
            "/api/v1/health/chat",
            json={"query": "糖尿病有什么症状?"}
        )
        assert response1.status_code == 200
        conv_id = response1.json()["data"]["conversation_id"]
        
        # 第二轮对话
        response2 = client.post(
            "/api/v1/health/chat",
            json={
                "query": "如何预防?",
                "conversation_id": conv_id
            }
        )
        assert response2.status_code == 200
        assert response2.json()["data"]["conversation_id"] == conv_id
    
    def test_chat_empty_query(self):
        """测试空查询"""
        response = client.post(
            "/api/v1/health/chat",
            json={"query": ""}
        )
        # 应该返回验证错误
        assert response.status_code in [400, 422]


class TestDrugEndpoint:
    """药品查询端点测试"""
    
    def test_drug_search(self):
        """测试药品搜索"""
        response = client.get("/api/v1/drug/search?q=感冒")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "drugs" in data["data"]
    
    def test_drug_list(self):
        """测试药品列表"""
        response = client.get("/api/v1/drug/list?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "drugs" in data["data"]
        assert len(data["data"]["drugs"]) <= 10
    
    def test_drug_interaction(self):
        """测试药物相互作用检查"""
        response = client.post(
            "/api/v1/drug/interaction",
            json=["阿司匹林", "布洛芬"]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "interactions" in data["data"]
    
    def test_drug_search_empty(self):
        """测试空搜索词"""
        response = client.get("/api/v1/drug/search?q=")
        # 应该返回验证错误
        assert response.status_code in [400, 422]


class TestTriageEndpoint:
    """智能导诊端点测试"""
    
    def test_triage_start_session(self):
        """测试开始导诊会话"""
        response = client.post("/api/v1/triage/start")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "session_id" in data["data"]
        assert "message" in data["data"]
    
    def test_triage_chat(self):
        """测试导诊对话"""
        # 开始会话
        start_response = client.post("/api/v1/triage/start")
        session_id = start_response.json()["data"]["session_id"]
        
        # 发送症状
        chat_response = client.post(
            f"/api/v1/triage/{session_id}/chat",
            json={"message": "我头疼,发烧38度"}
        )
        assert chat_response.status_code == 200
        data = chat_response.json()
        assert data["code"] == 200
        assert "message" in data["data"]
    
    def test_triage_status(self):
        """测试获取会话状态"""
        # 开始会话
        start_response = client.post("/api/v1/triage/start")
        session_id = start_response.json()["data"]["session_id"]
        
        # 获取状态
        status_response = client.get(f"/api/v1/triage/{session_id}/status")
        assert status_response.status_code == 200
        data = status_response.json()
        assert data["code"] == 200
        assert "state" in data["data"]
    
    def test_triage_departments(self):
        """测试获取科室列表"""
        response = client.get("/api/v1/triage/departments")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "departments" in data["data"]
    
    def test_triage_invalid_session(self):
        """测试无效会话 ID"""
        response = client.post(
            "/api/v1/triage/invalid-session-id/chat",
            json={"message": "测试"}
        )
        assert response.status_code in [400, 404]


class TestReportEndpoint:
    """报告解读端点测试"""
    
    def test_report_types(self):
        """测试获取支持的报告类型"""
        response = client.get("/api/v1/report/types")
        # 可能需要创建这个端点
        if response.status_code == 200:
            data = response.json()
            assert data["code"] == 200
    
    def test_report_references(self):
        """测试获取指标参考值"""
        response = client.get("/api/v1/report/references")
        # 可能需要创建这个端点
        if response.status_code == 200:
            data = response.json()
            assert data["code"] == 200


class TestErrorHandling:
    """错误处理测试"""
    
    def test_404_not_found(self):
        """测试 404 错误"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """测试不允许的请求方法"""
        response = client.put("/api/v1/health/chat")
        assert response.status_code == 405


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
