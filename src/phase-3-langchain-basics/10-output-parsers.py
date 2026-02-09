"""
输出解析器
==========

学习目标：
    1. 理解输出解析器的作用
    2. 掌握常用解析器的使用
    3. 学会自定义解析器

核心概念：
    - StrOutputParser：字符串解析
    - JsonOutputParser：JSON 解析
    - PydanticOutputParser：结构化对象解析

前置知识：
    - 09-memory-persistence.py

环境要求：
    - pip install langchain langchain-google-genai python-dotenv pydantic
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：输出解析器概述 ====================


def parser_overview():
    """输出解析器概述"""
    print("=" * 60)
    print("第一部分：输出解析器概述")
    print("=" * 60)

    print("""
    输出解析器的作用：
    ─────────────────
    
    将 LLM 的文本输出转换为结构化数据
    
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │  LLM 输出   │ ─▶ │   Parser    │ ─▶ │  结构化数据  │
    │   (文本)    │    │   (解析)    │    │ (JSON/对象) │
    └─────────────┘    └─────────────┘    └─────────────┘
    
    常用解析器：
    ───────────
    
    | 解析器              | 输出类型    | 使用场景          |
    |--------------------|-----------|------------------|
    | StrOutputParser    | 字符串     | 普通文本输出       |
    | JsonOutputParser   | 字典       | JSON 格式输出     |
    | PydanticOutputParser| Pydantic对象| 强类型结构化输出 |
    | CommaSeparatedList | 列表       | 逗号分隔列表       |
    """)


# ==================== 第二部分：StrOutputParser ====================


def str_parser_demo():
    """StrOutputParser 演示"""
    print("\n" + "=" * 60)
    print("第二部分：StrOutputParser")
    print("=" * 60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        prompt = ChatPromptTemplate.from_template("用一句话解释{topic}")

        # 不使用解析器
        print("📌 不使用解析器：")
        result1 = (prompt | llm).invoke({"topic": "人工智能"})
        print(f"类型: {type(result1)}")
        print(f"内容: {result1.content}")

        # 使用 StrOutputParser
        print("\n📌 使用 StrOutputParser：")
        parser = StrOutputParser()
        result2 = (prompt | llm | parser).invoke({"topic": "人工智能"})
        print(f"类型: {type(result2)}")
        print(f"内容: {result2}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第三部分：JsonOutputParser ====================


def json_parser_demo():
    """JsonOutputParser 演示"""
    print("\n" + "=" * 60)
    print("第三部分：JsonOutputParser")
    print("=" * 60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import JsonOutputParser

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
        parser = JsonOutputParser()

        prompt = ChatPromptTemplate.from_template("""
分析以下文本，返回 JSON 格式：
{format_instructions}

文本：{text}
""")

        chain = prompt | llm | parser

        result = chain.invoke(
            {
                "text": "苹果公司发布了新款 iPhone 15，售价 5999 元起",
                "format_instructions": parser.get_format_instructions(),
            }
        )

        print("📌 JSON 解析结果：")
        print(f"类型: {type(result)}")
        print(f"内容: {result}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第四部分：PydanticOutputParser ====================


def pydantic_parser_demo():
    """PydanticOutputParser 演示"""
    print("\n" + "=" * 60)
    print("第四部分：PydanticOutputParser")
    print("=" * 60)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import PydanticOutputParser
        from pydantic import BaseModel, Field
        from typing import List

        # 定义数据模型
        class ProductInfo(BaseModel):
            name: str = Field(description="产品名称")
            price: float = Field(description="价格")
            features: List[str] = Field(description="主要特点")
            rating: float = Field(description="评分 1-5")

        parser = PydanticOutputParser(pydantic_object=ProductInfo)

        prompt = ChatPromptTemplate.from_template("""
提取以下产品信息：
{format_instructions}

