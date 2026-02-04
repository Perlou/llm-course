"""
MediMind - 医疗报告解读模块

使用 Gemini Vision 进行医疗报告图像分析和指标解读。
"""

import base64
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, BinaryIO
from dataclasses import dataclass, field
from enum import Enum
from io import BytesIO

from src.utils import get_settings, log, generate_id


class IndicatorStatus(Enum):
    """指标状态"""
    NORMAL = "normal"       # 正常
    HIGH = "high"           # 偏高
    LOW = "low"             # 偏低
    CRITICAL = "critical"   # 危急值


class ReportType(Enum):
    """报告类型"""
    BLOOD_TEST = "blood_test"           # 血常规
    LIVER_FUNCTION = "liver_function"   # 肝功能
    KIDNEY_FUNCTION = "kidney_function" # 肾功能
    BLOOD_LIPID = "blood_lipid"         # 血脂
    BLOOD_SUGAR = "blood_sugar"         # 血糖
    THYROID = "thyroid"                 # 甲状腺功能
    URINE = "urine"                     # 尿常规
    UNKNOWN = "unknown"                 # 未知


@dataclass
class IndicatorResult:
    """指标结果"""
    name: str                               # 指标名称
    value: str                              # 检测值
    unit: str = ""                          # 单位
    reference_range: str = ""               # 参考范围
    status: IndicatorStatus = IndicatorStatus.NORMAL
    explanation: str = ""                   # 解释说明
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "reference_range": self.reference_range,
            "status": self.status.value,
            "explanation": self.explanation,
        }


@dataclass
class ReportAnalysisResult:
    """报告分析结果"""
    report_id: str
    report_type: ReportType
    patient_info: Dict[str, str] = field(default_factory=dict)
    test_date: str = ""
    indicators: List[IndicatorResult] = field(default_factory=list)
    summary: str = ""
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    raw_text: str = ""
    
    def to_dict(self) -> dict:
        return {
            "report_id": self.report_id,
            "report_type": self.report_type.value,
            "patient_info": self.patient_info,
            "test_date": self.test_date,
            "indicators": [ind.to_dict() for ind in self.indicators],
            "summary": self.summary,
            "recommendations": self.recommendations,
            "warnings": self.warnings,
        }
    
    @property
    def abnormal_count(self) -> int:
        """异常指标数量"""
        return len([i for i in self.indicators if i.status != IndicatorStatus.NORMAL])
    
    @property
    def critical_count(self) -> int:
        """危急值数量"""
        return len([i for i in self.indicators if i.status == IndicatorStatus.CRITICAL])


# 常见检验指标参考值
REFERENCE_RANGES = {
    # 血常规
    "白细胞计数": {"min": 4.0, "max": 10.0, "unit": "10^9/L", "alias": ["WBC", "白细胞"]},
    "红细胞计数": {"min": 4.0, "max": 5.5, "unit": "10^12/L", "alias": ["RBC", "红细胞"]},
    "血红蛋白": {"min": 120, "max": 160, "unit": "g/L", "alias": ["HGB", "Hb"]},
    "血小板计数": {"min": 100, "max": 300, "unit": "10^9/L", "alias": ["PLT", "血小板"]},
    "中性粒细胞百分比": {"min": 50, "max": 70, "unit": "%", "alias": ["NEUT%"]},
    "淋巴细胞百分比": {"min": 20, "max": 40, "unit": "%", "alias": ["LYMPH%"]},
    
    # 肝功能
    "谷丙转氨酶": {"min": 0, "max": 40, "unit": "U/L", "alias": ["ALT", "丙氨酸氨基转移酶"]},
    "谷草转氨酶": {"min": 0, "max": 40, "unit": "U/L", "alias": ["AST", "天冬氨酸氨基转移酶"]},
    "总胆红素": {"min": 3.4, "max": 17.1, "unit": "μmol/L", "alias": ["TBIL"]},
    "直接胆红素": {"min": 0, "max": 6.8, "unit": "μmol/L", "alias": ["DBIL"]},
    "白蛋白": {"min": 35, "max": 50, "unit": "g/L", "alias": ["ALB"]},
    
    # 肾功能
    "肌酐": {"min": 44, "max": 133, "unit": "μmol/L", "alias": ["Cr", "CREA"]},
    "尿素氮": {"min": 2.9, "max": 8.2, "unit": "mmol/L", "alias": ["BUN"]},
    "尿酸": {"min": 149, "max": 416, "unit": "μmol/L", "alias": ["UA"]},
    
    # 血脂
    "总胆固醇": {"min": 0, "max": 5.2, "unit": "mmol/L", "alias": ["TC", "胆固醇"]},
    "甘油三酯": {"min": 0, "max": 1.7, "unit": "mmol/L", "alias": ["TG"]},
    "高密度脂蛋白": {"min": 1.0, "max": 999, "unit": "mmol/L", "alias": ["HDL-C", "HDL"]},
    "低密度脂蛋白": {"min": 0, "max": 3.4, "unit": "mmol/L", "alias": ["LDL-C", "LDL"]},
    
    # 血糖
    "空腹血糖": {"min": 3.9, "max": 6.1, "unit": "mmol/L", "alias": ["GLU", "FPG", "葡萄糖"]},
    "糖化血红蛋白": {"min": 4.0, "max": 6.0, "unit": "%", "alias": ["HbA1c"]},
}

