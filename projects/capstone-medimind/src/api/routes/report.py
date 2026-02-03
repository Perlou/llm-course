"""
MediMind - 报告解读路由

体检报告、化验单图像解读接口。
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

router = APIRouter(prefix="/report")


class LabItem(BaseModel):
    """检验指标项"""
    name: str
    value: str
    unit: Optional[str] = None
    normal_range: Optional[str] = None
    status: str = "NORMAL"  # NORMAL, HIGH, LOW
    explanation: Optional[str] = None


class ReportAnalysis(BaseModel):
    """报告分析结果"""
    items: List[LabItem]
    summary: str
    abnormal_count: int
    should_consult_doctor: bool


@router.post("/analyze")
async def analyze_report(
    image: UploadFile = File(..., description="报告图片"),
):
    """
    报告解读接口
    
    上传体检报告或化验单图片，获取智能解读。
    
    支持格式: JPG, PNG
    """
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {image.content_type}，请上传 JPG 或 PNG 图片",
        )
    
    # 验证文件大小 (最大 10MB)
    contents = await image.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="文件过大，请上传小于 10MB 的图片",
        )
    
    # TODO: 实现报告解读
    # 1. 图像预处理
    # 2. Gemini Vision 识别
    # 3. 指标解析
    # 4. 生成解读报告
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "items": [],
            "summary": "报告解读功能开发中，请稍后再试。",
            "abnormal_count": 0,
            "should_consult_doctor": False,
        },
        "disclaimer": "⚕️ 报告解读仅供参考，如有异常指标请咨询专业医生。",
    }


@router.get("/indices")
async def list_common_indices():
    """
    获取常见检验指标列表
    
    返回常见检验指标及其说明。
    """
    # TODO: 从数据库获取
    common_indices = [
        {"name": "血红蛋白", "unit": "g/L", "normal_range": "男: 120-160, 女: 110-150"},
        {"name": "白细胞计数", "unit": "×10⁹/L", "normal_range": "4.0-10.0"},
        {"name": "血小板计数", "unit": "×10⁹/L", "normal_range": "100-300"},
        {"name": "空腹血糖", "unit": "mmol/L", "normal_range": "3.9-6.1"},
        {"name": "总胆固醇", "unit": "mmol/L", "normal_range": "< 5.2"},
    ]
    
    return {
        "code": 0,
        "message": "success",
        "data": common_indices,
    }
