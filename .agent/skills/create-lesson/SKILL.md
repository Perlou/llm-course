---
name: create-lesson
description: 创建新的 LLM 应用开发课程文件，包含理论解释、代码示例和练习
---

# 创建课程文件技能

此技能用于在 LLM 应用开发课程项目中创建新的课程文件。

## 文件命名规范

- 格式：`{序号:02d}-{英文名}.py`
- 示例：`01-openai-api-basics.py`, `02-streaming-responses.py`

## 课程文件结构

每个课程文件应包含以下部分：

```python
"""
{课程标题}
{'=' * len(课程标题)}

学习目标：
    1. 目标一
    2. 目标二
    3. 目标三

核心概念：
    - 概念一：简要说明
    - 概念二：简要说明

前置知识：
    - 前置课程一
    - 前置课程二

环境要求：
    - 需要配置 OPENAI_API_KEY 或其他 API Key
"""

import os
from dotenv import load_dotenv
# 其他必要的导入

# 加载环境变量
load_dotenv()

# ==================== 第一部分：理论介绍 ====================

def introduction():
    """
    {主题}介绍

    理论背景和核心概念解释...
    """
    print("=" * 60)
    print("第一部分：{主题}概述")
    print("=" * 60)

    # 详细的理论解释，使用 print 语句
    # 配合代码示例

# ==================== 第二部分：基础实现 ====================

def basic_implementation():
    """基础实现示例"""
    print("\n" + "=" * 60)
    print("第二部分：基础实现")
    print("=" * 60)

    # 代码实现
    # 详细注释

# ==================== 第三部分：进阶应用 ====================

def advanced_examples():
    """进阶应用示例"""
    print("\n" + "=" * 60)
    print("第三部分：进阶应用")
    print("=" * 60)

    # 更复杂的示例

# ==================== 第四部分：练习与思考 ====================

def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    exercises_text = """
    练习 1：...

    练习 2：...

    思考题：...
    """
    print(exercises_text)

# ==================== 主函数 ====================

def main():
    """主函数 - 按顺序执行所有部分"""
    introduction()
    basic_implementation()
    advanced_examples()
    exercises()

    print("\n" + "=" * 60)
    print("课程完成！下一步：{下一课程}")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

## 创建步骤

1. **确定课程位置**：根据主题确定放在哪个 phase 目录
2. **查看已有文件**：检查该目录下已有文件，确定序号
3. **参考现有课程**：查看同目录下的其他课程文件，保持风格一致
4. **创建文件**：使用上述模板创建新课程
5. **更新 README**：如果目录有 README.md，更新文件列表

## LLM 课程特殊要求

### API Key 处理

```python
# 始终使用环境变量，不要硬编码
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("请设置 OPENAI_API_KEY 环境变量")
```

### 错误处理

```python
# 包含 API 调用错误处理
from openai import OpenAI, APIError, RateLimitError

try:
    response = client.chat.completions.create(...)
except RateLimitError:
    print("API 速率限制，请稍后重试")
except APIError as e:
    print(f"API 错误: {e}")
```

### 成本提示

```python
# 在涉及 API 调用的课程中添加成本提示
print("⚠️ 注意：本课程将调用 OpenAI API，会产生少量费用")
print("预估 token 消耗：约 1000 tokens")
```

## 内容要求

- **理论与代码结合**：每个概念都要有对应的代码示例
- **循序渐进**：从简单到复杂，层层递进
- **中文注释**：所有注释和输出使用中文
- **可运行**：确保代码可以直接运行，输出清晰
- **API Key 安全**：使用环境变量，提供无 API 的 mock 模式

## 代码风格

- 使用 4 空格缩进
- 函数之间空两行
- 导入按标准库、第三方库、本地模块分组
- 变量名使用下划线命名法
- 类名使用驼峰命名法
