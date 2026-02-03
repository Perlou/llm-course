"""
MediMind - 药品查询路由

药品信息查询、药物相互作用查询接口。
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List

router = APIRouter(prefix="/drug")


class DrugInfo(BaseModel):
    """药品信息"""
    id: str
    name: str
    generic_name: Optional[str] = None
    category: Optional[str] = None
    indications: Optional[str] = None
    dosage: Optional[str] = None
    side_effects: Optional[str] = None
    contraindications: Optional[str] = None
    interactions: Optional[str] = None


class InteractionResult(BaseModel):
    """药物相互作用结果"""
    drug1: str
    drug2: str
    severity: str  # low, medium, high
    description: str
    recommendation: str


@router.get("/search")
async def search_drugs(
    q: str = Query(..., min_length=1, max_length=100, description="搜索关键词"),
    limit: int = Query(10, ge=1, le=50, description="结果数量限制"),
):
    """
    药品搜索接口
    
    根据药品名称或通用名搜索药品信息。
    """
    # TODO: 实现药品搜索
    return {
        "code": 0,
        "message": "success",
        "data": {
            "drugs": [],
            "total": 0,
            "query": q,
        },
    }


@router.get("/{drug_id}")
async def get_drug_detail(drug_id: str):
    """
    获取药品详情
    
    根据药品 ID 获取完整药品信息。
    """
    # TODO: 实现药品详情查询
    return {
        "code": 0,
        "message": "success",
        "data": None,
        "disclaimer": "药品信息仅供参考，用药请遵医嘱。",
    }


@router.post("/interaction")
async def check_interaction(drug_ids: List[str]):
    """
    药物相互作用查询
    
    检查多种药物之间的相互作用风险。
    """
    if len(drug_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="至少需要 2 种药品才能查询相互作用",
        )
    
    # TODO: 实现药物相互作用查询
    return {
        "code": 0,
        "message": "success",
        "data": {
            "interactions": [],
            "safe": True,
        },
        "disclaimer": "药物相互作用信息仅供参考，具体用药请咨询医生或药师。",
    }
