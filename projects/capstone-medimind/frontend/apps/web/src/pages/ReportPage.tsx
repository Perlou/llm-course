import { useState, useRef } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Upload, Camera, FileText, AlertCircle } from "lucide-react";
import { reportApi } from "@medimind/api-client";
import type { ReportAnalysisResponse, IndicatorItem } from "@medimind/types";
import { SafetyBanner, Card, Button, LabItemCard } from "@medimind/ui";
import { clsx } from "clsx";

export default function ReportPage() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<ReportAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = ["image/jpeg", "image/png", "image/jpg"];
    if (!validTypes.includes(file.type)) {
      setError("请上传 JPG 或 PNG 格式的图片");
      return;
    }

    // Create preview
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    setError(null);
    setResult(null);

    // Analyze
    await analyzeReport(file);
  };

  const analyzeReport = async (file: File) => {
    try {
      setIsAnalyzing(true);
      setError(null);
      const response = await reportApi.analyzeImage(file);
      setResult(response);
    } catch (err) {
      console.error("Analysis error:", err);
      setError("分析失败，请重试或上传更清晰的图片");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleReset = () => {
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // Count abnormal indicators
  const abnormalCount =
    result?.indicators.filter((i) => i.status !== "normal").length || 0;

  return (
    <div className="flex-1 flex flex-col max-w-2xl mx-auto w-full">
      {/* Header */}
      <div className="px-4 py-3 flex items-center gap-3 border-b border-border bg-white md:hidden">
        <Link
          to="/"
          className="p-1 -ml-1 text-text-secondary hover:text-text-primary"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <h1 className="font-semibold text-lg">报告解读</h1>
      </div>

      {/* Safety Banner */}
      <div className="px-4 py-3">
        <SafetyBanner variant="warning">
          报告解读仅供参考，具体诊断请咨询专业医生
        </SafetyBanner>
      </div>

      {/* Upload Area */}
      <div className="px-4 pb-4">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/jpg"
          onChange={handleFileSelect}
          className="hidden"
        />

        <Card
          className={clsx(
            "border-2 border-dashed transition-colors",
            previewUrl
              ? "border-medical-blue bg-blue-50/30"
              : "border-border hover:border-medical-blue",
          )}
        >
          {previewUrl ? (
            <div className="space-y-4">
              <img
                src={previewUrl}
                alt="报告预览"
                className="w-full max-h-64 object-contain rounded-lg"
              />
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  onClick={handleReset}
                  className="flex-1"
                >
                  重新上传
                </Button>
                {error && (
                  <Button onClick={() => analyzeReport} className="flex-1">
                    重试
                  </Button>
                )}
              </div>
            </div>
          ) : (
            <div
              className="py-12 flex flex-col items-center justify-center cursor-pointer"
              onClick={handleUploadClick}
            >
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-medical-blue/20 to-sky-100 flex items-center justify-center mb-4">
                <Camera className="w-8 h-8 text-medical-blue" />
              </div>
              <p className="text-text-primary font-medium">点击上传报告图片</p>
              <p className="text-sm text-text-muted mt-1">或拖拽文件至此处</p>
              <p className="text-xs text-text-muted mt-4">支持 JPG、PNG 格式</p>
            </div>
          )}
        </Card>
      </div>

      {/* Loading */}
      {isAnalyzing && (
        <div className="px-4 pb-4">
          <Card className="bg-blue-50">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full border-2 border-medical-blue border-t-transparent animate-spin" />
              <div>
                <p className="font-medium text-text-primary">正在分析报告...</p>
                <p className="text-sm text-text-secondary">
                  AI 正在识别指标并生成解读
                </p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="px-4 pb-4">
          <Card className="bg-red-50 border-red-200">
            <div className="flex items-center gap-2 text-alert-danger">
              <AlertCircle className="w-5 h-5" />
              <p>{error}</p>
            </div>
          </Card>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="flex-1 overflow-y-auto px-4 pb-24 md:pb-8">
          {/* Summary */}
          <div className="flex items-center gap-2 mb-4">
            <FileText className="w-5 h-5 text-medical-blue" />
            <h2 className="font-semibold text-lg">解读结果</h2>
          </div>

          {/* Abnormal Count */}
          {abnormalCount > 0 && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-alert-danger" />
              <span className="text-alert-danger font-medium">
                发现 {abnormalCount} 项异常指标
              </span>
            </div>
          )}

          {/* Indicators */}
          <div className="space-y-3">
            {result.indicators.map((indicator, index) => (
              <LabItemCard
                key={index}
                name={indicator.name}
                value={indicator.value}
                unit={indicator.unit}
                referenceRange={indicator.reference_range}
                status={
                  indicator.status as "normal" | "high" | "low" | "critical"
                }
                explanation={indicator.explanation}
              />
            ))}
          </div>

          {/* Summary */}
          {result.summary && (
            <Card className="mt-4 bg-blue-50">
              <h3 className="font-medium text-text-primary mb-2">综合解读</h3>
              <p className="text-sm text-text-secondary leading-relaxed">
                {result.summary}
              </p>
            </Card>
          )}

          {/* Recommendations */}
          {result.recommendations && result.recommendations.length > 0 && (
            <Card className="mt-4">
              <h3 className="font-medium text-text-primary mb-2">建议</h3>
              <ul className="space-y-2">
                {result.recommendations.map((rec, i) => (
                  <li
                    key={i}
                    className="text-sm text-text-secondary flex items-start gap-2"
                  >
                    <span className="text-medical-green">•</span>
                    {rec}
                  </li>
                ))}
              </ul>
            </Card>
          )}

          {/* Disclaimer */}
          <p className="text-xs text-text-muted mt-4 text-center">
            ⚕️ 以上解读仅供参考，如有疑问请咨询专业医生
          </p>
        </div>
      )}
    </div>
  );
}
