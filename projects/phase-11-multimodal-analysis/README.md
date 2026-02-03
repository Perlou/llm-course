# 多模态内容分析平台

> 基于 Gemini 2.0 的多模态内容理解与分析应用

---

## 📋 项目简介

本项目是一个功能完整的多模态内容分析平台，利用 Google Gemini 2.0 的强大多模态能力，实现对图像、图表、视频、音频等多种模态内容的智能理解与分析。

### 核心能力

| 功能模块   | 描述                         | 技术点         |
| ---------- | ---------------------------- | -------------- |
| 图像理解   | 分析图片内容、场景、物体识别 | Gemini Vision  |
| 图表分析   | 从图表中提取数据、趋势分析   | 结构化输出     |
| 视频摘要   | 视频内容理解、关键帧提取     | 视频处理       |
| 音频转录   | 语音转文字、内容分析         | Speech-to-Text |
| 多模态搜索 | 图文混合检索                 | 向量检索       |

---

## 🛠️ 技术栈

- **Python 3.10+**
- **google-generativeai** - Gemini SDK
- **LangChain 0.3+** - 链式处理
- **ChromaDB** - 向量存储
- **Pillow** - 图像处理
- **MoviePy** - 视频处理
- **Rich** - 终端 UI

---

## 🚀 快速开始

### 1. 环境准备

```bash
cd projects/phase-11-multimodal-analysis

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env，填入你的 Gemini API Key
```

获取 API Key：[Google AI Studio](https://aistudio.google.com/apikey)

### 3. 运行应用

```bash
# 命令行模式
python main.py

# API 服务模式
python app.py
```

---

## 📁 项目结构

```
phase-11-multimodal-analysis/
├── README.md              # 项目文档
├── main.py                # 主入口 (CLI)
├── app.py                 # FastAPI 服务
├── config.py              # 配置管理
├── requirements.txt       # 依赖列表
├── .env.example           # 环境变量模板
│
├── analyzers/             # 分析器模块
│   ├── __init__.py
│   ├── image_analyzer.py  # 图像分析
│   ├── chart_analyzer.py  # 图表分析
│   ├── video_analyzer.py  # 视频分析
│   └── audio_analyzer.py  # 音频分析
│
├── search/                # 搜索模块
│   ├── __init__.py
│   ├── embeddings.py      # 向量嵌入
│   └── multimodal_search.py # 多模态搜索
│
├── data/                  # 数据目录
│   ├── images/            # 图片文件
│   ├── videos/            # 视频文件
│   └── audio/             # 音频文件
│
└── tests/                 # 测试用例
    └── test_analyzers.py
```

---

## 💡 功能详解

### 1. 图像内容描述

分析图像内容，识别场景、物体、文字等。

```python
from analyzers import ImageAnalyzer

analyzer = ImageAnalyzer()
result = analyzer.describe("path/to/image.jpg")
print(result.description)  # 详细描述
print(result.objects)      # 检测到的物体
print(result.text)         # 识别的文字
```

### 2. 图表数据提取

从图表中提取结构化数据。

```python
from analyzers import ChartAnalyzer

analyzer = ChartAnalyzer()
result = analyzer.analyze("quarterly_report.png")
print(result.chart_type)   # 图表类型
print(result.data)         # 提取的数据
print(result.insights)     # 数据洞察
```

### 3. 视频摘要生成

理解视频内容，生成摘要。

```python
from analyzers import VideoAnalyzer

analyzer = VideoAnalyzer()
result = analyzer.summarize("meeting.mp4")
print(result.summary)      # 视频摘要
print(result.key_frames)   # 关键帧
print(result.timestamps)   # 时间戳
```

### 4. 音频转录分析

语音转文字，并进行内容分析。

```python
from analyzers import AudioAnalyzer

analyzer = AudioAnalyzer()
result = analyzer.transcribe("interview.mp3")
print(result.transcript)   # 转录文本
print(result.summary)      # 内容摘要
print(result.keywords)     # 关键词
```

### 5. 多模态搜索

支持图片和文本混合检索。

```python
from search import MultimodalSearch

search = MultimodalSearch()
# 添加图片到索引
search.add_image("image.jpg", metadata={"category": "产品"})

# 文本搜索
results = search.search("红色的汽车")

# 图片搜索
results = search.search_by_image("query_image.jpg")
```

---

## 📊 API 接口

启动服务：`python app.py`

### 图像分析

```http
POST /api/analyze/image
Content-Type: multipart/form-data

file: <图片文件>
task: describe | extract_text | detect_objects
```

### 图表分析

```http
POST /api/analyze/chart
Content-Type: multipart/form-data

file: <图表图片>
output_format: json | markdown
```

### 视频分析

```http
POST /api/analyze/video
Content-Type: multipart/form-data

file: <视频文件>
max_frames: 10
```

### 多模态搜索

```http
POST /api/search
Content-Type: application/json

{
  "query": "搜索文本",
  "top_k": 5
}
```

---

## 📈 预期效果

```
📷 上传: quarterly_report.png

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 图表分析结果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

类型: 柱状图（分组）
标题: 2024年季度收入对比

┌────────┬───────────┬───────────┐
│ 季度   │ 产品收入  │ 服务收入  │
├────────┼───────────┼───────────┤
│ Q1     │ 1,234万   │ 567万     │
│ Q2     │ 1,567万   │ 678万     │
│ Q3     │ 1,890万   │ 756万     │
│ Q4     │ 2,345万   │ 890万     │
└────────┴───────────┴───────────┘

📈 趋势洞察:
  • 全年收入持续增长，Q4 增幅最大 (24%)
  • 产品收入占比约 70%，是主要收入来源
  • 服务收入增速略低，建议关注

✅ 分析完成
```

---

## 🎓 学习要点

1. **Gemini 多模态 API 使用**
   - 理解 Gemini 的图像/视频/音频输入方式
   - 掌握多模态 Prompt 设计

2. **结构化输出**
   - 使用 JSON Schema 约束输出格式
   - Pydantic 数据模型定义

3. **多模态检索**
   - CLIP 等跨模态嵌入
   - 图文联合索引策略

4. **媒体文件处理**
   - 图像预处理与压缩
   - 视频关键帧提取
   - 音频格式转换

---

## 📚 参考资料

- [Gemini API 文档](https://ai.google.dev/docs)
- [Gemini Cookbook](https://github.com/google-gemini/cookbook)
- [LangChain 多模态](https://python.langchain.com/docs/how_to/#multimodal)

---

## 🔧 下一步

- [ ] 添加批量处理支持
- [ ] 实现流式输出
- [ ] 添加结果缓存
- [ ] 支持更多文件格式
