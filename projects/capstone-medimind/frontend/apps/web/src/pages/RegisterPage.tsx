import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { authApi } from "@medimind/api-client";
import { Button, Input } from "@medimind/ui";

/**
 * 注册页面
 */
export function RegisterPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [nickname, setNickname] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [agreed, setAgreed] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // 验证
    if (password !== confirmPassword) {
      setError("两次输入的密码不一致");
      return;
    }
    if (password.length < 6) {
      setError("密码至少需要 6 位");
      return;
    }
    if (!agreed) {
      setError("请先同意服务条款");
      return;
    }

    setLoading(true);

    try {
      const response = await authApi.register({ email, password, nickname });
      // 保存 token
      localStorage.setItem("access_token", response.access_token);
      localStorage.setItem("user", JSON.stringify(response.user));
      navigate("/");
    } catch (err: any) {
      setError(err.message || "注册失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-teal-600">🏥 创建账号</h1>
          <p className="mt-2 text-gray-600">注册成为 MediMind 用户</p>
        </div>

        {/* form */}
        <form
          onSubmit={handleSubmit}
          className="mt-8 space-y-6 bg-white p-8 rounded-xl shadow-lg"
        >
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                邮箱地址
              </label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                required
              />
            </div>

            <div>
              <label
                htmlFor="nickname"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                昵称
              </label>
              <Input
                id="nickname"
                type="text"
                value={nickname}
                onChange={(e) => setNickname(e.target.value)}
                placeholder="您的昵称"
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                密码 (至少 6 位)
              </label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            <div>
              <label
                htmlFor="confirmPassword"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                确认密码
              </label>
              <Input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            <div className="flex items-center">
              <input
                id="agree"
                type="checkbox"
                checked={agreed}
                onChange={(e) => setAgreed(e.target.checked)}
                className="h-4 w-4 text-teal-600 border-gray-300 rounded"
              />
              <label htmlFor="agree" className="ml-2 text-sm text-gray-600">
                我已阅读并同意{" "}
                <a href="#" className="text-teal-600">
                  服务条款
                </a>
              </label>
            </div>
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={loading || !agreed}
          >
            {loading ? "注册中..." : "注 册"}
          </Button>

          <div className="text-center text-sm text-gray-600">
            已有账号？{" "}
            <Link to="/login" className="text-teal-600 hover:underline">
              立即登录
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}

export default RegisterPage;
