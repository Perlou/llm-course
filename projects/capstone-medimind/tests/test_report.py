"""
MediMind - 报告分析测试
"""

import pytest

from src.core.report_analyzer import (
    ReportAnalyzer,
    ReportAnalysisResult,
    IndicatorResult,
    IndicatorStatus,
    ReportType,
    ImagePreprocessor,
    REFERENCE_RANGES,
    get_report_analyzer,
)


class TestIndicatorResult:
    """指标结果测试"""

    def test_create_indicator(self):
        """测试创建指标"""
        indicator = IndicatorResult(
            name="血红蛋白",
            value="145",
            unit="g/L",
            reference_range="120-160",
            status=IndicatorStatus.NORMAL,
        )
        
        assert indicator.name == "血红蛋白"
        assert indicator.value == "145"
        assert indicator.status == IndicatorStatus.NORMAL

    def test_indicator_to_dict(self):
        """测试指标序列化"""
        indicator = IndicatorResult(
            name="白细胞计数",
            value="12.5",
            unit="10^9/L",
            status=IndicatorStatus.HIGH,
            explanation="白细胞升高可能提示感染",
        )
        
        data = indicator.to_dict()
        
        assert data["name"] == "白细胞计数"
        assert data["value"] == "12.5"
        assert data["status"] == "high"


class TestReportAnalysisResult:
    """分析结果测试"""

    def test_create_result(self):
        """测试创建结果"""
        result = ReportAnalysisResult(
            report_id="test_123",
            report_type=ReportType.BLOOD_TEST,
        )
        
        assert result.report_id == "test_123"
        assert result.report_type == ReportType.BLOOD_TEST
        assert result.abnormal_count == 0

    def test_abnormal_count(self):
        """测试异常计数"""
        result = ReportAnalysisResult(
            report_id="test_456",
            report_type=ReportType.LIVER_FUNCTION,
            indicators=[
                IndicatorResult(name="ALT", value="45", status=IndicatorStatus.HIGH),
                IndicatorResult(name="AST", value="30", status=IndicatorStatus.NORMAL),
                IndicatorResult(name="TBIL", value="25", status=IndicatorStatus.HIGH),
            ],
        )
        
        assert result.abnormal_count == 2
        assert result.critical_count == 0

    def test_critical_count(self):
        """测试危急值计数"""
        result = ReportAnalysisResult(
            report_id="test_789",
            report_type=ReportType.BLOOD_TEST,
            indicators=[
                IndicatorResult(name="HGB", value="55", status=IndicatorStatus.CRITICAL),
                IndicatorResult(name="WBC", value="35", status=IndicatorStatus.CRITICAL),
            ],
        )
        
        assert result.critical_count == 2

    def test_result_to_dict(self):
        """测试结果序列化"""
        result = ReportAnalysisResult(
            report_id="test_abc",
            report_type=ReportType.BLOOD_SUGAR,
            patient_info={"name": "测试"},
            test_date="2026-01-15",
            summary="检测正常",
        )
        
        data = result.to_dict()
        
        assert data["report_id"] == "test_abc"
        assert data["report_type"] == "blood_sugar"
        assert data["patient_info"]["name"] == "测试"


class TestImagePreprocessor:
    """图像预处理测试"""

    def test_get_mime_type_jpg(self):
        """测试获取 JPG MIME 类型"""
        mime = ImagePreprocessor.get_mime_type("report.jpg")
        assert mime == "image/jpeg"

    def test_get_mime_type_png(self):
        """测试获取 PNG MIME 类型"""
        mime = ImagePreprocessor.get_mime_type("report.png")
        assert mime == "image/png"

    def test_get_mime_type_pdf(self):
        """测试获取 PDF MIME 类型"""
        mime = ImagePreprocessor.get_mime_type("report.pdf")
        assert mime == "application/pdf"

    def test_encode_image_bytes(self):
        """测试编码图像字节"""
        test_bytes = b"test image data"
        encoded = ImagePreprocessor.encode_image(test_bytes)
        
        assert isinstance(encoded, str)
        assert len(encoded) > 0


