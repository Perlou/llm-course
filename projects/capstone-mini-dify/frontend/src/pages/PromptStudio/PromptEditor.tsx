import { useState, useEffect, useMemo, useCallback } from "react";
import {
  ArrowLeft,
  Save,
  Loader2,
  Play,
  History,
  RotateCcw,
  X,
} from "lucide-react";
import { promptApi, providerApi } from "../../services/api";
import PromptTestPanel from "./PromptTestPanel";

interface Prompt {
  id: string;
  name: string;
  description: string | null;
  system_prompt: string;
  user_prompt: string;
  variables: unknown[];
  tags: string[];
  current_version: number;
}

interface PromptVersion {
  id: string;
  prompt_id: string;
  version: number;
  system_prompt: string;
  user_prompt: string;
  change_note: string | null;
  created_at: string;
}

interface Provider {
  id: string;
  name: string;
  provider_type: string;
  models: string[];
  is_active: boolean;
}

interface Props {
  prompt: Prompt | null; // null = creating
  onClose: () => void;
}

export default function PromptEditor({ prompt, onClose }: Props) {
  const isNew = !prompt;
  const [saving, setSaving] = useState(false);
  const [showVersions, setShowVersions] = useState(false);
  const [showTest, setShowTest] = useState(false);
  const [versions, setVersions] = useState<PromptVersion[]>([]);
  const [providers, setProviders] = useState<Provider[]>([]);

  const [form, setForm] = useState({
    name: prompt?.name || "",
    description: prompt?.description || "",
    system_prompt: prompt?.system_prompt || "你是一个有用的助手。",
    user_prompt: prompt?.user_prompt || "",
    tags_str: prompt?.tags?.join(",") || "",
  });

  // 自动提取 {{var}} 变量
  const detectedVars = useMemo(() => {
    const allText = form.system_prompt + " " + form.user_prompt;
    const matches = allText.match(/\{\{(\w+)\}\}/g);
    if (!matches) return [];
    return Array.from(new Set(matches.map((m) => m.replace(/\{|\}/g, ""))));
  }, [form.system_prompt, form.user_prompt]);

  // 加载版本历史和供应商列表
  const loadData = useCallback(async () => {
    if (prompt) {
      try {
        const v = await promptApi.versions(prompt.id);
        setVersions(v as unknown as PromptVersion[]);
      } catch (e) {
        console.error(e);
      }
    }
    try {
      const p = await providerApi.list();
      setProviders(p as unknown as Provider[]);
    } catch (e) {
      console.error(e);
    }
  }, [prompt]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const payload = {
        name: form.name,
        description: form.description || undefined,
        system_prompt: form.system_prompt,
        user_prompt: form.user_prompt,
        tags: form.tags_str
          .split(",")
          .map((t) => t.trim())
          .filter(Boolean),
      };
      if (isNew) {
        await promptApi.create(payload);
      } else {
        await promptApi.update(prompt!.id, payload);
      }
      onClose();
    } catch (err) {
      console.error("Save failed", err);
    } finally {
      setSaving(false);
    }
  };

  const handleRollback = async (version: number) => {
    if (!prompt) return;
    try {
      const updated = (await promptApi.rollback(
        prompt.id,
        version,
      )) as unknown as Prompt;
      setForm({
        name: updated.name,
        description: updated.description || "",
        system_prompt: updated.system_prompt,
        user_prompt: updated.user_prompt,
        tags_str: updated.tags?.join(",") || "",
      });
      setShowVersions(false);
      loadData();
    } catch (err) {
      console.error("Rollback failed", err);
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header Bar */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-slate-200 bg-white flex-shrink-0">
        <div className="flex items-center gap-3">
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-500 hover:text-slate-700 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <input
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            placeholder="输入模板名称..."
            className="text-lg font-semibold text-slate-800 bg-transparent border-none focus:outline-none focus:ring-0 placeholder-slate-300 w-60"
          />
          {!isNew && (
            <span className="text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded">
              v{prompt!.current_version}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {!isNew && (
            <>
              <button
                onClick={() => setShowVersions(!showVersions)}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg border transition-colors ${
                  showVersions
                    ? "border-indigo-300 bg-indigo-50 text-indigo-600"
                    : "border-slate-200 text-slate-600 hover:border-slate-300"
                }`}
              >
                <History className="w-4 h-4" />
                版本
              </button>
              <button
                onClick={() => setShowTest(!showTest)}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg border transition-colors ${
                  showTest
                    ? "border-emerald-300 bg-emerald-50 text-emerald-600"
                    : "border-slate-200 text-slate-600 hover:border-slate-300"
                }`}
              >
                <Play className="w-4 h-4" />
                测试
              </button>
            </>
          )}
          <button
            onClick={handleSave}
            disabled={saving || !form.name || !form.system_prompt}
            className="flex items-center gap-1.5 px-4 py-1.5 text-sm rounded-lg bg-indigo-500 text-white hover:bg-indigo-600 transition-colors disabled:opacity-50"
          >
            {saving ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            {isNew ? "创建" : "保存"}
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Editor */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              描述
            </label>
            <input
              value={form.description}
              onChange={(e) =>
                setForm({ ...form, description: e.target.value })
              }
              placeholder="简述该模板的用途..."
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400"
            />
          </div>

          {/* System Prompt */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              System Prompt
            </label>
            <textarea
              value={form.system_prompt}
              onChange={(e) =>
                setForm({ ...form, system_prompt: e.target.value })
              }
              placeholder="定义 AI 的角色和行为..."
              rows={5}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 resize-y"
            />
          </div>

          {/* User Prompt */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              User Prompt 模板
              <span className="text-slate-400 font-normal ml-2">
                使用 {"{{变量名}}"} 注入变量
              </span>
            </label>
            <textarea
              value={form.user_prompt}
              onChange={(e) =>
                setForm({ ...form, user_prompt: e.target.value })
              }
              placeholder={"请翻译以下文本：\n\n{{text}}"}
              rows={8}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 resize-y"
            />
          </div>

          {/* Detected Variables */}
          {detectedVars.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                检测到的变量
              </label>
              <div className="flex flex-wrap gap-2">
                {detectedVars.map((v) => (
                  <span
                    key={v}
                    className="px-3 py-1 rounded-full text-xs bg-amber-50 text-amber-700 border border-amber-200 font-mono"
                  >
                    {`{{${v}}}`}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Tags */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              标签
              <span className="text-slate-400 font-normal ml-1">
                (逗号分隔)
              </span>
            </label>
            <input
              value={form.tags_str}
              onChange={(e) => setForm({ ...form, tags_str: e.target.value })}
              placeholder="翻译,多语言"
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400"
            />
          </div>
        </div>

        {/* Version History Sidebar */}
        {showVersions && !isNew && (
          <div className="w-80 border-l border-slate-200 bg-slate-50 overflow-y-auto flex-shrink-0">
            <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200">
              <h3 className="font-semibold text-sm text-slate-700">版本历史</h3>
              <button
                onClick={() => setShowVersions(false)}
                className="p-1 rounded hover:bg-slate-200 text-slate-400"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="p-3 space-y-2">
              {versions.length === 0 ? (
                <p className="text-sm text-slate-400 text-center py-4">
                  暂无版本记录
                </p>
              ) : (
                versions.map((ver) => (
                  <div
                    key={ver.id}
                    className="bg-white rounded-lg p-3 border border-slate-200 text-sm"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-slate-700">
                        v{ver.version}
                      </span>
                      <button
                        onClick={() => handleRollback(ver.version)}
                        className="flex items-center gap-1 text-xs text-indigo-500 hover:text-indigo-700"
                        title="回滚到此版本"
                      >
                        <RotateCcw className="w-3 h-3" />
                        回滚
                      </button>
                    </div>
                    {ver.change_note && (
                      <p className="text-xs text-slate-500">
                        {ver.change_note}
                      </p>
                    )}
                    <p className="text-xs text-slate-400 mt-1">
                      {new Date(ver.created_at).toLocaleString("zh-CN")}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Test Panel */}
        {showTest && !isNew && prompt && (
          <PromptTestPanel
            promptId={prompt.id}
            variables={detectedVars}
            providers={providers}
            onClose={() => setShowTest(false)}
          />
        )}
      </div>
    </div>
  );
}
