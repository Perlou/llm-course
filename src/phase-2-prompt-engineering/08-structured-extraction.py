"""
结构化信息提取
==============

学习目标：
    1. 掌握从文本中提取结构化信息的技巧
    2. 学会设计提取 Schema
    3. 了解实体识别和关系抽取

核心概念：
    - 实体提取：识别文本中的命名实体
    - 关系抽取：识别实体间的关系
    - Schema 设计：定义提取结构

前置知识：
    - 07-json-output.py

环境要求：
    - pip install openai python-dotenv
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


# ==================== 第一部分：实体提取 ====================


def entity_extraction():
    """实体提取"""
    print("=" * 60)
    print("第一部分：实体提取")
    print("=" * 60)

    client = OpenAI()

    prompt = """从以下新闻中提取实体信息，返回JSON格式：

新闻：2024年3月15日，苹果公司CEO蒂姆·库克在加州库比蒂诺总部宣布，将投资10亿美元在中国上海建设新的研发中心。

提取以下类型的实体：
- 人物（PERSON）
- 组织（ORG）
- 地点（LOC）
- 日期（DATE）
- 金额（MONEY）

返回格式：
{
    "entities": [
        {"text": "实体文本", "type": "实体类型"}
    ]
}"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=300,
    )

    data = json.loads(response.choices[0].message.content)
    print("提取的实体：")
    for entity in data.get("entities", []):
        print(f"  [{entity['type']}] {entity['text']}")


# ==================== 第二部分：关系抽取 ====================


def relation_extraction():
    """关系抽取"""
    print("\n" + "=" * 60)
    print("第二部分：关系抽取")
    print("=" * 60)

    client = OpenAI()

    prompt = """从以下文本中提取实体及其关系：

文本：马化腾是腾讯公司的创始人兼CEO。腾讯总部位于深圳，旗下拥有微信和QQ等产品。

返回格式：
{
    "entities": ["实体列表"],
    "relations": [
        {"subject": "主体", "relation": "关系", "object": "客体"}
    ]
}"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=300,
    )

    data = json.loads(response.choices[0].message.content)

    print("实体:", data.get("entities", []))
    print("\n关系：")
    for rel in data.get("relations", []):
        print(f"  {rel['subject']} --[{rel['relation']}]--> {rel['object']}")


# ==================== 第三部分：表单信息提取 ====================


def form_extraction():
    """表单信息提取"""
    print("\n" + "=" * 60)
    print("第三部分：表单信息提取")
    print("=" * 60)

    client = OpenAI()

    prompt = """从以下简历文本中提取结构化信息：

简历：
张三，男，1990年5月出生，本科学历，毕业于北京大学计算机系。
目前在阿里巴巴担任高级工程师，有8年工作经验。
擅长Java和Python编程，邮箱：zhangsan@email.com，电话：13800138000。

返回JSON格式：
{
    "basic_info": {
        "name": "",
        "gender": "",
        "birth_date": "",
        "education": "",
        "school": "",
        "major": ""
    },
    "work_info": {
        "company": "",
        "position": "",
        "experience_years": 0
    },
    "skills": [],
    "contact": {
        "email": "",
        "phone": ""
    }
}"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=400,
    )

    data = json.loads(response.choices[0].message.content)
    print("提取结果：")
    print(json.dumps(data, ensure_ascii=False, indent=2))


# ==================== 第四部分：事件提取 ====================


def event_extraction():
    """事件提取"""
    print("\n" + "=" * 60)
    print("第四部分：事件提取")
    print("=" * 60)

    client = OpenAI()

    prompt = """从以下新闻中提取事件信息：

新闻：据报道，特斯拉于2024年1月在上海工厂交付了第100万辆Model 3。马斯克通过视频连线表示祝贺，并宣布将追加20亿美元投资扩大产能。

提取事件，包含：时间、地点、主体、动作、对象、结果

返回格式：
{
    "events": [
        {
            "time": "",
            "location": "",
            "subject": "",
            "action": "",
            "object": "",
            "result": ""
        }
    ]
}"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=400,
    )

    data = json.loads(response.choices[0].message.content)
    print("提取的事件：")
    for i, event in enumerate(data.get("events", []), 1):
        print(f"\n事件 {i}:")
        for key, value in event.items():
            if value:
                print(f"  {key}: {value}")


# ==================== 第五部分：练习与思考 ====================


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：商品信息提取
        从商品描述中提取名称、价格、规格等。

    练习 2：会议纪要提取
        从会议记录中提取时间、参会人、议题、结论。

    练习 3：合同关键信息
        从合同文本中提取双方、金额、期限等关键条款。

    思考题：
        1. 如何处理信息缺失的情况？
        2. 如何提高提取的准确性？
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 结构化信息提取")
    print("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 OPENAI_API_KEY")
        return

    try:
        entity_extraction()
        relation_extraction()
        form_extraction()
        event_extraction()
        exercises()
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return

    print("\n" + "=" * 60)
    print("✅ 课程完成！下一步：09-prompt-templates.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
