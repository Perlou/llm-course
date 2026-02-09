"""
模型合并
========

学习目标：
    1. 理解模型合并的概念
    2. 掌握 LoRA 权重合并
    3. 了解多模型合并技术

核心概念：
    - Merge and Unload
    - 模型融合
    - TIES/DARE Merge

环境要求：
    - pip install peft transformers
"""

import os
from dotenv import load_dotenv

load_dotenv()


def merge_overview():
    """合并概述"""
    print("=" * 60)
    print("第一部分：模型合并概述")
    print("=" * 60)

    print("""
    为什么需要模型合并？
    ───────────────────
    
    1. 推理效率
       - 合并后只需加载一个模型
       - 无额外计算开销
    
    2. 能力组合
       - 合并多个专业模型
       - 获得综合能力
    
    3. 部署简化
       - 无需管理多个 adapter
       - 统一模型格式
    
    
    合并类型
    ───────
    
    ┌─────────────────────────────────────────────────────────┐
    │                    模型合并类型                          │
    │                                                         │
    │   1. LoRA 合并                                          │
    │      Base + LoRA → Merged Model                         │
    │                                                         │
    │   2. 多 Adapter 合并                                    │
    │      Base + LoRA1 + LoRA2 → Combined Model              │
    │                                                         │
    │   3. 多模型融合                                         │
    │      Model A + Model B → Hybrid Model                   │
    │                                                         │
    └─────────────────────────────────────────────────────────┘
    """)


def lora_merge():
    """LoRA 合并"""
    print("\n" + "=" * 60)
    print("第二部分：LoRA 权重合并")
    print("=" * 60)

    print("""
    LoRA 合并原理
    ────────────
    
    W' = W + BA
    
    合并后得到一个标准模型，没有额外的 adapter 权重。
    """)

    code_example = """
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    # 1. 加载基础模型
    base_model = AutoModelForCausalLM.from_pretrained(
        "meta-llama/Llama-2-7b-hf",
        torch_dtype=torch.float16,
        device_map="auto",
    )

    # 2. 加载 PEFT 模型
    peft_model = PeftModel.from_pretrained(
        base_model,
        "./lora_adapter",
    )

    # 3. 合并权重
    merged_model = peft_model.merge_and_unload()

    # 4. 保存合并后的模型
    merged_model.save_pretrained("./merged_model")

    # 同时保存 tokenizer
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
    tokenizer.save_pretrained("./merged_model")

    # 5. 验证合并结果
    # 加载合并模型
    loaded_model = AutoModelForCausalLM.from_pretrained("./merged_model")
    """

    print(code_example)


def multi_adapter_merge():
    """多 Adapter 合并"""
    print("\n" + "=" * 60)
    print("第三部分：多 Adapter 合并")
    print("=" * 60)

    print("""
    加权合并多个 Adapter
    ───────────────────
    
    场景：组合多个任务特定的 adapter
    """)

    code_example = """
    from peft import PeftModel

    # 加载基础模型
    model = AutoModelForCausalLM.from_pretrained("base_model")

    # 加载第一个 adapter
    model = PeftModel.from_pretrained(model, "./adapter_translate")

    # 加载第二个 adapter
    model.load_adapter("./adapter_summarize", adapter_name="summarize")

    # 方法 1: 切换使用
    model.set_adapter("default")  # translate
    output1 = model.generate(...)

    model.set_adapter("summarize")
    output2 = model.generate(...)

    # 方法 2: 加权合并
    model.add_weighted_adapter(
        adapters=["default", "summarize"],
        weights=[0.6, 0.4],
        adapter_name="combined",
        combination_type="linear",  # 或 "svd", "ties"
    )
    model.set_adapter("combined")

    # 方法 3: 合并并卸载
    merged = model.merge_and_unload()
    """

    print(code_example)


def advanced_merge():
    """高级合并技术"""
    print("\n" + "=" * 60)
    print("第四部分：高级合并技术")
    print("=" * 60)

    print("""
    模型融合技术
    ───────────
    
    1. 线性插值 (Linear Interpolation)
       W_merged = α × W_A + (1-α) × W_B
    
    2. SLERP (Spherical Linear Interpolation)
       对权重向量进行球面插值
    
    3. TIES Merge
       - 保留最重要的参数变化
       - 解决符号冲突
       - 效果通常更好
    
    4. DARE (Drop And REscale)
       - 随机丢弃部分变化
       - 重新缩放剩余变化
    """)

    merge_code = '''
    # 使用 mergekit 进行高级合并
    # pip install mergekit

    # YAML 配置文件 (merge_config.yaml):
    """
    models:
      - model: ./model_a
        parameters:
          weight: 0.6
      - model: ./model_b
        parameters:
          weight: 0.4
    merge_method: ties  # 或 linear, slerp, dare_ties
    base_model: meta-llama/Llama-2-7b-hf
    parameters:
      density: 0.5
      normalize: true
    dtype: float16
    """

    # 命令行执行
    # mergekit-yaml merge_config.yaml ./merged_output
    '''

    print(merge_code)


