"""
MediMind - API 路由导出
"""

from .system import router as system_router
from .health_qa import router as health_qa_router
from .drug import router as drug_router
from .report import router as report_router
from .triage import router as triage_router

__all__ = [
    "system_router",
    "health_qa_router",
    "drug_router",
    "report_router",
    "triage_router",
]
