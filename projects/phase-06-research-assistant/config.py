"""
配置管理模块
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """应用配置"""

    # API 配置
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # 模型配置
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

    # Agent 配置
    max_iterations: int = int(os.getenv("MAX_ITERATIONS", "15"))
    verbose: bool = os.getenv("VERBOSE", "true").lower() == "true"

    # 路径配置
    notes_dir: str = os.path.join(os.path.dirname(__file__), "notes")
    reports_dir: str = os.path.join(os.path.dirname(__file__), "reports")

    def validate(self) -> bool:
        """验证配置"""
        if not self.openai_api_key:
            print("❌ 错误: 请设置 OPENAI_API_KEY 环境变量")
            return False

        # 确保目录存在
        os.makedirs(self.notes_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)

        return True


config = Config()