def merge_tips():
    """合并技巧"""
    print("\n" + "=" * 60)
    print("第五部分：合并最佳实践")
    print("=" * 60)

    print("""
    最佳实践
    ───────
    
    1. 合并前
       - 确保基础模型完全相同
       - 检查 adapter 兼容性
       - 备份原始模型
    
    2. 权重选择
       - 根据任务重要性调整权重
       - 可以进行消融实验
    
    3. 验证合并
       - 在多个任务上测试
       - 检查是否有能力丢失
    
    4. 精度注意
       - 合并时保持高精度
       - 量化在合并后进行
    
    
    常见问题
    ───────
    
    Q: 合并后模型变大了？
    A: 正常，因为 adapter 权重被融入。
    
    Q: 能力发生冲突怎么办？
    A: 调整权重或使用 TIES 合并。
    
    Q: QLoRA 模型能合并吗？
    A: 需要先反量化基础模型。
    """)


def exercises():
    """练习题"""
    print("\n" + "=" * 60)
    print("练习与思考")
    print("=" * 60)

    print("""
    练习 1：LoRA 合并
        训练一个 LoRA 并合并到基础模型

        ✅ 参考答案：
        ```python
        from peft import PeftModel, LoraConfig, get_peft_model
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        
        # 1. 训练 LoRA (假设已完成)
        # ...
        
        # 2. 加载基础模型
        base_model = AutoModelForCausalLM.from_pretrained(
            "Qwen/Qwen2-0.5B",
            torch_dtype=torch.float16,
        )
        
        # 3. 加载 LoRA adapter
        peft_model = PeftModel.from_pretrained(base_model, "./lora_adapter")
        
        # 4. 合并权重
        merged_model = peft_model.merge_and_unload()
        
        # 5. 保存合并后的模型
        merged_model.save_pretrained("./merged_model")
        
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2-0.5B")
        tokenizer.save_pretrained("./merged_model")
        
        # 6. 验证
        loaded = AutoModelForCausalLM.from_pretrained("./merged_model")
        print("合并成功！")
        ```
    
    练习 2：多 Adapter 实验
        比较不同权重的合并效果

        ✅ 参考答案：
        ```python
        def experiment_merge_weights(model, adapter_names, weight_pairs):
            results = []
            
            for weights in weight_pairs:
                # 创建合并的 adapter
                model.add_weighted_adapter(
                    adapters=adapter_names,
                    weights=list(weights),
                    adapter_name=f"merged_{weights}",
                )
                model.set_adapter(f"merged_{weights}")
                
                # 评估
                task1_score = evaluate_task1(model)
                task2_score = evaluate_task2(model)
                
                results.append({
                    "weights": weights,
                    "task1": task1_score,
                    "task2": task2_score,
                    "avg": (task1_score + task2_score) / 2,
                })
            
            # 找到最佳权重
            best = max(results, key=lambda x: x["avg"])
            return results, best
        
        # 测试
        weight_pairs = [(0.3, 0.7), (0.5, 0.5), (0.7, 0.3)]
        results, best = experiment_merge_weights(
            model, ["adapter_a", "adapter_b"], weight_pairs
        )
        ```
    
    练习 3：TIES 合并
        使用 mergekit 进行高级合并

        ✅ 参考答案：
        ```yaml
        # merge_config.yaml
        models:
          - model: ./model_chat
            parameters:
              weight: 0.5
              density: 0.5
          - model: ./model_code
            parameters:
              weight: 0.5
              density: 0.5
        merge_method: ties
        base_model: Qwen/Qwen2-0.5B
        parameters:
          normalize: true
          int8_mask: true
        dtype: float16
        ```
        
        ```bash
        # 执行合并
        pip install mergekit
        mergekit-yaml merge_config.yaml ./merged_output --cuda
        ```
    
    思考题：
    ────────
    1. 合并后能否恢复原始 adapter？

       ✅ 答：
       不能。合并是不可逆操作。
       建议：
       - 合并前保存 adapter 副本
       - 保存合并配置用于复现
       - 使用版本控制管理 adapter

    2. 如何自动选择最佳合并权重？

       ✅ 答：
       - 网格搜索：遍历权重组合
       - 贝叶斯优化：智能搜索
       - 验证集驱动：使用验证集分数指导
       
       ```python
       from sklearn.model_selection import ParameterGrid
       
       param_grid = {"w1": [0.3, 0.5, 0.7], "w2": [0.3, 0.5, 0.7]}
       best_score = 0
       best_weights = None
       
       for params in ParameterGrid(param_grid):
           if params["w1"] + params["w2"] != 1.0:
               continue
           score = evaluate_merged(params["w1"], params["w2"])
           if score > best_score:
               best_score = score
               best_weights = params
       ```
    """)


def main():
    print("🔗 模型合并")
    print("=" * 60)
    merge_overview()
    lora_merge()
    multi_adapter_merge()
    advanced_merge()
    merge_tips()
    exercises()
    print("\n✅ 课程完成！下一步：10-finetuning-evaluation.py")


if __name__ == "__main__":
    main()
