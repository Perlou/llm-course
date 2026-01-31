# Phase 9: LLM部署与生产化

> **学习目标**：掌握 LLM 应用的生产部署，从推理优化到安全合规的完整链路

---

## 1. 推理加速

### 1.1 模型量化

#### 为什么需要量化？

```
原始模型 (FP32)          量化后 (INT4)
┌─────────────────┐      ┌─────────────────┐
│ 7B × 4 bytes    │      │ 7B × 0.5 bytes  │
│ = 28 GB         │  →   │ = 3.5 GB        │
│ 需要A100        │      │ 消费级GPU可跑   │
└─────────────────┘      └─────────────────┘
```

#### 量化方法对比

| 方法     | 原理          | 精度损失 | 适用场景     |
| -------- | ------------- | -------- | ------------ |
| **FP16** | 半精度浮点    | 几乎无   | 基准方案     |
| **INT8** | 8位整数       | 极小     | 生产首选     |
| **GPTQ** | 逐层量化+校准 | 小       | 离线量化     |
| **AWQ**  | 保护重要权重  | 更小     | 质量优先     |
| **GGUF** | llama.cpp格式 | 可调     | CPU/边缘部署 |

#### 量化选择决策

```
                    精度要求高？
                        │
              ┌────是────┴────否────┐
              ↓                     ↓
           FP16/INT8            INT4量化
              │                     │
              │              ┌──────┴──────┐
              │              ↓             ↓
              │           GPU部署       CPU部署
              │           AWQ/GPTQ       GGUF
              ↓              ↓             ↓
         显存充足时      显存受限时     边缘设备
```

#### 量化实践要点

```python
# GPTQ 量化关键参数
quantize_config = {
    "bits": 4,              # 量化位数
    "group_size": 128,      # 分组大小，越小精度越高
    "desc_act": True,       # 激活值降序处理
    "dataset": "c4"         # 校准数据集
}

# AWQ 量化关键参数
awq_config = {
    "w_bit": 4,
    "q_group_size": 128,
    "zero_point": True,     # 零点量化
    "version": "GEMM"       # 计算版本
}
```

---

### 1.2 vLLM 部署

#### vLLM 核心优势

```
┌─────────────────────────────────────────────────────────┐
│                    vLLM 技术栈                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐    ┌─────────────────┐            │
│  │ PagedAttention  │    │ Continuous      │            │
│  │ 显存零碎片      │    │ Batching        │            │
│  │ 利用率提升2-4x  │    │ 动态批处理      │            │
│  └─────────────────┘    └─────────────────┘            │
│                                                         │
│  ┌─────────────────┐    ┌─────────────────┐            │
│  │ Tensor Parallel │    │ OpenAI兼容API   │            │
│  │ 多卡并行推理    │    │ 无缝迁移        │            │
│  └─────────────────┘    └─────────────────┘            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### PagedAttention 原理

```
传统KV Cache：                  PagedAttention：
┌────────────────────┐         ┌────┬────┬────┬────┐
│ Seq1: ████████░░░░ │         │物理页池              │
│ Seq2: ██████░░░░░░ │         ├────┴────┴────┴────┤
│ Seq3: ████░░░░░░░░ │         │ Seq1 → [P1,P3,P5] │
│     显存碎片严重   │         │ Seq2 → [P2,P4]    │
└────────────────────┘         │ Seq3 → [P6]       │
                               │   按需分配，无浪费  │
                               └────────────────────┘
```

#### 部署配置

```bash
# 基础启动
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2-7B-Instruct \
    --port 8000

# 生产级配置
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2-7B-Instruct \
    --tensor-parallel-size 2 \          # 2卡并行
    --max-model-len 8192 \              # 最大上下文
    --gpu-memory-utilization 0.9 \      # 显存利用率
    --max-num-seqs 64 \                 # 最大并发
    --enable-chunked-prefill            # 分块预填充
