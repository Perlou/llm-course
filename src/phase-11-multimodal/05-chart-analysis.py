"""
图表分析
========

学习目标：
    1. 使用多模态 LLM 分析各类图表
    2. 提取图表数据和趋势
    3. 生成图表洞察报告

核心概念：
    - 图表类型识别
    - 数据点提取
    - 趋势分析

环境要求：
    - pip install google-generativeai pillow matplotlib

📌 Gemini 迁移说明：
    本文件展示图表分析的核心概念。
    示例代码使用OpenAI API演示，Gemini等价实现参考02-gpt4-vision.py顶部说明。
"""

import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()


# ==================== 第一部分：图表分析概述 ====================


def introduction():
    """图表分析概述"""
    print("=" * 60)
    print("第一部分：图表分析概述")
    print("=" * 60)

    print("""
    📌 支持的图表类型：
    ┌─────────────┬───────────────────────────────────────┐
    │ 折线图      │ 趋势分析、时间序列                   │
    │ 柱状图      │ 对比分析、分类统计                   │
    │ 饼图        │ 占比分析、构成分析                   │
    │ 散点图      │ 相关性分析、分布分析                 │
    │ 热力图      │ 密度分析、矩阵可视化                 │
    │ 组合图      │ 多维度分析                           │
    └─────────────┴───────────────────────────────────────┘

    📌 分析任务：
    1. 识别图表类型
    2. 读取坐标轴和图例
    3. 提取数据点
    4. 分析趋势和模式
    5. 生成洞察报告
    """)


# ==================== 第二部分：基础图表分析 ====================


def basic_analysis():
    """基础图表分析"""
    print("\n" + "=" * 60)
    print("第二部分：基础图表分析")
    print("=" * 60)

    code = '''
from openai import OpenAI
import base64

client = OpenAI()

def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def analyze_chart(image_path: str) -> dict:
    """分析图表并提取信息"""
    image_base64 = encode_image(image_path)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """分析这张图表，返回 JSON 格式：

{
    "chart_type": "图表类型",
    "title": "图表标题",
    "x_axis": {
        "label": "X轴标签",
        "range": "数值范围或类别"
    },
    "y_axis": {
        "label": "Y轴标签",
        "range": "数值范围"
    },
    "legend": ["图例项"],
    "data_summary": "数据概要描述",
    "key_insights": ["关键发现列表"],
    "trend": "整体趋势描述"
}"""
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


# ==================== 第三部分：数据提取 ====================


def data_extraction():
    """数据提取"""
    print("\n" + "=" * 60)
    print("第三部分：从图表提取数据")
    print("=" * 60)

    code = '''
def extract_chart_data(image_path: str) -> dict:
    """从图表中提取具体数据点"""
    image_base64 = encode_image(image_path)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """请从图表中提取所有可读的数据点。

返回格式：
{
    "chart_type": "图表类型",
    "data": [
        {"label": "标签/X值", "value": 数值, "series": "系列名(如有)"}
    ],
    "statistics": {
        "max": {"label": "最大值标签", "value": 最大值},
        "min": {"label": "最小值标签", "value": 最小值},
        "average": 平均值(如可计算)
    },
    "notes": "特殊标注或注释"
}

尽可能精确读取数值，如果无法确定精确值，给出估计值并标注。"""
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
        max_tokens=2000
    )

    import json
    return json.loads(response.choices[0].message.content)
'''
    print(code)


# ==================== 第四部分：趋势分析 ====================


def trend_analysis():
    """趋势分析"""
    print("\n" + "=" * 60)
    print("第四部分：趋势分析")
    print("=" * 60)

    code = '''
def analyze_trend(image_path: str, context: str = "") -> str:
    """分析图表趋势并生成洞察"""
    image_base64 = encode_image(image_path)

    prompt = f"""分析这张图表的趋势，提供专业的数据分析洞察。

背景信息：{context if context else "无"}

请从以下方面分析：
1. 整体趋势（上升/下降/平稳/波动）
2. 关键转折点
3. 异常值或特殊点
4. 周期性模式（如有）
5. 与预期的对比（如有背景信息）
6. 可能的原因分析
7. 未来趋势预测
8. 行动建议

用专业但易懂的语言回答。"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
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

    return response.choices[0].message.content

# 使用示例
# insight = analyze_trend("sales_chart.png", "这是2024年的月度销售数据")
'''
    print(code)


# ==================== 第五部分：多图对比 ====================


def multi_chart_comparison():
    """多图对比"""
    print("\n" + "=" * 60)
    print("第五部分：多图表对比分析")
    print("=" * 60)

    code = '''
def compare_charts(images: list, analysis_focus: str = "") -> str:
    """对比分析多个图表"""
    content = []

    prompt = f"""对比分析以下图表。

分析重点：{analysis_focus if analysis_focus else "全面对比"}

