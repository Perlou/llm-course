"""
MediMind - 智能导诊 Agent

基于 LangGraph 的多轮对话导诊系统，实现症状分析、紧急判断、科室推荐。
"""

from typing import List, Dict, Any, Optional, Literal
from dataclasses import dataclass, field
from enum import Enum
import json

from src.utils import get_settings, log, generate_id
from src.core.guardrails import get_guardrails


class TriageState(Enum):
    """导诊状态"""
    INIT = "init"                    # 初始化
    COLLECTING = "collecting"        # 收集信息
    ANALYZING = "analyzing"          # 分析症状
    EMERGENCY = "emergency"          # 紧急情况
    RECOMMENDING = "recommending"    # 推荐科室
    COMPLETE = "complete"            # 完成


class UrgencyLevel(Enum):
    """紧急程度"""
    NORMAL = "normal"          # 普通
    URGENT = "urgent"          # 较急
    EMERGENCY = "emergency"    # 紧急


@dataclass
class SymptomInfo:
    """症状信息"""
    name: str                         # 症状名称
    duration: Optional[str] = None    # 持续时间
    severity: Optional[str] = None    # 严重程度
    frequency: Optional[str] = None   # 发作频率


@dataclass
class TriageContext:
    """导诊上下文"""
    session_id: str
    state: TriageState = TriageState.INIT
    symptoms: List[SymptomInfo] = field(default_factory=list)
    collected_info: Dict[str, Any] = field(default_factory=dict)
    urgency: UrgencyLevel = UrgencyLevel.NORMAL
    recommended_departments: List[str] = field(default_factory=list)
    messages: List[Dict[str, str]] = field(default_factory=list)
    questions_asked: int = 0
    max_questions: int = 5
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "state": self.state.value,
            "symptoms": [
                {"name": s.name, "duration": s.duration, "severity": s.severity}
                for s in self.symptoms
            ],
            "collected_info": self.collected_info,
            "urgency": self.urgency.value,
            "recommended_departments": self.recommended_departments,
            "questions_asked": self.questions_asked,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TriageContext":
        """从字典创建"""
        ctx = cls(session_id=data["session_id"])
        ctx.state = TriageState(data.get("state", "init"))
        ctx.symptoms = [
            SymptomInfo(name=s["name"], duration=s.get("duration"), severity=s.get("severity"))
            for s in data.get("symptoms", [])
        ]
        ctx.collected_info = data.get("collected_info", {})
        ctx.urgency = UrgencyLevel(data.get("urgency", "normal"))
        ctx.recommended_departments = data.get("recommended_departments", [])
        ctx.questions_asked = data.get("questions_asked", 0)
        return ctx


# 科室映射表
DEPARTMENT_MAPPING = {
    # 症状关键词 -> 推荐科室
    "头痛": ["神经内科", "疼痛科"],
    "头晕": ["神经内科", "耳鼻喉科"],
    "胸痛": ["心血管内科", "急诊科"],
    "胸闷": ["心血管内科", "呼吸内科"],
    "心悸": ["心血管内科"],
    "咳嗽": ["呼吸内科", "耳鼻喉科"],
    "发烧": ["发热门诊", "感染科"],
    "发热": ["发热门诊", "感染科"],
    "腹痛": ["消化内科", "普外科"],
    "胃痛": ["消化内科"],
    "腹泻": ["消化内科", "感染科"],
    "便秘": ["消化内科"],
    "恶心": ["消化内科"],
    "呕吐": ["消化内科", "急诊科"],
    "皮疹": ["皮肤科"],
    "瘙痒": ["皮肤科"],
    "关节痛": ["骨科", "风湿免疫科"],
    "腰痛": ["骨科", "康复科"],
    "失眠": ["神经内科", "心理科"],
    "焦虑": ["心理科", "精神科"],
    "抑郁": ["心理科", "精神科"],
    "眼睛": ["眼科"],
    "视力": ["眼科"],
    "耳鸣": ["耳鼻喉科"],
    "听力": ["耳鼻喉科"],
    "鼻塞": ["耳鼻喉科"],
    "咽痛": ["耳鼻喉科"],
    "血压高": ["心血管内科"],
    "血糖高": ["内分泌科"],
    "尿频": ["泌尿外科", "肾内科"],
    "尿急": ["泌尿外科"],
    "月经": ["妇科"],
    "怀孕": ["产科", "妇科"],
}

# 紧急症状列表
EMERGENCY_SYMPTOMS = [
    "胸痛剧烈", "呼吸困难", "意识模糊", "大量出血",
    "剧烈头痛", "突然瘫痪", "抽搐", "高烧不退",
    "严重过敏", "心跳骤停", "昏迷",
]

