import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import {
  MapPin,
  ArrowLeft,
  Search,
  Phone,
  Star,
  Navigation,
} from "lucide-react";
import { clsx } from "clsx";
import { hospitalApi } from "@medimind/api-client";
import type { Hospital, Location } from "@medimind/api-client";
import { Input, Button, Card, SafetyBanner } from "@medimind/ui";

export default function HospitalPage() {
  const [location, setLocation] = useState<Location | null>(null);
  const [locationError, setLocationError] = useState<string | null>(null);
  const [isLoadingLocation, setIsLoadingLocation] = useState(true);

  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [keyword, setKeyword] = useState("");
  const [radius, setRadius] = useState(5000);
  const [isMockData, setIsMockData] = useState(false);

  const [selectedHospital, setSelectedHospital] = useState<Hospital | null>(
    null,
  );

  // 获取用户位置
  useEffect(() => {
    if (!navigator.geolocation) {
      setLocationError("您的浏览器不支持地理定位");
      setIsLoadingLocation(false);
      // 使用模拟位置（北京天安门）
      setLocation({ lat: 39.9042, lng: 116.4074 });
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        });
        setIsLoadingLocation(false);
      },
      (error) => {
        let message = "无法获取位置";
        switch (error.code) {
          case error.PERMISSION_DENIED:
            message = "位置访问被拒绝，请在浏览器设置中允许位置访问";
            break;
          case error.POSITION_UNAVAILABLE:
            message = "位置信息不可用";
            break;
          case error.TIMEOUT:
            message = "获取位置超时";
            break;
        }
        setLocationError(message);
        setIsLoadingLocation(false);
        // 使用模拟位置
        setLocation({ lat: 39.9042, lng: 116.4074 });
      },
      { timeout: 10000, enableHighAccuracy: true },
    );
  }, []);

  // 搜索医院
  const searchHospitals = useCallback(async () => {
    if (!location) return;

    setIsLoading(true);
    try {
      const result = await hospitalApi.searchNearby({
        lat: location.lat,
        lng: location.lng,
        keyword: keyword || undefined,
        radius,
      });
      setHospitals(result.hospitals);
      setIsMockData(result.mock || false);
    } catch (error) {
      console.error("搜索医院失败:", error);
    } finally {
      setIsLoading(false);
    }
  }, [location, keyword, radius]);

  // 位置变化时自动搜索
  useEffect(() => {
    if (location && !isLoadingLocation) {
      searchHospitals();
    }
  }, [location, isLoadingLocation, searchHospitals]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    searchHospitals();
  };

  const formatDistance = (distance?: number) => {
    if (!distance) return "";
    if (distance < 1000) return `${Math.round(distance)}米`;
    return `${(distance / 1000).toFixed(1)}公里`;
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
        <h1 className="font-semibold text-lg">附近医院</h1>
      </div>

      {/* Safety Banner */}
      <div className="px-4 py-3">
        <SafetyBanner variant="info">
          🏥 医院信息来源于高德地图，就医前请电话确认
        </SafetyBanner>
      </div>

      {/* Location Status */}
      <div className="px-4 pb-3">
        <div className="flex items-center gap-2 text-sm text-text-secondary">
          <MapPin className="w-4 h-4" />
          {isLoadingLocation ? (
            <span>正在获取位置...</span>
          ) : locationError ? (
            <span className="text-alert-warning">
              {locationError}（使用默认位置）
            </span>
          ) : (
            <span>
              已定位: {location?.lat.toFixed(4)}, {location?.lng.toFixed(4)}
            </span>
          )}
        </div>
        {isMockData && (
          <p className="text-xs text-alert-warning mt-1">
            ⚠️ 当前显示为模拟数据（未配置高德 API Key）
          </p>
        )}
      </div>

      {/* Search */}
      <div className="px-4 pb-3">
        <form onSubmit={handleSearch} className="flex gap-2">
          <Input
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="搜索医院名称或科室..."
            leftIcon={<Search className="w-4 h-4" />}
            containerClassName="flex-1"
          />
          <Button type="submit" disabled={isLoading || !location}>
            搜索
          </Button>
        </form>

        {/* Radius Filter */}
        <div className="flex gap-2 mt-2">
          {[3000, 5000, 10000].map((r) => (
            <button
              key={r}
              onClick={() => setRadius(r)}
              className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                radius === r
                  ? "bg-medical-blue text-white border-medical-blue"
                  : "border-border hover:border-medical-blue"
              }`}
            >
              {r / 1000}km
            </button>
          ))}
        </div>
      </div>

      {/* Hospital List */}
      <div className="flex-1 overflow-y-auto px-4 pb-24 md:pb-8">
        {isLoading ? (
          <div className="text-center py-8 text-text-muted">搜索中...</div>
        ) : hospitals.length === 0 ? (
          <div className="text-center py-8 text-text-muted">未找到附近医院</div>
        ) : (
          <div className="space-y-3">
            {hospitals.map((hospital) => (
              <Card
                key={hospital.id}
                className="cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => setSelectedHospital(hospital)}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg">{hospital.name}</h3>
                    <p className="text-sm text-text-secondary mt-1">
                      {hospital.address}
                    </p>
                    {hospital.type_name && (
                      <span className="inline-block mt-2 px-2 py-0.5 text-xs bg-medical-blue/10 text-medical-blue rounded">
                        {hospital.type_name}
                      </span>
                    )}
                  </div>
                  <div className="text-right ml-3">
                    {hospital.distance && (
                      <div className="flex items-center gap-1 text-sm text-medical-blue">
                        <Navigation className="w-3 h-3" />
                        {formatDistance(hospital.distance)}
                      </div>
                    )}
                    {hospital.rating && (
                      <div className="flex items-center gap-1 text-sm text-alert-warning mt-1">
                        <Star className="w-3 h-3 fill-current" />
                        {hospital.rating.toFixed(1)}
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Hospital Detail Modal */}
      {selectedHospital && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <Card className="w-full max-w-lg">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-xl font-bold">{selectedHospital.name}</h2>
                {selectedHospital.type_name && (
                  <span className="inline-block mt-1 px-2 py-0.5 text-xs bg-medical-blue/10 text-medical-blue rounded">
                    {selectedHospital.type_name}
                  </span>
                )}
              </div>
              <button
                onClick={() => setSelectedHospital(null)}
                className="p-1 text-text-muted hover:text-text-primary"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3">
              <div className="flex items-start gap-2">
                <MapPin className="w-4 h-4 mt-1 text-text-secondary" />
                <p>{selectedHospital.address}</p>
              </div>

              {selectedHospital.tel && (
                <div className="flex items-center gap-2">
                  <Phone className="w-4 h-4 text-text-secondary" />
                  <a
                    href={`tel:${selectedHospital.tel}`}
                    className="text-medical-blue hover:underline"
                  >
                    {selectedHospital.tel}
                  </a>
                </div>
              )}

              {selectedHospital.distance && (
                <div className="flex items-center gap-2">
                  <Navigation className="w-4 h-4 text-text-secondary" />
                  <span>
                    距离您 {formatDistance(selectedHospital.distance)}
                  </span>
                </div>
              )}

              {selectedHospital.rating && (
                <div className="flex items-center gap-2">
                  <Star className="w-4 h-4 text-alert-warning fill-current" />
                  <span>评分 {selectedHospital.rating.toFixed(1)}</span>
                </div>
              )}
            </div>

            <div className="mt-6 flex gap-2">
              {selectedHospital.tel && (
                <a
                  href={`tel:${selectedHospital.tel}`}
                  className={clsx(
                    "flex-1 inline-flex items-center justify-center gap-1 px-4 py-2 rounded-lg font-medium transition-colors",
                    "bg-medical-blue text-white hover:bg-medical-blue/90",
                  )}
                >
                  <Phone className="w-4 h-4" />
                  拨打电话
                </a>
              )}
              {selectedHospital.location && (
                <a
                  href={`https://uri.amap.com/marker?position=${selectedHospital.location.lng},${selectedHospital.location.lat}&name=${encodeURIComponent(selectedHospital.name)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={clsx(
                    "flex-1 inline-flex items-center justify-center gap-1 px-4 py-2 rounded-lg font-medium transition-colors",
                    "border border-border bg-white text-text-primary hover:bg-gray-50",
                  )}
                >
                  <Navigation className="w-4 h-4" />
                  导航前往
                </a>
              )}
            </div>

            <div className="mt-4 pt-3 border-t border-border">
              <p className="text-xs text-text-muted">
                🏥 医院信息来源于高德地图，就医前请电话确认。
              </p>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