# 危急值阈值
CRITICAL_VALUES = {
    "白细胞计数": {"low": 2.0, "high": 30.0},
    "血红蛋白": {"low": 60, "high": 200},
    "血小板计数": {"low": 50, "high": 600},
    "空腹血糖": {"low": 2.8, "high": 22.2},
    "肌酐": {"low": 0, "high": 707},
}


class ImagePreprocessor:
    """图像预处理器"""
    
    @staticmethod
    def encode_image(image_data: Union[bytes, BinaryIO, str]) -> str:
        """
        将图像编码为 base64
        
        Args:
            image_data: 图像数据（bytes、文件对象或文件路径）
            
        Returns:
            base64 编码的字符串
        """
        if isinstance(image_data, str):
            # 文件路径
            with open(image_data, "rb") as f:
                data = f.read()
        elif isinstance(image_data, bytes):
            data = image_data
        else:
            # 文件对象
            data = image_data.read()
        
        return base64.b64encode(data).decode("utf-8")
    
    @staticmethod
    def get_mime_type(filename: str) -> str:
        """获取 MIME 类型"""
        ext = Path(filename).suffix.lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".pdf": "application/pdf",
        }
        return mime_types.get(ext, "image/jpeg")


class ReportAnalyzer:
    """医疗报告分析器"""
    
    def __init__(self):
        self.settings = get_settings()
        self._gemini_client = None
    
    def _get_gemini_client(self):
        """获取 Gemini 客户端"""
        if self._gemini_client is None:
            try:
                import google.generativeai as genai
                
                api_key = self.settings.gemini_api_key
                if not api_key:
                    raise ValueError("GEMINI_API_KEY 未配置")
                
                genai.configure(api_key=api_key)
                # 使用支持 Vision 的模型
                self._gemini_client = genai.GenerativeModel("gemini-2.0-flash")
                log.info("Gemini Vision 客户端初始化成功")
                
            except Exception as e:
                log.error(f"Gemini 客户端初始化失败: {e}")
                raise
        
        return self._gemini_client
    
    async def analyze_image(
        self,
        image_data: Union[bytes, str],
        filename: str = "report.jpg",
    ) -> ReportAnalysisResult:
        """
        分析报告图像
        
        Args:
            image_data: 图像数据或文件路径
            filename: 文件名（用于确定 MIME 类型）
            
        Returns:
            分析结果
        """
        report_id = generate_id("report_")
        
        try:
            # 编码图像
            if isinstance(image_data, str) and Path(image_data).exists():
                base64_image = ImagePreprocessor.encode_image(image_data)
            elif isinstance(image_data, bytes):
                base64_image = base64.b64encode(image_data).decode("utf-8")
            else:
                base64_image = image_data
            
            mime_type = ImagePreprocessor.get_mime_type(filename)
            
            # 调用 Gemini Vision
            result = await self._analyze_with_gemini(base64_image, mime_type)
            result.report_id = report_id
            
            # 后处理：检查指标状态
            result = self._process_indicators(result)
            
            log.info(f"报告分析完成: {report_id}, 指标数={len(result.indicators)}")
            return result
            
        except Exception as e:
            log.error(f"报告分析失败: {e}")
            raise
    
    async def _analyze_with_gemini(
        self,
        base64_image: str,
        mime_type: str,
    ) -> ReportAnalysisResult:
        """使用 Gemini Vision 分析"""
        client = self._get_gemini_client()
        
        prompt = """请分析这张医疗检验报告图片，提取以下信息并以JSON格式返回：

1. report_type: 报告类型（blood_test/liver_function/kidney_function/blood_lipid/blood_sugar/thyroid/urine/unknown）
2. patient_info: 患者信息（姓名、性别、年龄等，如能识别）
3. test_date: 检测日期
4. indicators: 检验指标列表，每个指标包含：
   - name: 指标名称
   - value: 检测值（数值）
   - unit: 单位
   - reference_range: 参考范围
5. raw_text: 图片中识别到的主要文本内容

请确保返回有效的JSON格式，示例：
```json
{
  "report_type": "blood_test",
  "patient_info": {"name": "张三", "gender": "男", "age": "45"},
  "test_date": "2026-01-15",
  "indicators": [
    {"name": "白细胞计数", "value": "6.5", "unit": "10^9/L", "reference_range": "4.0-10.0"},
    {"name": "血红蛋白", "value": "145", "unit": "g/L", "reference_range": "120-160"}
  ],
  "raw_text": "检验报告单..."
}
```

如果无法识别某些信息，对应字段留空或使用空数组。"""

        try:
            # 构建图像部分
            import google.generativeai as genai
            
            image_part = {
                "mime_type": mime_type,
                "data": base64_image,
            }
            
            response = client.generate_content([prompt, image_part])
            response_text = response.text
            
            # 解析 JSON
            result = self._parse_gemini_response(response_text)
            return result
            
        except Exception as e:
            log.error(f"Gemini Vision 分析失败: {e}")
            # 返回空结果
            return ReportAnalysisResult(
                report_id="",
                report_type=ReportType.UNKNOWN,
                raw_text=str(e),
            )
    
    def _parse_gemini_response(self, response_text: str) -> ReportAnalysisResult:
        """解析 Gemini 响应"""
        try:
            # 提取 JSON 部分
            json_match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 尝试直接解析
                json_str = response_text
            
            data = json.loads(json_str)
            
            # 转换为结果对象
            report_type = ReportType.UNKNOWN
            type_str = data.get("report_type", "unknown")
            try:
                report_type = ReportType(type_str)
            except ValueError:
                pass
            
            indicators = []
            for ind_data in data.get("indicators", []):
                indicators.append(IndicatorResult(
                    name=ind_data.get("name", ""),
                    value=str(ind_data.get("value", "")),
                    unit=ind_data.get("unit", ""),
                    reference_range=ind_data.get("reference_range", ""),
                ))
            
            return ReportAnalysisResult(
                report_id="",
                report_type=report_type,
                patient_info=data.get("patient_info", {}),
                test_date=data.get("test_date", ""),
                indicators=indicators,
                raw_text=data.get("raw_text", ""),
            )
            
        except json.JSONDecodeError as e:
            log.warning(f"JSON 解析失败: {e}")
            return ReportAnalysisResult(
                report_id="",
                report_type=ReportType.UNKNOWN,
                raw_text=response_text,
            )
    
    def _process_indicators(self, result: ReportAnalysisResult) -> ReportAnalysisResult:
        """处理指标，判断状态并添加解释"""
        for indicator in result.indicators:
            # 查找参考范围
            ref = self._find_reference(indicator.name)
            if ref:
                indicator.status = self._check_status(
                    indicator.name,
                    indicator.value,
                    ref,
                )
                indicator.explanation = self._generate_explanation(
                    indicator.name,
                    indicator.status,
                )
                
                # 更新参考范围（如果原始数据没有）
                if not indicator.reference_range:
                    indicator.reference_range = f"{ref['min']}-{ref['max']} {ref['unit']}"
        
        # 生成总结
        result.summary = self._generate_summary(result)
        result.recommendations = self._generate_recommendations(result)
        result.warnings = self._generate_warnings(result)
        
        return result
    
    def _find_reference(self, name: str) -> Optional[dict]:
        """查找指标参考范围"""
        # 直接匹配
        if name in REFERENCE_RANGES:
            return REFERENCE_RANGES[name]
        
        # 别名匹配
        for ref_name, ref_data in REFERENCE_RANGES.items():
            if name in ref_data.get("alias", []):
                return ref_data
            for alias in ref_data.get("alias", []):
                if alias in name or name in alias:
                    return ref_data
        
        return None
    
    def _check_status(
        self,
        name: str,
        value: str,
        ref: dict,
    ) -> IndicatorStatus:
        """检查指标状态"""
        try:
            # 提取数值
            num_match = re.search(r"[\d.]+", value)
            if not num_match:
                return IndicatorStatus.NORMAL
            
            num_value = float(num_match.group())
            
            # 检查危急值
            if name in CRITICAL_VALUES:
                critical = CRITICAL_VALUES[name]
                if num_value <= critical.get("low", -999):
                    return IndicatorStatus.CRITICAL
                if num_value >= critical.get("high", 99999):
                    return IndicatorStatus.CRITICAL
            
            # 检查正常范围
            if num_value < ref["min"]:
                return IndicatorStatus.LOW
            if num_value > ref["max"]:
                return IndicatorStatus.HIGH
            
            return IndicatorStatus.NORMAL
            
        except (ValueError, TypeError):
            return IndicatorStatus.NORMAL
    
    def _generate_explanation(self, name: str, status: IndicatorStatus) -> str:
        """生成指标解释"""
        explanations = {
            "白细胞计数": {
                IndicatorStatus.HIGH: "白细胞升高可能提示感染、炎症或其他血液疾病",
                IndicatorStatus.LOW: "白细胞降低可能与病毒感染、骨髓抑制等有关",
            },
            "血红蛋白": {
                IndicatorStatus.HIGH: "血红蛋白升高可能与脱水、慢性缺氧等有关",
                IndicatorStatus.LOW: "血红蛋白降低提示可能存在贫血",
            },
            "谷丙转氨酶": {
                IndicatorStatus.HIGH: "ALT升高可能提示肝细胞损伤",
                IndicatorStatus.LOW: "",
            },
            "空腹血糖": {
                IndicatorStatus.HIGH: "血糖升高可能与糖尿病或糖耐量异常有关",
                IndicatorStatus.LOW: "血糖偏低可能与饮食不足或某些疾病有关",
            },
            "总胆固醇": {
                IndicatorStatus.HIGH: "胆固醇升高是心血管疾病的风险因素",
                IndicatorStatus.LOW: "",
            },
        }
        
        if name in explanations:
            return explanations[name].get(status, "")
        
        if status == IndicatorStatus.HIGH:
            return f"{name}偏高，建议咨询医生"
        elif status == IndicatorStatus.LOW:
            return f"{name}偏低，建议咨询医生"
        elif status == IndicatorStatus.CRITICAL:
            return f"{name}为危急值，需要立即就医"
        
        return ""
    
    def _generate_summary(self, result: ReportAnalysisResult) -> str:
        """生成报告总结"""
        total = len(result.indicators)
        abnormal = result.abnormal_count
        critical = result.critical_count
        
        if critical > 0:
            return f"⚠️ 检出 {critical} 项危急值，请立即就医！共 {total} 项指标，{abnormal} 项异常。"
        elif abnormal > 0:
            return f"共 {total} 项指标，其中 {abnormal} 项异常，建议咨询医生。"
        else:
            return f"共 {total} 项指标，均在正常范围内。"
    
    def _generate_recommendations(self, result: ReportAnalysisResult) -> List[str]:
        """生成建议"""
        recommendations = []
        
        abnormal_names = [
            i.name for i in result.indicators
            if i.status != IndicatorStatus.NORMAL
        ]
        
        if result.critical_count > 0:
            recommendations.append("立即前往医院就诊")
            recommendations.append("携带本报告原件")
        
        if any("血糖" in n or "GLU" in n for n in abnormal_names):
            recommendations.append("控制饮食，减少糖分摄入")
            recommendations.append("定期监测血糖变化")
        
        if any("胆固醇" in n or "甘油三酯" in n for n in abnormal_names):
            recommendations.append("低脂饮食，适量运动")
            recommendations.append("考虑进一步检查心血管情况")
        
        if any("转氨酶" in n or "ALT" in n or "AST" in n for n in abnormal_names):
            recommendations.append("避免饮酒和油腻食物")
            recommendations.append("建议进行肝脏超声检查")
        
        if not recommendations and result.abnormal_count > 0:
            recommendations.append("建议将报告带给医生进行解读")
            recommendations.append("定期复查监测变化")
        
        return recommendations
    
    def _generate_warnings(self, result: ReportAnalysisResult) -> List[str]:
        """生成警告"""
        warnings = []
        
        for indicator in result.indicators:
            if indicator.status == IndicatorStatus.CRITICAL:
                warnings.append(f"⚠️ {indicator.name} 为危急值：{indicator.value}")
        
        return warnings
    
    def analyze_text_report(self, text: str) -> ReportAnalysisResult:
        """
        分析文本格式的报告（非图像）
        
        Args:
            text: 报告文本内容
            
        Returns:
            分析结果
        """
        report_id = generate_id("report_")
        indicators = []
        
        # 简单的正则提取
        patterns = [
            r"([^\d\s]+)[:\s]+(\d+\.?\d*)\s*([^\s\d]*)\s*[（(]?参考[值范围：:\s]*(\d+\.?\d*[-~]\d+\.?\d*)?",
            r"([A-Za-z]+)[:\s]+(\d+\.?\d*)\s*([^\s\d]*)",
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                name = match.group(1).strip()
                value = match.group(2).strip()
                unit = match.group(3).strip() if len(match.groups()) > 2 else ""
                ref_range = match.group(4).strip() if len(match.groups()) > 3 else ""
                
                indicators.append(IndicatorResult(
                    name=name,
                    value=value,
                    unit=unit,
                    reference_range=ref_range or "",
                ))
        
        result = ReportAnalysisResult(
            report_id=report_id,
            report_type=ReportType.UNKNOWN,
            indicators=indicators,
            raw_text=text,
        )
        
        return self._process_indicators(result)


# 单例
_report_analyzer: ReportAnalyzer = None


def get_report_analyzer() -> ReportAnalyzer:
    """获取报告分析器单例"""
    global _report_analyzer
    if _report_analyzer is None:
        _report_analyzer = ReportAnalyzer()
    return _report_analyzer
