"""
配置文件
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载根目录的 .env
ROOT_DIR = Path(__file__).parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

# API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 模型配置
GEMINI_MODEL = "gemini-1.5-flash"

# 输出目录
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