```

#### 关键参数调优

| 参数                     | 说明           | 建议值       |
| ------------------------ | -------------- | ------------ |
| `gpu-memory-utilization` | 显存使用比例   | 0.85-0.95    |
| `max-num-seqs`           | 最大并发序列   | 根据显存调整 |
| `max-model-len`          | 最大序列长度   | 按需设置     |
| `enforce-eager`          | 禁用CUDA Graph | 调试时开启   |

---

### 1.3 TGI 部署

#### TGI vs vLLM 对比

| 特性         | TGI                | vLLM          |
| ------------ | ------------------ | ------------- |
| **生态**     | HuggingFace原生    | 独立项目      |
| **功能**     | 功能丰富（水印等） | 专注推理性能  |
| **性能**     | 优秀               | 更优          |
| **量化支持** | GPTQ/AWQ/EETQ      | GPTQ/AWQ/FP8  |
| **部署方式** | Docker优先         | Python/Docker |

#### TGI 快速部署

```bash
# Docker 一键部署
docker run --gpus all \
    -v ~/.cache/huggingface:/data \
    -p 8080:80 \
    ghcr.io/huggingface/text-generation-inference:latest \
    --model-id Qwen/Qwen2-7B-Instruct \
    --max-input-length 4096 \
    --max-total-tokens 8192 \
    --max-batch-prefill-tokens 4096
```

#### TGI 特色功能

```
┌─────────────────────────────────────────┐
│            TGI 独特功能                 │
├─────────────────────────────────────────┤
│ • Token 流式输出                        │
│ • 输出水印（用于追踪）                   │
│ • 多LoRA动态加载                        │
│ • 内置Prometheus指标                    │
│ • Flash Attention 2 支持               │
│ • Paged Attention 支持                 │
└─────────────────────────────────────────┘
```

---

## 2. 服务化

### 2.1 FastAPI 服务

#### 服务架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI 服务层                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐           │
│   │  路由   │ →  │ 中间件  │ →  │ 处理器  │           │
│   │ Router  │    │Middleware│   │ Handler │           │
│   └─────────┘    └─────────┘    └─────────┘           │
│        │              │              │                 │
│        ↓              ↓              ↓                 │
│   ┌─────────────────────────────────────────┐         │
│   │           推理引擎 (vLLM/TGI)            │         │
│   └─────────────────────────────────────────┘         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### 核心代码结构

```python
# 项目结构
llm-service/
├── app/
│   ├── main.py           # 入口
│   ├── routers/          # 路由
│   │   ├── chat.py
│   │   └── completions.py
│   ├── models/           # 数据模型
│   │   └── schemas.py
│   ├── services/         # 业务逻辑
│   │   └── llm_service.py
│   └── middleware/       # 中间件
│       ├── auth.py
│       └── rate_limit.py
├── config.py
└── requirements.txt
```

#### 请求/响应模型

```python
# 请求模型
class ChatRequest(BaseModel):
    messages: List[Message]
    model: str = "qwen2-7b"
    max_tokens: int = 2048
    temperature: float = 0.7
    stream: bool = False

# 响应模型
class ChatResponse(BaseModel):
    id: str
    choices: List[Choice]
    usage: Usage
    created: int
```

#### 流式响应实现

```python
# SSE 流式响应核心逻辑
async def stream_chat(request: ChatRequest):
    async def generate():
        async for token in llm.stream_generate(request):
            chunk = {
                "choices": [{
                    "delta": {"content": token},
                    "index": 0
                }]
            }
            yield f"data: {json.dumps(chunk)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

---

### 2.2 异步处理

#### 为什么需要异步？

```
同步处理：
请求1 ████████████████░░░░░░░░░░░░░░░░  阻塞等待
请求2 ░░░░░░░░░░░░░░░░████████████████  排队

异步处理：
请求1 ████─────────────████             IO时释放
请求2 ░░░░████─────────────████         并发处理
         ↑ 等待推理时处理其他请求
```

#### 异步架构模式

```
┌─────────────────────────────────────────────────────────┐
│                   异步处理架构                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  请求 ──→ [消息队列] ──→ [Worker池] ──→ [结果存储]     │
│              │              │              │            │
│           Redis          Celery        Redis/DB        │
│           Kafka         AsyncIO                        │
│                                                         │
│  轮询/回调 ←─────────────────────────────┘              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### 任务队列实现

```python
# Celery 任务定义
@celery_app.task(bind=True, max_retries=3)
def async_generate(self, request_data: dict):
    try:
        result = llm_service.generate(request_data)
        return {"status": "success", "result": result}
    except Exception as e:
        self.retry(countdown=5)

