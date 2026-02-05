"""
MediMind - API 路由导出
"""

from .system import router as system_router
from .health_qa import router as health_qa_router
from .drug import router as drug_router
from .report import router as report_router
from .triage import router as triage_router
from .auth import router as auth_router
from .profile import router as profile_router
from .hospital import router as hospital_router
from .reminder import router as reminder_router

__all__ = [
    "system_router",
    "health_qa_router",
    "drug_router",
    "report_router",
    "triage_router",
    "auth_router",
    "profile_router",
    "hospital_router",
    "reminder_router",
]