请从以下方面进行对比：
1. 数据范围和规模对比
2. 趋势一致性或差异
3. 相关性分析
4. 共同模式发现
5. 差异点及可能原因
6. 综合结论"""

    content.append({"type": "text", "text": prompt})

    for i, img_path in enumerate(images):
        image_base64 = encode_image(img_path)
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
        max_tokens=2000
    )

    return response.choices[0].message.content
'''
    print(code)


# ==================== 第六部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现财务报表图表分析函数

        ✅ 参考答案：
        ```python
        import google.generativeai as genai
        from PIL import Image
        from typing import Dict
        
        class FinancialChartAnalyzer:
            '''财务报表图表分析器'''
            
            def __init__(self, api_key: str):
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
            
            def analyze_financial_chart(
                self, 
                image_path: str,
                chart_type: str = "auto"
            ) -> Dict:
                '''分析财务图表'''
                img = Image.open(image_path)
                
                prompt = '''分析这张财务图表，返回 JSON：
{
    "chart_type": "图表类型（折线图/柱状图/饼图）",
    "title": "图表标题",
    "time_period": "时间范围",
    "metrics": ["包含的财务指标"],
    "data_points": [
        {"period": "时间点", "value": 数值, "unit": "单位"}
    ],
    "analysis": {
        "trend": "整体趋势（上升/下降/波动）",
        "growth_rate": "增长率（如可计算）",
        "peak": {"period": "最高点时间", "value": 最大值},
        "trough": {"period": "最低点时间", "value": 最小值},
        "average": "平均值（如可计算）"
    },
    "insights": ["关键发现列表"],
    "recommendations": ["建议事项"]
}'''
                
                response = self.model.generate_content([prompt, img])
                
                import json
                return json.loads(response.text)
            
            def compare_financial_charts(
                self, 
                image_paths: list,
                context: str = ""
            ) -> str:
                '''对比多个财务图表'''
                content = [f'''对比分析以下财务图表。
背景信息：{context if context else "无"}

请提供：
1. 各图表反映的财务状况
2. 趋势一致性或差异
3. 相关性分析
4. 潜在风险点
5. 投资/经营建议''']
                
                for path in image_paths:
                    img = Image.open(path)
                    content.append(img)
                
                response = self.model.generate_content(content)
                return response.text
        
        # 使用示例
        # analyzer = FinancialChartAnalyzer(os.getenv("GOOGLE_API_KEY"))
        # result = analyzer.analyze_financial_chart("revenue_chart.png")
        # print(f"趋势: {result['analysis']['trend']}")
        ```
    
    练习 2：构建图表数据到 Excel 的导出功能

        ✅ 参考答案：
        ```python
        import pandas as pd
        from openpyxl import Workbook
        from openpyxl.chart import LineChart, Reference
        
        class ChartToExcel:
            '''图表数据导出到 Excel'''
            
            def __init__(self, api_key: str):
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
            
            def extract_data(self, image_path: str) -> Dict:
                '''从图表提取数据'''
                img = Image.open(image_path)
                
                prompt = '''从这张图表中提取所有数据点。
返回 JSON 格式：
{
    "title": "图表标题",
    "columns": ["列名1", "列名2", ...],
    "data": [
        ["值1", "值2", ...],
        ...
    ]
}
请尽可能精确读取数值。'''
                
                response = self.model.generate_content([prompt, img])
                
                import json
                return json.loads(response.text)
            
            def export_to_excel(
                self, 
                image_path: str, 
                output_path: str
            ) -> str:
                '''导出图表数据到 Excel'''
                # 提取数据
                data = self.extract_data(image_path)
                
                # 创建 DataFrame
                df = pd.DataFrame(
                    data['data'], 
                    columns=data['columns']
                )
                
                # 导出到 Excel
                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='数据', index=False)
                    
                    # 获取工作簿和工作表
                    workbook = writer.book
                    worksheet = writer.sheets['数据']
                    
                    # 添加图表（如果有数值列）
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if len(numeric_cols) > 0:
                        chart = LineChart()
                        chart.title = data.get('title', '数据图表')
                        
                        data_ref = Reference(
                            worksheet,
                            min_col=2,
                            max_col=len(df.columns),
                            min_row=1,
                            max_row=len(df) + 1
                        )
                        chart.add_data(data_ref, titles_from_data=True)
                        worksheet.add_chart(chart, "E2")
                
                return output_path
        
        # 使用示例
        # exporter = ChartToExcel(os.getenv("GOOGLE_API_KEY"))
        # exporter.export_to_excel("sales_chart.png", "sales_data.xlsx")
        ```

    思考题：多模态 LLM 分析图表的精度如何保证？

        ✅ 答：
        1. 高分辨率输入 - 使用 detail="high" 或高清图片
        2. 置信度标注 - 要求模型标注估计值的置信度
        3. 多次采样 - 多次请求取平均值或众数
        4. 人工验证 - 关键数据进行人工复核
        5. 原始数据校验 - 有条件时与原始数据源对比
        6. 结构化输出 - 使用 JSON 格式减少解析错误
    """)


def main():
    introduction()
    basic_analysis()
    data_extraction()
    trend_analysis()
    multi_chart_comparison()
    exercises()
    print("\n课程完成！下一步：06-video-understanding.py")


if __name__ == "__main__":
    main()
