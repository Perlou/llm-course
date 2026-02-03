"""
MediMind - 药品查询路由

药品信息查询、药物相互作用查询接口。
"""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List

from src.utils import log

router = APIRouter(prefix="/drug")

# 加载药品数据
_drugs_cache = None


def get_drugs_data() -> List[dict]:
    """获取药品数据（带缓存）"""
    global _drugs_cache
    if _drugs_cache is None:
        drug_file = Path(__file__).parent.parent.parent.parent / "data" / "drug_db" / "drugs.json"
        if drug_file.exists():
            with open(drug_file, "r", encoding="utf-8") as f:
                _drugs_cache = json.load(f)
        else:
            _drugs_cache = []
    return _drugs_cache


class DrugInfo(BaseModel):
    """药品信息"""
    id: str
    name: str
    generic_name: Optional[str] = None
    category: Optional[str] = None
    is_otc: bool = True
    indications: Optional[str] = None
    dosage: Optional[str] = None
    side_effects: Optional[str] = None
    contraindications: Optional[str] = None
    interactions: Optional[str] = None
    precautions: Optional[str] = None


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
    支持两种模式：
    1. 本地 JSON 数据搜索（默认）
    2. 向量语义搜索（需要依赖）
    """
    drugs = get_drugs_data()
    
    # 简单关键词搜索
    results = []
    q_lower = q.lower()
    
    for drug in drugs:
        name = drug.get("name", "").lower()
        generic = drug.get("generic_name", "").lower()
        indications = drug.get("indications", "").lower()
        
        if q_lower in name or q_lower in generic or q_lower in indications:
            results.append(drug)
            if len(results) >= limit:
                break
    
    # 如果本地搜索无结果，尝试向量搜索
    if not results:
        try:
            from src.core import get_retriever
            retriever = get_retriever()
            vector_results = retriever.retrieve_drugs(q, top_k=limit)
            
            for vr in vector_results:
                # 从元数据中提取药品ID，并从缓存中获取完整数据
                drug_id = vr.metadata.get("drug_id", "")
                for drug in drugs:
                    if drug["id"] == drug_id:
                        results.append(drug)
                        break
        except ImportError:
            pass  # 依赖未安装，使用本地搜索结果
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "drugs": results,
            "total": len(results),
            "query": q,
        },
    }


@router.get("/list")
async def list_all_drugs(
    limit: int = Query(20, ge=1, le=100, description="结果数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
):
    """
    获取药品列表
    """
    drugs = get_drugs_data()
    total = len(drugs)
    
    # 分页
    paginated = drugs[offset:offset + limit]
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "drugs": paginated,
            "total": total,
            "limit": limit,
            "offset": offset,
        },
    }


@router.get("/{drug_id}")
async def get_drug_detail(drug_id: str):
    """
    获取药品详情
    
    根据药品 ID 获取完整药品信息。
    """
    drugs = get_drugs_data()
    
    for drug in drugs:
        if drug["id"] == drug_id:
            return {
                "code": 0,
                "message": "success",
                "data": drug,
                "disclaimer": "⚕️ 药品信息仅供参考，用药请遵医嘱。",
            }
    
    raise HTTPException(status_code=404, detail=f"药品不存在: {drug_id}")


@router.post("/interaction")
async def check_interaction(drug_names: List[str]):
    """
    药物相互作用查询
    
    检查多种药物之间的相互作用风险。
    """
    if len(drug_names) < 2:
        raise HTTPException(
            status_code=400,
            detail="至少需要 2 种药品才能查询相互作用",
        )
    
    drugs = get_drugs_data()
    
    # 查找药品信息
    found_drugs = []
    for name in drug_names:
        for drug in drugs:
            if name in drug["name"] or name in drug.get("generic_name", ""):
                found_drugs.append(drug)
                break
    
    if len(found_drugs) < 2:
        return {
            "code": 0,
            "message": "success",
            "data": {
                "interactions": [],
                "safe": True,
                "message": "未找到足够的药品信息进行相互作用分析",
            },
            "disclaimer": "⚕️ 药物相互作用信息仅供参考，具体用药请咨询医生或药师。",
        }
    
    # 分析相互作用
    interactions = []
    for i, drug1 in enumerate(found_drugs):
        for drug2 in found_drugs[i+1:]:
            # 简单的相互作用检测（实际应用需要更复杂的规则）
            interaction_text1 = drug1.get("interactions", "")
            interaction_text2 = drug2.get("interactions", "")
            
            # 检查是否在对方的相互作用列表中
            has_interaction = False
            severity = "low"
            description = ""
            
            if drug2["name"] in interaction_text1 or drug2.get("generic_name", "") in interaction_text1:
                has_interaction = True
                description = f"{drug1['name']} 与 {drug2['name']} 可能存在相互作用"
                severity = "medium"
            
            if has_interaction:
                interactions.append({
                    "drug1": drug1["name"],
                    "drug2": drug2["name"],
                    "severity": severity,
                    "description": description,
                    "recommendation": "建议咨询医生或药师后再联合使用",
                })
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "interactions": interactions,
            "safe": len(interactions) == 0,
            "checked_drugs": [d["name"] for d in found_drugs],
        },
        "disclaimer": "⚕️ 药物相互作用信息仅供参考，具体用药请咨询医生或药师。",
    }
