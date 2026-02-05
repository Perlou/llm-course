#!/usr/bin/env python3
"""
迁移脚本：从 google.generativeai 迁移到 google.genai
======================================================

将项目中所有使用已废弃的 google.generativeai 包的代码
迁移到新的 google.genai SDK。

用法：
    python scripts/migrate_to_google_genai.py --dry-run  # 预览变更
    python scripts/migrate_to_google_genai.py            # 执行迁移
"""

import os
import re
import sys
import argparse
from pathlib import Path

# 迁移映射
IMPORT_PATTERNS = [
    # 标准导入
    (r"import google\.generativeai as genai", "from google import genai"),
    (r"from google\.generativeai import GenerativeModel", "from google import genai"),
    # 配置语句 - 删除（新 SDK 使用 Client() 自动读取环境变量）
    (r"genai\.configure\(api_key=os\.getenv\([\"']GOOGLE_API_KEY[\"']\)\)\n?", ""),
    (r"genai\.configure\(api_key=.*?\)\n?", ""),
]

# requirements.txt 中的包名替换
REQUIREMENTS_PATTERNS = [
    (r"google-generativeai[>=<\d.]*", "google-genai>=1.0.0"),
]

# pip install 注释中的替换
PIP_INSTALL_PATTERNS = [
    (r"pip install google-generativeai", "pip install google-genai"),
]


def migrate_file(file_path: Path, dry_run: bool = False) -> tuple[bool, list[str]]:
    """
    迁移单个文件

    Returns:
        (是否有变更, 变更描述列表)
    """
    changes = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return False, [f"读取失败: {e}"]

    original_content = content

    # 判断文件类型
    if file_path.name == "requirements.txt":
        # 处理 requirements.txt
        for pattern, replacement in REQUIREMENTS_PATTERNS:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes.append(f"替换: {pattern} -> {replacement}")

    elif file_path.suffix == ".py":
        # 处理 Python 文件

        # 1. 替换 import 语句
        for pattern, replacement in IMPORT_PATTERNS:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                if replacement:
                    changes.append(f"替换导入: {pattern[:50]}...")
                else:
                    changes.append(f"删除: {pattern[:50]}...")

        # 2. 替换 pip install 注释
        for pattern, replacement in PIP_INSTALL_PATTERNS:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes.append(f"更新 pip 安装说明")

        # 3. 检测并提示需要手动迁移的代码模式
        manual_migrations = []

        # GenerativeModel 实例化
        if re.search(r"genai\.GenerativeModel\(", content):
            manual_migrations.append(
                "genai.GenerativeModel() -> client.models.generate_content()"
            )

        # start_chat
        if re.search(r"model\.start_chat\(", content):
            manual_migrations.append("model.start_chat() -> client.chats.create()")

        # generate_content on model
        if re.search(r"model\.generate_content\(", content):
            manual_migrations.append(
                "model.generate_content() -> client.models.generate_content()"
            )

        # send_message
        if re.search(r"chat\.send_message\(", content):
            manual_migrations.append("chat.send_message() 签名变化: message= 参数")

        if manual_migrations:
            changes.append(f"⚠️  需要手动迁移: {', '.join(manual_migrations)}")

    elif file_path.suffix == ".md":
        # 处理 Markdown 文件中的依赖说明
        if "google-generativeai" in content:
            content = content.replace("google-generativeai", "google-genai")
            changes.append("更新 Markdown 中的包名引用")

    # 如果有变更，写入文件
    if content != original_content and not dry_run:
        file_path.write_text(content, encoding="utf-8")

    return content != original_content, changes


def find_files_to_migrate(root_dir: Path) -> list[Path]:
    """查找需要迁移的文件"""
    files = []

    for pattern in ["**/*.py", "**/requirements.txt", "**/*.md"]:
        for file_path in root_dir.glob(pattern):
            # 跳过虚拟环境和缓存目录
            if any(
                part in file_path.parts
                for part in [".venv", "venv", "__pycache__", ".git", "node_modules"]
            ):
                continue

            # 检查文件是否包含需要迁移的内容
            try:
                content = file_path.read_text(encoding="utf-8")
                if "google.generativeai" in content or "google-generativeai" in content:
                    files.append(file_path)
            except:
                pass

    return files


def main():
    parser = argparse.ArgumentParser(description="迁移到新的 google.genai SDK")
    parser.add_argument(
        "--dry-run", action="store_true", help="仅预览变更，不实际修改文件"
    )
    parser.add_argument("--path", type=str, default=".", help="项目根目录路径")
    args = parser.parse_args()

    root_dir = Path(args.path).resolve()
    print(f"📂 扫描目录: {root_dir}")
    print("=" * 60)

    files = find_files_to_migrate(root_dir)
    print(f"找到 {len(files)} 个需要迁移的文件\n")

    if args.dry_run:
        print("🔍 预览模式 (--dry-run)\n")

    total_changes = 0
    files_with_manual_work = []

    for file_path in sorted(files):
        changed, changes = migrate_file(file_path, dry_run=args.dry_run)

        if changed or changes:
            rel_path = file_path.relative_to(root_dir)
            print(f"📄 {rel_path}")
            for change in changes:
                print(f"   {change}")
                if "⚠️" in change:
                    files_with_manual_work.append((rel_path, change))
            print()
            total_changes += 1

    print("=" * 60)
    if args.dry_run:
        print(f"预览完成: {total_changes} 个文件将被修改")
        print("\n运行不带 --dry-run 的命令来执行实际迁移")
    else:
        print(f"✅ 迁移完成: {total_changes} 个文件已修改")

    if files_with_manual_work:
        print("\n" + "=" * 60)
        print("⚠️  以下文件需要手动完成 API 调用迁移:")
        print("=" * 60)
        for rel_path, note in files_with_manual_work:
            print(f"  - {rel_path}")
        print("\n📖 迁移指南: https://ai.google.dev/gemini-api/docs/migrate")


if __name__ == "__main__":
    main()