class TestReportAnalyzer:
    """报告分析器测试"""

    @pytest.fixture
    def analyzer(self):
        return ReportAnalyzer()

    def test_find_reference_direct(self, analyzer):
        """测试直接查找参考值"""
        ref = analyzer._find_reference("白细胞计数")
        
        assert ref is not None
        assert ref["min"] == 4.0
        assert ref["max"] == 10.0

    def test_find_reference_alias(self, analyzer):
        """测试别名查找参考值"""
        ref = analyzer._find_reference("WBC")
        
        assert ref is not None
        assert ref["unit"] == "10^9/L"

    def test_find_reference_not_found(self, analyzer):
        """测试查找不存在的参考值"""
        ref = analyzer._find_reference("不存在的指标")
        
        assert ref is None

    def test_check_status_normal(self, analyzer):
        """测试正常状态判断"""
        ref = {"min": 4.0, "max": 10.0, "unit": "10^9/L"}
        status = analyzer._check_status("白细胞计数", "6.5", ref)
        
        assert status == IndicatorStatus.NORMAL

    def test_check_status_high(self, analyzer):
        """测试偏高状态判断"""
        ref = {"min": 4.0, "max": 10.0, "unit": "10^9/L"}
        status = analyzer._check_status("白细胞计数", "12.5", ref)
        
        assert status == IndicatorStatus.HIGH

    def test_check_status_low(self, analyzer):
        """测试偏低状态判断"""
        ref = {"min": 4.0, "max": 10.0, "unit": "10^9/L"}
        status = analyzer._check_status("白细胞计数", "2.5", ref)
        
        assert status == IndicatorStatus.LOW

    def test_check_status_critical(self, analyzer):
        """测试危急值判断"""
        ref = {"min": 4.0, "max": 10.0, "unit": "10^9/L"}
        status = analyzer._check_status("白细胞计数", "35.0", ref)
        
        assert status == IndicatorStatus.CRITICAL

    def test_generate_summary_normal(self, analyzer):
        """测试生成正常总结"""
        result = ReportAnalysisResult(
            report_id="test",
            report_type=ReportType.BLOOD_TEST,
            indicators=[
                IndicatorResult(name="WBC", value="6.5", status=IndicatorStatus.NORMAL),
            ],
        )
        
        summary = analyzer._generate_summary(result)
        
        assert "正常" in summary

    def test_generate_summary_abnormal(self, analyzer):
        """测试生成异常总结"""
        result = ReportAnalysisResult(
            report_id="test",
            report_type=ReportType.BLOOD_TEST,
            indicators=[
                IndicatorResult(name="WBC", value="12.5", status=IndicatorStatus.HIGH),
                IndicatorResult(name="HGB", value="145", status=IndicatorStatus.NORMAL),
            ],
        )
        
        summary = analyzer._generate_summary(result)
        
        assert "异常" in summary

    def test_analyze_text_report(self, analyzer):
        """测试分析文本报告"""
        text = """
        检验报告
        白细胞计数: 6.5 10^9/L (参考值: 4.0-10.0)
        血红蛋白: 145 g/L (参考值: 120-160)
        """
        
        result = analyzer.analyze_text_report(text)
        
        assert result.report_id.startswith("report_")
        # 文本解析可能提取到部分指标
        assert isinstance(result.indicators, list)


class TestReferenceRanges:
    """参考范围测试"""

    def test_reference_ranges_exist(self):
        """测试参考范围存在"""
        assert len(REFERENCE_RANGES) > 0
        assert "白细胞计数" in REFERENCE_RANGES
        assert "血红蛋白" in REFERENCE_RANGES

    def test_reference_range_structure(self):
        """测试参考范围结构"""
        ref = REFERENCE_RANGES["白细胞计数"]
        
        assert "min" in ref
        assert "max" in ref
        assert "unit" in ref
        assert "alias" in ref


class TestGetReportAnalyzer:
    """测试获取单例"""

    def test_singleton(self):
        """测试单例模式"""
        analyzer1 = get_report_analyzer()
        analyzer2 = get_report_analyzer()
        
        assert analyzer1 is analyzer2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
