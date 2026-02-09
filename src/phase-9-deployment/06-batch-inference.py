"""
批量推理
========

学习目标：
    1. 理解批量推理的优势
    2. 实现静态批处理和动态批处理
    3. 优化批处理参数

核心概念：
    - 静态批处理：固定大小批次一起处理
    - 动态批处理：持续填充，最大化利用率
    - Continuous Batching：vLLM/TGI 的核心技术

环境要求：
    - pip install transformers torch
"""

import asyncio
import time
from typing import List


# ==================== 第一部分：批处理概念 ====================


def introduction():
    """批处理概念"""
    print("=" * 60)
    print("第一部分：批处理概念")
    print("=" * 60)

    print("""
    📌 为什么需要批处理？

    单条处理：效率低
    ┌────┐ ┌────┐ ┌────┐ ┌────┐
    │Req1│→│Req2│→│Req3│→│Req4│  串行处理
    └────┘ └────┘ └────┘ └────┘

    批量处理：效率高
    ┌────┬────┬────┬────┐
    │Req1│Req2│Req3│Req4│  并行处理
    └────┴────┴────┴────┘

    📌 批处理策略对比：
    ┌─────────────┬──────────────────────────────────────┐
    │  静态批处理  │ 凑够固定数量再处理，简单但有延迟     │
    ├─────────────┼──────────────────────────────────────┤
    │  动态批处理  │ 设置超时，到时间或凑够即处理         │
    ├─────────────┼──────────────────────────────────────┤
    │  Continuous │ 完成一个立即加入新的，持续填充       │
    └─────────────┴──────────────────────────────────────┘
    """)


# ==================== 第二部分：静态批处理 ====================


def static_batching():
    """静态批处理"""
    print("\n" + "=" * 60)
    print("第二部分：静态批处理")
    print("=" * 60)

    code = """
class StaticBatcher:
    def __init__(self, model, batch_size=8):
        self.model = model
        self.batch_size = batch_size
        self.queue = []

    def add(self, request):
        self.queue.append(request)
        if len(self.queue) >= self.batch_size:
            return self.process_batch()
        return None

    def process_batch(self):
        batch = self.queue[:self.batch_size]
        self.queue = self.queue[self.batch_size:]

        # 批量推理
        inputs = [r["text"] for r in batch]
        outputs = self.model.generate(inputs)

        return list(zip(batch, outputs))

# 使用
batcher = StaticBatcher(model, batch_size=8)
for request in requests:
    result = batcher.add(request)
    if result:
        print("Batch processed:", len(result))
"""
    print(code)


# ==================== 第三部分：动态批处理 ====================


def dynamic_batching():
    """动态批处理"""
    print("\n" + "=" * 60)
    print("第三部分：动态批处理")
    print("=" * 60)

    code = """
import asyncio
import time

class DynamicBatcher:
    def __init__(self, max_batch=8, max_wait=0.1):
        self.queue = asyncio.Queue()
        self.max_batch = max_batch
        self.max_wait = max_wait  # 秒

    async def add(self, request):
        future = asyncio.Future()
        await self.queue.put((request, future))
        return await future

    async def process_loop(self):
        while True:
            batch = []
            futures = []
            deadline = time.time() + self.max_wait

            # 收集批次
            while len(batch) < self.max_batch:
                timeout = max(0, deadline - time.time())
                try:
                    item, future = await asyncio.wait_for(
                        self.queue.get(), timeout
                    )
                    batch.append(item)
                    futures.append(future)
                except asyncio.TimeoutError:
                    break

            if batch:
                results = await self.batch_inference(batch)
                for future, result in zip(futures, results):
                    future.set_result(result)

    async def batch_inference(self, batch):
        # 实际推理逻辑
        return [f"Result for {b}" for b in batch]
"""
    print(code)


# ==================== 第四部分：参数调优 ====================


