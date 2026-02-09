"""
vLLM 部署实战
============

学习目标：
    1. 理解 vLLM 的核心技术（PagedAttention、Continuous Batching）
    2. 掌握 vLLM 服务部署和参数调优
    3. 使用 OpenAI 兼容 API 调用

核心概念：
    - PagedAttention：高效的 KV Cache 管理
    - Continuous Batching：动态批处理

环境要求：
    - pip install vllm
    - NVIDIA GPU with CUDA 11.8+
"""

import os


# ==================== 第一部分：vLLM 核心技术 ====================


def introduction():
    """vLLM 核心技术介绍"""
    print("=" * 60)
    print("第一部分：vLLM 核心技术")
    print("=" * 60)

    print("""
    📌 vLLM 核心优势：
    1. 高吞吐量 - 比 HuggingFace 快 24x
    2. PagedAttention - 显存利用率提升 2-4 倍
    3. Continuous Batching - 动态批处理
    4. OpenAI 兼容 API

    PagedAttention 原理：
    ┌────────────────────────────────────────┐
    │ 物理页池: [P1][P2][P3][P4][P5][P6]...  │
    │ Seq1 -> [P1, P3, P5]  按需分配         │
    │ Seq2 -> [P2, P4]      无碎片           │
    └────────────────────────────────────────┘
    """)


# ==================== 第二部分：基础使用 ====================


def basic_usage():
    """vLLM 基础使用"""
    print("\n" + "=" * 60)
    print("第二部分：基础使用")
    print("=" * 60)

    print("""
    # 安装
    pip install vllm

    # 离线推理示例
    from vllm import LLM, SamplingParams

    llm = LLM(model="Qwen/Qwen2-7B-Instruct")
    sampling_params = SamplingParams(temperature=0.7, max_tokens=256)

    prompts = ["介绍一下 vLLM", "什么是 LLM？"]
    outputs = llm.generate(prompts, sampling_params)

    for output in outputs:
        print(output.outputs[0].text)
    """)


# ==================== 第三部分：服务部署 ====================


def server_deployment():
    """服务部署"""
    print("\n" + "=" * 60)
    print("第三部分：服务部署")
    print("=" * 60)

    print("""
    # 启动 OpenAI 兼容服务
    python -m vllm.entrypoints.openai.api_server \\
        --model Qwen/Qwen2-7B-Instruct \\
        --port 8000 \\
        --gpu-memory-utilization 0.9 \\
        --max-num-seqs 64

    # Python 客户端调用
    from openai import OpenAI

    client = OpenAI(base_url="http://localhost:8000/v1", api_key="x")
    response = client.chat.completions.create(
        model="Qwen/Qwen2-7B-Instruct",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response.choices[0].message.content)
    """)


# ==================== 第四部分：参数调优 ====================


def parameter_tuning():
    """参数调优"""
    print("\n" + "=" * 60)
    print("第四部分：参数调优")
    print("=" * 60)

    print("""
    关键参数：
    ┌───────────────────────┬────────────────┬──────────────┐
    │        参数            │     说明       │   推荐值     │
    ├───────────────────────┼────────────────┼──────────────┤
    │ gpu-memory-utilization│ 显存使用比例   │ 0.85-0.95   │
    │ max-num-seqs          │ 最大并发序列   │ 32-128      │
    │ max-model-len         │ 最大序列长度   │ 按需设置     │
    │ tensor-parallel-size  │ GPU 并行数     │ GPU 卡数    │
    └───────────────────────┴────────────────┴──────────────┘

    # 量化模型部署
    python -m vllm.entrypoints.openai.api_server \\
        --model Qwen/Qwen2-7B-Instruct-AWQ \\
        --quantization awq
    """)


# ==================== 第五部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：部署 vLLM 服务并测试

        ✅ 参考答案：
        ```bash
        # 1. 安装 vLLM
        pip install vllm

        # 2. 启动服务
        python -m vllm.entrypoints.openai.api_server \\
            --model Qwen/Qwen2-1.5B-Instruct \\
            --port 8000 \\
            --gpu-memory-utilization 0.85

        # 3. 测试调用
        curl http://localhost:8000/v1/chat/completions \\
            -H "Content-Type: application/json" \\
            -d '{
                "model": "Qwen/Qwen2-1.5B-Instruct",
                "messages": [{"role": "user", "content": "Hello!"}],
                "max_tokens": 100
            }'
        ```
        
        ```python
        # Python 客户端测试
        from openai import OpenAI
        
        client = OpenAI(base_url="http://localhost:8000/v1", api_key="x")
        
        response = client.chat.completions.create(
            model="Qwen/Qwen2-1.5B-Instruct",
            messages=[{"role": "user", "content": "请用一句话介绍 vLLM"}],
            max_tokens=100,
        )
        print(response.choices[0].message.content)
        ```
    
    练习 2：对比不同参数配置的性能差异

        ✅ 参考答案：
        ```python
        import time
        import concurrent.futures
        from openai import OpenAI
        
        def benchmark_config(config_name, port):
            client = OpenAI(base_url=f"http://localhost:{port}/v1", api_key="x")
            
            prompts = ["介绍人工智能", "什么是机器学习", "解释深度学习"] * 10
            
            start = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [
                    executor.submit(
                        client.chat.completions.create,
                        model="Qwen/Qwen2-1.5B-Instruct",
                        messages=[{"role": "user", "content": p}],
                        max_tokens=100,
                    )
                    for p in prompts
                ]
                results = [f.result() for f in futures]
            
            total_time = time.time() - start
            total_tokens = sum(r.usage.completion_tokens for r in results)
            
            return {
                "config": config_name,
                "throughput": total_tokens / total_time,
                "avg_latency": total_time / len(prompts),
            }
        
        # 测试不同配置 (需要启动多个服务)
        # 配置1: max-num-seqs=16
        # 配置2: max-num-seqs=64
        # 配置3: max-num-seqs=128
        ```

    思考题：vLLM 相比 HuggingFace generate 有什么优势？

        ✅ 答：
        1. 更高吞吐量 - PagedAttention 减少显存碎片，支持更多并发
        2. 更好显存利用率 - 动态 KV Cache 分配
        3. Continuous Batching - 完成即填充，最大化 GPU 利用
        4. 原生 OpenAI API 兼容 - 无缝替换
        5. 量化模型支持 - AWQ/GPTQ 无缝加载
    """)


def main():
    introduction()
    basic_usage()
    server_deployment()
    parameter_tuning()
    exercises()
    print("\n课程完成！下一步：03-tgi-deployment.py")


if __name__ == "__main__":
    main()