# 问诊问题模板
TRIAGE_QUESTIONS = [
    "您的主要不适症状是什么？",
    "这个症状持续多长时间了？",
    "症状是持续存在还是间歇发作？",
    "有什么因素会加重或缓解症状？",
    "您之前有过类似的情况吗？有什么基础疾病吗？",
]


class TriageAgent:
    """智能导诊 Agent"""
    
    def __init__(self):
        self.guardrails = get_guardrails()
        self._sessions: Dict[str, TriageContext] = {}
    
    def start_session(self) -> TriageContext:
        """开始新的导诊会话"""
        session_id = generate_id("triage_")
        context = TriageContext(session_id=session_id)
        context.state = TriageState.COLLECTING
        self._sessions[session_id] = context
        
        log.info(f"开始导诊会话: {session_id}")
        return context
    
    def get_session(self, session_id: str) -> Optional[TriageContext]:
        """获取会话"""
        return self._sessions.get(session_id)
    
    def process_message(
        self,
        session_id: str,
        user_message: str,
    ) -> Dict[str, Any]:
        """
        处理用户消息
        
        Args:
            session_id: 会话 ID
            user_message: 用户消息
            
        Returns:
            响应字典
        """
        context = self.get_session(session_id)
        if not context:
            return {
                "error": True,
                "message": "会话不存在或已过期",
            }
        
        # 保存用户消息
        context.messages.append({
            "role": "user",
            "content": user_message,
        })
        
        # 检查输入安全性
        input_check = self.guardrails.check_input(user_message)
        if not input_check.passed:
            return {
                "error": True,
                "message": input_check.message,
                "session_id": session_id,
            }
        
        # 检查紧急情况
        if self.guardrails.is_emergency(user_message):
            context.urgency = UrgencyLevel.EMERGENCY
            context.state = TriageState.EMERGENCY
            return self._handle_emergency(context)
        
        # 根据当前状态处理
        if context.state == TriageState.COLLECTING:
            return self._handle_collecting(context, user_message)
        elif context.state == TriageState.ANALYZING:
            return self._handle_analyzing(context)
        elif context.state == TriageState.RECOMMENDING:
            return self._handle_recommending(context)
        elif context.state == TriageState.COMPLETE:
            return self._handle_complete(context)
        else:
            return self._handle_collecting(context, user_message)
    
    def _handle_emergency(self, context: TriageContext) -> Dict[str, Any]:
        """处理紧急情况"""
        context.state = TriageState.COMPLETE
        
        response = """🚨 **紧急情况提醒**

检测到您可能正在经历紧急医疗状况！

**请立即采取以下措施：**
1. 📞 **拨打 120 急救电话**
2. 🏥 **前往最近医院急诊科**
3. ⏰ **不要延误，时间就是生命**

如果有人陪伴，请让他们：
- 准备好您的身份证、医保卡
- 简要记录症状发作时间
- 保持您处于安全姿势

**请勿等待，立即就医！**"""
        
        context.messages.append({
            "role": "assistant",
            "content": response,
        })
        
        return {
            "session_id": context.session_id,
            "state": context.state.value,
            "urgency": context.urgency.value,
            "message": response,
            "is_complete": True,
            "recommended_departments": ["急诊科"],
        }
    
    def _handle_collecting(
        self,
        context: TriageContext,
        user_message: str,
    ) -> Dict[str, Any]:
        """处理信息收集阶段"""
        # 提取症状
        symptoms = self._extract_symptoms(user_message)
        for symptom in symptoms:
            if not any(s.name == symptom for s in context.symptoms):
                context.symptoms.append(SymptomInfo(name=symptom))
        
        context.questions_asked += 1
        
        # 判断是否收集足够信息
        if context.questions_asked >= context.max_questions or len(context.symptoms) >= 3:
            context.state = TriageState.ANALYZING
            return self._handle_analyzing(context)
        
        # 生成下一个问题
        next_question = self._generate_next_question(context)
        
        context.messages.append({
            "role": "assistant",
            "content": next_question,
        })
        
        return {
            "session_id": context.session_id,
            "state": context.state.value,
            "urgency": context.urgency.value,
            "message": next_question,
            "is_complete": False,
            "symptoms": [s.name for s in context.symptoms],
            "questions_asked": context.questions_asked,
        }
    
    def _handle_analyzing(self, context: TriageContext) -> Dict[str, Any]:
        """处理分析阶段"""
        context.state = TriageState.RECOMMENDING
        
        # 分析症状并推荐科室
        departments = self._recommend_departments(context)
        context.recommended_departments = departments
        
        # 判断紧急程度
        urgency = self._assess_urgency(context)
        context.urgency = urgency
        
        return self._handle_recommending(context)
    
    def _handle_recommending(self, context: TriageContext) -> Dict[str, Any]:
        """处理推荐阶段"""
        context.state = TriageState.COMPLETE
        
        # 生成就医建议
        recommendation = self._generate_recommendation(context)
        
        context.messages.append({
            "role": "assistant",
            "content": recommendation,
        })
        
        return {
            "session_id": context.session_id,
            "state": context.state.value,
            "urgency": context.urgency.value,
            "message": recommendation,
            "is_complete": True,
            "recommended_departments": context.recommended_departments,
            "symptoms": [s.name for s in context.symptoms],
        }
    
    def _handle_complete(self, context: TriageContext) -> Dict[str, Any]:
        """处理完成阶段"""
        return {
            "session_id": context.session_id,
            "state": context.state.value,
            "message": "导诊已完成。如需重新咨询，请开始新的会话。",
            "is_complete": True,
            "recommended_departments": context.recommended_departments,
        }
    
    def _extract_symptoms(self, text: str) -> List[str]:
        """从文本中提取症状"""
        symptoms = []
        
        for keyword in DEPARTMENT_MAPPING.keys():
            if keyword in text:
                symptoms.append(keyword)
        
        # 额外的症状关键词
        extra_symptoms = [
            "疼", "痛", "痒", "肿", "红", "热", "麻", "晕",
            "吐", "泻", "闷", "喘", "咳", "烧",
        ]
        for symptom in extra_symptoms:
            if symptom in text and symptom not in symptoms:
                # 尝试提取完整症状词
                for keyword in DEPARTMENT_MAPPING.keys():
                    if symptom in keyword and keyword in text:
                        if keyword not in symptoms:
                            symptoms.append(keyword)
                        break
        
        return symptoms
    
    def _generate_next_question(self, context: TriageContext) -> str:
        """生成下一个追问"""
        idx = context.questions_asked - 1
        
        if idx < len(TRIAGE_QUESTIONS):
            base_question = TRIAGE_QUESTIONS[idx]
        else:
            base_question = "还有其他不适吗？"
        
        # 根据已收集的症状定制问题
        if context.symptoms and idx == 1:
            symptom_name = context.symptoms[0].name
            return f"您提到{symptom_name}，这个症状大概持续多长时间了？"
        
        return base_question
    
    def _recommend_departments(self, context: TriageContext) -> List[str]:
        """推荐科室"""
        departments = set()
        
        for symptom in context.symptoms:
            if symptom.name in DEPARTMENT_MAPPING:
                for dept in DEPARTMENT_MAPPING[symptom.name]:
                    departments.add(dept)
        
        # 如果没有匹配，推荐全科
        if not departments:
            departments.add("全科门诊")
        
        return list(departments)[:3]  # 最多返回3个科室
    
    def _assess_urgency(self, context: TriageContext) -> UrgencyLevel:
        """评估紧急程度"""
        symptom_names = [s.name for s in context.symptoms]
        
        # 检查紧急症状 - 需要完全匹配紧急症状
        for symptom in symptom_names:
            if symptom in EMERGENCY_SYMPTOMS:
                return UrgencyLevel.EMERGENCY
        
        # 检查较急症状 - 症状中包含紧急关键词
        urgent_keywords = ["剧烈", "严重", "突然", "持续加重", "不止"]
        for symptom in symptom_names:
            for keyword in urgent_keywords:
                if keyword in symptom:
                    return UrgencyLevel.URGENT
        
        return UrgencyLevel.NORMAL
    
    def _generate_recommendation(self, context: TriageContext) -> str:
        """生成就医建议"""
        symptoms_str = "、".join([s.name for s in context.symptoms]) or "您描述的症状"
        departments_str = "、".join(context.recommended_departments)
        
        urgency_text = {
            UrgencyLevel.NORMAL: "建议您在方便时",
            UrgencyLevel.URGENT: "建议您尽快（24小时内）",
            UrgencyLevel.EMERGENCY: "建议您立即",
        }
        
        urgency_advice = urgency_text.get(context.urgency, "建议您")
        
        recommendation = f"""## 🏥 导诊结果

### 症状总结
根据您描述的症状：**{symptoms_str}**

### 推荐科室
{urgency_advice}前往以下科室就诊：
"""
        
        for i, dept in enumerate(context.recommended_departments, 1):
            recommendation += f"\n{i}. **{dept}**"
        
        recommendation += f"""

### 就诊建议
- 携带身份证、医保卡
- 准备好病历资料（如有）
- 记录症状发作时间和特点
- 列出正在服用的药物

### 注意事项
- 如症状加重或出现新症状，请及时就医
- 本建议仅供参考，最终诊断需由医生确定

---
⚕️ *以上建议仅供参考，不构成医疗诊断。请以医生诊断为准。*"""
        
        return recommendation


# 单例
_triage_agent: TriageAgent = None


def get_triage_agent() -> TriageAgent:
    """获取导诊 Agent 单例"""
    global _triage_agent
    if _triage_agent is None:
        _triage_agent = TriageAgent()
    return _triage_agent
