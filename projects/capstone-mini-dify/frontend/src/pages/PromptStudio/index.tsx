import { useState, useEffect, useCallback } from "react";
import {
  PenTool,
  Plus,
  Trash2,
  Edit,
  Tag,
  Loader2,
  Clock,
  X,
} from "lucide-react";
import { promptApi } from "../../services/api";
import PromptEditor from "./PromptEditor";

interface Prompt {
  id: string;
  name: string;
  description: string | null;
  system_prompt: string;
  user_prompt: string;
  variables: unknown[];
  tags: string[];
  current_version: number;
  created_at: string;
  updated_at: string;
}

export default function PromptStudioPage() {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterTag, setFilterTag] = useState<string | null>(null);
  const [editingPrompt, setEditingPrompt] = useState<Prompt | null>(null);
  const [creating, setCreating] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  const fetchPrompts = useCallback(async () => {
    try {
      setLoading(true);
      const data = await promptApi.list(filterTag || undefined);
      setPrompts(data as unknown as Prompt[]);
    } catch (err) {
      console.error("Failed to fetch prompts", err);
    } finally {
      setLoading(false);
    }
  }, [filterTag]);

  useEffect(() => {
    fetchPrompts();
  }, [fetchPrompts]);

  const handleDelete = async (id: string) => {
    try {
      await promptApi.delete(id);
      setDeleteConfirm(null);
      fetchPrompts();
    } catch (err) {
      console.error("Failed to delete prompt", err);
    }
  };

  // 收集所有 tags
  const allTags = Array.from(new Set(prompts.flatMap((p) => p.tags)));

  // 如果在编辑或创建模式
  if (editingPrompt || creating) {
    return (
      <PromptEditor
        prompt={editingPrompt}
        onClose={() => {
          setEditingPrompt(null);
          setCreating(false);
          fetchPrompts();
        }}
      />
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">✏️ Prompt 工坊</h1>
          <p className="text-sm text-slate-500 mt-1">
            创建和管理 Prompt 模板，支持变量注入和多模型测试
          </p>
        </div>
        <button
          onClick={() => setCreating(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          新建模板
        </button>
      </div>

      {/* Tag Filter */}
      {allTags.length > 0 && (
        <div className="flex items-center gap-2 mb-4 flex-wrap">
          <Tag className="w-4 h-4 text-slate-400" />
          <button
            onClick={() => setFilterTag(null)}
            className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
              !filterTag
                ? "bg-indigo-100 text-indigo-700"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            全部
          </button>
          {allTags.map((tag) => (
            <button
              key={tag}
              onClick={() => setFilterTag(tag)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                filterTag === tag
                  ? "bg-indigo-100 text-indigo-700"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {tag}
            </button>
          ))}
          {filterTag && (
            <button
              onClick={() => setFilterTag(null)}
              className="p-1 text-slate-400 hover:text-slate-600"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      )}

      {/* Prompt List */}
      {loading ? (
        <div className="flex items-center justify-center py-20 text-slate-400">
          <Loader2 className="w-6 h-6 animate-spin mr-2" />
          加载中...
        </div>
      ) : prompts.length === 0 ? (
        <div className="text-center py-20 text-slate-400">
          <PenTool className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>暂无 Prompt 模板</p>
          <p className="text-sm mt-1">点击"新建模板"创建第一个 Prompt</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {prompts.map((prompt) => (
            <div
              key={prompt.id}
              className="card p-5 group relative cursor-pointer hover:shadow-md transition-all duration-200"
              onClick={() => setEditingPrompt(prompt)}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold text-slate-800 line-clamp-1">
                  {prompt.name}
                </h3>
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 ml-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setEditingPrompt(prompt);
                    }}
                    className="p-1 rounded hover:bg-slate-100 text-slate-400 hover:text-indigo-500"
                    title="编辑"
                  >
                    <Edit className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setDeleteConfirm(prompt.id);
                    }}
                    className="p-1 rounded hover:bg-slate-100 text-slate-400 hover:text-red-500"
                    title="删除"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Description */}
              {prompt.description && (
                <p className="text-sm text-slate-500 line-clamp-2 mb-3">
                  {prompt.description}
                </p>
              )}

              {/* Prompt preview */}
              <div className="bg-slate-50 rounded-lg p-3 mb-3 text-xs text-slate-600 font-mono line-clamp-3">
                {prompt.user_prompt}
              </div>

              {/* Footer */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5 flex-wrap">
                  {prompt.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-0.5 rounded-full text-xs bg-indigo-50 text-indigo-600"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <span className="flex items-center gap-0.5">
                    <Clock className="w-3 h-3" />v{prompt.current_version}
                  </span>
                </div>
              </div>

              {/* Delete confirm overlay */}
              {deleteConfirm === prompt.id && (
                <div
                  className="absolute inset-0 bg-white/95 rounded-xl flex flex-col items-center justify-center gap-3 backdrop-blur-sm z-10"
                  onClick={(e) => e.stopPropagation()}
                >
                  <p className="text-sm text-slate-600">
                    确定删除 <strong>{prompt.name}</strong>？
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setDeleteConfirm(null)}
                      className="px-3 py-1.5 text-sm rounded-md border border-slate-300 text-slate-600 hover:bg-slate-50"
                    >
                      取消
                    </button>
                    <button
                      onClick={() => handleDelete(prompt.id)}
                      className="px-3 py-1.5 text-sm rounded-md bg-red-500 text-white hover:bg-red-600"
                    >
                      确认删除
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
