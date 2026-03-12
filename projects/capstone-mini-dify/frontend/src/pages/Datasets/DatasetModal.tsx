import { useState } from "react";
import { X, Loader2 } from "lucide-react";
import { datasetApi } from "../../services/api";

interface Dataset {
  id: string;
  name: string;
  description: string | null;
  chunk_size: number;
  chunk_overlap: number;
}

interface Props {
  dataset: Dataset | null;
  onClose: () => void;
  onSave: () => void;
}

export default function DatasetModal({ dataset, onClose, onSave }: Props) {
  const isEdit = !!dataset;
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    name: dataset?.name || "",
    description: dataset?.description || "",
    chunk_size: dataset?.chunk_size || 500,
    chunk_overlap: dataset?.chunk_overlap || 50,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        name: form.name,
        description: form.description || undefined,
        chunk_size: form.chunk_size,
        chunk_overlap: form.chunk_overlap,
      };
      if (isEdit) {
        await datasetApi.update(dataset!.id, payload);
      } else {
        await datasetApi.create(payload);
      }
      onSave();
    } catch (err) {
      console.error("Save failed", err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <h2 className="text-lg font-semibold text-slate-800">
            {isEdit ? "编辑知识库" : "创建知识库"}
          </h2>
          <button
            onClick={onClose}
            className="p-1 rounded-md hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              名称
            </label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="例如：产品文档知识库"
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              描述
            </label>
            <textarea
              value={form.description}
              onChange={(e) =>
                setForm({ ...form, description: e.target.value })
              }
              placeholder="简述知识库用途..."
              rows={2}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 resize-y"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                切分大小
              </label>
              <input
                type="number"
                value={form.chunk_size}
                onChange={(e) =>
                  setForm({ ...form, chunk_size: parseInt(e.target.value) || 500 })
                }
                min={100}
                max={2000}
                className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400"
              />
              <p className="text-xs text-slate-400 mt-1">每个切片的字符数</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                切分重叠
              </label>
              <input
                type="number"
                value={form.chunk_overlap}
                onChange={(e) =>
                  setForm({
                    ...form,
                    chunk_overlap: parseInt(e.target.value) || 50,
                  })
                }
                min={0}
                max={500}
                className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400"
              />
              <p className="text-xs text-slate-400 mt-1">相邻切片重叠字符</p>
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm rounded-lg border border-slate-300 text-slate-600 hover:bg-slate-50 transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-4 py-2 text-sm rounded-lg bg-indigo-500 text-white hover:bg-indigo-600 transition-colors disabled:opacity-50 flex items-center gap-1.5"
            >
              {saving && <Loader2 className="w-4 h-4 animate-spin" />}
              {isEdit ? "保存" : "创建"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
