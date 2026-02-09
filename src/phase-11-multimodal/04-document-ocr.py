"""
文档 OCR 处理
============

学习目标：
    1. 使用多模态 LLM 进行文档 OCR
    2. 处理不同类型的文档（发票、合同、表格等）
    3. 结构化提取文档信息

核心概念：
    - OCR (Optical Character Recognition)
    - 文档结构理解
    - 信息抽取

环境要求：
    - pip install openai pillow pdf2image

📌 Gemini 迁移说明：
    本文件展示文档OCR的核心概念。
    示例代码使用OpenAI API演示，Gemini等价实现参考02-gpt4-vision.py顶部说明。ge
"""

import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：OCR 概述 ====================


def introduction():
    """OCR 概述"""
    print("=" * 60)
    print("第一部分：文档 OCR 概述")
    print("=" * 60)

    print("""
    📌 传统 OCR vs 多模态 LLM OCR：
    ┌──────────────┬──────────────────┬──────────────────┐
    │              │    传统 OCR      │  多模态 LLM      │
    ├──────────────┼──────────────────┼──────────────────┤
    │ 文字识别     │ ✅ 准确          │ ✅ 准确          │
    │ 版面理解     │ ❌ 有限          │ ✅ 理解结构      │
    │ 语义理解     │ ❌ 不支持        │ ✅ 理解含义      │
    │ 信息抽取     │ ❌ 需规则        │ ✅ 自动抽取      │
    │ 多语言       │ 需要专门模型     │ ✅ 原生支持      │
    └──────────────┴──────────────────┴──────────────────┘

    📌 适用场景：
    - 发票/收据识别
    - 合同信息提取
    - 表格数据抽取
    - 证件信息识别
    - 文档问答
    """)


# ==================== 第二部分：基础 OCR ====================


def basic_ocr():
    """基础 OCR"""
    print("\n" + "=" * 60)
    print("第二部分：基础文字识别")
    print("=" * 60)

    code = '''
from openai import OpenAI
import base64

client = OpenAI()

def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def extract_text(image_path: str) -> str:
    """从图片中提取所有文字"""
    image_base64 = encode_image(image_path)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """请识别并提取图片中的所有文字。
要求：
1. 保持原有的排版格式
2. 区分标题、正文、注释等
3. 表格内容用表格格式表示
4. 如有手写文字，尽量识别"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                            "detail": "high"  # 高分辨率模式
                        }
                    }
                ]
            }
        ],
        max_tokens=2000
    )

    return response.choices[0].message.content
'''
    print(code)


# ==================== 第三部分：发票识别 ====================


def invoice_recognition():
    """发票识别"""
    print("\n" + "=" * 60)
    print("第三部分：发票识别")
    print("=" * 60)

    code = '''
def extract_invoice_info(image_path: str) -> dict:
    """提取发票信息"""
    image_base64 = encode_image(image_path)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """请识别这张发票，提取以下信息并返回 JSON：
{
    "invoice_code": "发票代码",
    "invoice_number": "发票号码",
    "invoice_date": "开票日期",
    "seller": {
        "name": "销售方名称",
        "tax_id": "纳税人识别号"
    },
    "buyer": {
        "name": "购买方名称",
        "tax_id": "纳税人识别号"
    },
    "items": [
        {"name": "商品名称", "quantity": 数量, "unit_price": 单价, "amount": 金额}
    ],
    "total_amount": "合计金额",
    "tax_amount": "税额",
    "total_with_tax": "价税合计"
}

如果某项信息无法识别，填写 null。"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ],
        max_tokens=1500
    )

    import json
    return json.loads(response.choices[0].message.content)
'''
    print(code)


# ==================== 第四部分：表格提取 ====================


def table_extraction():
    """表格提取"""
    print("\n" + "=" * 60)
    print("第四部分：表格数据提取")
    print("=" * 60)

    code = '''
def extract_table(image_path: str, output_format: str = "markdown") -> str:
    """从图片中提取表格"""
    image_base64 = encode_image(image_path)

    format_prompts = {
        "markdown": "请用 Markdown 表格格式输出",
        "csv": "请用 CSV 格式输出，用逗号分隔",
        "json": "请用 JSON 数组格式输出，每行是一个对象"
    }

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""识别图片中的表格数据。
{format_prompts.get(output_format, format_prompts['markdown'])}

要求：
1. 准确识别每个单元格的内容
2. 保持表格的行列结构
3. 合并单元格需要正确处理"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ],
        max_tokens=3000
    )

    return response.choices[0].message.content

# 使用示例
# table_md = extract_table("spreadsheet.png", "markdown")
# table_csv = extract_table("spreadsheet.png", "csv")
'''
    print(code)


# ==================== 第五部分：合同分析 ====================


def contract_analysis():
    """合同分析"""
    print("\n" + "=" * 60)
    print("第五部分：合同文档分析")
    print("=" * 60)

    code = '''
def analyze_contract(image_paths: list) -> dict:
    """分析合同文档（支持多页）"""
    content = [{
        "type": "text",
        "text": """分析这份合同文档，提取以下关键信息：

{
    "contract_type": "合同类型",
    "parties": [
        {"role": "甲方/乙方", "name": "名称", "address": "地址"}
    ],
    "subject": "合同标的",
    "amount": "合同金额",
    "duration": {
        "start": "开始日期",
        "end": "结束日期"
    },
    "key_terms": ["关键条款列表"],
    "payment_terms": "付款条款",
    "liability": "违约责任",
    "risks": ["潜在风险点"]
}"""
    }]

    for path in image_paths:
        image_base64 = encode_image(path)
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_base64}",
                "detail": "high"
            }
        })

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": content}],
        max_tokens=3000
    )

    import json
    return json.loads(response.choices[0].message.content)
'''
    print(code)