# 提交任务
task = async_generate.delay(request.dict())
return {"task_id": task.id}

# 查询结果
result = AsyncResult(task_id)
if result.ready():
    return result.get()
```

---

### 2.3 批量推理

#### 批处理策略

```
┌─────────────────────────────────────────────────────────┐
│                  批量推理优化                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  策略1: 静态批处理                                      │
│  ┌────┬────┬────┬────┐                                 │
│  │Req1│Req2│Req3│Req4│ → 固定batch一起推理             │
│  └────┴────┴────┴────┘                                 │
│                                                         │
│  策略2: 动态批处理 (Continuous Batching)                │
│  ┌────┬────┬────┐                                      │
│  │Req1│Req2│    │ → Req1完成后立即加入Req4             │
│  └────┴────┴────┘                                      │
│  ┌────┬────┬────┐                                      │
│  │Req4│Req2│Req3│ → 持续填充，最大化利用率             │
│  └────┴────┴────┘                                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### 批处理参数配置

| 参数               | 说明         | 权衡                |
| ------------------ | ------------ | ------------------- |
| `max_batch_size`   | 最大批大小   | 大→高吞吐，延迟增加 |
| `max_waiting_time` | 最大等待时间 | 长→批更大，延迟增加 |
| `dynamic_batching` | 动态批处理   | 开启可提升30%+吞吐  |

#### 批量推理实现

```python
class BatchProcessor:
    def __init__(self, max_batch=8, max_wait=0.1):
        self.queue = asyncio.Queue()
        self.max_batch = max_batch
        self.max_wait = max_wait  # 秒

    async def process_loop(self):
        while True:
            batch = []
            deadline = time.time() + self.max_wait

            # 收集批次
            while len(batch) < self.max_batch:
                timeout = max(0, deadline - time.time())
                try:
                    item = await asyncio.wait_for(
                        self.queue.get(), timeout
                    )
                    batch.append(item)
                except asyncio.TimeoutError:
                    break

            if batch:
                results = await self.batch_inference(batch)
                # 返回结果...
```

---

## 3. 生产化

### 3.1 Docker 部署

#### Dockerfile 最佳实践

```dockerfile
# 多阶段构建
FROM nvidia/cuda:12.1-devel AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

FROM nvidia/cuda:12.1-runtime
WORKDIR /app

# 非root用户
RUN useradd -m -u 1000 appuser
USER appuser

# 复制依赖和代码
COPY --from=builder /install /usr/local
COPY --chown=appuser:appuser . .

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

#### Docker Compose 编排

```yaml
version: "3.8"
services:
  llm-api:
    build: .
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    ports:
      - "8000:8000"
    volumes:
      - model-cache:/root/.cache/huggingface
    environment:
      - MODEL_NAME=Qwen/Qwen2-7B-Instruct
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data

volumes:
  model-cache:
  redis-data:
```

---

### 3.2 K8s 扩展

#### K8s 部署架构

```
┌─────────────────────────────────────────────────────────┐
│                    Kubernetes 集群                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐        ┌─────────────────────────┐    │
│  │   Ingress   │───────→│       Service          │    │
│  │  (nginx)    │        │   (ClusterIP/LB)       │    │
│  └─────────────┘        └───────────┬─────────────┘    │
│                                     │                   │
│         ┌───────────────────────────┼───────────┐      │
│         ↓                           ↓           ↓      │
│    ┌─────────┐               ┌─────────┐  ┌─────────┐ │
│    │ Pod-1   │               │ Pod-2   │  │ Pod-3   │ │
│    │ GPU:1   │               │ GPU:1   │  │ GPU:1   │ │
│    │┌───────┐│               │┌───────┐│  │┌───────┐│ │
│    ││ vLLM  ││               ││ vLLM  ││  ││ vLLM  ││ │
│    │└───────┘│               │└───────┘│  │└───────┘│ │
│    └─────────┘               └─────────┘  └─────────┘ │
│         │                           │           │      │
│         └───────────────────────────┴───────────┘      │
│                          ↓                              │
│              ┌─────────────────────────┐               │
│              │    PVC (模型存储)        │               │
│              │    NFS / Ceph / S3      │               │
│              └─────────────────────────┘               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### 核心资源配置

