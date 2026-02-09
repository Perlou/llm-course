"""
监控与日志
==========

学习目标：
    1. 设计 LLM 服务监控指标
    2. 实现 Prometheus 指标暴露
    3. 配置日志规范

核心概念：
    - Prometheus：指标收集系统
    - Grafana：可视化面板
    - 结构化日志：JSON 格式日志

环境要求：
    - pip install prometheus-client
    - Prometheus + Grafana（可选）
"""

import time
import json
import logging


# ==================== 第一部分：监控指标体系 ====================


def introduction():
    """监控指标体系"""
    print("=" * 60)
    print("第一部分：监控指标体系")
    print("=" * 60)

    print("""
    📌 监控指标金字塔：
    ┌─────────────────────────────────────────────────────────┐
    │                    ┌─────────┐                          │
    │                    │ 业务指标 │ ← 成功率、用户满意度    │
    │                    └────┬────┘                          │
    │               ┌─────────┴─────────┐                     │
    │               │     性能指标       │ ← 延迟/吞吐        │
    │               └─────────┬─────────┘                     │
    │          ┌──────────────┴──────────────┐                │
    │          │         资源指标            │ ← GPU/内存     │
    │          └──────────────┬──────────────┘                │
    │     ┌───────────────────┴───────────────────┐           │
    │     │              基础设施                 │ ← 节点    │
    │     └───────────────────────────────────────┘           │
    └─────────────────────────────────────────────────────────┘

    📌 关键指标：
    ┌─────────────────────┬──────────┬────────────┐
    │       指标名称       │   类型   │   告警阈值  │
    ├─────────────────────┼──────────┼────────────┤
    │ llm_request_latency │ Histogram│ P99 > 30s  │
    │ llm_ttft_seconds    │ Histogram│ P95 > 3s   │
    │ llm_tokens_per_sec  │ Gauge    │ < 10       │
    │ llm_queue_size      │ Gauge    │ > 100      │
    │ gpu_memory_used     │ Gauge    │ > 90%      │
    │ llm_error_total     │ Counter  │ 错误率>1%  │
    └─────────────────────┴──────────┴────────────┘
    """)


# ==================== 第二部分：Prometheus 集成 ====================


def prometheus_integration():
    """Prometheus 集成"""
    print("\n" + "=" * 60)
    print("第二部分：Prometheus 集成")
    print("=" * 60)

    code = """
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import FastAPI, Response
import time

app = FastAPI()

# 定义指标
REQUEST_COUNT = Counter(
    "llm_request_total", "Total requests",
    ["model", "status"]
)
REQUEST_LATENCY = Histogram(
    "llm_request_latency_seconds", "Request latency",
    buckets=[0.5, 1, 2, 5, 10, 30, 60]
)
TTFT = Histogram(
    "llm_ttft_seconds", "Time to first token",
    buckets=[0.1, 0.5, 1, 2, 5]
)
QUEUE_SIZE = Gauge(
    "llm_queue_size", "Current queue size"
)

# 暴露指标端点
@app.get("/metrics")
async def metrics():
    return Response(
        generate_latest(),
        media_type="text/plain"
    )

# 使用示例
@app.post("/v1/chat/completions")
async def chat(request):
    start = time.time()
    try:
        result = await generate(request)
        REQUEST_COUNT.labels(model="qwen2", status="success").inc()
        return result
    finally:
        REQUEST_LATENCY.observe(time.time() - start)
"""
    print(code)


# ==================== 第三部分：结构化日志 ====================


def structured_logging():
    """结构化日志"""
    print("\n" + "=" * 60)
    print("第三部分：结构化日志")
    print("=" * 60)

    print("""
    📌 日志格式规范（JSON）：

    请求日志：
    {
      "timestamp": "2024-01-15T10:30:00.000Z",
      "level": "INFO",
      "trace_id": "abc-123",
      "event": "inference_complete",
      "model": "qwen2-7b",
      "input_tokens": 256,
      "output_tokens": 512,
      "ttft_ms": 180,
      "total_ms": 3200,
      "status": "success"
    }

    错误日志：
    {
      "timestamp": "2024-01-15T10:31:00.000Z",
      "level": "ERROR",
      "trace_id": "xyz-789",
      "event": "inference_failed",
      "error_type": "OOMError",
      "error_message": "CUDA out of memory"
    }
    """)

    code = """
import structlog
import logging

# 配置结构化日志
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.BoundLogger,
    logger_factory=structlog.PrintLoggerFactory()
)

logger = structlog.get_logger()

# 使用
logger.info(
    "inference_complete",
    model="qwen2-7b",
    input_tokens=256,
    output_tokens=512,
    total_ms=3200
)
"""
    print(code)


