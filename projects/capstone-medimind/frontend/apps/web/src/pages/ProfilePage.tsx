import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { profileApi } from "@medimind/api-client";
import { Button, Input, Card } from "@medimind/ui";

/**
 * 健康档案页面
 */
export function ProfilePage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<profileApi.HealthProfile | null>(null);
  const [records, setRecords] = useState<profileApi.HealthRecord[]>([]);
  const [isEditing, setIsEditing] = useState(false);

  // 表单状态
  const [gender, setGender] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [heightCm, setHeightCm] = useState("");
  const [weightKg, setWeightKg] = useState("");
  const [bloodType, setBloodType] = useState("");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [profileData, recordsData] = await Promise.all([
        profileApi.getProfile(),
        profileApi.getRecords({ limit: 10 }),
      ]);
      setProfile(profileData);
      setRecords(recordsData.records);

      // 填充表单
      if (profileData) {
        setGender(profileData.gender || "");
        setBirthDate(profileData.birth_date || "");
        setHeightCm(profileData.height_cm?.toString() || "");
        setWeightKg(profileData.weight_kg?.toString() || "");
        setBloodType(profileData.blood_type || "");
      }
    } catch (error) {
      console.error("加载数据失败:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      await profileApi.updateProfile({
        gender: gender || undefined,
        birth_date: birthDate || undefined,
        height_cm: heightCm ? parseFloat(heightCm) : undefined,
        weight_kg: weightKg ? parseFloat(weightKg) : undefined,
        blood_type: bloodType || undefined,
      });
      setIsEditing(false);
      await loadData();
    } catch (error) {
      console.error("保存失败:", error);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-gray-500">加载中...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* 标题 */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">健康档案</h1>
        <Button variant="secondary" onClick={() => navigate("/")}>
          返回首页
        </Button>
      </div>

      {/* 基本信息 */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">基本信息</h2>
          {!isEditing && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setIsEditing(true)}
            >
              编辑
            </Button>
          )}
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm text-gray-500 mb-1">性别</label>
            {isEditing ? (
              <select
                value={gender}
                onChange={(e) => setGender(e.target.value)}
                className="w-full border rounded-lg px-3 py-2"
              >
                <option value="">请选择</option>
                <option value="male">男</option>
                <option value="female">女</option>
              </select>
            ) : (
              <p className="font-medium">
                {gender === "male" ? "男" : gender === "female" ? "女" : "-"}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm text-gray-500 mb-1">出生日期</label>
            {isEditing ? (
              <Input
                type="date"
                value={birthDate}
                onChange={(e) => setBirthDate(e.target.value)}
              />
            ) : (
              <p className="font-medium">{birthDate || "-"}</p>
            )}
          </div>

          <div>
            <label className="block text-sm text-gray-500 mb-1">
              身高 (cm)
            </label>
            {isEditing ? (
              <Input
                type="number"
                value={heightCm}
                onChange={(e) => setHeightCm(e.target.value)}
              />
            ) : (
              <p className="font-medium">{heightCm || "-"}</p>
            )}
          </div>

          <div>
            <label className="block text-sm text-gray-500 mb-1">
              体重 (kg)
            </label>
            {isEditing ? (
              <Input
                type="number"
                value={weightKg}
                onChange={(e) => setWeightKg(e.target.value)}
              />
            ) : (
              <p className="font-medium">{weightKg || "-"}</p>
            )}
          </div>

          <div>
            <label className="block text-sm text-gray-500 mb-1">血型</label>
            {isEditing ? (
              <select
                value={bloodType}
                onChange={(e) => setBloodType(e.target.value)}
                className="w-full border rounded-lg px-3 py-2"
              >
                <option value="">请选择</option>
                <option value="A">A 型</option>
                <option value="B">B 型</option>
                <option value="AB">AB 型</option>
                <option value="O">O 型</option>
              </select>
            ) : (
              <p className="font-medium">
                {bloodType ? `${bloodType} 型` : "-"}
              </p>
            )}
          </div>
        </div>

        {isEditing && (
          <div className="flex gap-2 mt-4">
            <Button onClick={handleSave}>保存</Button>
            <Button variant="secondary" onClick={() => setIsEditing(false)}>
              取消
            </Button>
          </div>
        )}
      </Card>

      {/* 健康记录 */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">最近健康记录</h2>

        {records.length === 0 ? (
          <p className="text-gray-500 text-center py-4">暂无健康记录</p>
        ) : (
          <div className="space-y-3">
            {records.map((record) => (
              <div
                key={record.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div>
                  <span className="font-medium">
                    {getRecordTypeLabel(record.record_type)}
                  </span>
                  <span className="mx-2 text-teal-600">
                    {record.value} {record.unit}
                  </span>
                </div>
                <span className="text-sm text-gray-500">
                  {new Date(record.recorded_at).toLocaleString("zh-CN")}
                </span>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}

function getRecordTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    blood_pressure: "🩸 血压",
    blood_sugar: "💉 血糖",
    heart_rate: "💓 心率",
    weight: "⚖️ 体重",
    temperature: "🌡️ 体温",
  };
  return labels[type] || type;
}

export default ProfilePage;