```yaml
# Deployment 关键配置
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-service
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: vllm
          image: llm-service:v1.0
          resources:
            limits:
              nvidia.com/gpu: 1 # GPU资源
              memory: "32Gi"
            requests:
              memory: "16Gi"

          # 探针配置
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 60 # 模型加载时间
            periodSeconds: 10

          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 30

      # GPU节点调度
      nodeSelector:
        nvidia.com/gpu.product: "NVIDIA-A100"

      tolerations:
        - key: "nvidia.com/gpu"
          operator: "Exists"
          effect: "NoSchedule"
```

#### HPA 自动扩缩容

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: llm-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: llm-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Pods
      pods:
        metric:
          name: requests_queue_size
        target:
          type: AverageValue
          averageValue: "50" # 队列积压超50触发扩容
```

---

### 3.3 监控与日志

#### 监控指标体系

```
┌─────────────────────────────────────────────────────────┐
│                    监控指标金字塔                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│                    ┌─────────┐                          │
│                    │ 业务指标 │                          │
│                    │ 成功率   │                          │
│                    └────┬────┘                          │
│               ┌─────────┴─────────┐                     │
│               │     性能指标       │                     │
│               │ 延迟/吞吐/Token速率│                     │
│               └─────────┬─────────┘                     │
│          ┌──────────────┴──────────────┐                │
│          │         资源指标            │                │
│          │ GPU利用率/显存/CPU/内存     │                │
│          └──────────────┬──────────────┘                │
│     ┌───────────────────┴───────────────────┐           │
│     │              基础设施                 │           │
│     │         节点状态/网络/存储            │           │
│     └───────────────────────────────────────┘           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### 关键指标定义

| 指标名称                | 类型      | 说明        | 告警阈值    |
| ----------------------- | --------- | ----------- | ----------- |
| `llm_request_total`     | Counter   | 请求总数    | -           |
| `llm_request_latency`   | Histogram | 端到端延迟  | P99 > 30s   |
| `llm_ttft_seconds`      | Histogram | 首Token延迟 | P95 > 3s    |
| `llm_tokens_per_second` | Gauge     | 生成速率    | < 10        |
| `llm_queue_size`        | Gauge     | 队列长度    | > 100       |
| `gpu_memory_used_bytes` | Gauge     | 显存使用    | > 90%       |
| `llm_error_total`       | Counter   | 错误数      | 错误率 > 1% |

#### 日志规范

```json
// 请求日志格式
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "INFO",
  "trace_id": "abc-123-def",
  "event": "inference_complete",
  "user_id": "user_456",
  "model": "qwen2-7b",
  "input_tokens": 256,
  "output_tokens": 512,
  "ttft_ms": 180,
  "total_ms": 3200,
  "status": "success",
  "gpu_id": 0
}

// 错误日志格式
{
  "timestamp": "2024-01-15T10:31:00.000Z",
  "level": "ERROR",
  "trace_id": "xyz-789",
  "event": "inference_failed",
  "error_type": "OOMError",
  "error_message": "CUDA out of memory",
  "input_tokens": 8192,
  "gpu_memory_used": "39.5GB"
}
```

#### 监控栈部署

