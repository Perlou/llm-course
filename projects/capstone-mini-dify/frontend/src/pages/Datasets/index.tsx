import { useState, useEffect, useCallback } from "react";
import {
  Database,
  Plus,
  Trash2,
  Edit,
  Loader2,
  FileText,
  Layers,
  Eye,
} from "lucide-react";
import { datasetApi } from "../../services/api";
import DatasetModal from "./DatasetModal";
import DatasetDetail from "./DatasetDetail";

interface Dataset {
  id: string;
  name: string;
  description: string | null;
  embedding_model: string;
  chunk_size: number;
  chunk_overlap: number;
  document_count: number;
  chunk_count: number;
  created_at: string;
  updated_at: string;
}

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingDataset, setEditingDataset] = useState<Dataset | null>(null);
  const [viewingDataset, setViewingDataset] = useState<Dataset | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  const fetchDatasets = useCallback(async () => {
    try {
      setLoading(true);
      const data = await datasetApi.list();
      setDatasets(data as unknown as Dataset[]);
    } catch (err) {
      console.error("Failed to fetch datasets", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDatasets();
  }, [fetchDatasets]);

  const handleDelete = async (id: string) => {
    try {
      await datasetApi.delete(id);
      setDeleteConfirm(null);
      fetchDatasets();
    } catch (err) {
      console.error("Failed to delete dataset", err);
    }
  };

  const handleSave = () => {
    setModalOpen(false);
    setEditingDataset(null);
    fetchDatasets();
  };

  // 详情页模式
  if (viewingDataset) {
    return (
      <DatasetDetail
        dataset={viewingDataset}
        onBack={() => {
          setViewingDataset(null);
          fetchDatasets();
        }}
      />
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">📚 知识库</h1>
          <p className="text-sm text-slate-500 mt-1">
            管理文档知识库，支持向量检索和 RAG 问答
          </p>
        </div>
        <button
          onClick={() => {
            setEditingDataset(null);
            setModalOpen(true);
          }}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          创建知识库
        </button>
      </div>

      {/* Dataset Cards */}
      {loading ? (
        <div className="flex items-center justify-center py-20 text-slate-400">
          <Loader2 className="w-6 h-6 animate-spin mr-2" />
          加载中...
        </div>
      ) : datasets.length === 0 ? (
        <div className="text-center py-20 text-slate-400">
          <Database className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>暂无知识库</p>
          <p className="text-sm mt-1">点击"创建知识库"开始</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {datasets.map((ds) => (
            <div
              key={ds.id}
              className="card p-5 group relative hover:shadow-md transition-all duration-200 cursor-pointer"
              onClick={() => setViewingDataset(ds)}
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center">
                    <Database className="w-5 h-5 text-emerald-500" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-800 line-clamp-1">
                      {ds.name}
                    </h3>
                    <span className="text-xs text-slate-400">
                      {ds.embedding_model}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setViewingDataset(ds);
                    }}
                    className="p-1.5 rounded-md hover:bg-slate-100 text-slate-400 hover:text-blue-500 transition-colors"
                    title="查看"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setEditingDataset(ds);
                      setModalOpen(true);
                    }}
                    className="p-1.5 rounded-md hover:bg-slate-100 text-slate-400 hover:text-indigo-500 transition-colors"
                    title="编辑"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setDeleteConfirm(ds.id);
                    }}
                    className="p-1.5 rounded-md hover:bg-slate-100 text-slate-400 hover:text-red-500 transition-colors"
                    title="删除"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Description */}
              {ds.description && (
                <p className="text-sm text-slate-500 line-clamp-2 mb-3">
                  {ds.description}
                </p>
              )}

              {/* Stats */}
              <div className="flex items-center gap-3">
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-blue-50 text-blue-600">
                  <FileText className="w-3 h-3" />
                  {ds.document_count} 文档
                </span>
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-purple-50 text-purple-600">
                  <Layers className="w-3 h-3" />
                  {ds.chunk_count} 切片
                </span>
              </div>

              {/* Config info */}
              <div className="mt-3 text-xs text-slate-400">
                切分: {ds.chunk_size} / 重叠: {ds.chunk_overlap}
              </div>

              {/* Delete confirm overlay */}
              {deleteConfirm === ds.id && (
                <div
                  className="absolute inset-0 bg-white/95 rounded-xl flex flex-col items-center justify-center gap-3 backdrop-blur-sm z-10"
                  onClick={(e) => e.stopPropagation()}
                >
                  <p className="text-sm text-slate-600">
                    确定删除 <strong>{ds.name}</strong>？
                  </p>
                  <p className="text-xs text-slate-400">
                    将同时删除所有文档和向量数据
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setDeleteConfirm(null)}
                      className="px-3 py-1.5 text-sm rounded-md border border-slate-300 text-slate-600 hover:bg-slate-50"
                    >
                      取消
                    </button>
                    <button
                      onClick={() => handleDelete(ds.id)}
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

      {/* Modal */}
      {modalOpen && (
        <DatasetModal
          dataset={editingDataset}
          onClose={() => {
            setModalOpen(false);
            setEditingDataset(null);
          }}
          onSave={handleSave}
        />
      )}
    </div>
  );
}
