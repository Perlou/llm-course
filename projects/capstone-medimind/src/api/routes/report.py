"""
MediMind - 报告解读路由

医疗检验报告图像分析和指标解读 API。
"""

import base64
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from src.utils import log

router = APIRouter(prefix="/report")


class TextReportRequest(BaseModel):
    """文本报告请求"""
    text: str = Field(..., min_length=10, max_length=10000, description="报告文本内容")


class IndicatorItem(BaseModel):
    """指标项"""
    name: str
    value: str
    unit: str = ""
    reference_range: str = ""
    status: str = "normal"
    explanation: str = ""


class ReportAnalysisResponse(BaseModel):
    """报告分析响应"""
    report_id: str
    report_type: str
    patient_info: Dict[str, str] = {}
    test_date: str = ""
    indicators: List[IndicatorItem]
    summary: str
    recommendations: List[str]
    warnings: List[str]
    abnormal_count: int
    critical_count: int


@router.post("/analyze/image", response_model=dict)
async def analyze_report_image(
    file: UploadFile = File(..., description="报告图片文件"),
):
    """
    分析报告图片
    
    上传医疗检验报告图片，自动识别指标并解读。
    支持格式：JPG, PNG, PDF
    """
    from src.core.report_analyzer import get_report_analyzer
    
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png", "image/webp", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file.content_type}。支持: JPG, PNG, WEBP, PDF",
        )
    
    # 验证文件大小（最大 10MB）
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="文件过大，最大支持 10MB",
        )
    
    try:
        analyzer = get_report_analyzer()
        result = await analyzer.analyze_image(contents, file.filename)
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                **result.to_dict(),
                "abnormal_count": result.abnormal_count,
                "critical_count": result.critical_count,
            },
        }
        
    except Exception as e:
        log.error(f"报告分析失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"报告分析失败: {str(e)}",
        )


@router.post("/analyze/base64", response_model=dict)
async def analyze_report_base64(
    image_base64: str = Form(..., description="Base64编码的图片"),
    filename: str = Form(default="report.jpg", description="文件名"),
):
    """
    分析 Base64 编码的报告图片
    
    适用于前端直接传递 base64 图片数据的场景。
    """
    from src.core.report_analyzer import get_report_analyzer
    
    try:
        # 移除可能的 data URL 前缀
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]
        
        # 解码验证
        try:
            image_bytes = base64.b64decode(image_base64)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="无效的 Base64 编码",
            )
        
        # 验证大小
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="文件过大，最大支持 10MB",
            )
        
        analyzer = get_report_analyzer()
        result = await analyzer.analyze_image(image_bytes, filename)
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                **result.to_dict(),
                "abnormal_count": result.abnormal_count,
                "critical_count": result.critical_count,
            },
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"报告分析失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"报告分析失败: {str(e)}",
        )


@router.post("/analyze/text", response_model=dict)
async def analyze_report_text(request: TextReportRequest):
    """
    分析文本格式的报告
    
    适用于已经 OCR 处理过的报告文本。
    """
    from src.core.report_analyzer import get_report_analyzer
    
    try:
        analyzer = get_report_analyzer()
        result = analyzer.analyze_text_report(request.text)
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                **result.to_dict(),
                "abnormal_count": result.abnormal_count,
                "critical_count": result.critical_count,
            },
        }
        
    except Exception as e:
        log.error(f"文本报告分析失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"分析失败: {str(e)}",
        )


@router.get("/reference/{indicator_name}", response_model=dict)
async def get_indicator_reference(indicator_name: str):
    """
    获取指标参考值
    
    查询特定检验指标的正常参考范围。
    """
    from src.core.report_analyzer import REFERENCE_RANGES
    
    # 直接查找
    if indicator_name in REFERENCE_RANGES:
        ref = REFERENCE_RANGES[indicator_name]
        return {
            "code": 0,
            "message": "success",
            "data": {
                "name": indicator_name,
                "min": ref["min"],
                "max": ref["max"],
                "unit": ref["unit"],
                "aliases": ref.get("alias", []),
            },
        }
    
    # 别名查找
    for name, ref in REFERENCE_RANGES.items():
        aliases = ref.get("alias", [])
        if indicator_name in aliases or any(indicator_name.upper() == a.upper() for a in aliases):
            return {
                "code": 0,
                "message": "success",
                "data": {
                    "name": name,
                    "min": ref["min"],
                    "max": ref["max"],
                    "unit": ref["unit"],
                    "aliases": aliases,
                },
            }
    
    raise HTTPException(
        status_code=404,
        detail=f"未找到指标: {indicator_name}",
    )


@router.get("/references", response_model=dict)
async def list_references():
    """
    获取所有指标参考值
    
    返回系统支持的所有检验指标及其参考范围。
    """
    from src.core.report_analyzer import REFERENCE_RANGES
    
    references = []
    for name, ref in REFERENCE_RANGES.items():
        references.append({
            "name": name,
            "min": ref["min"],
            "max": ref["max"],
            "unit": ref["unit"],
            "aliases": ref.get("alias", []),
        })
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "references": references,
            "total": len(references),
        },
    }


@router.get("/types", response_model=dict)
async def list_report_types():
    """
    获取支持的报告类型
    
    返回系统支持解读的医疗报告类型。
    """
    from src.core.report_analyzer import ReportType
    
    report_types = [
        {"id": "blood_test", "name": "血常规", "description": "红白细胞、血红蛋白、血小板等"},
        {"id": "liver_function", "name": "肝功能", "description": "转氨酶、胆红素、白蛋白等"},
        {"id": "kidney_function", "name": "肾功能", "description": "肌酐、尿素氮、尿酸等"},
        {"id": "blood_lipid", "name": "血脂", "description": "胆固醇、甘油三酯、高低密度脂蛋白"},
        {"id": "blood_sugar", "name": "血糖", "description": "空腹血糖、糖化血红蛋白"},
        {"id": "thyroid", "name": "甲状腺功能", "description": "TSH、T3、T4等"},
        {"id": "urine", "name": "尿常规", "description": "尿蛋白、尿糖、潜血等"},
    ]
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "types": report_types,
            "total": len(report_types),
        },
    }
