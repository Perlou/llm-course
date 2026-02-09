"""
TGI 部署实战
===========

学习目标：
    1. 理解 TGI 的特点和适用场景
    2. 掌握 TGI Docker 部署
    3. 了解 TGI 与 vLLM 的对比选择

核心概念：
    - TGI：HuggingFace 官方推理服务
    - Flash Attention：高效注意力计算
    - 多 LoRA 支持：动态加载适配器

环境要求：
    - Docker with NVIDIA GPU support
    - 或 pip install text-generation
"""


# ==================== 第一部分：TGI 介绍 ====================


def introduction():
    """TGI 介绍"""
    print("=" * 60)
    print("第一部分：TGI 介绍")
    print("=" * 60)

    print("""
    📌 TGI vs vLLM 对比：
    ┌────────────┬──────────────────┬──────────────────┐
    │    特性    │       TGI        │       vLLM       │
    ├────────────┼──────────────────┼──────────────────┤
    │   生态     │ HuggingFace原生  │ 独立项目         │
    │   功能     │ 功能丰富         │ 专注推理性能     │
    │   性能     │ 优秀             │ 更优             │
    │   量化     │ GPTQ/AWQ/EETQ    │ GPTQ/AWQ/FP8     │
    │   部署     │ Docker优先       │ Python/Docker    │
    │   多LoRA   │ ✅ 原生支持      │ ✅ 支持          │
    │   水印     │ ✅ 支持          │ ❌ 不支持        │
    └────────────┴──────────────────┴──────────────────┘

    选择建议：
    - 追求极致性能 → vLLM
    - 需要 HuggingFace 生态特性 → TGI
    - 需要输出水印追踪 → TGI
    """)


# ==================== 第二部分：Docker 部署 ====================


def docker_deployment():
    """Docker 部署"""
    print("\n" + "=" * 60)
    print("第二部分：Docker 部署")
    print("=" * 60)

    print("""
    # 基础部署
    docker run --gpus all \\
        -v ~/.cache/huggingface:/data \\
        -p 8080:80 \\
        ghcr.io/huggingface/text-generation-inference:latest \\
        --model-id Qwen/Qwen2-7B-Instruct

    # 生产级配置
    docker run --gpus all \\
        -v ~/.cache/huggingface:/data \\
        -p 8080:80 \\
        ghcr.io/huggingface/text-generation-inference:latest \\
        --model-id Qwen/Qwen2-7B-Instruct \\
        --max-input-length 4096 \\
        --max-total-tokens 8192 \\
        --max-batch-prefill-tokens 4096 \\
        --quantize awq  # 使用量化模型

    # 关键参数说明
    --max-input-length      # 最大输入长度
    --max-total-tokens      # 最大总 token 数
    --max-batch-prefill-tokens  # 预填充批处理 token 数
    --quantize              # 量化方式: awq/gptq/eetq
    --num-shard             # GPU 分片数（多卡）
    """)


# ==================== 第三部分：API 调用 ====================


def api_usage():
    """API 调用"""
    print("\n" + "=" * 60)
    print("第三部分：API 调用")
    print("=" * 60)

    print("""
    # Python 客户端
    from text_generation import Client

    client = Client("http://localhost:8080")

    # 普通生成
    response = client.generate(
        "介绍一下人工智能",
        max_new_tokens=256,
        temperature=0.7
    )
    print(response.generated_text)

    # 流式生成
    for token in client.generate_stream("讲一个笑话"):
        print(token.token.text, end="", flush=True)

    # REST API 调用
    curl http://localhost:8080/generate \\
        -H "Content-Type: application/json" \\
        -d '{
            "inputs": "Hello!",
            "parameters": {"max_new_tokens": 100}
        }'
    """)


# ==================== 第四部分：高级特性 ====================


def advanced_features():
    """高级特性"""
    print("\n" + "=" * 60)
    print("第四部分：高级特性")
    print("=" * 60)

    print("""
    📌 TGI 特色功能：

    1. 多 LoRA 动态加载
    docker run ... \\
        --lora-adapters my-adapter=/path/to/adapter

    2. 输出水印（用于追踪生成内容）
    --watermark-gamma 0.5 --watermark-delta 2.0

    3. 内置 Prometheus 指标
    curl http://localhost:8080/metrics

    4. OpenAI 兼容端点
    curl http://localhost:8080/v1/chat/completions \\
        -H "Content-Type: application/json" \\
        -d '{"model": "tgi", "messages": [...]}'
    """)


# ==================== 第五部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：使用 Docker 部署 TGI 服务

        ✅ 参考答案：
        ```bash
        # 1. 拉取镜像
        docker pull ghcr.io/huggingface/text-generation-inference:latest

        # 2. 启动服务
        docker run --gpus all \\
            -v ~/.cache/huggingface:/data \\
            -p 8080:80 \\
            ghcr.io/huggingface/text-generation-inference:latest \\
            --model-id Qwen/Qwen2-1.5B-Instruct \\
            --max-input-length 2048 \\
            --max-total-tokens 4096

        # 3. 测试调用
        curl http://localhost:8080/generate \\
            -H "Content-Type: application/json" \\
            -d '{"inputs": "介绍一下 TGI", "parameters": {"max_new_tokens": 100}}'
        ```
        
        ```python
        # Python 客户端测试
        from text_generation import Client
        
        client = Client("http://localhost:8080")
        
        # 普通生成
        response = client.generate("什么是 TGI？", max_new_tokens=100)
        print(response.generated_text)
        
        # 流式生成
        for token in client.generate_stream("讲一个笑话", max_new_tokens=200):
            print(token.token.text, end="", flush=True)
        ```
    
    练习 2：对比 TGI 和 vLLM 的响应延迟

        ✅ 参考答案：
        ```python
        import time
        import requests
        
        def test_tgi(prompt, n=10):
            latencies = []
            for _ in range(n):
                start = time.time()
                requests.post(
                    "http://localhost:8080/generate",
                    json={"inputs": prompt, "parameters": {"max_new_tokens": 100}}
                )
                latencies.append(time.time() - start)
            return sum(latencies) / len(latencies)
        
        def test_vllm(prompt, n=10):
            latencies = []
            for _ in range(n):
                start = time.time()
                requests.post(
                    "http://localhost:8000/v1/chat/completions",
                    json={
                        "model": "Qwen/Qwen2-1.5B-Instruct",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 100
                    }
                )
                latencies.append(time.time() - start)
            return sum(latencies) / len(latencies)
        
        prompt = "解释什么是大语言模型"
        print(f"TGI 平均延迟: {test_tgi(prompt):.3f}s")
        print(f"vLLM 平均延迟: {test_vllm(prompt):.3f}s")
        ```

    思考题：什么场景下选择 TGI 而不是 vLLM？

        ✅ 答：
        1. 需要水印追踪 - TGI 原生支持输出水印
        2. 多 LoRA 动态切换 - 运行时切换不同适配器
        3. HuggingFace 生态集成 - 与 Hub 深度集成
        4. 需要 EETQ 量化 - TGI 特有
        5. 企业合规要求 - 输出可追溯
    """)


def main():
    introduction()
    docker_deployment()
    api_usage()
    advanced_features()
    exercises()
    print("\n课程完成！下一步：04-fastapi-llm-service.py")


if __name__ == "__main__":
    main()
