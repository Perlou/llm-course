import { useState, useEffect, useCallback, useRef } from "react";
import {
  ArrowLeft,
  Upload,
  Trash2,
  Search,
  Loader2,
  FileText,
  CheckCircle,
  XCircle,
  Clock,
  Layers,
} from "lucide-react";
import { datasetApi } from "../../services/api";

interface Dataset {
  id: string;
  name: string;
  description: string | null;
  embedding_model: string;
  chunk_size: number;
  chunk_overlap: number;
  document_count: number;
  chunk_count: number;
}

interface Document {
  id: string;
  dataset_id: string;
  name: string;
  file_type: string;
  file_size: number | null;
  chunk_count: number;
  status: string;
  error_msg: string | null;
  created_at: string;
}

interface RetrieveResult {
  content: string;
  score: number;
  document_id: string;
  document_name: string;
  chunk_index: number;
}

interface Props {
  dataset: Dataset;
  onBack: () => void;
}

const STATUS_BADGES: Record<
  string,
  { icon: React.ReactNode; text: string; cls: string }
> = {
  pending: {
    icon: <Clock className="w-3 h-3" />,
    text: "等待处理",
    cls: "bg-amber-50 text-amber-600",
  },
  processing: {
    icon: <Loader2 className="w-3 h-3 animate-spin" />,
    text: "处理中",
    cls: "bg-blue-50 text-blue-600",
  },
  completed: {
    icon: <CheckCircle className="w-3 h-3" />,
    text: "已完成",
    cls: "bg-emerald-50 text-emerald-600",
  },
  failed: {
    icon: <XCircle className="w-3 h-3" />,
    text: "失败",
    cls: "bg-red-50 text-red-500",
  },
};

