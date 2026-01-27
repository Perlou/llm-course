"""
JSON 格式输出
=============

学习目标：
    1. 掌握让 LLM 输出 JSON 的技巧
    2. 学会处理 JSON 解析错误
    3. 了解 response_format 参数

核心概念：
    - JSON Mode：强制 JSON 输出
    - Schema 定义：定义期望的结构
    - 错误处理：解析异常处理

前置知识：
    - 06-self-consistency.py

环境要求：
    - pip install openai python-dotenv
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


# ==================== 第一部分：基础 JSON 输出 ====================


def basic_json_output():
    """基础 JSON 输出"""
    print("=" * 60)
    print("第一部分：基础 JSON 输出")
    print("=" * 60)

    client = OpenAI()

    # 简单方式
    print("📌 方式一：在提示词中要求 JSON")
    prompt = """提取以下文本中的信息，以JSON格式返回：

文本：张三今年25岁，住在北京，是一名软件工程师。

返回格式：
{
    "name": "姓名",
    "age": 年龄,
    "city": "城市",
    "job": "职业"
}"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
    )

    content = response.choices[0].message.content
    print(f"原始回复:\n{content}")

    # 解析 JSON
    try:
        data = json.loads(content)
        print(f"\n解析成功: {data}")
    except json.JSONDecodeError as e:
        print(f"\n解析失败: {e}")


# ==================== 第二部分：JSON Mode ====================


def json_mode():
    """JSON Mode"""
    print("\n" + "=" * 60)
    print("第二部分：JSON Mode（推荐）")
    print("=" * 60)

    client = OpenAI()

    print("📌 使用 response_format 参数：")

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是一个数据提取助手，总是返回JSON格式。"},
            {
                "role": "user",
                "content": "提取信息：李四，30岁，上海，产品经理。返回包含name、age、city、job的JSON。",
            },
        ],
        response_format={"type": "json_object"},
        max_tokens=150,
    )

    content = response.choices[0].message.content
    print(f"回复:\n{content}")

    data = json.loads(content)
    print(f"\n已解析: {data}")


# ==================== 第三部分：复杂结构 ====================


def complex_structure():
    """复杂 JSON 结构"""
    print("\n" + "=" * 60)
    print("第三部分：复杂结构")
    print("=" * 60)

    client = OpenAI()

    prompt = """分析以下产品评论，返回JSON格式的分析结果：

评论："这款手机拍照效果很好，电池续航也不错，就是价格有点贵，屏幕边缘有点黄。"

返回格式：
{
    "overall_sentiment": "positive/negative/mixed",
    "aspects": [
        {"aspect": "方面", "sentiment": "positive/negative", "comment": "评价"}
    ],
    "summary": "一句话总结"
}"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=300,
    )

    data = json.loads(response.choices[0].message.content)
    print("分析结果：")
    print(json.dumps(data, ensure_ascii=False, indent=2))


# ==================== 第四部分：批量处理 ====================


def batch_extraction():
    """批量提取"""
    print("\n" + "=" * 60)
    print("第四部分：批量处理")
    print("=" * 60)

    client = OpenAI()

    prompt = """从以下新闻标题中提取所有公司名称和相关事件，返回JSON数组：

标题列表：
1. 苹果公司发布新款iPhone
2. 微软收购游戏公司
3. 特斯拉股价创新高

返回格式：
{
    "extractions": [
        {"company": "公司名", "event": "事件"}
    ]
}"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=200,
    )

    data = json.loads(response.choices[0].message.content)
    print("提取结果：")
    for item in data.get("extractions", []):
        print(f"  - {item['company']}: {item['event']}")


# ==================== 第五部分：错误处理 ====================


def error_handling():
    """错误处理"""
    print("\n" + "=" * 60)
    print("第五部分：错误处理")
    print("=" * 60)

    def safe_json_parse(text: str) -> dict:
        """安全的 JSON 解析"""
        # 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 尝试提取代码块中的 JSON
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end > start:
                try:
                    return json.loads(text[start:end].strip())
                except:
                    pass

        # 尝试找到 { 和 } 之间的内容
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except:
                pass

        return {"error": "无法解析", "raw": text}

    # 测试
    test_cases = [
        '{"name": "张三", "age": 25}',
        'Here is the JSON: {"name": "李四"}',
        '```json\n{"name": "王五"}\n```',
    ]

    print("📌 安全解析测试：")
    for text in test_cases:
        result = safe_json_parse(text)
        print(f"  输入: {text[:30]}...")
        print(f"  结果: {result}\n")


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：产品信息提取
        从产品描述中提取名称、价格、特点等信息。

    练习 2：对话意图识别
        分析用户输入，返回意图和参数的JSON。

    练习 3：数据验证
        实现JSON结构验证函数，检查必填字段。

    思考题：
        1. JSON Mode 有什么限制？
        2. 如何处理嵌套层级很深的结构？
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 JSON 格式输出")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 OPENAI_API_KEY")
        return

    try:
        basic_json_output()
        json_mode()
        complex_structure()
        batch_extraction()
        error_handling()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：08-structured-extraction.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