```
┌─────────────────────────────────────────────────────────┐
│                    可观测性架构                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  应用指标 ───→ Prometheus ───→ Grafana                  │
│                    ↓                                    │
│              AlertManager ───→ 钉钉/Slack/PagerDuty    │
│                                                         │
│  应用日志 ───→ Fluent Bit ───→ Loki ───→ Grafana       │
│                                                         │
│  链路追踪 ───→ OpenTelemetry ───→ Jaeger/Tempo         │
│                                                         │
│  GPU监控 ───→ DCGM Exporter ───→ Prometheus            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 4. 安全与合规

### 4.1 安全护栏

#### 安全威胁全景

```
┌─────────────────────────────────────────────────────────┐
│                   LLM 安全威胁                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  输入威胁                     输出风险                  │
│  ┌─────────────────┐         ┌─────────────────┐       │
│  │ • Prompt注入    │         │ • 有害内容      │       │
│  │ • 越狱攻击      │         │ • 隐私泄露      │       │
│  │ • 恶意指令      │         │ • 虚假信息      │       │
│  │ • 敏感信息探测  │         │ • 偏见歧视      │       │
│  └─────────────────┘         └─────────────────┘       │
│                                                         │
│  系统威胁                     合规要求                  │
│  ┌─────────────────┐         ┌─────────────────┐       │
│  │ • DDoS攻击      │         │ • 数据保护法规  │       │
│  │ • 资源耗尽      │         │ • 内容审核要求  │       │
│  │ • 模型窃取      │         │ • 审计追溯      │       │
│  └─────────────────┘         └─────────────────┘       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### 多层防护体系

```
请求 ──→ [网关层] ──→ [输入过滤] ──→ [模型推理] ──→ [输出审核] ──→ 响应
            │            │              │              │
            ↓            ↓              ↓              ↓
        认证鉴权      内容检测      监控告警       敏感过滤
        速率限制      长度限制      资源隔离       合规审计
        IP黑白名单    注入检测      超时控制       水印追踪
```

#### 输入安全检查

```python
class InputGuard:
    """输入安全护栏"""

    def check(self, text: str) -> GuardResult:
        checks = [
            self._check_length(text),           # 长度限制
            self._check_injection(text),        # 注入检测
            self._check_sensitive(text),        # 敏感词
            self._check_rate_limit(),           # 频率限制
        ]
        return self._aggregate(checks)

    def _check_injection(self, text: str) -> bool:
        # 检测常见注入模式
        patterns = [
            r"ignore.*previous.*instructions",
            r"disregard.*above",
            r"you are now",
            r"new instructions:",
        ]
        return not any(re.search(p, text, re.I) for p in patterns)
```

#### 输出安全审核

```python
class OutputGuard:
    """输出安全护栏"""

    def check(self, output: str) -> GuardResult:
        checks = [
            self._check_harmful_content(output),    # 有害内容
            self._check_pii_leakage(output),        # PII泄露
            self._check_hallucination(output),      # 幻觉检测
        ]
        return self._aggregate(checks)

    def _check_pii_leakage(self, text: str) -> bool:
        # 检测个人敏感信息
        pii_patterns = {
            'phone': r'\d{11}',
            'id_card': r'\d{17}[\dXx]',
            'email': r'\S+@\S+\.\S+',
        }
        for name, pattern in pii_patterns.items():
            if re.search(pattern, text):
                return False  # 发现PII
        return True
```

#### 安全配置清单

| 防护措施     | 配置项      | 推荐值    |
| ------------ | ----------- | --------- |
| **速率限制** | 每用户QPS   | 10-50     |
| **输入限制** | 最大Token数 | 4096-8192 |
| **输出限制** | 最大Token数 | 2048-4096 |
| **超时控制** | 请求超时    | 60-120s   |
| **并发限制** | 每用户并发  | 2-5       |
| **内容过滤** | 敏感词库    | 持续更新  |

---

## 总结

### 生产部署检查清单

```
推理优化
  □ 完成模型量化评估
  □ 选择合适的推理框架
  □ 配置最优推理参数

服务化
  □ API服务开发完成
  □ 流式响应实现
  □ 异步处理配置
  □ 批量推理优化

生产化
  □ Docker镜像构建
  □ K8s资源编排
  □ 自动扩缩容配置
  □ 监控告警体系
  □ 日志收集规范

安全合规
  □ 输入安全检查
  □ 输出内容审核
  □ 访问控制配置
  □ 审计日志记录
```

### 技术选型快速参考

| 场景       | 推荐方案                |
| ---------- | ----------------------- |
| 快速验证   | Ollama + FastAPI        |
| 小规模生产 | vLLM + Docker Compose   |
| 中大规模   | vLLM + K8s + Prometheus |
| 极致性能   | TensorRT-LLM + 多GPU    |

---
