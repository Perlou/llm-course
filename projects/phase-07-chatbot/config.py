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
    model_name: str = os.getenv("MODEL_NAME", "gpt-4o-mini")
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
    max_tokens: int = int(os.getenv("MAX_TOKENS", "2000"))

    # 记忆配置
    max_history: int = int(os.getenv("MAX_HISTORY", "20"))

    def validate(self) -> bool:
        """验证配置"""
        if not self.openai_api_key:
            print("❌ 错误: 请设置 OPENAI_API_KEY 环境变量")
            return False
        return True


config = Config()
