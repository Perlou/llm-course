"""
多模态分析演示脚本
==================

展示各个分析器的使用方法。
运行前请确保已安装依赖并配置 GOOGLE_API_KEY。
"""

import os
import sys
from pathlib import Path

# 添加项目目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from config import config


def demo_image_analyzer():
    """演示图像分析"""
    print("\n" + "=" * 60)
    print("📷 图像分析演示")
    print("=" * 60)

    from analyzers import ImageAnalyzer

    analyzer = ImageAnalyzer()

    code = '''
# 图像分析器使用示例
from analyzers import ImageAnalyzer

analyzer = ImageAnalyzer()

# 1. 描述图片
result = analyzer.describe("path/to/image.jpg")
print(result.description)

# 2. 检测物体
result = analyzer.detect_objects("path/to/image.jpg")
for obj in result.objects:
    print(f"- {obj['name']} ({obj['position']})")

# 3. 提取文字 (OCR)
result = analyzer.extract_text("path/to/document.png")
print(result.text)

# 4. 完整分析
result = analyzer.analyze_full("path/to/image.jpg")
print(result.description)
print(result.objects)
print(result.scene)
'''
    print(code)
    print("\n✅ 图像分析器已就绪，请提供图片进行分析")


def demo_chart_analyzer():
    """演示图表分析"""
    print("\n" + "=" * 60)
    print("📊 图表分析演示")
    print("=" * 60)

    from analyzers import ChartAnalyzer

    analyzer = ChartAnalyzer()

    code = '''
# 图表分析器使用示例
from analyzers import ChartAnalyzer

analyzer = ChartAnalyzer()

# 1. 分析图表
result = analyzer.analyze("chart.png")
print(f"图表类型: {result.chart_type}")
print(f"标题: {result.title}")
print(f"趋势: {result.trend}")

# 2. 提取数据
data = analyzer.extract_data("chart.png", output_format="json")
for item in data:
    print(f"{item['label']}: {item['value']}")

# 3. 趋势分析
analysis = analyzer.analyze_trend("chart.png", context="这是2024年的销售数据")
print(analysis)

# 4. 多图对比
report = analyzer.compare_charts(
    ["chart1.png", "chart2.png"],
    analysis_focus="同比增长"
)
print(report)
'''
    print(code)
    print("\n✅ 图表分析器已就绪，请提供图表进行分析")


def demo_video_analyzer():
    """演示视频分析"""
    print("\n" + "=" * 60)
    print("🎬 视频分析演示")
    print("=" * 60)

    try:
        from analyzers import VideoAnalyzer

        analyzer = VideoAnalyzer()
    except Exception as e:
        print(f"⚠️  注意: {e}")

    code = '''
# 视频分析器使用示例
from analyzers import VideoAnalyzer

analyzer = VideoAnalyzer()

# 1. 生成摘要
result = analyzer.summarize("video.mp4", num_frames=10)
print(f"时长: {result.duration}秒")
print(f"摘要: {result.summary}")

# 2. 帧分析
result = analyzer.analyze_frames("video.mp4", num_frames=10)
for frame in result.key_frames:
    print(f"{frame['timestamp_str']}: {frame['description']}")

# 3. 视频问答
answer = analyzer.answer_question(
    "video.mp4",
    question="视频中发生了什么？"
)
print(answer)

# 4. 场景检测
scenes = analyzer.detect_scenes("video.mp4", num_frames=20)
for scene in scenes:
    print(f"场景 {scene['scene_id']}: {scene['description']}")
'''
    print(code)
    print("\n✅ 视频分析器已就绪（需要 moviepy）")


def demo_audio_analyzer():
    """演示音频分析"""
    print("\n" + "=" * 60)
    print("🎙️ 音频分析演示")
    print("=" * 60)

    try:
        from analyzers import AudioAnalyzer

        analyzer = AudioAnalyzer(use_openai=False)
    except Exception as e:
        print(f"⚠️  注意: {e}")

    code = '''
# 音频分析器使用示例
from analyzers import AudioAnalyzer

analyzer = AudioAnalyzer()

# 1. 语音转文字
result = analyzer.transcribe("audio.mp3", language="zh")
print(result.transcript)

# 2. 内容分析
result = analyzer.analyze("podcast.mp3")
print(f"摘要: {result.summary}")
print(f"关键词: {result.keywords}")

# 3. 会议分析
result = analyzer.meeting_analysis("meeting.wav")
print(f"会议摘要: {result.summary}")
print(f"待办事项: {result.action_items}")
'''
    print(code)
    print("\n✅ 音频分析器已就绪（需要 openai 或 SpeechRecognition）")


def demo_multimodal_search():
    """演示多模态搜索"""
    print("\n" + "=" * 60)
    print("🔍 多模态搜索演示")
    print("=" * 60)

    code = '''
# 多模态搜索使用示例
from search import MultimodalSearch

search = MultimodalSearch()

# 1. 添加图片到索引
image_id = search.add_image(
    "product.jpg",
    metadata={"category": "电子产品"}
)

# 2. 文本搜索
results = search.search("红色的汽车", top_k=5)
for r in results:
    print(f"[{r.score:.2f}] {r.description}")

# 3. 以图搜图
results = search.search_by_image("query.jpg", top_k=5)
for r in results:
    print(f"[{r.score:.2f}] {r.image_path}")

# 4. 相似搜索
similar = search.search_similar(image_id, top_k=3)
for r in similar:
    print(f"相似: {r.description}")

# 5. 查看统计
stats = search.get_stats()
print(f"索引数量: {stats['total_count']}")
'''
    print(code)
    print("\n✅ 多模态搜索已就绪（需要 chromadb）")


def demo_api_service():
    """演示 API 服务"""
    print("\n" + "=" * 60)
    print("🌐 API 服务演示")
    print("=" * 60)

    code = '''
# 启动 API 服务
python app.py

# API 端点示例

# 1. 图像分析
curl -X POST "http://localhost:8000/api/analyze/image" \\
  -F "file=@image.jpg" \\
  -F "task=describe"

# 2. 图表分析
curl -X POST "http://localhost:8000/api/analyze/chart" \\
  -F "file=@chart.png"

# 3. 视频分析
curl -X POST "http://localhost:8000/api/analyze/video" \\
  -F "file=@video.mp4" \\
  -F "max_frames=10"

# 4. 音频分析
curl -X POST "http://localhost:8000/api/analyze/audio" \\
  -F "file=@audio.mp3" \\
  -F "language=zh"

# 5. 多模态搜索
curl -X POST "http://localhost:8000/api/search" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "红色汽车", "top_k": 5}'

# 查看完整 API 文档
# http://localhost:8000/docs
'''
    print(code)


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🖼️  多模态内容分析平台 - 功能演示")
    print("=" * 60)

    # 验证配置
    if not config.google_api_key:
        print("\n⚠️  警告: 未设置 GOOGLE_API_KEY")
        print("请复制 .env.example 为 .env 并填入 API Key")
        print("获取地址: https://aistudio.google.com/apikey\n")

    print(f"\n模型: {config.gemini_model}")
    print(f"数据目录: {config.data_dir}")

    # 演示各个功能
    demo_image_analyzer()
    demo_chart_analyzer()
    demo_video_analyzer()
    demo_audio_analyzer()
    demo_multimodal_search()
    demo_api_service()

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)
    print("""
下一步:
1. 配置 GOOGLE_API_KEY
2. 运行 python main.py 启动命令行界面
3. 或运行 python app.py 启动 API 服务
    """)


if __name__ == "__main__":
    main()
