#!/usr/bin/env python3
"""
批量转换脚本：将 OpenAI API 调用转换为 Gemini API
================================================

此脚本用于自动将课程文件中的 OpenAI API 调用转换为 Google Gemini API。
"""

import os
import re


def convert_openai_to_gemini(content: str) -> str:
    """将 OpenAI 代码转换为 Gemini 代码"""

    # 替换导入语句
    content = re.sub(
        r"from openai import OpenAI", "import google.generativeai as genai", content
    )

    # 替换客户端初始化
    content = re.sub(
        r"client = OpenAI\(\)",
        'genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))\n    model = genai.GenerativeModel("gemini-2.0-flash")',
        content,
    )

    # 替换 API 调用 (简单替换)
    content = re.sub(
        r"client\.chat\.completions\.create\(", "model.generate_content(", content
    )

    # 替换环境变量检查
    content = re.sub(r"OPENAI_API_KEY", "GOOGLE_API_KEY", content)

    # 替换 response 访问
    content = re.sub(
        r"response\.choices\[0\]\.message\.content", "response.text", content
    )

    # 替换 max_tokens
    content = re.sub(
        r"max_tokens=", 'generation_config={"max_output_tokens": ', content
    )

    return content


def process_file(filepath: str) -> bool:
    """处理单个文件"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        if "from openai import" not in content:
            return False

        new_content = convert_openai_to_gemini(content)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

        return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python convert_to_gemini.py <file_or_directory>")
        sys.exit(1)

    target = sys.argv[1]

    if os.path.isfile(target):
        if process_file(target):
            print(f"✅ Converted: {target}")
        else:
            print(f"⏭️ Skipped: {target}")
    elif os.path.isdir(target):
        for root, dirs, files in os.walk(target):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    if process_file(filepath):
                        print(f"✅ Converted: {filepath}")
    else:
        print(f"❌ Invalid target: {target}")
