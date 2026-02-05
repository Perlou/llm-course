import { useNavigate } from "react-router-dom";
import {
  MessageCircle,
  Pill,
  FileText,
  Stethoscope,
  Mic,
  Send,
  Bot,
  MapPin,
  Bell,
} from "lucide-react";
import { SafetyBanner, FeatureCard, Input, Button } from "@medimind/ui";
import { useState } from "react";

export default function HomePage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/health?q=${encodeURIComponent(query)}`);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      {/* Safety Banner */}
      <div className="px-4 py-3">
        <SafetyBanner variant="warning">
          本服务仅提供健康科普，不能替代医生诊断
        </SafetyBanner>
      </div>

      {/* Welcome Section */}
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-8">
        {/* Avatar */}
        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-medical-blue to-medical-green flex items-center justify-center mb-4 shadow-lg">
          <Bot className="w-10 h-10 text-white" />
        </div>

        {/* Welcome Text */}
        <h1 className="text-2xl font-bold text-text-primary text-center">
          您好！
        </h1>
        <p className="text-lg text-text-primary text-center mt-1">
          我是<span className="text-medical-blue font-semibold">健康助手</span>
        </p>
        <p className="text-text-secondary text-center mt-2">
          有任何健康问题，都可以问我哦 💬
        </p>

        {/* Search Input */}
        <form onSubmit={handleSubmit} className="w-full max-w-md mt-6">
          <div className="relative">
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="请输入您的问题..."
              className="pr-24"
            />
            <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
              <button
                type="button"
                className="p-2 text-text-muted hover:text-medical-blue transition-colors"
              >
                <Mic className="w-5 h-5" />
              </button>
              <Button type="submit" size="sm" className="rounded-lg">
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </form>
      </div>

      {/* Feature Cards */}
      <div className="px-4 pb-24 md:pb-8">
        <div className="grid grid-cols-2 gap-3 max-w-md mx-auto">
          <FeatureCard
            icon={<MessageCircle className="w-6 h-6" />}
            title="健康问答"
            titleEn="Health Q&A"
            description="快速查找健康知识，为您解答常见问题。"
            color="blue"
            onClick={() => navigate("/health")}
          />
          <FeatureCard
            icon={<Pill className="w-6 h-6" />}
            title="药品查询"
            titleEn="Drug Search"
            description="查询药品信息，了解用法用量及禁忌。"
            color="green"
            onClick={() => navigate("/drug")}
          />
          <FeatureCard
            icon={<FileText className="w-6 h-6" />}
            title="报告解读"
            titleEn="Report Analysis"
            description="上传检查报告，智能辅助解读结果。"
            color="purple"
            onClick={() => navigate("/report")}
          />
          <FeatureCard
            icon={<Stethoscope className="w-6 h-6" />}
            title="智能导诊"
            titleEn="Smart Triage"
            description="基于症状智能评估，推荐就医科室。"
            color="orange"
            onClick={() => navigate("/triage")}
          />
          <FeatureCard
            icon={<MapPin className="w-6 h-6" />}
            title="附近医院"
            titleEn="Nearby Hospitals"
            description="基于位置搜索附近医院，导航就诊。"
            color="blue"
            onClick={() => navigate("/hospital")}
          />
          <FeatureCard
            icon={<Bell className="w-6 h-6" />}
            title="提醒管理"
            titleEn="Reminders"
            description="设置用药、测量、复查提醒，管理健康。"
            color="orange"
            onClick={() => navigate("/reminder")}
          />
        </div>
      </div>
    </div>
  );
}