def parameter_tuning():
    """参数调优"""
    print("\n" + "=" * 60)
    print("第四部分：参数调优")
    print("=" * 60)

    print("""
    📌 批处理参数调优：
    ┌─────────────────┬────────────────┬────────────────────┐
    │      参数        │      说明      │       权衡          │
    ├─────────────────┼────────────────┼────────────────────┤
    │ max_batch_size  │ 最大批大小     │ 大→高吞吐，延迟增加 │
    │ max_waiting_time│ 最大等待时间   │ 长→批更大，延迟增加 │
    │ dynamic_batching│ 动态批处理     │ 提升 30%+ 吞吐量   │
    └─────────────────┴────────────────┴────────────────────┘

    调优策略：
    1. 低延迟要求 → 减小 batch_size 和 wait_time
    2. 高吞吐要求 → 增大 batch_size，使用 Continuous Batching
    3. 实际测试确定最优配置

    参考值：
    - 在线服务：batch_size=4-8, wait_time=50-100ms
    - 离线处理：batch_size=32-64, wait_time=500ms-1s
    """)


# ==================== 第五部分：练习 ====================


def exercises():
    """练习"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：实现动态批处理服务

        ✅ 参考答案：
        ```python
        import asyncio
        import time
        from typing import Dict, Any
        import uuid
        
        class DynamicBatchService:
            def __init__(self, model, max_batch=8, max_wait=0.1):
                self.model = model
                self.queue = asyncio.Queue()
                self.max_batch = max_batch
                self.max_wait = max_wait
                self.running = True
            
            async def add_request(self, request: dict) -> str:
                future = asyncio.Future()
                request_id = str(uuid.uuid4())
                await self.queue.put((request_id, request, future))
                result = await future
                return result
            
            async def batch_worker(self):
                while self.running:
                    batch = []
                    futures = []
                    deadline = time.time() + self.max_wait
                    
                    while len(batch) < self.max_batch:
                        timeout = max(0, deadline - time.time())
                        try:
                            req_id, request, future = await asyncio.wait_for(
                                self.queue.get(), timeout
                            )
                            batch.append(request)
                            futures.append(future)
                        except asyncio.TimeoutError:
                            break
                    
                    if batch:
                        results = await self.batch_inference(batch)
                        for future, result in zip(futures, results):
                            future.set_result(result)
            
            async def batch_inference(self, batch):
                # 批量推理
                inputs = [r["text"] for r in batch]
                outputs = self.model.generate(inputs)
                return outputs
        
        # 使用
        service = DynamicBatchService(model, max_batch=8, max_wait=0.1)
        asyncio.create_task(service.batch_worker())
        result = await service.add_request({"text": "Hello"})
        ```
    
    练习 2：测试不同批处理参数对吞吐量和延迟的影响

        ✅ 参考答案：
        ```python
        import asyncio
        import time
        
        async def benchmark_batch_params(service_class, model, params_list):
            results = []
            
            for max_batch, max_wait in params_list:
                service = service_class(model, max_batch, max_wait)
                asyncio.create_task(service.batch_worker())
                
                # 生成测试请求
                requests = [{"text": f"Request {i}"} for i in range(100)]
                
                start = time.time()
                tasks = [service.add_request(r) for r in requests]
                await asyncio.gather(*tasks)
                total_time = time.time() - start
                
                results.append({
                    "max_batch": max_batch,
                    "max_wait": max_wait,
                    "throughput": len(requests) / total_time,
                    "avg_latency": total_time / len(requests),
                })
                
                service.running = False
            
            return results
        
        # 测试参数组合
        params = [(4, 0.05), (8, 0.1), (16, 0.2), (32, 0.5)]
        results = await benchmark_batch_params(DynamicBatchService, model, params)
        
        for r in results:
            print(f"batch={r['max_batch']}, wait={r['max_wait']:.2f}s -> "
                  f"throughput={r['throughput']:.1f}/s, latency={r['avg_latency']*1000:.0f}ms")
        ```

    思考题：为什么 vLLM 的 Continuous Batching 比静态批处理更高效？

        ✅ 答：
        1. 静态批处理需要等待所有请求完成才能处理下一批
        2. Continuous Batching 在任意请求完成时立即加入新请求
        3. 持续填充 GPU，保持高利用率
        4. 短请求不会被长请求阻塞
        5. 实际吞吐量可提升 2-3 倍
    """)


def main():
    introduction()
    static_batching()
    dynamic_batching()
    parameter_tuning()
    exercises()
    print("\n课程完成！下一步：07-docker-deployment.py")


if __name__ == "__main__":
    main()