# ==================== 第四部分：监控栈部署 ====================


def monitoring_stack():
    """监控栈部署"""
    print("\n" + "=" * 60)
    print("第四部分：监控栈部署")
    print("=" * 60)

    print("""
    📌 可观测性架构：
    ┌─────────────────────────────────────────────────────────┐
    │  应用指标 ──→ Prometheus ──→ Grafana                   │
    │                    ↓                                    │
    │              AlertManager ──→ 钉钉/Slack               │
    │                                                         │
    │  应用日志 ──→ Fluent Bit ──→ Loki ──→ Grafana          │
    │                                                         │
    │  GPU监控 ──→ DCGM Exporter ──→ Prometheus              │
    └─────────────────────────────────────────────────────────┘

    # Prometheus 配置（prometheus.yml）
    scrape_configs:
      - job_name: 'llm-service'
        static_configs:
          - targets: ['localhost:8000']
        metrics_path: /metrics
        scrape_interval: 15s
    """)


# ==================== 第五部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：为 FastAPI 服务添加 Prometheus 指标

        ✅ 参考答案：
        ```python
        from fastapi import FastAPI, Response
        from prometheus_client import (
            Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
        )
        import time
        
        app = FastAPI()
        
        # 定义指标
        REQUEST_TOTAL = Counter(
            "llm_request_total",
            "Total number of requests",
            ["model", "status"]
        )
        
        REQUEST_LATENCY = Histogram(
            "llm_request_latency_seconds",
            "Request latency in seconds",
            buckets=[0.5, 1, 2, 5, 10, 30, 60, 120]
        )
        
        TTFT = Histogram(
            "llm_ttft_seconds",
            "Time to first token",
            buckets=[0.1, 0.2, 0.5, 1, 2, 5]
        )
        
        TOKENS_PER_SECOND = Gauge(
            "llm_tokens_per_second",
            "Token generation speed"
        )
        
        QUEUE_SIZE = Gauge(
            "llm_queue_size",
            "Current request queue size"
        )
        
        # 暴露指标端点
        @app.get("/metrics")
        def metrics():
            return Response(
                generate_latest(),
                media_type=CONTENT_TYPE_LATEST
            )
        
        # 使用装饰器记录指标
        @app.post("/v1/chat/completions")
        async def chat(request: ChatRequest):
            start = time.time()
            try:
                result = await generate(request)
                REQUEST_TOTAL.labels(
                    model=request.model,
                    status="success"
                ).inc()
                return result
            except Exception as e:
                REQUEST_TOTAL.labels(
                    model=request.model,
                    status="error"
                ).inc()
                raise
            finally:
                REQUEST_LATENCY.observe(time.time() - start)
        ```
    
    练习 2：配置 Grafana 仪表板展示 LLM 关键指标

        ✅ 参考答案：
        ```json
        {
          "dashboard": {
            "title": "LLM Service Dashboard",
            "panels": [
              {
                "title": "请求 QPS",
                "type": "graph",
                "targets": [{
                  "expr": "rate(llm_request_total[1m])"
                }]
              },
              {
                "title": "P99 延迟",
                "type": "graph",
                "targets": [{
                  "expr": "histogram_quantile(0.99, rate(llm_request_latency_seconds_bucket[5m]))"
                }]
              },
              {
                "title": "TTFT P95",
                "type": "graph",
                "targets": [{
                  "expr": "histogram_quantile(0.95, rate(llm_ttft_seconds_bucket[5m]))"
                }]
              },
              {
                "title": "队列大小",
                "type": "stat",
                "targets": [{
                  "expr": "llm_queue_size"
                }]
              },
              {
                "title": "错误率",
                "type": "graph",
                "targets": [{
                  "expr": "rate(llm_request_total{status='error'}[5m]) / rate(llm_request_total[5m])"
                }]
              }
            ]
          }
        }
        ```

    思考题：TTFT（首 Token 延迟）为什么是重要指标？

        ✅ 答：
        1. 用户感知 - 直接影响用户等待体验
        2. 流式核心 - 决定流式响应何时开始
        3. 预填充性能 - 反映模型加载和预处理效率
        4. 长短请求区分 - 与总延迟配合分析请求类型
        5. SLA 关键指标 - 通常用于定义服务质量
    """)


def main():
    introduction()
    prometheus_integration()
    structured_logging()
    monitoring_stack()
    exercises()
    print("\n课程完成！下一步：10-security-guardrails.py")


if __name__ == "__main__":
    main()