产品描述：{description}
""")

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
        chain = prompt | llm | parser

        result = chain.invoke(
            {
                "description": "小米14手机，骁龙8 Gen3处理器，6.36英寸屏幕，售价3999元，用户好评如潮",
                "format_instructions": parser.get_format_instructions(),
            }
        )

        print("📌 Pydantic 解析结果：")
        print(f"类型: {type(result)}")
        print(f"名称: {result.name}")
        print(f"价格: {result.price}")
        print(f"特点: {result.features}")
        print(f"评分: {result.rating}")

    except Exception as e:
        print(f"❌ 错误: {e}")


# ==================== 第五部分：自定义解析器 ====================


def custom_parser_demo():
    """自定义解析器"""
    print("\n" + "=" * 60)
    print("第五部分：自定义解析器")
    print("=" * 60)

    from langchain_core.output_parsers import BaseOutputParser

    class BulletPointParser(BaseOutputParser[list]):
        """解析项目符号列表"""

        def parse(self, text: str) -> list:
            lines = text.strip().split("\n")
            items = []
            for line in lines:
                line = line.strip()
                if line.startswith("- ") or line.startswith("• "):
                    items.append(line[2:])
                elif line.startswith("* "):
                    items.append(line[2:])
                elif line and line[0].isdigit() and ". " in line:
                    items.append(line.split(". ", 1)[1])
            return items

    # 测试
    parser = BulletPointParser()

    test_text = """
    - 第一个要点
    - 第二个要点
    - 第三个要点
    """

    result = parser.parse(test_text)
    print("📌 自定义解析器测试：")
    print(f"输入: {test_text}")
    print(f"输出: {result}")


# ==================== 第六部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：提取实体
        使用 PydanticOutputParser 从新闻中提取人名、地点、时间。

        ✅ 参考答案：
        ```python
        from pydantic import BaseModel, Field
        from typing import List, Optional
        from langchain_core.output_parsers import PydanticOutputParser

        class NewsEntities(BaseModel):
            people: List[str] = Field(description="提到的人名")
            locations: List[str] = Field(description="提到的地点")
            times: List[str] = Field(description="提到的时间")
            organizations: Optional[List[str]] = Field(description="提到的组织机构", default=[])

        parser = PydanticOutputParser(pydantic_object=NewsEntities)

        prompt = ChatPromptTemplate.from_template('''
        从以下新闻中提取实体信息：
        {format_instructions}

        新闻：{news}
        ''')

        chain = prompt | llm | parser

        result = chain.invoke({
            "news": "2024年1月15日，马云在杭州阿里巴巴总部发表演讲",
            "format_instructions": parser.get_format_instructions()
        })
        # result.people = ["马云"]
        # result.locations = ["杭州"]
        # result.times = ["2024年1月15日"]
        ```

    练习 2：情感分析
        创建解析器将文本分类为正面/负面/中性。

        ✅ 参考答案：
        ```python
        from pydantic import BaseModel, Field
        from enum import Enum

        class Sentiment(str, Enum):
            POSITIVE = "正面"
            NEGATIVE = "负面"
            NEUTRAL = "中性"

        class SentimentResult(BaseModel):
            sentiment: Sentiment = Field(description="情感倾向")
            confidence: float = Field(description="置信度 0-1")
            reason: str = Field(description="判断理由")

        sentiment_parser = PydanticOutputParser(pydantic_object=SentimentResult)

        sentiment_prompt = ChatPromptTemplate.from_template('''
        分析以下文本的情感：
        {format_instructions}

        文本：{text}
        ''')

        sentiment_chain = sentiment_prompt | llm | sentiment_parser

        result = sentiment_chain.invoke({
            "text": "这个产品太棒了，超出预期！",
            "format_instructions": sentiment_parser.get_format_instructions()
        })
        ```

    练习 3：多格式解析
        支持解析 JSON、YAML、列表等多种格式。

        ✅ 参考答案：
        ```python
        from langchain_core.output_parsers import BaseOutputParser
        import json
        import yaml

        class MultiFormatParser(BaseOutputParser):
            def parse(self, text: str):
                text = text.strip()
                
                # 尝试 JSON
                try:
                    if text.startswith('{') or text.startswith('['):
                        return {"format": "json", "data": json.loads(text)}
                except json.JSONDecodeError:
                    pass
                
                # 尝试 YAML
                try:
                    data = yaml.safe_load(text)
                    if isinstance(data, (dict, list)):
                        return {"format": "yaml", "data": data}
                except yaml.YAMLError:
                    pass
                
                # 尝试列表格式
                if any(text.startswith(p) for p in ['- ', '• ', '* ', '1.']):
                    items = []
                    for line in text.split('\\n'):
                        line = line.strip()
                        for prefix in ['- ', '• ', '* ']:
                            if line.startswith(prefix):
                                items.append(line[len(prefix):])
                                break
                        else:
                            if line and line[0].isdigit() and '. ' in line:
                                items.append(line.split('. ', 1)[1])
                    return {"format": "list", "data": items}
                
                # 默认纯文本
                return {"format": "text", "data": text}
        ```

    思考题：
        1. 解析失败时如何处理？
           
           ✅ 答案：
           - 重试机制：让 LLM 重新生成
           - 回退解析：尝试宽松的解析规则
           - 错误修复：使用 LLM 修复格式问题
           - 默认值：返回预定义的默认结构
           - 记录日志：保存失败案例用于改进
           - 使用 `OutputFixingParser` 自动修复

        2. 如何提高 LLM 输出格式的一致性？
           
           ✅ 答案：
           - 降低温度：temperature=0 更确定
           - 提供示例：Few-Shot 展示期望格式
           - 格式说明：明确指定 JSON Schema
           - 结构化输出：使用 Gemini 的结构化输出功能
           - 后处理：正则表达式提取有效部分
           - 多次尝试：失败时重试几次
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 输出解析器")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 GOOGLE_API_KEY")
        return

    try:
        parser_overview()
        str_parser_demo()
        json_parser_demo()
        pydantic_parser_demo()
        custom_parser_demo()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("🎉 Phase 3 课程全部完成！")
    print("下一步：进入 Phase 4 学习 RAG 应用")
    print("=" * 60)


if __name__ == "__main__":
    main()