# ==================== 第六部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现身份证/名片信息提取函数

        ✅ 参考答案：
        ```python
        import google.generativeai as genai
        from PIL import Image
        from typing import Dict
        
        class IDCardExtractor:
            '''身份证/名片信息提取器'''
            
            def __init__(self, api_key: str):
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            def extract_id_card(self, image_path: str) -> Dict:
                '''提取身份证信息'''
                img = Image.open(image_path)
                
                prompt = '''识别这张身份证，提取信息并返回 JSON：
{
    "name": "姓名",
    "gender": "性别",
    "ethnicity": "民族",
    "birth_date": "出生日期 (YYYY-MM-DD)",
    "address": "住址",
    "id_number": "身份证号",
    "issuing_authority": "签发机关（如有）",
    "valid_period": "有效期限（如有）",
    "side": "正面/背面"
}
注意：保护隐私，部分信息可用 * 遮挡。'''
                
                response = self.model.generate_content([prompt, img])
                
                import json
                return json.loads(response.text)
            
            def extract_business_card(self, image_path: str) -> Dict:
                '''提取名片信息'''
                img = Image.open(image_path)
                
                prompt = '''识别这张名片，提取信息并返回 JSON：
{
    "name": "姓名",
    "title": "职位",
    "company": "公司名称",
    "department": "部门",
    "phone": ["电话号码列表"],
    "email": "邮箱",
    "address": "地址",
    "website": "网站",
    "social_media": {"微信": "...", "其他": "..."}
}'''
                
                response = self.model.generate_content([prompt, img])
                
                import json
                return json.loads(response.text)
        
        # 使用示例
        # extractor = IDCardExtractor(os.getenv("GOOGLE_API_KEY"))
        # id_info = extractor.extract_id_card("id_card.jpg")
        # card_info = extractor.extract_business_card("business_card.jpg")
        ```
    
    练习 2：实现多页 PDF 的批量 OCR 处理

        ✅ 参考答案：
        ```python
        from pdf2image import convert_from_path
        import tempfile
        import os
        
        class PDFBatchOCR:
            '''PDF 批量 OCR 处理器'''
            
            def __init__(self, api_key: str):
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            def pdf_to_images(
                self, 
                pdf_path: str, 
                dpi: int = 200
            ) -> list:
                '''将 PDF 转换为图片'''
                images = convert_from_path(pdf_path, dpi=dpi)
                return images
            
            def ocr_page(self, image) -> str:
                '''OCR 单页'''
                prompt = '''请识别这页文档中的所有文字。
保持原有格式，区分标题、正文、表格等。'''
                
                response = self.model.generate_content([prompt, image])
                return response.text
            
            def ocr_pdf(
                self, 
                pdf_path: str,
                output_format: str = "text"
            ) -> Dict:
                '''OCR 整个 PDF'''
                images = self.pdf_to_images(pdf_path)
                
                results = []
                full_text = []
                
                for i, img in enumerate(images):
                    text = self.ocr_page(img)
                    results.append({
                        'page': i + 1,
                        'text': text
                    })
                    full_text.append(f"=== 第 {i+1} 页 ===\\n{text}")
                
                return {
                    'total_pages': len(images),
                    'pages': results,
                    'full_text': "\\n\\n".join(full_text)
                }
            
            def extract_structure(self, pdf_path: str) -> Dict:
                '''提取文档结构'''
                images = self.pdf_to_images(pdf_path)
                
                # 只分析第一页获取目录结构
                prompt = '''分析这个文档的结构，返回 JSON：
{
    "title": "文档标题",
    "type": "文档类型（合同/报告/论文等）",
    "sections": ["章节列表"],
    "summary": "内容概要"
}'''
                
                response = self.model.generate_content([prompt, images[0]])
                
                import json
                return json.loads(response.text)
        
        # 使用示例
        # ocr = PDFBatchOCR(os.getenv("GOOGLE_API_KEY"))
        # result = ocr.ocr_pdf("document.pdf")
        # print(f"共 {result['total_pages']} 页")
        # print(result['full_text'])
        ```

    思考题：多模态 LLM OCR 的优势和局限是什么？

        ✅ 答：
        优势：
        1. 语义理解 - 不仅识别文字，还理解含义
        2. 信息抽取 - 自动提取关键字段
        3. 复杂版面 - 处理表格、多栏、混合布局
        4. 多语言 - 原生支持多种语言混排
        5. 问答能力 - 可以就文档内容提问
        
        局限：
        1. 成本较高 - 按 token 计费，大量文档成本高
        2. 速度较慢 - 比传统 OCR 延迟更高
        3. 长文档限制 - 需要分页处理
        4. 手写识别 - 复杂手写准确率有限
        5. 隐私风险 - 数据发送到云端处理
    """)


def main():
    introduction()
    basic_ocr()
    invoice_recognition()
    table_extraction()
    contract_analysis()
    exercises()
    print("\n课程完成！下一步：05-chart-analysis.py")


if __name__ == "__main__":
    main()