function formatSize(bytes: number | null): string {
  if (!bytes) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DatasetDetail({ dataset, onBack }: Props) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Retrieve state
  const [query, setQuery] = useState("");
  const [retrieving, setRetrieving] = useState(false);
  const [results, setResults] = useState<RetrieveResult[]>([]);

  const fetchDocuments = useCallback(async () => {
    try {
      setLoading(true);
      const data = await datasetApi.listDocuments(dataset.id);
      setDocuments(data as unknown as Document[]);
    } catch (err) {
      console.error("Failed to fetch documents", err);
    } finally {
      setLoading(false);
    }
  }, [dataset.id]);

  useEffect(() => {
    fetchDocuments();
    // 定时刷新处理中的文档状态
    const interval = setInterval(() => {
      fetchDocuments();
    }, 5000);
    return () => clearInterval(interval);
  }, [fetchDocuments]);

  const handleUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setUploading(true);
    try {
      for (const file of Array.from(files)) {
        await datasetApi.uploadDocument(dataset.id, file);
      }
      fetchDocuments();
    } catch (err) {
      console.error("Upload failed", err);
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    handleUpload(e.dataTransfer.files);
  };

  const handleDelete = async (docId: string) => {
    try {
      await datasetApi.deleteDocument(dataset.id, docId);
      setDeleteConfirm(null);
      fetchDocuments();
    } catch (err) {
      console.error("Delete failed", err);
    }
  };

  const handleRetrieve = async () => {
    if (!query.trim()) return;
    setRetrieving(true);
    setResults([]);
    try {
      const res = (await datasetApi.retrieve(dataset.id, {
        query: query.trim(),
        top_k: 5,
      })) as unknown as { results: RetrieveResult[] };
      setResults(res.results);
    } catch (err) {
      console.error("Retrieve failed", err);
    } finally {
      setRetrieving(false);
    }
  };

  const hasProcessingDocs = documents.some(
    (d) => d.status === "pending" || d.status === "processing"
  );

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={onBack}
          className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-500 hover:text-slate-700 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-slate-800">{dataset.name}</h1>
          {dataset.description && (
            <p className="text-sm text-slate-500 mt-0.5">
              {dataset.description}
            </p>
          )}
        </div>
        <div className="flex items-center gap-3 text-sm">
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-blue-50 text-blue-600">
            <FileText className="w-3.5 h-3.5" />
            {dataset.document_count} 文档
          </span>
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-purple-50 text-purple-600">
            <Layers className="w-3.5 h-3.5" />
            {dataset.chunk_count} 切片
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Documents */}
        <div className="lg:col-span-2 space-y-4">
          {/* Upload Area */}
          <div
            className={`border-2 border-dashed rounded-xl p-6 text-center transition-colors ${
              dragOver
                ? "border-indigo-400 bg-indigo-50/50"
                : "border-slate-200 hover:border-slate-300"
            }`}
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
          >
            {uploading ? (
              <div className="flex items-center justify-center gap-2 text-slate-500">
                <Loader2 className="w-5 h-5 animate-spin" />
                上传处理中...
              </div>
            ) : (
              <>
                <Upload className="w-8 h-8 mx-auto mb-2 text-slate-400" />
                <p className="text-sm text-slate-600">
                  拖拽文件到此处，或
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="text-indigo-500 hover:text-indigo-700 ml-1 font-medium"
                  >
                    点击上传
                  </button>
                </p>
                <p className="text-xs text-slate-400 mt-1">
                  支持 TXT、MD、PDF、DOCX 格式
                </p>
              </>
            )}
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".txt,.md,.pdf,.docx"
              className="hidden"
              onChange={(e) => handleUpload(e.target.files)}
            />
          </div>

          {/* Processing hint */}
          {hasProcessingDocs && (
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-50 text-blue-600 text-sm">
              <Loader2 className="w-4 h-4 animate-spin" />
              有文档正在处理中，页面将自动刷新状态...
            </div>
          )}

          {/* Document List */}
          {loading ? (
            <div className="flex items-center justify-center py-12 text-slate-400">
              <Loader2 className="w-5 h-5 animate-spin mr-2" />
              加载中...
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-12 text-slate-400 text-sm">
              暂无文档，上传文件开始构建知识库
            </div>
          ) : (
            <div className="space-y-2">
              {documents.map((doc) => {
                const badge = STATUS_BADGES[doc.status] || STATUS_BADGES.pending;
                return (
                  <div
                    key={doc.id}
                    className="flex items-center justify-between px-4 py-3 bg-white rounded-lg border border-slate-200 hover:shadow-sm transition-shadow relative"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <FileText className="w-5 h-5 text-slate-400 flex-shrink-0" />
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-slate-700 truncate">
                          {doc.name}
                        </p>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className="text-xs text-slate-400 uppercase">
                            {doc.file_type}
                          </span>
                          <span className="text-xs text-slate-400">
                            {formatSize(doc.file_size)}
                          </span>
                          {doc.chunk_count > 0 && (
                            <span className="text-xs text-slate-400">
                              {doc.chunk_count} 切片
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 flex-shrink-0">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs ${badge.cls}`}
                        title={doc.error_msg || undefined}
                      >
                        {badge.icon}
                        {badge.text}
                      </span>
                      <button
                        onClick={() => setDeleteConfirm(doc.id)}
                        className="p-1 rounded hover:bg-slate-100 text-slate-400 hover:text-red-500 transition-colors"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>

                    {/* Delete confirm */}
                    {deleteConfirm === doc.id && (
                      <div className="absolute inset-0 bg-white/95 rounded-lg flex items-center justify-center gap-3 z-10">
                        <span className="text-sm text-slate-600">确认删除？</span>
                        <button
                          onClick={() => setDeleteConfirm(null)}
                          className="px-2.5 py-1 text-xs rounded border border-slate-300 text-slate-600"
                        >
                          取消
                        </button>
                        <button
                          onClick={() => handleDelete(doc.id)}
                          className="px-2.5 py-1 text-xs rounded bg-red-500 text-white"
                        >
                          删除
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right: Retrieve Test */}
        <div className="space-y-4">
          <div className="card p-4">
            <h3 className="font-semibold text-sm text-slate-700 mb-3">
              🔍 检索测试
            </h3>
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleRetrieve()}
                placeholder="输入检索问题..."
                className="flex-1 px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400"
              />
              <button
                onClick={handleRetrieve}
                disabled={retrieving || !query.trim()}
                className="px-3 py-2 rounded-lg bg-indigo-500 text-white hover:bg-indigo-600 transition-colors disabled:opacity-50"
              >
                {retrieving ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Search className="w-4 h-4" />
                )}
              </button>
            </div>

            {/* Results */}
            {results.length > 0 && (
              <div className="space-y-2 max-h-[60vh] overflow-y-auto">
                {results.map((r, i) => (
                  <div
                    key={i}
                    className="p-3 rounded-lg bg-slate-50 border border-slate-200"
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-xs font-medium text-slate-600">
                        {r.document_name} · #{r.chunk_index}
                      </span>
                      <span className="text-xs text-indigo-500 font-mono">
                        {(r.score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <p className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed line-clamp-6">
                      {r.content}
                    </p>
                  </div>
                ))}
              </div>
            )}

            {results.length === 0 && !retrieving && query && (
              <p className="text-sm text-slate-400 text-center py-4">
                暂无结果
              </p>
            )}
          </div>

          {/* Config Info */}
          <div className="card p-4">
            <h3 className="font-semibold text-sm text-slate-700 mb-2">
              ⚙️ 配置信息
            </h3>
            <div className="space-y-1.5 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-500">Embedding 模型</span>
                <span className="text-slate-700 font-mono text-xs">
                  {dataset.embedding_model}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">切分大小</span>
                <span className="text-slate-700">{dataset.chunk_size}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">切分重叠</span>
                <span className="text-slate-700">{dataset.chunk_overlap}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
