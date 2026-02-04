import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Search, ArrowLeft, X, AlertTriangle } from "lucide-react";
import { drugApi } from "@medimind/api-client";
import type { DrugInfo, InteractionResult } from "@medimind/types";
import { Input, Button, DrugCard, Card, SafetyBanner } from "@medimind/ui";
import { clsx } from "clsx";

export default function DrugSearchPage() {
  const [query, setQuery] = useState("");
  const [drugs, setDrugs] = useState<DrugInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDrug, setSelectedDrug] = useState<DrugInfo | null>(null);

  // Interaction check
  const [selectedDrugs, setSelectedDrugs] = useState<string[]>([]);
  const [interactions, setInteractions] = useState<InteractionResult[]>([]);
  const [isCheckingInteraction, setIsCheckingInteraction] = useState(false);

  // Load drug list on mount
  useEffect(() => {
    loadDrugs();
  }, []);

  const loadDrugs = async () => {
    try {
      setIsLoading(true);
      const result = await drugApi.list(20, 0);
      setDrugs(result.drugs);
    } catch (error) {
      console.error("Load drugs error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) {
      loadDrugs();
      return;
    }

    try {
      setIsLoading(true);
      const result = await drugApi.search(query);
      setDrugs(result.drugs);
    } catch (error) {
      console.error("Search error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDrugClick = async (drug: DrugInfo) => {
    try {
      const detail = await drugApi.getDetail(drug.id);
      setSelectedDrug(detail);
    } catch (error) {
      setSelectedDrug(drug);
    }
  };

  const handleInteractionCheck = async () => {
    if (selectedDrugs.length < 2) return;

    try {
      setIsCheckingInteraction(true);
      const result = await drugApi.checkInteraction(selectedDrugs);
      setInteractions(result.interactions);
    } catch (error) {
      console.error("Interaction check error:", error);
    } finally {
      setIsCheckingInteraction(false);
    }
  };

  const toggleDrugSelection = (drugName: string) => {
    setSelectedDrugs((prev) =>
      prev.includes(drugName)
        ? prev.filter((d) => d !== drugName)
        : [...prev, drugName],
    );
    setInteractions([]);
  };

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
        <h1 className="font-semibold text-lg">药品查询</h1>
      </div>

      {/* Safety Banner */}
      <div className="px-4 py-3">
        <SafetyBanner variant="warning">
          药品信息仅供参考，用药请遵医嘱
        </SafetyBanner>
      </div>

      {/* Search */}
      <div className="px-4 pb-3">
        <form onSubmit={handleSearch} className="flex gap-2">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="搜索药品名称或适应症..."
            leftIcon={<Search className="w-4 h-4" />}
            containerClassName="flex-1"
          />
          <Button type="submit" disabled={isLoading}>
            搜索
          </Button>
        </form>
      </div>

      {/* Interaction Check Section */}
      {selectedDrugs.length > 0 && (
        <div className="px-4 pb-3">
          <Card className="bg-slate-50">
            <p className="text-sm text-text-secondary mb-2">
              已选择药品进行相互作用检查：
            </p>
            <div className="flex flex-wrap gap-2 mb-3">
              {selectedDrugs.map((name) => (
                <span
                  key={name}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-white border border-border rounded-full text-sm"
                >
                  {name}
                  <button
                    onClick={() => toggleDrugSelection(name)}
                    className="p-0.5 hover:text-alert-danger"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
            <Button
              size="sm"
              onClick={handleInteractionCheck}
              disabled={selectedDrugs.length < 2 || isCheckingInteraction}
              isLoading={isCheckingInteraction}
            >
              检查药物相互作用
            </Button>

            {/* Interaction Results */}
            {interactions.length > 0 && (
              <div className="mt-3 space-y-2">
                {interactions.map((interaction, i) => (
                  <div
                    key={i}
                    className={clsx(
                      "p-3 rounded-lg border",
                      interaction.severity === "high"
                        ? "bg-red-50 border-red-200"
                        : interaction.severity === "medium"
                          ? "bg-orange-50 border-orange-200"
                          : "bg-yellow-50 border-yellow-200",
                    )}
                  >
                    <div className="flex items-center gap-2 font-medium">
                      <AlertTriangle className="w-4 h-4" />
                      {interaction.drug1} + {interaction.drug2}
                    </div>
                    <p className="text-sm mt-1">{interaction.description}</p>
                    <p className="text-sm text-text-secondary mt-1">
                      建议：{interaction.recommendation}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      )}

      {/* Drug List */}
      <div className="flex-1 overflow-y-auto px-4 pb-24 md:pb-8">
        {isLoading ? (
          <div className="text-center py-8 text-text-muted">加载中...</div>
        ) : drugs.length === 0 ? (
          <div className="text-center py-8 text-text-muted">未找到相关药品</div>
        ) : (
          <div className="space-y-3">
            {drugs.map((drug) => (
              <div key={drug.id} className="relative">
                <DrugCard
                  id={drug.id}
                  name={drug.name}
                  genericName={drug.generic_name}
                  category={drug.category}
                  isOtc={drug.is_otc}
                  indications={drug.indications}
                  onClick={() => handleDrugClick(drug)}
                />
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleDrugSelection(drug.name);
                  }}
                  className={clsx(
                    "absolute top-3 right-3 w-5 h-5 rounded border-2 transition-colors",
                    selectedDrugs.includes(drug.name)
                      ? "bg-medical-blue border-medical-blue"
                      : "border-border bg-white hover:border-medical-blue",
                  )}
                >
                  {selectedDrugs.includes(drug.name) && (
                    <span className="text-white text-xs">✓</span>
                  )}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Drug Detail Modal */}
      {selectedDrug && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <Card className="w-full max-w-lg max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">{selectedDrug.name}</h2>
              <button
                onClick={() => setSelectedDrug(null)}
                className="p-1 text-text-muted hover:text-text-primary"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              {selectedDrug.generic_name && (
                <div>
                  <h3 className="text-sm font-medium text-text-secondary">
                    通用名
                  </h3>
                  <p>{selectedDrug.generic_name}</p>
                </div>
              )}
              {selectedDrug.indications && (
                <div>
                  <h3 className="text-sm font-medium text-text-secondary">
                    适应症
                  </h3>
                  <p>{selectedDrug.indications}</p>
                </div>
              )}
              {selectedDrug.dosage && (
                <div>
                  <h3 className="text-sm font-medium text-text-secondary">
                    用法用量
                  </h3>
                  <p>{selectedDrug.dosage}</p>
                </div>
              )}
              {selectedDrug.side_effects && (
                <div>
                  <h3 className="text-sm font-medium text-text-secondary">
                    不良反应
                  </h3>
                  <p>{selectedDrug.side_effects}</p>
                </div>
              )}
              {selectedDrug.contraindications && (
                <div>
                  <h3 className="text-sm font-medium text-text-secondary">
                    禁忌
                  </h3>
                  <p>{selectedDrug.contraindications}</p>
                </div>
              )}
              {selectedDrug.precautions && (
                <div>
                  <h3 className="text-sm font-medium text-text-secondary">
                    注意事项
                  </h3>
                  <p>{selectedDrug.precautions}</p>
                </div>
              )}
            </div>

            <div className="mt-6 pt-4 border-t border-border">
              <p className="text-xs text-text-muted">
                ⚕️ 药品信息仅供参考，用药请遵医嘱。
              </p>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
