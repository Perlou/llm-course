#!/usr/bin/env python3
"""
批量转换脚本：将课程文件中的 OpenAI API 调用转换为 Gemini API
=============================================================

用法：python batch_convert.py
"""

import os
import re

# 需要转换的文件列表
FILES_TO_CONVERT = [
    # Phase 2 剩余文件
    "src/phase-2-prompt-engineering/06-self-consistency.py",
    "src/phase-2-prompt-engineering/07-json-output.py",
    "src/phase-2-prompt-engineering/08-structured-extraction.py",
    "src/phase-2-prompt-engineering/09-prompt-templates.py",
    "src/phase-2-prompt-engineering/10-adversarial-prompting.py",
    "src/phase-2-prompt-engineering/11-project-smart-customer-service.py",
]


def convert_file(content: str) -> str:
    """将 OpenAI 代码转换为 Gemini 代码"""

    # 1. 替换文件头部注释中的 openai
    content = re.sub(r"pip install openai", "pip install google-generativeai", content)

    # 2. 替换导入语句
    content = re.sub(r"from openai import OpenAI\n", "", content)

    # 3. 替换环境变量名
    content = re.sub(r"OPENAI_API_KEY", "GOOGLE_API_KEY", content)

    # 4. 替换 client = OpenAI() 为 Gemini 初始化
    # 这需要在函数内部添加 genai 配置
    content = re.sub(
        r"(\s+)client = OpenAI\(\)",
        r"""\1import google.generativeai as genai
\1genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
\1model = genai.GenerativeModel("gemini-2.0-flash")""",
        content,
    )

    # 5. 替换简单的 API 调用
    # client.chat.completions.create(...) -> model.generate_content(...)

    # 替换带 system message 的调用
    content = re.sub(
        r"client\.chat\.completions\.create\(\s*"
        r'model="gpt-[\d.]+-turbo",\s*'
        r"messages=\[\s*"
        r'\{"role": "system", "content": ([^}]+)\},\s*'
        r'\{"role": "user", "content": ([^}]+)\}\s*'
        r"\],?\s*"
        r"(?:max_tokens=(\d+),?)?\s*"
        r"\)",
        lambda m: f"""genai.GenerativeModel(
            "gemini-2.0-flash",
            system_instruction={m.group(1)}
        ).generate_content(
            {m.group(2)},
            generation_config={{"max_output_tokens": {m.group(3) or 500}}}
        )""",
        content,
    )

    # 替换简单的用户消息调用
    content = re.sub(
        r"client\.chat\.completions\.create\(\s*"
        r'model="gpt-[\d.]+-turbo",\s*'
        r'messages=\[\{"role": "user", "content": ([^}]+)\}\],?\s*'
        r"(?:max_tokens=(\d+),?)?\s*"
        r"\)",
        lambda m: f'model.generate_content(\n            {m.group(1)},\n            generation_config={{"max_output_tokens": {m.group(2) or 500}}}\n        )',
        content,
    )

    # 6. 替换 response 访问方式
    content = re.sub(
        r"response\.choices\[0\]\.message\.content", "response.text", content
    )
    content = re.sub(
        r"r\d+\.choices\[0\]\.message\.content",
        lambda m: m.group(0).replace(".choices[0].message.content", ".text"),
        content,
    )

    # 7. 添加 Gemini 版本标识到标题
    content = re.sub(
        r'("""[\n\r]+[\w\s]+)\n(=+)', r"\1 (Gemini 版本)\n\2", content, count=1
    )

    return content


def process_file(filepath: str) -> bool:
    """处理单个文件"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # 检查是否需要转换
        if "from openai import" not in content and "OpenAI()" not in content:
            print(f"⏭️ 跳过（无 OpenAI 调用）：{filepath}")
            return False

        new_content = convert_file(content)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"✅ 已转换：{filepath}")
        return True
    except Exception as e:
        print(f"❌ 错误 {filepath}: {e}")
        return False


def main():
    base_dir = "/Users/perlou/Desktop/personal/llm-course"

    print("🔄 开始批量转换课程文件...")
    print("=" * 60)

    converted = 0
    for rel_path in FILES_TO_CONVERT:
        filepath = os.path.join(base_dir, rel_path)
        if os.path.exists(filepath):
            if process_file(filepath):
                converted += 1
        else:
            print(f"⚠️ 文件不存在：{filepath}")

    print("=" * 60)
    print(f"✅ 完成！共转换 {converted} 个文件")


if __name__ == "__main__":
    main()
