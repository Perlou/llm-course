"""
结构化信息提取 - Gemini 版本
============================

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
    - pip install google-generativeai python-dotenv
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：实体提取 ====================


def entity_extraction():
    """实体提取"""
    print("=" * 60)
    print("第一部分：实体提取")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    model = genai.GenerativeModel(
        "gemini-2.0-flash", system_instruction="只返回JSON格式，不要添加任何说明文字。"
    )

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

    response = model.generate_content(
        prompt, generation_config={"max_output_tokens": 300}
    )

    data = json.loads(response.text)
    print("提取的实体：")
    for entity in data.get("entities", []):
        print(f"  [{entity['type']}] {entity['text']}")


# ==================== 第二部分：关系抽取 ====================


def relation_extraction():
    """关系抽取"""
    print("\n" + "=" * 60)
    print("第二部分：关系抽取")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    model = genai.GenerativeModel(
        "gemini-2.0-flash", system_instruction="只返回JSON格式。"
    )

    prompt = """从以下文本中提取实体及其关系：

文本：马化腾是腾讯公司的创始人兼CEO。腾讯总部位于深圳，旗下拥有微信和QQ等产品。

返回格式：
{
    "entities": ["实体列表"],
    "relations": [
        {"subject": "主体", "relation": "关系", "object": "客体"}
    ]
}"""

    response = model.generate_content(
        prompt, generation_config={"max_output_tokens": 300}
    )

    data = json.loads(response.text)

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

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        system_instruction="只返回JSON格式，不要添加markdown代码块。",
    )

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

    response = model.generate_content(
        prompt, generation_config={"max_output_tokens": 400}
    )

    data = json.loads(response.text)
    print("提取结果：")
    print(json.dumps(data, ensure_ascii=False, indent=2))


# ==================== 第四部分：事件提取 ====================


def event_extraction():
    """事件提取"""
    print("\n" + "=" * 60)
    print("第四部分：事件提取")
    print("=" * 60)

    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    model = genai.GenerativeModel(
        "gemini-2.0-flash", system_instruction="只返回JSON格式。"
    )

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

    response = model.generate_content(
        prompt, generation_config={"max_output_tokens": 400}
    )

    data = json.loads(response.text)
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

        ✅ 参考答案：
        ```
        请从以下商品描述中提取结构化信息：

        商品描述：
        \"\"\"
        【新品】Apple iPhone 15 Pro Max 256GB 钛金属原色
        官方售价：¥9999 起
        屏幕：6.7 英寸超视网膜 XDR 显示屏
        芯片：A17 Pro 仿生芯片
        相机：4800 万像素主摄 + 超广角 + 长焦
        \"\"\"

        请按以下格式提取：
        - 商品名称：
        - 品牌：
        - 型号：
        - 存储容量：
        - 颜色：
        - 价格：
        - 屏幕尺寸：
        - 处理器：
        - 相机规格：
        ```

    练习 2：会议纪要提取
        从会议记录中提取时间、参会人、议题、结论。

        ✅ 参考答案：
        ```
        请从以下会议记录中提取关键信息：

        会议记录：
        \"\"\"
        {会议记录文本}
        \"\"\"

        请提取并填充以下模板：
        
        【会议基本信息】
        - 会议主题：
        - 会议时间：
        - 会议地点/方式：
        - 主持人：
        
        【参会人员】
        - 出席人员：
        - 缺席人员：
        
        【议题与讨论】
        1. 议题一：
           - 主要观点：
           - 决议：
        
        【待办事项】
        | 任务 | 负责人 | 截止日期 |
        |------|--------|----------|
        
        【下次会议安排】
        ```

    练习 3：合同关键信息
        从合同文本中提取双方、金额、期限等关键条款。

        ✅ 参考答案：
        ```
        请从以下合同文本中提取关键条款：

        合同文本：
        \"\"\"
        {合同文本}
        \"\"\"

        请提取以下信息（如无则标注"未提及"）：
        
        【合同主体】
        - 甲方（全称）：
        - 甲方法定代表人：
        - 乙方（全称）：
        - 乙方法定代表人：
        
        【核心条款】
        - 合同标的：
        - 合同金额：
        - 付款方式：
        - 付款时间节点：
        
        【期限条款】
        - 合同签订日期：
        - 合同生效日期：
        - 合同有效期：
        - 续约条件：
        
        【违约与争议】
        - 违约责任：
        - 争议解决方式：
        - 管辖法院/仲裁机构：
        ```

    思考题：
        1. 如何处理信息缺失的情况？
           
           ✅ 答案：
           - 使用特定标记：如 "N/A"、"未提及"、null
           - 在输出中说明确信度
           - 区分"明确没有"和"文本未提及"
           - 建议用户补充缺失信息

        2. 如何提高提取的准确性？
           
           ✅ 答案：
           - 提供明确示例（Few-Shot）
           - 使用分隔符隔离原文和指令
           - 分步提取复杂信息
           - 使用正则表达式后处理验证
           - 对关键字段做二次确认
           - 使用 Schema 约束输出格式
    """)


# ==================== 主函数 ====================


def main():
    """主函数"""
    print("🚀 结构化信息提取 - Gemini 版本")
    print("=" * 60)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 GOOGLE_API_KEY")
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
